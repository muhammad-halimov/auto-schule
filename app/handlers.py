import asyncio
import logging
from datetime import datetime, timezone

from aiogram_calendar import SimpleCalendar
from aiogram_calendar.schemas import SimpleCalendarCallback
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile, BotCommand, ReplyKeyboardRemove
from app.APIhandler import (get_instructor_by_id, get_teacher_by_id, get_car_by_id, get_course_by_id,
                            user_is_authorized, get_lesson_by_id, update_user_data, get_drive_schedule_by_id,
                            get_category_by_id, get_autodrome_by_id, post_instructor_lesson)
from config_local import profile_photos

import app.keyboard as kb

router = Router()


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Запустить бота')
    ]
    await bot.set_my_commands(main_menu_commands)


async def on_startup(bot: Bot):
    await set_main_menu(bot)


@router.message(CommandStart())
async def cmd_start(message: Message):
    if user_is_authorized(message.from_user.id) == 0:
        await message.reply(f'Привет, {message.from_user.full_name}'
                            f', вы зашли в официального телеграм бота автошколы "endeavor", я вижу что вы новичок'
                            f' с чего бы вы хотели начать?',
                            reply_markup=kb.guest_main)
    else:

        user = user_is_authorized(message.from_user.id)

        role = user.roles[0]

        if role == "ROLE_STUDENT":
            await message.reply(f'Привет, {user.surname} {user.name}'
                                f', Ваша роль Студент',
                                reply_markup=kb.student_main)
        elif role == "ROLE_TEACHER":
            await message.reply(f'Привет, {user.surname} {user.name}'
                                f', Ваша роль Учитель',
                                reply_markup=kb.teacher_main)
        elif role == "ROLE_INSTRUCTOR":
            await message.reply(f'Привет, {user.surname} {user.name}'
                                f', Ваша роль Инструктор',
                                reply_markup=kb.instructor_main)
        elif role == "ROLE_ADMIN":
            await message.reply(f'Привет, {user.surname} {user.name}'
                                f', Ваша роль Админ',
                                reply_markup=kb.admin_main)


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
    waiting_for_data = State()


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


requests_storage = []


@router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        'Введите ваши данные в следующем формате:\n'
        'Имя Фамилия\n'
        'Номер телефона\n'
        'Желаемая категория (A, B, C или D)\n\n'
        'Пример:\n'
        'Иван Иванов\n'
        '+79123456789\n'
        'B',
        reply_markup=kb.back_to_main_menu
    )
    await state.set_state(RequestStates.waiting_for_data)


@router.message(RequestStates.waiting_for_data)
async def process_request_data(message: Message, state: FSMContext):
    try:
        data = message.text.split('\n')
        if len(data) != 3:
            raise ValueError("Неверный формат данных")

        name = data[0].strip()
        phone = data[1].strip()
        category = data[2].strip().upper()

        if category not in ['A', 'B', 'C', 'D', 'В', 'А', 'С']:
            raise ValueError("Неверная категория")

        requests_storage.append({
            'user_id': message.from_user.id,
            'name': name,
            'phone': phone,
            'category': category,
            'timestamp': message.date
        })

        await message.answer(
            f"✅ Ваша заявка принята!\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Категория: {category}\n\n"
            f"Мы свяжемся с вами в ближайшее время.",
            reply_markup=kb.guest_main
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка в формате данных. Пожалуйста, введите данные еще раз в правильном формате.\n"
            f"Ошибка: {str(e)}"
        )
    finally:
        await state.clear()


@router.callback_query(F.data == 'catalog')
async def request(callback: CallbackQuery):
    await callback.answer('Вы выбрали категории')
    await callback.message.answer('Вот категории вождения которые есть в нашей автошколе,'
                                  ' нажмите на любую категорию для просмотра информации о ней',
                                  reply_markup=kb.categories)


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

    user = user_is_authorized(callback.from_user.id)

    await callback.message.answer(f"🧑‍🏫 Информация о вас:\n\n"
                                  f"▫️ <b>Фамилия:</b> {user.surname}\n"
                                  f"▫️ <b>Имя:</b> {user.name}\n"
                                  f"▫️ <b>Отчество:</b> {user.patronymic}",
                                  parse_mode='HTML',
                                  reply_markup=kb.student_info)


@router.callback_query(F.data == "back_to_student_menu")
async def handle_back_to_student_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user = user_is_authorized(callback.from_user.id)

    await back_to_student_menu(callback.message, user)


