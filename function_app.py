"""
This file is used to register the function apps with the Azure Functions host.
"""
import logging
import azure.functions as func
from sqlalchemy.orm import scoped_session
from controllers import get_report, get_trigger_analyses, check_exception, send_emails
from models import session_factory

app = func.FunctionApp()  # Create a new FunctionApp instance


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="izincorrectrowtray")
@app.timer_trigger(
    schedule="0 30 14 1 * *",  # type:ignore[arg-type]  # Run at 14:30 on the first day of every month
    arg_name="izincorrectrowtray"
)
# pylint:disable=unused-argument
def iz_incorrect_row_tray(izincorrectrowtray: func.TimerRequest) -> None:  # type:ignore
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


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="iznorowtray")
@app.timer_trigger(
    schedule="0 0 14 1 * *",  # type:ignore[arg-type]  # Run at 14:00 on the first day of every month
    arg_name="iznorowtray"
)
def iz_no_row_tray(iznorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in all IZs and send email notification.

    :param iznorowtray: TimerRequest
    :return: None
    """
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
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        # TODO: Fix Alma records

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfduplicate")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]  # Run at 12:00 on the first day of every month
    arg_name="scfduplicate"
)
# pylint: disable=unused-argument
def scf_duplicate(scfduplicate: func.TimerRequest) -> None:  # type:ignore[unused-argument]
    """
    Get report of duplicate barcodes in SCF and send email notification.

    :param scfduplicate: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_duplicate'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        session.remove()
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


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfincorrectrowtray")
@app.timer_trigger(
    schedule="0 30 13 1 1,7 *",  # type:ignore[arg-type]  # Run at 13:30 on the first day of January and July
    arg_name="scfincorrectrowtray"
)
# pylint:disable=unused-argument
def scf_incorrect_row_tray(scfincorrectrowtray: func.TimerRequest) -> None:  # type:ignore
    """
    Get report of barcodes with incorrect row/tray in SCF and send email notification.

    :param scfincorrectrowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_incorrect_row_tray'  # Trigger code

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


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfnorowtray")
@app.timer_trigger(
    schedule="0 0 13 1 1,7 *",  # type:ignore[arg-type]  # Run at 13:00 on the first day of January and July
    arg_name="scfnorowtray"
)
def scf_no_row_tray(scfnorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in SCF and send email notification.

    :param scfnorowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_no_row_tray'  # Trigger code

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


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfnox")
@app.timer_trigger(
    schedule="0 30 12 1 * *",  # type:ignore[arg-type]  # Run at 12:30 on the first day of every month
    arg_name="scfnox"
)
def scf_no_x(scfnox: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of barcodes with no X in SCF, fix records in Alma, and send email notification.

    :param scfnox: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_no_x'  # Trigger code

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

        # TODO: Fix Alma records

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfwithdrawn")
@app.timer_trigger(
    schedule="0 0 11 1 7 *",  # type:ignore[arg-type]  # Run at 11:00 on the first day of July
    arg_name="scfwithdrawn"
)
def scf_withdrawn(scfwithdrawn: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes marked withdrawn in SCF and send email notification.

    :param scfwithdrawn: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_withdrawn'  # Trigger code

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

        # TODO: Separate emails for each Provenance Code

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session
