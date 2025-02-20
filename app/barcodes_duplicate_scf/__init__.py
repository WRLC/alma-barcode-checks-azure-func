"""
Duplicate barcodes in SCF
"""
import os
import azure.functions as func
from shared import check_envs
from shared.report import get_report
from shared.email import construct_email

app = func.Blueprint()  # Create a Blueprint object

envs = {  # List of environment variables to check
    "region": "ALMA_REGION",  # region
    "from": "EMAIL_FROM",  # sender
    "frequency": "DUPEBARCODES_CRON_FREQUENCY",  # frequency
    "iz": "DUPEBARCODES_IZ",  # IZ
    "path": "DUPEBARCODES_REPORT_PATH",  # report path
    "name": "DUPEBARCODES_REPORT_NAME",  # report name
    "to": "DUPEBARCODES_EMAIL_TO"  # recipient(s)
}

check_envs(envs)  # Check if the environment variables are set


# noinspection PyUnusedLocal
@app.function_name(name="dupebarcodes")
@app.timer_trigger(
    schedule=os.getenv(envs['frequency']),  # type:ignore[arg-type]
    run_on_startup=False,
    arg_name="dupebarcodes"
)
def main(dupebarcodes: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of duplicate barcodes in SCF and send email notification.

    :param dupebarcodes: TimerRequest
    :return: None
    """

    report = get_report(envs)  # Get the report from Alma Analytics
    if not report:
        return  # If the report is empty, return

    email = construct_email(report, envs)  # Construct the email
    if not email:
        return  # If the email is empty, return

    email.send()  # Send the email
