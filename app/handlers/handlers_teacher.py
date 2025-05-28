from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, URLInputFile, Message

from app.APIhandlers.APIhandlersUser import get_user_by_id
from app.utils.jsons_creator import UserStorage
from config_local import profile_photos
from app.keyboards import static_keyboard as static_kb
from app.keyboards import keyboard as kb

teacher_router = Router()

storage = UserStorage()

JSON_DATA_DIR = "data/json/"


@teacher_router.callback_query(F.data == "teacher_info")
async def get_teacher_info(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = storage.get_user_credentials(callback.from_user.id).db_id
    user = get_user_by_id(user_id)

    if not user:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    info_text = (
        f"🧑‍🎓 Информация о вас:\n\n"
        f"▫️ <b>Фамилия:</b> {user.get('surname', '')}\n"
        f"▫️ <b>Имя:</b> {user.get('name', '')}\n"
        f"▫️ <b>Отчество:</b> {user.get('patronym', '')}\n"
        f"▫️ <b>Категория</b> {user.get('category').get('title')[-1]}"
    )

    if user.get('image') is None:
        await callback.message.answer_photo(
            photo=FSInputFile("static/img/default.jpg"),
            caption=info_text,
            parse_mode='HTML',
            reply_markup=static_kb.teacher_info
        )
    else:
        await callback.message.answer_photo(
            photo=URLInputFile(f"{profile_photos}{user.get('image')}"),
            caption=info_text,
            parse_mode='HTML',
            reply_markup=static_kb.teacher_info
        )


async def handle_back_to_teacher_menu(message: Message, user_id):
    user = get_user_by_id(storage.get_user_credentials(user_id).db_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.get('surname', '')} {user.get('name', '')}, Ваша роль Учитель',
        reply_markup=static_kb.teacher_main
    )


@teacher_router.callback_query(F.data == "back_to_teacher_menu")
async def back_to_teacher_menu(callback: CallbackQuery, state: FSMContext):
    user_id = storage.get_user_credentials(callback.from_user.id).db_id
    user = get_user_by_id(user_id)
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await callback.message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await callback.message.answer(
        f'Привет, {user.get('surname', '')} {user.get('name', '')}, Ваша роль Админ',
        reply_markup=static_kb.teacher_main
    )