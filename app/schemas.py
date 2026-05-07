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


class KnowhowCreate(BaseModel):
    title: str = Field(..., min_length=1, description="ノウハウタイトル")
    keywords: str | None = Field(default=None, description="キーワード")
    content: str = Field(..., min_length=1, description="本文")
    middle_category_id: int | None = Field(
        default=None, description="中項目ID（未分類の場合はnull）"
    )


class KnowhowUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, description="変更後タイトル")
    keywords: str | None = Field(default=None, description="変更後キーワード")
    content: str | None = Field(default=None, min_length=1, description="変更後本文")
    middle_category_id: int | None = Field(
        default=None, description="変更後中項目ID（未分類の場合はnull）"
    )


class KnowhowSwapDisplayOrderIn(BaseModel):
    knowhow_id_a: int = Field(..., description="ノウハウID（一方）")
    knowhow_id_b: int = Field(..., description="ノウハウID（他方）")


class KnowhowSwapDisplayOrderOut(BaseModel):
    knowhow_a: KnowhowListItemOut
    knowhow_b: KnowhowListItemOut


class KnowhowKeywordSearchItemOut(BaseModel):
    major_category_id: int | None = Field(
        default=None, description="大項目ID（未分類ノウハウは null）"
    )
    major_category_name: str | None = Field(default=None, description="大項目名称")
    middle_category_id: int | None = Field(
        default=None, description="中項目ID（未分類ノウハウは null）"
    )
    middle_category_name: str | None = Field(default=None, description="中項目名称")
    knowhow_id: int
    title: str
    display_order: int
