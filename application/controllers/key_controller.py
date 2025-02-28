"""
Controllers for key model.
"""
import logging
import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from application.controllers.exception_controller import check_exception
from application.models.key_sql import Key


def get_key(iz: int, area: int, write: int, session: scoped_session) -> str | None:
    """
    Get the API key to retrieve the report
    """
    if not check_exception(iz) or not check_exception(area):  # Check for empty values
        return None

    stmt = (  # Select the appropriate API key from the database
        select(Key)
        .where(Key.iz_id == iz)
        .where(Key.area_id == area)
        .where(Key.write == write)
    )

    try:
        apikey = session.scalars(stmt).one().key  # Execute the statement and get the result

    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No API key found: %s', e)  # log the error
        return None

    logging.debug('API key retrieved')  # Log success

    return apikey  # Return the API key
