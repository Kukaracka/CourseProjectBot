from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F
import time
import csv

from FSM import Reg, FSMContext
import database.requests as rq
from parser import get_weather


from aiogram import Router

from logic.FSM import NewTask
from photos_and_constant_messages.constant_messages import start_message, complete_registration

import keyboards as kb

async def create_weather_list(city_name):
    weathet_term, weather_cond = await get_weather(city_name)
    result = (f"Утром на улице {weather_cond[0]}, {weathet_term[0]}\nДнем - {weather_cond[1]}, {weathet_term[1]}\n"
              f"Вечером - {weather_cond[2]}, {weathet_term[2]}\nНочью - {weather_cond[3]}, {weathet_term[3]}\n\n")
    return result


async def generate_task_list(data):
    data = sorted(data)
    result = ""
    for i, j in enumerate(data):
        if j[0] == "1":
            result += f'  {str(i+1)}. {j[1]} (ежедневно)\n'
        else:
            result += f'  {str(i+1)}. {j[1]} ({j[0]})\n'
    return result

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer_photo(photo="AgACAgIAAxkBAAMwZzyI9-KJ0NNSRz80VVAAAVrq1q-FAAJF5TEbJfXpSey_l44yqu19AQADAgADeQADNgQ",
                               caption=start_message)
    await message.answer("Для начала, подскажите, как я могу к вам обращаться?")

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'{message.photo[-1].file_id}')

@router.message(Reg.name)
async def name_capture(message: Message, state=Reg.name):
    await state.update_data(name=message.text)
    await state.set_state(Reg.time_to_message)
    await message.answer(f'Очень приятно, {message.text}, теперь подскажите, во сколько '
                         f'вам будет удобно получать от ежедневный прогноз?\n\n'
                         f'Введите в формате часы:минуты, например 9:00')


@router.callback_query(F.data=="change_info")
async def name_capture_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg.name)
    await callback.message.answer("Для начала, подскажите, как я могу к вам обращаться?")

@router.message(Reg.time_to_message)
async def time_to_message_capture(message: Message, state=Reg.time_to_message):
    await state.update_data(time_to_message = message.text)
    await state.set_state(Reg.city)
    await message.answer('Подскажите, в каком городе вы живёте?')

@router.message(Reg.city)
async def city_capture(message: Message, state=Reg.city):
    await state.update_data(city = message.text)
    data = await state.get_data()
    res = await rq.getter_city_in_bd(message.text)
    await message.answer(complete_registration,
                         reply_markup=kb.main_menu)
    await rq.setter_user_information(message.from_user.id, data)

@router.callback_query(F.data == "to_main")
async def to_main_forward(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    name = await rq.getter_city_name(user_id)

    weather_mess = await create_weather_list(name)
    data = await rq.getter_all_tasks(callback.from_user.id, all=False)
    mess = await generate_task_list(data)
    await callback.message.answer_photo(photo="AgACAgIAAxkBAAICFWc9XJ5_qPu6YpMQsDx3qF4MjqvuAAJI7jEbYx7oSVsxVBPQwFS1AQADAgADeQADNgQ",
                                        caption=f"{weather_mess}"
                                                f"Ваши задачи на сегодняшний день:\n\n{mess}",
                                        reply_markup=kb.main_menu)
    await callback.answer('Вы вернулись на главную')



@router.callback_query(F.data == "new_task")
async def new_task_begin(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Опишите вашу новую задачу')
    await callback.message.answer("Введите краткое описание задачи:",
                                  reply_markup=kb.to_main_from_anywhere)
    await state.set_state(NewTask.description)

@router.message(NewTask.description)
async def new_task_description(message: Message, state: NewTask.description):
    await state.update_data(description = message.text)
    await message.answer("Введите дату, в которую нужно "
                        "выполнить задачу (если задача ежедневная - введите 1):",
                         reply_markup=kb.to_main_from_anywhere)
    await state.set_state(NewTask.date)

@router.message(NewTask.date)
async def new_task_date(message: Message, state: NewTask.date):
    await state.update_data(date = message.text)
    data = await state.get_data()
    await rq.setter_new_task(message.from_user.id, data['date'], data['description'])
    await message.answer("Отлично! Новая задача добавлена.",
                         reply_markup=kb.to_main_from_anywhere)

@router.callback_query(F.data == "get_all_tasks")
async def watch_current_tasks(callback: CallbackQuery):
    await callback.answer()
    data = await rq.getter_all_tasks(callback.from_user.id, all=True)
    mess = await generate_task_list(data)
    await callback.message.answer(f'Вот все ваши задачи!\n\n{mess}',
                                  reply_markup=kb.to_main_from_anywhere)

@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    mess = await rq.getter_all_information(callback.from_user.id)
    mess = (f'\nВаше имя - {mess[0]}\n'
            f'Город - {mess[1]}\n\n')
    await callback.message.answer(mess,
                                  reply_markup=kb.settings)



