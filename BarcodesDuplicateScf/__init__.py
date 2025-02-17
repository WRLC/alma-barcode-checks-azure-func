import logging
import os
import azure.functions as func
from shared.analytics_utils import get_report
from shared.email_utils import construct_email

app = func.Blueprint()  # Create a Blueprint object

if not os.getenv("DUPEBARCODES_CRON_FREQUENCY"):  # Check if frequency is set
    logging.error("DUPEBARCODES_CRON_FREQUENCY not set")  # Log error if not set
    raise ValueError("DUPEBARCODES_CRON_FREQUENCY not set")  # Raise error if not set

frequency = os.getenv("DUPEBARCODES_CRON_FREQUENCY")  # Get the frequency from the environment variable


# noinspection PyUnusedLocal
@app.function_name(name="dupebarcodes")
@app.timer_trigger(schedule="0 0 6 1 * *", run_on_startup=True, arg_name="dupebarcodes")
def main(dupebarcodes: func.TimerRequest) -> None:
    """
    This function is triggered by a timer trigger. It gets a report from Alma Analytics, extracts the data rows and
    column headings, builds an email body using a Jinja template, and sends the email

    :param dupebarcodes: TimerRequest
    :return: None
    """
    if not os.getenv("DUPEBARCODES_REGION"):  # Check if region is set
        logging.error("DUPEBARCODES_REGION not set")  # Log error if not set
        raise ValueError("DUPEBARCODES_REGION not set")  # Raise error if not set

    if not os.getenv("DUPEBARCODES_IZ"):  # Check if IZ is set
        logging.error("DUPEBARCODES_IZ not set")  # Log error if not set
        raise ValueError("DUPEBARCODES_IZ not set")  # Raise error if not set

    if not os.getenv("DUPEBARCODES_REPORT_PATH"):  # Check if report path is set
        logging.error("DUPEBARCODES_REPORT_PATH not set")  # Log error if not set
        raise ValueError("DUPEBARCODES_REPORT_PATH not set")  # Raise error if not set

    report = get_report(  # Get the report from Alma Analytics
        os.getenv("DUPEBARCODES_REGION"),  # region
        os.getenv("DUPEBARCODES_IZ"),  # IZ
        os.getenv("DUPEBARCODES_REPORT_PATH")  # report path
    )

    if not report:
        return  # If the report is empty, return

    email = construct_email(report)  # Construct the email

    if not email:
        return  # If the email is empty, return

    email.send()  # Send the email
