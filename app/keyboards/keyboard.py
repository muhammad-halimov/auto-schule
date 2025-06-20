from datetime import datetime
from typing import List

from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.APIhandlers.APIhandlersAutodrome import autodromes
from app.APIhandlers.APIhandlersCar import cars, admin_cars, get_all_marks_car
from app.APIhandlers.APIhandlersCategory import categories, admin_categories, admin_categories_schedule, \
    admin_categories_course
from app.APIhandlers.APIhandlersCourse import courses, get_course_by_id, Quiz, admin_courses, get_all_quizzes
from app.APIhandlers.APIhandlersDriveLesson import get_instructor_lessons
from app.APIhandlers.APIhandlersInstructor import instructors, admin_instructors
from app.APIhandlers.APIhandlersLesson import get_all_lessons, get_lesson_by_id
from app.APIhandlers.APIhandlersSchedule import drive_schedules, admin_drive_schedules
from app.APIhandlers.APIhandlersStudent import student_courses, check_time_lessons, my_schedules, get_all_students, \
    get_courses_sign_up, get_all_transaction
from app.APIhandlers.APIhandlersTeacher import teachers, get_teacher_courses, get_teacher_lessons, get_teacher_quizzes
from app.APIhandlers.APIhandlersUser import users


async def inline_categories():
    keyboard = InlineKeyboardBuilder()
    added_categories = set()
    for category in admin_categories_course():
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
        text="➡️ Записаться",
        callback_data="course_sign_up"
    )

    keyboard.button(
        text="◀️ Назад",
        callback_data="back_to_student_menu"
    )

    return keyboard.adjust(1).as_markup()


async def sign_up_courses(user_id):
    builder = InlineKeyboardBuilder()
    courses_list = get_courses_sign_up(user_id)

    for course in courses_list:
        builder.button(
            text=f"{course.get('title')}",
            callback_data=f"{course.get('id')}"
        )

    builder.button(
        text="◀️ Назад",
        callback_data="back_to_student_menu"
    )

    return builder.adjust(1).as_markup()


async def sign_up_courses_actions(course_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="➡️ Записаться",
        callback_data=f"student_course_sign_up_{course_id}"
    )

    builder.button(
        text="◀️ Назад",
        callback_data="course_sign_up"
    )

    return builder.adjust(1).as_markup()


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


async def get_cancel_course_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить редактирование", callback_data="back_to_admin_menu")
    return builder.as_markup()


async def get_cancel_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel_admin_edit")
    return builder.as_markup()


async def get_cancel_teacher_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel_course_teacher_add")
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
            lesson_time = datetime.fromisoformat(lesson.date).strftime("%Y-%m-%d %H:%M") if isinstance(lesson.date, str) else ''
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
            text=f"{user.get('roles')[0]} {user.get('surname', '')} {user['name']}",
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


async def inline_user_action(user_id: int, is_approved: bool, roles: List[str]):
    builder = InlineKeyboardBuilder()

    if is_approved is False:
        builder.button(
            text="✅ Одобрить",
            callback_data=f"approve_{user_id}"
        )

        builder.button(
            text="✅ Активировать",
            callback_data=f"approve_{user_id}"
        )

    builder.button(
        text="📨 Отправить пароль на почту",
        callback_data=f"send_pass_{user_id}"
    )

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
            callback_data="no_lessons")
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


async def inline_teacher_lessons_by_course(course_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    course = get_course_by_id(course_id)
    if not course or not hasattr(course, 'lessons'):
        builder.button(
            text="❌ Уроки не найдены",
            callback_data="no_lessons")
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
        callback_data=f"update_teacher_course_{course_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_teacher_course_{course_id}"
    )

    builder.button(
        text="◀️ Назад к курсам",
        callback_data="teacher_courses"
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_course_teacher_add"
    )

    return builder.adjust(1).as_markup()


async def inline_course_teacher_quizzes():
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_teacher_edit"
    )

    return builder.adjust(1).as_markup()


async def inline_course_categories():
    builder = InlineKeyboardBuilder()
    categories_list = categories()

    for cat in categories_list:
        if cat.type == "course":
            builder.button(
                text=cat.title,
                callback_data=f"category_{cat.id}"
            )

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_admin_edit"
    )

    return builder.adjust(1).as_markup()


