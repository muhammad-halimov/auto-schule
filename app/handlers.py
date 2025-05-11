import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Optional

from app.calendar import RussianSimpleCalendar
from aiogram_calendar.schemas import SimpleCalendarCallback
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile, BotCommand
from app.APIhandler import (get_instructor_by_id, get_teacher_by_id, get_car_by_id, get_course_by_id,
                            get_lesson_by_id, update_user_data, get_drive_schedule_by_id,
                            get_category_by_id, get_autodrome_by_id, post_instructor_lesson, start, send_request,
                            UserStorage, Student, check_password)
from config_local import profile_photos

import app.keyboard as kb

router = Router()

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


def get_user_data(user_id: int) -> Optional[dict]:
    return storage.get(user_id)


class AuthStates(StatesGroup):
    waiting_for_password = State()


@router.message(CommandStart())
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
            reply_markup=kb.guest_main
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


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    telegram_id = data['telegram_id']

    try:
        # Удаляем сообщение с паролем от пользователя
        await message.delete()
    except TelegramBadRequest:
        pass

    # Удаляем предыдущее сообщение бота (если есть)
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

            # Отправляем подтверждение и запоминаем его ID
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
            # Остаемся в состоянии waiting_for_password для повторного ввода

    except Exception as e:
        error_msg = await message.answer(f"❌ Ошибка: {str(e)}")
        await state.update_data(last_bot_message_id=error_msg.message_id)
        await state.clear()


async def show_main_menu(message: Message, user):
    role = user.roles[0] if user.roles else None
    greeting = f"Привет, {user.surname} {user.name}\n"

    if role == "ROLE_STUDENT":
        greeting += "Ваша роль: Студент"
        markup = kb.student_main
    elif role == "ROLE_TEACHER":
        greeting += "Ваша роль: Учитель"
        markup = kb.teacher_main
    elif role == "ROLE_INSTRUCTOR":
        greeting += "Ваша роль: Инструктор"
        markup = kb.instructor_main
    elif role == "ROLE_ADMIN":
        greeting += "Ваша роль: Администратор"
        markup = kb.admin_main
    else:
        greeting += "Ваша роль не определена"
        markup = kb.guest_main

    await message.answer(greeting, reply_markup=markup)


@router.message(AuthStates.waiting_for_password)
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

    # Сохраняем пользователя с введенным паролем
    storage.set_user(
        telegram_id=telegram_id,
        user_data=user,
        password=password,  # Используем введенный пароль
        db_id=user.id
    )

    await state.clear()

    # Приветствуем пользователя
    await message.answer(
        "Регистрация завершена! Теперь вы можете пользоваться ботом.",
        reply_markup=kb.student_main if "ROLE_STUDENT" in user.roles else kb.guest_main
    )


@router.callback_query(F.data == 'info')
async def info(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали просмотр информации')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await state.clear()

    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=kb.info)


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=kb.guest_main)


class RequestStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_category = State()
    waiting_for_password = State()


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
    viewing_lessons = State()
    viewing_course = State()


class EditStudentStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()
    waiting_for_password = State()


class ScheduleStates(StatesGroup):
    waiting_for_id = State()
    viewing_schedule = State()


class InstructorLessonStates(StatesGroup):
    waiting_for_date = State()


class BookingStates(StatesGroup):
    waiting_for_password = State()


class MyScheduleStates(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        'Введите ваше имя:',
        reply_markup=kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_name)


@router.message(RequestStates.waiting_for_name)
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
        reply_markup=kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_surname)


@router.message(RequestStates.waiting_for_surname)
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
        reply_markup=kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_phone)


@router.message(RequestStates.waiting_for_phone)
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
            reply_markup=kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    await state.update_data(phone=phone)
    msg = await message.answer(
        'Введите ваш email:',
        reply_markup=kb.back_to_main_menu
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_email)


