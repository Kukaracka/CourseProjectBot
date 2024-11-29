import asyncio
import logging
from time import sleep, time
import datetime as dt
import statistics
from creating_functions import *
import keyboards as kb

from aiogram import Bot, Dispatcher
from database import requests as rq
from aiogram.types import FSInputFile

from config.BOT_TOKEN import token

from image_creation import create_image

from handlers import router
from bot import bot

from database.models import async_main


async def start_bot():
    await async_main()
    asyncio.get_event_loop().create_task(check_time())
    await dp.start_polling(bot)


async def check_time():
    while True:
        # await asyncio.sleep(60)
        hours, minutes = dt.datetime.now().time().hour, dt.datetime.now().time().minute
        # print(dt.datetime.now().time().hour, dt.datetime.now().time().minute)
        temp_time = f"{hours}:{minutes}"
        user_time_list = await rq.getter_user_id_from_time(temp_time)
        for current_user in user_time_list:
            name = await rq.getter_all_information(current_user)
            name = name[0]
            city = await rq.getter_city_name(current_user)
            await rq.setter_weather_from_city(city)
            weather_temp, weather_cond = await rq.getter_actual_weather_from_db(city)
            weather_temp_time = []
            for i in weather_temp.split(","):
                weather_temp_time.append(int(i))
            weather_temp_time = round(statistics.mean(weather_temp_time))
            weather_cond_time = weather_cond.split(",")[2]
            day = dt.datetime.now().day
            month = dt.datetime.now().month
            await create_image(style = 2, ratio="2:3", tg_id=current_user,
                               weather_mean=weather_temp_time, weather_cond=weather_cond_time)

            task_list = await rq.getter_all_tasks(current_user, is_all=False)
            tasks = await create_task_list(task_list)
            weather_mess = await create_weather_list(weather_temp, weather_cond)
            image = FSInputFile(f"../images/{current_user}.jpg")

            await bot.send_photo(chat_id=current_user, photo=image,
                                 caption=f"Добрый день, {name} ❤️\n\n"
                                         f"Погода на сегодня:\n\n"
                                         f"{weather_mess}"f"Ваши задачи на день:\n\n"
                                         f"{tasks}",
                                 reply_markup=kb.main_menu)
            await delete_messages(current_user)
        await asyncio.sleep(60)

async def delete_messages(tg_id):
    messages_list = await rq.getter_messages_for_delete(tg_id)
    for tg_id, current_message in messages_list:
        await bot.delete_message(chat_id=tg_id, message_id=current_message)

async def send_message(hours, minutes):
    # await bot.send_message(chat_id=470068887, text=f"{hours} {minutes}")
    pass


if __name__ == '__main__':
    global bot
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Выключение бота")