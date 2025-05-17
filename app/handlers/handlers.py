import asyncio
import json
import os
from typing import Optional

from app.APIhandlers.APIhandlersStudent import Student
from app.APIhandlers.APIhandlersUser import UserStorage, start, check_password, send_request
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BotCommand

import app.keyboards.keyboard as kb
import app.keyboards.static_keyboard as static_kb

main_router = Router()

storage = UserStorage()

JSON_DATA_DIR = "data/json/"


def load_json_data(filename: str) -> Optional[dict]:
    filepath = os.path.join(JSON_DATA_DIR, f"{filename}.json")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Запустить бота')
    ]
    await bot.set_my_commands(main_menu_commands)


async def on_startup(bot: Bot):
    await set_main_menu(bot)


class AuthStates(StatesGroup):
    waiting_for_password = State()


@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = storage.get_user(telegram_id)

    credentials = storage.get_credentials(telegram_id)
    user_pass = credentials.password if credentials else "default"

    if user:
        if user_pass == "default_password":
            await message.answer(
                f'Привет, {message.from_user.full_name}\n'
                'Пожалуйста, введите ваш пароль для завершения регистрации:'
            )
            await state.set_state(AuthStates.waiting_for_password)
            await state.update_data(telegram_id=telegram_id, user_data=user)
            return
        else:
            await show_main_menu(message, user)
            return

    db_user = start(telegram_id)

    if db_user == 0:
        await message.answer(
            f'Привет, {message.from_user.full_name}\n'
            'Вы зашли в официального телеграм бота автошколы "Endeavor"\n'
            'Я вижу что вы новичок, с чего бы вы хотели начать?',
            reply_markup=static_kb.guest_main
        )
        storage.clear_user(telegram_id)
        return
    else:
        db_user_pass = getattr(db_user, 'password', "default")
        if hasattr(db_user, 'password') and db_user_pass != "default":
            storage.set_user(
                telegram_id=telegram_id,
                user_data=db_user,
                password=db_user.password,
                db_id=db_user.id
            )
            await show_main_menu(message, db_user)
        else:
            await message.answer(
                f'Привет, {message.from_user.full_name}\n'
                'Пожалуйста, введите ваш пароль для завершения регистрации:'
            )
            await state.set_state(AuthStates.waiting_for_password)
            await state.update_data(telegram_id=telegram_id, user_data=db_user)


@main_router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    telegram_id = data['telegram_id']

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if 'last_bot_message_id' in data:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    try:
        user = storage.get_user(message.from_user.id)

        status_code = check_password(email=user.email, password=password)

        if status_code == 200:
            storage.set_user(
                telegram_id=telegram_id,
                user_data=user,
                password=password,
                db_id=user.id
            )

            msg = await message.answer("🔐 Пароль успешно сохранен!")

            await asyncio.sleep(2)
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass

            await state.clear()
            await show_main_menu(message, user)
        else:
            error_msg = await message.answer("❌ Неверный пароль. Пожалуйста, попробуйте еще раз:")
            await state.update_data(last_bot_message_id=error_msg.message_id)

    except Exception as e:
        error_msg = await message.answer(f"❌ Ошибка: {str(e)}")
        await state.update_data(last_bot_message_id=error_msg.message_id)
        await state.clear()


async def show_main_menu(message: Message, user):
    role = user.roles[0] if user.roles else None
    greeting = f"Привет, {user.surname} {user.name}\n"

    if role == "ROLE_STUDENT":
        greeting += "Ваша роль: Студент"
        markup = static_kb.student_main
    elif role == "ROLE_TEACHER":
        greeting += "Ваша роль: Учитель"
        markup = static_kb.teacher_main
    elif role == "ROLE_INSTRUCTOR":
        greeting += "Ваша роль: Инструктор"
        markup = static_kb.instructor_main
    elif role == "ROLE_ADMIN":
        greeting += "Ваша роль: Администратор"
        markup = static_kb.admin_main
    else:
        greeting += "Ваша роль не определена"
        markup = static_kb.guest_main

    await message.answer(greeting, reply_markup=markup)


@main_router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()

    telegram_id = data['telegram_id']
    user = data.get('user_data')

    if not user:
        user = Student(
            id=telegram_id,
            name=message.from_user.first_name,
            surname=message.from_user.last_name or "",
            patronymic="",
            phone="",
            email="",
            contract="",
            dateOfBirth="",
            roles=["ROLE_STUDENT"],
            image="static/img/default.jpg",
            type="student"
        )

    storage.set_user(
        telegram_id=telegram_id,
        user_data=user,
        password=password,
        db_id=user.id
    )

    await state.clear()

    await message.answer(
        "Регистрация завершена! Теперь вы можете пользоваться ботом.",
        reply_markup=static_kb.student_main if "ROLE_STUDENT" in user.roles else static_kb.guest_main
    )


