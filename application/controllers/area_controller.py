"""
Controllers for area model.
"""
import logging
import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from application.models.area_sql import Area


def get_area_by_name(name: str, session: scoped_session) -> Area | None:
    """
    Get area from database by name.

    :param name: Area name
    :param session: Session object
    :return: Area object
    """
    if not name:  # Check for empty values
        logging.error('Missing area name parameter')
        return None

    stmt = select(Area).where(Area.name == name)  # Select the area from the database

    try:
        area = session.scalars(stmt).one()  # Execute the statement and get the result
    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No area found: %s', e)  # log the error
        return None

    logging.debug('Area retrieved: %s', name)  # Log success

    return area
