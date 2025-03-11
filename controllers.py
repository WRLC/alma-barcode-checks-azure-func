"""
Controllers for the application.
"""
import logging
import urllib.parse
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type:ignore[import-untyped]
import requests  # type:ignore[import-untyped]
from requests.auth import HTTPBasicAuth  # type:ignore[import-untyped]
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.orm import scoped_session
from models import Analysis, Apikey, Area, Config, Report, Azuretrigger, Email


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
        logging.error('Missing analysis parameters for %s', analysis.azuretrigger.name)
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
        response = requests.get(path, params=payload_str, timeout=600)  # Get the report from Alma
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


def get_key(iz: int, area: int, write: int, session: scoped_session) -> str | None:
    """
    Get the API key to retrieve the report
    """
    if not check_exception(iz) or not check_exception(area):  # Check for empty values
        return None

    stmt = (  # Select the appropriate API key from the database
        select(Apikey)
        .where(Apikey.iz_id == iz)
        .where(Apikey.area_id == area)
        .where(Apikey.writekey == write)
    )

    try:
        apikey = session.scalars(stmt).one().apikey  # Execute the statement and get the result

    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No API key found: %s', e)  # log the error
        return None

    logging.debug('API key retrieved')  # Log success

    return apikey  # Return the API key


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


def get_trigger(code: str, session: scoped_session) -> Azuretrigger | None:
    """
    Get trigger from database by name.

    :param code: Trigger code
    :param session: Session object
    :return: Trigger object
    """
    if not code:  # Check for empty values
        logging.error('Missing trigger code parameter')
        return None

    stmt = select(Azuretrigger).where(Azuretrigger.code == code)  # Select the trigger from the database
    try:
        trigger = session.scalars(stmt).one()  # Execute the statement and get the result
    except sqlalchemy.exc.NoResultFound as e:  # Handle exceptions
        logging.error('No trigger %s found: %s', code, e)
        return None

    logging.debug('Trigger retrieved: %s', code)  # Log success

    return trigger


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


def send_emails(report: Report, analysis: Analysis, session: scoped_session) -> None:
    """
    Send the email to the analysis's recipients

    :param report: Report
    :param analysis: Analysis
    :param session: Session object
    :return: None
    """
    email = construct_email(report)  # type:ignore[arg-type] # Construct the email

    if not check_exception(email):  # Check for empty or errors
        return

    recipients = analysis.recipients  # Get the analysis's recipients

    if not check_exception(recipients):  # Check for empty or errors
        return

    for recipient in recipients:  # Iterate through the analysis's recipients

        if not check_exception(recipient):  # Check for empty or errors
            return

        email.send(recipient.user.email, session)  # type:ignore[union-attr]  # Send email to recipient


