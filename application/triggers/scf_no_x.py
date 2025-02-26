"""
Barcodes with No X in SCF
"""
import os
import azure.functions as func
from application.controllers.analysis_controller import get_report
from application.controllers.email_controller import construct_email

app = func.Blueprint()  # Create a Blueprint object

envs = {  # List of environment variables to check
    "region": "ALMA_REGION",  # region
    "from": "EMAIL_FROM",  # sender
    "frequency": "BARCODESNOXSCF_CRON_FREQUENCY",  # frequency
    "iz": "BARCODESNOXSCF_IZ",  # IZ
    "path": "BARCODESNOXSCF_REPORT_PATH",  # report path
    "name": "BARCODESNOXSCF_REPORT_NAME",  # report name
    "to": "BARCODESNOXSCF_EMAIL_TO"  # recipient(s)
}


# noinspection PyUnusedLocal
@app.function_name(name="barcodesnoxscf")
@app.timer_trigger(
    schedule=os.getenv(envs['frequency']),  # type:ignore[arg-type]
    run_on_startup=False,
    arg_name="barcodesnoxscf"
)
def main(barcodesnoxscf: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of barcodes with no X in SCF, fix records in Alma, and send email notification.

    :param barcodesnoxscf: TimerRequest
    :return: None
    """
    report = get_report(envs)  # Get the report from Alma Analytics

    if not report:
        return  # If the report is empty, return

    # report.fix_missing_x_scf()  # Fix the missing X SCF barcodes

    email = construct_email(report, envs)  # Construct the email

    if not email:
        return  # If the email is empty, return

    email.send()
