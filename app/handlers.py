from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile
from app.APIhandler import get_instructor_by_id, get_teacher_by_id, get_car_by_id
from datetime import datetime
from config import profile_photos

import app.keyboard as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет, {message.from_user.full_name}'
                        f', вы зашли в официального телеграм бота автошколы "Супер", с чего бы вы хотели начать?',
                        reply_markup=kb.main)


@router.callback_query(F.data == 'auth')
async def auth(callback: CallbackQuery):
    await callback.answer('Введите ваш пароль')
    await callback.message.answer('Введите ваш пароль')


@router.callback_query(F.data == 'info')
async def auth(callback: CallbackQuery):
    await callback.answer('Вы выбрали просморт информации')
    await callback.message.answer('Что бы вы хотели узнать о нашей автошколе?',
                                  reply_markup=kb.info)


class RequestStates(StatesGroup):
    waiting_for_data = State()


class InstructorStates(StatesGroup):
    waiting_for_id = State()


class TeacherStates(StatesGroup):
    waiting_for_id = State()


class CarStates(StatesGroup):
    waiting_for_id = State()


class CourseStates(StatesGroup):
    waiting_for_id = State()


requests_storage = []


@router.callback_query(F.data == 'request')
async def request(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали подать заявку')
    await callback.message.answer(
        'Введите ваши данные в следующем формате:\n'
        'Имя Фамилия\n'
        'Номер телефона\n'
        'Желаемая категория (A, B, C или D)\n\n'
        'Пример:\n'
        'Иван Иванов\n'
        '+79123456789\n'
        'B'
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
            reply_markup=kb.main
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
    await callback.message.answer('Вот инструктора вождения которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=await kb.inline_instructors())
    await state.set_state(InstructorStates.waiting_for_id)


@router.callback_query(F.data == 'teachers')
async def request_teachers(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали учителей')
    await callback.message.answer('Вот учителя которые есть в нашей автошколе, '
                                  'нажмите на любого для просмотра информации о нем',
                                  reply_markup=await kb.inline_teachers())
    await state.set_state(TeacherStates.waiting_for_id)


@router.callback_query(F.data == 'cars')
async def request_cars(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали автомобили')
    await callback.message.answer('Вот автомобили которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о ней',
                                  reply_markup=await kb.inline_cars())
    await state.set_state(CarStates.waiting_for_id)


@router.callback_query(F.data == 'courses')
async def request_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали курсы')
    await callback.message.answer('Вот курсы которые есть в нашей автошколе, '
                                  'нажмите на любой для просмотра информации о нем',
                                  reply_markup=await kb.inline_courses())
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


@router.callback_query(InstructorStates.waiting_for_id)
async def handle_instructor_id(callback: CallbackQuery, state: FSMContext):
    instructor_id = int(callback.data)
    instructor = get_instructor_by_id(instructor_id)

    if instructor:
        message_text = (
            f"🧑‍🏫 Информация об инструкторе:\n\n"
            f"▫️ <b>ФИО:</b> {instructor.surname} {instructor.name} {instructor.patronymic}\n"
            f"▫️ <b>Телефон:</b> {instructor.phone}\n"
            f"▫️ <b>Email:</b> {instructor.email}\n"
            f"▫️ <b>Дата рождения:</b> {datetime.fromisoformat(instructor.dateOfBirth).strftime("%d.%m.%Y")}\n"
            f"▫️ <b>Водительское удостоверение:</b> {instructor.license}\n"
            f"▫️ <b>Дата приема на работу:</b> {datetime.fromisoformat(instructor.hireDate).strftime("%d.%m.%Y")}"
        )
        if hasattr(instructor, 'image') and instructor.image:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{instructor.image}"),
                    caption=message_text,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML'
                )

        await callback.message.answer(message_text, parse_mode='HTML')
    else:
        await callback.message.answer("Инструктор не найден")

    await state.clear()


@router.callback_query(TeacherStates.waiting_for_id)
async def handle_teacher_id(callback: CallbackQuery, state: FSMContext):
    teacher_id = int(callback.data)
    teacher = get_teacher_by_id(teacher_id)
    if teacher:
        message_text = (
            f"🧑‍🏫 Информация об учителе:\n\n"
            f"▫️ <b>ФИО:</b> {teacher.surname} {teacher.name} {teacher.patronymic}\n"
            f"▫️ <b>Телефон:</b> {teacher.phone}\n"
            f"▫️ <b>Email:</b> {teacher.email}\n"
            f"▫️ <b>Дата рождения:</b> {datetime.fromisoformat(teacher.dateOfBirth).strftime("%d.%m.%Y")}\n"
            f"▫️ <b>Дата приема на работу:</b> {datetime.fromisoformat(teacher.hireDate).strftime("%d.%m.%Y")}"
        )
        if hasattr(teacher, 'image') and teacher.image:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{teacher.image}"),
                    caption=message_text,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await callback.message.answer_photo(
                    photo=FSInputFile("static/img/default.jpg"),
                    caption=message_text,
                    parse_mode='HTML'
                )
        else:
            await callback.message.answer(message_text, parse_mode='HTML')
    else:
        await callback.message.answer("Учитель не найден")

    await state.clear()


@router.callback_query(CarStates.waiting_for_id)
async def handle_car_id(callback: CallbackQuery, state: FSMContext):
    car_id = int(callback.data)
    car = get_car_by_id(car_id)

    if car:
        message_text = (
            f"🧑‍🏫 Информация об автомобиле:\n\n"
            f"▫️ <b>Авто:</b> {car.carMark} {car.carModel} {car.stateNumber}\n"
            f"▫️ <b>Вин номер:</b> {car.vinNumber}\n"
            f"▫️ <b>Дата производства:</b> {datetime.fromisoformat(car.productionYear).strftime("%d.%m.%Y")}"
        )

        await callback.message.answer(message_text, parse_mode='HTML')
    else:
        await callback.message.answer("Автомобиль не найден")

    await state.clear()
