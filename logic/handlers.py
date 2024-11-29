from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
from aiogram import F
from bot import bot
from creating_functions import *

import os.path

from FSM import Reg, FSMContext
import database.requests as rq


from aiogram import Router

from logic.FSM import NewTask
from photos_and_constant_messages.constant_messages import start_message, complete_registration

import keyboards as kb


async def delete_messages(tg_id):
    messages_list = await rq.getter_messages_for_delete(tg_id)
    for tg_id, current_message in messages_list:
        await bot.delete_message(chat_id=tg_id, message_id=current_message)


router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    msg1 = await message.answer_photo(photo="AgACAgIAAxkBAAMwZzyI9-KJ0NNSRz80VVAAAVrq1q-FAAJF5TEbJfXpSey_l44yqu19AQADAgADeQADNgQ",
                               caption=start_message)
    msg2 = await message.answer("Для начала, подскажите, как я могу к вам обращаться?")
    await rq.setter_message_for_delete(message.from_user.id, msg1.message_id)
    await rq.setter_message_for_delete(message.from_user.id, msg2.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'{message.photo[-1].file_id}')

@router.message(Reg.name)
async def name_capture(message: Message, state=Reg.name):
    await state.update_data(name=message.text)
    await state.set_state(Reg.time_to_message)
    msg = await message.answer(f'Очень приятно, {message.text}, теперь подскажите, во сколько '
                         f'вам будет удобно получать от ежедневный прогноз?\n\n'
                         f'Введите в формате часы:минуты, например 9:00')
    await rq.setter_message_for_delete(message.from_user.id, msg.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)

@router.callback_query(F.data=="change_info")
async def name_capture_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg.name)
    msg = await callback.message.answer("Для начала, подскажите, как я могу к вам обращаться?")
    await rq.setter_message_for_delete(callback.from_user.id, msg.message_id)

@router.message(Reg.time_to_message)
async def time_to_message_capture(message: Message, state=Reg.time_to_message):
    await state.update_data(time_to_message = message.text)
    await state.set_state(Reg.city)
    msg = await message.answer('Подскажите, в каком городе вы живёте?')
    await rq.setter_message_for_delete(message.from_user.id, msg.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)

@router.message(Reg.city)
async def city_capture(message: Message, state=Reg.city):
    await state.update_data(city = message.text)
    data = await state.get_data()
    msg = await message.answer(complete_registration,
                         reply_markup=kb.main_menu)
    await rq.setter_user_information(message.from_user.id, data["name"], data["time_to_message"], data["city"])
    await rq.setter_weather_from_city(data["city"].capitalize())
    await rq.setter_message_for_delete(message.from_user.id, msg.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)

@router.callback_query(F.data == "to_main")
async def to_main_forward(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    city_name = await rq.getter_city_name(user_id)
    name = await rq.getter_all_information(tg_id=user_id)
    name = name[0]
    weather_term, weather_cond = await rq.getter_actual_weather_from_db(city_name)
    weather_mess = await create_weather_list(weather_term, weather_cond)
    data = await rq.getter_all_tasks(callback.from_user.id, is_all=False)
    mess = await create_task_list(data)
    if os.path.exists(f"../images/{callback.from_user.id}.jpg"):
        image = FSInputFile(f"../images/{callback.from_user.id}.jpg")
    else:
        image = "AgACAgIAAxkBAAIC4mdJ5bU-WuqUhAUrbSHgR432XceRAAI54zEbTgVRSiMqKusTkQYUAQADAgADeQADNgQ"
    msg = await callback.message.answer_photo(photo=image,
                                        caption=f"Добрый день, {name} ❤️\n\n"
                                         f"Погода на сегодня:\n\n"
                                         f"{weather_mess}"f"Ваши задачи на день:\n\n"
                                         f"{mess}",
                                        reply_markup=kb.main_menu)
    await callback.answer('Вы вернулись на главную')
    await delete_messages(callback.from_user.id)
    await rq.setter_message_for_delete(callback.from_user.id, msg.message_id)


@router.callback_query(F.data == "new_task")
async def new_task_begin(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Опишите вашу новую задачу')
    msg = await callback.message.answer("Введите краткое описание задачи:",
                                  reply_markup=kb.to_main_from_anywhere)
    await state.set_state(NewTask.description)
    await rq.setter_message_for_delete(callback.from_user.id, msg.message_id)


@router.message(NewTask.description)
async def new_task_description(message: Message, state: NewTask.description):
    await state.update_data(description = message.text)
    msg = await message.answer("Введите дату, в которую нужно "
                        "выполнить задачу (если задача ежедневная - введите 1):",
                         reply_markup=kb.to_main_from_anywhere)
    await state.set_state(NewTask.date)
    await rq.setter_message_for_delete(message.from_user.id, msg.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)


@router.message(NewTask.date)
async def new_task_date(message: Message, state: NewTask.date):
    await state.update_data(date = message.text)
    data = await state.get_data()
    await rq.setter_new_task(message.from_user.id, data['date'], data['description'])
    msg = await message.answer("Отлично! Новая задача добавлена.",
                         reply_markup=kb.to_main_from_anywhere)
    await rq.setter_message_for_delete(message.from_user.id, msg.message_id)
    await rq.setter_message_for_delete(message.from_user.id, message.message_id)


@router.callback_query(F.data == "get_all_tasks")
async def watch_current_tasks(callback: CallbackQuery):
    await callback.answer()
    data = await rq.getter_all_tasks(callback.from_user.id, is_all=True)
    mess = await create_task_list(data)
    msg = await callback.message.answer(f'Вот все ваши задачи!\n\n{mess}',
                                  reply_markup=kb.to_main_from_anywhere)
    await delete_messages(callback.from_user.id)
    await rq.setter_message_for_delete(callback.from_user.id, msg.message_id)


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await rq.getter_all_information(callback.from_user.id)
    mess = (f'\nВаше имя - {data[0]}\n'
            f'Город - {data[1]}\n'
            f'Время отправки сообщений - {data[2]}\n')
    msg = await callback.message.answer_photo(photo="AgACAgIAAxkBAAIDSGdKENIEzBT_czJjY70ZsfNZTLxxAAJx5jEbZypRSqNnlMVmXcEdAQADAgADeQADNgQ"
                                        ,caption=mess,
                                        reply_markup=kb.settings)
    await delete_messages(callback.from_user.id)
    await rq.setter_message_for_delete(callback.from_user.id, msg.message_id)


