import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.BOT_TOKEN import token

from handlers import router


from database.models import async_main


async def start_bot():
    await async_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Выключение бота")