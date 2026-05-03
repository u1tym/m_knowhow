from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.jwt_auth import verified_username_from_request
from app.models import Account


def get_current_aid(
    request: Request,
    db: Session = Depends(get_db),
) -> int:
    username = verified_username_from_request(request)
    stmt = select(Account.id).where(
        Account.username == username,
        Account.is_deleted.is_(False),
    )
    aid = db.scalar(stmt)
    if aid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません。",
        )
    return int(aid)
