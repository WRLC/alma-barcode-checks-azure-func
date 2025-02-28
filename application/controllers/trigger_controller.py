"""
Controllers for trigger model.
"""
import logging

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from application.models.trigger_sql import Trigger


def get_trigger(code: str, session: scoped_session) -> Trigger | None:
    """
    Get trigger from database by name.

    :param code: Trigger code
    :param session: Session object
    :return: Trigger object
    """
    if not code:  # Check for empty values
        logging.error('Missing trigger code parameter')
        return None

    stmt = select(Trigger).where(Trigger.code == code)  # Select the trigger from the database
    try:
        trigger = session.scalars(stmt).one()  # Execute the statement and get the result
    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No trigger %s found: %s', code, e)
        return None

    logging.debug('Trigger retrieved: %s', code)  # Log success

    return trigger
