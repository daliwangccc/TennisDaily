from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleOut, ArticleDetail, ArticleList

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=ArticleList)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Article)
    count_query = select(func.count(Article.id))

    if category:
        query = query.where(Article.category == category)
        count_query = count_query.where(Article.category == category)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(desc(Article.published_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ArticleList(
        items=[ArticleOut.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{article_id}", response_model=ArticleDetail)
async def get_news(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleDetail.model_validate(article)
