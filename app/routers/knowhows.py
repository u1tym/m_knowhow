from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import get_current_aid
from app.schemas import KnowhowDetailOut, KnowhowListItemOut

router = APIRouter(tags=["knowhows"])


@router.get(
    "/middle-categories/{middle_category_id}/knowhows",
    response_model=list[KnowhowListItemOut],
)
def list_knowhows(
    middle_category_id: int,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> list[KnowhowListItemOut]:
    middle = crud.get_middle_category_if_active(db, middle_category_id, aid)
    if middle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="中項目が見つからないか、削除済みです。",
        )
    rows = crud.list_knowhows_by_middle(db, middle_category_id, aid)
    return [KnowhowListItemOut.model_validate(r) for r in rows]


@router.get("/knowhows/{knowhow_id}", response_model=KnowhowDetailOut)
def get_knowhow(
    knowhow_id: int,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> KnowhowDetailOut:
    row = crud.get_knowhow_detail(db, knowhow_id, aid)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ノウハウが見つからないか、削除済みです。",
        )
    return KnowhowDetailOut.model_validate(row)
