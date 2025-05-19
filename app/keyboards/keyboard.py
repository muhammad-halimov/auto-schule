from typing import List

from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.APIhandlers.APIhandlersAutodrome import autodromes
from app.APIhandlers.APIhandlersCar import cars, admin_cars
from app.APIhandlers.APIhandlersCategory import categories, admin_categories
from app.APIhandlers.APIhandlersCourse import courses, get_course_by_id, Quiz, admin_courses, get_all_quizzes
from app.APIhandlers.APIhandlersInstructor import instructors, admin_instructors
from app.APIhandlers.APIhandlersLesson import get_all_lessons
from app.APIhandlers.APIhandlersSchedule import drive_schedules, admin_drive_schedules
from app.APIhandlers.APIhandlersStudent import student_courses, check_time_lessons, my_schedules
from app.APIhandlers.APIhandlersTeacher import teachers
from app.APIhandlers.APIhandlersUser import users


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
            keyboard.add(InlineKeyboardButton(text=f'📚 Курс: {course.title}',
                                              callback_data=f'{course.id}'))
            added_courses.add(course_key)

    return keyboard.adjust(1).as_markup()


async def inline_student_courses(student_id):
    keyboard = InlineKeyboardBuilder()
    s_courses = student_courses(student_id)

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


async def get_cancel_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить редактирование", callback_data="cancel_admin_edit")
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


async def build_test_keyboard(test: Quiz) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for answer in test.answers:
        builder.button(
            text=answer['answerText'],
            callback_data=f"answer_{answer['id']}"
        )

    builder.adjust(1)

    return builder.as_markup()


async def all_users_list():
    builder = InlineKeyboardBuilder()

    for user in users():
        builder.button(
            text=f"{user.get('roles')[0]} {user.get('surname', '')} {user.get('name', '')}",
            callback_data=f"{user['id']}"
        )

    builder.button(
        text="🆕 Добавить",
        callback_data="add_user"
    )

    builder.button(
        text="◀️ Вернуться в главное меню",
        callback_data=f"back_to_admin_menu"
    )

    return builder.adjust(1).as_markup()


async def inline_user_action(user_id: int, roles: List[str]):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_user_{user_id}-{roles[0]}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_user_{user_id}"
    )

    builder.button(
        text="◀️ Вернуться к списку пользователей",
        callback_data=f"users_list"
    )

    return builder.adjust(1).as_markup()


async def inline_admin_courses():
    keyboard = InlineKeyboardBuilder()
    added_courses = set()
    for course in admin_courses():
        course_key = f"{course.id}"

        if course_key not in added_courses:
            keyboard.add(InlineKeyboardButton(text=f'📚 Курс: {course.title}',
                                              callback_data=f'{course.id}'))
            added_courses.add(course_key)

    keyboard.button(
        text="🆕 Добавить",
        callback_data="add_course"
    )

    keyboard.button(
        text="◀️ Назад к меню",
        callback_data="back_to_admin_menu"
    )

    return keyboard.adjust(1).as_markup()


async def inline_admin_lessons_by_course(course_id: int) -> InlineKeyboardMarkup:
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
        callback_data=f"admin_test_{course_id}"
    )

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_course_{course_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_course_{course_id}"
    )

    builder.button(
        text="◀️ Назад к курсам",
        callback_data="courses_list"
    )

    builder.adjust(1)

    return builder.as_markup()


async def inline_course_quizzes():
    builder = InlineKeyboardBuilder()
    quizzes = get_all_quizzes()

    for quiz in quizzes:
        builder.button(
            text=quiz.question,
            callback_data=f"quiz_{quiz.id}"
        )

    builder.button(
        text="✅ Продолжить",
        callback_data="continue"
    )

    return builder.adjust(1).as_markup()



async def inline_course_categories():
    builder = InlineKeyboardBuilder()
    categories_list = categories()

    for cat in categories_list:
        builder.button(
            text=cat.title,
            callback_data=f"category_{cat.id}"
        )

    return builder.adjust(1).as_markup()


async def inline_course_users(users_in_course):
    builder = InlineKeyboardBuilder()
    users_list = users()

    for user in users_list:
        if "ROLE_STUDENT" in user['roles'] and user['id'] not in users_in_course:
            builder.button(
                text=f"👤 {user['surname']} {user['name']}",
                callback_data=f"user_{user['id']}"
            )

    builder.button(
        text="✅ Продолжить",
        callback_data="continue"
    )

    return builder.adjust(1).as_markup()


async def inline_course_lessons():
    builder = InlineKeyboardBuilder()
    lessons = get_all_lessons()

    for lesson in lessons:
        builder.button(
            text=lesson.title,
            callback_data=f"lesson_{lesson.id}"
        )

    builder.button(
        text="✅ Продолжить",
        callback_data="continue"
    )

    return builder.adjust(1).as_markup()


