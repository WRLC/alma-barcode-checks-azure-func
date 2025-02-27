"""
Controller for the Analysis model
"""
import logging
import urllib.parse
import requests  # type:ignore[import-untyped]
from application.controllers.area_controller import get_area_by_name
from application.controllers.config_controller import get_config
from application.controllers.exception_controller import check_exception
from application.controllers.key_controller import get_key
from application.models.analysis_sql import Analysis


def analysis_api_call(analysis: Analysis) -> requests.Response | Exception | None:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :return: requests.Response
    """
    if not analysis:  # Check for empty values
        logging.error('No analysis found')
        return None

    if not analysis.path or not analysis.iz:  # Check if the analysis has a path
        logging.error('Missing analysis parameters for %s', analysis.trigger.name)
        return ValueError('Missing analysis parameters for %s', analysis.trigger.name)

    area = get_area_by_name('analytics')  # Get the area from the database

    if not check_exception(area) or isinstance(check_exception(area), Exception):  # Check for empty values or errors
        return check_exception(area)  # Return the error or None

    iz = analysis.iz  # Get the IZ from the analysis

    apikey = get_key(iz.id, area.id, 0)  # type:ignore[union-attr]  # Get the API key

    if not check_exception(apikey) or isinstance(check_exception(apikey), Exception):  # Check for empty or errors
        return check_exception(apikey)  # Return the error or None

    payload = {'limit': '1000', 'col_names': 'true', 'path': analysis.path, 'apikey': apikey}  # Create the payload
    payload_str = urllib.parse.urlencode(payload, safe=':%')

    path = build_path()  # Build the API path

    if not check_exception(path) or isinstance(check_exception(path), Exception):  # Check for empty or errors
        return check_exception(path)  # Return the error or None

    try:  # Try to get the report from Alma
        response = requests.get(path, params=payload_str, timeout=300)  # Get the report from Alma
        response.raise_for_status()  # Check for HTTP errors
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:  # Handle exceptions
        logging.error(e)
        return e

    logging.info('API call succeeded: %s %s', analysis.iz.code, analysis.trigger.name)  # Log success

    return response


def build_path() -> str | bool | Exception | None:
    """
    Build the API path.

    :return: The API path.
    """
    region = get_config('alma_region')  # Get the region from the database

    if not check_exception(region) or isinstance(check_exception(region), Exception):  # Check for empty or errors
        return check_exception(region)  # Return the error or None

    path = f'https://api-{region}.hosted.exlibrisgroup.com'

    if region == 'cn':
        path += '.cn'

    path += '/almaws/v1/analytics/reports'

    return path
