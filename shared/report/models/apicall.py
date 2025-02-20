"""
ApiCall model
"""
import logging
import os
import urllib.parse
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import requests  # type:ignore[import-untyped]


class ApiCall:
    """
    An object to create and execute an API call.
    """
    def __init__(self, region: str, iz: str, report_path: str) -> None:
        """
        Initialize the API call object.

        :param region: The region code.
        :param iz: The institution code.
        :param report_path: The path to the report.
        :return: None
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
    def get_apikey(self) -> str | None:
        """
        Get the API key from the Azure Key Vault.

        :return: The API key or None.
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
            response = requests.get(self.build_path(), params=payload_str, timeout=300)  # Get the report from Alma
            response.raise_for_status()  # Check for HTTP errors
        except Exception as e:  # Handle exceptions
            logging.error(e)
            raise

        return response
