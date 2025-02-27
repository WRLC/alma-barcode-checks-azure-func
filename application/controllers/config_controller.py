"""
Controller for managing configuration settings.
"""
import logging

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.config_sql import Config


def get_config(key: str) -> str | Exception | None:
    """
    Get a config from the database.

    :param key: The key to look up in the config table.
    :return: The config value.
    """
    if not key:  # Check for empty values
        logging.error('Missing config key parameter')
        return None

    # Get the region from the database
    session = Session(engine)  # Create a Session object

    stmt = select(Config).where(Config.key == key)  # Select the region from the database

    try:
        config = session.scalars(stmt).one().value  # Execute the statement and get the result
    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('Error: %s', e)  # log the error
        return e

    logging.debug('Config retrieved: %s', key)  # Log success

    return config  # Return the region
