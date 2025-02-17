"""
Shared utility functions for sending emails
"""
import logging
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests  # type: ignore[import-untyped]
from requests.auth import HTTPBasicAuth  # type:ignore[import-untyped]

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
        if not os.getenv('WEBHOOK_URL'):  # Check if webhook URL is set
            logging.error('No webhook URL provided')  # If not, log error
            raise ValueError('No webhook URL provided')  # If not, raise error

        if not os.getenv('WEBHOOK_USER'):  # Check if webhook user is set
            logging.error('No webhook user provided')  # If not, log error
            raise ValueError('No webhook user provided')  # If not, raise error

        if not os.getenv('WEBHOOK_PASS'):  # Check if webhook password is set
            logging.error('No webhook password provided')  # If not, log error
            raise ValueError('No webhook password provided')  # If not, raise error

        basic = HTTPBasicAuth(os.getenv('WEBHOOK_USER'), os.getenv('WEBHOOK_PASS'))  # Create the basic auth object

        try:  # Try to send the email
            response = requests.post(  # Send the email
                url=os.getenv('WEBHOOK_URL'),
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


def construct_email(response) -> Email | None:
    """
    Construct the email object
    """
    if not os.getenv('EMAIL_TO'):  # Check if to email address is set
        logging.error('No email address provided')
        raise ValueError('No to email address provided')  # If not, raise an error

    if not os.getenv('EMAIL_SENDER'):  # Check if sender email address is set
        logging.error('No email address provided')  # If not, log an error
        raise ValueError('No sender email address provided')  # If not, raise an error

    rows = get_rows(response) if get_rows(response) else None  # Get the data rows

    columns = get_columns(response) if get_columns(response) else None  # Get the column headings

    body = render_template(  # Build the email body
        'email.html',  # template
        rows=rows,  # rows
        columns=columns,  # columns
        column_keys=list(columns.keys()),  # type:ignore[union-attr] # column keys
        title=response.data['data']['report_name'].upper()  # IZ
    )

    email = Email(  # Create the email object
        subject=f"{response.data['data']['report_name']}",  # subject
        body=body,  # body
        to=os.getenv('EMAIL_TO'),  # type:ignore # recipient(s)
        sender=os.getenv('EMAIL_SENDER'),  # type:ignore  # sender
    )

    return email


def get_rows(response) -> list or None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param response: requests.Response
    :return: list or None
    """
    return response.data['data']['rows']  # Get the data rows


def get_columns(response) -> list or None:  # type:ignore[valid-type]
    """
    Get the column headings from the report

    :param response: requests.Response
    :return: list or None
    """
    return response.data['data']['columns']  # Get the column headings


def render_template(template, **kwargs) -> str:
    """
    Render a Jinja template with the variables passed in

    :param template: str
    :param kwargs: dict
    :return: str
    """
    env = Environment(  # create the environment
        loader=FileSystemLoader('shared/templates'),  # load the templates from the templates directory
        autoescape=select_autoescape(['html', 'xml'])  # autoescape html and xml
    )

    template = env.get_template(template)  # get the template

    logging.info('Email rendered')  # log the template rendered

    return template.render(**kwargs)  # render the template with the variables passed in
