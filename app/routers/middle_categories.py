from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import get_current_aid
from app.schemas import MiddleCategoryCreate, MiddleCategoryOut, MiddleCategoryRename

router = APIRouter(tags=["middle_categories"])


@router.get(
    "/major-categories/{major_category_id}/middle-categories",
    response_model=list[MiddleCategoryOut],
)
def list_middle_categories(
    major_category_id: int,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> list[MiddleCategoryOut]:
    if crud.get_major_category_if_active(db, major_category_id, aid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大項目が見つからないか、削除済みです。",
        )
    rows = crud.list_middle_categories(db, major_category_id, aid)
    return [MiddleCategoryOut.model_validate(r) for r in rows]


@router.post(
    "/major-categories/{major_category_id}/middle-categories",
    response_model=MiddleCategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_middle_category(
    major_category_id: int,
    body: MiddleCategoryCreate,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> MiddleCategoryOut:
    try:
        row = crud.create_middle_category(db, major_category_id, body.name, aid)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="大項目が見つからないか、削除済みです。",
            )
        db.commit()
        db.refresh(row)
    except IntegrityError as e:
        db.rollback()
        if crud.is_integrity_unique_violation(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="この大項目の下に同じ名前の中項目が既に存在します。",
            ) from e
        raise
    return MiddleCategoryOut.model_validate(row)


@router.patch("/middle-categories/{category_id}", response_model=MiddleCategoryOut)
def rename_middle_category(
    category_id: int,
    body: MiddleCategoryRename,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> MiddleCategoryOut:
    try:
        row = crud.rename_middle_category(db, category_id, body.name, aid)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="中項目が見つからないか、削除済みです。",
            )
        db.commit()
        db.refresh(row)
    except IntegrityError as e:
        db.rollback()
        if crud.is_integrity_unique_violation(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="同じ大項目の下に同じ名前の中項目が既に存在します。",
            ) from e
        raise
    return MiddleCategoryOut.model_validate(row)
