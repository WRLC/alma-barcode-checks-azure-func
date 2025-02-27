"""
Controllers for key model.
"""
import logging
import sqlalchemy.exc

from sqlalchemy import select
from sqlalchemy.orm import Session, Mapped
from application.extensions import engine
from application.models.key_sql import Key


def get_key(iz: int, area: Mapped[int], write: int) -> str | Exception | None:
    """
    Get the API key to retrieve the report
    """
    if not iz or not area or not write:  # Check for empty values
        logging.warning('Missing API key parameters')
        return None

    session = Session(engine)  # Create a Session object

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
        return e  # return the error

    return apikey  # Return the API key
