"""
Area model
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from application.extensions import Base


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
