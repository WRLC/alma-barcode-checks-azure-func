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
