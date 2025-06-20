import asyncio
import json
import os
import re
from typing import Optional

from app.APIhandlers.APIhandlersUser import UserStorage, start, check_password, send_request, get_user_role_by_id, \
    get_full_name
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BotCommand

import app.keyboards.keyboard as kb
import app.keyboards.static_keyboard as static_kb
from app.utils.jsons_creator import UserCredentials

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
    credentials = storage.get_user_credentials(telegram_id)

    if credentials:
        if credentials.password == "default_password":
            await message.answer(
                f'Привет, {message.from_user.full_name}\n'
                'Пожалуйста, введите ваш пароль для завершения регистрации:'
            )
            await state.set_state(AuthStates.waiting_for_password)
            await state.update_data(telegram_id=telegram_id)
            return
        else:
            await show_main_menu(message, credentials)
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
        user_email = db_user.email or ""

        storage.set_user(
            telegram_id=telegram_id,
            db_id=db_user.db_id,
            email=user_email,
            password="default_password"
        )

        await message.answer(
            f'Привет, {message.from_user.full_name}\n'
            'Пожалуйста, введите ваш пароль для завершения регистрации:'
        )
        await state.set_state(AuthStates.waiting_for_password)
        await state.update_data(telegram_id=telegram_id)


@main_router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    telegram_id = data['telegram_id']
    credentials = storage.get_user_credentials(telegram_id)

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
        if not credentials:
            raise ValueError("Пользователь не найден")

        status_code = check_password(email=credentials.email, password=password)

        if status_code == 200:
            storage.set_user(
                telegram_id=telegram_id,
                db_id=credentials.db_id,
                email=credentials.email,
                password=password
            )

            msg = await message.answer("🔐 Пароль верный!")

            await asyncio.sleep(2)
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass

            await state.clear()
            await show_main_menu(message, credentials)
        else:
            error_msg = await message.answer("❌ Неверный пароль. Пожалуйста, попробуйте еще раз:")
            await state.update_data(last_bot_message_id=error_msg.message_id)

    except Exception as e:
        error_msg = await message.answer(f"❌ Ошибка: {str(e)}")
        await state.update_data(last_bot_message_id=error_msg.message_id)
        await state.clear()


async def show_main_menu(message: Message, credentials: UserCredentials):
    roles = get_user_role_by_id(credentials.db_id)
    greeting = f"Привет, {get_full_name(credentials.db_id)}\n"
    markup = static_kb.guest_main

    if roles:
        role = roles
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

    await message.answer(greeting, reply_markup=markup)


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


class EditAdminStates(StatesGroup):
    waiting_for_choose = State()
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


class AllUsersStates(StatesGroup):
    waiting_for_id = State()


class EditStudentFromAdminStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()


class EditInstructorFromAdminStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()


class EditTeacherFromAdminStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()


class AllCoursesStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_lesson_id = State()


class AllCategoryStates(StatesGroup):
    waiting_for_id = State()


class AllSchedulesStates(StatesGroup):
    waiting_for_id = State()


class InstructorSchedulesStates(StatesGroup):
    waiting_for_id = State()


class AddUserStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()
    waiting_for_email = State()
    waiting_for_password = State()
    confirmation = State()


class UpdateCourseStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_lessons = State()
    waiting_for_users = State()
    waiting_for_category = State()
    waiting_for_quizzes = State()
    confirmation = State()


class UpdateTeacherCourseStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_lessons = State()
    waiting_for_users = State()
    waiting_for_category = State()
    waiting_for_quizzes = State()
    confirmation = State()


class AddCourseStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_lessons = State()
    waiting_for_users = State()
    waiting_for_category = State()
    waiting_for_quizzes = State()
    confirmation = State()


class AddTeacherCourseStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_lessons = State()
    waiting_for_users = State()
    waiting_for_category = State()
    waiting_for_quizzes = State()
    confirmation = State()


class AddCategoryStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_price = State()
    waiting_for_master_title = State()
    waiting_for_title = State()
    waiting_for_description = State()
    confirmation = State()


class UpdateCategoryStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_title = State()
    waiting_for_masterTitle = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_type = State()


class EditScheduleStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_time_from = State()
    waiting_for_time_to = State()
    waiting_for_days = State()
    waiting_for_notice = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_instructor = State()
    confirmation = State()


class EditInstructorScheduleStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_time_from = State()
    waiting_for_time_to = State()
    waiting_for_days = State()
    waiting_for_notice = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_instructor = State()
    confirmation = State()


class AllCarsStates(StatesGroup):
    waiting_for_id = State()


class EditCarStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_mark = State()
    waiting_for_model = State()
    waiting_for_number = State()
    waiting_for_year = State()
    waiting_for_vin = State()
    confirmation = State()


