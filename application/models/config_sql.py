"""
Config model
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from application.extensions import Base


class Config(Base):  # pylint: disable=too-few-public-methods
    """
    Config model
    """
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(primary_key=True)  # Config ID
    key: Mapped[str] = mapped_column(String(50), unique=True)  # Config key
    value: Mapped[str] = mapped_column(String(50))  # Config value

    def __repr__(self) -> str:
        return f"Config(id={self.id!r}, key={self.key!r}, value={self.value!r})"
