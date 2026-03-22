from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import MajorCategoryCreate, MajorCategoryOut, MajorCategoryRename

router = APIRouter(prefix="/major-categories", tags=["major_categories"])


@router.get("", response_model=list[MajorCategoryOut])
def list_major_categories(db: Session = Depends(get_db)) -> list[MajorCategoryOut]:
    rows = crud.list_major_categories(db)
    return [MajorCategoryOut.model_validate(r) for r in rows]


@router.post("", response_model=MajorCategoryOut, status_code=status.HTTP_201_CREATED)
def create_major_category(
    body: MajorCategoryCreate, db: Session = Depends(get_db)
) -> MajorCategoryOut:
    try:
        row = crud.create_major_category(db, body.name)
        db.commit()
        db.refresh(row)
    except IntegrityError as e:
        db.rollback()
        if crud.is_integrity_unique_violation(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="同じ名前の大項目が既に存在します。",
            ) from e
        raise
    return MajorCategoryOut.model_validate(row)


@router.patch("/{category_id}", response_model=MajorCategoryOut)
def rename_major_category(
    category_id: int, body: MajorCategoryRename, db: Session = Depends(get_db)
) -> MajorCategoryOut:
    try:
        row = crud.rename_major_category(db, category_id, body.name)
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
                detail="同じ名前の大項目が既に存在します。",
            ) from e
        raise
    return MajorCategoryOut.model_validate(row)