class AddScheduleStates(StatesGroup):
    waiting_for_time_from = State()
    waiting_for_time_to = State()
    waiting_for_days = State()
    waiting_for_notice = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_instructor = State()
    confirmation = State()


class AddInstructorScheduleStates(StatesGroup):
    waiting_for_time_from = State()
    waiting_for_time_to = State()
    waiting_for_days = State()
    waiting_for_notice = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_instructor = State()
    confirmation = State()


class AddCarStates(StatesGroup):
    waiting_for_mark = State()
    waiting_for_model = State()
    waiting_for_number = State()
    waiting_for_year = State()
    waiting_for_vin = State()
    confirmation = State()


class AdminLessonStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_video = State()


class AdminAddLessonStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_date = State()
    waiting_for_time = State()


class AdminEditLessonState(StatesGroup):
    waiting_for_choose = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_date = State()
    waiting_for_time = State()


class TeacherCourseState(StatesGroup):
    waiting_for_id = State()


class TeacherLessonState(StatesGroup):
    waiting_for_id = State()
    waiting_for_video = State()


class TeacherAddLessonState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_date = State()
    waiting_for_time = State()


class TeacherEditLessonState(StatesGroup):
    waiting_for_choose = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_date = State()
    waiting_for_time = State()


class TeacherQuizzesState(StatesGroup):
    waiting_for_id = State()


class TeacherAddQuizState(StatesGroup):
    waiting_for_question = State()
    waiting_for_answers = State()
    waiting_for_correct_answer = State()


class TeacherEditQuestionState(StatesGroup):
    waiting_for_choose = State()
    waiting_for_question_text = State()
    waiting_for_answer_text = State()
    waiting_for_correct_answer = State()


class CheckTeacherStudentProgress(StatesGroup):
    waiting_for_id = State()


class CourseSignUpState(StatesGroup):
    waiting_for_id = State()


class StudentTransactionsState(StatesGroup):
    waitintg_for_id = State()


class InstructorDriveLessonState(StatesGroup):
    waiting_for_id = State()


class AddInstructorLessonStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_student = State()
    confirmation = State()


class EditInstructorLessonStates(StatesGroup):
    waiting_for_choose = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_autodrome = State()
    waiting_for_category = State()
    waiting_for_student = State()


class FillStudentBalance(StatesGroup):
    waiting_for_amount = State()
    waiting_for_method = State()


@main_router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        'Введите ваше имя ⬇️',
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
        'Введите вашу фамилию ⬇️',
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
        'Введите ваш телефон ⬇️',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_phone)

PHONE_REGEX = re.compile(r'^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

@main_router.message(RequestStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    # Удаление предыдущих сообщений
    await delete_previous_messages(message, state)

    phone = message.text.strip()

    # Нормализация номера телефона
    normalized_phone = re.sub(r'[^\d+]', '', phone)

    # Проверка валидности номера
    if not PHONE_REGEX.fullmatch(phone) or len(normalized_phone) not in (10, 11, 12):
        msg = await message.answer(
            '❌ Неверный формат телефона. Пожалуйста, введите номер в одном из форматов:\n'
            '+7 XXX XXX XX XX\n8 XXX XXX XX XX\nXXX XXX XX XX',
            reply_markup=static_kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    # Приведение к стандартному формату +7...
    if normalized_phone.startswith('8'):
        normalized_phone = '7' + normalized_phone[1:]
    elif len(normalized_phone) == 10:
        normalized_phone = '7' + normalized_phone
    elif not normalized_phone.startswith('+'):
        normalized_phone = '+' + normalized_phone

    await state.update_data(phone=normalized_phone)
    msg = await message.answer(
        '📧 Введите ваш email (например: example@mail.com) ⬇️',
        reply_markup=static_kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_email)

@main_router.message(RequestStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    # Удаление предыдущих сообщений
    await delete_previous_messages(message, state)

    email = message.text.strip().lower()

    # Проверка валидности email
    if not EMAIL_REGEX.fullmatch(email):
        msg = await message.answer(
            '❌ Неверный формат email. Пожалуйста, введите в формате:\n'
            'example@domain.com\n'
            '• Должен содержать @ и точку после него\n'
            '• Допустимы буквы, цифры, точки и дефисы',
            reply_markup=static_kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    # Проверка доменной части
    domain_part = email.split('@')[1]
    if len(domain_part.split('.')) < 2:
        msg = await message.answer(
            '❌ Неверный домен в email. Проверьте правильность написания',
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

async def delete_previous_messages(message: Message, state: FSMContext):
    """Удаление предыдущих сообщений бота и пользователя"""
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
        'Выберите категорию вождения⬇️',
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
