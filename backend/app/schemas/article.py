from pydantic import BaseModel
from datetime import datetime


class ArticleOut(BaseModel):
    id: int
    title: str
    summary: str | None = None
    source: str | None = None
    source_url: str | None = None
    category: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleOut):
    content: str | None = None


class ArticleList(BaseModel):
    items: list[ArticleOut]
    total: int
    page: int
    page_size: int
