"""
Module to get a report from Alma Analytics
"""
import logging
import os
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
from shared.report.models.apicall import ApiCall
from shared.report.models.report import Report


# pylint: disable=r0914
def get_report(envs: dict[str, str]) -> Report | None:
    """
    Get the report from Alma Analytics

    :param envs: dict[str, str]
    :return: requests.Response or None
    """

    api_call = ApiCall(
        os.getenv(envs['region']),  # type:ignore[arg-type]
        os.getenv(envs['iz']),  # type:ignore[arg-type]
        os.getenv(envs['path'])  # type:ignore[arg-type]
    )  # Create an API call object
    response = api_call.execute()

    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if soup.find('error'):  # Check for Alma errors
        logging.warning('Error: %s', soup.find('error').text)
        return None

    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not columnlist:  # Check for columns
        logging.warning('No data columns in response.')
        return None

    columns = {}  # Create a dictionary of columns
    for column in columnlist:  # Add columns to the dictionary
        columns[column['name']] = column['saw-sql:columnHeading']
        if 'CASE  WHEN Provenance Code' in columns[column['name']]:
            columns[column['name']] = 'Provenance Code'

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

    # Get the report name from the environment variables
    report_name = os.getenv(envs['iz']).upper() + ' ' + os.getenv(envs['name'])  # type:ignore

    return Report(
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': report_name,
                'columns': columns,
                'rows': rows
            }
        }
    )
