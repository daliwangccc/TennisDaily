from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import date
from app.database import get_db
from app.models.match import Match
from app.schemas.match import MatchOut, MatchDetail, MatchList

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchList)
async def list_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    match_date: date | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Match)
    count_query = select(func.count(Match.id))

    if match_date:
        query = query.where(Match.match_date == match_date)
        count_query = count_query.where(Match.match_date == match_date)
    if status:
        query = query.where(Match.status == status)
        count_query = count_query.where(Match.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(desc(Match.match_date)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return MatchList(
        items=[MatchOut.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{match_id}", response_model=MatchDetail)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchDetail.model_validate(match)
