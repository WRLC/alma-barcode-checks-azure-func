"""
Analysis model.
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from application.extensions import Base


class Analysis(Base):  # pylint: disable=too-few-public-methods
    """
    Analysis model.
    """
    __tablename__ = "analysis"

    id: Mapped[int] = mapped_column(primary_key=True)  # Analysis ID
    path: Mapped[str] = mapped_column(String(255))  # Path to the analysis
    trigger_id: Mapped[int] = mapped_column(ForeignKey("trigger.id"))  # Trigger ID
    iz_id: Mapped[int] = mapped_column(ForeignKey("iz.id"))  # IZ ID

    trigger: Mapped["Trigger"] = relationship(back_populates="analyses")  # type:ignore[name-defined]
    iz: Mapped["Iz"] = relationship(back_populates="analyses")  # type:ignore[name-defined]

    recipients: Mapped[list["Recipient"]] = relationship(  # type:ignore[name-defined]
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Analysis(id={self.id!r})"
