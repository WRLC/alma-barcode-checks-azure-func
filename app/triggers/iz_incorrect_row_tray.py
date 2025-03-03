"""
Barcodes with incorrect row/tray in all IZs
"""
import logging
import azure.functions as func
from sqlalchemy.orm import scoped_session
from app.controllers.analysis_controller import get_trigger_analyses
from app.controllers.email_controller import send_emails
from app.controllers.exception_controller import check_exception
from app.controllers.report_controller import get_report
from app.extensions import session_factory

app = func.Blueprint()  # Create a Blueprint object


# noinspection PyUnusedLocal
@app.function_name(name="izincorrectrowtray")
@app.timer_trigger(
    schedule="0 30 14 1 * *",  # type:ignore[arg-type]  # Run at 14:30 on the first day of every month
    arg_name="izincorrectrowtray"
)
def main(izincorrectrowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with incorrect row/tray in all IZs and send email notification.

    :param izincorrectrowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'iz_incorrect_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session
