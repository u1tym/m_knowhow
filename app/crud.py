from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Knowhow, MajorCategory, MiddleCategory


def _utc_now_naive() -> datetime:
    return datetime.utcnow()


def list_major_categories(db: Session) -> list[MajorCategory]:
    stmt = (
        select(MajorCategory)
        .where(MajorCategory.is_deleted.is_(False))
        .order_by(MajorCategory.display_order.asc(), MajorCategory.id.asc())
    )
    return list(db.scalars(stmt).all())


def create_major_category(db: Session, name: str) -> MajorCategory:
    next_order = db.scalar(
        select(func.coalesce(func.max(MajorCategory.display_order), 0)).where(
            MajorCategory.is_deleted.is_(False)
        )
    )
    assert next_order is not None
    row = MajorCategory(
        name=name.strip(),
        display_order=int(next_order) + 1,
        is_deleted=False,
        updated_at=_utc_now_naive(),
    )
    db.add(row)
    db.flush()
    return row


def rename_major_category(db: Session, category_id: int, new_name: str) -> MajorCategory | None:
    row = db.get(MajorCategory, category_id)
    if row is None or row.is_deleted:
        return None
    row.name = new_name.strip()
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def get_major_category_if_active(db: Session, category_id: int) -> MajorCategory | None:
    row = db.get(MajorCategory, category_id)
    if row is None or row.is_deleted:
        return None
    return row


def get_middle_category_if_active(db: Session, category_id: int) -> MiddleCategory | None:
    row = db.get(MiddleCategory, category_id)
    if row is None or row.is_deleted:
        return None
    return row


def list_middle_categories(db: Session, major_category_id: int) -> list[MiddleCategory]:
    stmt = (
        select(MiddleCategory)
        .where(
            MiddleCategory.major_category_id == major_category_id,
            MiddleCategory.is_deleted.is_(False),
        )
        .order_by(MiddleCategory.display_order.asc(), MiddleCategory.id.asc())
    )
    return list(db.scalars(stmt).all())


def create_middle_category(
    db: Session, major_category_id: int, name: str
) -> MiddleCategory | None:
    if get_major_category_if_active(db, major_category_id) is None:
        return None
    next_order = db.scalar(
        select(func.coalesce(func.max(MiddleCategory.display_order), 0)).where(
            MiddleCategory.major_category_id == major_category_id,
            MiddleCategory.is_deleted.is_(False),
        )
    )
    assert next_order is not None
    row = MiddleCategory(
        major_category_id=major_category_id,
        name=name.strip(),
        display_order=int(next_order) + 1,
        is_deleted=False,
        updated_at=_utc_now_naive(),
    )
    db.add(row)
    db.flush()
    return row


def rename_middle_category(db: Session, category_id: int, new_name: str) -> MiddleCategory | None:
    row = db.get(MiddleCategory, category_id)
    if row is None or row.is_deleted:
        return None
    row.name = new_name.strip()
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def list_knowhows_by_middle(db: Session, middle_category_id: int) -> list[Knowhow]:
    stmt = (
        select(Knowhow)
        .where(
            Knowhow.middle_category_id == middle_category_id,
            Knowhow.is_deleted.is_(False),
        )
        .order_by(Knowhow.display_order.asc(), Knowhow.id.asc())
    )
    return list(db.scalars(stmt).all())


def get_knowhow_detail(db: Session, knowhow_id: int) -> Knowhow | None:
    row = db.get(Knowhow, knowhow_id)
    if row is None or row.is_deleted:
        return None
    return row


def is_integrity_unique_violation(exc: IntegrityError) -> bool:
    orig: Any = getattr(exc, "orig", None)
    if orig is not None and hasattr(orig, "pgcode"):
        return str(orig.pgcode) == "23505"
    msg = str(exc).lower()
    return "unique" in msg or "duplicate" in msg