@main_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=static_kb.guest_main)


class CategoryStates(StatesGroup):
    waiting_for_id = State()


class RequestStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_category = State()
    waiting_for_password = State()
    waiting_for_agreement = State()


class InstructorStates(StatesGroup):
    waiting_for_id = State()
    viewing_instructor = State()


class TeacherStates(StatesGroup):
    waiting_for_id = State()
    viewing_teacher = State()


class CarStates(StatesGroup):
    waiting_for_id = State()
    viewing_car = State()


class CourseStates(StatesGroup):
    waiting_for_id = State()
    viewing_course = State()


class StudentCourseStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_lesson_id = State()
    waiting_for_mark = State()
    waiting_for_video_by_url = State()


class EditStudentStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()
    waiting_for_password = State()
    waiting_for_photo = State()


class ScheduleStates(StatesGroup):
    waiting_for_id = State()
    viewing_schedule = State()


class InstructorLessonStates(StatesGroup):
    waiting_for_date = State()


class BookingStates(StatesGroup):
    waiting_for_password = State()


class MyScheduleStates(StatesGroup):
    waiting_for_id = State()


class TestStates(StatesGroup):
    waiting_for_answer = State()


@main_router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        'Введите ваше имя:',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_name)


@main_router.message(RequestStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    await state.update_data(name=message.text)
    msg = await message.answer(
        'Введите вашу фамилию:',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_surname)


@main_router.message(RequestStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    await state.update_data(surname=message.text)
    msg = await message.answer(
        'Введите ваш телефон:',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_phone)


@main_router.message(RequestStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    phone = message.text
    if not phone.replace('+', '').isdigit():
        msg = await message.answer(
            '❌ Неверный формат телефона. Введите еще раз:',
            reply_markup=static_kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    await state.update_data(phone=phone)
    msg = await message.answer(
        'Введите ваш email:',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_email)


@main_router.message(RequestStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    email = message.text
    if '@' not in email or '.' not in email:
        msg = await message.answer(
            '❌ Неверный формат email. Введите еще раз:',
            reply_markup=static_kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    await state.update_data(email=email)

    msg = await message.answer(
        'Для продолжения необходимо ваше согласие на обработку персональных данных:',
        reply_markup=static_kb.agreement
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_agreement)


# Новый обработчик для согласия на обработку данных
@main_router.callback_query(F.data == 'agree', RequestStates.waiting_for_agreement)
async def process_agreement(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await callback.bot.delete_message(callback.message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    await state.update_data(agreement=True)

    msg = await callback.message.answer(
        'Выберите категорию вождения:',
        reply_markup=await kb.inline_categories()
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_category)


@main_router.callback_query(F.data.startswith('category_'), RequestStates.waiting_for_category)
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    if 'last_bot_message_id' in data:
        try:
            await callback.bot.delete_message(callback.message.chat.id, data['last_bot_message_id'])
        except TelegramBadRequest:
            pass

    if not data.get('agreement', False):
        await callback.message.answer(
            "❌ Для подачи заявки необходимо согласие на обработку персональных данных",
            reply_markup=static_kb.back_to_main_menu
        )
        await state.clear()
        return

    category_id = callback.data.split('_')[1]
    category_title = callback.data.split('_')[2]
    await state.update_data(category=category_id)

    response_status = send_request(
        telegram_id=callback.from_user.id,
        name=data.get('name'),
        surname=data.get('surname'),
        phone=data.get('phone'),
        email=data.get('email'),
        category=category_id
    )

    if response_status == 201:
        await callback.message.answer(
            "✅ Ваша заявка успешно отправлена!\n\n"
            f"<b>Имя:</b> {data.get('name')}\n"
            f"<b>Фамилия:</b> {data.get('surname')}\n"
            f"<b>Телефон:</b> {data.get('phone')}\n"
            f"<b>Email:</b> {data.get('email')}\n"
            f"<b>Категория:</b> {category_title}\n\n"
            "Теперь вы можете войти в систему, используя команду /start",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ Ошибка при отправке заявки.\n"
            "Попробуйте позже или обратитесь в поддержку."
        )

    await state.clear()
