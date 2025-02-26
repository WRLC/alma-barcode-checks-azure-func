"""
Duplicate barcodes in SCF
"""
import azure.functions as func
from application.controllers.email_controller import construct_email
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
    for analysis in get_trigger('scf_duplicate').analyses:  # Iterate through the trigger's analyses

        email = construct_email(analysis)  # Construct the email

        for recipient in analysis.recipients:  # Iterate through the analysis's recipients
            email.send(recipient.user.email)  # Send email to recipient