async def inline_course_teacher_categories():
    builder = InlineKeyboardBuilder()
    categories_list = categories()

    for cat in categories_list:
        if cat.type == "course":
            builder.button(
                text=cat.title,
                callback_data=f"category_{cat.id}"
            )

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_course_teacher_add"
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_admin_edit"
    )

    return builder.adjust(1).as_markup()


async def inline_course_teacher_users(users_in_course):
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_course_teacher_add"
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_course_add"
    )

    return builder.adjust(1).as_markup()


async def inline_teacher_course_lessons():
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

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_course_teacher_add"
    )

    return builder.adjust(1).as_markup()


async def inline_admin_category():
    keyboard = InlineKeyboardBuilder()
    added_categories = set()
    for category in admin_categories():
        category_key = f"{category.id}"

        if category_key not in added_categories:
            keyboard.add(InlineKeyboardButton(text=f'👨🏻‍💻 Категория: {category.title}, Тип {category.type}',
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


async def inline_instuctor_schedule_action(schedule_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_instructor_schedule_{schedule_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_instructor_schedule_{schedule_id}"
    )

    builder.button(
        text="◀️ Вернуться в меню",
        callback_data=f"back_to_instructor_menu"
    )

    return builder.adjust(1).as_markup()


async def inline_no_schedule_action():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🆕 Добавить",
        callback_data=f"add_instructor_schedule"
    )

    builder.button(
        text="◀️ Вернуться в меню",
        callback_data=f"back_to_instructor_menu"
    )

    return builder.adjust(1).as_markup()


ADMIN_TIME_PREFIX = "admin_time_"
ADMIN_DAY_PREFIX = "admin_day_"
ADMIN_DONE_PREFIX = "admin_days_done"


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


INSTRUCTOR_TIME_PREFIX = "instructor_time_"
INSTRUCTOR_DAY_PREFIX = "instructor_day_"
INSTRUCTOR_DONE_PREFIX = "instructor_days_done"


async def get_instructor_time_keyboard(prefix: str = "instructor_time"):
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


async def get_instructor_days_keyboard(selected_days: list = None):
    if selected_days is None:
        selected_days = []

    builder = InlineKeyboardBuilder()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for day in days:
        emoji = "✅ " if day in selected_days else ""
        builder.add(InlineKeyboardButton(
            text=f"{emoji}{day}",
            callback_data=f"{INSTRUCTOR_DAY_PREFIX}{day}"
        ))

    builder.add(InlineKeyboardButton(
        text="✅ Готово",
        callback_data=INSTRUCTOR_DONE_PREFIX
    ))

    builder.adjust(3)
    return builder.as_markup()


async def get_cancel_schedule_edit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_schedule_edit")
    ]])


async def get_cancel_instructor_schedule_edit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_instructor_schedule_edit")
    ]])


