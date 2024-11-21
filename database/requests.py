from sqlalchemy.sql.functions import current_date

from database.models import async_session
from database.models import InformationAboutUser, Task, City, ActualCity, ActualWeather

from sqlalchemy import select, update, delete
import asyncio
from logic import parser

from datetime import date


async def setter_user_information(tg_id: int, name: str, time_to_message: str, city: str) -> None:
    """
    Функция записывает информацию о пользователе в таблицу information_about_users
    :param tg_id:
    :param name:
    :param time_to_message:
    :param city:
    :return:
    """
    async with async_session() as session:
        user = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        if not user:
            session.add(InformationAboutUser(tg_id=tg_id, name=name,
                                             time=time_to_message, sity=city.capitalize()))
        else:
            user = await session.get(InformationAboutUser, tg_id)
            user.name = name
            user.time = time_to_message
            user.city = city.capitalize()
        await session.commit()


async def setter_sity(name: str, url: str, translit: str) -> None:
    """
    функция записывает данные о городе в таблицу cities
    :param name:
    :param url:
    :param translit:
    :return:
    """
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        if not city:
            session.add(City(name=name, url=url, translit=translit))
        else:
            sity = await session.scalar(select(City).where(City.name == name))
            sity.url = url
        await session.commit()


async def getter_city_in_bd(city: str) -> bool:
    """
    Функция возвращает bool значение, есть ли в таблице переданный город, получая данные из таблицы cities
    :param city:
    :return:
    """
    async with async_session() as session:
        city = city.capitalize()
        result = await session.scalar(select(City).where(City.name == city))
        await session.commit()
        if not result:
            return False
        else:
            return True


async def setter_new_task(tg_id: int, date_from_user: int, description: str) -> None:
    """
    Функция добавляет новую задачу в таблицу tasks
    :param tg_id:
    :param date_from_user:
    :param description:
    :return:
    """
    async with async_session() as session:
        session.add(Task(tg_id=tg_id, description=description, date = str(date_from_user), remind1=False,
                         remind3=False, remind7=False, remind30=False))
        await session.commit()


async def getter_all_tasks(tg_id: int, is_all: bool) -> list:
    """
    Функция возвращает все задачи пользователя/задачи пользователя, получая информацию из таблицы tasks
     на текущий день в зависимости от параметра is_all
    :param tg_id:
    :param is_all:
    :return:
    """
    temp_date = date.today()
    async with async_session() as session:
        list_of_tasks = []
        temp_date = str(temp_date.day) + '.' + str(temp_date.month)
        if is_all:
            tasks = await session.scalars(select(Task).where(Task.tg_id == tg_id))
        else:
            tasks = await session.scalars(select(Task).where((Task.date == temp_date) | (Task.date == "1")))
        for i in tasks.all():
            list_of_tasks.append([i.date, i.description])
        await session.commit()
        return list_of_tasks


async def getter_city_name(tg_id: int) -> str:
    """
    Функция возвращает название города, исходя из tg_id, получая информацию из таблицы information_about_users
    :param tg_id:
    :return:
    """
    async with async_session() as session:
        time = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        await session.close()
        if time.sity.capitalize():
            return time.sity.capitalize()
        else:
            return ValueError


async def getter_url_from_city(city: str) -> str:
    """
    Функция возвращает url города исходя из его названия, получая информацию из cities
    :param city:
    :return:
    """
    async with async_session() as session:
        time = await session.scalar(select(City).where(City.name == city))
        await session.close()
        if time.url:
            return time.url
        else:
            return ValueError


async def setter_actual_city(name_eng):
    """
    функция записывает данные о городе в таблицу actual_cities
    :param name_eng:
    :return:
    """
    async with async_session() as session:
        city = await session.scalar(select(ActualCity).where(ActualCity.name_eng == name_eng))
        if not city:
            session.add(ActualCity(name_eng=name_eng, name=name_eng))
        else:
            sity = await session.scalar(select(ActualCity).where(ActualCity.name_eng == name_eng))
            sity.name = name_eng
        await session.commit()
        await session.close()

async def getter_city_eng(name: str) -> str:
    """
    Функция возвращает название города на английском, исходя из его
    названия на русском, получая данные из таблицы cities
    :param name:
    :return:
    """
    async with async_session() as session:
        city = await session.scalar(select(City).where(City.name == name))
        await session.close()
    if city is not None:
        return city.translit
    else:
        print(name)


async def getter_all_information(tg_id: int) -> tuple:
    """
    Функция возвращает информацию о пользователе, исходя из его tg_id, получая
    информацию из таблицы information_about_users
    :param tg_id:
    :return:
    """
    async with async_session() as session:
        data = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))
        await session.close()
        print(data)
        return data.name, data.sity.capitalize()

async def getter_weather_from_db(city: str) -> tuple:
    async with async_session() as session:
        data = await session.scalars(select(ActualWeather).where(ActualWeather.city == city))
        print(data.city, data.weather_temp, data.weather_cond)

async def setter_weather_from_city(city: str):
    temp = ""
    cond = ""
    async with async_session() as session:
        weather_temp, weather_cond = await parser.getter_weather(city)
        for i in range(4):
            temp += f'{weather_temp[i][:-1]},'
            cond += f'{weather_cond[i]},'
        temp = temp[:-1]
        cond = cond[:-1]

        if temp:
            session.add(ActualWeather(city=city, weather_temp=temp, weather_condition=cond))
            await session.commit()
        else:
            await session.commit()
        print('dobav')
async def getter_actual_weather_from_db(city: str) -> tuple:
    async with async_session() as session:
        data = await session.scalar(select(ActualWeather).where(ActualWeather.city == city.capitalize()))
        await session.close()

        if data:
            return data.weather_temp, data.weather_condition





