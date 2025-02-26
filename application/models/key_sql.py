"""
Key model
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from application.extensions import Base


class Key(Base):  # pylint: disable=too-few-public-methods
    """
    Key model
    """
    __tablename__ = "key"

    id: Mapped[int] = mapped_column(primary_key=True)  # Key ID
    key: Mapped[str] = mapped_column(String(255))  # Key value
    write: Mapped[bool] = mapped_column()  # Write access
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))  # Area ID
    iz_id: Mapped[int] = mapped_column(ForeignKey("iz.id"))  # IZ ID

    iz: Mapped["Iz"] = relationship(back_populates="keys")  # type:ignore[name-defined]
    area: Mapped["Area"] = relationship(back_populates="keys")  # type:ignore[name-defined]

    def __repr__(self) -> str:
        return f"Key(id={self.id!r})"
