from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Knowhow, MajorCategory, MiddleCategory


def _utc_now_naive() -> datetime:
    return datetime.utcnow()


def _ilike_fragment(fragment: str) -> str:
    """LIKE パターンとして渡すユーザー入力のワイルドカード（%, _）と \\ をエスケープする。"""
    return (
        fragment.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def list_major_categories(db: Session, aid: int) -> list[MajorCategory]:
    stmt = (
        select(MajorCategory)
        .where(
            MajorCategory.aid == aid,
            MajorCategory.is_deleted.is_(False),
        )
        .order_by(MajorCategory.display_order.asc(), MajorCategory.id.asc())
    )
    return list(db.scalars(stmt).all())


def create_major_category(db: Session, name: str, aid: int) -> MajorCategory:
    next_order = db.scalar(
        select(func.coalesce(func.max(MajorCategory.display_order), 0)).where(
            MajorCategory.aid == aid,
            MajorCategory.is_deleted.is_(False),
        )
    )
    assert next_order is not None
    row = MajorCategory(
        aid=aid,
        name=name.strip(),
        display_order=int(next_order) + 1,
        is_deleted=False,
        updated_at=_utc_now_naive(),
    )
    db.add(row)
    db.flush()
    return row


def rename_major_category(
    db: Session, category_id: int, new_name: str, aid: int
) -> MajorCategory | None:
    row = db.get(MajorCategory, category_id)
    if row is None or row.is_deleted or row.aid != aid:
        return None
    row.name = new_name.strip()
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def get_major_category_if_active(
    db: Session, category_id: int, aid: int
) -> MajorCategory | None:
    row = db.get(MajorCategory, category_id)
    if row is None or row.is_deleted or row.aid != aid:
        return None
    return row


def get_middle_category_if_active(
    db: Session, category_id: int, aid: int
) -> MiddleCategory | None:
    row = db.get(MiddleCategory, category_id)
    if row is None or row.is_deleted or row.aid != aid:
        return None
    return row


def list_middle_categories(
    db: Session, major_category_id: int, aid: int
) -> list[MiddleCategory]:
    stmt = (
        select(MiddleCategory)
        .where(
            MiddleCategory.major_category_id == major_category_id,
            MiddleCategory.aid == aid,
            MiddleCategory.is_deleted.is_(False),
        )
        .order_by(MiddleCategory.display_order.asc(), MiddleCategory.id.asc())
    )
    return list(db.scalars(stmt).all())


def create_middle_category(
    db: Session, major_category_id: int, name: str, aid: int
) -> MiddleCategory | None:
    if get_major_category_if_active(db, major_category_id, aid) is None:
        return None
    next_order = db.scalar(
        select(func.coalesce(func.max(MiddleCategory.display_order), 0)).where(
            MiddleCategory.major_category_id == major_category_id,
            MiddleCategory.aid == aid,
            MiddleCategory.is_deleted.is_(False),
        )
    )
    assert next_order is not None
    row = MiddleCategory(
        aid=aid,
        major_category_id=major_category_id,
        name=name.strip(),
        display_order=int(next_order) + 1,
        is_deleted=False,
        updated_at=_utc_now_naive(),
    )
    db.add(row)
    db.flush()
    return row


def rename_middle_category(
    db: Session, category_id: int, new_name: str, aid: int
) -> MiddleCategory | None:
    row = db.get(MiddleCategory, category_id)
    if row is None or row.is_deleted or row.aid != aid:
        return None
    row.name = new_name.strip()
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def list_knowhows_by_middle(
    db: Session, middle_category_id: int, aid: int
) -> list[Knowhow]:
    stmt = (
        select(Knowhow)
        .where(
            Knowhow.middle_category_id == middle_category_id,
            Knowhow.aid == aid,
            Knowhow.is_deleted.is_(False),
        )
        .order_by(Knowhow.display_order.asc(), Knowhow.id.asc())
    )
    return list(db.scalars(stmt).all())


def get_knowhow_detail(db: Session, knowhow_id: int, aid: int) -> Knowhow | None:
    row = db.get(Knowhow, knowhow_id)
    if row is None or row.is_deleted or row.aid != aid:
        return None
    return row


def _next_knowhow_display_order(
    db: Session, aid: int, middle_category_id: int | None
) -> int:
    stmt = select(func.coalesce(func.max(Knowhow.display_order), 0)).where(
        Knowhow.aid == aid,
        Knowhow.is_deleted.is_(False),
    )
    if middle_category_id is None:
        stmt = stmt.where(Knowhow.middle_category_id.is_(None))
    else:
        stmt = stmt.where(Knowhow.middle_category_id == middle_category_id)
    next_order = db.scalar(stmt)
    assert next_order is not None
    return int(next_order) + 1


def create_knowhow(
    db: Session,
    *,
    aid: int,
    title: str,
    keywords: str | None,
    content: str,
    middle_category_id: int | None,
) -> Knowhow | None:
    if middle_category_id is not None and get_middle_category_if_active(
        db, middle_category_id, aid
    ) is None:
        return None

    row = Knowhow(
        aid=aid,
        title=title.strip(),
        keywords=keywords.strip() if isinstance(keywords, str) else None,
        content=content.strip(),
        display_order=_next_knowhow_display_order(db, aid, middle_category_id),
        is_deleted=False,
        middle_category_id=middle_category_id,
        updated_at=_utc_now_naive(),
    )
    db.add(row)
    db.flush()
    return row


def get_knowhow_for_mutation(db: Session, knowhow_id: int, aid: int) -> Knowhow | None:
    """未削除チェックなしで aid が一致するノウハウを取得（論理削除 API 用）。"""
    row = db.get(Knowhow, knowhow_id)
    if row is None or row.aid != aid:
        return None
    return row


def swap_knowhow_display_orders(db: Session, a: Knowhow, b: Knowhow) -> None:
    a_order, b_order = a.display_order, b.display_order
    a.display_order = b_order
    b.display_order = a_order
    now = _utc_now_naive()
    a.updated_at = now
    b.updated_at = now
    db.flush()


def search_knowhows_by_keywords_all_match(
    db: Session, aid: int, keywords: list[str]
) -> list[tuple[Knowhow, MiddleCategory | None, MajorCategory | None]]:
    trimmed = [k.strip() for k in keywords if k.strip()]
    if not trimmed:
        return []

    stmt = (
        select(Knowhow, MiddleCategory, MajorCategory)
        .outerjoin(
            MiddleCategory,
            Knowhow.middle_category_id == MiddleCategory.id,
        )
        .outerjoin(
            MajorCategory,
            MiddleCategory.major_category_id == MajorCategory.id,
        )
        .where(
            Knowhow.aid == aid,
            Knowhow.is_deleted.is_(False),
            Knowhow.keywords.isnot(None),
            or_(
                Knowhow.middle_category_id.is_(None),
                and_(
                    MiddleCategory.is_deleted.is_(False),
                    MajorCategory.id.isnot(None),
                    MajorCategory.is_deleted.is_(False),
                ),
            ),
        )
    )
    for kw in trimmed:
        pat = f"%{_ilike_fragment(kw)}%"
        stmt = stmt.where(Knowhow.keywords.ilike(pat, escape="\\"))

    stmt = stmt.order_by(
        MajorCategory.display_order.asc().nulls_last(),
        MajorCategory.id.asc().nulls_last(),
        MiddleCategory.display_order.asc().nulls_last(),
        MiddleCategory.id.asc().nulls_last(),
        Knowhow.display_order.asc(),
        Knowhow.id.asc(),
    )
    rows = db.execute(stmt).all()
    return [(k, mid, maj) for k, mid, maj in rows]


def soft_delete_knowhow(db: Session, *, aid: int, knowhow_id: int) -> Knowhow | None:
    row = get_knowhow_for_mutation(db, knowhow_id, aid)
    if row is None or row.is_deleted:
        return None
    row.is_deleted = True
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def update_knowhow(
    db: Session,
    *,
    aid: int,
    knowhow_id: int,
    title: str | None,
    keywords: str | None,
    content: str | None,
    middle_category_id: int | None,
    middle_category_id_provided: bool,
) -> Knowhow | None:
    row = get_knowhow_detail(db, knowhow_id, aid)
    if row is None:
        return None

    if middle_category_id_provided:
        if middle_category_id is not None and get_middle_category_if_active(
            db, middle_category_id, aid
        ) is None:
            return None
        if row.middle_category_id != middle_category_id:
            row.middle_category_id = middle_category_id
            row.display_order = _next_knowhow_display_order(db, aid, middle_category_id)

    if title is not None:
        row.title = title.strip()
    if keywords is not None:
        row.keywords = keywords.strip()
    if content is not None:
        row.content = content.strip()
    row.updated_at = _utc_now_naive()
    db.flush()
    return row


def is_integrity_unique_violation(exc: IntegrityError) -> bool:
    orig: Any = getattr(exc, "orig", None)
    if orig is not None and hasattr(orig, "pgcode"):
        return str(orig.pgcode) == "23505"
    msg = str(exc).lower()
    return "unique" in msg or "duplicate" in msg
