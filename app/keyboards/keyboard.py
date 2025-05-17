from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.APIhandlers.APIhandlersCar import cars
from app.APIhandlers.APIhandlersCategory import categories
from app.APIhandlers.APIhandlersCourse import courses, get_course_by_id, Test
from app.APIhandlers.APIhandlersInstructor import instructors
from app.APIhandlers.APIhandlersSchedule import drive_schedules
from app.APIhandlers.APIhandlersStudent import student_courses, check_time_lessons, my_schedules
from app.APIhandlers.APIhandlersTeacher import teachers


async def inline_categories():
    keyboard = InlineKeyboardBuilder()
    added_categories = set()
    for category in categories():
        category_key = f"{category.id}"

        if category_key not in added_categories:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 Категория: {category.title}',
                                              callback_data=f'category_{category.id}'))
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
        text="📝 Контрольный тест",
        callback_data=f"test_{course_id}"
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
    taked_time = check_time_lessons(instructor_id=instructor_id, date=selected_date, email=email,
                                    password=user_password)
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
            lesson_time = lesson.date if isinstance(lesson.date, str) else ''
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


async def get_videos_keyboard(video_urls: list, lesson_id: int):
    builder = InlineKeyboardBuilder()
    if not video_urls or len(video_urls) == 0:
        builder.button(
            text="Нет видео",
            callback_data="back_to_student_courses_list"
        )

    i = 1
    for video in video_urls:
        builder.button(
            text=f"🎬 Видео {i}",
            callback_data=f"{video}_{lesson_id}"
        )

        i += 1

    builder.button(
        text="◀️ Назад к курсам",
        callback_data="back_to_student_courses_list"
    )

    return builder.adjust(1).as_markup()


async def get_video_keyboard(lesson_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Отметить как просмотренное",
        callback_data=f"marked_{lesson_id}"
    )

    builder.button(
        text="◀️ Назад к курсам",
        callback_data="back_to_student_courses_list"
    )

    return builder.adjust(1).as_markup()


async def build_test_keyboard(test: Test) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for answer in test.answers:
        builder.button(
            text=answer['answerText'],
            callback_data=f"answer_{answer['id']}"
        )

    # Распределяем кнопки по 1 в ряд (для вариантов ответа)
    builder.adjust(1)

    return builder.as_markup()
