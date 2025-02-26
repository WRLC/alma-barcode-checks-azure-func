"""
Controller for the Email model
"""
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from application.controllers.analysis_controller import get_report
from application.models.analysis_sql import Analysis
from application.models.email import Email


def construct_email(analysis: Analysis) -> Email:
    """
    Construct the email object

    :param analysis: Analysis
    :return: Email or None
    """
    report = get_report(analysis)  # Get the report from Alma Analytics

    body = render_template(  # Build the email body
        'email.html',  # template
        rows=report.data['data']['rows'],  # rows
        columns=report.data['data']['columns'],  # columns
        column_keys=list(report.data['data']['columns'].keys()),  # type:ignore[union-attr] # column keys
        title=report.data['data']['report_name'].upper()  # IZ
    )

    email = Email(  # Create the email object
        subject=f"{report.data['data']['report_name']}",  # subject
        body=body  # body
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
        loader=FileSystemLoader('application/templates'),  # load the templates from the templates directory
        autoescape=select_autoescape(['html', 'xml'])  # autoescape html and xml
    )

    template = env.get_template(template)  # get the template

    logging.info('Email rendered')  # log the template rendered

    return template.render(**kwargs)  # render the template with the variables passed in
