"""
Email model
"""
import logging
import requests  # type: ignore[import-untyped]
from requests.auth import HTTPBasicAuth  # type:ignore[import-untyped]
from sqlalchemy.orm import scoped_session
from app.controllers.config_controller import get_config


class Email:
    """
    Email object
    """
    def __init__(self, subject: str, body: str) -> None:
        """
        Email object

        :param subject: str
        :param body: str
        :return: None
        """
        self.subject = subject
        self.body = body

    def __str__(self) -> str:
        """
        Return the email as a string

        :return: str
        """
        return f"Subject: {self.subject}\n\n{self.body}"

    def send(self, to: str, session: scoped_session) -> None:
        """
        Send the email to webhook

        :return: None
        """
        # Create the basic auth object
        basic = HTTPBasicAuth(get_config('webhook_user', session), get_config('webhook_pass', session))

        try:  # Try to send the email
            response = requests.post(  # Send the email
                url=get_config('webhook_url', session),
                json={
                    "subject": self.subject,
                    "body": self.body,
                    "to": to,
                    "sender": get_config('sender_email', session)
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

        logging.info('Email sent to %s: %s', to, self.subject)
