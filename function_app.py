"""
This file is used to register the function apps with the Azure Functions host.
"""
import logging
import os
from typing import Any
import urllib.parse
import azure.functions as func
from bs4 import BeautifulSoup  # type:ignore[import-untyped]
import dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type:ignore[import-untyped]
import requests  # type:ignore[import-untyped]
from requests.auth import HTTPBasicAuth  # type:ignore[import-untyped]
from sqlalchemy import create_engine, String, ForeignKey, select
import sqlalchemy.exc
from sqlalchemy.orm import Mapped, mapped_column, relationship, scoped_session, sessionmaker, DeclarativeBase

dotenv.load_dotenv()  # Load environment variables from .env file

app = func.FunctionApp()  # Create a new FunctionApp instance

engine = create_engine(os.getenv("SQLALCHEMY_DB_URL"))  # type:ignore[arg-type] # Create a new SQLite database
session_factory = sessionmaker(bind=engine)  # Create a session factory


##########
# Models #
##########


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """
    Base class for all models.
    """
    pass  # pylint: disable=unnecessary-pass


class Analysis(Base):  # pylint: disable=too-few-public-methods
    """
    Analysis model.
    """
    __tablename__ = "analysis"

    id: Mapped[int] = mapped_column(primary_key=True)  # Analysis ID
    path: Mapped[str] = mapped_column(String(255))  # Path to the analysis
    azuretrigger_id: Mapped[int] = mapped_column(ForeignKey("azuretrigger.id"))  # Trigger ID
    iz_id: Mapped[int] = mapped_column(ForeignKey("iz.id"))  # IZ ID

    azuretrigger: Mapped["Azuretrigger"] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="analyses"
    )
    iz: Mapped["Iz"] = relationship(back_populates="analyses")  # type:ignore[name-defined]  # noqa: F821

    recipients: Mapped[list["Recipient"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Analysis(id={self.id!r})"


class Apikey(Base):  # pylint: disable=too-few-public-methods
    """
    Key model
    """
    __tablename__ = "apikey"

    id: Mapped[int] = mapped_column(primary_key=True)  # Key ID
    apikey: Mapped[str] = mapped_column(String(255))  # Key value
    writekey: Mapped[bool] = mapped_column()  # Write access
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))  # Area ID
    iz_id: Mapped[int] = mapped_column(ForeignKey("iz.id"))  # IZ ID

    iz: Mapped["Iz"] = relationship(back_populates="apikeys")  # type:ignore[name-defined]  # noqa: F821
    area: Mapped["Area"] = relationship(back_populates="apikeys")  # type:ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"Key(id={self.id!r})"


