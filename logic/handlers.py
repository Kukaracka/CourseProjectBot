from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram import F

import csv


from FSM import Reg, FSMContext


from aiogram import Router

from photos_and_constant_messages.constant_messages import start_message

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
    with open('../data/id_names.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        field = ('id', 'name')
        writer.writerow(field)
        writer.writerow([message.from_user.id, message.text])