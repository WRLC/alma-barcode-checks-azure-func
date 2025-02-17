"""
Shared utility functions for Alma Analytics
"""
import json
import logging
import os
import urllib.parse
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from bs4 import BeautifulSoup
import requests


class Report:
    """
    Report object
    """
    def __init__(self, data: json) -> None:
        """
        Report object

        :param data: json
        :return: None
        """
        self.data = data


class ReportException(Exception):
    """
    Report exception
    """
    def __init__(self, message: str) -> None:
        """
        Report exception

        :param message: str
        :return: None
        """
        super().__init__(message)


class ApiCall:
    """
    An object to create and execute an API call.
    """
    def __init__(self, region: str, iz: str, report_path: str) -> None:
        """
        Initialize the API call object.
        :param iz: The institution code.
        :param report_path: The path to the report.
        """
        self.region = region
        self.iz = iz
        self.report_path = report_path

    def build_path(self) -> str:
        """
        Build the API path.
        :return: The API path.
        """
        path = f'https://api-{self.region}.hosted.exlibrisgroup.com'

        if self.region == 'cn':
            path += '.cn'

        path += '/almaws/v1/analytics/reports'

        return path

    # noinspection PyTypeChecker
    def get_apikey(self) -> str:
        """
        Get the API key from the Azure Key Vault.

        :return: The API key.
        """
        # Get the API key from Key Vault
        keyvaultname = os.environ["KEY_VAULT_NAME"]  # Get the Azure Key Vault name
        kvuri = f"https://{keyvaultname}.vault.azure.net"  # Get the Azure Key Vault URI
        credential = DefaultAzureCredential()  # Get the Azure credentials
        secret_client = SecretClient(vault_url=kvuri, credential=credential)  # Get the Azure Key Vault client

        apikey = secret_client.get_secret(f"{self.iz}-ALMA-API-KEY").value  # Get the API key from the Azure Key Vault

        return apikey

    def execute(self) -> requests.Response:
        """
        Execute the API call.
        :return: The response from the API call.
        """
        payload = {'limit': '1000', 'col_names': 'true', 'path': self.report_path, 'apikey': self.get_apikey()}
        payload_str = urllib.parse.urlencode(payload, safe=':%')

        try:  # Try to get the report from Alma
            response = requests.get(self.build_path(), params=payload_str)  # Get the report from Alma
            response.raise_for_status()  # Check for HTTP errors
        except Exception as e:  # Handle exceptions
            logging.error(e)
            raise

        return response


def get_report(region: str, iz: str, report_path: str) -> Report | None:
    """
    Get the report from Alma Analytics

    :return: requests.Response or None
    """

    api_call = ApiCall(region, iz, report_path)
    response = api_call.execute()

    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if soup.find('error'):  # Check for Alma errors
        logging.warning(f'Error: {soup.find("error").text}')
        return None

    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not columnlist:  # Check for columns
        logging.warning('No data columns in response.')
        return None

    columns = {}  # Create a dictionary of columns
    for column in columnlist:  # Add columns to the dictionary
        columns[column['name']] = column['saw-sql:columnHeading']

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

    return Report(
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': f'{iz.upper()} {os.getenv("DUPEBARCODES_REPORT_NAME")}',
                'columns': columns,
                'rows': rows
            }
        }
    )
