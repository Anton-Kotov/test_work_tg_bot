import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import BotCommand

from tg_bot.config import load_config
from tg_bot.database.pg_command import Database
from tg_bot.modules.logging_set import logger


from tg_bot.handlers.admin import register_admin
from tg_bot.handlers.start import register_start



def register_all_handlers(dp):
    register_start(dp)
    register_admin(dp)

async def set_all_default_commands(bot: Bot):
    return await bot.set_my_commands(commands=[BotCommand("start", "начало работы с ботом"),
                                               BotCommand("admin", "панель администратора")])
async def main():

    logger.info("Запуск бота")
    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    db = Database()
    bot["db"] = db

    register_all_handlers(dp)
    await set_all_default_commands(bot)


    try:
        await db.create()
        await dp.start_polling()

    finally:
        await db.close()
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger().error("Завершение бота")
