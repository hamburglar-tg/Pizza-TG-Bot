import asyncio
import logging

from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from src.handlers import dp, bot
from database.db_handler import create_tables


async def main():
    await create_tables()

    commands = await bot.get_my_commands()
    if not commands:
        private_chat_commands = [
            BotCommand(command='start', description='🚀 Главное меню'),
            BotCommand(command='info', description='🔮 Информация'),
            BotCommand(command='support', description='🧑‍💻 Поддержка')
        ]

        await bot.set_my_commands(private_chat_commands, scope=BotCommandScopeAllPrivateChats())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
