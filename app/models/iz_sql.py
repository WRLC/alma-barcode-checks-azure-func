"""
IZ model
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


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
