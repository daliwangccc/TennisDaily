"""Insert sample data for development."""
import asyncio
from datetime import date, datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base
from app.models.article import Article
from app.models.player import Player
from app.models.tournament import Tournament
from app.models.match import Match
from app.models.ranking import Ranking
from app.config import settings


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        count = (await db.execute(select(func.count(Player.id)))).scalar()
        if count and count > 0:
            print("Database already has data, skipping seed.")
            return

        # -- Players --
        players = [
            Player(id=1, name_en="Jannik Sinner", name_cn="辛纳", country="ITA", hand="R", height_cm=191, turned_pro=2018),
            Player(id=2, name_en="Novak Djokovic", name_cn="德约科维奇", country="SRB", hand="R", height_cm=188, turned_pro=2003),
            Player(id=3, name_en="Carlos Alcaraz", name_cn="阿尔卡拉斯", country="ESP", hand="R", height_cm=183, turned_pro=2018),
            Player(id=4, name_en="Alexander Zverev", name_cn="兹维列夫", country="GER", hand="R", height_cm=198, turned_pro=2013),
            Player(id=5, name_en="Daniil Medvedev", name_cn="梅德韦杰夫", country="RUS", hand="R", height_cm=198, turned_pro=2014),
            Player(id=6, name_en="Aryna Sabalenka", name_cn="萨巴伦卡", country="BLR", hand="R", height_cm=182, turned_pro=2015),
            Player(id=7, name_en="Iga Swiatek", name_cn="斯瓦泰克", country="POL", hand="R", height_cm=176, turned_pro=2016),
            Player(id=8, name_en="Coco Gauff", name_cn="高芙", country="USA", hand="R", height_cm=175, turned_pro=2018),
            Player(id=9, name_en="Jasmine Paolini", name_cn="保利尼", country="ITA", hand="R", height_cm=163, turned_pro=2014),
            Player(id=10, name_en="Qinwen Zheng", name_cn="郑钦文", country="CHN", hand="R", height_cm=178, turned_pro=2019),
        ]
        db.add_all(players)

        # -- Tournaments --
        tournaments = [
            Tournament(id=1, name="Australian Open 2026", category="Grand Slam", surface="Hard", location="Melbourne", start_date=date(2026, 1, 19), end_date=date(2026, 2, 1)),
            Tournament(id=2, name="Roland Garros 2026", category="Grand Slam", surface="Clay", location="Paris", start_date=date(2026, 5, 25), end_date=date(2026, 6, 8)),
            Tournament(id=3, name="Monte-Carlo Masters 2026", category="Masters 1000", surface="Clay", location="Monte Carlo", start_date=date(2026, 4, 6), end_date=date(2026, 4, 13)),
        ]
        db.add_all(tournaments)

        # -- Matches --
        matches = [
            Match(tournament_id=3, player1_id=1, player2_id=3, winner_id=1, player1_name="Sinner", player2_name="Alcaraz", score="6-4, 3-6, 7-5", round="Final", surface="Clay", match_date=date(2026, 4, 13), status="finished"),
            Match(tournament_id=3, player1_id=2, player2_id=4, winner_id=2, player1_name="Djokovic", player2_name="Zverev", score="7-6(5), 6-3", round="SF", surface="Clay", match_date=date(2026, 4, 12), status="finished"),
            Match(tournament_id=3, player1_id=1, player2_id=5, winner_id=1, player1_name="Sinner", player2_name="Medvedev", score="6-2, 6-4", round="SF", surface="Clay", match_date=date(2026, 4, 12), status="finished"),
            Match(tournament_id=3, player1_id=3, player2_id=4, winner_id=3, player1_name="Alcaraz", player2_name="Zverev", score="6-3, 4-6, 6-4", round="QF", surface="Clay", match_date=date(2026, 4, 11), status="finished"),
        ]
        db.add_all(matches)

        # -- Rankings (ATP) --
        week = date(2026, 4, 14)
        atp_rankings = [
            Ranking(player_id=1, player_name="Jannik Sinner", rank=1, points=11830, tour="ATP", type="singles", week_date=week),
            Ranking(player_id=2, player_name="Novak Djokovic", rank=2, points=9850, tour="ATP", type="singles", week_date=week),
            Ranking(player_id=3, player_name="Carlos Alcaraz", rank=3, points=8580, tour="ATP", type="singles", week_date=week),
            Ranking(player_id=4, player_name="Alexander Zverev", rank=4, points=7815, tour="ATP", type="singles", week_date=week),
            Ranking(player_id=5, player_name="Daniil Medvedev", rank=5, points=6540, tour="ATP", type="singles", week_date=week),
        ]
        wta_rankings = [
            Ranking(player_id=6, player_name="Aryna Sabalenka", rank=1, points=10210, tour="WTA", type="singles", week_date=week),
            Ranking(player_id=7, player_name="Iga Swiatek", rank=2, points=8115, tour="WTA", type="singles", week_date=week),
            Ranking(player_id=8, player_name="Coco Gauff", rank=3, points=7380, tour="WTA", type="singles", week_date=week),
            Ranking(player_id=9, player_name="Jasmine Paolini", rank=4, points=5344, tour="WTA", type="singles", week_date=week),
            Ranking(player_id=10, player_name="Qinwen Zheng", rank=5, points=5140, tour="WTA", type="singles", week_date=week),
        ]
        db.add_all(atp_rankings + wta_rankings)

        # -- Articles --
        articles = [
            Article(title="辛纳逆转阿尔卡拉斯 夺蒙特卡洛大师赛冠军", summary="在一场扣人心弦的三盘大战中，世界第一辛纳以6-4, 3-6, 7-5击败阿尔卡拉斯，赢得蒙特卡洛大师赛冠军。", content="在一场扣人心弦的三盘大战中，世界第一辛纳以6-4, 3-6, 7-5击败阿尔卡拉斯，赢得蒙特卡洛大师赛冠军。这是辛纳本赛季第三个冠军头衔。", source="TennisDaily", category="赛事新闻", published_at=datetime(2026, 4, 13, 20, 0)),
            Article(title="德约科维奇连续第22年闯入大师赛四强", summary="37岁的德约科维奇在蒙特卡洛大师赛中击败兹维列夫，再次证明了自己的竞技状态。", content="37岁的德约科维奇在蒙特卡洛大师赛中击败兹维列夫，再次证明了自己的竞技状态。", source="TennisDaily", category="球员动态", published_at=datetime(2026, 4, 12, 22, 0)),
            Article(title="郑钦文确认出战马德里公开赛", summary="中国金花郑钦文宣布将参加下周开始的马德里公开赛，目前排名WTA第五位。", content="中国金花郑钦文宣布将参加下周开始的马德里公开赛，目前排名WTA第五位。", source="TennisDaily", category="球员动态", published_at=datetime(2026, 4, 14, 10, 0)),
            Article(title="2026红土赛季前瞻：谁将称霸法网？", summary="随着红土赛季的全面展开，让我们一起分析今年法网的夺冠热门。", content="随着红土赛季的全面展开，让我们一起分析今年法网的夺冠热门。辛纳、阿尔卡拉斯和德约科维奇被视为最大热门。", source="TennisDaily", category="评论分析", published_at=datetime(2026, 4, 14, 8, 0)),
            Article(title="ATP最新排名：辛纳领跑 阿尔卡拉斯重返前三", summary="本周ATP排名更新，辛纳以11830分继续领跑，阿尔卡拉斯凭借蒙特卡洛亚军重返第三。", content="本周ATP排名更新，辛纳以11830分继续领跑，阿尔卡拉斯凭借蒙特卡洛亚军重返第三。", source="TennisDaily", category="赛事新闻", published_at=datetime(2026, 4, 14, 12, 0)),
        ]
        db.add_all(articles)

        await db.commit()
        print("Seed data inserted successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
