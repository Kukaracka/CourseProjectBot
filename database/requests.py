from database.models import async_session
from database.models import InformationAboutUser, Task, City

from sqlalchemy import select, update, delete


async def setter_user_information(tg_id, data):
    async with async_session() as session:
        user = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))

        if not user:
            session.add(InformationAboutUser(tg_id=tg_id, name=data['name'],
                                             time=data['time_to_message'], sity=data['city']))
        else:
            user = await session.get(InformationAboutUser, tg_id)
            user.name = data['name']
            user.time = data['time_to_message']
            user.city = data['city'].capitalize()
        await session.commit()

async def setter_sity(name, url):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        if not city:
            session.add(City(name=name, url=url))
        else:
            sity = await session.scalar(select(City).where(City.name == name))
            sity.url = url
        await session.commit()

async def getter_city_in_bd(city: str) -> bool:
    async with async_session() as session:
        city = city.capitalize()
        result = await session.scalar(select(City).where(City.name == city))
        await session.commit()
        print(city, result)
        if not result:
            return False
        else:
            return True

    # return city in result