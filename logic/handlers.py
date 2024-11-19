from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F

import csv

from FSM import Reg, FSMContext
import database.requests as rq


from aiogram import Router

from photos_and_constant_messages.constant_messages import start_message, complete_registration

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer_photo(photo="AgACAgIAAxkBAAMwZzyI9-KJ0NNSRz80VVAAAVrq1q-FAAJF5TEbJfXpSey_l44yqu19AQADAgADeQADNgQ",
                               caption=start_message)

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
    print(res)
    await message.answer(complete_registration)
    await rq.setter_user_information(message.from_user.id, data)