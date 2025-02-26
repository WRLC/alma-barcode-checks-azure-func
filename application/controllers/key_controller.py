"""
Controllers for key model.
"""
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.key_sql import Key


def get_key(iz: int, area: int, write: int) -> str:
    """
    Get the API key to retrieve the report
    """
    session = Session(engine)  # Create a Session object

    try:
        stmt = (  # Select the appropriate API key from the database
            select(Key)
            .where(Key.iz_id == iz)
            .where(Key.area_id == area)
            .where(Key.write == write)
        )
        apikey = session.scalars(stmt).one().key  # Execute the statement and get the result

    except Exception as e:  # Handle exceptions
        logging.error('Error: %s', e)  # log the error
        raise  # re-raise the exception

    return apikey  # Return the API key
