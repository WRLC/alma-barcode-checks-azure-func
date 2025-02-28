"""
Controller for the Email model
"""
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import scoped_session
from application.controllers.exception_controller import check_exception
from application.models.analysis_sql import Analysis
from application.models.email import Email
from application.models.report import Report


def send_emails(report: Report, analysis: Analysis, session: scoped_session) -> None:
    """
    Send the email to the analysis's recipients

    :param report: Report
    :param analysis: Analysis
    :param session: Session object
    :return: None
    """
    email = construct_email(report)  # type:ignore[arg-type] # Construct the email

    if not check_exception(email):  # Check for empty or errors
        return

    recipients = analysis.recipients  # Get the analysis's recipients

    if not check_exception(recipients):  # Check for empty or errors
        return

    for recipient in recipients:  # Iterate through the analysis's recipients

        if not check_exception(recipient):  # Check for empty or errors
            return

        email.send(recipient.user.email, session)  # type:ignore[union-attr]  # Send email to recipient


def construct_email(report: Report) -> Email | None:
    """
    Construct the email object

    :param report: Report
    :return: Email or None
    """

    if not check_exception(report):  # Check for empty or errors
        return None

    try:
        body = render_template(  # Build the email body
            'email.html',  # template
            rows=report.data['data']['rows'],  # type:ignore[union-attr]  # rows
            columns=report.data['data']['columns'],  # type:ignore[union-attr]  # columns
            column_keys=list(report.data['data']['columns'].keys()),  # type:ignore[union-attr] # column keys
            title=report.data['data']['report_name'].upper()  # type:ignore[union-attr]  # IZ
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return None

    try:
        email = Email(  # Create the email object
            subject=f"{report.data['data']['report_name']}",  # type:ignore[union-attr]  # subject
            body=body  # body
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return None

    logging.debug('Email constructed: %s', email.subject)  # Log the email constructed

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

    logging.debug('Email rendered')  # log the template rendered

    return template.render(**kwargs)  # render the template with the variables passed in
