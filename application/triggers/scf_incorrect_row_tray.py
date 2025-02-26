"""
Barcodes with incorrect row/tray in SCF
"""
import os
import azure.functions as func
from application.controllers.analysis_controller import get_report
from application.controllers.email_controller import construct_email

app = func.Blueprint()  # Create a Blueprint object

envs = {  # List of environment variables to check
    "region": "ALMA_REGION",  # region
    "from": "EMAIL_FROM",  # sender
    "frequency": "BARCODESINCORRECTROWTRAYSCF_CRON_FREQUENCY",  # frequency
    "iz": "BARCODESINCORRECTROWTRAYSCF_IZ",  # IZ
    "path": "BARCODESINCORRECTROWTRAYSCF_REPORT_PATH",  # report path
    "name": "BARCODESINCORRECTROWTRAYSCF_REPORT_NAME",  # report name
    "to": "BARCODESINCORRECTROWTRAYSCF_EMAIL_TO"  # recipient(s)
}


# noinspection PyUnusedLocal
@app.function_name(name="barcodesincorrectrowtrayscf")
@app.timer_trigger(
    schedule=os.getenv(envs['frequency']),  # type:ignore[arg-type]
    run_on_startup=False,
    arg_name="barcodesincorrectrowtrayscf"
)
def main(
        barcodesincorrectrowtrayscf: func.TimerRequest  # type:ignore[unused-argument]  # pylint:disable=unused-argument
) -> None:
    """
    Get report of barcodes with incorrect row/tray in SCF and send email notification.

    :param barcodesincorrectrowtrayscf: TimerRequest
    :return: None
    """
    report = get_report(envs)  # Get the report from Alma Analytics
    if not report:
        return  # If the report is empty, return

    email = construct_email(report, envs)  # Construct the email
    if not email:
        return

    email.send()  # Send the email