async def inline_admin_category():
    keyboard = InlineKeyboardBuilder()
    added_categories = set()
    for category in admin_categories():
        category_key = f"{category.id}"

        if category_key not in added_categories:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 Категория: {category.title}',
                                              callback_data=f'admin_category_{category.id}'))
            added_categories.add(category_key)

    keyboard.button(
        text="🆕 Добавить",
        callback_data=f"add_category"
    )

    keyboard.button(
        text="◀️ Назад в меню",
        callback_data="back_to_admin_menu"
    )

    return keyboard.adjust(1).as_markup()


async def category_action(category_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_category_{category_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_category_{category_id}"
    )

    builder.button(
        text="◀️ Назад к категориям",
        callback_data="category_list"
    )

    return builder.adjust(1).as_markup()


def get_user_roles_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Студент", callback_data="ROLE_STUDENT"),
            InlineKeyboardButton(text="Инструктор", callback_data="ROLE_INSTRUCTOR"),
            InlineKeyboardButton(text="Учитель", callback_data="ROLE_TEACHER")
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_edit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def inline_admin_schedules() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    schedules = admin_drive_schedules()
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
        text="🆕 Добавить",
        callback_data="add_schedule"
    )

    builder.button(
        text="◀️ Назад в меню",
        callback_data="back_to_admin_menu"
    )

    builder.adjust(1)

    return builder.as_markup()


async def inline_schedule_action(schedule_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_schedule_{schedule_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_schedule_{schedule_id}"
    )

    builder.button(
        text="◀️ Вернуться к списку расписаний",
        callback_data=f"schedules_list"
    )

    return builder.adjust(1).as_markup()


ADMIN_TIME_PREFIX = "admin_time_"
ADMIN_DAY_PREFIX = "admin_day_"
ADMIN_DONE_PREFIX = "admin_days_done"

# Клавиатура для выбора времени (админ)
async def get_admin_time_keyboard(prefix: str = "admin_time"):
    builder = InlineKeyboardBuilder()
    for hour in range(8, 19):
        for minute in [0, 30]:
            if hour == 18 and minute == 30:
                continue
            time_str = f"{hour:02d}:{minute:02d}"
            builder.add(InlineKeyboardButton(
                text=time_str,
                callback_data=f"{prefix}_{time_str}"
            ))
    builder.adjust(4)
    return builder.as_markup()


async def get_admin_days_keyboard(selected_days: list = None):
    if selected_days is None:
        selected_days = []

    builder = InlineKeyboardBuilder()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for day in days:
        emoji = "✅ " if day in selected_days else ""
        builder.add(InlineKeyboardButton(
            text=f"{emoji}{day}",
            callback_data=f"{ADMIN_DAY_PREFIX}{day}"
        ))

    builder.add(InlineKeyboardButton(
        text="✅ Готово",
        callback_data=ADMIN_DONE_PREFIX
    ))

    builder.adjust(3)
    return builder.as_markup()


async def get_cancel_schedule_edit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_schedule_edit")
    ]])


async def inline_schedule_edit_autodrome():
    builder = InlineKeyboardBuilder()

    for autodrome in autodromes():
        builder.add(InlineKeyboardButton(
            text=autodrome.title,
            callback_data=f"autodrome_{autodrome.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_schedule_edit_category():
    builder = InlineKeyboardBuilder()

    for category in admin_categories():
        builder.add(InlineKeyboardButton(
            text=category.title,
            callback_data=f"category_{category.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_schedule_edit_instructors():
    builder = InlineKeyboardBuilder()

    for instructor in admin_instructors():
        builder.add(InlineKeyboardButton(
            text=f"{instructor.surname} {instructor.name}",
            callback_data=f"instructor_{instructor.id}"
        ))

    return builder.adjust(2).as_markup()


async def confirm_schedule_update_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_schedule_update"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_schedule_edit"
    )

    return builder.adjust(1).as_markup()


async def confirm_schedule_add_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_schedule_addition"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_schedule_addition"
    )

    return builder.adjust(1).as_markup()


async def admin_inline_cars():
    keyboard = InlineKeyboardBuilder()
    added_cars = set()
    for car in admin_cars():
        car_key = f"{car.id}"

        if car_key not in added_cars:
            keyboard.add(InlineKeyboardButton(text=f'🚗 Автомобиль: {car.carMark} {car.carModel} {car.stateNumber}',
                                              callback_data=f'{car.id}'))
            added_cars.add(car_key)

    keyboard.button(
        text="🆕 Добавить",
        callback_data="add_car"
    )

    keyboard.button(
        text="◀️ Назад в меню",
        callback_data="back_to_admin_menu"
    )

    return keyboard.adjust(1).as_markup()


async def cars_action(car_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_car_{car_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_car_{car_id}"
    )

    builder.button(
        text="◀️ Вернуться к списку расписаний",
        callback_data=f"auto_list"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_car_edit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_car_edit")
    ]])


async def confirm_car_update_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_car_update"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_car_edit"
    )

    return builder.adjust(1).as_markup()


async def confirm_car_addition_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_car_addition"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_car_addition"
    )

    return builder.adjust(1).as_markup()