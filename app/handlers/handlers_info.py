from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, FSInputFile, URLInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

import app.keyboards.static_keyboard as static_kb
import app.keyboards.keyboard as kb
from app.APIhandlers.APIhandlersCar import get_car_by_id
from app.APIhandlers.APIhandlersCategory import get_category_by_id
from app.APIhandlers.APIhandlersCourse import get_course_by_id
from app.APIhandlers.APIhandlersInstructor import get_instructor_by_id
from app.APIhandlers.APIhandlersTeacher import get_teacher_by_id
from app.handlers.handlers import CourseStates, CarStates, TeacherStates, InstructorStates, CategoryStates
from app.handlers.handlers_student import show_student_courses
from config_local import profile_photos

info_router = Router()


@info_router.callback_query(F.data == 'info')
async def info(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали просмотр информации')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await state.clear()

    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=static_kb.info)


@info_router.callback_query(F.data == 'back_to_info')
async def back_to_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await info(callback, state)


@info_router.callback_query(F.data == 'catalog')
async def request(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    categories_kb = await kb.inline_categories()

    categories_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.answer('Вы выбрали категории')
    await callback.message.answer('Вот категории вождения которые есть в нашей автошколе,'
                                  ' нажмите на любую категорию для просмотра информации о ней',
                                  reply_markup=categories_kb)

    await state.set_state(CategoryStates.waiting_for_id)


@info_router.callback_query(CategoryStates.waiting_for_id)
async def request_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = callback.data.split('_')[1]
    category_info = get_category_by_id(category_id=int(category_id))

    await callback.message.answer(text=f"🧑‍🏫 Информация о категории:\n\n"
                                  f"▫️ <b>Название:</b> {category_info.title}\n"
                                  f"▫️ <b>Описание:</b> {category_info.description}\n",
                                  parse_mode="HTML",
                                  reply_markup=static_kb.category_back_button)

    await state.clear()


@info_router.callback_query(F.data == 'instructors')
async def request_instructors(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали инструкторов')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructors_kb = await kb.inline_instructors()

    instructors_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=instructors_kb)
    await state.set_state(InstructorStates.waiting_for_id)


@info_router.callback_query(F.data == 'teachers')
async def request_teachers(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали учителей')
    await callback.message.delete()

    teachers_kb = await kb.inline_teachers()

    teachers_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer('Вот учителя которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=teachers_kb)
    await state.set_state(TeacherStates.waiting_for_id)


@info_router.callback_query(F.data == 'cars')
async def request_cars(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали автомобили')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cars_kb = await kb.inline_cars()

    cars_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer('Вот автомобили которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о ней',
                                  reply_markup=cars_kb)
    await state.set_state(CarStates.waiting_for_id)


@info_router.callback_query(F.data == 'courses')
async def request_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали курсы')
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer('Вот курсы которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о нем',
                                  reply_markup=courses_kb)
    await state.set_state(CourseStates.waiting_for_id)


@info_router.callback_query(
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


@info_router.callback_query(InstructorStates.waiting_for_id)
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
            f"▫️ <b>Стаж вождения:</b> {instructor.experience}\n"
        )
        if hasattr(instructor, 'image') and instructor.image:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{instructor.image}"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.instructor_back_button
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.instructor_back_button)
        else:
            await callback.message.answer_photo(
                photo=FSInputFile("static/img/default.jpg"),
                caption=message_text,
                parse_mode='HTML',
                reply_markup=static_kb.instructor_back_button)
    else:
        await callback.message.answer("Инструктор не найден",
                                      reply_markup=static_kb.instructor_back_button)

    await state.set_state(InstructorStates.viewing_instructor)


@info_router.callback_query(F.data == "back_to_instructors_list", InstructorStates.viewing_instructor)
async def back_to_instructors_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructors_kb = await kb.inline_instructors()

    instructors_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=instructors_kb)

    await state.set_state(InstructorStates.waiting_for_id)


# TEACHERS

@info_router.callback_query(TeacherStates.waiting_for_id)
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
                    reply_markup=static_kb.teacher_back_button
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.teacher_back_button
                )
        else:
            await callback.message.answer_photo(
                photo=FSInputFile("static/img/default.jpg"),
                caption=message_text,
                parse_mode='HTML',
                reply_markup=static_kb.teacher_back_button)
    else:
        await callback.message.answer("Учитель не найден",
                                      reply_markup=static_kb.teacher_back_button)

    await state.set_state(TeacherStates.viewing_teacher)


@info_router.callback_query(F.data == "back_to_teachers_list", TeacherStates.viewing_teacher)
async def back_to_teachers_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    teachers_kb = await kb.inline_teachers()

    teachers_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer(
        'Вот учителя которые есть в нашей автошколе, '
        'нажмите на любого для просмотра информации о нем',
        reply_markup=teachers_kb)

    await state.set_state(TeacherStates.waiting_for_id)


# CARS

@info_router.callback_query(CarStates.waiting_for_id)
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
            f"▫️ <b>Марка:</b> {car.carMark}\n"
            f"▫️ <b>Модель:</b> {car.carModel}\n"
            f"▫️ <b>Номер:</b> {car.stateNumber}\n"
        )

        await callback.message.answer(message_text,
                                      parse_mode='HTML',
                                      reply_markup=static_kb.car_back_button)
    else:
        await callback.message.answer("Автомобиль не найден",
                                      reply_markup=static_kb.car_back_button)

    await state.set_state(CarStates.viewing_car)


@info_router.callback_query(F.data == "back_to_cars_list", CarStates.viewing_car)
async def back_to_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cars_kb = await kb.inline_cars()

    cars_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer(
        'Вот автомобили которые есть в нашей автошколе, '
        'нажмите на любой для просмотра информации о ней',
        reply_markup=cars_kb)

    await state.set_state(CarStates.waiting_for_id)


# COURSES

@info_router.callback_query(CourseStates.waiting_for_id)
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
                                      reply_markup=static_kb.course_back_button)
    else:
        await callback.message.answer("Курс не найден",
                                      reply_markup=static_kb.course_back_button)

    await state.set_state(CourseStates.viewing_course)


@info_router.callback_query(F.data == "back_to_courses_list", CourseStates.viewing_course)
async def back_to_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(static_kb.info_back_button)

    await callback.message.answer(
        'Вот курсы которые есть в нашей автошколе, '
        'нажмите на любой для просмотра информации о нем',
        reply_markup=courses_kb)

    await state.set_state(CourseStates.waiting_for_id)
