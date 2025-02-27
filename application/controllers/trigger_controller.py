"""
Controllers for trigger model.
"""
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.trigger_sql import Trigger


def get_trigger(code: str) -> Trigger:
    """
    Get trigger from database by name.

    :param code: Trigger code
    :return: Trigger object
    """
    session = Session(engine)  # Create a Session object

    stmt = select(Trigger).where(Trigger.code == code)  # Select the trigger from the database
    trigger = session.scalars(stmt).one()  # Execute the statement and get the result

    logging.debug('Trigger retrieved: %s', code)  # Log success

    return trigger
