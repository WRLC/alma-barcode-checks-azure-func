"""
This function is triggered by a timer trigger. It gets a report from Alma Analytics, extracts the data rows and column
headings, builds an email body using a Jinja template, and sends the email
"""
import logging
import os
import azure.functions as func
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests

load_dotenv()  # Load the environment variables

app = func.FunctionApp()  # Create the FunctionApp object


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

    def send(self) -> None:
        """
        Send the email to webhook

        :return: None
        """
        try:
            response = requests.post(
                url=os.getenv('MAIL_WEBHOOK_URL'),
                json={
                    "subject": self.subject,
                    "body": self.body,
                    "to": self.to,
                    "sender": self.sender
                }
            )
        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {e}')
            raise SystemExit(0)

        if response.status_code != 200:
            logging.error(f'Error: {response.status_code}: {response.text}')
            raise SystemExit(0)


# noinspection PyUnusedLocal
@app.function_name(name="dupebarcodes")
@app.timer_trigger(schedule="0 0 6 1 * *", arg_name="dupebarcodes")
def dupe_barcodes(dupebarcodes: func.TimerRequest) -> None:
    """
    This function is triggered by a timer trigger. It gets a report from Alma Analytics, extracts the data rows and
    column headings, builds an email body using a Jinja template, and sends the email

    :param dupebarcodes: TimerRequest
    :return: None
    """
    response = get_report()  # Get the report from Alma Analytics

    if response is None:  # If no response, exit
        raise SystemExit(0)

    rows = get_rows(response) if get_rows(response) else None  # Get the data rows
    columns = get_columns(response) if get_columns(response) else None  # Get the column headings

    if not rows or not columns:  # If no data, exit
        raise SystemExit(0)

    body = render_template(  # Build the email body
        'email.html',  # template
        rows=rows,  # rows
        columns=columns,  # columns
        iz=os.getenv('ANALYTICS_IZ').upper()  # IZ
    )

    email = Email(  # Create the email object
        subject=f"{os.getenv('ANALYTICS_IZ').upper()} Duplicate Barcode Report",  # subject
        body=body,  # body
        to=os.getenv('EMAIL_TO'),  # recipient(s)
        sender=os.getenv('EMAIL_SENDER'),  # sender
    )

    email.send()  # Send the email
    logging.info(f'Email sent to {email.to}')  # Log the email sent


def get_report() -> requests.Response or None:
    """
    Get the report from Alma Analytics

    :return: requests.Response or None
    """
    # Get the report from Alma Analytics
    try:
        response = requests.post(  # POST request with JSON payload
            os.getenv('ANALYTICS_URL'),  # URL
            json={
                "path": os.getenv('ANALYTICS_PATH'),  # Path
                "iz": os.getenv('ANALYTICS_IZ'),  # IZ
                "region": os.getenv('ANALYTICS_REGION'),  # Region
            }
        )
    except requests.exceptions.RequestException as e:  # Handle exceptions
        logging.error(f'Error: {e}')  # Log the error
        return None  # Return None

    if response.status_code != 200:  # If not a 200 status code
        logging.error(f'Error: {response.status_code}: {response.text}')  # Log the error
        return None  # Return None

    return response


def get_rows(response) -> list or None:
    """
    Get the data rows from the report

    :param response: requests.Response
    :return: list or None
    """
    return response.json()['data']['rows']  # Get the data rows


def get_columns(response) -> list or None:
    """
    Get the column headings from the report

    :param response: requests.Response
    :return: list or None
    """
    return response.json()['data']['columns']  # Get the column headings


def render_template(template, **kwargs) -> str:
    """
    Render a Jinja template with the variables passed in

    :param template: str
    :param kwargs: dict
    :return: str
    """
    env = Environment(  # create the environment
        loader=FileSystemLoader('templates'),  # load the templates from the templates directory
        autoescape=select_autoescape(['html', 'xml'])  # autoescape html and xml
    )
    template = env.get_template(template)  # get the template
    return template.render(**kwargs)  # render the template with the variables passed in