async def inline_schedule_edit_autodrome():
    builder = InlineKeyboardBuilder()

    for autodrome in autodromes():
        builder.add(InlineKeyboardButton(
            text=autodrome.title,
            callback_data=f"autodrome_{autodrome.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_instructor_schedule_edit_autodrome():
    builder = InlineKeyboardBuilder()

    for autodrome in autodromes():
        builder.add(InlineKeyboardButton(
            text=autodrome.title,
            callback_data=f"instructor_autodrome_{autodrome.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_schedule_edit_category():
    builder = InlineKeyboardBuilder()

    for category in admin_categories_schedule():
        builder.add(InlineKeyboardButton(
            text=category.title,
            callback_data=f"category_{category.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_instructor_schedule_edit_category():
    builder = InlineKeyboardBuilder()

    for category in admin_categories_schedule():
        builder.add(InlineKeyboardButton(
            text=category.title,
            callback_data=f"instructor_category_{category.id}"
        ))

    return builder.adjust(2).as_markup()


async def inline_schedule_edit_instructors():
    builder = InlineKeyboardBuilder()
    schedules = drive_schedules()

    for instructor in admin_instructors():
        for schedule in schedules:
            if instructor.id != schedule.instructor_id:
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


async def confirm_instructor_schedule_add_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_instructor_schedule_addition"
    )
    builder.button(
        text="❌ Отменить",
        callback_data="cancel_instructor_schedule_addition"
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
        text="◀️ Вернуться к списку машин",
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
        callback_data="cancel_car_edit"
    )

    return builder.adjust(1).as_markup()


async def teacher_courses(teacher_id):
    builder = InlineKeyboardBuilder()

    courses_list = get_teacher_courses(teacher_id)
    if len(courses_list) == 0:
        builder.button(
            text="Нет курсов",
            callback_data="no_courses"
        )
    else:
        for course in courses_list:
            builder.button(
                text=f"📝 {course.title}",
                callback_data=f"{course.id}"
            )

    builder.button(
        text="🆕 Добавить курс",
        callback_data="add_course_teacher"
    )

    builder.button(
        text="◀️ В главное меню",
        callback_data="back_to_teacher_menu"
    )

    return builder.adjust(1).as_markup()


async def teacher_lessons(teacher_id):
    builder = InlineKeyboardBuilder()

    lessons_list = get_teacher_lessons(teacher_id)
    if len(lessons_list) == 0:
        builder.button(
            text="Нет занятий",
            callback_data="no_lessons"
        )
    else:
        for lesson in lessons_list:
            builder.button(
                text=f"📝 {lesson.title}",
                callback_data=f"{lesson.id}"
            )

    builder.button(
        text="🆕 Добавить урок",
        callback_data="add_lesson_teacher"
    )

    builder.button(
        text="◀️ В главное меню",
        callback_data="back_to_teacher_menu"
    )

    return builder.adjust(1).as_markup()


async def teacher_lesson_action(lesson_id):
    builder = InlineKeyboardBuilder()
    videos = get_lesson_by_id(lesson_id).videos
    i = 1
    for video in videos:
        builder.button(
            text=f"🎬 Видео {i}",
            callback_data=f"{video['video']}"
        )
        i += 1

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_teacher_lesson_{lesson_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_teacher_lesson_{lesson_id}"
    )

    builder.button(
        text="◀️ Вернуться к списку занятий",
        callback_data=f"teacher_lessons"
    )

    return builder.adjust(1).as_markup()


async def admin_lesson_action(lesson_id):
    builder = InlineKeyboardBuilder()
    videos = get_lesson_by_id(lesson_id).videos
    i = 1
    for video in videos:
        builder.button(
            text=f"🎬 Видео {i}",
            callback_data=f"{video['video']}"
        )
        i += 1

    builder.button(
        text="🔄 Редактировать",
        callback_data=f"update_admin_lesson_{lesson_id}"
    )

    builder.button(
        text="🗑️ Удалить",
        callback_data=f"delete_admin_lesson_{lesson_id}"
    )

    builder.button(
        text="◀️ Вернуться к списку занятий",
        callback_data=f"lessons_list"
    )

    return builder.adjust(1).as_markup()


async def get_event_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оффлайн",
        callback_data="offline"
    )

    builder.button(
        text="Онлайн",
        callback_data="online"
    )

    builder.button(
        text="❌ Отменить создание",
        callback_data="cancel_teacher_add_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_event_admin_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оффлайн",
        callback_data="offline"
    )

    builder.button(
        text="Онлайн",
        callback_data="online"
    )

    builder.button(
        text="❌ Отменить создание",
        callback_data="cancel_admin_add_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_event_update_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оффлайн",
        callback_data="offline"
    )

    builder.button(
        text="Онлайн",
        callback_data="online"
    )

    builder.button(
        text="⏭️ Пропустить",
        callback_data="skip"
    )

    builder.button(
        text="❌ Отменить редактирование",
        callback_data="cancel_teacher_update_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_event_admin_update_type_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оффлайн",
        callback_data="admin_offline"
    )

    builder.button(
        text="Онлайн",
        callback_data="admin_online"
    )

    builder.button(
        text="⏭️ Пропустить",
        callback_data="admin_skip"
    )

    builder.button(
        text="❌ Отменить редактирование",
        callback_data="cancel_admin_update_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_teacher_add_lesson_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Отменить создание",
        callback_data="cancel_teacher_add_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_admin_add_lesson_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❌ Отменить создание",
        callback_data="cancel_admin_add_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_teacher_update_lesson_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⏭️ Пропустить",
        callback_data="skip"
    )

    builder.button(
        text="❌ Отменить редактирование",
        callback_data="cancel_teacher_update_lesson"
    )

    return builder.adjust(1).as_markup()


async def get_cancel_admin_update_lesson_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⏭️ Пропустить",
        callback_data="admin_skip"
    )

    builder.button(
        text="❌ Отменить редактирование",
        callback_data="cancel_admin_update_lesson"
    )

    return builder.adjust(1).as_markup()


def get_time_selection_keyboard(with_skip=False):
    builder = InlineKeyboardBuilder()
    times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    for time_str in times:
        builder.button(text=time_str, callback_data=f"teacher_lesson_time_{time_str}")
    if with_skip:
        builder.button(text="⏭️ Пропустить", callback_data="time_skip")
        builder.button(text="❌ Отмена", callback_data="cancel_teacher_update_lesson")
        return builder.adjust(4).as_markup()
    else:
        builder.button(text="❌ Отмена", callback_data="cancel_teacher_update_lesson")
        return builder.adjust(4).as_markup()


def get_time_selection_keyboard_instructor_lesson():
    builder = InlineKeyboardBuilder()
    times = [f"{hour:02d}:00" for hour in range(9, 19)]

    for time_str in times:
        builder.button(text=time_str, callback_data=f"instructor_lesson_time_{time_str}")

    builder.button(text="❌ Отмена", callback_data="cancel_lesson_creation")
    return builder.adjust(4).as_markup()


def get_time_admin_selection_keyboard(with_skip=False):
    builder = InlineKeyboardBuilder()
    times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    for time_str in times:
        builder.button(text=time_str, callback_data=f"admin_lesson_time_{time_str}")
    if with_skip:
        builder.button(text="⏭️ Пропустить", callback_data="time_skip")
        builder.button(text="❌ Отмена", callback_data="cancel_admin_update_lesson")
        return builder.adjust(4).as_markup()
    else:
        builder.button(text="❌ Отмена", callback_data="cancel_admin_update_lesson")
        return builder.adjust(4).as_markup()


async def inline_teacher_quizzes():
    builder = InlineKeyboardBuilder()

    quizzes = get_teacher_quizzes()

    for quiz in quizzes:
        builder.button(text=f"{quiz.question}",
                       callback_data=f"{quiz.id}")

    builder.button(text="🆕 Добавить",
                   callback_data="add_teacher_quiz")

    builder.button(text="◀️ Назад в меню",
                   callback_data="back_to_teacher_menu")

    return builder.adjust(1).as_markup()


async def quiz_action_keyboard(quiz_id):
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄 Редактировать",
                   callback_data=f"update_teacher_quiz_{quiz_id}")

    builder.button(text="🗑️ Удалить",
                   callback_data=f"delete_teacher_quiz_{quiz_id}")

    builder.button(text="◀️ Назад к списку",
                   callback_data="teacher_quizzes")

    return builder.adjust(1).as_markup()


async def get_done_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово", callback_data="done_answers")
    builder.button(text="❌ Отмена", callback_data="cancel_quiz_creation")
    return builder.as_markup()


async def get_cancel_teacher_update_question_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отменить", callback_data="cancel_question_editing")
    return keyboard.as_markup()


async def teacher_all_student():
    builder = InlineKeyboardBuilder()
    students = get_all_students()

    for student in students:
        builder.button(
            text=f"{student.surname} {student.name} {student.patronymic if student.patronymic is not None else ''}",
            callback_data=f"{student.id}"
        )

    builder.button(
        text="◀️ Назад в меню",
        callback_data="back_to_teacher_menu"
    )

    return builder.adjust(1).as_markup()


async def get_teacher_student_progress():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="◀️ Назад к списку студентов", callback_data="student_progress")
    return keyboard.as_markup()


async def get_cancel_category_edit_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отменить редактирование", callback_data="cancel_category_edit")
    return keyboard.as_markup()


async def get_marks_car():
    builder = InlineKeyboardBuilder()
    marks = get_all_marks_car()

    for mark in marks:
        builder.button(
            text=f"{mark.get("title")}",
            callback_data=f"mark_{mark.get("id")}"
        )

    return builder.adjust(1).as_markup()


async def get_category_types():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Курс",
        callback_data="type_course"
    )

    builder.button(
        text="Вождение",
        callback_data="type_driving"
    )

    return builder.adjust(1).as_markup()


