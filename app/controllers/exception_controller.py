"""
Controller for handling exceptions
"""
import logging


def check_exception(value: object) -> bool:
    """
    Return the exception value
    :param value: object
    :return: Exception or None
    """
    if not value or isinstance(value, Exception):  # Check for errors
        if isinstance(value, Exception):
            logging.error('Error: %s', value)  # Log the error

        return False

    return True
