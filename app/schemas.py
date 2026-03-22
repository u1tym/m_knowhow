from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MajorCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_order: int
    created_at: datetime
    updated_at: datetime


class MajorCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, description="大項目名（DB上ユニーク）")


class MajorCategoryRename(BaseModel):
    name: str = Field(..., min_length=1, description="変更後の大項目名")


class MiddleCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    major_category_id: int
    name: str
    display_order: int
    created_at: datetime
    updated_at: datetime


class MiddleCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, description="中項目名（同一大大項目内でユニーク）")


class MiddleCategoryRename(BaseModel):
    name: str = Field(..., min_length=1, description="変更後の中項目名")


class KnowhowListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    keywords: str | None
    display_order: int
    middle_category_id: int | None
    created_at: datetime
    updated_at: datetime


class KnowhowDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    keywords: str | None
    content: str
    display_order: int
    middle_category_id: int | None
    created_at: datetime
    updated_at: datetime