@router.callback_query(F.data == 'student_courses')
async def show_student_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали просмотр ваших курсов')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    markup = await kb.inline_student_courses(callback.from_user.id)
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

    except ValueError:
        await callback.answer("❌ Некорректный ID курса")
        await state.clear()
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

    telegram_id = callback.from_user.id

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(telegram_id=telegram_id))

    await state.set_state(StudentCourseStates.waiting_for_id)


@router.callback_query(F.data == "back_to_student_courses_list", StudentCourseStates.viewing_lessons)
async def back_to_student_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    telegram_id = callback.from_user.id

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(telegram_id=telegram_id))

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


@router.message(EditStudentStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['last_bot_msg'])
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    user_data = await state.get_data()
    update = update_user_data(
        user_id=message.from_user.id,
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        password=message.text
    )

    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")
        await result_msg.delete()
        await state.clear()
        await back_to_student_menu(message, user_is_authorized(message.from_user.id))
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await result_msg.delete()


async def back_to_student_menu(message: Message, user):
    await message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=kb.student_main
    )


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
    await student_info(callback)


@router.callback_query(F.data == "drive_schedules")
async def show_drive_schedules(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        'Выберите инструктора у которого хотите посмотреть расписание:',
        reply_markup=await kb.inline_schedules())
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
                time_to=f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}"
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

    user = user_is_authorized(callback.from_user.id)

    await state.clear()
    await callback.message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=kb.student_main)


@router.callback_query(F.data.startswith("sign_up_"))
async def handle_sign_up(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        parts = callback.data[7:].split('_')

        if len(parts) != 6:
            raise ValueError("Неверный формат callback_data")

        instructor_id = int(parts[1])
        autodrome_id = int(parts[2])
        category_id = int(parts[3])
        time_from = str(parts[4])
        time_to = str(parts[5])

        await state.update_data(
            sign_up_instructor_id=instructor_id,
            sign_up_autodrome_id=autodrome_id,
            sign_up_category_id=category_id,
            sign_up_time_from=time_from,
            sign_up_time_to=time_to
        )

        await callback.message.answer(
            "Выберите дату для записи:",
            reply_markup=await SimpleCalendar().start_calendar()
        )

    except Exception as e:
        print(f"Error processing sign up: {e}")
        await callback.answer("❌ Ошибка при обработке записи", show_alert=True)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        await state.update_data(selected_date=date.strftime('%Y-%m-%d'))

        data = await state.get_data()

        await callback.message.answer(
            "Выберите время:",
            reply_markup=kb.generate_time_keyboard(
                data.get('sign_up_time_from'),
                data.get('sign_up_time_to')
            )
        )


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

    await state.update_data(
        booking_datetime=full_datetime,
        booking_time_str=time_str
    )

    password_msg = await callback.message.answer(
        "🔒 Введите ваш пароль для подтверждения записи:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.update_data(password_msg_id=password_msg.message_id)
    await state.set_state(BookingStates.waiting_for_password)


@router.message(BookingStates.waiting_for_password, F.text)
async def process_booking_password(message: Message, state: FSMContext):
    try:
        await message.delete()

        data = await state.get_data()
        if 'password_msg_id' in data:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=data['password_msg_id']
                )
            except TelegramBadRequest:
                pass

        full_datetime = data['booking_datetime']
        instructor_id = data.get('sign_up_instructor_id')
        autodrome_id = data.get('sign_up_autodrome_id')
        category_id = data.get('sign_up_category_id')
        password = message.text

        instructor = get_instructor_by_id(instructor_id)
        autodrome = get_autodrome_by_id(autodrome_id)
        category = get_category_by_id(category_id)

        if post_instructor_lesson(
                user_id=message.from_user.id,
                instructor_id=instructor_id,
                autodrome_id=autodrome_id,
                category_id=category_id,
                date_time=full_datetime,
                password=password
        ) == 201:
            result_msg = await message.answer(
                f"✅ Вы записаны на:\n"
                f"Дата и время: {full_datetime}\n"
                f"Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n"
                f"Автодром: {autodrome.title}\n"
                f"Категория: {category.title}"
            )
        else:
            result_msg = await message.answer("❌ Запись не удалась. Проверьте правильность пароля.")

        await asyncio.sleep(3)
        await result_msg.delete()

    except Exception as e:
        print(f"Error processing booking: {e}")
        await message.answer("❌ Произошла ошибка при обработке записи")
        await asyncio.sleep(3)
        await message.delete()
    finally:
        await state.clear()
        await back_to_student_menu(message, user_is_authorized(message.from_user.id))
