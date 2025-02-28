"""
Controller for the Analysis model
"""
import logging
import urllib.parse
import requests  # type:ignore[import-untyped]
from sqlalchemy.orm import scoped_session
from application.controllers.area_controller import get_area_by_name
from application.controllers.config_controller import get_config
from application.controllers.exception_controller import check_exception
from application.controllers.apikey_controller import get_key
from application.controllers.azuretrigger_controller import get_trigger
from application.models.analysis_sql import Analysis


# noinspection PyTypeChecker
def get_trigger_analyses(trigger_code: str, session: scoped_session) -> list["Analysis"] | None:
    """
    Get the analyses for a trigger
    """
    if not trigger_code:  # Check for empty values
        logging.error('Missing trigger code parameter')
        return None

    trigger = get_trigger(trigger_code, session)  # Get the trigger from the database

    if not check_exception(trigger):  # Check for empty or errors
        return None

    analyses = trigger.analyses  # type:ignore[union-attr]  # Get the analyses from the trigger

    return analyses


def get_analysis(analysis: Analysis, session: scoped_session) -> requests.Response | None:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :param session: Session object
    :return: requests.Response
    """
    if not analysis:  # Check for empty parameters
        logging.error('No analysis found')
        return None

    area = get_area_by_name('analytics', session)  # Get the area from the database

    if not check_exception(area):  # Check for empty values or errors
        return None

    if not analysis.path or not analysis.iz:  # Check if the analysis has a path or iz
        logging.error('Missing analysis parameters for %s', analysis.trigger.name)
        return None

    iz = analysis.iz  # Get the IZ from the analysis

    if not check_exception(iz):  # Check for empty values or errors
        return None

    apikey = get_key(iz.id, area.id, 0, session)  # type:ignore[union-attr]  # Get the API key

    if not check_exception(apikey):  # Check for empty or errors
        return None

    payload = {'limit': '1000', 'col_names': 'true', 'path': analysis.path, 'apikey': apikey}  # Create the payload
    payload_str = urllib.parse.urlencode(payload, safe=':%')

    path = build_path(session)  # Build the API path

    if not check_exception(path):  # Check for empty or errors
        return None

    try:  # Try to get the report from Alma
        response = requests.get(path, params=payload_str, timeout=300)  # Get the report from Alma
        response.raise_for_status()  # Check for HTTP errors
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:  # Handle exceptions
        logging.error(e)
        return None

    logging.info('API call succeeded: %s %s', analysis.iz.code, analysis.azuretrigger.name)  # Log success

    return response


def build_path(session: scoped_session) -> str | None:
    """
    Build the API path.

    :param session: Session object
    :return: The API path.
    """
    region = get_config('alma_region', session)  # Get the region from the database

    if not check_exception(region):  # Check for empty or errors
        return None

    path = f'https://api-{region}.hosted.exlibrisgroup.com'

    if region == 'cn':
        path += '.cn'

    path += '/almaws/v1/analytics/reports'

    return path