@router.message(RequestStates.waiting_for_email)
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
            reply_markup=kb.back_to_main_menu
        )
        await state.update_data(last_bot_message_id=msg.message_id)
        return

    await state.update_data(email=email)
    msg = await message.answer(
        'Выберите категорию вождения:',
        reply_markup=await kb.inline_categories()
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(RequestStates.waiting_for_category)


@router.callback_query(F.data.startswith('category_'), RequestStates.waiting_for_category)
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


@router.callback_query(F.data == 'catalog')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категории')
    await callback.message.answer('Вот категории вождения которые есть в нашей автошколе,'
                                  ' нажмите на любую категорию для просмотра информации о ней',
                                  reply_markup=await kb.inline_categories())


@router.callback_query(F.data == 'A')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию А')
    await callback.message.answer('Категория A это мотоциклы')


@router.callback_query(F.data == 'B')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию B')
    await callback.message.answer('Категория B это легковые автомобили')


@router.callback_query(F.data == 'C')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию C')
    await callback.message.answer('Категория C это грузовые автомобили')


@router.callback_query(F.data == 'D')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию D')
    await callback.message.answer('Категория D это грузовые автобусы')


@router.callback_query(F.data == 'D')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию D')
    await callback.message.answer('Категория D это грузовые автобусы')


@router.callback_query(F.data == 'А')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию D')
    await callback.message.answer('Категория D это грузовые автобусы')


@router.callback_query(F.data == 'В')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию D')
    await callback.message.answer('Категория D это грузовые автобусы')


@router.callback_query(F.data == 'С')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию D')
    await callback.message.answer('Категория D это грузовые автобусы')


@router.callback_query(F.data == 'instructors')
async def request_instructors(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали инструкторов')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructors_kb = await kb.inline_instructors()

    instructors_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=instructors_kb)
    await state.set_state(InstructorStates.waiting_for_id)


@router.callback_query(F.data == 'back_to_info')
async def back_to_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await info(callback, state)


@router.callback_query(F.data == 'teachers')
async def request_teachers(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали учителей')
    await callback.message.delete()

    teachers_kb = await kb.inline_teachers()

    teachers_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот учителя которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=teachers_kb)
    await state.set_state(TeacherStates.waiting_for_id)


@router.callback_query(F.data == 'cars')
async def request_cars(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали автомобили')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cars_kb = await kb.inline_cars()

    cars_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот автомобили которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о ней',
                                  reply_markup=cars_kb)
    await state.set_state(CarStates.waiting_for_id)


@router.callback_query(F.data == 'courses')
async def request_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали курсы')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот курсы которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о нем',
                                  reply_markup=courses_kb)
    await state.set_state(CourseStates.waiting_for_id)


@router.callback_query(
    F.data.in_(['instructors', 'teachers', 'cars', 'courses', 'student_courses']),
    StateFilter('*')
)
async def cancel_current_action(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    if callback.data == 'instructors':
        await request_instructors(callback, state)
    elif callback.data == 'teachers':
        await request_teachers(callback, state)
    elif callback.data == 'cars':
        await request_cars(callback, state)
    elif callback.data == 'courses':
        await request_courses(callback, state)
    elif callback.data == 'student_courses':
        await show_student_courses(callback, state)


# INSTRUCTORS


@router.callback_query(InstructorStates.waiting_for_id)
async def handle_instructor_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructor_id = int(callback.data)
    instructor = get_instructor_by_id(instructor_id)

    if instructor:
        message_text = (
            f"🧑‍🏫 Информация об инструкторе:\n\n"
            f"▫️ <b>ФИО:</b> {instructor.surname} {instructor.name} {instructor.patronymic}\n"
            f"▫️ <b>Телефон:</b> {instructor.phone}\n"
            f"▫️ <b>Email:</b> {instructor.email}\n"
            f"▫️ <b>Водительское удостоверение:</b> {instructor.license}\n"
        )
        if hasattr(instructor, 'image') and instructor.image:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{instructor.image}"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=kb.instructor_back_button
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=kb.instructor_back_button)
        else:
            await callback.message.answer_photo(
                photo=FSInputFile("static/img/default.jpg"),
                caption=message_text,
                parse_mode='HTML',
                reply_markup=kb.instructor_back_button)
    else:
        await callback.message.answer("Инструктор не найден",
                                      reply_markup=kb.instructor_back_button)

    await state.set_state(InstructorStates.viewing_instructor)


