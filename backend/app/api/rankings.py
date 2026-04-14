from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.ranking import Ranking
from app.schemas.ranking import RankingOut, RankingList

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("", response_model=RankingList)
async def list_rankings(
    tour: str = Query("ATP", pattern="^(ATP|WTA)$"),
    type: str = Query("singles", pattern="^(singles|doubles)$"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    # Get the latest week_date for this tour/type
    latest_week = await db.execute(
        select(func.max(Ranking.week_date))
        .where(Ranking.tour == tour, Ranking.type == type)
    )
    week_date = latest_week.scalar()

    query = (
        select(Ranking)
        .where(Ranking.tour == tour, Ranking.type == type)
    )
    if week_date:
        query = query.where(Ranking.week_date == week_date)

    query = query.order_by(Ranking.rank).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    count_query = select(func.count(Ranking.id)).where(
        Ranking.tour == tour, Ranking.type == type
    )
    if week_date:
        count_query = count_query.where(Ranking.week_date == week_date)
    total = (await db.execute(count_query)).scalar() or 0

    return RankingList(
        items=[RankingOut.model_validate(r) for r in items],
        total=total,
        tour=tour,
        type=type,
    )
