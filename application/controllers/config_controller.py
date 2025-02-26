"""
Controller for managing configuration settings.
"""
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from application.extensions import engine
from application.models.config_sql import Config


def get_config(key: str) -> str:
    """
    Get a config from the database.

    :param key: The key to look up in the config table.
    :return: The config value.
    """
    # Get the region from the database
    session = Session(engine)  # Create a Session object

    try:
        stmt = select(Config).where(Config.key == key)  # Select the region from the database
        config = session.scalars(stmt).one().value  # Execute the statement and get the result
    except Exception as e:  # Handle exceptions
        logging.error('Error: %s', e)  # log the error
        raise  # re-raise the exception

    return config  # Return the region
