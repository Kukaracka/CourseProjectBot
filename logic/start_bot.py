import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.BOT_TOKEN import token

from handlers import router

bot = Bot(token=token)
dp = Dispatcher()


async  def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Exit")