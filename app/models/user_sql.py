"""
User model
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


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
