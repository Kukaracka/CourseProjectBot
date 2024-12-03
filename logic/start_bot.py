import sys
import os
from pprint import pprint
sys.path.append(os.path.join(os.getcwd(), 'logic'))
pprint(sys.path)


import asyncio
import logging
import datetime as dt
import statistics
from logic.chatting_functions import *
import logic.keyboards as kb



from aiogram import Dispatcher
from database import requests as rq
from aiogram.types import FSInputFile


from logic.image_creation import create_image

from logic.handlers import router
from logic.bot import bot

from database.models import async_main


async def start_bot():
    await async_main()
    asyncio.get_event_loop().create_task(send_timely_messages())
    await dp.start_polling(bot)


async def send_timely_messages():
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
            await create_image(style = 2, ratio="2:3", tg_id=current_user,
                               weather_mean=weather_temp_time, weather_cond=weather_cond_time)

            task_list = await rq.getter_all_tasks(current_user, is_all=False)
            tasks = await create_task_list(task_list)
            weather_mess = await create_weather_list(weather_temp, weather_cond)
            image = FSInputFile(f"../images/{current_user}.jpg")

            msg = await bot.send_photo(chat_id=current_user, photo=image,
                                 caption=f"Добрый день, {name} ❤️\n\n"
                                         f"Погода на сегодня:\n"
                                         f"{weather_mess}"f"Ваши задачи на день:\n"
                                         f"{tasks}",
                                 reply_markup=kb.main_menu)
            await delete_messages(current_user)
            await rq.setter_message_for_delete(current_user, msg.message_id)
        await asyncio.sleep(60)

async def delete_messages(tg_id):
    messages_list = await rq.getter_messages_for_delete(tg_id)
    for tg_id, current_message in messages_list:
        await bot.delete_message(chat_id=tg_id, message_id=current_message)


if __name__ == '__main__':
    global bot
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Выключение бота")