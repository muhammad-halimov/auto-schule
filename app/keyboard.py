from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.APIhandler import instructors, teachers, cars, courses, student_courses

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚀 Начать работу")]],
    resize_keyboard=True,
    input_field_placeholder="Нажмите кнопку ниже"
)

guest_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Посмотреть информацию об автошколе', callback_data='info')],
    [InlineKeyboardButton(text='📝 Подать заявку на обучение', callback_data='request')]
    ])

student_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='student_info')],
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='student_courses')]
    ])

teacher_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='teacher_info')],
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='student_courses')],
    [InlineKeyboardButton(text='📝 Мои занятия', callback_data='teacher_lessons')]
    ])

instructor_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='instructor_info')],
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='student_courses')]
    ])

admin_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='instructor_info')],
    [InlineKeyboardButton(text='👨‍🏫 Список пользователей', callback_data='users_list')],
    [InlineKeyboardButton(text='📚 Список курсов', callback_data='courses_list')],
    [InlineKeyboardButton(text='🚗 Список авто', callback_data='auto_list')]
    ])

info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📋 Категории вождения', callback_data='catalog')],
    [InlineKeyboardButton(text='👨‍🏫 Инструктора', callback_data='instructors')],
    [InlineKeyboardButton(text='👨‍🏫 Учителя', callback_data='teachers')],
    [InlineKeyboardButton(text='🚗 Автомобили', callback_data='cars')],
    [InlineKeyboardButton(text='📚 Курсы', callback_data='courses')],
    [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_main_menu')]
])

password = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔢 Создать пароль', callback_data='catalog')]
])

categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='A', callback_data='A')],
    [InlineKeyboardButton(text='B', callback_data='B')],
    [InlineKeyboardButton(text='C', callback_data='C')],
    [InlineKeyboardButton(text='D', callback_data='D')]
])


async def inline_instructors():
    keyboard = InlineKeyboardBuilder()
    added_instructors = set()
    for instructor in instructors():
        instructor_key = f"{instructor.id}"

        if instructor_key not in added_instructors:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 ФИО: {instructor.surname} {instructor.name} '
                                                   f'{instructor.patronymic}, '
                                                   f'📱 Телефон: {instructor.phone}',
                                              callback_data=f'{instructor.id}'))
            added_instructors.add(instructor_key)

    return keyboard.adjust(1).as_markup()


async def inline_teachers():
    keyboard = InlineKeyboardBuilder()
    added_teachers = set()
    for teacher in teachers():
        teacher_key = f"{teacher.id}"

        if teacher_key not in added_teachers:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 ФИО: {teacher.surname} {teacher.name} {teacher.patronymic}',
                                              callback_data=f'{teacher.id}'))
            added_teachers.add(teacher_key)

    return keyboard.adjust(1).as_markup()


async def inline_cars():
    keyboard = InlineKeyboardBuilder()
    added_cars = set()
    for car in cars():
        car_key = f"{car.id}"

        if car_key not in added_cars:
            keyboard.add(InlineKeyboardButton(text=f'🚗 Автомобиль: {car.carMark} {car.carModel} {car.stateNumber}',
                                              callback_data=f'{car.id}'))
            added_cars.add(car_key)

    return keyboard.adjust(1).as_markup()


async def inline_courses():
    keyboard = InlineKeyboardBuilder()
    added_courses = set()
    for course in courses():
        course_key = f"{course.id}"

        if course_key not in added_courses:
            keyboard.add(InlineKeyboardButton(text=f'📚 Курс: {course.title}, '
                                                   f'📝 Описание: {course.description}',
                                              callback_data=f'{course.id}'))
            added_courses.add(course_key)

    return keyboard.adjust(1).as_markup()


async def inline_student_courses(telegram_id):
    keyboard = InlineKeyboardBuilder()
    s_courses = student_courses(telegram_id)

    if not s_courses:
        keyboard.button(
            text="❌ Нет доступных курсов",
            callback_data="no_courses"
        )
    else:
        for course in s_courses:
            keyboard.button(
                text=f"📚 {course.title[:30]}",
                callback_data=f"course_{course.id}"
            )

    keyboard.button(
        text="◀️ Назад",
        callback_data="back_to_student_menu"
    )

    return keyboard.adjust(1).as_markup()


instructor_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_instructors_list")]])


car_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_cars_list")]])


teacher_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_teachers_list")]])


course_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_courses_list")]])

info_back_button = [InlineKeyboardButton(text='◀️ Назад к информации', callback_data='back_to_info')]

back_to_student_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_student_menu')]])

back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_main_menu')]])
