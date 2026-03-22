from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MajorCategory(Base):
    __tablename__ = "major_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    middle_categories: Mapped[list["MiddleCategory"]] = relationship(
        "MiddleCategory", back_populates="major_category"
    )


class MiddleCategory(Base):
    __tablename__ = "middle_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    major_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("major_categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    major_category: Mapped["MajorCategory"] = relationship(
        "MajorCategory", back_populates="middle_categories"
    )
    knowhows: Mapped[list["Knowhow"]] = relationship("Knowhow", back_populates="middle_category")


class Knowhow(Base):
    __tablename__ = "knowhows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    keywords: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    middle_category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("middle_categories.id"), nullable=True
    )

    middle_category: Mapped["MiddleCategory | None"] = relationship(
        "MiddleCategory", back_populates="knowhows"
    )
