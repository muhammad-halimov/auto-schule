import asyncio
from datetime import datetime, time
from typing import Optional, List

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, URLInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendarCallback

from app.APIhandlers.APIhandlersCourse import (
    add_course_to_api, get_quiz_title, update_course_in_api,
    get_course_by_id, delete_course
)
from app.APIhandlers.APIhandlersLesson import (
    get_lesson_title, get_lesson_by_id, delete_lesson_from_api,
    add_lesson_to_api, update_lesson_in_api
)
from app.APIhandlers.APIhandlersStudent import get_student_progress_by_id
from app.APIhandlers.APIhandlersTeacher import get_quiz_by_id, delete_quiz_from_api, create_quiz, update_question_in_api
from app.APIhandlers.APIhandlersUser import get_user_by_id, get_user_name
from app.calendar import RussianSimpleCalendar
from app.handlers.handlers import (
    TeacherCourseState, AddTeacherCourseStates, UpdateTeacherCourseStates,
    TeacherLessonState, TeacherAddLessonState, TeacherEditLessonState, TeacherQuizzesState, TeacherAddQuizState,
    TeacherEditQuestionState, CheckTeacherStudentProgress
)
from app.utils.jsons_creator import UserStorage
from config_local import profile_photos, lessons_videos
from app.keyboards import static_keyboard as static_kb
from app.keyboards import keyboard as kb

teacher_router = Router()
storage = UserStorage()

JSON_DATA_DIR = "data/json/"
DEFAULT_PROFILE_PHOTO = "static/img/default.jpg"


async def delete_previous_messages(message: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot = message.bot if isinstance(message, Message) else message.message.bot
    chat_id = message.chat.id if isinstance(message, Message) else message.message.chat.id

    for msg_type in ['last_bot_msg', 'last_keyboard_msg']:
        msg_id = data.get(msg_type)
        if msg_id is not None:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except TelegramBadRequest as e:
                if "message to delete not found" not in str(e):
                    print(f"Error deleting {msg_type}: {e}")

    prev_msgs = data.get('prev_msgs', [])
    if prev_msgs:
        for msg_id in prev_msgs:
            if msg_id is not None:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except TelegramBadRequest as e:
                    if "message to delete not found" not in str(e):
                        print(f"Error deleting prev_msg {msg_id}: {e}")

    if isinstance(message, Message):
        try:
            await message.delete()
        except TelegramBadRequest as e:
            if "message to delete not found" not in str(e):
                print(f"Error deleting current message: {e}")

    await state.update_data({
        'last_bot_msg': None,
        'last_keyboard_msg': None,
        'prev_msgs': []
    })


class MessageManager:

    @staticmethod
    async def safe_delete(message: Optional[Message]) -> None:
        if message:
            try:
                await message.delete()
            except TelegramBadRequest:
                pass

    @staticmethod
    async def cleanup_chat(chat_id: int, message_ids: List[int], bot) -> None:

        for msg_id in message_ids:
            try:
                await bot.delete_message(chat_id, msg_id)
            except TelegramBadRequest:
                continue


async def handle_back_to_teacher_menu(update: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    if isinstance(update, CallbackQuery):
        message = update.message
        user_id = update.from_user.id
    else:
        message = update
        user_id = update.from_user.id

    await MessageManager.safe_delete(message)

    user = get_user_by_id(storage.get_user_credentials(user_id).db_id)
    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.get("surname", "")} {user.get("name", "")}, Ваша роль Учитель',
        reply_markup=static_kb.teacher_main
    )


@teacher_router.callback_query(F.data == "teacher_info")
async def get_teacher_info(callback: CallbackQuery) -> None:
    await MessageManager.safe_delete(callback.message)

    user_id = storage.get_user_credentials(callback.from_user.id).db_id
    user = get_user_by_id(user_id)

    if not user:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    info_text = (
        f"🧑‍🎓 Информация о вас:\n\n"
        f"▫️ <b>Фамилия:</b> {user.get('surname', '')}\n"
        f"▫️ <b>Имя:</b> {user.get('name', '')}\n"
        f"▫️ <b>Отчество:</b> {user.get('patronym', '')}\n"
        f"▫️ <b>Категория</b> {user.get('category').get('title')[-1]}"
    )

    photo = (URLInputFile(f"{profile_photos}{user.get('image')}")
             if user.get('image') else FSInputFile(DEFAULT_PROFILE_PHOTO))

    await callback.message.answer_photo(
        photo=photo,
        caption=info_text,
        parse_mode='HTML',
        reply_markup=static_kb.teacher_info
    )


