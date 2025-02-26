"""
Barcodes with no row/tray in SCF.
"""
import os
import azure.functions as func
from application.controllers.analysis_controller import get_report
from application.controllers.email_controller import construct_email

app = func.Blueprint()  # Create a Blueprint object

envs = {  # List of environment variables to check
    "region": "ALMA_REGION",  # region
    "from": "EMAIL_FROM",  # sender
    "frequency": "BARCODESNOROWTRAYSCF_CRON_FREQUENCY",  # frequency
    "iz": "BARCODESNOROWTRAYSCF_IZ",  # IZ
    "path": "BARCODESNOROWTRAYSCF_REPORT_PATH",  # report path
    "name": "BARCODESNOROWTRAYSCF_REPORT_NAME",  # report name
    "to": "BARCODESNOROWTRAYSCF_EMAIL_TO"  # recipient(s)
}


# noinspection PyUnusedLocal
@app.function_name(name="barcodesnorowtrayscf")
@app.timer_trigger(
    schedule=os.getenv(envs['frequency']),  # type:ignore[arg-type]
    run_on_startup=False,
    arg_name="barcodesnorowtrayscf"
)
def main(
        barcodesnorowtrayscf: func.TimerRequest  # type:ignore[unused-argument]  # pylint:disable=unused-argument
) -> None:
    """
    Get report of barcodes with no row/tray in SCF and send email notification.

    :param barcodesnorowtrayscf: TimerRequest
    :return: None
    """
    report = get_report(envs)  # Get the report from Alma Analytics
    if not report:
        return  # If the report is empty, return

    email = construct_email(report, envs)  # Construct the email
    if not email:
        return  # If the email is empty, return

    email.send()  # Send the email
