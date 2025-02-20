"""
Email module
"""
import logging
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from shared.report.models.report import Report
from shared.email.models.email import Email

load_dotenv()


def construct_email(response: Report, envs: dict[str, str]) -> Email | None:
    """
    Construct the email object

    :param response: Report
    :param envs: dict[str, str]
    :return: Email or None
    """
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
        to=os.getenv(envs['to']),  # type:ignore # recipient(s)
        sender=os.getenv(envs['from']),  # type:ignore  # sender
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
