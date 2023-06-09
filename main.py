import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import handler


bot = Bot(token="5918123308:AAHOPBzpxWq1gB5mQbvXnTSJyBQ6foLT8Zs")


# Запуск бота
async def main():
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handler.router)

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await dp.storage.close()


if __name__ == "__main__":
    asyncio.run(main())