def construct_email(report: Report) -> Email | None:
    """
    Construct the email object

    :param report: Report
    :return: Email or None
    """

    if not check_exception(report):  # Check for empty or errors
        return None

    try:
        body = render_template(  # Build the email body
            'email.html',  # template
            rows=report.data['data']['rows'],  # type:ignore[union-attr]  # rows
            columns=report.data['data']['columns'],  # type:ignore[union-attr]  # columns
            column_keys=list(report.data['data']['columns'].keys()),  # type:ignore[union-attr] # column keys
            title=report.data['data']['report_name'].upper()  # type:ignore[union-attr]  # IZ
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return None

    try:
        email = Email(  # Create the email object
            subject=f"{report.data['data']['report_name']}",  # type:ignore[union-attr]  # subject
            body=body  # body
        )
    except KeyError as e:  # Handle exceptions
        logging.error(e)
        return None

    logging.debug('Email constructed: %s', email.subject)  # Log the email constructed

    return email


def render_template(template, **kwargs) -> str:
    """
    Render a Jinja template with the variables passed in

    :param template: str
    :param kwargs: dict
    :return: str
    """
    env = Environment(  # create the environment
        loader=FileSystemLoader('templates'),  # load the templates from the templates directory
        autoescape=select_autoescape(['html', 'xml'])  # autoescape html and xml
    )

    template = env.get_template(template)  # get the template

    logging.debug('Email rendered')  # log the template rendered

    return template.render(**kwargs)  # render the template with the variables passed in


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


# pylint: disable=r0914
def get_report(analysis: Analysis, session: scoped_session) -> Report | None:
    """
    Get the report from Alma Analytics

    :param analysis: Analysis
    :param session: Session object
    :return: requests.Response or None
    """
    if not check_exception(analysis):  # Check for empty or errors
        return None

    # Get the data from Alma Analytics
    response = get_analysis(analysis, session)

    if not check_exception(response):  # Check for empty or errors
        return None

    soup = get_soup(response)  # Parse the XML response

    if not check_exception(soup):  # Check for empty or errors
        return None

    columns = get_columns(soup)  # type: ignore # Get the columns from the XML response
    rows = get_rows(soup)  # type: ignore # Get the rows from the XML response

    for i in [columns, rows]:  # Iterate through the columns and rows
        if not check_exception(i):  # Check for empty or errors
            return None

    report = Report(  # Create the report object
        data={
            'status': 'success',
            'message': 'Report data retrieved',
            'data': {
                'report_name': analysis.iz.code.upper() + ' ' + analysis.azuretrigger.name,
                'columns': columns,
                'rows': rows
            }
        }
    )

    logging.debug('Report data compiled: %s', report.data['data']['report_name'])  # Log the success message

    return report  # Return the report


def get_soup(response) -> BeautifulSoup | None:
    """
    Parse the XML response

    :param response: requests.Response
    :return: BeautifulSoup
    """
    if not check_exception(response):  # Check for empty or errors
        return None

    soup = BeautifulSoup(response.content, 'xml')  # Parse the XML response

    if not check_exception(soup):  # Check for empty or errors
        return None  # Return the error or None

    if soup.find('error'):  # Check for Alma errors
        logging.error('Error: %s', soup.find('error').text)  # type: ignore
        return None

    logging.debug('XML response parsed')  # Log the success message

    return soup


def get_columns(soup: BeautifulSoup) -> dict[str, str] | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    if not check_exception(soup):  # Check for empty or errors
        return None

    columnlist = soup.find_all('xsd:element')  # Get the columns from the XML response

    if not check_exception(columnlist):
        return None

    columns = {}  # Create a dictionary of columns

    for column in columnlist:  # Iterate through the columns
        columns[column['name']] = column['saw-sql:columnHeading']  # type: ignore # Add column to dictionary

        if 'CASE  WHEN Provenance Code' in columns[column['name']]:  # type: ignore # If column is Provenance Code
            columns[column['name']] = 'Provenance Code'  # type: ignore # Change column name to Provenance Code

    logging.debug('Columns retrieved')  # Log the success message

    return columns  # type: ignore # Return the dictionary of columns


def get_rows(soup: BeautifulSoup) -> list | None:  # type:ignore[valid-type]
    """
    Get the data rows from the report

    :param soup: BeautifulSoup
    :return: list or None
    """
    if not check_exception(soup):  # Check for empty or errors
        return None

    rowlist = soup.find_all('Row')  # Get the rows from the XML response

    if not check_exception(rowlist):
        return None

    rows = []  # Create a list of rows

    for value in rowlist:  # Iterate through the rows
        values = {}  # Create a dictionary of values
        kids = value.findChildren()  # type: ignore # Get the children of the row

        for kid in kids:  # Iterate through the children
            values[kid.name] = kid.text  # Add the child to the dictionary

        rows.append(values)  # Add the dictionary to the list

    logging.debug('Rows retrieved')  # Log the success message

    return rows  # Return the list of rows


def send(email: Email, to: str, session: scoped_session) -> None:
    """
            Send the email to webhook

            :return: None
            """
    # Create the basic auth object
    basic = HTTPBasicAuth(get_config('webhook_user', session), get_config('webhook_pass', session))

    try:  # Try to send the email
        response = requests.post(  # Send the email
            url=get_config('webhook_url', session),
            json={
                "subject": email.subject,
                "body": email.body,
                "to": to,
                "sender": get_config('sender_email', session)
            },
            timeout=10,
            auth=basic
        )

    except requests.exceptions.RequestException as e:  # Handle request exceptions
        logging.error('Error: %s', e)  # If there is an error, log it
        raise  # If there is an error, raise it

    if response.status_code != 201:  # Check if the response status code is not 201
        logging.error('Error: %s: %s', response.status_code, response.text)  # If not, log error
        raise requests.exceptions.RequestException(  # If not, raise an error
            f'Error: {response.status_code}: {response.text}'
        )

    logging.info('Email sent to %s: %s', to, email.subject)