@router.callback_query(F.data == "back_to_instructors_list", InstructorStates.viewing_instructor)
async def back_to_instructors_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructors_kb = await kb.inline_instructors()

    instructors_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=instructors_kb)

    await state.set_state(InstructorStates.waiting_for_id)


# TEACHERS

@router.callback_query(TeacherStates.waiting_for_id)
async def handle_teacher_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    teacher_id = int(callback.data)
    teacher = get_teacher_by_id(teacher_id)

    if teacher:
        message_text = (
            f"🧑‍🏫 Информация об учителе:\n\n"
            f"▫️ <b>ФИО:</b> {teacher.surname} {teacher.name} {teacher.patronymic}\n"
            f"▫️ <b>Телефон:</b> {teacher.phone}\n"
            f"▫️ <b>Email:</b> {teacher.email}\n"
        )
        if hasattr(teacher, 'image') and teacher.image:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{teacher.image}"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=kb.teacher_back_button
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=kb.teacher_back_button
                )
        else:
            await callback.message.answer_photo(
                photo=FSInputFile("static/img/default.jpg"),
                caption=message_text,
                parse_mode='HTML',
                reply_markup=kb.teacher_back_button)
    else:
        await callback.message.answer("Учитель не найден",
                                      reply_markup=kb.teacher_back_button)

    await state.set_state(TeacherStates.viewing_teacher)


@router.callback_query(F.data == "back_to_teachers_list", TeacherStates.viewing_teacher)
async def back_to_teachers_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    teachers_kb = await kb.inline_teachers()

    teachers_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer(
        'Вот учителя которые есть в нашей автошколе, '
        'нажмите на любого для просмотра информации о нем',
        reply_markup=teachers_kb)

    await state.set_state(TeacherStates.waiting_for_id)


# CARS

@router.callback_query(CarStates.waiting_for_id)
async def handle_car_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data)
    car = get_car_by_id(car_id)

    if car:
        message_text = (
            f"🧑‍🏫 Информация об автомобиле:\n\n"
            f"▫️ <b>Марка:</b> {car.carMark}"
            f"▫️ <b>Модель:</b> {car.carModel}\n"
            f"▫️ <b>Номер:</b> {car.stateNumber}\n"
        )

        await callback.message.answer(message_text, parse_mode='HTML',
                                      reply_markup=kb.car_back_button)
    else:
        await callback.message.answer("Автомобиль не найден",
                                      reply_markup=kb.car_back_button)

    await state.set_state(CarStates.viewing_car)


@router.callback_query(F.data == "back_to_cars_list", CarStates.viewing_car)
async def back_to_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cars_kb = await kb.inline_cars()

    cars_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer(
        'Вот автомобили которые есть в нашей автошколе, '
        'нажмите на любой для просмотра информации о ней',
        reply_markup=cars_kb)

    await state.set_state(CarStates.waiting_for_id)


# COURSES

@router.callback_query(CourseStates.waiting_for_id)
async def handle_course_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = int(callback.data)
    course = get_course_by_id(course_id)

    if course:
        message_text = (
            f"🧑‍🏫 Информация о курсе:\n\n"
            f"▫️ <b>Название:</b> {course.title}\n"
            f"▫️ <b>Описание:</b> {course.description}"
        )
        await callback.message.answer(message_text, parse_mode='HTML',
                                      reply_markup=kb.course_back_button)
    else:
        await callback.message.answer("Курс не найден",
                                      reply_markup=kb.course_back_button)

    await state.set_state(CourseStates.viewing_course)


@router.callback_query(F.data == "back_to_courses_list", CourseStates.viewing_course)
async def back_to_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer(
        'Вот курсы которые есть в нашей автошколе, '
        'нажмите на любой для просмотра информации о нем',
        reply_markup=courses_kb)

    await state.set_state(CourseStates.waiting_for_id)


