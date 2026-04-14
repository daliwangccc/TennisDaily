from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_cn: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str | None] = mapped_column(String(100))
    birth_date: Mapped[str | None] = mapped_column(Date)
    hand: Mapped[str | None] = mapped_column(String(10))       # R / L
    backhand: Mapped[str | None] = mapped_column(String(10))   # one / two
    height_cm: Mapped[int | None] = mapped_column(Integer)
    turned_pro: Mapped[int | None] = mapped_column(Integer)
    coach: Mapped[str | None] = mapped_column(String(200))
    photo_url: Mapped[str | None] = mapped_column(String(1000))
