"""
Controller for handling exceptions
"""
import logging


def check_exception(value: object) -> bool | Exception | None:
    """
    Return the exception value
    :param value: object
    :return: Exception or None
    """
    if not value:  # Check for empty values
        logging.warning('No area found')
        return None

    if isinstance(value, Exception):  # Check for errors
        return value

    return True
