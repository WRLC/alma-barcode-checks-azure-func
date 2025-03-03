"""
Key model
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


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
