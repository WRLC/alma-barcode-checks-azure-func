"""
Recipient Model
"""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.extensions import Base


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
