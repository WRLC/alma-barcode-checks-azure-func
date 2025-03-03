"""
Controller for managing configuration settings.
"""
import logging

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from app.models.config_sql import Config


def get_config(key: str, session: scoped_session) -> str | None:
    """
    Get a config from the database.

    :param key: The key to look up in the config table.
    :param session: The SQLAlchemy session to use.
    :return: The config value.
    """
    if not key:  # Check for empty values
        logging.error('Missing config key parameter')
        return None

    # Get the region from the database
    stmt = select(Config).where(Config.configkey == key)  # Select the region from the database

    try:
        config = session.scalars(stmt).one().value  # Execute the statement and get the result
    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('Error: %s', e)  # log the error
        return None

    logging.debug('Config retrieved: %s', key)  # Log success

    return config  # Return the region
