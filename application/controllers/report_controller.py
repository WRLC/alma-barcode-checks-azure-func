"""
Controllers for the report model.
"""
import logging
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
from application.controllers.analysis_controller import analysis_api_call
from application.controllers.exception_controller import check_exception
from application.models.analysis_sql import Analysis
from application.models.report import Report


# pylint: disable=r0914
def get_report(analysis: Analysis) -> Report | bool | Exception | None:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :return: requests.Response or None
    """
    response = analysis_api_call(analysis)  # Create an API call object and execute it

    if not check_exception(response) or isinstance(check_exception(response), Exception):  # Check for empty or errors
        return check_exception(response)  # Return the error or None

    soup = get_soup(response)  # Parse the XML response

    if not check_exception(soup) or isinstance(check_exception(soup), Exception):  # Check for empty or errors
        return check_exception(soup)  # Return the error or None

    columns = get_columns(soup)  # Get the columns from the XML response
    rows = get_rows(soup)  # Get the rows from the XML response

    for i in [columns, rows]:  # Iterate through the columns and rows
        if not check_exception(i) or isinstance(check_exception(i), Exception):  # Check for empty or errors
            return check_exception(i)  # Return the error or None

    report = Report(  # Create the report object
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': analysis.iz.code.upper() + ' ' + analysis.trigger.name,
                'columns': columns,
                'rows': rows
            }
        }
    )

    logging.debug('Report data compiled: %s', report.data['data']['report_name'])  # Log the success message

    return report  # Return the report


def get_soup(response) -> BeautifulSoup | Exception | None:
    """
    Parse the XML response

    :param response: requests.Response
    :return: BeautifulSoup
    """
    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if not check_exception(soup) or isinstance(check_exception(soup), Exception):  # Check for empty or errors
        return check_exception(soup)  # Return the error or None

    if soup.find('error'):  # Check for Alma errors
        logging.error('Error: %s', soup.find('error').text)
        return ValueError(soup.find('error').text)

    logging.debug('XML response parsed')  # Log the success message

    return soup


def get_columns(soup: BeautifulSoup) -> dict[str, str] | bool | Exception | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not check_exception(columnlist) or isinstance(check_exception(columnlist), Exception):
        return check_exception(columnlist)

    columns = {}  # Create a dictionary of columns

    for column in columnlist:  # Iterate through the columns
        columns[column['name']] = column['saw-sql:columnHeading']  # Add column to dictionary

        if 'CASE  WHEN Provenance Code' in columns[column['name']]:  # If column is Provenance Code
            columns[column['name']] = 'Provenance Code'  # Change column name to Provenance Code

    logging.debug('Columns retrieved')  # Log the success message

    return columns  # Return the dictionary of columns


def get_rows(soup: BeautifulSoup) -> list | bool | Exception | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    rowlist = soup.find_all('Row')  # Get the rows from the XML response

    if not check_exception(rowlist) or isinstance(check_exception(rowlist), Exception):
        return check_exception(rowlist)

    rows = []  # Create a list of rows

    for value in rowlist:  # Iterate through the rows
        values = {}  # Create a dictionary of values
        kids = value.findChildren()  # Get the children of the row

        for kid in kids:  # Iterate through the children
            values[kid.name] = kid.text  # Add the child to the dictionary

        rows.append(values)  # Add the dictionary to the list

    logging.debug('Rows retrieved')  # Log the success message

    return rows  # Return the list of rows