async def admin_lessons():
    builder = InlineKeyboardBuilder()
    lessons = get_all_lessons()

    for lesson in lessons:
        builder.button(
            text=f"{lesson.title}",
            callback_data=f"{lesson.id}"
        )

    builder.button(
        text="🆕 Добавить",
        callback_data="add_admin_lesson"
    )

    builder.button(
        text="◀️ Назад в главное меню",
        callback_data="back_to_admin_menu"
    )

    return builder.adjust(1).as_markup()


async def get_student_transactions_list(user_id, email, password):
    builder = InlineKeyboardBuilder()
    transactions = get_all_transaction(user_id, email, password)

    for transaction in transactions:
        if transaction.get('user').get('id') == user_id:
            builder.button(
                text=f"{datetime.fromisoformat(transaction.get('transactionDatetime')
                                               ).strftime("%d.%m.%Y %H:%M")}",
                callback_data=f"{transaction.get('id')}")

    builder.button(
        text="💰 Пополнить баланс",
        callback_data="fill_student_balance"
    )

    builder.button(
        text="◀️ Назад в главное меню",
        callback_data="back_to_student_menu"
    )

    return builder.adjust(1).as_markup()


async def student_transaction_actions():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="◀️ Назад в главное меню",
        callback_data="back_to_student_menu"
    )

    return builder.adjust(1).as_markup()


