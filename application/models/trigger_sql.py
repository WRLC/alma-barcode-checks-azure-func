"""
Trigger model
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from application.extensions import Base


class Trigger(Base):  # pylint: disable=too-few-public-methods
    """
    Trigger model
    """
    __tablename__ = "trigger"
    id: Mapped[int] = mapped_column(primary_key=True)  # Trigger ID
    code: Mapped[str] = mapped_column(String(50))  # Trigger code
    name: Mapped[str] = mapped_column(String(255))  # Trigger name

    analyses: Mapped[list["Analysis"]] = relationship(  # type:ignore[name-defined]  # noqa: F821
        back_populates="trigger",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Trigger(id={self.id!r}, name={self.name!r}, ncron={self.ncron!r})"
