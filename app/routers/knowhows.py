from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import get_current_aid
from app.schemas import (
    KnowhowCreate,
    KnowhowDetailOut,
    KnowhowKeywordSearchItemOut,
    KnowhowListItemOut,
    KnowhowSwapDisplayOrderIn,
    KnowhowSwapDisplayOrderOut,
    KnowhowUpdate,
)

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


@router.get("/knowhows/search", response_model=list[KnowhowKeywordSearchItemOut])
def search_knowhows_by_keywords(
    keyword: Annotated[list[str], Query(min_length=1)],
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> list[KnowhowKeywordSearchItemOut]:
    rows = crud.search_knowhows_by_keywords_all_match(db, aid, keyword)
    out: list[KnowhowKeywordSearchItemOut] = []
    for knowhow, middle, major in rows:
        out.append(
            KnowhowKeywordSearchItemOut(
                major_category_id=major.id if major is not None else None,
                major_category_name=major.name if major is not None else None,
                middle_category_id=middle.id if middle is not None else None,
                middle_category_name=middle.name if middle is not None else None,
                knowhow_id=knowhow.id,
                title=knowhow.title,
                display_order=knowhow.display_order,
            )
        )
    return out


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


@router.post("/knowhows", response_model=KnowhowDetailOut, status_code=status.HTTP_201_CREATED)
def create_knowhow(
    body: KnowhowCreate,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> KnowhowDetailOut:
    row = crud.create_knowhow(
        db,
        aid=aid,
        title=body.title,
        keywords=body.keywords,
        content=body.content,
        middle_category_id=body.middle_category_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="中項目が見つからないか、削除済みです。",
        )
    db.commit()
    db.refresh(row)
    return KnowhowDetailOut.model_validate(row)


@router.patch("/knowhows/{knowhow_id}", response_model=KnowhowDetailOut)
def update_knowhow(
    knowhow_id: int,
    body: KnowhowUpdate,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> KnowhowDetailOut:
    row = crud.update_knowhow(
        db,
        aid=aid,
        knowhow_id=knowhow_id,
        title=body.title,
        keywords=body.keywords,
        content=body.content,
        middle_category_id=body.middle_category_id,
        middle_category_id_provided="middle_category_id" in body.model_fields_set,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ノウハウまたは中項目が見つからないか、削除済みです。",
        )
    db.commit()
    db.refresh(row)
    return KnowhowDetailOut.model_validate(row)


@router.post(
    "/knowhows/swap-display-order",
    response_model=KnowhowSwapDisplayOrderOut,
)
def swap_knowhow_display_order(
    body: KnowhowSwapDisplayOrderIn,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> KnowhowSwapDisplayOrderOut:
    if body.knowhow_id_a == body.knowhow_id_b:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="同じノウハウIDを2つ指定することはできません。",
        )
    a = crud.get_knowhow_detail(db, body.knowhow_id_a, aid)
    b = crud.get_knowhow_detail(db, body.knowhow_id_b, aid)
    if a is None or b is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ノウハウが見つからないか、削除済みです。",
        )
    if a.middle_category_id != b.middle_category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="同一中項目に属するノウハウ同士（または未分類同士）のみ表示順を入れ替えできます。",
        )
    crud.swap_knowhow_display_orders(db, a, b)
    db.commit()
    db.refresh(a)
    db.refresh(b)
    return KnowhowSwapDisplayOrderOut(
        knowhow_a=KnowhowListItemOut.model_validate(a),
        knowhow_b=KnowhowListItemOut.model_validate(b),
    )


@router.delete("/knowhows/{knowhow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowhow(
    knowhow_id: int,
    db: Session = Depends(get_db),
    aid: int = Depends(get_current_aid),
) -> None:
    row = crud.soft_delete_knowhow(db, aid=aid, knowhow_id=knowhow_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ノウハウが見つからないか、すでに削除済みです。",
        )
    db.commit()
