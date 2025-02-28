"""
Controllers for the report model.
"""
import logging
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
from sqlalchemy.orm import scoped_session

from application.controllers.analysis_controller import get_analysis
from application.controllers.exception_controller import check_exception
from application.models.analysis_sql import Analysis
from application.models.report import Report


# pylint: disable=r0914
def get_report(analysis: Analysis, session: scoped_session) -> Report | None:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :param session: Session object
    :return: requests.Response or None
    """
    if not check_exception(analysis):  # Check for empty or errors
        return None

    # Get the data from Alma Analytics
    response = get_analysis(analysis, session)

    if not check_exception(response):  # Check for empty or errors
        return None

    soup = get_soup(response)  # Parse the XML response

    if not check_exception(soup):  # Check for empty or errors
        return None

    columns = get_columns(soup)  # Get the columns from the XML response
    rows = get_rows(soup)  # Get the rows from the XML response

    for i in [columns, rows]:  # Iterate through the columns and rows
        if not check_exception(i):  # Check for empty or errors
            return None

    report = Report(  # Create the report object
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': analysis.iz.code.upper() + ' ' + analysis.azuretrigger.name,
                'columns': columns,
                'rows': rows
            }
        }
    )

    logging.debug('Report data compiled: %s', report.data['data']['report_name'])  # Log the success message

    return report  # Return the report


def get_soup(response) -> BeautifulSoup | None:
    """
    Parse the XML response

    :param response: requests.Response
    :return: BeautifulSoup
    """
    if not check_exception(response):  # Check for empty or errors
        return None

    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if not check_exception(soup):  # Check for empty or errors
        return None  # Return the error or None

    if soup.find('error'):  # Check for Alma errors
        logging.error('Error: %s', soup.find('error').text)
        return None

    logging.debug('XML response parsed')  # Log the success message

    return soup


def get_columns(soup: BeautifulSoup) -> dict[str, str] | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    if not check_exception(soup):  # Check for empty or errors
        return None

    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not check_exception(columnlist):
        return None

    columns = {}  # Create a dictionary of columns

    for column in columnlist:  # Iterate through the columns
        columns[column['name']] = column['saw-sql:columnHeading']  # Add column to dictionary

        if 'CASE  WHEN Provenance Code' in columns[column['name']]:  # If column is Provenance Code
            columns[column['name']] = 'Provenance Code'  # Change column name to Provenance Code

    logging.debug('Columns retrieved')  # Log the success message

    return columns  # Return the dictionary of columns


def get_rows(soup: BeautifulSoup) -> list | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    if not check_exception(soup):  # Check for empty or errors
        return None

    rowlist = soup.find_all('Row')  # Get the rows from the XML response

    if not check_exception(rowlist):
        return None

    rows = []  # Create a list of rows

    for value in rowlist:  # Iterate through the rows
        values = {}  # Create a dictionary of values
        kids = value.findChildren()  # Get the children of the row

        for kid in kids:  # Iterate through the children
            values[kid.name] = kid.text  # Add the child to the dictionary

        rows.append(values)  # Add the dictionary to the list

    logging.debug('Rows retrieved')  # Log the success message

    return rows  # Return the list of rows
