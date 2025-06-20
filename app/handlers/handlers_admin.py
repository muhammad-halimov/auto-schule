import asyncio
import logging
import re
from datetime import datetime, time, date

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, URLInputFile, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendarCallback

from app.APIhandlers.APIhandlersAutodrome import get_autodrome_by_id
from app.APIhandlers.APIhandlersCar import get_admin_car_by_id, delete_car, update_car_in_api, add_car_to_api, \
    get_car_mark_title
from app.APIhandlers.APIhandlersInstructor import get_instructor_by_id
from app.APIhandlers.APIhandlersLesson import get_lesson_title, get_lesson_by_id, add_lesson_to_api, \
    delete_lesson_from_api, update_lesson_in_api
from app.APIhandlers.APIhandlersSchedule import delete_schedule_from_api, \
    get_admin_drive_schedule_by_id, update_schedule, add_schedule
from app.APIhandlers.APIhandlersUser import get_user_by_id, delete_user, update_user_by_admin, get_user_name, \
    add_user_by_admin, update_user_data, approve_user_in_api, send_password_for_user_in_api
from app.APIhandlers.APIhandlersCourse import get_course_by_id, delete_course, get_quiz_title, \
    update_course_in_api, add_course_to_api
from app.APIhandlers.APIhandlersCategory import (get_category_by_id, get_admin_category_by_id, add_category_to_api,
                                                 delete_category, update_category_in_api, get_price_by_category_id)
from app.calendar import RussianSimpleCalendar
from app.handlers.handlers import AllUsersStates, EditStudentFromAdminStates, \
    EditInstructorFromAdminStates, EditTeacherFromAdminStates, AllCoursesStates, UpdateCourseStates, AddCourseStates, \
    AllCategoryStates, AddCategoryStates, UpdateCategoryStates, AddUserStates, AllSchedulesStates, EditScheduleStates, \
    AllCarsStates, EditCarStates, AddScheduleStates, AddCarStates, EditAdminStates, AdminLessonStates, \
    AdminAddLessonStates, AdminEditLessonState
from app.handlers.handlers_teacher import MessageManager
from app.keyboards.keyboard import inline_admin_lessons_by_course
from app.utils.jsons_creator import UserStorage
from config_local import profile_photos, lessons_videos
import app.keyboards.static_keyboard as static_kb
import app.keyboards.keyboard as kb

admin_router = Router()

storage = UserStorage()

JSON_DATA_DIR = "data/json/"


@admin_router.callback_query(F.data == "admin_info")
async def admin_info(callback: CallbackQuery):
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
        f"▫️ <b>Отчество:</b> {user.get('patronym', '')}"
    )
    image = user.get('image')

    if user.get('image') != '' or user.get('image') is not None:
        try:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{image}"),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.admin_info
                )
                return
            except Exception as url_error:
                print(f"URL send failed, trying FSInputFile: {url_error}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.admin_info
                )
                return
        except Exception as e:
            print(f"Both photo sending methods failed: {e}")

    await callback.message.answer(
        info_text,
        parse_mode='HTML',
        reply_markup=static_kb.admin_info
    )


async def handle_back_to_admin_menu(message: Message, user_id):
    user = get_user_by_id(storage.get_user_credentials(user_id).db_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.get('surname', '')} {user.get('name', '')}, Ваша роль Админ',
        reply_markup=static_kb.admin_main
    )


@admin_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
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
        reply_markup=static_kb.admin_main
    )


@admin_router.callback_query(F.data == "update_admin_info")
async def start_updating_admin_info(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    telegram_user_id = callback.from_user.id
    user_credentials = storage.get_user_credentials(telegram_user_id)

    if not user_credentials:
        msg = await callback.message.answer("Ошибка: данные пользователя не найдены")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        return

    user_data = get_user_by_id(user_credentials.db_id)
    if not user_data:
        msg = await callback.message.answer("Ошибка: не удалось получить данные пользователя")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        return

    admin_dict = {
        'id': user_credentials.db_id,
        'surname': user_data.get('surname'),
        'name': user_data.get('name'),
        'patronymic': user_data.get('patronym')
    }

    await state.update_data(
        original_admin=admin_dict,
        current_admin=admin_dict.copy()
    )
    await show_admin_info_edit_options(callback, state)
    await state.set_state(EditAdminStates.waiting_for_choose)


async def show_admin_info_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    admin = data['current_admin']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Фамилия: {admin.get('surname')}", callback_data="edit_admin_info_surname")
    keyboard.button(text=f"Имя: {admin.get('name')}", callback_data="edit_admin_info_name")
    keyboard.button(text=f"Отчество: {admin.get('patronymic')}", callback_data="edit_admin_info_patronymic")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_admin_info_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_admin_info_edit")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в ваших данных? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в ваших данных? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            logging.warning(f"Ошибка при редактировании сообщения: {e}")
            if isinstance(update, CallbackQuery):
                await update.message.answer(
                    "Что вы хотите изменить в ваших данных? (нажмите на пункт для редактирования)",
                    reply_markup=keyboard.as_markup()
                )
            else:
                await update.answer(
                    "Что вы хотите изменить в ваших данных? (нажмите на пункт для редактирования)",
                    reply_markup=keyboard.as_markup()
                )


@admin_router.callback_query(
    EditAdminStates.waiting_for_choose,
    F.data.startswith("edit_admin_info_")
)
async def process_admin_info_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[3]
    await MessageManager.safe_delete(callback.message)

    if choice == "surname":
        msg = await callback.message.answer(
            "Введите новую фамилию или отправьте '-' чтобы оставить текущую:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditAdminStates.waiting_for_surname)

    elif choice == "name":
        msg = await callback.message.answer(
            "Введите новое имя или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditAdminStates.waiting_for_name)

    elif choice == "patronymic":
        msg = await callback.message.answer(
            "Введите новое отчество или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditAdminStates.waiting_for_patronymic)

    await callback.answer()


@admin_router.message(EditAdminStates.waiting_for_surname)
@admin_router.message(EditAdminStates.waiting_for_name)
@admin_router.message(EditAdminStates.waiting_for_patronymic)
async def process_admin_info_field(message: Message, state: FSMContext):
    current_state = await state.get_state()
    field_map = {
        EditAdminStates.waiting_for_surname: 'surname',
        EditAdminStates.waiting_for_name: 'name',
        EditAdminStates.waiting_for_patronymic: 'patronymic'
    }
    field = field_map[current_state]

    data = await state.get_data()
    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    await MessageManager.safe_delete(message)

    if message.text != '-':
        data = await state.get_data()
        data['current_admin'][field] = message.text
        await state.update_data(current_admin=data['current_admin'])

    await show_admin_info_edit_options(message, state)


@admin_router.callback_query(F.data == "finish_admin_info_editing")
async def finalize_admin_info_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_admin']
    updated = data['current_admin']

    changes = {}
    for key in ['surname', 'name', 'patronymic']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    if changes:
        telegram_user_id = callback.from_user.id
        credentials = storage.get_user_credentials(telegram_user_id)

        update_result = update_user_data(
            user_id=original['id'],
            surname=updated.get('surname'),
            name=updated.get('name'),
            patronymic=updated.get('patronymic'),
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            if storage.update_user_from_api(telegram_user_id):
                msg = await callback.message.answer("✅ Данные успешно обновлены!")
            else:
                msg = await callback.message.answer(
                    "✅ Данные обновлены в системе, но возникла проблема с локальным хранилищем")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении данных")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_admin_info_edit")
async def cancel_admin_info_edit(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Редактирование данных отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "users_list")
async def get_user_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все пользователи которые есть в системе:",
                                  reply_markup=await kb.all_users_list())

    await state.set_state(AllUsersStates.waiting_for_id)


@admin_router.callback_query(AllUsersStates.waiting_for_id)
async def handle_user_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_user":
        await start_adding_user(callback, state)
    elif callback.data.startswith('send_pass'):
        await send_password_for_user(callback, state)
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        user_id = callback.data

        user = get_user_by_id(user_id=int(user_id))

        if "ROLE_STUDENT" in user['roles']:
            category_title = 'Не указано'
            if user.get('category'):
                category_title = user['category'].get('title', 'Не указано')

            await callback.message.answer(
                text=f"<b>ID: {user['id']}</b>\n\n"
                     f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                     f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                     f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                     f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                     f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n"
                     f"<b>Категория:</b> {category_title}\n\n"
                     f"<b>Одобрен?:</b> {user.get('is_approved')}\n\n"
                     f"<b>Активен?:</b> {user.get('is_active')}\n\n",
                parse_mode="HTML",
                reply_markup=await kb.inline_user_action(user['id'], user.get('is_approved'), user['roles'])
            )
        elif "ROLE_INSTRUCTOR" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n"
                                               f"<b>Одобрен?:</b> {user.get('is_approved')}\n\n"
                                               f"<b>Активен?:</b> {user.get('is_active')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user.get('is_approved'),
                                                                                   user['roles']))
        elif "ROLE_TEACHER" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n"
                                               f"<b>Одобрен?:</b> {user.get('is_approved')}\n\n"
                                               f"<b>Активен?:</b> {user.get('is_active')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user.get('is_approved'),
                                                                                   user['roles']))
        elif "ROLE_ADMIN" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n"
                                               f"<b>Одобрен?:</b> {user.get('is_approved')}\n\n"
                                               f"<b>Активен?:</b> {user.get('is_active')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user.get('is_approved'),
                                                                                   user['roles']))

        await state.clear()


@admin_router.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = int(callback.data.split('_')[1])
    credentials = storage.get_user_credentials(callback.from_user.id)

    result = approve_user_in_api(user_id, credentials.email, credentials.password)

    if result == 200:
        msg = await callback.message.answer(text="✅ Пользователь одобрен")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_admin_menu(callback, state)
    else:
        msg = await callback.message.answer(text="❌ Пользователь не одобрен")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith('send_pass_'))
