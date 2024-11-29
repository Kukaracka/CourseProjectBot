from sqlalchemy import BigInteger, String, ForeignKey, Boolean, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine



engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class InformationAboutUser(Base):
    __tablename__ = "information_about_users"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    time: Mapped[str] = mapped_column(String(32))
    sity: Mapped[str] = mapped_column(String(32))

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column()
    date: Mapped[str] = mapped_column(String(12))
    description: Mapped[str] = mapped_column(String(512))
    remind1: Mapped[bool] = mapped_column(Boolean())
    remind3: Mapped[bool] = mapped_column(Boolean())
    remind7: Mapped[bool] = mapped_column(Boolean())
    remind30: Mapped[bool] = mapped_column(Boolean())

class City(Base):
    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    url: Mapped[str] = mapped_column(String(256))
    translit: Mapped[str] = mapped_column(String(64))

class ActualCity(Base):
    __tablename__ = "actual_cities"

    name: Mapped[str] = mapped_column(primary_key=True)
    name_eng: Mapped[str] = mapped_column(String(32))

class ActualWeather(Base):
    __tablename__ = "actual_weather"

    city: Mapped[str] = mapped_column(primary_key=True)
    weather_temp: Mapped[str] = mapped_column(String(32))
    weather_condition: Mapped[str] = mapped_column(String(32))

class MessageForDelete(Base):
    __tablename__ = "messages_for_delete"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column()
    message_id: Mapped[int] = mapped_column()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)





