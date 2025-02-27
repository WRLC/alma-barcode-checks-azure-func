"""
Barcodes with No X in SCF
"""
import azure.functions as func
from application.controllers.trigger_controller import get_trigger
from application.controllers.email_controller import construct_email

app = func.Blueprint()  # Create a Blueprint object


# noinspection PyUnusedLocal
@app.function_name(name="scfnox")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]
    arg_name="scfnox"
)
def main(scfnox: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of barcodes with no X in SCF, fix records in Alma, and send email notification.

    :param scfnox: TimerRequest
    :return: None
    """
    for analysis in get_trigger('scf_no_x').analyses:  # Iterate through the trigger's analyses

        email = construct_email(analysis)  # Construct the email

        # TODO: Fix records in Alma  # pylint:disable=fixme

        for recipient in analysis.recipients:  # Iterate through the analysis's recipients

            email.send(recipient.user.email)  # Send email to recipient