async def send_password_for_user(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = int(callback.data.split('_')[2])
    credentials = storage.get_user_credentials(callback.from_user.id)
    result = send_password_for_user_in_api(user_id, credentials.email, credentials.password)

    if result == 200:
        msg = await callback.message.answer(text="✅ Пароль отправлен")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_admin_menu(callback, state)
    else:
        msg = await callback.message.answer(text="❌ Пароль не отправлен")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_user")
async def start_adding_user(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите роль нового пользователя:",
        reply_markup=kb.get_user_roles_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_role)


@admin_router.callback_query(AddUserStates.waiting_for_role, F.data.startswith("ROLE_"))
async def process_role_selection(callback: CallbackQuery, state: FSMContext):
    role = callback.data

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(role=role)

    new_msg = await callback.message.answer(
        "Введите фамилию нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_surname)


@admin_router.message(AddUserStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Введите имя нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_name)


@admin_router.message(AddUserStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(name=message.text)

    new_msg = await message.answer(
        "Введите отчество нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_patronymic)


@admin_router.message(AddUserStates.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(patronymic=message.text)

    new_msg = await message.answer(
        "Введите email нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_email)


@admin_router.message(AddUserStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if not validate_email(message.text):
        error_msg = await message.answer("Некорректный email. Пожалуйста, введите правильный email:")
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(email=message.text)

    new_msg = await message.answer(
        "Введите пароль для нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_password)


@admin_router.message(AddUserStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 6:
        error_msg = await message.answer("Пароль должен содержать минимум 6 символов. Введите пароль снова:")
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(password=message.text)

    data = await state.get_data()
    role_display = {
        "STUDENT": "Студент",
        "INSTRUCTOR": "Инструктор",
        "TEACHER": "Учитель"
    }.get(data['role'], data['role'])

    confirm_text = (
        "Проверьте данные нового пользователя:\n\n"
        f"Роль: {role_display}\n"
        f"ФИО: {data.get('surname')} {data.get('name')} {data.get('patronymic')}\n"
        f"Email: {data.get('email')}\n"
        f"Пароль: {'*' * len(data.get('password', ''))}\n\n"
        "Всё верно?"
    )

    new_msg = await message.answer(
        confirm_text,
        reply_markup=static_kb.confirm_user_addition
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.confirmation)


@admin_router.callback_query(AddUserStates.confirmation, F.data == "confirm_user_addition")
async def finalize_user_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    admin_id = callback.from_user.id
    admin_email = storage.get_user_credentials(admin_id).email
    admin_password = storage.get_user_credentials(admin_id).password

    result = add_user_by_admin(
        role=data['role'],
        surname=data['surname'],
        name=data['name'],
        patronymic=data['patronymic'],
        email=data['email'],
        password=data['password'],
        admin_email=admin_email,
        admin_password=admin_password
    )

    if result == 201:
        success_msg = await callback.message.answer("Пользователь успешно добавлен!")
        await asyncio.sleep(2)
        try:
            await success_msg.delete()
        except TelegramBadRequest:
            pass
    else:
        error_msg = await callback.message.answer("Ошибка при добавлении пользователя!")
        await asyncio.sleep(2)
        try:
            await error_msg.delete()
        except TelegramBadRequest:
            pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(AddUserStates.confirmation, F.data == "cancel_user_addition")
async def cancel_user_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cancel_msg = await callback.message.answer("Добавление пользователя отменено")
    await asyncio.sleep(2)
    try:
        await cancel_msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


async def delete_previous_messages(message: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot = message.bot if isinstance(message, Message) else message.message.bot
    chat_id = message.chat.id if isinstance(message, Message) else message.message.chat.id

    for msg_type in ['last_bot_msg', 'last_keyboard_msg']:
        msg_id = data.get(msg_type)
        if msg_id is not None:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except TelegramBadRequest as e:
                if "message to delete not found" not in str(e):
                    print(f"Error deleting {msg_type}: {e}")

    prev_msgs = data.get('prev_msgs', [])
    if prev_msgs:
        for msg_id in prev_msgs:
            if msg_id is not None:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except TelegramBadRequest as e:
                    if "message to delete not found" not in str(e):
                        print(f"Error deleting prev_msg {msg_id}: {e}")

    if isinstance(message, Message):
        try:
            await message.delete()
        except TelegramBadRequest as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting current message: {e}")

    await state.update_data({
        'last_bot_msg': None,
        'last_keyboard_msg': None,
        'prev_msgs': []
    })


@admin_router.callback_query(F.data.startswith("update_user"))
async def start_editing(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите новую фамилию ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    user_id = int(callback.data.split('-')[0][12:])
    user_role = callback.data.split('-')[1]

    if user_role == "ROLE_STUDENT":
        await state.set_state(EditStudentFromAdminStates.waiting_for_surname)
    if user_role == "ROLE_INSTRUCTOR":
        await state.set_state(EditInstructorFromAdminStates.waiting_for_surname)
    if user_role == "ROLE_TEACHER":
        await state.set_state(EditTeacherFromAdminStates.waiting_for_surname)

    await state.update_data(last_bot_msg=new_msg.message_id,
                            user_id=user_id)


@admin_router.message(EditStudentFromAdminStates.waiting_for_surname)
async def process_student_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentFromAdminStates.waiting_for_name)


@admin_router.message(EditStudentFromAdminStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditStudentFromAdminStates.waiting_for_patronymic)
async def process_student_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user_credentials(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user_credentials(telegram_user_id).db_id
    user_pass = storage.get_user_credentials(telegram_user_id).password
    user_email = storage.get_user_credentials(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


@admin_router.message(EditInstructorFromAdminStates.waiting_for_surname)
async def process_instructor_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditInstructorFromAdminStates.waiting_for_name)


@admin_router.message(EditInstructorFromAdminStates.waiting_for_name)
async def process_instructor_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditInstructorFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditInstructorFromAdminStates.waiting_for_patronymic)
async def process_instructor_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user_credentials(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user_credentials(telegram_user_id).db_id
    user_pass = storage.get_user_credentials(telegram_user_id).password
    user_email = storage.get_user_credentials(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    print(update)
    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


@admin_router.message(EditTeacherFromAdminStates.waiting_for_surname)
async def process_teacher_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditTeacherFromAdminStates.waiting_for_name)


@admin_router.message(EditTeacherFromAdminStates.waiting_for_name)
async def process_teacher_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditTeacherFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditTeacherFromAdminStates.waiting_for_patronymic)
async def process_teacher_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user_credentials(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user_credentials(telegram_user_id).db_id
    user_pass = storage.get_user_credentials(telegram_user_id).password
    user_email = storage.get_user_credentials(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


@admin_router.callback_query(F.data == "cancel_admin_edit")
async def get_cancel_admin_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            logging.debug("Сообщение для удаления не найдено (last_bot_msg)")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        logging.debug("Сообщение для удаления не найдено (callback.message)")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    cancel_msg = await callback.message.answer("Редактирование отменено")

    try:
        await cancel_msg.delete()
    except TelegramBadRequest:
        logging.debug("Не удалось удалить сообщение об отмене")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения об отмене: {e}")

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("delete_user_"))
async def start_delete(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = int(callback.data.split('_')[2])

    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    delete_result = delete_user(user_id, email, password)

    if delete_result == 204:
        await callback.message.answer(text=f"Пользователь {user_id} успешно удален")
        await asyncio.sleep(2)
        await get_user_list(callback, state)
    else:
        await callback.message.answer(text="Ошибка удаления пользователя")
        await asyncio.sleep(2)
        await get_user_list(callback, state)


@admin_router.callback_query(F.data == "courses_list")
async def get_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот список всех курсов ⬇️",
                                  reply_markup=await kb.inline_admin_courses())

    await state.set_state(AllCoursesStates.waiting_for_id)


@admin_router.callback_query(AllCoursesStates.waiting_for_id)
async def admin_course_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_course":
        await start_adding_course(callback, state)
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        course_id = int(callback.data)
        course = get_course_by_id(course_id=course_id)

        if not course:
            await callback.message.answer("🚫 Курс не найден")
            return

        await callback.message.answer(text=f"<b>ID: {course.id}</b>\n\n"
                                           f"<b>Название:</b> {course.title}\n\n"
                                           f"<b>Описание:</b> {course.description or "Нет описания"}\n\n"
                                           f"<b>Занятия и тесты на курсе:</b>\n\n",
                                      parse_mode="HTML",
                                      reply_markup=await inline_admin_lessons_by_course(course_id))

        await state.set_state(AllCoursesStates.waiting_for_lesson_id)


@admin_router.callback_query(F.data.startswith("delete_course_"))
async def delete_admin_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = int(callback.data.split('_')[2])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    delete_result = delete_course(course_id=course_id, email=email, password=password)

    if delete_result == 204:
        result = await callback.message.answer(text=f"Курс {course_id} успешно удален")
        await asyncio.sleep(2)
        await result.delete()
        await get_courses_list(callback, state)
    else:
        result = await callback.message.answer(text="Ошибка удаления курса")
        await asyncio.sleep(2)
        await result.delete()
        await get_courses_list(callback, state)


@admin_router.callback_query(F.data.startswith("update_course_"))
async def start_updating_admin_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = int(callback.data.split('_')[2])
    course_data = get_course_by_id(course_id)

    if not course_data:
        await callback.message.answer("Курс не найден")
        return

    course_dict = {
        'id': course_data.id,
        'title': course_data.title,
        'description': course_data.description,
        'category_id': course_data.category.get('id') if course_data.category else None,
        'lessons': [lesson.get('id') for lesson in course_data.lessons],
        'users': [user.get('id') for user in course_data.users],
        'quizzes': [quiz.get('id') for quiz in course_data.quizzes]
    }
    print(course_dict)

    await state.update_data(
        original_course=course_dict,
        current_course=course_dict.copy()
    )
    await show_admin_course_edit_options(callback, state)
    await state.set_state(UpdateCourseStates.waiting_for_choose)


async def show_admin_course_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course = data['current_course']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Название: {course.get('title')}",
                    callback_data="edit_course_admin_title")
    keyboard.button(text=f"Описание: {course.get('description')[:30]}...",
                    callback_data="edit_course_admin_description")
    keyboard.button(text=f"Категория: {course.get('category_id')}",
                    callback_data="edit_course_admin_category")
    keyboard.button(text="Уроки", callback_data="edit_course_admin_lessons")
    keyboard.button(text="Пользователи", callback_data="edit_course_admin_users")
    keyboard.button(text="Тесты", callback_data="edit_course_admin_quizzes")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_course_editing_admin")
    keyboard.button(text="❌ Отменить", callback_data="cancel_course_update")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(UpdateCourseStates.waiting_for_choose)


@admin_router.callback_query(
    UpdateCourseStates.waiting_for_choose,
    F.data.startswith("edit_course_admin_")
)
async def process_admin_course_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[3]
    print(choice)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if choice == "title":
        msg = await callback.message.answer(
            "Введите новое название курса или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_title)

    elif choice == "description":
        msg = await callback.message.answer(
            "Введите новое описание курса или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_description)

    elif choice == "category":
        msg = await callback.message.answer(
            "Выберите новую категорию курса:",
            reply_markup=await kb.inline_course_categories()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_category)

    elif choice == "lessons":
        msg = await callback.message.answer(
            "Выберите уроки для курса:",
            reply_markup=await kb.inline_course_lessons()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_lessons)

    elif choice == "users":
        data = await state.get_data()
        current_users = data['current_course'].get('users', [])

        msg = await callback.message.answer(
            "Выберите пользователей для курса:",
            reply_markup=await kb.inline_course_users(current_users)
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_users)

    elif choice == "quizzes":
        msg = await callback.message.answer(
            "Выберите тесты для курса:",
            reply_markup=await kb.inline_course_quizzes()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_quizzes)

    await callback.answer()


@admin_router.message(UpdateCourseStates.waiting_for_title)
async def process_admin_edit_course_title(message: Message, state: FSMContext):

    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_course']['title'] = message.text
        await state.update_data(current_course=data['current_course'])

    await MessageManager.safe_delete(message)

    await show_admin_course_edit_options(message, state)


@admin_router.message(UpdateCourseStates.waiting_for_description)
async def process_admin_edit_course_description(message: Message, state: FSMContext):

    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_course']['description'] = message.text
        await state.update_data(current_course=data['current_course'])

    await MessageManager.safe_delete(message)

    await show_admin_course_edit_options(message, state)


@admin_router.callback_query(UpdateCourseStates.waiting_for_category, F.data.startswith("category_"))
async def process_admin_edit_course_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    data = await state.get_data()
    data['current_course']['category_id'] = category_id
    await state.update_data(current_course=data['current_course'])

    await callback.message.delete()
    await show_admin_course_edit_options(callback, state)


@admin_router.callback_query(UpdateCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def process_admin_edit_course_lessons(callback: CallbackQuery, state: FSMContext):
    try:
        lesson_id = int(callback.data.split('_')[1])
        data = await state.get_data()

        # Гарантируем, что lessons будет списком
        current_lessons = list(data['current_course'].get('lessons', []))

        # Преобразуем все элементы в int на случай если пришли строки
        current_lessons = [int(x) for x in current_lessons if str(x).isdigit()]

        if lesson_id in current_lessons:
            current_lessons.remove(lesson_id)
        else:
            current_lessons.append(lesson_id)

        data['current_course']['lessons'] = current_lessons
        await state.update_data(current_course=data['current_course'])
        await callback.answer(f"Урок {'добавлен' if lesson_id in current_lessons else 'удалён'}")
    except Exception as e:
        print(f"Error in process_admin_edit_course_lessons: {e}")
        await callback.answer("Ошибка при изменении уроков", show_alert=True)


@admin_router.callback_query(UpdateCourseStates.waiting_for_lessons, F.data == "continue")
async def finish_admin_edit_course_lessons(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_admin_course_edit_options(callback, state)


@admin_router.callback_query(UpdateCourseStates.waiting_for_users, F.data.startswith("user_"))
async def process_admin_edit_course_users(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = int(callback.data.split('_')[1])
        data = await state.get_data()

        # Гарантируем, что users будет списком
        current_users = list(data['current_course'].get('users', []))

        # Преобразуем все элементы в int
        current_users = [int(x) for x in current_users if str(x).isdigit()]

        if user_id in current_users:
            current_users.remove(user_id)
        else:
            current_users.append(user_id)

        data['current_course']['users'] = current_users
        await state.update_data(current_course=data['current_course'])
        await callback.answer(f"Пользователь {'добавлен' if user_id in current_users else 'удалён'}")
    except Exception as e:
        print(f"Error in process_admin_edit_course_users: {e}")
        await callback.answer("Ошибка при изменении пользователей", show_alert=True)


@admin_router.callback_query(UpdateCourseStates.waiting_for_users, F.data == "continue")
async def finish_admin_edit_course_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_admin_course_edit_options(callback, state)


@admin_router.callback_query(UpdateCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def process_admin_edit_course_quizzes(callback: CallbackQuery, state: FSMContext):
    try:
        quiz_id = int(callback.data.split('_')[1])
        data = await state.get_data()

        current_quizzes = list(data['current_course'].get('quizzes', []))

        current_quizzes = [int(x) for x in current_quizzes if str(x).isdigit()]

        if quiz_id in current_quizzes:
            current_quizzes.remove(quiz_id)
        else:
            current_quizzes.append(quiz_id)

        data['current_course']['quizzes'] = current_quizzes
        await state.update_data(current_course=data['current_course'])
        await callback.answer(f"Тест {'добавлен' if quiz_id in current_quizzes else 'удалён'}")
    except Exception as e:
        print(f"Error in process_admin_edit_course_quizzes: {e}")
        await callback.answer("Ошибка при изменении тестов", show_alert=True)


@admin_router.callback_query(UpdateCourseStates.waiting_for_quizzes, F.data == "continue")
async def finish_admin_edit_course_quizzes(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_admin_course_edit_options(callback, state)


@admin_router.callback_query(F.data == "finish_course_editing_admin")
async def finalize_admin_course_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_course']
    updated = data['current_course']

    changes = {}
    for key in ['title', 'description', 'category_id']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    for key in ['lessons', 'users', 'quizzes']:
        original_list = sorted(original.get(key, []))
        updated_list = sorted(updated.get(key, []))
        if original_list != updated_list:
            changes[key] = updated.get(key)

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        update_result = update_course_in_api(
            course_id=changes['id'],
            title=changes.get('title', original['title']),
            description=changes.get('description', original['description']),
            lessons=changes.get('lessons', original['lessons']),
            users=changes.get('users', original['users']),
            category=changes.get('category_id', original['category_id']),
            quizzes=changes.get('quizzes', original['quizzes']),
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            msg = await callback.message.answer("✅ Курс успешно обновлен!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении курса")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_course_update")
async def cancel_course_update(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Обновление курса отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_course")
async def start_adding_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите название нового курса ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(
        last_bot_msg=new_msg.message_id,
        selected_lessons=[],
        selected_users=[],
        selected_quizzes=[]
    )
    await state.set_state(AddCourseStates.waiting_for_title)


@admin_router.message(AddCourseStates.waiting_for_title)
async def process_course_title_admin(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(title=message.text)
    new_msg = await message.answer(
        "Введите описание нового курса ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_description)


@admin_router.message(AddCourseStates.waiting_for_description)
async def process_course_description_admin(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)
    await state.update_data(description=message.text)

    new_msg = await message.answer(
        "Выберите уроки для нового курса ⬇️",
        reply_markup=await kb.inline_course_lessons()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_lessons)


@admin_router.callback_query(AddCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def select_lessons_admin(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_lessons = data.get('selected_lessons', [])

    if lesson_id in selected_lessons:
        selected_lessons.remove(lesson_id)
    else:
        selected_lessons.append(lesson_id)

    await state.update_data(selected_lessons=selected_lessons)
    await callback.answer(f"Урок {'добавлен' if lesson_id in selected_lessons else 'удален'}")


@admin_router.callback_query(AddCourseStates.waiting_for_lessons, F.data == "continue")
async def process_lessons_selection_admin(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите пользователей для нового курса ⬇️",
        reply_markup=await kb.inline_course_users([])
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_users)


@admin_router.callback_query(AddCourseStates.waiting_for_users, F.data.startswith("user_"))
async def select_users_admin(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_users = data.get('selected_users', [])

    if user_id in selected_users:
        selected_users.remove(user_id)
    else:
        selected_users.append(user_id)

    await state.update_data(selected_users=selected_users)
    await callback.answer(f"Пользователь {'добавлен' if user_id in selected_users else 'удален'}")


@admin_router.callback_query(AddCourseStates.waiting_for_users, F.data == "continue")
async def process_users_selection_admin(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите категорию для нового курса ⬇️",
        reply_markup=await kb.inline_course_categories()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_category)


@admin_router.callback_query(AddCourseStates.waiting_for_category, F.data.startswith("category_"))
async def select_category_admin(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(category_id=category_id)

    new_msg = await callback.message.answer(
        "Выберите тесты для нового курса ⬇️",
        reply_markup=await kb.inline_course_quizzes()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_quizzes)


@admin_router.callback_query(AddCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def select_quizzes_admin(callback: CallbackQuery, state: FSMContext):
    quiz_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_quizzes = data.get('selected_quizzes', [])

    if quiz_id in selected_quizzes:
        selected_quizzes.remove(quiz_id)
    else:
        selected_quizzes.append(quiz_id)

    await state.update_data(selected_quizzes=selected_quizzes)
    await callback.answer(f"Тест {'добавлен' if quiz_id in selected_quizzes else 'удален'}")


@admin_router.callback_query(AddCourseStates.waiting_for_quizzes, F.data == "continue")
async def confirm_course_addition_admin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    message_text = (
            "Проверьте данные нового курса:\n\n"
            f"Название: {data.get('title')}\n"
            f"Описание: {data.get('description')}\n"
            f"Цена: {data.get('price')} ₽ \n\n"
            "Выбранные уроки:\n" + "\n".join([get_lesson_title(lesson_id) for lesson_id in data.get('selected_lessons',
                                                                                                    [])]) + "\n\n"
            "Выбранные пользователи:\n" + "\n".join([get_user_name(user_id) for user_id in data.get('selected_users',
                                                                                                    [])]) + "\n\n"
            "Выбранные тесты:\n" + "\n".join([get_quiz_title(quiz_id) for quiz_id in data.get('selected_quizzes', [])])
    )

    await callback.message.answer(
        message_text,
        reply_markup=static_kb.confirm_course_addition
    )
    await state.set_state(AddCourseStates.confirmation)


@admin_router.callback_query(AddCourseStates.confirmation, F.data == "confirm_course_addition")
async def finalize_course_addition_admin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    add_result = add_course_to_api(
        title=data['title'],
        description=data['description'],
        lessons=data.get('selected_lessons', []),
        users=data.get('selected_users', []),
        category=data.get('category_id'),
        quizzes=data.get('selected_quizzes', []),
        email=email,
        password=password
    )

    if add_result == 201:
        result = await callback.message.answer("Новый курс успешно добавлен!")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)
    else:
        result = await callback.message.answer("Ошибка при добавлении курса")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)

    await state.clear()


@admin_router.callback_query(AddCourseStates.confirmation, F.data == "cancel_course_add")
async def cancel_course_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    result = await callback.message.answer("Добавление курса отменено")
    await asyncio.sleep(2)
    await result.delete()
    await back_to_admin_menu(callback, state)
    await state.clear()


@admin_router.callback_query(F.data == "category_list")
async def get_category_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот какие категории есть в системе:",
                                  reply_markup=await kb.inline_admin_category())

    await state.set_state(AllCategoryStates.waiting_for_id)


@admin_router.callback_query(AllCategoryStates.waiting_for_id, F.data.startswith("admin_category_"))
async def handle_get_admin_category_by_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    category = get_admin_category_by_id(category_id)

    if not category:
        await callback.message.answer(text="Нет категорий",
                                      reply_markup=static_kb.add_category)

    await callback.message.answer(text=f"Категория {category.id}\n\n"
                                  f"<b>Название:</b> {category.title}\n"
                                  f"<b>Краткое название:</b> {category.master_title}\n"
                                  f"<b>Описание:</b> {category.description}\n"
                                  f"<b>Цена:</b> {category.price} ₽ \n"
                                  f"<b>Тип:</b> {category.type}\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.category_action(category_id))

    await state.clear()


@admin_router.callback_query(F.data == "add_category")
async def start_adding_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите название новой категории:",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_title)


@admin_router.message(AddCategoryStates.waiting_for_title)
async def process_category_title(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 3:
        error_msg = await message.answer(
            "Название должно содержать минимум 3 символа. Попробуйте снова:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(title=message.text)

    new_msg = await message.answer(
        "Введите короткое название категории (для отображения в интерфейсе):",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_master_title)


@admin_router.message(AddCategoryStates.waiting_for_master_title)
async def process_category_master_title(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) > 2:
        error_msg = await message.answer(
            "Короткое название должно содержать 1 символ. Попробуйте снова:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(masterTitle=message.text)

    new_msg = await message.answer(
        "Введите описание категории:",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_description)


@admin_router.message(AddCategoryStates.waiting_for_description)
async def process_category_description(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 10:
        error_msg = await message.answer(
            "Описание должно содержать минимум 10 символов. Попробуйте снова:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(description=message.text)

    new_msg = await message.answer(
        "Введите цену категории (только цифры):",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_price)


@admin_router.message(AddCategoryStates.waiting_for_price)
async def process_category_price(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        error_msg = await message.answer(
            "Цена должна быть положительным числом. Попробуйте снова:",
            reply_markup=await kb.get_cancel_admin_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(price=price)

    new_msg = await message.answer(
        "Выберите тип категории:",
        reply_markup=await kb.get_category_types()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_type)


@admin_router.callback_query(AddCategoryStates.waiting_for_type, F.data.startswith("type_"))
async def process_category_type(callback: CallbackQuery, state: FSMContext):
    category_type = callback.data.split("_")[1]
    await state.update_data(type=category_type)

    data = await state.get_data()

    confirm_text = (
        "Проверьте данные категории:\n\n"
        f"🏷️ Название: {data['title']}\n"
        f"📌 Короткое название: {data['masterTitle']}\n"
        f"📝 Описание: {data['description']}\n"
        f"💰 Цена: {data['price']} ₽\n"
        f"🔧 Тип: {data['type']}\n\n"
        "Всё верно?"
    )

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        confirm_text,
        reply_markup=await kb.confirm_category_addition_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCategoryStates.confirmation)


@admin_router.callback_query(AddCategoryStates.confirmation, F.data == "confirm_category_addition")
async def finalize_category_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    credentials = storage.get_user_credentials(callback.from_user.id)

    category_data = {
        "title": data['title'],
        "masterTitle": data['masterTitle'],
        "description": data['description'],
        "price": data['price'],
        "type": data['type']
    }

    result = add_category_to_api(
        category_data=category_data,
        email=credentials.email,
        password=credentials.password
    )

    if result == 201:
        msg = await callback.message.answer("✅ Категория успешно добавлена!")
    else:
        msg = await callback.message.answer("❌ Ошибка при добавлении категории")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_category_addition")
async def cancel_category_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Добавление категории отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("delete_category_"))
async def start_delete_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    result = delete_category(category_id, email, password)

    if result == 204:
        result = await callback.message.answer(text="Категория удалена")
        await asyncio.sleep(2)
        await result.delete()
        await get_category_list(callback, state)
    else:
        result = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result.delete()
        await get_category_list(callback, state)


@admin_router.callback_query(F.data.startswith("update_category_"))
async def start_updating_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    category = get_category_by_id(category_id)

    if not category:
        await callback.message.answer("Категория не найдена")
        return

    category_dict = {
        'id': category_id,
        'title': category.title,
        'masterTitle': category.master_title,
        'description': category.description,
        'price': category.price,
        'type': category.type
    }

    await state.update_data(
        original_category=category_dict,
        current_category=category_dict.copy()
    )
    await show_category_edit_options(callback, state)
    await state.set_state(UpdateCategoryStates.waiting_for_choose)


async def show_category_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['current_category']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Название: {category.get('title')}", callback_data="edit_category_title")
    keyboard.button(text=f"Короткое название: {category.get('masterTitle')}", callback_data="edit_category_masterTitle")
    keyboard.button(text=f"Описание: {category.get('description')}", callback_data="edit_category_description")
    keyboard.button(text=f"Цена: {category.get('price')}", callback_data="edit_category_price")
    keyboard.button(text=f"Тип: {category.get('type')}", callback_data="edit_category_type")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_category_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_category_edit")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в категории? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в категории? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в категории? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в категории? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(UpdateCategoryStates.waiting_for_choose)


@admin_router.callback_query(
    UpdateCategoryStates.waiting_for_choose,
    F.data.startswith("edit_category_")
)
async def process_category_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[2]

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if choice == "title":
        msg = await callback.message.answer(
            "Введите новое название категории или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_category_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCategoryStates.waiting_for_title)

    elif choice == "masterTitle":
        msg = await callback.message.answer(
            "Введите новое короткое название категории или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_category_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCategoryStates.waiting_for_masterTitle)

    elif choice == "description":
        msg = await callback.message.answer(
            "Введите новое описание категории или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_category_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCategoryStates.waiting_for_description)

    elif choice == "price":
        msg = await callback.message.answer(
            "Введите новую цену категории или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_category_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCategoryStates.waiting_for_price)

    elif choice == "type":
        msg = await callback.message.answer(
            "Введите новый тип категории или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_category_types()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(UpdateCategoryStates.waiting_for_type)

    await callback.answer()


@admin_router.message(UpdateCategoryStates.waiting_for_title)
async def process_edit_category_title(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_category']['title'] = message.text
        await state.update_data(current_category=data['current_category'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_category_edit_options(message, state)


@admin_router.message(UpdateCategoryStates.waiting_for_masterTitle)
async def process_edit_category_master_title(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_category']['masterTitle'] = message.text
        await state.update_data(current_category=data['current_category'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_category_edit_options(message, state)


@admin_router.message(UpdateCategoryStates.waiting_for_description)
async def process_edit_category_description(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_category']['description'] = message.text
        await state.update_data(current_category=data['current_category'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_category_edit_options(message, state)


@admin_router.message(UpdateCategoryStates.waiting_for_price)
async def process_edit_category_price(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_category']['price'] = message.text
        await state.update_data(current_category=data['current_category'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_category_edit_options(message, state)


@admin_router.callback_query(UpdateCategoryStates.waiting_for_type, F.data.startswith("type_"))
async def process_edit_category_type(callback: CallbackQuery, state: FSMContext):
    category_type = callback.data.split("_")[1]
    data = await state.get_data()

    data['current_category']['type'] = category_type
    await state.update_data(current_category=data['current_category'])

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await show_category_edit_options(callback, state)
    await callback.answer(f"Тип изменён на {category_type}")


@admin_router.callback_query(F.data == "finish_category_editing")
async def finalize_category_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_category']
    updated = data['current_category']

    changes = {}
    for key in ['title', 'masterTitle', 'description', 'price', 'type']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        category_data = {
            "title": updated.get('title'),
            "masterTitle": updated.get('masterTitle'),
            "description": updated.get('description'),
            "price": int(updated.get('price')),
            "type": updated.get('type')
        }

        result = update_category_in_api(
            category_id=changes['id'],
            data=category_data,
            email=credentials.email,
            password=credentials.password
        )

        if result == 200:
            msg = await callback.message.answer("✅ Категория успешно обновлена!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении категории")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_category_edit")
async def cancel_category_edit(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Редактирование категории отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "schedules_list")
async def get_schedule_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все расписания в системе ⬇️",
                                  reply_markup=await kb.inline_admin_schedules())

    await state.set_state(AllSchedulesStates.waiting_for_id)


@admin_router.callback_query(AllSchedulesStates.waiting_for_id)
async def get_admin_schedule_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "schedules_list":
        await get_schedule_list(callback, state)
    elif callback.data == "add_schedule":
        await start_adding_schedule(callback, state)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data)
    schedule = get_admin_drive_schedule_by_id(schedule_id)

    if not schedule:
        await callback.message.answer("🕒 Расписание не найдено")
        await state.clear()
        return

    autodrome = get_autodrome_by_id(schedule.autodrome_id)
    category = get_category_by_id(schedule.category_id)
    instructor = get_instructor_by_id(schedule.instructor_id)
    price = get_price_by_category_id(schedule.category_id)
    days = ', '.join(schedule.days_of_week) if isinstance(schedule.days_of_week, list) else schedule.days_of_week

    await callback.message.answer(text=f"📅 Информация о расписании {schedule_id}:\n\n"
                                  f"⏱ Время: {datetime.fromisoformat(schedule.time_from).strftime('%H:%M')} - "
                                  f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}\n\n"
                                  f"📆 Дни: {days}\n\n"
                                  f"🏁 Автодром: {autodrome.title}\n\n"
                                  f"📋 Категория: {category.title}\n\n"
                                  f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
                                  f"💲 Цена: {price} ₽ \n\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.inline_schedule_action(schedule_id))

    await state.clear()


@admin_router.callback_query(F.data.startswith('delete_schedule_'))
async def delete_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[2])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password
    result = delete_schedule_from_api(schedule_id, email, password)

    if result == 204:
        result_msg = await callback.message.answer(text="Удаление успешно")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)
    else:
        result_msg = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("update_schedule_"))
async def start_updating_admin_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[2])
    schedule = get_admin_drive_schedule_by_id(schedule_id)

    if not schedule:
        await callback.message.answer("Расписание не найдено")
        return

    schedule_dict = {
        'id': schedule.id,
        'time_from': schedule.time_from,
        'time_to': schedule.time_to,
        'days_of_week': schedule.days_of_week,
        'notice': schedule.notice,
        'autodrome_id': schedule.autodrome_id,
        'category_id': schedule.category_id,
        'instructor_id': schedule.instructor_id
    }

    await state.update_data(
        original_schedule=schedule_dict,
        current_schedule=schedule_dict.copy()
    )
    await show_admin_schedule_edit_options(callback, state)
    await state.set_state(EditScheduleStates.waiting_for_choose)


async def show_admin_schedule_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    schedule = data['current_schedule']

    autodrome = get_autodrome_by_id(schedule.get('autodrome_id'))
    category = get_category_by_id(schedule.get('category_id'))

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Время начала: {datetime.fromisoformat(schedule.get('time_from')).strftime('%H:%M')}",
                    callback_data="edit_schedule_admin_time_from")
    keyboard.button(text=f"Время окончания: {datetime.fromisoformat(schedule.get('time_to')).strftime('%H:%M')}",
                    callback_data="edit_schedule_admin_time_to")
    keyboard.button(text=f"Дни недели: {schedule.get('days_of_week')}", callback_data="edit_schedule_admin_days")
    keyboard.button(text=f"Примечание: {schedule.get('notice', 'отсутствует')[:20]}...",
                    callback_data="edit_schedule_admin_notice")
    keyboard.button(text=f"Автодром: {autodrome.title if autodrome else 'Не указан'}",
                    callback_data="edit_schedule_admin_autodrome")
    keyboard.button(text=f"Категория: {category.title if category else 'Не указана'}",
                    callback_data="edit_schedule_admin_category")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_schedule_editing_admin")
    keyboard.button(text="❌ Отменить", callback_data="cancel_schedule_edit")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(EditScheduleStates.waiting_for_choose)


@admin_router.callback_query(
    EditScheduleStates.waiting_for_choose,
    F.data.startswith("edit_schedule_admin_")
)
async def process_admin_schedule_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[3:]
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if choice == ['time', 'from']:
        msg = await callback.message.answer(
            "Выберите время начала занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}from")
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_time_from)

    elif choice == ['time', 'to']:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_time_to)

    elif choice == ['days']:
        data = await state.get_data()
        current_days = data['current_schedule'].get('days_of_week', "")
        if isinstance(current_days, str):
            current_days = [d.strip() for d in current_days.split(",")] if current_days else []

        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard(current_days if current_days else [])
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_days)

    elif choice == ["notice"]:
        msg = await callback.message.answer(
            "Введите новое примечание или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_schedule_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_notice)

    elif choice == ["autodrome"]:
        msg = await callback.message.answer(
            "Выберите автодром:",
            reply_markup=await kb.inline_schedule_edit_autodrome()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_autodrome)

    elif choice == ["category"]:
        msg = await callback.message.answer(
            "Выберите категорию:",
            reply_markup=await kb.inline_schedule_edit_category()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditScheduleStates.waiting_for_category)

    await callback.answer()


@admin_router.callback_query(
    EditScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}from_")
)
async def process_admin_time_from(callback: CallbackQuery, state: FSMContext):
    try:
        time_str = callback.data.split('_')[3]
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        data = await state.get_data()

        # Проверяем время окончания, если оно уже установлено
        if 'current_schedule' in data and 'time_to' in data['current_schedule']:
            time_to = datetime.fromisoformat(data['current_schedule']['time_to']).time()
            if time_obj >= time_to:
                await callback.answer("⏰ Время начала должно быть раньше времени окончания!")
                return

        iso_time = datetime.combine(date.today(), time_obj).isoformat()
        if 'current_schedule' not in data:
            data['current_schedule'] = {}

        data['current_schedule']['time_from'] = iso_time
        await state.update_data(current_schedule=data['current_schedule'])

        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        await show_admin_schedule_edit_options(callback, state)
        await callback.answer(f"Установлено время начала: {time_str}")

    except Exception as e:
        print(f"Error in process_admin_time_from: {e}")
        await callback.answer("❌ Ошибка при установке времени")

@admin_router.callback_query(
    EditScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}to_")
)
async def process_admin_time_to(callback: CallbackQuery, state: FSMContext):
    try:
        time_str = callback.data.split('_')[3]
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        data = await state.get_data()

        # Обязательная проверка наличия времени начала
        if 'current_schedule' not in data or 'time_from' not in data['current_schedule']:
            await callback.answer("⚠️ Сначала установите время начала!")
            return

        time_from = datetime.fromisoformat(data['current_schedule']['time_from']).time()

        if time_obj <= time_from:
            await callback.answer("⏰ Время окончания должно быть позже времени начала!")
            return

        iso_time = datetime.combine(date.today(), time_obj).isoformat()
        data['current_schedule']['time_to'] = iso_time
        await state.update_data(current_schedule=data['current_schedule'])

        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        await show_admin_schedule_edit_options(callback, state)
        await callback.answer(f"Установлено время окончания: {time_str}")

    except Exception as e:
        print(f"Error in process_admin_time_to: {e}")
        await callback.answer("❌ Ошибка при установке времени")


@admin_router.callback_query(
    EditScheduleStates.waiting_for_days,
    F.data.startswith(kb.ADMIN_DAY_PREFIX))
async def process_admin_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.ADMIN_DAY_PREFIX, "")
    data = await state.get_data()

    selected_days = data['current_schedule'].get('days_of_week', "")

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

        day_order = {
            'Пн': 0,
            'Вт': 1,
            'Ср': 2,
            'Чт': 3,
            'Пт': 4,
            'Сб': 5,
            'Вс': 6
        }

        selected_days_sorted = sorted(selected_days, key=lambda x: day_order.get(x, 7))
        data['current_schedule']['days_of_week'] = selected_days_sorted
        await state.update_data(current_schedule=data['current_schedule'])
        await callback.answer(f"День {'добавлен' if day in selected_days else 'удален'}")


@admin_router.callback_query(
    EditScheduleStates.waiting_for_days,
    F.data == kb.ADMIN_DONE_PREFIX
)
async def process_admin_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data['current_schedule'].get('days_of_week', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@admin_router.message(EditScheduleStates.waiting_for_notice)
async def process_admin_notice(message: Message, state: FSMContext):

    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    notice = message.text if message.text != '-' else None

    data['current_schedule']['notice'] = notice
    await state.update_data(current_schedule=data['current_schedule'])

    await MessageManager.safe_delete(message)
    await show_admin_schedule_edit_options(message, state)


@admin_router.callback_query(
    EditScheduleStates.waiting_for_autodrome,
    F.data.startswith("autodrome_")
)
async def process_admin_autodrome(callback: CallbackQuery, state: FSMContext):
    autodrome_id = int(callback.data.split('_')[1])

    data = await state.get_data()
    data['current_schedule']['autodrome_id'] = autodrome_id
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@admin_router.callback_query(
    EditScheduleStates.waiting_for_category,
    F.data.startswith("category_")
)
async def process_admin_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    data = await state.get_data()
    data['current_schedule']['category_id'] = category_id
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@admin_router.callback_query(F.data == "finish_schedule_editing_admin")
async def finalize_admin_schedule_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_schedule']
    updated = data['current_schedule']

    changes = {}
    for key in ['time_from', 'time_to', 'days_of_week', 'notice', 'autodrome_id', 'category_id', 'instructor_id']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        schedule_data = {
            "timeFrom": updated.get('time_from'),
            "timeTo": updated.get('time_to'),
            "daysOfWeek": ",".join(updated.get('days_of_week')),
            "notice": updated.get('notice'),
            "autodrome": f"api/autodromes/{updated.get('autodrome_id')}",
            "category": f"api/categories/{updated.get('category_id')}"
        }

        update_result = update_schedule(
            schedule_id=changes['id'],
            json=schedule_data,
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            msg = await callback.message.answer("✅ Расписание успешно обновлено!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении расписания")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")
        await asyncio.sleep(1)
        await MessageManager.safe_delete(msg)

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_schedule_edit")
async def cancel_schedule_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Редактирование расписания отменено")
    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_schedule")
async def start_adding_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(
        selected_days=[],
        notice=None
    )

    msg = await callback.message.answer(
        "Выберите время начала занятия:",
        reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}from")
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_time_from)


@admin_router.callback_query(
    AddScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}from_")
)
async def process_time_from(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()

    await state.update_data(time_from=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddScheduleStates.waiting_for_time_to)


@admin_router.callback_query(
    AddScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}to_")
)
async def process_time_to(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    time_from = datetime.fromisoformat(data['time_from']).time()
    if time_obj <= time_from:
        await callback.answer("Время окончания должно быть позже времени начала!")
        return

    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()
    await state.update_data(time_to=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddScheduleStates.waiting_for_days)


@admin_router.callback_query(
    AddScheduleStates.waiting_for_days,
    F.data.startswith(kb.ADMIN_DAY_PREFIX)
)
async def process_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.ADMIN_DAY_PREFIX, "")
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.get_admin_days_keyboard(selected_days)
    )
    await callback.answer()


@admin_router.callback_query(
    AddScheduleStates.waiting_for_days,
    F.data == kb.ADMIN_DONE_PREFIX
)
async def process_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    days_str = ", ".join(selected_days)
    await state.update_data(days_of_week=days_str)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        "Введите примечание (или отправьте '-' чтобы не добавлять):",
        reply_markup=await kb.get_cancel_schedule_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_notice)


@admin_router.message(AddScheduleStates.waiting_for_notice)
async def process_notice(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    notice = message.text if message.text != '-' else None
    await state.update_data(notice=notice)

    msg = await message.answer(
        "Выберите автодром:",
        reply_markup=await kb.inline_schedule_edit_autodrome()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_autodrome)


@admin_router.callback_query(AddScheduleStates.waiting_for_autodrome, F.data.startswith("autodrome_"))
async def process_autodrome(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    autodrome_id = int(callback.data.split('_')[1])
    await state.update_data(autodrome=f"api/autodromes/{autodrome_id}")

    msg = await callback.message.answer(
        "Выберите категорию:",
        reply_markup=await kb.inline_schedule_edit_category()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_category)


@admin_router.callback_query(AddScheduleStates.waiting_for_category, F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[1])
    await state.update_data(category=f"api/categories/{category_id}")

    msg = await callback.message.answer(
        "Выберите инструктора:",
        reply_markup=await kb.inline_schedule_edit_instructors()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_instructor)


@admin_router.callback_query(AddScheduleStates.waiting_for_instructor, F.data.startswith("instructor_"))
async def process_instructor(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructor_id = int(callback.data.split('_')[1])
    await state.update_data(instructor=f"api/users/{instructor_id}")

    data = await state.get_data()

    time_from = datetime.fromisoformat(data['time_from']).strftime('%H:%M')
    time_to = datetime.fromisoformat(data['time_to']).strftime('%H:%M')
    days = data['days_of_week']
    notice = data.get('notice', 'отсутствует')

    autodrome = get_autodrome_by_id(int(data['autodrome'].split('/')[-1]))
    category = get_category_by_id(int(data['category'].split('/')[-1]))
    instructor = get_instructor_by_id(int(data['instructor'].split('/')[-1]))

    confirm_text = (
        "Проверьте данные нового расписания:\n\n"
        f"🕒 Время: {time_from} - {time_to}\n"
        f"📆 Дни: {days}\n"
        f"📝 Примечание: {notice}\n"
        f"🏁 Автодром: {autodrome.title}\n"
        f"📋 Категория: {category.title}\n"
        f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
        "Создать расписание?"
    )

    msg = await callback.message.answer(
        confirm_text,
        reply_markup=await kb.confirm_schedule_add_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.confirmation)


@admin_router.callback_query(AddScheduleStates.confirmation, F.data == "confirm_schedule_addition")
async def finalize_schedule_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    schedule_data = {
        "timeFrom": data['time_from'],
        "timeTo": data['time_to'],
        "daysOfWeek": data['days_of_week'],
        "notice": data.get('notice'),
        "autodrome": data['autodrome'],
        "category": data['category'],
        "instructor": data['instructor']
    }

    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    success = add_schedule(schedule_data, email, password)

    if success == 201:
        await callback.message.edit_text("✅ Расписание успешно создано!")
    else:
        await callback.message.edit_text("❌ Ошибка при создании расписания!")

    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_schedule_addition")
async def cancel_schedule_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Создание расписания отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "auto_list")
async def get_auto_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все авто в системе ⬇️",
                                  reply_markup=await kb.admin_inline_cars())

    await state.set_state(AllCarsStates.waiting_for_id)


@admin_router.callback_query(AllCarsStates.waiting_for_id)
async def get_auto_admin_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_car":
        await start_adding_car(callback, state)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data)
    car = get_admin_car_by_id(car_id)
    car_mark = get_car_mark_title(car_id)

    await callback.message.answer(text=f"🧑‍🏫 Информация об автомобиле {car_id}:\n\n"
                                       f"▫️ <b>Марка:</b> {car_mark}\n"
                                       f"▫️ <b>Модель:</b> {car.carModel}\n"
                                       f"▫️ <b>Номер:</b> {car.stateNumber}\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.cars_action(car_id))

    await state.clear()


@admin_router.callback_query(F.data.startswith('delete_car_'))
async def delete_car_by_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data.split('_')[2])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    result = delete_car(car_id, email, password)

    if result == 204:
        result_msg = await callback.message.answer(text="Удаление успешно")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)
    else:
        result_msg = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_car")
async def start_adding_car(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    # Инициализируем все поля как None
    await state.update_data(
        carMark=None,
        carModel=None,
        stateNumber=None,
        productionYear=None,
        vinNumber=None
    )

    msg = await callback.message.answer(
        "Выберите марку автомобиля:",
        reply_markup=await kb.get_marks_car()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_mark)


@admin_router.callback_query(AddCarStates.waiting_for_mark, F.data.startswith("mark_"))
async def process_car_mark(callback: CallbackQuery, state: FSMContext):
    mark_id = int(callback.data.split('_')[1])
    mark_title = get_car_mark_title(mark_id)

    if not mark_title:
        await callback.answer("Марка не найдена")
        return

    await state.update_data(carMark=mark_id)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        f"Марка: {mark_title}\nВведите модель автомобиля:",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_model)


@admin_router.message(AddCarStates.waiting_for_model)
async def process_car_model(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(carModel=message.text)

    msg = await message.answer(
        "Введите гос. номер (например, А123БВ777):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_number)


@admin_router.message(AddCarStates.waiting_for_number)
async def process_state_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 6 or len(message.text) > 9:
        error_msg = await message.answer(
            "Номер должен содержать от 6 до 9 символов. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(stateNumber=message.text.upper())

    msg = await message.answer(
        "Введите год выпуска (например, 2020):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_year)


@admin_router.message(AddCarStates.waiting_for_year)
async def process_production_year(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    try:
        year = int(message.text)
        current_year = datetime.now().year

        if year < 1980 or year > current_year + 1:
            raise ValueError
    except ValueError:
        current_year = datetime.now().year
        error_msg = await message.answer(
            f"Год должен быть числом между 1980 и {current_year + 1}. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(productionYear=str(year))

    msg = await message.answer(
        "Введите VIN номер (17 символов):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_vin)


@admin_router.message(AddCarStates.waiting_for_vin)
async def process_vin_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    vin = message.text.upper().strip()

    if len(vin) != 17 or not all(c.isalnum() for c in vin):
        error_msg = await message.answer(
            "VIN должен содержать ровно 17 букв и цифр. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(vinNumber=vin)

    data = await state.get_data()
    mark_title = get_car_mark_title(data['carMark'])

    confirm_text = (
        "Проверьте данные автомобиля:\n\n"
        f"🏷️ Марка: {mark_title}\n"
        f"🚗 Модель: {data['carModel']}\n"
        f"🔢 Гос. номер: {data['stateNumber']}\n"
        f"📅 Год выпуска: {data['productionYear']}\n"
        f"🔎 VIN: {data['vinNumber']}\n\n"
        "Всё верно?"
    )

    msg = await message.answer(
        confirm_text,
        reply_markup=await kb.confirm_car_addition_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.confirmation)


@admin_router.callback_query(AddCarStates.confirmation, F.data == "confirm_car_addition")
async def finalize_car_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_data = {
        "carMark": f"api/auto_producers/{data['carMark']}",
        "carModel": data['carModel'],
        "stateNumber": data['stateNumber'],
        "productionYear": int(data['productionYear']),
        "vinNumber": data['vinNumber']
    }

    credentials = storage.get_user_credentials(callback.from_user.id)
    success = add_car_to_api(car_data, credentials.email, credentials.password)

    if success == 201:
        msg = await callback.message.answer("✅ Автомобиль успешно добавлен!")
    else:
        msg = await callback.message.answer("❌ Ошибка при добавлении автомобиля!")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_car_addition")
async def cancel_car_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Добавление автомобиля отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("update_car_"))
async def start_updating_admin_car(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data.split('_')[2])
    car = get_admin_car_by_id(car_id)

    if not car:
        await callback.message.answer("Автомобиль не найден")
        return

    car_dict = {
        'id': car_id,
        'carMark': car.carMark.get('id'),
        'carModel': car.carModel,
        'stateNumber': car.stateNumber,
        'productionYear': car.productionYear,
        'vinNumber': car.vinNumber
    }

    await state.update_data(
        original_car=car_dict,
        current_car=car_dict.copy()
    )
    await show_admin_car_edit_options(callback, state)
    await state.set_state(EditCarStates.waiting_for_choose)


async def show_admin_car_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    car = data['current_car']
    car_mark_title = get_car_mark_title(car.get('carMark'))

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Марка: {car_mark_title}", callback_data="edit_car_admin_mark")
    keyboard.button(text=f"Модель: {car.get('carModel')}", callback_data="edit_car_admin_model")
    keyboard.button(text=f"Гос. номер: {car.get('stateNumber')}", callback_data="edit_car_admin_number")
    keyboard.button(text=f"Год выпуска: {car.get('productionYear')}", callback_data="edit_car_admin_year")
    keyboard.button(text=f"VIN: {car.get('vinNumber')}", callback_data="edit_car_admin_vin")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_car_editing_admin")
    keyboard.button(text="❌ Отменить", callback_data="cancel_car_edit")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в автомобиле? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в автомобиле? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в автомобиле? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в автомобиле? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(EditCarStates.waiting_for_choose)


@admin_router.callback_query(
    EditCarStates.waiting_for_choose,
    F.data.startswith("edit_car_admin_")
)
async def process_admin_car_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[3]

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if choice == "mark":
        msg = await callback.message.answer(
            "Выберите новую марку:",
            reply_markup=await kb.get_marks_car()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditCarStates.waiting_for_mark)

    if choice == "model":
        msg = await callback.message.answer(
            "Введите новую модель автомобиля или отправьте '-' чтобы оставить текущую:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditCarStates.waiting_for_model)

    elif choice == "number":
        msg = await callback.message.answer(
            "Введите новый гос. номер или отправьте '-' чтобы оставить текущий:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditCarStates.waiting_for_number)

    elif choice == "year":
        msg = await callback.message.answer(
            "Введите новый год выпуска или отправьте '-' чтобы оставить текущий:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditCarStates.waiting_for_year)

    elif choice == "vin":
        msg = await callback.message.answer(
            "Введите новый VIN номер или отправьте '-' чтобы оставить текущий:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditCarStates.waiting_for_vin)

    await callback.answer()


@admin_router.callback_query(EditCarStates.waiting_for_mark, F.data.startswith("mark_"))
async def process_admin_edit_car_mark(callback: CallbackQuery, state: FSMContext):
    mark_id = int(callback.data.split('_')[1])
    data = await state.get_data()

    mark_title = get_car_mark_title(mark_id)

    if not mark_title:
        await callback.answer("Марка не найдена")
        return

    data['current_car']['carMark'] = mark_id
    await state.update_data(current_car=data['current_car'])

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await show_admin_car_edit_options(callback, state)
    await callback.answer(f"Марка изменена на {mark_title}")


@admin_router.message(EditCarStates.waiting_for_model)
async def process_admin_edit_car_model(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        data['current_car']['carModel'] = message.text
        await state.update_data(current_car=data['current_car'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_admin_car_edit_options(message, state)


@admin_router.message(EditCarStates.waiting_for_number)
async def process_admin_edit_car_number(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        if len(message.text) < 6 or len(message.text) > 9:
            error_msg = await message.answer(
                "Номер должен содержать от 6 до 9 символов. Попробуйте снова:",
                reply_markup=await kb.get_cancel_car_edit_keyboard()
            )
            return error_msg

        data['current_car']['stateNumber'] = message.text.upper()
        await state.update_data(current_car=data['current_car'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_admin_car_edit_options(message, state)


@admin_router.message(EditCarStates.waiting_for_year)
async def process_admin_edit_car_year(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        try:
            year = int(message.text)
            current_year = datetime.now().year
            if year < 1980 or year > current_year + 1:
                raise ValueError

            data['current_car']['productionYear'] = str(year)
            await state.update_data(current_car=data['current_car'])
        except ValueError:
            current_year = datetime.now().year
            error_msg = await message.answer(
                f"Год должен быть числом между 1980 и {current_year + 1}. Попробуйте снова:",
                reply_markup=await kb.get_cancel_car_edit_keyboard()
            )
            return error_msg

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_admin_car_edit_options(message, state)


@admin_router.message(EditCarStates.waiting_for_vin)
async def process_admin_edit_car_vin(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    if message.text != '-':
        vin = message.text.upper().strip()
        if len(vin) != 17 or not all(c.isalnum() for c in vin):
            error_msg = await message.answer(
                "VIN должен содержать ровно 17 букв и цифр. Попробуйте снова:",
                reply_markup=await kb.get_cancel_car_edit_keyboard()
            )
            return error_msg

        data['current_car']['vinNumber'] = vin
        await state.update_data(current_car=data['current_car'])

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await show_admin_car_edit_options(message, state)


@admin_router.callback_query(F.data == "finish_car_editing_admin")
async def finalize_admin_car_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_car']
    updated = data['current_car']

    changes = {}
    for key in ['carMark', 'carModel', 'stateNumber', 'productionYear', 'vinNumber']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        car_data = {
            "carMark": f"api/auto_producers/{updated.get('carMark')}",
            "carModel": updated.get('carModel'),
            "stateNumber": updated.get('stateNumber'),
            "productionYear": int(updated.get('productionYear')),
            "vinNumber": updated.get('vinNumber')
        }

        update_result = update_car_in_api(
            car_id=changes['id'],
            car_data=car_data,
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            msg = await callback.message.answer("✅ Автомобиль успешно обновлен!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении автомобиля")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_car_edit")
async def cancel_car_edit(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Редактирование автомобиля отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "lessons_list")
async def get_lesson_list(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    await callback.message.answer(text="Вот список всех зантий ⬇️",
                                  reply_markup=await kb.admin_lessons())

    await state.set_state(AdminLessonStates.waiting_for_id)


@admin_router.callback_query(AdminLessonStates.waiting_for_id)
async def get_admin_lesson_info_by_id(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    if callback.data == "add_admin_lesson":
        await start_admin_adding_lesson(callback, state)
    else:
        lesson_id = int(callback.data)
        lesson = get_lesson_by_id(lesson_id)

        info = (
            "📚 <b>Занятие</b>:\n\n"
            f"📖 <b>Название</b>: {lesson.title}\n\n"
            f"📝 <b>Описание</b>: {lesson.description}\n\n"
            f"🎯 <b>Тип урока</b>: {lesson.lesson_type}\n\n"
            f"📅 <b>Дата</b>: {datetime.fromisoformat(lesson.date).strftime('%d.%m.%Y %H:%M')}\n\n"
        )

        await callback.message.answer(
            text=info,
            parse_mode="HTML",
            reply_markup=await kb.admin_lesson_action(lesson_id)
        )
        await state.set_state(AdminLessonStates.waiting_for_video)


@admin_router.callback_query(AdminLessonStates.waiting_for_video, F.data.startswith('video_'))
async def check_lesson_video(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    video_url = f"{lessons_videos}{callback.data.split('_')[1]}"
    await callback.message.answer_video(
        video=URLInputFile(video_url),
        reply_markup=static_kb.back_to_admin_menu,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=15
    )
    await state.clear()


@admin_router.callback_query(F.data.startswith('delete_admin_lesson_'))
async def delete_admin_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    credentials = storage.get_user_credentials(callback.from_user.id)
    lesson_id = int(callback.data.split('_')[3])

    result = delete_lesson_from_api(lesson_id, credentials.email, credentials.password)

    if result == 204:
        msg = await callback.message.answer(text="✅ Урок удален")
    else:
        msg = await callback.message.answer(text="❌ Удаление не удалось")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await get_lesson_list(callback, state)


@admin_router.callback_query(F.data == "add_admin_lesson")
async def start_admin_adding_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await MessageManager.safe_delete(callback.message)

    msg = await callback.message.answer(
        "Введите название занятия ⬇️",
        reply_markup=await kb.get_cancel_teacher_add_lesson_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AdminAddLessonStates.waiting_for_title)


@admin_router.message(AdminAddLessonStates.waiting_for_title)
async def process_admin_lesson_title(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(message, state)

    msg = await message.answer(
        "Введите описание занятия ⬇️",
        reply_markup=await kb.get_cancel_admin_add_lesson_keyboard()
    )
    await state.update_data({
        'title': message.text,
        'last_bot_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(AdminAddLessonStates.waiting_for_description)


@admin_router.message(AdminAddLessonStates.waiting_for_description)
async def process_teacher_lesson_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(message, state)

    msg = await message.answer(
        "Выберите тип занятия ⬇️",
        reply_markup=await kb.get_event_admin_type_keyboard()
    )
    await state.update_data({
        'description': message.text,
        'last_bot_msg': msg.message_id,
        'last_keyboard_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(AdminAddLessonStates.waiting_for_type)


@admin_router.callback_query(AdminAddLessonStates.waiting_for_type)
async def process_teacher_lesson_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])
    if 'last_keyboard_msg' in data:
        prev_msgs.append(data['last_keyboard_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(callback, state)

    msg = await callback.message.answer(
        "Выберите дату для занятия ⬇️",
        reply_markup=await RussianSimpleCalendar().start_calendar(allowed_days="Пн,Вт,Ср,Чт,Пт,Сб,Вс")
    )
    await state.update_data({
        'type': callback.data,
        'last_bot_msg': msg.message_id,
        'last_keyboard_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(AdminAddLessonStates.waiting_for_date)


@admin_router.callback_query(AdminAddLessonStates.waiting_for_date, SimpleCalendarCallback.filter())
async def process_admin_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    current_state = await state.get_state()
    if current_state != AdminAddLessonStates.waiting_for_date.state:
        return

    try:
        if callback_data.act == "DAY":
            selected_date = date(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            if selected_date < datetime.now().date():
                await callback.answer("❌ Нельзя выбрать прошедшую дату!", show_alert=True)
                return

            await MessageManager.safe_delete(callback.message)
            await state.update_data(date=selected_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            await callback.message.answer(
                "Выберите время занятия:",
                reply_markup=kb.get_time_admin_selection_keyboard()
            )
            await state.set_state(AdminAddLessonStates.waiting_for_time)

        elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            new_year, new_month = callback_data.year, callback_data.month

            if callback_data.act == "PREV-YEAR":
                new_year -= 1
            elif callback_data.act == "NEXT-YEAR":
                new_year += 1
            elif callback_data.act == "PREV-MONTH":
                new_month -= 1
                if new_month < 1:
                    new_month = 12
                    new_year -= 1
            elif callback_data.act == "NEXT-MONTH":
                new_month += 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month
                )
            )

        elif callback_data.act == "CANCEL":
            await cancel_admin_add_lesson(callback, state)
            await state.clear()

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@admin_router.callback_query(AdminAddLessonStates.waiting_for_time, F.data.startswith("admin_lesson_time_"))
async def process_teacher_lesson_time(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    selected_time_str = callback.data.split("_")[3]
    hours, minutes = map(int, selected_time_str.split(":"))
    selected_time = time(hour=hours, minute=minutes)

    data = await state.get_data()
    selected_date = datetime.strptime(data.get("date"), '%Y-%m-%dT%H:%M:%S.%fZ').date()
    combined_datetime = datetime.combine(selected_date, selected_time)

    form_data = {
        "title": data.get("title", "string"),
        "description": data.get("description", "string"),
        "type": data.get("type", "string"),
        "teacher": f'api/users/{storage.get_user_credentials(callback.from_user.id).db_id}',
        "date": combined_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    credentials = storage.get_user_credentials(callback.from_user.id)
    success = add_lesson_to_api(credentials.email, credentials.password, form_data)

    if success:
        msg_text = (
            "✅ Занятие успешно создано!\n\n"
            f"📌 Название: {form_data['title']}\n"
            f"📝 Описание: {form_data['description']}\n"
            f"🔘 Тип: {form_data['type']}\n"
            f"📅 Дата: {combined_datetime.strftime('%d-%m-%Y %H:%M')}\n"
            f"⏰ Время: {selected_time_str}"
        )
    else:
        msg_text = "❌ Ошибка при создании занятия"

    msg = await callback.message.answer(msg_text)
    await asyncio.sleep(3)
    await MessageManager.safe_delete(msg)
    await state.clear()
    await get_lesson_list(callback, state)


@admin_router.callback_query(F.data == "cancel_admin_add_lesson")
async def cancel_admin_add_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_lesson_list(callback, state)


@admin_router.callback_query(F.data.startswith('update_admin_lesson_'))
async def start_admin_lesson_editing(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[3])
    lesson_data = get_lesson_by_id(lesson_id)

    lesson_dict = {
        'id': lesson_data.id,
        'title': lesson_data.title,
        'description': lesson_data.description,
        'type': lesson_data.lesson_type,
        'date': lesson_data.date,
    }

    await state.update_data(
        original_lesson=lesson_dict,
        current_lesson=lesson_dict.copy()
    )
    await show_edit_options(callback, state)
    await state.set_state(AdminEditLessonState.waiting_for_choose)


async def show_edit_options(update: Message | CallbackQuery, state: FSMContext, force_new_message: bool = False):
    data = await state.get_data()
    lesson = data['current_lesson']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Название: {lesson.get('title')}", callback_data="edit_admin_title")
    keyboard.button(text=f"Описание: {lesson.get('description')[:30]}...", callback_data="edit_admin_description")
    keyboard.button(text=f"Тип: {lesson.get('type')}", callback_data="edit_admin_type")
    keyboard.button(text=f"Дата: {datetime.fromisoformat(lesson.get('date')).strftime('%d-%m-%Y %H:%M')}",
                    callback_data="edit_admin_date")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_admin_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_admin_editing")
    keyboard.adjust(1)

    message_text = "Что вы хотите изменить? (нажмите на пункт для редактирования)"

    if isinstance(update, CallbackQuery) and not force_new_message:
        try:
            await update.message.edit_text(
                message_text,
                reply_markup=keyboard.as_markup()
            )
        except TelegramBadRequest:
            await update.message.answer(
                message_text,
                reply_markup=keyboard.as_markup()
            )
    else:
        await update.message.answer(
            message_text,
            reply_markup=keyboard.as_markup()
        ) if isinstance(update, CallbackQuery) else await update.answer(
            message_text,
            reply_markup=keyboard.as_markup()
        )

    await state.set_state(AdminEditLessonState.waiting_for_choose)


@admin_router.callback_query(AdminEditLessonState.waiting_for_choose, F.data.startswith("edit_"))
async def process_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[2]
    await MessageManager.safe_delete(callback.message)

    if choice == "title":
        await callback.message.answer(
            "Введите новое название или отправьте '-' чтобы пропустить:",
            reply_markup=await kb.get_cancel_admin_update_lesson_keyboard()
        )
        await state.set_state(AdminEditLessonState.waiting_for_title)

    elif choice == "description":
        await callback.message.answer(
            "Введите новое описание или отправьте '-' чтобы пропустить:",
            reply_markup=await kb.get_cancel_admin_update_lesson_keyboard()
        )
        await state.set_state(AdminEditLessonState.waiting_for_description)

    elif choice == "type":
        await callback.message.answer(
            "Выберите новый тип занятия или нажмите 'Пропустить':",
            reply_markup=await kb.get_event_admin_update_type_keyboard()
        )
        await state.set_state(AdminEditLessonState.waiting_for_type)

    elif choice == "date":
        await callback.message.answer(
            "Выберите новую дату или нажмите 'Пропустить':",
            reply_markup=await RussianSimpleCalendar().start_calendar()
        )
        await state.set_state(AdminEditLessonState.waiting_for_date)

    await callback.answer()


@admin_router.message(AdminEditLessonState.waiting_for_title)
async def process_edit_title(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_lesson']['title'] = message.text
        await state.update_data(current_lesson=data['current_lesson'])

    await show_edit_options(message, state)


@admin_router.message(AdminEditLessonState.waiting_for_description)
async def process_edit_description(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_lesson']['description'] = message.text
        await state.update_data(current_lesson=data['current_lesson'])

    await show_edit_options(message, state)


@admin_router.callback_query(AdminEditLessonState.waiting_for_type, F.data.in_(["admin_online", "admin_offline",
                                                                                "admin_skip"]))
async def process_edit_type(callback: CallbackQuery, state: FSMContext):
    if callback.data.split('_')[1] != "skip":
        data = await state.get_data()
        data['current_lesson']['type'] = callback.data.split('_')[1]
        await state.update_data(current_lesson=data['current_lesson'])
    else:
        await callback.answer("Редактирование типа занятия пропущено")

    await show_edit_options(callback, state)


@admin_router.callback_query(AdminEditLessonState.waiting_for_date, SimpleCalendarCallback.filter())
async def process_edit_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    try:
        if callback_data.act == "DAY":
            selected_date = date(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            if selected_date < datetime.now().date():
                await callback.answer("❌ Нельзя выбрать прошедшую дату!", show_alert=True)
                return

            await MessageManager.safe_delete(callback.message)

            data = await state.get_data()
            current_lesson = data['current_lesson'].copy()
            current_lesson['date'] = selected_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            await state.update_data(current_lesson=current_lesson)

            time_keyboard = kb.get_time_admin_selection_keyboard(with_skip=True)
            await callback.message.answer(
                f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}\n"
                "Выберите время занятия:",
                reply_markup=time_keyboard
            )
            await state.set_state(AdminEditLessonState.waiting_for_time)

        elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            new_year, new_month = callback_data.year, callback_data.month

            if callback_data.act == "PREV-YEAR":
                new_year -= 1
            elif callback_data.act == "NEXT-YEAR":
                new_year += 1
            elif callback_data.act == "PREV-MONTH":
                new_month -= 1
                if new_month < 1:
                    new_month = 12
                    new_year -= 1
            elif callback_data.act == "NEXT-MONTH":
                new_month += 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month
                )
            )

        elif callback_data.act == "CANCEL":
            await callback.message.delete()
            await show_edit_options(callback, state)

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@admin_router.callback_query(AdminEditLessonState.waiting_for_time, F.data.startswith("admin_lesson_time_"))
async def process_selected_time(callback: CallbackQuery, state: FSMContext):
    try:
        selected_time_str = callback.data.split("_")[3]
        hours, minutes = map(int, selected_time_str.split(":"))

        data = await state.get_data()
        selected_date = datetime.strptime(data['current_lesson']['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        combined_datetime = datetime.combine(selected_date, time(hour=hours, minute=minutes))

        current_lesson = data['current_lesson'].copy()
        current_lesson['date'] = combined_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        await state.update_data(current_lesson=current_lesson)

        await MessageManager.safe_delete(callback.message)
        await show_edit_options(callback, state, force_new_message=True)

    except Exception as e:
        print(f"Error processing time: {e}")
        await callback.answer("❌ Ошибка при обработке времени", show_alert=True)


@admin_router.callback_query(F.data == "finish_admin_editing")
async def finish_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_lesson']
    updated = data['current_lesson']

    changes = {}
    for key in ['title', 'description', 'type', 'date']:
        if original[key] != updated[key]:
            changes[key] = updated[key]

    if changes:
        changes['id'] = original['id']
        changes['teacher'] = f'api/users/{storage.get_user_credentials(callback.from_user.id).db_id}'

        credentials = storage.get_user_credentials(callback.from_user.id)
        if update_lesson_in_api(credentials.email, credentials.password, changes) == 200:
            msg = await callback.message.answer("✅ Изменения сохранены!")
            await asyncio.sleep(2)
            await MessageManager.safe_delete(msg)
            await back_to_admin_menu(callback, state)
        else:
            msg = await callback.message.answer("❌ Ошибка при сохранении изменений")
            await asyncio.sleep(2)
            await MessageManager.safe_delete(msg)
            await back_to_admin_menu(callback, state)
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)

    await state.clear()


@admin_router.callback_query(F.data == "cancel_editing")
async def cancel_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_lesson_list(callback, state)


@admin_router.callback_query(F.data == "cancel_admin_update_lesson")
async def cancel_teacher_update_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_lesson_list(callback, state)
