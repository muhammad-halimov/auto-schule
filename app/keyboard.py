from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.APIhandler import (instructors, teachers, cars, courses, student_courses, get_course_by_id, drive_schedules,
                            categories, my_schedules, check_time_lessons)

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
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='student_courses')],
    [InlineKeyboardButton(text='📅 Расписания инструкторов', callback_data='drive_schedules')],
    [InlineKeyboardButton(text='📅 Мое расписание', callback_data='my_schedules')]
    ])

teacher_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='teacher_info')],
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='courses')],
    [InlineKeyboardButton(text='📝 Мои занятия', callback_data='teacher_lessons')]
    ])

instructor_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='instructor_info')],
    [InlineKeyboardButton(text='📝 Мои курсы', callback_data='instructor_my_schedules')]
    ])

admin_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ Мой профиль', callback_data='admin_info')],
    [InlineKeyboardButton(text='👨‍🏫 Список пользователей', callback_data='users_list')],
    [InlineKeyboardButton(text='📚 Список курсов', callback_data='courses_list')],
    [InlineKeyboardButton(text='📅 Список расписаний', callback_data='schedules_list')],
    [InlineKeyboardButton(text='🚗 Список авто', callback_data='auto_list')]
    ])

student_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Редактирвать свою информацию', callback_data='update_info')],
    [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_student_menu')]
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


async def inline_categories():
    keyboard = InlineKeyboardBuilder()
    added_categories = set()
    for category in categories():
        category_key = f"{category.id}"

        if category_key not in added_categories:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 Категория: {category.title}',
                                              callback_data=f'category_{category.id}_{category.title}'))
            added_categories.add(category_key)

    return keyboard.adjust(1).as_markup()


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


async def inline_student_courses(id):
    keyboard = InlineKeyboardBuilder()
    s_courses = student_courses(id)

    if not s_courses:
        keyboard.button(
            text="❌ Нет доступных курсов",
            callback_data="no_courses"
        )
    else:
        for course in s_courses:
            keyboard.button(
                text=f"📚 {course.title[:30]}",
                callback_data=f"{course.id}"
            )

    keyboard.button(
        text="◀️ Назад",
        callback_data="back_to_student_menu"
    )

    return keyboard.adjust(1).as_markup()


async def inline_lessons_by_course(course_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    course = get_course_by_id(course_id)
    if not course or not hasattr(course, 'lessons'):
        builder.button(
            text="❌ Уроки не найдены",
            callback_data="no_lessons"
        )
    else:
        for lesson in course.lessons:
            if isinstance(lesson, dict):
                builder.button(
                    text=f"📝 {lesson.get('title', 'Без названия')[:30]}",
                    callback_data=f"{lesson.get('id')}"
                )
            else:
                builder.button(
                    text=f"📝 {getattr(lesson, 'title', 'Без названия')[:30]}",
                    callback_data=f"{getattr(lesson, 'id', 0)}"
                )

    builder.button(
        text="◀️ Назад к курсам",
        callback_data="student_courses"
    )

    builder.adjust(1)

    return builder.as_markup()


async def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить редактирование", callback_data="cancel_edit")
    return builder.as_markup()


async def inline_schedules() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    schedules = drive_schedules()
    instructors_list = {i.id: i for i in instructors()}

    if not schedules:
        builder.button(
            text="❌ Расписания отсутствуют",
            callback_data="no_schedules"
        )
    else:
        unique_instructors = {s.instructor_id for s in schedules}

        instructor_names = {
            i_id: f"{instructors_list[i_id].surname} {instructors_list[i_id].name} {instructors_list[i_id].patronymic}"
            for i_id in unique_instructors if i_id in instructors_list
        }

        added_ids = set()
        for schedule in schedules:
            if schedule.id not in added_ids:
                instructor_name = instructor_names.get(schedule.instructor_id, "Неизвестный инструктор")
                builder.button(
                    text=f"📚 Инструктор: {instructor_name[:30]}",
                    callback_data=f"{schedule.id}"
                )
                added_ids.add(schedule.id)

    builder.button(
        text="◀️ Назад в меню",
        callback_data="cancel_schedule"
    )
    builder.adjust(1)

    return builder.as_markup()


async def instructor_schedule(instructor_id: int, autodrome_id: int, category_id: int, time_from: str, time_to: str,
                              days):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="📅 Записаться",
            callback_data=f"sign_up_{instructor_id}_{autodrome_id}_{category_id}_{time_from}_{time_to}_{days}"
        ),
        InlineKeyboardButton(
            text="◀️ Назад к расписанию",
            callback_data="drive_schedules"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def generate_time_keyboard(instructor_id, selected_date, email, user_password, time_from, time_to):
    taked_time = check_time_lessons(instructor_id=instructor_id, date=selected_date, email=email, password=user_password)
    if taked_time is None:
        taked_time = []

    builder = InlineKeyboardBuilder()
    for hour in range(int(time_from[:2]), int(time_to[:2])):
        for minute in ['00', '30']:
            time_str = f"{hour:02d}:{minute}"
            if time_str not in taked_time:
                builder.button(
                    text=time_str,
                    callback_data=f"time_{time_str}"
                )
    builder.button(text="◀️ Назад к датам", callback_data="back_to_calendar")
    builder.adjust(4)
    return builder.as_markup()


async def inline_my_schedule(student_id: int, email: str, user_password: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    lessons = my_schedules(student_id, email, user_password)

    if not lessons or lessons == 0:
        builder.button(
            text="Нет запланированных занятий",
            callback_data="no_lessons"
        )
    else:
        lessons_sorted = sorted(lessons, key=lambda x: x.date)
        for lesson in lessons_sorted[:5]:
            lesson_time = lesson.date.split(' ')[1][:5] if isinstance(lesson.date, str) else ''
            instructor_name = f"{lesson.instructor.get('surname', '')} {lesson.instructor.get('name', '')[:1]}."
            text = f"{lesson_time} - {instructor_name} ({lesson.autodrome.get('title', '')})"

            builder.button(
                text=text[:64],
                callback_data=f"{lesson.id}"
            )

    builder.button(
        text="◀️ Назад",
        callback_data="back_to_student_menu"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_my_lesson_keyboard(schedule_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="❌ Отменить запись",
                callback_data=f"cancel_lesson_{schedule_id}"
            )],
            [InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="my_schedules"
            )]
        ]
    )


instructor_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_instructors_list")]])


car_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_cars_list")]])


teacher_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_teachers_list")]])


course_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_courses_list")]])

student_course_back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Вернуться к списку", callback_data="back_to_student_courses_list")]])

info_back_button = [InlineKeyboardButton(text='◀️ Назад к информации', callback_data='back_to_info')]

back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_main_menu')]])

back_to_student_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='back_to_student_menu')]])

back_to_my_schedules_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='◀️ Назад к меню', callback_data='my_schedules')]])

agreement = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Согласен на обработку персональных данных', callback_data='agree')]])
