"""
Barcodes with no row/tray in SCF.
"""
import logging
import azure.functions as func
from sqlalchemy.orm import sessionmaker, scoped_session
from application.controllers.analysis_controller import get_trigger_analyses
from application.controllers.email_controller import send_emails
from application.controllers.exception_controller import check_exception
from application.controllers.report_controller import get_report
from application.extensions import engine

app = func.Blueprint()  # Create a Blueprint object


# noinspection PyUnusedLocal
@app.function_name(name="iznorowtray")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]
    arg_name="scfnorowtray"
)
def main(iznorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in SCF and send email notification.

    :param iznorowtray: TimerRequest
    :return: None
    """
    session_factory = sessionmaker(engine)  # Create a session factory
    session = scoped_session(session_factory)  # Create a session

    code = 'iz_no_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.trigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session
