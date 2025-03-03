"""
Controllers for key model.
"""
import logging
import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from app.controllers.exception_controller import check_exception
from app.models.apikey_sql import Apikey


def get_key(iz: int, area: int, write: int, session: scoped_session) -> str | None:
    """
    Get the API key to retrieve the report
    """
    if not check_exception(iz) or not check_exception(area):  # Check for empty values
        return None

    stmt = (  # Select the appropriate API key from the database
        select(Apikey)
        .where(Apikey.iz_id == iz)
        .where(Apikey.area_id == area)
        .where(Apikey.writekey == write)
    )

    try:
        apikey = session.scalars(stmt).one().apikey  # Execute the statement and get the result

    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No API key found: %s', e)  # log the error
        return None

    logging.debug('API key retrieved')  # Log success

    return apikey  # Return the API key
