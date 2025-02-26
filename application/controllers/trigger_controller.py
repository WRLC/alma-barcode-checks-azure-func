"""
Controllers for trigger model.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.trigger_sql import Trigger


def get_trigger(name: str) -> Trigger:
    """
    Get trigger from database by name.

    :param name: Trigger name
    :return: Trigger object
    """
    session = Session(engine)  # Create a Session object

    stmt = select(Trigger).where(Trigger.name == name)  # Select the trigger from the database
    trigger = session.scalars(stmt).one()  # Execute the statement and get the result

    return trigger