async def inline_instructor_drive_lessons(user_id, email, password):
    builder = InlineKeyboardBuilder()
    drive_lessons = get_instructor_lessons(email, password)

    for lesson in drive_lessons:
        if lesson.instructor.get('id') == user_id:
            builder.button(
                text=f"{datetime.fromisoformat(lesson.date).strftime("%Y-%m-%d %H:%M")} {lesson.student.get('surname')}"
                     f" {lesson.student.get('name')}",
                callback_data=f"{lesson.id}"
            )

    builder.button(
        text="🆕 Добавить",
        callback_data="add_instructor_lesson"
    )

    builder.button(
        text="◀️ Назад в главное меню",
        callback_data="back_to_instructor_menu"
    )

    return builder.adjust(1).as_markup()


async def instructor_lesson_actions(lesson_id):
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄 Редактировать",
                   callback_data=f"update_instructor_lesson_{lesson_id}")

    builder.button(text="🗑️ Удалить",
                   callback_data=f"delete_instructor_lesson_{lesson_id}")

    builder.button(text="◀️ Назад к списку",
                   callback_data="instructor_my_lessons")

    return builder.adjust(1).as_markup()


async def get_autodromes_keyboard():
    builder = InlineKeyboardBuilder()
    autodromes_list = autodromes()

    for a in autodromes_list:
        builder.button(text=a.title, callback_data=f"autodrome_{a.id}")
    return builder.adjust(1).as_markup()


async def get_categories_keyboard():
    builder = InlineKeyboardBuilder()
    categories_list = admin_categories_schedule()

    for c in categories_list:
        builder.button(text=c.title, callback_data=f"category_{c.id}")
    return builder.adjust(1).as_markup()


async def get_students_keyboard():
    builder = InlineKeyboardBuilder()
    students = get_all_students()

    for s in students:
        builder.button(text=f"{s.surname} {s.name}", callback_data=f"student_{s.id}")
    return builder.adjust(1).as_markup()


async def get_confirm_lesson_creation_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Подтвердить", callback_data="confirm_lesson_creation")
    builder.button(text="❌ Отменить", callback_data="cancel_lesson_creation")

    return builder.adjust(2).as_markup()


async def amount():
    builder = InlineKeyboardBuilder()

    builder.button(text="1000", callback_data=f"amount_{1000}")
    builder.button(text="5000", callback_data=f"amount_{5000}")
    builder.button(text="10000", callback_data=f"amount_{10000}")
    builder.button(text="15000", callback_data=f"amount_{15000}")
    builder.button(text="20000", callback_data=f"amount_{20000}")

    return builder.adjust(1).as_markup()


async def confirm_category_addition_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Подтвердить",
        callback_data="confirm_category_addition"
    )

    builder.button(
        text="❌ Отменить",
        callback_data="cancel_category_addition"
    )

    return builder.adjust(1).as_markup()