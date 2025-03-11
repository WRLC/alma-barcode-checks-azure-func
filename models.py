"""
Models for application
"""
import os
from typing import Any
import dotenv
from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

dotenv.load_dotenv()

engine = create_engine(os.getenv("SQLALCHEMY_DB_URL"))  # type:ignore[arg-type] # Create a new SQLite database
session_factory = sessionmaker(bind=engine)  # Create a session factory


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


class Email:  # pylint: disable=too-few-public-methods
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
