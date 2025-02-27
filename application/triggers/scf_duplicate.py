"""
Duplicate barcodes in SCF
"""
import logging

import azure.functions as func
from application.controllers.email_controller import construct_email
from application.controllers.exception_controller import check_exception
from application.controllers.trigger_controller import get_trigger

app = func.Blueprint()  # Create a Blueprint object


# noinspection PyUnusedLocal
@app.function_name(name="scfduplicate")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]
    arg_name="scfduplicate"
)
def main(scfduplicate: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of duplicate barcodes in SCF and send email notification.

    :param scfduplicate: TimerRequest
    :return: None
    """
    trigger = get_trigger('scf_duplicate')  # Get the trigger

    if not check_exception(trigger) or isinstance(trigger, Exception):  # Check for empty or errors
        logging.warning("Trigger is empty or has an error")  # Log a warning
        return  # Skip the trigger if there is an error

    analyses = trigger.analyses  # Get the trigger's analyses

    if not check_exception(analyses) or isinstance(analyses, Exception):  # Check for empty or errors
        logging.warning("Analyses are empty or have an error")  # Log a warning
        return  # Skip the trigger if there is an error

    for analysis in analyses:  # Iterate through the trigger's analyses

        if not check_exception(analysis) or isinstance(analysis, Exception):  # Check for empty or errors
            logging.warning("Analysis is empty or has an error")  # Log a warning
            continue  # Skip the analysis if there is an error

        email = construct_email(analysis)  # Construct the email

        if not check_exception(email) or isinstance(email, Exception):  # Check for empty or errors
            logging.warning("Email is empty or has an error")  # Log a warning
            continue  # Skip the email if there is an error

        recipients = analysis.recipients  # Get the analysis's recipients

        if not check_exception(recipients) or isinstance(recipients, Exception):  # Check for empty or errors
            logging.warning("Recipients are empty or have an error")
            continue  # Skip the recipients if there is an error

        for recipient in recipients:  # Iterate through the analysis's recipients

            if not check_exception(recipient) or isinstance(recipient, Exception):  # Check for empty or errors
                logging.warning("Recipient is empty or has an error")
                continue  # Skip the recipient if there is an error

            email.send(recipient.user.email)  # type:ignore[union-attr]  # Send email to recipient
