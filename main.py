import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import router
from web import flask_app


async def telegram_bot():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(telegram_bot()),
        loop.run_in_executor(None, flask_app),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    main()