@router.callback_query(F.data == "student_info")
async def student_info(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user = storage.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    info_text = (
        f"🧑‍🎓 Информация о вас:\n\n"
        f"▫️ <b>Фамилия:</b> {user.surname or 'не указана'}\n"
        f"▫️ <b>Имя:</b> {user.name or 'не указано'}\n"
        f"▫️ <b>Отчество:</b> {user.patronymic or 'не указано'}"
    )

    if hasattr(user, 'image') and user.image and user.image != 'static/img/default.png':
        try:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{user.image}"),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=kb.student_info
                )
                return
            except Exception as url_error:
                print(f"URL send failed, trying FSInputFile: {url_error}")
                await callback.message.answer_photo(
                    photo=FSInputFile(user.image),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=kb.student_info
                )
                return
        except Exception as e:
            print(f"Both photo sending methods failed: {e}")

    await callback.message.answer(
        info_text,
        parse_mode='HTML',
        reply_markup=kb.student_info
    )


async def handle_back_to_student_menu(message: Message, user_id):
    user = storage.get_user(user_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=kb.student_main
    )


@router.callback_query(F.data == "back_to_student_menu")
async def back_to_student_menu(callback: CallbackQuery, state: FSMContext):
    user = storage.get_user(callback.from_user.id)
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await callback.message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await callback.message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=kb.student_main
    )


@router.callback_query(F.data == 'student_courses')
async def show_student_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали просмотр ваших курсов')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user = storage.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Данные пользователя не найдены")
        return

    markup = await kb.inline_student_courses(id=user.id)
    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=markup
    )

    await state.set_state(StudentCourseStates.waiting_for_id)


@router.callback_query(StudentCourseStates.waiting_for_id)
async def handle_student_course_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        course_id = int(callback.data)
        course = get_course_by_id(course_id)

        if not course:
            await callback.message.answer("Курс не найден",
                                          reply_markup=kb.student_course_back_button)
            await state.clear()
            return

        message_text = (
            f"🧑‍🏫 Информация о курсе:\n\n"
            f"▫️ <b>Название:</b> {course.title}\n"
            f"▫️ <b>Описание:</b> {course.description}\n\n"
            f"▫️ <b>Занятия на курсе:</b>"
        )

        await callback.message.answer(message_text, parse_mode='HTML',
                                      reply_markup=await kb.inline_lessons_by_course(course_id))

        await state.clear()
        await state.set_state(StudentCourseStates.waiting_for_lesson_id)
    except Exception as e:
        print(f"Error: {e}")
        await callback.answer("❌ Произошла ошибка")
        await state.clear()


@router.callback_query(StudentCourseStates.waiting_for_lesson_id)
async def handle_student_course_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    lesson_id = int(callback.data)
    lesson = get_lesson_by_id(lesson_id)

    if lesson:
        message_text = (
            f"🧑‍🏫 Информация о занятие:\n\n"
            f"▫️ <b>Название:</b> {lesson.title}\n"
            f"▫️ <b>Тип:</b> {lesson.lesson_type}\n"
            f"▫️ <b>Описание:</b> {lesson.description}\n"
            f"▫️ <b>Дата:</b> {datetime.fromisoformat(lesson.date).strftime('%d.%m.%Y')}\n"
        )

        await callback.message.answer(message_text, parse_mode='HTML',
                                      reply_markup=kb.student_course_back_button)
    else:
        await callback.message.answer("Занятие не найдено",
                                      reply_markup=kb.student_course_back_button)

    await state.set_state(StudentCourseStates.viewing_lessons)


@router.callback_query(F.data == "back_to_student_courses_list", StudentCourseStates.viewing_course)
async def back_to_student_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = get_user_data(callback.from_user.id)

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(user_data["id"]))

    await state.set_state(StudentCourseStates.waiting_for_id)


@router.callback_query(F.data == "back_to_student_courses_list", StudentCourseStates.viewing_lessons)
async def back_to_student_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = storage.get_user(callback.from_user.id)

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(id=user_data.id))

    await state.clear()
    await state.set_state(StudentCourseStates.waiting_for_id)


