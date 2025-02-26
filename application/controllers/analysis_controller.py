"""
Controller for the Analysis model
"""
import logging
import urllib.parse
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
import requests  # type:ignore[import-untyped]
from application.controllers.area_controller import get_area_by_name
from application.controllers.config_controller import get_config
from application.controllers.key_controller import get_key
from application.models.analysis_sql import Analysis
from application.models.report import Report


# pylint: disable=r0914
def get_report(analysis: Analysis) -> Report:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :return: requests.Response or None
    """
    response = analysis_api_call(analysis)  # Create an API call object and execute it
    soup = get_soup(response)  # Parse the XML response
    columns = get_columns(soup)  # Get the columns from the XML response
    rows = get_rows(soup)  # Get the rows from the XML response

    return Report(
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': analysis.iz.name.upper() + ' ' + analysis.trigger.name,
                'columns': columns,
                'rows': rows
            }
        }
    )


def analysis_api_call(analysis: Analysis) -> requests.Response:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :return: requests.Response
    """
    area = get_area_by_name('analytics')  # Get the area from the database
    iz = analysis.iz  # Get the IZ from the analysis

    apikey = get_key(iz.id, area.id, 0)  # Get the API key

    payload = {'limit': '1000', 'col_names': 'true', 'path': analysis.path, 'apikey': apikey}  # Create the payload
    payload_str = urllib.parse.urlencode(payload, safe=':%')

    try:  # Try to get the report from Alma
        response = requests.get(build_path(), params=payload_str, timeout=300)  # Get the report from Alma
        response.raise_for_status()  # Check for HTTP errors
    except Exception as e:  # Handle exceptions
        logging.error(e)
        raise

    return response


def build_path() -> str:
    """
    Build the API path.

    :return: The API path.
    """
    region = get_config('alma_region')  # Get the region from the database

    path = f'https://api-{region}.hosted.exlibrisgroup.com'

    if region == 'cn':
        path += '.cn'

    path += '/almaws/v1/analytics/reports'

    return path


def get_soup(response) -> BeautifulSoup:
    """
    Parse the XML response

    :param response: requests.Response
    :return: BeautifulSoup
    """
    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if soup.find('error'):  # Check for Alma errors
        logging.warning('Error: %s', soup.find('error').text)
        raise ValueError(soup.find('error').text)

    return soup


def get_columns(soup: BeautifulSoup) -> dict[str, str] or None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not columnlist:  # Check for columns
        logging.warning('No data columns in response.')
        return None

    columns = {}  # Create a dictionary of columns
    for column in columnlist:  # Add columns to the dictionary
        columns[column['name']] = column['saw-sql:columnHeading']
        if 'CASE  WHEN Provenance Code' in columns[column['name']]:
            columns[column['name']] = 'Provenance Code'

    return columns


def get_rows(soup: BeautifulSoup) -> list or None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    rowlist = soup.find_all('Row')  # Get the rows from the XML response

    if not rowlist:  # Check for rows
        logging.info('No data rows in response.')
        return None

    rows = []

    for value in rowlist:
        values = {}
        kids = value.findChildren()
        for kid in kids:
            values[kid.name] = kid.text
        rows.append(values)

    return rows
