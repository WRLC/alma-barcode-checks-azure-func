"""
Email model
"""
import logging
import os
from dotenv import load_dotenv
import requests  # type: ignore[import-untyped]
from requests.auth import HTTPBasicAuth  # type:ignore[import-untyped]
from shared import check_envs

load_dotenv()


class Email:
    """
    Email object
    """
    def __init__(self, subject: str, body: str, to: str, sender: str) -> None:
        """
        Email object

        :param subject: str
        :param body: str
        :param to: str
        :param sender: str
        :return: None
        """
        self.subject = subject
        self.body = body
        self.to = to
        self.sender = sender

    def __str__(self) -> str:
        """
        Return the email as a string

        :return: str
        """
        return f"Subject: {self.subject}\n\n{self.body}"

    def send(self) -> None:
        """
        Send the email to webhook

        :return: None
        """
        envs = {  # List of environment variables to check
            "url": "WEBHOOK_URL",  # webhook URL
            "user": "WEBHOOK_USER",  # webhook user
            "pass": "WEBHOOK_PASS"  # webhook password
        }

        check_envs(envs)  # Check if the environment variables are set

        basic = HTTPBasicAuth(os.getenv(envs['user']), os.getenv(envs['pass']))  # Create the basic auth object

        try:  # Try to send the email
            response = requests.post(  # Send the email
                url=os.getenv(envs['url']),
                json={
                    "subject": self.subject,
                    "body": self.body,
                    "to": self.to,
                    "sender": self.sender
                },
                timeout=10,
                auth=basic
            )

        except requests.exceptions.RequestException as e:  # Handle request exceptions
            logging.error('Error: %s', e)  # If there is an error, log it
            raise  # If there is an error, raise it

        if response.status_code != 201:  # Check if the response status code is not 201
            logging.error('Error: %s: %s', response.status_code, response.text)  # If not, log error
            raise requests.exceptions.RequestException(  # If not, raise an error
                f'Error: {response.status_code}: {response.text}'
            )
