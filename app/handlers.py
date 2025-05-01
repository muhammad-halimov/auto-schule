from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile, BotCommand
from app.APIhandler import get_instructor_by_id, get_teacher_by_id, get_car_by_id, get_course_by_id, user_is_authorized
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
                                reply_markup=kb.guest_main)
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

    await callback.message.delete()
    await state.clear()

    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=kb.info)


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_student_menu(callback: CallbackQuery):

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


requests_storage = []


@router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')

    await callback.message.delete()

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
    await callback.message.delete()

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
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

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
    await callback.message.delete()

    cars_kb = await kb.inline_cars()

    cars_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот автомобили которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о ней',
                                  reply_markup=cars_kb)
    await state.set_state(CarStates.waiting_for_id)


@router.callback_query(F.data == 'courses')
async def request_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали курсы')
    await callback.message.delete()

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот курсы которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о нем',
                                  reply_markup=courses_kb)
    await state.set_state(CourseStates.waiting_for_id)


@router.callback_query(
    F.data.in_(['instructors', 'teachers', 'cars', 'courses']),
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


# INSTRUCTORS


@router.callback_query(InstructorStates.waiting_for_id)
async def handle_instructor_id(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()

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

    await callback.message.delete()

    instructors_kb = await kb.inline_instructors()

    instructors_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=instructors_kb)

    await state.set_state(InstructorStates.waiting_for_id)


# TEACHERS

@router.callback_query(TeacherStates.waiting_for_id)
async def handle_teacher_id(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()

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

    await callback.message.delete()

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

    await callback.message.delete()

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

    await callback.message.delete()

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

    await callback.message.delete()

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

    await callback.message.delete()

    courses_kb = await kb.inline_courses()

    courses_kb.inline_keyboard.append(kb.info_back_button)

    await callback.message.answer(
        'Вот курсы которые есть в нашей автошколе, '
        'нажмите на любой для просмотра информации о нем',
        reply_markup=courses_kb)

    await state.set_state(CourseStates.waiting_for_id)


@router.callback_query(F.data == "student_info")
async def student_info(callback: CallbackQuery):

    await callback.message.delete()

    user = user_is_authorized(callback.from_user.id)

    await callback.message.answer(f"🧑‍🏫 Информация о вас:\n\n"
                                  f"▫️ <b>Фамилия:</b> {user.surname}\n"
                                  f"▫️ <b>Имя:</b> {user.name}\n"
                                  f"▫️ <b>Отчество:</b> {user.patronymic}",
                                  parse_mode='HTML',
                                  reply_markup=kb.back_to_student_menu)


@router.callback_query(F.data == "back_to_student_menu")
async def back_to_student_menu(callback: CallbackQuery):

    await callback.message.delete()

    user = user_is_authorized(callback.from_user.id)

    await callback.message.answer(f'Привет, {user.surname} {user.name}'
                                  f', Ваша роль Студент',
                                  reply_markup=kb.student_main)
