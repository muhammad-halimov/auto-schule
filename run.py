import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.handlers.handlers_admin import admin_router
from app.handlers.handlers_instructor import instructor_router
from config_local import TOKEN
from app.handlers.handlers import main_router
from app.handlers.handlers_student import student_router
from app.handlers.handlers_info import info_router
from app.handlers.handlers_teacher import teacher_router

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(main_router)
    dp.include_router(admin_router)
    dp.include_router(student_router)
    dp.include_router(info_router)
    dp.include_router(teacher_router)
    dp.include_router(instructor_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