class Area(Base):  # pylint: disable=too-few-public-methods
    """
    Area model
    """
    __tablename__ = "area"

    id: Mapped[int] = mapped_column(primary_key=True)  # Area ID
    name: Mapped[str] = mapped_column(String(50))  # Area name

    apikeys: Mapped[list["Apikey"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="area",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Area(id={self.id!r}, name={self.name!r})"


class Azuretrigger(Base):  # pylint: disable=too-few-public-methods
    """
    Trigger model
    """
    __tablename__ = "azuretrigger"
    id: Mapped[int] = mapped_column(primary_key=True)  # Trigger ID
    code: Mapped[str] = mapped_column(String(50))  # Trigger code
    name: Mapped[str] = mapped_column(String(255))  # Trigger name

    analyses: Mapped[list["Analysis"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="azuretrigger",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Trigger(id={self.id!r}, name={self.name!r})"


class Config(Base):  # pylint: disable=too-few-public-methods
    """
    Config model
    """
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(primary_key=True)  # Config ID
    configkey: Mapped[str] = mapped_column(String(50), unique=True)  # Config key
    value: Mapped[str] = mapped_column(String(50))  # Config value

    def __repr__(self) -> str:
        return f"Config(id={self.id!r}, value={self.value!r})"


class Iz(Base):  # pylint: disable=too-few-public-methods
    """
    IZ model
    """
    __tablename__ = "iz"

    id: Mapped[int] = mapped_column(primary_key=True)  # IZ ID
    name: Mapped[str] = mapped_column(String(50))  # IZ name
    code: Mapped[str] = mapped_column(String(50))  # IZ code

    apikeys: Mapped[list["Apikey"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="iz",
        cascade="all, delete-orphan",
    )

    analyses: Mapped[list["Analysis"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="iz",
        cascade="all, delete-orphan",
    )

    users: Mapped[list["User"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="iz",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Iz(id={self.id!r}, name={self.name!r}, code={self.code!r})"


class Recipient(Base):  # pylint: disable=too-few-public-methods
    """
    Recipient model
    """
    __tablename__ = "recipient"

    id: Mapped[int] = mapped_column(primary_key=True)  # Recipient ID
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))  # User ID
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analysis.id"))  # Analysis ID

    user: Mapped["User"] = relationship(back_populates="recipients")  # type:ignore[name-defined]  # noqa: F821
    analysis: Mapped["Analysis"] = relationship(back_populates="recipients")  # type:ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"Recipient(id={self.id!r})"


class User(Base):  # pylint: disable=too-few-public-methods
    """
    User model
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)  # User ID
    email: Mapped[str] = mapped_column(String(50))  # Username
    iz_id: Mapped[str] = mapped_column(ForeignKey("iz.id"))  # IZ ID

    iz: Mapped["Iz"] = relationship(back_populates="users")  # type:ignore[name-defined]  # noqa: F821

    recipients: Mapped[list["Recipient"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.email!r})"


class Email:
    """
    Email object
    """
    def __init__(self, subject: str, body: str) -> None:
        """
        Email object

        :param subject: str
        :param body: str
        :return: None
        """
        self.subject = subject
        self.body = body

    def __str__(self) -> str:
        """
        Return the email as a string

        :return: str
        """
        return f"Subject: {self.subject}\n\n{self.body}"

    def send(self, to: str, session: scoped_session) -> None:
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
                    "subject": self.subject,
                    "body": self.body,
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

        logging.info('Email sent to %s: %s', to, self.subject)


class Report:  # pylint: disable=too-few-public-methods
    """
    Report object
    """
    def __init__(self, data: dict[str, Any]) -> None:
        """
        Report object

        :param data: json
        :return: None
        """
        self.data = data

    def __str__(self) -> str:
        """
        Return the report as a string

        :return: str
        """
        return f"{self.data}"


############
# Triggers #
############


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="izincorrectrowtray")
@app.timer_trigger(
    schedule="0 30 14 1 * *",  # type:ignore[arg-type]  # Run at 14:30 on the first day of every month
    arg_name="izincorrectrowtray"
)
# pylint:disable=unused-argument
def iz_incorrect_row_tray(izincorrectrowtray: func.TimerRequest) -> None:  # type:ignore
    """
    Get report of barcodes with incorrect row/tray in all IZs and send email notification.

    :param izincorrectrowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'iz_incorrect_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="iznorowtray")
@app.timer_trigger(
    schedule="0 0 14 1 * *",  # type:ignore[arg-type]  # Run at 14:00 on the first day of every month
    arg_name="iznorowtray"
)
def iz_no_row_tray(iznorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in all IZs and send email notification.

    :param iznorowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'iz_no_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        # TODO: Fix Alma records

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfduplicate")
@app.timer_trigger(
    schedule="0 0 12 1 * *",  # type:ignore[arg-type]  # Run at 12:00 on the first day of every month
    arg_name="scfduplicate"
)
# pylint: disable=unused-argument
def scf_duplicate(scfduplicate: func.TimerRequest) -> None:  # type:ignore[unused-argument]
    """
    Get report of duplicate barcodes in SCF and send email notification.

    :param scfduplicate: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_duplicate'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        session.remove()
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfincorrectrowtray")
@app.timer_trigger(
    schedule="0 30 13 1 1,7 *",  # type:ignore[arg-type]  # Run at 13:30 on the first day of January and July
    arg_name="scfincorrectrowtray"
)
# pylint:disable=unused-argument
def scf_incorrect_row_tray(scfincorrectrowtray: func.TimerRequest) -> None:  # type:ignore
    """
    Get report of barcodes with incorrect row/tray in SCF and send email notification.

    :param scfincorrectrowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_incorrect_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfnorowtray")
@app.timer_trigger(
    schedule="0 0 13 1 1,7 *",  # type:ignore[arg-type]  # Run at 13:00 on the first day of January and July
    arg_name="scfnorowtray"
)
def scf_no_row_tray(scfnorowtray: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes with no row/tray in SCF and send email notification.

    :param scfnorowtray: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_no_row_tray'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfnox")
@app.timer_trigger(
    schedule="0 30 12 1 * *",  # type:ignore[arg-type]  # Run at 12:30 on the first day of every month
    arg_name="scfnox"
)
def scf_no_x(scfnox: func.TimerRequest) -> None:  # type:ignore[unused-argument]  # pylint: disable=unused-argument
    """
    Get report of barcodes with no X in SCF, fix records in Alma, and send email notification.

    :param scfnox: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_no_x'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        # TODO: Fix Alma records

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


# noinspection PyUnusedLocal,PyUnresolvedReferences
@app.function_name(name="scfwithdrawn")
@app.timer_trigger(
    schedule="0 0 11 1 7 *",  # type:ignore[arg-type]  # Run at 11:00 on the first day of July
    arg_name="scfwithdrawn"
)
def scf_withdrawn(scfwithdrawn: func.TimerRequest) -> None:  # type:ignore  # pylint:disable=unused-argument
    """
    Get report of barcodes marked withdrawn in SCF and send email notification.

    :param scfwithdrawn: TimerRequest
    :return: None
    """
    session = scoped_session(session_factory)  # Create a session

    code = 'scf_withdrawn'  # Trigger code

    analyses = get_trigger_analyses(code, session)  # Get the trigger's analyses

    if not check_exception(analyses):  # Check for empty or errors
        return

    for analysis in analyses:  # type:ignore[union-attr]  # Iterate through the analyses

        if not check_exception(analysis):  # Check for empty values
            continue

        report = get_report(analysis, session)  # Get a report from the analysis

        if not check_exception(report):  # Check for empty or errors
            logging.info('No results for report %s %s', analysis.iz.code, analysis.azuretrigger.name)
            continue

        # TODO: Separate emails for each Provenance Code

        send_emails(report, analysis, session)  # type:ignore[arg-type]  # Send the report as email

    session.remove()  # Remove the session


###############
# Controllers #
###############


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