@router.callback_query(F.data == "update_info")
async def start_editing(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    new_msg = await callback.message.answer(
        "Введите новую фамилию:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_surname)


@router.message(EditStudentStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
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
        "Теперь введите новое имя:",
        reply_markup=await kb.get_cancel_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_name)


@router.message(EditStudentStates.waiting_for_name)
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
        "Теперь введите новое отчество:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_patronymic)


@router.message(EditStudentStates.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
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

    user_id = message.from_user.id
    user = storage.get_user(message.from_user.id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_student_menu(message, user_id)
        return

    user_id = user.id
    user_pass = storage.get_credentials(message.from_user.id)
    user_data = await state.get_data()

    update = update_user_data(
        id=user_id,
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        password=user_pass.password
    )

    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_student_menu(message, user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_student_menu(message, user_id)


@router.callback_query(F.data == "cancel_edit")
async def cancel_editing(callback: CallbackQuery, state: FSMContext):
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
    await back_to_student_menu(callback, state)


@router.callback_query(F.data == "drive_schedules")
async def show_drive_schedules(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        'Выберите инструктора у которого хотите посмотреть расписание:',
        reply_markup=await kb.inline_schedules()
    )
    await state.set_state(ScheduleStates.waiting_for_id)


@router.callback_query(ScheduleStates.waiting_for_id)
async def handle_schedule_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "cancel_schedule":
        await cancel_schedule_selection(callback, state)
        return

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        schedule_id = int(callback.data)
        schedule = get_drive_schedule_by_id(schedule_id)

        if not schedule:
            await callback.message.answer("🕒 Расписание не найдено")
            await state.clear()
            return

        autodrome = get_autodrome_by_id(schedule.autodrome_id)
        category = get_category_by_id(schedule.category_id)
        instructor = get_instructor_by_id(schedule.instructor_id)

        days = ', '.join(schedule.days_of_week) if isinstance(schedule.days_of_week, list) else schedule.days_of_week

        response = (
            "📅 Информация о расписании:\n\n"
            f"⏱ Время: {datetime.fromisoformat(schedule.time_from).strftime('%H:%M')} - "
            f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}\n\n"
            f"📆 Дни: {days}\n\n"
            f"🏁 Автодром: {autodrome.title}\n\n"
            f"📋 Категория: {category.title}\n\n"
            f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
        )

        if schedule.notice:
            response += f"📝 Примечание: {schedule.notice}\n"

        await callback.message.answer(
            response,
            parse_mode="HTML",
            reply_markup=await kb.instructor_schedule(
                instructor_id=schedule.instructor_id,
                autodrome_id=schedule.autodrome_id,
                category_id=schedule.category_id,
                time_from=f"{datetime.fromisoformat(schedule.time_from).strftime('%H:%M')}",
                time_to=f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}",
                days=f"{days}"
            )
        )

    except (ValueError, AttributeError) as e:
        print(f"Error processing schedule: {e}")
        await callback.message.answer("❌ Ошибка обработки запроса")
    finally:
        await state.clear()


@router.callback_query(F.data == "cancel_schedule")
async def cancel_schedule_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = storage.get_user(callback.from_user.id)
    if not user_data:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await state.clear()
    await callback.message.answer(
        f'Привет, {user_data.surname} {user_data.name}, Ваша роль Студент',
        reply_markup=kb.student_main)


@router.callback_query(F.data.startswith("sign_up_"))
async def handle_sign_up(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        parts = callback.data[7:].split('_')
        if len(parts) != 7:
            raise ValueError("Неверный формат callback_data")

        await state.update_data(
            sign_up_instructor_id=int(parts[1]),
            sign_up_autodrome_id=int(parts[2]),
            sign_up_category_id=int(parts[3]),
            sign_up_time_from=parts[4],
            sign_up_time_to=parts[5],
            sign_up_days=parts[6]
        )

        await callback.message.answer(
            "Выберите дату для записи:",
            reply_markup=await RussianSimpleCalendar().start_calendar(allowed_days=parts[6])
        )
    except Exception as e:
        print(f"Error processing sign up: {e}")
        await callback.answer("❌ Ошибка при обработке записи", show_alert=True)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    try:
        act = callback_data.act
        year = callback_data.year
        month = callback_data.month

        new_year = year
        new_month = month

        state_data = await state.get_data()
        allowed_days = state_data.get('sign_up_days')

        if act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            if act == "PREV-YEAR":
                new_year = year - 1
                new_month = month
            elif act == "NEXT-YEAR":
                new_year = year + 1
                new_month = month
            elif act == "PREV-MONTH":
                new_year = year
                new_month = month - 1
                if month == 1:
                    new_month = 12
                    new_year = year - 1
            elif act == "NEXT-MONTH":
                new_year = year
                new_month = month + 1
                if month == 12:
                    new_month = 1
                    new_year = year + 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month,
                    allowed_days=allowed_days
                )
            )
            return

        if act == "CANCEL":
            await cancel_schedule_selection(callback, state)
            return

        if act == "DAY":
            selected_date = datetime(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            await state.update_data(selected_date=selected_date.strftime('%Y-%m-%d'))
            data = await state.get_data()

            await callback.message.answer(
                f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}",
                reply_markup=kb.generate_time_keyboard(
                    data.get('sign_up_time_from'),
                    data.get('sign_up_time_to')
                )
            )
            return

        await callback.answer("Неизвестное действие с календарем", show_alert=True)

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@router.callback_query(F.data == "back_to_calendar")
async def back_to_calendar(callback: CallbackQuery, state: FSMContext):
    await back_to_student_menu(callback, state)


@router.callback_query(F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    time_str = callback.data.split('_')[1]
    data = await state.get_data()
    date_str = data.get('selected_date')
    full_datetime = f"{date_str} {time_str}"
    user_id = callback.from_user.id

    user_pass = storage.get_credentials(callback.from_user.id)
    if not user_pass:
        await callback.message.answer("❌ Данные пользователя не найдены")
        await state.clear()
        return

    await state.update_data(
        booking_datetime=full_datetime,
        booking_time_str=time_str,
        user_password=user_pass.password
    )

    try:
        result = post_instructor_lesson(
            user_id=callback.from_user.id,
            instructor_id=data.get('sign_up_instructor_id'),
            autodrome_id=data.get('sign_up_autodrome_id'),
            category_id=data.get('sign_up_category_id'),
            date_time=full_datetime,
            password=user_pass.password
        )

        if result == 201:
            instructor = get_instructor_by_id(data['sign_up_instructor_id'])
            autodrome = get_autodrome_by_id(data['sign_up_autodrome_id'])
            category = get_category_by_id(data['sign_up_category_id'])

            msg = await callback.message.answer(
                f"✅ Вы записаны на:\n"
                f"Дата и время: {full_datetime}\n"
                f"Инструктор: {instructor.surname} {instructor.name}\n"
                f"Автодром: {autodrome.title}\n"
                f"Категория: {category.title}"
            )
        else:
            msg = await callback.message.answer("❌ Ошибка при записи")

        await asyncio.sleep(2)
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass

    except Exception as e:
        print(f"Error processing booking: {e}")
        await callback.message.answer("❌ Произошла ошибка при обработке записи")
    finally:
        await state.clear()
        await handle_back_to_student_menu(callback.message, user_id)


@router.callback_query(F.data == "my_schedules")
async def check_my_schedules(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    credentials = storage.get_credentials(callback.from_user.id)
    if not credentials or not credentials.user:
        await callback.answer("Данные пользователя не найдены")
        return

    user = credentials.user
    await callback.message.answer(
        "Вот ваши ближайшие занятия:",
        reply_markup=await kb.inline_my_schedule(
            student_id=user.id,
            email=user.email,
            user_password=credentials.password
        )
    )
    await state.set_state(MyScheduleStates.waiting_for_id)


@router.message(MyScheduleStates.waiting_for_id)
async def handle_my_schedule_id(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