@teacher_router.callback_query(F.data == "back_to_teacher_menu")
async def back_to_teacher_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await handle_back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data == "teacher_courses")
async def check_teacher_courses(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    teacher_id = storage.get_user_credentials(callback.from_user.id).db_id
    await callback.message.answer(
        text="Вот ваши курсы:",
        reply_markup=await kb.teacher_courses(teacher_id)
    )
    await state.set_state(TeacherCourseState.waiting_for_id)


@teacher_router.callback_query(TeacherCourseState.waiting_for_id)
async def get_teacher_course_by_id(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data.startswith('delete_teacher_course_'):
        await delete_teacher_course(callback, state)
    elif callback.data.startswith('update_teacher_course_'):
        await start_updating_teacher_course(callback, state)
    elif callback.data == 'add_course_teacher':
        await start_adding_teacher_course(callback, state)
    else:
        await MessageManager.safe_delete(callback.message)
        course_id = int(callback.data)
        course = get_course_by_id(course_id)

        info = (
            f"🧑‍🎓 Информация о курсе:\n\n"
            f"▫️ <b>Название:</b> {course.title}\n"
            f"▫️ <b>Описание:</b> {course.description}\n"
        )

        await callback.message.answer(
            text=info,
            parse_mode="HTML",
            reply_markup=await kb.inline_teacher_lessons_by_course(course_id)
        )
        await state.clear()


@teacher_router.callback_query(F.data.startswith('delete_teacher_course_'))
async def delete_teacher_course(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    course_id = int(callback.data.split('_')[3])
    credentials = storage.get_user_credentials(callback.from_user.id)

    delete_result = delete_course(
        course_id=course_id,
        email=credentials.email,
        password=credentials.password
    )

    if delete_result == 204:
        msg = await callback.message.answer(text=f"Курс {course_id} успешно удален")
    else:
        msg = await callback.message.answer(text="Ошибка удаления курса")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await check_teacher_courses(callback, state)


@teacher_router.callback_query(F.data == "add_course_teacher")
async def start_adding_teacher_course(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    new_msg = await callback.message.answer(
        "Введите название нового курса ⬇️",
        reply_markup=await kb.get_cancel_teacher_keyboard()
    )

    await state.update_data(
        last_bot_msg=new_msg.message_id,
        selected_lessons=[],
        selected_users=[],
        selected_quizzes=[]
    )
    await state.set_state(AddTeacherCourseStates.waiting_for_title)


@teacher_router.message(AddTeacherCourseStates.waiting_for_title)
async def process_course_title(message: Message, state: FSMContext) -> None:
    await delete_previous_messages(message, state)
    await state.update_data(title=message.text)

    new_msg = await message.answer(
        "Введите описание нового курса ⬇️",
        reply_markup=await kb.get_cancel_teacher_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddTeacherCourseStates.waiting_for_description)


@teacher_router.message(AddTeacherCourseStates.waiting_for_description)
async def process_course_description(message: Message, state: FSMContext) -> None:
    await delete_previous_messages(message, state)
    await state.update_data(description=message.text)

    new_msg = await message.answer(
        "Выберите уроки для нового курса ⬇️",
        reply_markup=await kb.inline_teacher_course_lessons()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddTeacherCourseStates.waiting_for_lessons)


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def select_lessons(callback: CallbackQuery, state: FSMContext) -> None:
    lesson_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_lessons = data.get('selected_lessons', [])

    if lesson_id in selected_lessons:
        selected_lessons.remove(lesson_id)
    else:
        selected_lessons.append(lesson_id)

    await state.update_data(selected_lessons=selected_lessons)
    await callback.answer(f"Урок {'добавлен' if lesson_id in selected_lessons else 'удален'}")


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_lessons, F.data == "continue")
async def process_lessons_selection(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    new_msg = await callback.message.answer(
        "Выберите пользователей для нового курса ⬇️",
        reply_markup=await kb.inline_course_teacher_users([])
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddTeacherCourseStates.waiting_for_users)


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_users, F.data.startswith("user_"))
async def select_users(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_users = data.get('selected_users', [])

    if user_id in selected_users:
        selected_users.remove(user_id)
    else:
        selected_users.append(user_id)

    await state.update_data(selected_users=selected_users)
    await callback.answer(f"Пользователь {'добавлен' if user_id in selected_users else 'удален'}")


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_users, F.data == "continue")
async def process_users_selection(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    new_msg = await callback.message.answer(
        "Выберите категорию для нового курса ⬇️",
        reply_markup=await kb.inline_course_teacher_categories()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddTeacherCourseStates.waiting_for_category)


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_category, F.data.startswith("category_"))
async def select_category(callback: CallbackQuery, state: FSMContext) -> None:
    category_id = int(callback.data.split('_')[1])
    await MessageManager.safe_delete(callback.message)
    await state.update_data(category_id=category_id)

    new_msg = await callback.message.answer(
        "Выберите тесты для нового курса ⬇️",
        reply_markup=await kb.inline_course_quizzes()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddTeacherCourseStates.waiting_for_quizzes)


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def select_quizzes(callback: CallbackQuery, state: FSMContext) -> None:
    quiz_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_quizzes = data.get('selected_quizzes', [])

    if quiz_id in selected_quizzes:
        selected_quizzes.remove(quiz_id)
    else:
        selected_quizzes.append(quiz_id)

    await state.update_data(selected_quizzes=selected_quizzes)
    await callback.answer(f"Тест {'добавлен' if quiz_id in selected_quizzes else 'удален'}")


@teacher_router.callback_query(AddTeacherCourseStates.waiting_for_quizzes, F.data == "continue")
async def confirm_course_addition(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await MessageManager.safe_delete(callback.message)

    message_text = (
            "✅ Проверьте данные нового курса:\n\n"
            f"🏷️ Название: {data.get('title')}\n"
            f"📋 Описание: {data.get('description')}\n"
            "📖 Выбранные уроки:\n" + "\n".join(["🔹 " + get_lesson_title(lesson_id) for lesson_id in
                                                data.get('selected_lessons', [])]) + "\n\n"
            "👨‍🎓 Выбранные пользователи:\n" + "\n".join(["▪️ " + get_user_name(user_id) for user_id in
                                                        data.get('selected_users', [])]) + "\n\n"
            "🧠 Выбранные тесты:\n" + "\n".join(["🔸 " + get_quiz_title(quiz_id) for quiz_id in
                                                data.get('selected_quizzes', [])])
    )

    await callback.message.answer(
        message_text,
        reply_markup=static_kb.confirm_course_addition_teacher
    )
    await state.set_state(AddTeacherCourseStates.confirmation)


@teacher_router.callback_query(AddTeacherCourseStates.confirmation, F.data == "confirm_course_addition_teacher")
async def finalize_course_addition(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await MessageManager.safe_delete(callback.message)

    credentials = storage.get_user_credentials(callback.from_user.id)
    add_result = add_course_to_api(
        title=data['title'],
        description=data['description'],
        lessons=data.get('selected_lessons', []),
        users=data.get('selected_users', []),
        category=data.get('category_id'),
        quizzes=data.get('selected_quizzes', []),
        email=credentials.email,
        password=credentials.password
    )

    if add_result == 201:
        msg = await callback.message.answer("Новый курс успешно добавлен!")
    else:
        msg = await callback.message.answer("Ошибка при добавлении курса")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await handle_back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data == "cancel_course_teacher_add")
async def cancel_course_addition(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)
    await handle_back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data.startswith('update_teacher_course_'))
async def start_updating_teacher_course(callback: CallbackQuery, state: FSMContext):
    course_id = int(callback.data.split('_')[3])
    course_data = get_course_by_id(course_id)

    course_dict = {
        'id': course_data.id,
        'title': course_data.title,
        'description': course_data.description,
        'category_id': course_data.category.get('id') if course_data.category else None,
        'lessons': [lesson.get('id') for lesson in course_data.lessons],
        'users': [user.get('id') for user in course_data.users],
        'quizzes': [quiz.get('id') for quiz in course_data.quizzes]
    }

    await state.update_data(
        original_course=course_dict,
        current_course=course_dict.copy()
    )
    await show_course_edit_options(callback, state)
    await state.set_state(UpdateTeacherCourseStates.waiting_for_choose)


async def show_course_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course = data['current_course']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Название: {course.get('title')}", callback_data="edit_course_title")
    keyboard.button(text=f"Описание: {course.get('description')[:30]}...", callback_data="edit_course_description")
    keyboard.button(text=f"Категория: {course.get('category_id')}", callback_data="edit_course_category")
    keyboard.button(text="Уроки", callback_data="edit_course_lessons")
    keyboard.button(text="Пользователи", callback_data="edit_course_users")
    keyboard.button(text="Тесты", callback_data="edit_course_quizzes")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_course_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_course_editing")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в курсе? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(UpdateTeacherCourseStates.waiting_for_choose)


@teacher_router.callback_query(
    UpdateTeacherCourseStates.waiting_for_choose,
    F.data.startswith("edit_course_")
)
async def process_course_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[2]

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if choice == "title":
        await callback.message.answer(
            "Введите новое название курса или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_teacher_keyboard()
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_title)

    elif choice == "description":
        await callback.message.answer(
            "Введите новое описание курса или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_teacher_keyboard()
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_description)

    elif choice == "category":
        await callback.message.answer(
            "Выберите новую категорию курса:",
            reply_markup=await kb.inline_course_categories()
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_category)

    elif choice == "lessons":

        await callback.message.answer(
            "Выберите уроки для курса:",
            reply_markup=await kb.inline_course_lessons()
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_lessons)

    elif choice == "users":
        data = await state.get_data()
        current_users = data['current_course'].get('users', [])

        await callback.message.answer(
            "Выберите пользователей для курса:",
            reply_markup=await kb.inline_course_users(current_users)
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_users)

    elif choice == "quizzes":

        await callback.message.answer(
            "Выберите тесты для курса:",
            reply_markup=await kb.inline_course_quizzes()
        )
        await state.set_state(UpdateTeacherCourseStates.waiting_for_quizzes)

    await callback.answer()


@teacher_router.message(UpdateTeacherCourseStates.waiting_for_title)
async def process_edit_course_title(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_course']['title'] = message.text
        await state.update_data(current_course=data['current_course'])

    await show_course_edit_options(message, state)


@teacher_router.message(UpdateTeacherCourseStates.waiting_for_description)
async def process_edit_course_description(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_course']['description'] = message.text
        await state.update_data(current_course=data['current_course'])

    await show_course_edit_options(message, state)


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_category, F.data.startswith("category_"))
async def process_edit_course_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    data = await state.get_data()
    data['current_course']['category_id'] = category_id
    await state.update_data(current_course=data['current_course'])

    await callback.message.delete()
    await show_course_edit_options(callback, state)


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def process_edit_course_lessons(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    current_lessons = data['current_course'].get('lessons', [])

    if lesson_id in current_lessons:
        current_lessons.remove(lesson_id)
    else:
        current_lessons.append(lesson_id)

    data['current_course']['lessons'] = current_lessons
    await state.update_data(current_course=data['current_course'])
    await callback.answer(f"Урок {'добавлен' if lesson_id in current_lessons else 'удален'}")


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_lessons, F.data == "continue")
async def finish_edit_course_lessons(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_course_edit_options(callback, state)


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_users, F.data.startswith("user_"))
async def process_edit_course_users(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    current_users = data['current_course'].get('users', [])

    if user_id in current_users:
        current_users.remove(user_id)
    else:
        current_users.append(user_id)

    data['current_course']['users'] = current_users
    await state.update_data(current_course=data['current_course'])
    await callback.answer(f"Пользователь {'добавлен' if user_id in current_users else 'удален'}")


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_users, F.data == "continue")
async def finish_edit_course_users(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_course_edit_options(callback, state)


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def process_edit_course_quizzes(callback: CallbackQuery, state: FSMContext):
    quiz_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    current_quizzes = data['current_course'].get('quizzes', [])

    if quiz_id in current_quizzes:
        current_quizzes.remove(quiz_id)
    else:
        current_quizzes.append(quiz_id)

    data['current_course']['quizzes'] = current_quizzes
    await state.update_data(current_course=data['current_course'])
    await callback.answer(f"Тест {'добавлен' if quiz_id in current_quizzes else 'удален'}")


@teacher_router.callback_query(UpdateTeacherCourseStates.waiting_for_quizzes, F.data == "continue")
async def finish_edit_course_quizzes(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await show_course_edit_options(callback, state)


@teacher_router.callback_query(F.data == "finish_course_editing")
async def finalize_course_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_course']
    updated = data['current_course']

    changes = {}
    for key in ['title', 'description', 'category_id', 'price', 'lessons', 'users', 'quizzes']:
        if original.get(key) != updated.get(key):
            changes[key] = updated.get(key)

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        update_result = update_course_in_api(
            course_id=changes['id'],
            title=changes.get('title', original['title']),
            description=changes.get('description', original['description']),
            lessons=changes.get('lessons', original['lessons']),
            users=changes.get('users', original['users']),
            category=changes.get('category_id', original['category_id']),
            quizzes=changes.get('quizzes', original['quizzes']),
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            msg = await callback.message.answer("✅ Курс успешно обновлен!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении курса")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await state.clear()
    await handle_back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data == "cancel_course_editing")
async def cancel_course_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await handle_back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data == "teacher_lessons")
async def get_teacher_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    teacher_id = storage.get_user_credentials(callback.from_user.id).db_id
    await callback.message.answer(
        text="Вот ваши уроки ⬇️",
        reply_markup=await kb.teacher_lessons(teacher_id)
    )
    await state.set_state(TeacherLessonState.waiting_for_id)


@teacher_router.callback_query(TeacherLessonState.waiting_for_id)
async def check_lesson_by_id(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "add_lesson_teacher":
        await add_lesson_teacher(callback, state)
    elif callback.data.startswith('delete_teacher_lesson_'):
        await delete_teacher_lesson(callback, state)
    elif callback.data.startswith('update_teacher_lesson_'):
        await start_lesson_editing(callback, state)
    else:
        await MessageManager.safe_delete(callback.message)
        lesson_id = int(callback.data)
        lesson = get_lesson_by_id(lesson_id)

        info = (
            "📚 <b>Занятие</b>:\n\n"
            f"📖 <b>Название</b>: {lesson.title}\n\n"
            f"📝 <b>Описание</b>: {lesson.description}\n\n"
            f"🎯 <b>Тип урока</b>: {lesson.lesson_type}\n\n"
            f"📅 <b>Дата</b>: {datetime.fromisoformat(lesson.date).strftime('%d.%m.%Y %H:%M')}\n\n"
        )

        await callback.message.answer(
            text=info,
            parse_mode="HTML",
            reply_markup=await kb.teacher_lesson_action(lesson_id)
        )
        await state.set_state(TeacherLessonState.waiting_for_video)


@teacher_router.callback_query(TeacherLessonState.waiting_for_video)
async def check_lesson_video(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data.startswith('video_'):
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        video_url = f"{lessons_videos}{callback.data.split('_')[1]}"
        await callback.message.answer_video(
            video=URLInputFile(video_url),
            reply_markup=static_kb.back_to_teacher_lessons,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=15
        )
        await state.clear()
    else:
        await callback.answer()


@teacher_router.callback_query(F.data.startswith('delete_teacher_lesson_'))
async def delete_teacher_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)

    credentials = storage.get_user_credentials(callback.from_user.id)
    lesson_id = int(callback.data.split('_')[3])

    result = delete_lesson_from_api(lesson_id, credentials.email, credentials.password)

    if result == 204:
        msg = await callback.message.answer(text="✅ Урок удален")
    else:
        msg = await callback.message.answer(text="❌ Удаление не удалось")

    await asyncio.sleep(2)
    await MessageManager.safe_delete(msg)
    await get_teacher_lesson(callback, state)


@teacher_router.callback_query(F.data == "add_lesson_teacher")
async def add_lesson_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await MessageManager.safe_delete(callback.message)

    msg = await callback.message.answer(
        "Введите название занятия ⬇️",
        reply_markup=await kb.get_cancel_teacher_add_lesson_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(TeacherAddLessonState.waiting_for_title)


@teacher_router.message(TeacherAddLessonState.waiting_for_title)
async def process_teacher_lesson_title(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(message, state)

    msg = await message.answer(
        "Введите описание занятия ⬇️",
        reply_markup=await kb.get_cancel_teacher_add_lesson_keyboard()
    )
    await state.update_data({
        'title': message.text,
        'last_bot_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(TeacherAddLessonState.waiting_for_description)


@teacher_router.message(TeacherAddLessonState.waiting_for_description)
async def process_teacher_lesson_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(message, state)

    msg = await message.answer(
        "Выберите тип занятия ⬇️",
        reply_markup=await kb.get_event_type_keyboard()
    )
    await state.update_data({
        'description': message.text,
        'last_bot_msg': msg.message_id,
        'last_keyboard_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(TeacherAddLessonState.waiting_for_type)


@teacher_router.callback_query(TeacherAddLessonState.waiting_for_type)
async def process_teacher_lesson_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    prev_msgs = data.get('prev_msgs', [])
    if 'last_bot_msg' in data:
        prev_msgs.append(data['last_bot_msg'])
    if 'last_keyboard_msg' in data:
        prev_msgs.append(data['last_keyboard_msg'])

    await state.update_data(prev_msgs=prev_msgs)
    await delete_previous_messages(callback, state)

    msg = await callback.message.answer(
        "Выберите дату для занятия ⬇️",
        reply_markup=await RussianSimpleCalendar().start_calendar(allowed_days="Пн,Вт,Ср,Чт,Пт,Сб,Вс")
    )
    await state.update_data({
        'type': callback.data,
        'last_bot_msg': msg.message_id,
        'last_keyboard_msg': msg.message_id,
        'prev_msgs': prev_msgs
    })
    await state.set_state(TeacherAddLessonState.waiting_for_date)


@teacher_router.callback_query(TeacherAddLessonState.waiting_for_date, SimpleCalendarCallback.filter())
async def process_teacher_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    current_state = await state.get_state()
    if current_state != TeacherAddLessonState.waiting_for_date.state:
        return

    try:
        if callback_data.act == "DAY":
            selected_date = datetime(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            await MessageManager.safe_delete(callback.message)
            await state.update_data(date=selected_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            await callback.message.answer(
                "Выберите время занятия:",
                reply_markup=kb.get_time_selection_keyboard()
            )
            await state.set_state(TeacherAddLessonState.waiting_for_time)

        elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            new_year, new_month = callback_data.year, callback_data.month

            if callback_data.act == "PREV-YEAR":
                new_year -= 1
            elif callback_data.act == "NEXT-YEAR":
                new_year += 1
            elif callback_data.act == "PREV-MONTH":
                new_month -= 1
                if new_month < 1:
                    new_month = 12
                    new_year -= 1
            elif callback_data.act == "NEXT-MONTH":
                new_month += 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month
                )
            )

        elif callback_data.act == "CANCEL":
            await cancel_teacher_add_lesson(callback)
            await state.clear()

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@teacher_router.callback_query(TeacherAddLessonState.waiting_for_time, F.data.startswith("teacher_lesson_time_"))
async def process_teacher_lesson_time(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    selected_time_str = callback.data.split("_")[3]
    hours, minutes = map(int, selected_time_str.split(":"))
    selected_time = time(hour=hours, minute=minutes)

    data = await state.get_data()
    selected_date = datetime.strptime(data.get("date"), '%Y-%m-%dT%H:%M:%S.%fZ').date()
    combined_datetime = datetime.combine(selected_date, selected_time)

    form_data = {
        "title": data.get("title", "string"),
        "description": data.get("description", "string"),
        "type": data.get("type", "string"),
        "teacher": f'api/users/{storage.get_user_credentials(callback.from_user.id).db_id}',
        "date": combined_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    credentials = storage.get_user_credentials(callback.from_user.id)
    success = add_lesson_to_api(credentials.email, credentials.password, form_data)

    if success:
        msg_text = (
            "✅ Занятие успешно создано!\n\n"
            f"📌 Название: {form_data['title']}\n"
            f"📝 Описание: {form_data['description']}\n"
            f"🔘 Тип: {form_data['type']}\n"
            f"📅 Дата: {combined_datetime.strftime('%d-%m-%Y %H:%M')}\n"
            f"⏰ Время: {selected_time_str}"
        )
    else:
        msg_text = "❌ Ошибка при создании занятия"

    msg = await callback.message.answer(msg_text)
    await asyncio.sleep(3)
    await MessageManager.safe_delete(msg)
    await state.clear()
    await get_teacher_lesson(callback, state)


@teacher_router.callback_query(F.data == "cancel_teacher_add_lesson")
async def cancel_teacher_add_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_teacher_lesson(callback, state)


@teacher_router.callback_query(F.data.startswith('update_teacher_lesson_'))
async def start_lesson_editing(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[3])
    lesson_data = get_lesson_by_id(lesson_id)

    lesson_dict = {
        'id': lesson_data.id,
        'title': lesson_data.title,
        'description': lesson_data.description,
        'type': lesson_data.lesson_type,
        'date': lesson_data.date,
    }

    await state.update_data(
        original_lesson=lesson_dict,
        current_lesson=lesson_dict.copy()
    )
    await show_edit_options(callback, state)
    await state.set_state(TeacherEditLessonState.waiting_for_choose)


async def show_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lesson = data['current_lesson']

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Название: {lesson.get('title')}", callback_data="edit_title")
    keyboard.button(text=f"Описание: {lesson.get('description')[:30]}...", callback_data="edit_description")
    keyboard.button(text=f"Тип: {lesson.get('type')}", callback_data="edit_type")
    keyboard.button(text=f"Дата: {datetime.fromisoformat(lesson.get('date')).strftime('%d-%m-%Y %H:%M')}",
                    callback_data="edit_date")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_editing")
    keyboard.adjust(1)

    if isinstance(update, CallbackQuery):
        await update.message.edit_text(
            "Что вы хотите изменить? (нажмите на пункт для редактирования)",
            reply_markup=keyboard.as_markup()
        )
    else:
        await update.answer(
            "Что вы хотите изменить? (нажмите на пункт для редактирования)",
            reply_markup=keyboard.as_markup()
        )

    await state.set_state(TeacherEditLessonState.waiting_for_choose)


@teacher_router.callback_query(TeacherEditLessonState.waiting_for_choose, F.data.startswith("edit_"))
async def process_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[1]
    await MessageManager.safe_delete(callback.message)

    if choice == "title":
        await callback.message.answer(
            "Введите новое название или отправьте '-' чтобы пропустить:",
            reply_markup=await kb.get_cancel_teacher_update_lesson_keyboard()
        )
        await state.set_state(TeacherEditLessonState.waiting_for_title)

    elif choice == "description":
        await callback.message.answer(
            "Введите новое описание или отправьте '-' чтобы пропустить:",
            reply_markup=await kb.get_cancel_teacher_update_lesson_keyboard()
        )
        await state.set_state(TeacherEditLessonState.waiting_for_description)

    elif choice == "type":
        await callback.message.answer(
            "Выберите новый тип занятия или нажмите 'Пропустить':",
            reply_markup=await kb.get_event_update_type_keyboard()
        )
        await state.set_state(TeacherEditLessonState.waiting_for_type)

    elif choice == "date":
        await callback.message.answer(
            "Выберите новую дату или нажмите 'Пропустить':",
            reply_markup=await RussianSimpleCalendar().start_calendar()
        )
        await state.set_state(TeacherEditLessonState.waiting_for_date)

    await callback.answer()


@teacher_router.message(TeacherEditLessonState.waiting_for_title)
async def process_edit_title(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_lesson']['title'] = message.text
        await state.update_data(current_lesson=data['current_lesson'])

    await show_edit_options(message, state)


@teacher_router.message(TeacherEditLessonState.waiting_for_description)
async def process_edit_description(message: Message, state: FSMContext):
    if message.text != '-':
        data = await state.get_data()
        data['current_lesson']['description'] = message.text
        await state.update_data(current_lesson=data['current_lesson'])

    await show_edit_options(message, state)


@teacher_router.callback_query(TeacherEditLessonState.waiting_for_type, F.data.in_(["online", "offline", "skip"]))
async def process_edit_type(callback: CallbackQuery, state: FSMContext):
    if callback.data != "skip":
        data = await state.get_data()
        data['current_lesson']['type'] = callback.data
        await state.update_data(current_lesson=data['current_lesson'])
    else:
        await callback.answer("Редактирование типа занятия пропущено")

    await show_edit_options(callback, state)


@teacher_router.callback_query(TeacherEditLessonState.waiting_for_date, SimpleCalendarCallback.filter())
async def process_edit_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    try:
        if callback_data.act == "DAY":
            selected_date = datetime(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            await MessageManager.safe_delete(callback.message)

            data = await state.get_data()
            current_lesson = data['current_lesson'].copy()
            current_lesson['date'] = selected_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            await state.update_data(current_lesson=current_lesson)

            time_keyboard = kb.get_time_selection_keyboard(with_skip=True)
            await callback.message.answer(
                f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}\n"
                "Выберите время занятия:",
                reply_markup=time_keyboard
            )
            await state.set_state(TeacherEditLessonState.waiting_for_time)

        elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            new_year, new_month = callback_data.year, callback_data.month

            if callback_data.act == "PREV-YEAR":
                new_year -= 1
            elif callback_data.act == "NEXT-YEAR":
                new_year += 1
            elif callback_data.act == "PREV-MONTH":
                new_month -= 1
                if new_month < 1:
                    new_month = 12
                    new_year -= 1
            elif callback_data.act == "NEXT-MONTH":
                new_month += 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month
                )
            )

        elif callback_data.act == "CANCEL":
            await callback.message.delete()
            await show_edit_options(callback, state)

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@teacher_router.callback_query(TeacherEditLessonState.waiting_for_time, F.data.startswith("time_"))
async def process_selected_time(callback: CallbackQuery, state: FSMContext):
    try:
        selected_time_str = callback.data.split("_")[1]
        hours, minutes = map(int, selected_time_str.split(":"))

        data = await state.get_data()
        selected_date = datetime.strptime(data['current_lesson']['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        combined_datetime = datetime.combine(selected_date, time(hour=hours, minute=minutes))

        current_lesson = data['current_lesson'].copy()
        current_lesson['date'] = combined_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        await state.update_data(current_lesson=current_lesson)

        await MessageManager.safe_delete(callback.message)
        await show_edit_options(callback, state)

    except Exception as e:
        print(f"Error processing time: {e}")
        await callback.answer("❌ Ошибка при обработке времени", show_alert=True)


@teacher_router.callback_query(F.data == "finish_editing")
async def finish_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_lesson']
    updated = data['current_lesson']

    changes = {}
    for key in ['title', 'description', 'type', 'date']:
        if original[key] != updated[key]:
            changes[key] = updated[key]

    if changes:
        changes['id'] = original['id']
        changes['teacher'] = f'api/users/{storage.get_user_credentials(callback.from_user.id).db_id}'

        credentials = storage.get_user_credentials(callback.from_user.id)
        if update_lesson_in_api(credentials.email, credentials.password, changes) == 200:
            await callback.message.answer("✅ Изменения сохранены!")
            await asyncio.sleep(2)
            await get_teacher_lesson(callback, state)
        else:
            await callback.message.answer("❌ Ошибка при сохранении изменений")
            await asyncio.sleep(2)
            await get_teacher_lesson(callback, state)
    else:
        await callback.message.answer("ℹ️ Нет изменений для сохранения")
        await asyncio.sleep(2)
        await get_teacher_lesson(callback, state)

    await state.clear()


@teacher_router.callback_query(F.data == "cancel_editing")
async def cancel_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_teacher_lesson(callback, state)


@teacher_router.callback_query(F.data == "cancel_teacher_update_lesson")
async def cancel_teacher_update_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_teacher_lesson(callback, state)


@teacher_router.callback_query(F.data == "teacher_quizzes")
async def get_teacher_quizzes(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    await callback.message.answer(text="Вот ваши тесты:",
                                  reply_markup=await kb.inline_teacher_quizzes())

    await state.set_state(TeacherQuizzesState.waiting_for_id)


@teacher_router.callback_query(TeacherQuizzesState.waiting_for_id)
async def get_teacher_quiz_by_id(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    if callback.data == "add_teacher_quiz":
        await start_add_teacher_quiz(callback, state)
    else:
        quiz_id = int(callback.data)
        quiz = get_quiz_by_id(quiz_id)

        quiz_text = f"❓ Вопрос: {quiz.question}\n\nОтветы:\n"
        for answer in quiz.answers:
            quiz_text += f" - {answer.get('answerText')} {'(верный)' if answer.get('status') else ''}\n"

        await callback.message.answer(text=quiz_text,
                                      reply_markup=await kb.quiz_action_keyboard(quiz_id))

        await state.clear()


@teacher_router.callback_query(F.data.startswith('delete_teacher_quiz_'))
async def start_delete_quiz(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    quiz_id = int(callback.data.split('_')[3])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

    result = delete_quiz_from_api(quiz_id, email, password)

    if result == 204:
        await callback.message.answer(text="✅ Тест удален")
        await asyncio.sleep(2)
        await back_to_teacher_menu(callback, state)
    else:
        await callback.message.answer(text="❌ Тест не удален")
        await asyncio.sleep(2)
        await back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data == "add_teacher_quiz")
async def start_add_teacher_quiz(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()

    msg = await callback.message.answer(
        "📝 Введите вопрос для теста:",
        reply_markup=await kb.get_cancel_teacher_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(TeacherAddQuizState.waiting_for_question)


@teacher_router.message(TeacherAddQuizState.waiting_for_question)
async def process_quiz_question(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    await MessageManager.safe_delete(message)

    await state.update_data(question=message.text, answers=[])

    msg = await message.answer(
        "➕ Введите вариант ответа (или нажмите 'Готово', если вариантов достаточно):",
        reply_markup=await kb.get_done_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(TeacherAddQuizState.waiting_for_answers)


@teacher_router.message(TeacherAddQuizState.waiting_for_answers)
async def process_quiz_answer(message: Message, state: FSMContext):
    await MessageManager.safe_delete(message)
    data = await state.get_data()
    answers = data.get('answers', [])

    if message.text.lower() == 'готово':
        if len(answers) < 2:
            await message.answer("❌ Нужно добавить минимум 2 варианта ответа!")
            return

        answer_options = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])

        try:
            await message.bot.edit_message_text(
                text=f"✅ Варианты ответов:\n{answer_options}\n\n🔢 Укажите номер правильного ответа:",
                chat_id=message.chat.id,
                message_id=data['last_bot_msg'],
                reply_markup=await kb.get_cancel_teacher_keyboard()
            )
        except TelegramBadRequest:
            msg = await message.answer(
                f"✅ Варианты ответов:\n{answer_options}\n\n🔢 Укажите номер правильного ответа:",
                reply_markup=await kb.get_cancel_teacher_keyboard()
            )
            await state.update_data(last_bot_msg=msg.message_id)

        await state.set_state(TeacherAddQuizState.waiting_for_correct_answer)
        await MessageManager.safe_delete(message)
        return

    answers.append(message.text)
    await state.update_data(answers=answers)

    current_answers = "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])

    try:
        await message.bot.edit_message_text(
            text=f"✅ Введенные варианты ответов:\n{current_answers}\n\n"
                 f"➕ Введите следующий вариант ответа или нажмите 'Готово':",
            chat_id=message.chat.id,
            message_id=data['last_bot_msg'],
            reply_markup=await kb.get_done_cancel_keyboard()
        )
    except TelegramBadRequest:
        msg = await message.answer(
            text=f"✅ Введенные варианты ответов:\n{current_answers}\n\n"
                 f"➕ Введите следующий вариант ответа или нажмите 'Готово':",
            reply_markup=await kb.get_done_cancel_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await MessageManager.safe_delete(message)


@teacher_router.callback_query(F.data == "done_answers")
async def handle_done_answers(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()

    if len(data.get('answers', [])) < 2:
        msg = await callback.message.answer("❌ Нужно добавить минимум 2 варианта ответа!")
        await asyncio.sleep(2)
        await msg.delete()
        return

    answer_options = "\n".join([f"{i+1}. {a}" for i, a in enumerate(data['answers'])])
    msg = await callback.message.answer(
        f"✅ Варианты ответов:\n{answer_options}\n\n🔢 Укажите номер правильного ответа:",
        reply_markup=await kb.get_cancel_teacher_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(TeacherAddQuizState.waiting_for_correct_answer)


@teacher_router.message(TeacherAddQuizState.waiting_for_correct_answer)
async def process_correct_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get('answers', [])

    try:
        correct_index = int(message.text) - 1
        if correct_index < 0 or correct_index >= len(answers):
            raise ValueError
    except (ValueError, IndexError):
        await message.answer("❌ Укажите корректный номер правильного ответа!")
        return

    await MessageManager.safe_delete(message)

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    quiz_data = {
        "question": data['question'],
    }

    answers = {
        "answers": [
            {
                "answerText": answer,
                "status": i == correct_index
            } for i, answer in enumerate(answers)
        ]
    }

    email = storage.get_user_credentials(message.from_user.id).email
    password = storage.get_user_credentials(message.from_user.id).password

    success = create_quiz(quiz_data, answers, email, password)

    if success == 201:
        answer_list = "\n".join(
            f"{'✅' if i == correct_index else '❌'} {i+1}. {answer.get('answerText')}"
            for i, answer in enumerate(answers.get('answers'))
        )

        success = await message.answer(
            "🎉 Тест успешно создан!\n\n"
            f"❓ Вопрос: {data['question']}\n\n"
            f"📋 Варианты ответов:\n{answer_list}"
        )
        await asyncio.sleep(2)
        await MessageManager.safe_delete(success)
        await handle_back_to_teacher_menu(message, state)
    else:
        error = await message.answer("❌ Ошибка при создании теста!")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(error)
        await handle_back_to_teacher_menu(message, state)

    await state.clear()


@teacher_router.callback_query(F.data == "cancel_quiz_creation")
async def cancel_quiz_creation(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await back_to_teacher_menu(callback, state)


@teacher_router.callback_query(F.data.startswith('update_teacher_quiz_'))
async def start_question_editing(callback: CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split('_')[3])
    question_data = get_quiz_by_id(question_id)

    question_dict = {
        'id': question_data.id,
        'question_text': question_data.question,
        'answers': [
            {
                'id': answer.get('id'),
                'answerText': answer.get('answerText'),
                'status': answer.get('status')
            } for answer in question_data.answers
        ],
    }

    await state.update_data(
        original_question=question_dict,
        current_question=question_dict.copy()
    )
    await show_question_edit_options(callback, state)
    await state.set_state(TeacherEditQuestionState.waiting_for_choose)


async def show_question_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = data['current_question']

    keyboard = InlineKeyboardBuilder()

    question_text_preview = (question.get('question_text', '')[:30] + "...") \
        if len(question.get('question_text', '')) > 30 else question.get('question_text', '')
    keyboard.button(text=f"📝 Вопрос: {question_text_preview}", callback_data="edit_question_text")

    for idx, answer in enumerate(question.get('answers', [])):
        status = "✅" if answer.get('status') else "❌"
        answer_preview = (answer.get('answerText', '')[:20] + "...")\
            if len(answer.get('answerText', '')) > 20 else answer.get('answerText', '')
        keyboard.button(text=f"{status} Ответ {idx+1}: {answer_preview}", callback_data=f"edit_answer_{idx}")

    keyboard.button(text="🔘 Выбрать правильный ответ", callback_data="select_correct_answer")

    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_question_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_question_editing")
    keyboard.adjust(1)

    text = "Что вы хотите изменить? (нажмите на пункт для редактирования)\n\n"
    text += f"📌 Вопрос: {question.get('question_text', '')}\n\n"
    text += "📋 Ответы:\n"
    for idx, answer in enumerate(question.get('answers', [])):
        status = "✅" if answer.get('status') else "❌"
        text += f"{idx+1}. {status} {answer.get('answerText', '')}\n"

    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await MessageManager.safe_delete(update)
        await update.answer(text, reply_markup=keyboard.as_markup())

    await state.set_state(TeacherEditQuestionState.waiting_for_choose)


@teacher_router.callback_query(TeacherEditQuestionState.waiting_for_choose, F.data == "edit_question_text")
async def edit_question_text_handler(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    sent_message = await callback.message.answer(
        "✏️ Введите новый текст вопроса:",
        reply_markup=await kb.get_cancel_teacher_keyboard()
    )
    await state.update_data(bot_message_to_delete=sent_message.message_id)
    await state.set_state(TeacherEditQuestionState.waiting_for_question_text)
    await callback.answer()


@teacher_router.message(TeacherEditQuestionState.waiting_for_question_text)
async def process_question_text_update(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'bot_message_to_delete' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['bot_message_to_delete'])
        except TelegramBadRequest:
            pass

    await MessageManager.safe_delete(message)

    data['current_question']['question_text'] = message.text
    await state.update_data(current_question=data['current_question'])

    confirm_msg = await message.answer(f"✅ Текст вопроса обновлен на: {message.text}")
    await asyncio.sleep(1.5)
    await MessageManager.safe_delete(confirm_msg)

    await show_question_edit_options(message, state)


@teacher_router.callback_query(TeacherEditQuestionState.waiting_for_choose, F.data.startswith("edit_answer_"))
async def process_answer_edit(callback: CallbackQuery, state: FSMContext):
    answer_idx = int(callback.data.split("_")[-1])
    await state.update_data(editing_answer_idx=answer_idx)

    await MessageManager.safe_delete(callback.message)
    sent_message = await callback.message.answer(
        f"Введите новый текст для ответа {answer_idx+1} или '-' чтобы пропустить:",
        reply_markup=await kb.get_cancel_teacher_update_question_keyboard()
    )
    await state.update_data(bot_message_to_delete=sent_message.message_id)
    await state.set_state(TeacherEditQuestionState.waiting_for_answer_text)
    await callback.answer()


@teacher_router.message(TeacherEditQuestionState.waiting_for_answer_text)
async def process_edit_answer_text(message: Message, state: FSMContext):
    data = await state.get_data()
    answer_idx = data['editing_answer_idx']

    if 'bot_message_to_delete' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['bot_message_to_delete'])
        except TelegramBadRequest:
            pass

    await MessageManager.safe_delete(message)

    if message.text != '-':
        old_id = data['current_question']['answers'][answer_idx].get('id')
        data['current_question']['answers'][answer_idx] = {
            'id': old_id,
            'answerText': message.text,
            'status': data['current_question']['answers'][answer_idx].get('status', False)
        }
        await state.update_data(current_question=data['current_question'])

        confirm_msg = await message.answer(f"✅ Ответ {answer_idx+1} обновлен на: {message.text}")
        await asyncio.sleep(1.5)
        await MessageManager.safe_delete(confirm_msg)
    else:
        skip_msg = await message.answer(f"⏭️ Ответ {answer_idx+1} пропущен")
        await asyncio.sleep(1)
        await MessageManager.safe_delete(skip_msg)

    await show_question_edit_options(message, state)


@teacher_router.callback_query(TeacherEditQuestionState.waiting_for_choose, F.data == "select_correct_answer")
async def select_correct_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answers = data['current_question'].get('answers', [])

    keyboard = InlineKeyboardBuilder()
    for idx, answer in enumerate(answers):
        keyboard.button(text=f"{idx+1}. {answer.get('answerText', '')[:15]}", callback_data=f"set_correct_{idx}")

    keyboard.button(text="↩️ Назад", callback_data="back_to_editing")
    keyboard.adjust(1)

    await callback.message.edit_text(
        "Выберите номер правильного ответа:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(TeacherEditQuestionState.waiting_for_correct_answer)
    await callback.answer()


@teacher_router.callback_query(TeacherEditQuestionState.waiting_for_correct_answer, F.data.startswith("set_correct_"))
async def process_correct_answer_selection(callback: CallbackQuery, state: FSMContext):
    correct_idx = int(callback.data.split("_")[-1])
    data = await state.get_data()

    for i, answer in enumerate(data['current_question']['answers']):
        answer['status'] = (i == correct_idx)

    await state.update_data(current_question=data['current_question'])
    await callback.answer(f"Ответ {correct_idx+1} установлен как правильный!")
    await show_question_edit_options(callback, state)


@teacher_router.callback_query(TeacherEditQuestionState.waiting_for_correct_answer, F.data == "back_to_editing")
async def back_to_editing(callback: CallbackQuery, state: FSMContext):
    await show_question_edit_options(callback, state)
    await callback.answer()


@teacher_router.callback_query(F.data == "cancel_question_editing")
async def cancel_question_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    cancel_msg = await callback.message.answer("❌ Редактирование отменено")
    await asyncio.sleep(1.5)
    await MessageManager.safe_delete(cancel_msg)

    await handle_back_to_teacher_menu(callback, state)
    await state.clear()
    await callback.answer()


@teacher_router.callback_query(F.data == "finish_question_editing")
async def finish_question_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_question']
    updated = data['current_question']
    credentials = storage.get_user_credentials(callback.from_user.id)

    update_data = {
        'id': original['id'],
        'question_text': updated['question_text'],
        'answers': [
            {
                'id': answer.get('id'),
                'answerText': answer.get('answerText'),
                'status': answer.get('status')
            } for answer in updated['answers']
        ]
    }

    has_changes = (
            original['question_text'] != updated['question_text'] or
            any(
                orig['answerText'] != upd['answerText'] or
                orig['status'] != upd['status'] or
                orig.get('id') != upd.get('id')
                for orig, upd in zip(original['answers'], updated['answers'])
            )
    )

    await MessageManager.safe_delete(callback.message)

    if not has_changes:
        no_changes_msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(no_changes_msg)
        await handle_back_to_teacher_menu(callback, state)
        await state.clear()
        return

    loading_msg = await callback.message.answer("💾 Сохранение изменений...")

    response = update_question_in_api(
        credentials.email,
        credentials.password,
        update_data
    )

    await MessageManager.safe_delete(loading_msg)

    if response == 200:
        answer_info = "\n".join(
            f"ID {answer.get('id')}: {'✅' if answer['status'] else '❌'} {answer['answerText']}"
            for answer in updated['answers']
        )

        success_msg = await callback.message.answer(
            f"✅ Вопрос ID {original['id']} обновлен!\n\n"
            f"📌 Текст: {updated['question_text']}\n\n"
            f"📋 Ответы:\n{answer_info}"
        )
        await asyncio.sleep(3)
        await MessageManager.safe_delete(success_msg)
        await handle_back_to_teacher_menu(callback, state)
    else:
        error_msg = await callback.message.answer("❌ Ошибка при сохранении изменений")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(error_msg)
        await handle_back_to_teacher_menu(callback, state)

    await state.clear()


@teacher_router.callback_query(F.data == "cancel_question_editing")
async def cancel_question_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await get_teacher_quizzes(callback, state)


@teacher_router.callback_query(F.data == "student_progress")
async def get_student_list(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    await callback.message.answer("Вот все студенты ⬇️",
                                  reply_markup=await kb.teacher_all_student())

    await state.set_state(CheckTeacherStudentProgress.waiting_for_id)


@teacher_router.callback_query(CheckTeacherStudentProgress.waiting_for_id)
async def check_student_progress_by_id(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)

    student_id = int(callback.data)
    credentials = storage.get_user_credentials(callback.from_user.id)
    progress = get_student_progress_by_id(student_id, credentials.email, credentials.password)

    text = (
        f"✅ Студент {student_id}\n\n"
    )
    for course in progress['combinedProgress']['byCourse']:
        text += (
            f"{course.get('courseTitle')}\n"
            f"📝 Прогресс по занятиям: {course['details']['lessons']['percentage']}\n"
            f"📋 Прогресс по тестам: {course['details']['quizzes']['correctPercentage']}\n\n")

    await callback.message.answer(text=text,
                                  reply_markup=await kb.get_teacher_student_progress())

    await state.clear()
