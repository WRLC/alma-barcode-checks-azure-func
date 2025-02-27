"""
Barcodes with no row/tray in SCF.
"""
import azure.functions as func
from application.controllers.email_controller import construct_email
from application.controllers.trigger_controller import get_trigger

app = func.Blueprint()  # Create a Blueprint object


# noinspection PyUnusedLocal
@app.function_name(name="scfnorowtray")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]
    arg_name="scfnorowtray"
)
def main(scfnorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in SCF and send email notification.

    :param scfnorowtray: TimerRequest
    :return: None
    """
    for analysis in get_trigger('scf_no_row_tray').analyses:  # Iterate through the trigger's analyses

        email = construct_email(analysis)  # Construct the email

        for recipient in analysis.recipients:  # Iterate through the analysis's recipients

            email.send(recipient.user.email)  # Send the email
