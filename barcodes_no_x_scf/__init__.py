"""
Barcodes No X SCF Azure Function
"""
import logging
import os
import azure.functions as func
from shared.analytics_utils import get_report
from shared.email_utils import construct_email

app = func.Blueprint()  # Create a Blueprint object

if not os.getenv("BARCODESNOXSCF_CRON_FREQUENCY"):  # Check if frequency is set
    logging.error("BARCODESNOXSCF_CRON_FREQUENCY not set")  # Log error if not set
    raise ValueError("BARCODESNOXSCF_CRON_FREQUENCY not set")  # Raise error if not set

frequency = os.getenv("BARCODESNOXSCF_CRON_FREQUENCY")  # Get the frequency from the environment variable


# noinspection PyUnusedLocal
@app.function_name(name="barcodesnoxscf")
@app.timer_trigger(schedule=frequency, run_on_startup=True, arg_name="barcodesnoxscf")  # type:ignore[arg-type]
def main(barcodesnoxscf: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    This function is triggered by a timer trigger. It gets a report from Alma Analytics, extracts the data rows and
    column headings, builds an email body using a Jinja template, and sends the email. It also updates the records in
    Alma with the new barcode.

    :param barcodesnoxscf: TimerRequest
    :return: None
    """
    if not os.getenv("BARCODESNOXSCF_REGION"):
        logging.error("BARCODESNOXSCF_REGION not set")
        raise ValueError("BARCODESNOXSCF_REGION not set")

    if not os.getenv("BARCODESNOXSCF_IZ"):
        logging.error("BARCODESNOXSCF_IZ not set")
        raise ValueError("BARCODESNOXSCF_IZ not set")

    if not os.getenv("BARCODESNOXSCF_REPORT_PATH"):
        logging.error("BARCODESNOXSCF_REPORT_PATH not set")
        raise ValueError("BARCODESNOXSCF_REPORT_PATH not set")

    if not os.getenv("BARCODESNOXSCF_REPORT_NAME"):
        logging.error("BARCODESNOXSCF_REPORT_NAME not set")
        raise ValueError("BARCODESNOXSCF_REPORT_NAME not set")

    report = get_report(  # Get the report from Alma Analytics
        os.getenv("BARCODESNOXSCF_REGION"),  # type:ignore[arg-type] # region
        os.getenv("BARCODESNOXSCF_IZ"),  # type:ignore[arg-type] # IZ
        os.getenv("BARCODESNOXSCF_REPORT_PATH"),  # type:ignore[arg-type] # report path
        os.getenv("BARCODESNOXSCF_REPORT_NAME")  # type:ignore[arg-type] # report name
    )

    if not report:
        return  # If the report is empty, return

    # report.fix_missing_x_scf()  # Fix the missing X SCF barcodes

    email = construct_email(report)  # Construct the email

    if not email:
        return  # If the email is empty, return

    email.send()
