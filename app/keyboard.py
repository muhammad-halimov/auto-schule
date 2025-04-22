from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder
from app.APIhandler import instructors, teachers, cars, courses

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🪪 Авторизироваться', callback_data='auth')],
    [InlineKeyboardButton(text='ℹ️ Посмотреть информацию об автошколе', callback_data='info')],
    [InlineKeyboardButton(text='📝 Подать заявку на обучение', callback_data='request')]
    ])

info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📋 Категории вождения', callback_data='catalog')],
    [InlineKeyboardButton(text='👨‍🏫 Инструктора', callback_data='instructors')],
    [InlineKeyboardButton(text='👨‍🏫 Учителя', callback_data='teachers')],
    [InlineKeyboardButton(text='🚗 Автомобили', callback_data='cars')],
    [InlineKeyboardButton(text='📚 Курсы', callback_data='courses')],
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
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 ФИО: {instructor.surname} {instructor.name} {instructor.patronymic}, '
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
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 ФИО: {teacher.surname} {teacher.name} {teacher.patronymic}, '
                                                   f'📱 Телефон: {teacher.phone}',
                                              callback_data=f'{teacher.id}'))
            added_teachers.add(teacher_key)

    return keyboard.adjust(1).as_markup()


async def inline_cars():
    keyboard = InlineKeyboardBuilder()
    added_cars = set()
    for car in cars():
        car_key = f"{car.id}"

        if car_key not in added_cars:
            keyboard.add(InlineKeyboardButton(text=f'🚗 Автомобиль: {car.carMark} {car.carModel} {car.stateNumber}, '
                                                   f'📅 Дата производства: {car.productionYear}',
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
