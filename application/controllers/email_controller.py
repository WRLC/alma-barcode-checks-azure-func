"""
Controller for the Email model
"""
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from application.controllers.exception_controller import check_exception
from application.controllers.report_controller import get_report
from application.models.analysis_sql import Analysis
from application.models.email import Email


def construct_email(analysis: Analysis) -> Email | Exception | None:
    """
    Construct the email object

    :param analysis: Analysis
    :return: Email or None
    """
    report = get_report(analysis)  # Get the report from Alma Analytics

    if not check_exception(report) or isinstance(check_exception(report), Exception):  # Check for empty or errors
        return check_exception(report)  # Return the error or None

    try:
        body = render_template(  # Build the email body
            'email.html',  # template
            rows=report.data['data']['rows'],  # rows
            columns=report.data['data']['columns'],  # columns
            column_keys=list(report.data['data']['columns'].keys()),  # type:ignore[union-attr] # column keys
            title=report.data['data']['report_name'].upper()  # IZ
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return KeyError(e)

    try:
        email = Email(  # Create the email object
            subject=f"{report.data['data']['report_name']}",  # subject
            body=body  # body
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return KeyError(e)

    return email


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
