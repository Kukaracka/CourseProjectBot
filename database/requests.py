from sqlalchemy.sql.functions import current_date

from database.models import async_session
from database.models import InformationAboutUser, Task, City, ActualCity

from sqlalchemy import select, update, delete
import asyncio

from datetime import date


async def setter_user_information(tg_id, data):
    async with async_session() as session:
        user = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        if not user:
            session.add(InformationAboutUser(tg_id=tg_id, name=data['name'],
                                             time=data['time_to_message'], sity=data['city'].capitalize()))
        else:
            user = await session.get(InformationAboutUser, tg_id)
            user.name = data['name']
            user.time = data['time_to_message']
            user.city = data['city'].capitalize()
        await session.commit()

async def setter_sity(name, url, translit):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        if not city:
            session.add(City(name=name, url=url, translit=translit))
        else:
            sity = await session.scalar(select(City).where(City.name == name))
            sity.url = url
        await session.commit()

async def getter_city_in_bd(city: str) -> bool:
    async with async_session() as session:
        city = city.capitalize()
        result = await session.scalar(select(City).where(City.name == city))
        await session.commit()
        if not result:
            return False
        else:
            return True

async def setter_new_task(tg_id, date, description):
    async with async_session() as session:
        session.add(Task(tg_id=tg_id, description=description, date = date, remind1=False,
                         remind3=False, remind7=False, remind30=False))
        await session.commit()

async def getter_all_tasks(tg_id, all: bool):
    current_date = date.today()
    async with async_session() as session:
        result = []
        current_date = str(current_date.day) + '.' + str(current_date.month)
        if all:
            tasks = await session.scalars(select(Task).where(Task.tg_id == tg_id))
        else:
            tasks = await session.scalars(select(Task).where((Task.date == current_date) | (Task.date == "1")))
        for i in tasks.all():
            result.append([i.date, i.description])
        await session.commit()
        return result

async def getter_city_name(tg_id):
    async with async_session() as session:
        time = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        await session.close()
        if time.sity.capitalize():
            return time.sity.capitalize()
        else:
            return ValueError

async def getter_url_from_city(city):
    async with async_session() as session:
        time = await session.scalar(select(City).where(City.name == city))
        await session.close()
        if time.url:
            return time.url
        else:
            return ValueError

async def add_actual_city(name_eng):
    async with async_session() as session:
        city = await session.scalar(select(ActualCity).where(ActualCity.name_eng == name_eng))
        if not city:
            session.add(ActualCity(name_eng=name_eng, name=name_eng))
        else:
            sity = await session.scalar(select(ActualCity).where(ActualCity.name_eng == name_eng))
            sity.name = name_eng
        await session.close()

        await session.commit()
async def getter_city_eng(name):
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        await session.close()
    if city is not None:
        return city.translit
    else:
        print(name)

async def getter_all_information(tg_id):
    async with async_session() as session:
        data = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        await session.close()
        print(data)
        return (data.name, data.sity.capitalize())



