import asyncio
import logging
import re
from datetime import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, URLInputFile, FSInputFile, Message

from app.APIhandlers.APIhandlersAutodrome import get_autodrome_by_id
from app.APIhandlers.APIhandlersCar import get_admin_car_by_id, delete_car, update_car_in_api, add_car_to_api
from app.APIhandlers.APIhandlersInstructor import get_instructor_by_id
from app.APIhandlers.APIhandlersLesson import  get_lesson_title
from app.APIhandlers.APIhandlersSchedule import delete_schedule_from_api, \
    get_admin_drive_schedule_by_id, update_schedule, add_schedule
from app.APIhandlers.APIhandlersUser import get_user_by_id, delete_user, update_user_by_admin, get_user_name, \
    add_user_by_admin
from app.APIhandlers.APIhandlersCourse import get_course_by_id, delete_course, get_quiz_title, \
    update_course_in_api, user_ids_in_course, add_course_to_api
from app.APIhandlers.APIhandlersCategory import get_category_by_id, get_admin_category_by_id, add_category_to_api, delete_category, \
    update_category_in_api
from app.handlers.handlers import AllUsersStates, EditStudentFromAdminStates, \
    EditInstructorFromAdminStates, EditTeacherFromAdminStates, AllCoursesStates, UpdateCourseStates, AddCourseStates, \
    AllCategoryStates, AddCategoryStates, UpdateCategoryStates, AddUserStates, AllSchedulesStates, EditScheduleStates, \
    AllCarsStates, EditCarStates, AddScheduleStates, AddCarStates
from app.keyboards.keyboard import inline_admin_lessons_by_course
from app.utils.jsons_creator import UserStorage
from config_local import profile_photos
import app.keyboards.static_keyboard as static_kb
import app.keyboards.keyboard as kb

admin_router = Router()

storage = UserStorage()

JSON_DATA_DIR = "data/json/"


@admin_router.callback_query(F.data == "admin_info")
async def admin_info(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user = storage.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    info_text = (
        f"🧑‍🎓 Информация о вас:\n\n"
        f"▫️ <b>Фамилия:</b> {user.surname or 'не указана'}\n"
        f"▫️ <b>Имя:</b> {user.name or 'не указано'}\n"
        f"▫️ <b>Отчество:</b> {user.patronymic or 'не указано'}"
    )

    if hasattr(user, 'image') and user.image and user.image != 'static/img/default.png':
        try:
            try:
                await callback.message.answer_photo(
                    photo=URLInputFile(f"{profile_photos}{user.image}"),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.admin_info
                )
                return
            except Exception as url_error:
                print(f"URL send failed, trying FSInputFile: {url_error}")
                await callback.message.answer_photo(
                    photo=FSInputFile(user.image),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.admin_info
                )
                return
        except Exception as e:
            print(f"Both photo sending methods failed: {e}")

    await callback.message.answer(
        info_text,
        parse_mode='HTML',
        reply_markup=static_kb.admin_info
    )


async def handle_back_to_admin_menu(message: Message, user_id):
    user = storage.get_user(user_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Админ',
        reply_markup=static_kb.admin_main
    )


@admin_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    user = storage.get_user(callback.from_user.id)
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await callback.message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await callback.message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Админ',
        reply_markup=static_kb.admin_main
    )


@admin_router.callback_query(F.data == "users_list")
async def get_user_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все пользователи которые есть в системе:",
                                  reply_markup=await kb.all_users_list())

    await state.set_state(AllUsersStates.waiting_for_id)


@admin_router.callback_query(AllUsersStates.waiting_for_id)
async def handle_user_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_user":
        await start_adding_user(callback, state)
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        user_id = callback.data

        user = get_user_by_id(user_id=int(user_id))

        if "ROLE_STUDENT" in user['roles']:
            category_title = 'Не указано'
            if user.get('category'):
                category_title = user['category'].get('title', 'Не указано')

            await callback.message.answer(
                text=f"<b>ID: {user['id']}</b>\n\n"
                     f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                     f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                     f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                     f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                     f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n"
                     f"<b>Категория:</b> {category_title}\n\n",
                parse_mode="HTML",
                reply_markup=await kb.inline_user_action(user['id'], user['roles'])
            )
        elif "ROLE_INSTRUCTOR" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user['roles']))
        elif "ROLE_TEACHER" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user['roles']))
        elif "ROLE_ADMIN" in user['roles']:
            await callback.message.answer(text=f"<b>ID: {user['id']}</b>\n\n"
                                               f"<b>Имя:</b> {user.get('name', 'Не указано')}\n\n"
                                               f"<b>Фамилия:</b> {user.get('surname', 'Не указано')}\n\n"
                                               f"<b>Отчество:</b> {user.get('patronym', 'Не указано')}\n\n"
                                               f"<b>Телефон:</b> {user.get('phone', 'Не указано')}\n\n"
                                               f"<b>Email:</b> {user.get('email', 'Не указано')}\n\n",
                                          parse_mode="HTML",
                                          reply_markup=await kb.inline_user_action(user['id'], user['roles']))

        await state.clear()


@admin_router.callback_query(F.data == "add_user")
async def start_adding_user(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите роль нового пользователя:",
        reply_markup=kb.get_user_roles_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_role)


@admin_router.callback_query(AddUserStates.waiting_for_role, F.data.startswith("ROLE_"))
async def process_role_selection(callback: CallbackQuery, state: FSMContext):
    role = callback.data

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(role=role)

    new_msg = await callback.message.answer(
        "Введите фамилию нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_surname)


@admin_router.message(AddUserStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Введите имя нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_name)

@admin_router.message(AddUserStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(name=message.text)

    new_msg = await message.answer(
        "Введите отчество нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_patronymic)

@admin_router.message(AddUserStates.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(patronymic=message.text)

    new_msg = await message.answer(
        "Введите email нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_email)

@admin_router.message(AddUserStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if not validate_email(message.text):
        error_msg = await message.answer("Некорректный email. Пожалуйста, введите правильный email:")
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(email=message.text)

    new_msg = await message.answer(
        "Введите пароль для нового пользователя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.waiting_for_password)

@admin_router.message(AddUserStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 6:
        error_msg = await message.answer("Пароль должен содержать минимум 6 символов. Введите пароль снова:")
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(password=message.text)

    data = await state.get_data()
    role_display = {
        "STUDENT": "Студент",
        "INSTRUCTOR": "Инструктор",
        "TEACHER": "Учитель"
    }.get(data['role'], data['role'])

    confirm_text = (
        "Проверьте данные нового пользователя:\n\n"
        f"Роль: {role_display}\n"
        f"ФИО: {data.get('surname')} {data.get('name')} {data.get('patronymic')}\n"
        f"Email: {data.get('email')}\n"
        f"Пароль: {'*' * len(data.get('password', ''))}\n\n"
        "Всё верно?"
    )

    new_msg = await message.answer(
        confirm_text,
        reply_markup=static_kb.confirm_user_addition
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddUserStates.confirmation)


@admin_router.callback_query(AddUserStates.confirmation, F.data == "confirm_user_addition")
async def finalize_user_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    admin_id = callback.from_user.id
    admin_email = storage.get_user(admin_id).email
    admin_password = storage.get_credentials(admin_id).password

    result = add_user_by_admin(
        role=data['role'],
        surname=data['surname'],
        name=data['name'],
        patronymic=data['patronymic'],
        email=data['email'],
        password=data['password'],
        admin_email=admin_email,
        admin_password=admin_password
    )

    if result == 201:  # 201 Created
        success_msg = await callback.message.answer("Пользователь успешно добавлен!")
        await asyncio.sleep(2)
        try:
            await success_msg.delete()
        except TelegramBadRequest:
            pass
    else:
        error_msg = await callback.message.answer("Ошибка при добавлении пользователя!")
        await asyncio.sleep(2)
        try:
            await error_msg.delete()
        except TelegramBadRequest:
            pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(AddUserStates.confirmation, F.data == "cancel_user_addition")
async def cancel_user_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    cancel_msg = await callback.message.answer("Добавление пользователя отменено")
    await asyncio.sleep(2)
    try:
        await cancel_msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


async def delete_previous_messages(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass


@admin_router.callback_query(F.data.startswith("update_user"))
async def start_editing(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите новую фамилию ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    user_id = int(callback.data.split('-')[0][12:])
    user_role = callback.data.split('-')[1]

    if user_role == "ROLE_STUDENT":
        await state.set_state(EditStudentFromAdminStates.waiting_for_surname)
    if user_role == "ROLE_INSTRUCTOR":
        await state.set_state(EditInstructorFromAdminStates.waiting_for_surname)
    if user_role == "ROLE_TEACHER":
        await state.set_state(EditTeacherFromAdminStates.waiting_for_surname)

    await state.update_data(last_bot_msg=new_msg.message_id,
                            user_id=user_id)


#СТУДЕНТЫ


@admin_router.message(EditStudentFromAdminStates.waiting_for_surname)
async def process_student_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentFromAdminStates.waiting_for_name)


@admin_router.message(EditStudentFromAdminStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditStudentFromAdminStates.waiting_for_patronymic)
async def process_student_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user(telegram_user_id).id
    user_pass = storage.get_credentials(telegram_user_id).password
    user_email = storage.get_user(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    if update == 200:
            result_msg = await message.answer("Данные успешно обновлены!")

            await asyncio.sleep(1)
            try:
                await result_msg.delete()
            except TelegramBadRequest:
                pass
            await state.clear()
            await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


# ИНСТРУКТОРА


@admin_router.message(EditInstructorFromAdminStates.waiting_for_surname)
async def process_instructor_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditInstructorFromAdminStates.waiting_for_name)


@admin_router.message(EditInstructorFromAdminStates.waiting_for_name)
async def process_instructor_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditInstructorFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditInstructorFromAdminStates.waiting_for_patronymic)
async def process_instructor_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user(telegram_user_id).id
    user_pass = storage.get_credentials(telegram_user_id).password
    user_email = storage.get_user(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    print(update)
    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


#УЧИТЕЛЯ


@admin_router.message(EditTeacherFromAdminStates.waiting_for_surname)
async def process_teacher_surname(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить предыдущее сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(surname=message.text)

    new_msg = await message.answer(
        "Теперь введите новое имя ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditTeacherFromAdminStates.waiting_for_name)


@admin_router.message(EditTeacherFromAdminStates.waiting_for_name)
async def process_teacher_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(name=message.text)
    new_msg = await message.answer(
        "Теперь введите новое отчество ⬇️",
        reply_markup=await kb.get_cancel_admin_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditTeacherFromAdminStates.waiting_for_patronymic)


@admin_router.message(EditTeacherFromAdminStates.waiting_for_patronymic)
async def process_teacher_patronymic(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest as e:
            logging.debug(f"Не удалось удалить сообщение бота: {e}")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения бота: {e}")

    try:
        await message.delete()
    except TelegramBadRequest as e:
        logging.debug(f"Не удалось удалить сообщение пользователя: {e}")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    await state.update_data(patronymic=message.text)

    telegram_user_id = message.from_user.id
    user = storage.get_user(telegram_user_id)

    if not user:
        await message.answer("Ошибка: данные пользователя не найдены")
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
        return

    user_id = storage.get_user(telegram_user_id).id
    user_pass = storage.get_credentials(telegram_user_id).password
    user_email = storage.get_user(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_by_admin(
        user_id=user_data.get('user_id'),
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    if update == 200:
        result_msg = await message.answer("Данные успешно обновлены!")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_admin_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_admin_menu(message, user_id)


#ВЫХОД ИЗ РЕДАКТИРОВАНИЯ


@admin_router.callback_query(F.data == "cancel_admin_edit")
async def get_cancel_admin_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            logging.debug("Сообщение для удаления не найдено (last_bot_msg)")
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        logging.debug("Сообщение для удаления не найдено (callback.message)")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    cancel_msg = await callback.message.answer("Редактирование отменено")

    try:
        await cancel_msg.delete()
    except TelegramBadRequest:
        logging.debug("Не удалось удалить сообщение об отмене")
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения об отмене: {e}")

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("delete_user_"))
async def start_delete(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = int(callback.data.split('_')[2])

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    delete_result = delete_user(user_id, email, password)

    if delete_result == 204:
        await callback.message.answer(text=f"Пользователь {user_id} успешно удален")
        await asyncio.sleep(2)
        await get_user_list(callback, state)
    else:
        await callback.message.answer(text="Ошибка удаления пользователя")
        await asyncio.sleep(2)
        await get_user_list(callback, state)


@admin_router.callback_query(F.data == "courses_list")
async def get_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот список всех курсов:",
                                  reply_markup=await kb.inline_admin_courses())

    await state.set_state(AllCoursesStates.waiting_for_id)


@admin_router.callback_query(AllCoursesStates.waiting_for_id)
async def admin_course_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_course":
        await start_adding_course(callback, state)
    else:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        course_id = int(callback.data)
        course = get_course_by_id(course_id=course_id)

        if not course:
            await callback.message.answer("🚫 Курс не найден")
            return

        await callback.message.answer(text=f"<b>ID: {course.id}</b>\n\n"
                                           f"<b>Название:</b> {course.title}\n\n"
                                           f"<b>Описание:</b> {course.description or "Нет описания"}\n\n"
                                           f"<b>Занятия и тесты на курсе:</b>\n\n",
                                      parse_mode="HTML",
                                      reply_markup=await inline_admin_lessons_by_course(course_id))

        await state.set_state(AllCoursesStates.waiting_for_lesson_id)


@admin_router.callback_query(F.data.startswith("delete_course_"))
async def delete_admin_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = int(callback.data.split('_')[2])
    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    delete_result = delete_course(course_id=course_id, email=email, password=password)

    if delete_result == 204:
        result = await callback.message.answer(text=f"Курс {course_id} успешно удален")
        await asyncio.sleep(2)
        await result.delete()
        await get_courses_list(callback, state)
    else:
        result = await callback.message.answer(text="Ошибка удаления курса")
        await asyncio.sleep(2)
        await result.delete()
        await get_courses_list(callback, state)


@admin_router.callback_query(F.data.startswith("update_course_"))
async def start_updating_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = int(callback.data.split('_')[2])
    await state.update_data(course_id=course_id)

    new_msg = await callback.message.answer(
        "Введите новое название курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_title)


@admin_router.message(UpdateCourseStates.waiting_for_title)
async def process_course_title(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(title=message.text)
    new_msg = await message.answer(
        "Введите новое описание курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_description)


@admin_router.message(UpdateCourseStates.waiting_for_description)
async def process_course_description(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)
    await state.update_data(description=message.text)

    new_msg = await message.answer(
        "Выберите уроки для курса ⬇️",
        reply_markup=await kb.inline_course_lessons()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_lessons)


@admin_router.callback_query(UpdateCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def select_lessons(callback: CallbackQuery, state: FSMContext):

    lesson_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_lessons = data.get('selected_lessons', [])

    if lesson_id in selected_lessons:
        selected_lessons.remove(lesson_id)
    else:
        selected_lessons.append(lesson_id)

    await state.update_data(selected_lessons=selected_lessons)
    await callback.answer(f"Урок {'добавлен' if lesson_id in selected_lessons else 'удален'}")


@admin_router.callback_query(UpdateCourseStates.waiting_for_lessons, F.data == "continue")
async def process_lessons_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    course_id = data.get('course_id')

    users_in_course = user_ids_in_course(course_id)

    new_msg = await callback.message.answer(
        "Выберите пользователей для курса ⬇️",
        reply_markup=await kb.inline_course_users(users_in_course)
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_users)


@admin_router.callback_query(UpdateCourseStates.waiting_for_users, F.data.startswith("user_"))
async def select_users(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_users = data.get('selected_users', [])

    if user_id in selected_users:
        selected_users.remove(user_id)
    else:
        selected_users.append(user_id)

    await state.update_data(selected_users=selected_users)
    await callback.answer(f"Пользователь {'добавлен' if user_id in selected_users else 'удален'}")


@admin_router.callback_query(UpdateCourseStates.waiting_for_users, F.data == "continue")
async def process_users_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите категорию курса ⬇️",
        reply_markup=await kb.inline_course_categories()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_category)


@admin_router.callback_query(UpdateCourseStates.waiting_for_category, F.data.startswith("category_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(category_id=category_id)

    new_msg = await callback.message.answer(
        "Введите цену курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCourseStates.waiting_for_price)

@admin_router.message(UpdateCourseStates.waiting_for_price)
async def process_course_price(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)
    try:
        price = float(message.text)
        await state.update_data(price=price)

        new_msg = await message.answer(
            "Выберите тесты для курса ⬇️",
            reply_markup=await kb.inline_course_quizzes()
        )
        await state.update_data(last_bot_msg=new_msg.message_id)
        await state.set_state(UpdateCourseStates.waiting_for_quizzes)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену (число)")

@admin_router.callback_query(UpdateCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def select_quizzes(callback: CallbackQuery, state: FSMContext):
    quiz_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_quizzes = data.get('selected_quizzes', [])

    if quiz_id in selected_quizzes:
        selected_quizzes.remove(quiz_id)
    else:
        selected_quizzes.append(quiz_id)

    await state.update_data(selected_quizzes=selected_quizzes)
    await callback.answer(f"Тест {'добавлен' if quiz_id in selected_quizzes else 'удален'}")


@admin_router.callback_query(UpdateCourseStates.waiting_for_quizzes, F.data == "continue")
async def confirm_course_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    message_text = (
            "Проверьте данные курса:\n\n"
            f"Название: {data.get('title')}\n"
            f"Описание: {data.get('description')}\n"
            f"Цена: {data.get('price')}\n\n"
            "Выбранные уроки:\n" + "\n".join([get_lesson_title(lesson_id) for lesson_id in data.get('selected_lessons', [])]) + "\n\n"
            "Выбранные пользователи:\n" + "\n".join([get_user_name(user_id) for user_id in data.get('selected_users', [])]) + "\n\n"
            "Выбранные тесты:\n" + "\n".join([get_quiz_title(quiz_id) for quiz_id in data.get('selected_quizzes', [])])
    )

    await callback.message.answer(
        message_text,
        reply_markup=static_kb.confirm_course_update
    )
    await state.set_state(UpdateCourseStates.confirmation)


@admin_router.callback_query(UpdateCourseStates.confirmation, F.data == "confirm_update")
async def finalize_course_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    update_result = update_course_in_api(
        course_id=data['course_id'],
        title=data['title'],
        description=data['description'],
        lessons=data.get('selected_lessons', []),
        users=data.get('selected_users', []),
        category=data.get('category_id'),
        price=data.get('price'),
        quizzes=data.get('selected_quizzes', []),
        email=email,
        password=password
    )

    if update_result == 200:
        result = await callback.message.answer("Курс успешно обновлен!")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)
    else:
        result = await callback.message.answer("Ошибка при обновлении курса")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)

    await state.clear()


@admin_router.callback_query(UpdateCourseStates.confirmation, F.data == "cancel_update")
async def cancel_course_update(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    result = await callback.message.answer("Обновление курса отменено")
    await asyncio.sleep(2)
    await result.delete()
    await state.clear()


@admin_router.callback_query(F.data == "add_course")
async def start_adding_course(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите название нового курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(
        last_bot_msg=new_msg.message_id,
        selected_lessons=[],
        selected_users=[],
        selected_quizzes=[]
    )
    await state.set_state(AddCourseStates.waiting_for_title)

@admin_router.message(AddCourseStates.waiting_for_title)
async def process_course_title(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(title=message.text)
    new_msg = await message.answer(
        "Введите описание нового курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_description)

@admin_router.message(AddCourseStates.waiting_for_description)
async def process_course_description(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)
    await state.update_data(description=message.text)

    new_msg = await message.answer(
        "Выберите уроки для нового курса ⬇️",
        reply_markup=await kb.inline_course_lessons()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_lessons)

@admin_router.callback_query(AddCourseStates.waiting_for_lessons, F.data.startswith("lesson_"))
async def select_lessons(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_lessons = data.get('selected_lessons', [])

    if lesson_id in selected_lessons:
        selected_lessons.remove(lesson_id)
    else:
        selected_lessons.append(lesson_id)

    await state.update_data(selected_lessons=selected_lessons)
    await callback.answer(f"Урок {'добавлен' if lesson_id in selected_lessons else 'удален'}")

@admin_router.callback_query(AddCourseStates.waiting_for_lessons, F.data == "continue")
async def process_lessons_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите пользователей для нового курса ⬇️",
        reply_markup=await kb.inline_course_users([])
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_users)

@admin_router.callback_query(AddCourseStates.waiting_for_users, F.data.startswith("user_"))
async def select_users(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_users = data.get('selected_users', [])

    if user_id in selected_users:
        selected_users.remove(user_id)
    else:
        selected_users.append(user_id)

    await state.update_data(selected_users=selected_users)
    await callback.answer(f"Пользователь {'добавлен' if user_id in selected_users else 'удален'}")

@admin_router.callback_query(AddCourseStates.waiting_for_users, F.data == "continue")
async def process_users_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Выберите категорию для нового курса ⬇️",
        reply_markup=await kb.inline_course_categories()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_category)

@admin_router.callback_query(AddCourseStates.waiting_for_category, F.data.startswith("category_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(category_id=category_id)

    new_msg = await callback.message.answer(
        "Введите цену нового курса ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCourseStates.waiting_for_price)

@admin_router.message(AddCourseStates.waiting_for_price)
async def process_course_price(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)
    try:
        price = float(message.text)
        await state.update_data(price=price)

        new_msg = await message.answer(
            "Выберите тесты для нового курса ⬇️",
            reply_markup=await kb.inline_course_quizzes()
        )
        await state.update_data(last_bot_msg=new_msg.message_id)
        await state.set_state(AddCourseStates.waiting_for_quizzes)
    except ValueError:
        error_msg = await message.answer("Пожалуйста, введите корректную цену (число)")
        await state.update_data(last_bot_msg=error_msg.message_id)

@admin_router.callback_query(AddCourseStates.waiting_for_quizzes, F.data.startswith("quiz_"))
async def select_quizzes(callback: CallbackQuery, state: FSMContext):
    quiz_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_quizzes = data.get('selected_quizzes', [])

    if quiz_id in selected_quizzes:
        selected_quizzes.remove(quiz_id)
    else:
        selected_quizzes.append(quiz_id)

    await state.update_data(selected_quizzes=selected_quizzes)
    await callback.answer(f"Тест {'добавлен' if quiz_id in selected_quizzes else 'удален'}")

@admin_router.callback_query(AddCourseStates.waiting_for_quizzes, F.data == "continue")
async def confirm_course_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    message_text = (
            "Проверьте данные нового курса:\n\n"
            f"Название: {data.get('title')}\n"
            f"Описание: {data.get('description')}\n"
            f"Цена: {data.get('price')}\n\n"
            "Выбранные уроки:\n" + "\n".join([get_lesson_title(lesson_id) for lesson_id in data.get('selected_lessons', [])]) + "\n\n"
            "Выбранные пользователи:\n" + "\n".join([get_user_name(user_id) for user_id in data.get('selected_users', [])]) + "\n\n"
                                                                                                                                                                                                                                                  "Выбранные тесты:\n" + "\n".join([get_quiz_title(quiz_id) for quiz_id in data.get('selected_quizzes', [])])
    )

    await callback.message.answer(
        message_text,
        reply_markup=static_kb.confirm_course_addition
    )
    await state.set_state(AddCourseStates.confirmation)

@admin_router.callback_query(AddCourseStates.confirmation, F.data == "confirm_addition")
async def finalize_course_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    add_result = add_course_to_api(
        title=data['title'],
        description=data['description'],
        lessons=data.get('selected_lessons', []),
        users=data.get('selected_users', []),
        category=data.get('category_id'),
        price=data.get('price'),
        quizzes=data.get('selected_quizzes', []),
        email=email,
        password=password
    )

    if add_result == 201:
        result = await callback.message.answer("Новый курс успешно добавлен!")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)
    else:
        result = await callback.message.answer("Ошибка при добавлении курса")
        await asyncio.sleep(2)
        await result.delete()
        await back_to_admin_menu(callback, state)

    await state.clear()

@admin_router.callback_query(AddCourseStates.confirmation, F.data == "cancel_addition")
async def cancel_course_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    result = await callback.message.answer("Добавление курса отменено")
    await asyncio.sleep(2)
    await result.delete()
    await state.clear()


@admin_router.callback_query(F.data == "category_list")
async def get_category_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот какие категории есть в системе:",
                                  reply_markup=await kb.inline_admin_category())

    await state.set_state(AllCategoryStates.waiting_for_id)


@admin_router.callback_query(AllCategoryStates.waiting_for_id, F.data.startswith("admin_category_"))
async def handle_get_admin_category_by_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    category = get_admin_category_by_id(category_id)

    if not category:
        await callback.message.answer(text="Нет категорий",
                                      reply_markup=static_kb.add_category)

    await callback.message.answer(text=f"Категория {category.id}\n\n"
                                  f"<b>Название:</b> {category.title}\n"
                                  f"<b>Фамилия:</b> {category.description}\n\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.category_action(category_id))

    await state.clear()


@admin_router.callback_query(F.data == "add_category")
async def start_adding_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    new_msg = await callback.message.answer(
        "Введите название новой категории:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_title)

@admin_router.message(AddCategoryStates.waiting_for_title)
async def process_category_title(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(title=message.text)

    new_msg = await message.answer(
        "Введите описание категории:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(AddCategoryStates.waiting_for_description)

@admin_router.message(AddCategoryStates.waiting_for_description)
async def process_category_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(description=message.text)
    category_data = await state.get_data()

    email = storage.get_user(message.from_user.id).email
    password = storage.get_credentials(message.from_user.id).password

    result = add_category_to_api(
        title=category_data['title'],
        description=category_data['description'],
        email=email,
        password=password
    )

    if result == 201:
        success_msg = await message.answer("Категория успешно добавлена!")
    else:
        success_msg = await message.answer("Ошибка при добавлении категории")

    await asyncio.sleep(2)
    try:
        await success_msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await handle_back_to_admin_menu(message, message.from_user.id)


@admin_router.callback_query(F.data.startswith("delete_category_"))
async def start_delete_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    result = delete_category(category_id, email, password)

    if result == 204:
        result = await callback.message.answer(text="Категория удалена")
        await asyncio.sleep(2)
        await result.delete()
        await get_category_list(callback, state)
    else:
        result = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result.delete()
        await get_category_list(callback, state)


@admin_router.callback_query(F.data.startswith("update_category_"))
async def start_updating_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    category = get_category_by_id(category_id)

    if not category:
        await callback.message.answer("Категория не найдена")
        return

    await state.update_data(
        category_id=category_id,
        current_title=category.title,
        current_description=category.description
    )

    new_msg = await callback.message.answer(
        f"Введите новое название или нажмите ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCategoryStates.waiting_for_title)

@admin_router.message(UpdateCategoryStates.waiting_for_title, F.text)
async def process_update_title(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(title=message.text)

    new_msg = await message.answer(
        f"Введите новое описание ⬇️",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(UpdateCategoryStates.waiting_for_description)

@admin_router.message(UpdateCategoryStates.waiting_for_description, F.text)
async def process_update_description(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'last_bot_msg' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_bot_msg']
            )
        except TelegramBadRequest:
            pass

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(description=message.text)

    category_data = await state.get_data()
    email = storage.get_user(message.from_user.id).email
    password = storage.get_credentials(message.from_user.id).password

    result = update_category_in_api(
        category_id=category_data['category_id'],
        title=category_data.get('title'),
        description=category_data.get('description'),
        email=email,
        password=password
    )

    if result == 200:
        success_msg = await message.answer("Категория успешно обновлена!")
    else:
        success_msg = await message.answer("Ошибка при обновлении категории")

    await asyncio.sleep(2)
    try:
        await success_msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await handle_back_to_admin_menu(message, message.from_user.id)


@admin_router.callback_query(F.data == "schedules_list")
async def get_schedule_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все расписания в системе ⬇️",
                                  reply_markup=await kb.inline_admin_schedules())

    await state.set_state(AllSchedulesStates.waiting_for_id)


@admin_router.callback_query(AllSchedulesStates.waiting_for_id)
async def get_admin_schedule_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "schedules_list":
        await get_schedule_list(callback, state)
    elif callback.data == "add_schedule":
        await start_adding_schedule(callback, state)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data)
    schedule = get_admin_drive_schedule_by_id(schedule_id)

    if not schedule:
        await callback.message.answer("🕒 Расписание не найдено")
        await state.clear()
        return

    autodrome = get_autodrome_by_id(schedule.autodrome_id)
    category = get_category_by_id(schedule.category_id)
    instructor = get_instructor_by_id(schedule.instructor_id)
    days = ', '.join(schedule.days_of_week) if isinstance(schedule.days_of_week, list) else schedule.days_of_week

    await callback.message.answer(text=f"📅 Информация о расписании {schedule_id}:\n\n"
                                  f"⏱ Время: {datetime.fromisoformat(schedule.time_from).strftime('%H:%M')} - "
                                  f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}\n\n"
                                  f"📆 Дни: {days}\n\n"
                                  f"🏁 Автодром: {autodrome.title}\n\n"
                                  f"📋 Категория: {category.title}\n\n"
                                  f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.inline_schedule_action(schedule_id))

    await state.clear()


@admin_router.callback_query(F.data.startswith('delete_schedule_'))
async def delete_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[2])
    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password
    result = delete_schedule_from_api(schedule_id, email, password)

    if result == 204:
        result_msg = await callback.message.answer(text="Удаление успешно")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)
    else:
        result_msg = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)


# Начало редактирования расписания (админ)
@admin_router.callback_query(F.data.startswith("update_schedule_"))
async def admin_start_schedule_edit(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[2])
    schedule = get_admin_drive_schedule_by_id(schedule_id)

    if not schedule:
        await callback.message.answer("Расписание не найдено")
        await state.clear()
        return

    await state.update_data(
        schedule_id=schedule_id,
        current_time_from=schedule.time_from,
        current_time_to=schedule.time_to,
        current_days=schedule.days_of_week,
        current_notice=schedule.notice,
        current_autodrome=schedule.autodrome_id,
        current_category=schedule.category_id,
        current_instructor=schedule.instructor_id,
        selected_days=[]
    )

    msg = await callback.message.answer(
        "Выберите время начала занятия:",
        reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}from")
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.waiting_for_time_from)

@admin_router.callback_query(
    EditScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}from_")
)
async def admin_process_time_from(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()

    await state.update_data(time_from=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(EditScheduleStates.waiting_for_time_to)

@admin_router.callback_query(
    EditScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}to_")
)
async def admin_process_time_to(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    time_from = datetime.fromisoformat(data['time_from']).time()
    if time_obj <= time_from:
        await callback.answer("Время окончания должно быть позже времени начала!")
        return

    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()
    await state.update_data(time_to=iso_time)

    current_days = data.get('current_days', "")
    if isinstance(current_days, list):
        current_days = ", ".join(current_days)

    try:
        msg = await callback.message.edit_text(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard(current_days.split(", ") if current_days else [])
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard(current_days.split(", ") if current_days else [])
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(EditScheduleStates.waiting_for_days)

@admin_router.callback_query(
    EditScheduleStates.waiting_for_days,
    F.data.startswith(kb.ADMIN_DAY_PREFIX)
)
async def admin_process_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.ADMIN_DAY_PREFIX, "")
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.get_admin_days_keyboard(selected_days)
    )
    await callback.answer()

@admin_router.callback_query(
    EditScheduleStates.waiting_for_days,
    F.data == kb.ADMIN_DONE_PREFIX
)
async def admin_process_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    # Сохраняем дни как строку через запятую
    days_str = ", ".join(selected_days)
    await state.update_data(days_of_week=days_str)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        "Текущее примечание: " + (data['current_notice'] if data['current_notice'] else "отсутствует") +
        "\n\nВведите новое примечание или отправьте '-' чтобы оставить текущее:",
        reply_markup=await kb.get_cancel_schedule_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.waiting_for_notice)

@admin_router.message(EditScheduleStates.waiting_for_notice)
async def process_notice(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    data = await state.get_data()
    notice = message.text if message.text != '-' else data['current_notice']
    await state.update_data(notice=notice)

    msg = await message.answer(
        "Выберите автодром:",
        reply_markup=await kb.inline_schedule_edit_autodrome()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.waiting_for_autodrome)

@admin_router.callback_query(EditScheduleStates.waiting_for_autodrome, F.data.startswith("autodrome_"))
async def process_autodrome(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    autodrome_id = int(callback.data.split('_')[1])
    await state.update_data(autodrome=f"api/autodromes/{autodrome_id}")

    msg = await callback.message.answer(
        "Выберите категорию:",
        reply_markup=await kb.inline_schedule_edit_category()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.waiting_for_category)

@admin_router.callback_query(EditScheduleStates.waiting_for_category, F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[1])
    await state.update_data(category=f"api/categories/{category_id}")

    msg = await callback.message.answer(
        "Выберите инструктора:",
        reply_markup=await kb.inline_schedule_edit_instructors()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.waiting_for_instructor)

@admin_router.callback_query(EditScheduleStates.waiting_for_instructor, F.data.startswith("instructor_"))
async def process_instructor(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructor_id = int(callback.data.split('_')[1])
    await state.update_data(instructor=f"api/users/{instructor_id}")

    data = await state.get_data()

    time_from = datetime.fromisoformat(data.get('time_from', data['current_time_from'])).strftime('%H:%M')
    time_to = datetime.fromisoformat(data.get('time_to', data['current_time_to'])).strftime('%H:%M')
    days = data.get('days_of_week', data['current_days'])
    notice = data.get('notice', data['current_notice']) or "отсутствует"

    autodrome = get_autodrome_by_id(
        int(data['autodrome'].split('/')[-1]) if 'autodrome' in data else data['current_autodrome'])
    category = get_category_by_id(
        int(data['category'].split('/')[-1]) if 'category' in data else data['current_category'])
    instructor = get_instructor_by_id(
        int(data['instructor'].split('/')[-1]) if 'instructor' in data else data['current_instructor'])

    confirm_text = (
        "Проверьте данные расписания:\n\n"
        f"🕒 Время: {time_from} - {time_to}\n"
        f"📆 Дни: {days}\n"
        f"📝 Примечание: {notice}\n"
        f"🏁 Автодром: {autodrome.title}\n"
        f"📋 Категория: {category.title}\n"
        f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
        "Подтвердить изменения?"
    )

    msg = await callback.message.answer(
        confirm_text,
        reply_markup=await kb.confirm_schedule_update_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(EditScheduleStates.confirmation)

@admin_router.callback_query(EditScheduleStates.confirmation, F.data == "confirm_schedule_update")
async def finalize_schedule_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    schedule_data = {
        "timeFrom": data.get('time_from', data['current_time_from']),
        "timeTo": data.get('time_to', data['current_time_to']),
        "daysOfWeek": data.get('days_of_week', data['current_days']),
        "notice": data.get('notice', data['current_notice']),
        "autodrome": data.get('autodrome', f"api/autodromes/{data['current_autodrome']}"),
        "category": data.get('category', f"api/categories/{data['current_category']}"),
        "instructor": data.get('instructor', f"api/users/{data['current_instructor']}")
    }

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    success = update_schedule(data['schedule_id'], schedule_data, email, password)

    if success == 200:
        await callback.message.edit_text("✅ Расписание успешно обновлено!")
    else:
        await callback.message.edit_text("❌ Ошибка при обновлении расписания!")

    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_schedule_edit")
async def cancel_schedule_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Редактирование расписания отменено")
    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_schedule")
async def start_adding_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(
        selected_days=[],
        notice=None
    )

    msg = await callback.message.answer(
        "Выберите время начала занятия:",
        reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}from")
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_time_from)

@admin_router.callback_query(
    AddScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}from_")
)
async def process_time_from(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()

    await state.update_data(time_from=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_admin_time_keyboard(f"{kb.ADMIN_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddScheduleStates.waiting_for_time_to)

@admin_router.callback_query(
    AddScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.ADMIN_TIME_PREFIX}to_")
)
async def process_time_to(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    time_from = datetime.fromisoformat(data['time_from']).time()
    if time_obj <= time_from:
        await callback.answer("Время окончания должно быть позже времени начала!")
        return

    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()
    await state.update_data(time_to=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_admin_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddScheduleStates.waiting_for_days)

@admin_router.callback_query(
    AddScheduleStates.waiting_for_days,
    F.data.startswith(kb.ADMIN_DAY_PREFIX)
)
async def process_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.ADMIN_DAY_PREFIX, "")
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.get_admin_days_keyboard(selected_days)
    )
    await callback.answer()

@admin_router.callback_query(
    AddScheduleStates.waiting_for_days,
    F.data == kb.ADMIN_DONE_PREFIX
)
async def process_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    days_str = ", ".join(selected_days)
    await state.update_data(days_of_week=days_str)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        "Введите примечание (или отправьте '-' чтобы не добавлять):",
        reply_markup=await kb.get_cancel_schedule_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_notice)

@admin_router.message(AddScheduleStates.waiting_for_notice)
async def process_notice(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    notice = message.text if message.text != '-' else None
    await state.update_data(notice=notice)

    msg = await message.answer(
        "Выберите автодром:",
        reply_markup=await kb.inline_schedule_edit_autodrome()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_autodrome)

@admin_router.callback_query(AddScheduleStates.waiting_for_autodrome, F.data.startswith("autodrome_"))
async def process_autodrome(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    autodrome_id = int(callback.data.split('_')[1])
    await state.update_data(autodrome=f"api/autodromes/{autodrome_id}")

    msg = await callback.message.answer(
        "Выберите категорию:",
        reply_markup=await kb.inline_schedule_edit_category()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_category)

@admin_router.callback_query(AddScheduleStates.waiting_for_category, F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[1])
    await state.update_data(category=f"api/categories/{category_id}")

    msg = await callback.message.answer(
        "Выберите инструктора:",
        reply_markup=await kb.inline_schedule_edit_instructors()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.waiting_for_instructor)

@admin_router.callback_query(AddScheduleStates.waiting_for_instructor, F.data.startswith("instructor_"))
async def process_instructor(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    instructor_id = int(callback.data.split('_')[1])
    await state.update_data(instructor=f"api/users/{instructor_id}")

    data = await state.get_data()

    time_from = datetime.fromisoformat(data['time_from']).strftime('%H:%M')
    time_to = datetime.fromisoformat(data['time_to']).strftime('%H:%M')
    days = data['days_of_week']
    notice = data.get('notice', 'отсутствует')

    autodrome = get_autodrome_by_id(int(data['autodrome'].split('/')[-1]))
    category = get_category_by_id(int(data['category'].split('/')[-1]))
    instructor = get_instructor_by_id(int(data['instructor'].split('/')[-1]))

    confirm_text = (
        "Проверьте данные нового расписания:\n\n"
        f"🕒 Время: {time_from} - {time_to}\n"
        f"📆 Дни: {days}\n"
        f"📝 Примечание: {notice}\n"
        f"🏁 Автодром: {autodrome.title}\n"
        f"📋 Категория: {category.title}\n"
        f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
        "Создать расписание?"
    )

    msg = await callback.message.answer(
        confirm_text,
        reply_markup=await kb.confirm_schedule_add_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddScheduleStates.confirmation)

@admin_router.callback_query(AddScheduleStates.confirmation, F.data == "confirm_schedule_addition")
async def finalize_schedule_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    schedule_data = {
        "timeFrom": data['time_from'],
        "timeTo": data['time_to'],
        "daysOfWeek": data['days_of_week'],
        "notice": data.get('notice'),
        "autodrome": data['autodrome'],
        "category": data['category'],
        "instructor": data['instructor']
    }

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    success = add_schedule(schedule_data, email, password)

    if success == 201:
        await callback.message.edit_text("✅ Расписание успешно создано!")
    else:
        await callback.message.edit_text("❌ Ошибка при создании расписания!")

    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)

@admin_router.callback_query(F.data == "cancel_schedule_addition")
async def cancel_schedule_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Создание расписания отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "auto_list")
async def get_auto_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(text="Вот все авто в системе ⬇️",
                                  reply_markup=await kb.admin_inline_cars())

    await state.set_state(AllCarsStates.waiting_for_id)


@admin_router.callback_query(AllCarsStates.waiting_for_id)
async def get_auto_admin_by_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "add_car":
        await start_adding_car(callback, state)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data)
    car = get_admin_car_by_id(car_id)

    await callback.message.answer(text=f"🧑‍🏫 Информация об автомобиле {car_id}:\n\n"
                                       f"▫️ <b>Марка:</b> {car.carMark}\n"
                                       f"▫️ <b>Модель:</b> {car.carModel}\n"
                                       f"▫️ <b>Номер:</b> {car.stateNumber}\n",
                                  parse_mode="HTML",
                                  reply_markup=await kb.cars_action(car_id))

    await state.clear()


@admin_router.callback_query(F.data.startswith('delete_car_'))
async def delete_car_by_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data.split('_')[2])
    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    result = delete_car(car_id, email, password)

    if result == 204:
        result_msg = await callback.message.answer(text="Удаление успешно")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)
    else:
        result_msg = await callback.message.answer(text="Удаление не удалось")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "add_car")
async def start_adding_car(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data(
        carModel=None,
        stateNumber=None,
        productionYear=None,
        vinNumber=None
    )

    msg = await callback.message.answer(
        "Введите модель автомобиля:",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_model)

@admin_router.message(AddCarStates.waiting_for_model)
async def process_car_model(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(carModel=message.text)

    msg = await message.answer(
        "Введите гос. номер (например, А123БВ777):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_number)

@admin_router.message(AddCarStates.waiting_for_number)
async def process_state_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 6 or len(message.text) > 9:
        error_msg = await message.answer(
            "Номер должен содержать от 6 до 9 символов. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(stateNumber=message.text.upper())

    msg = await message.answer(
        "Введите год выпуска (например, 2020):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_year)

@admin_router.message(AddCarStates.waiting_for_year)
async def process_production_year(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    try:
        year = int(message.text)
        current_year = datetime.now().year

        if year < 1980 or year > current_year + 1:
            raise ValueError
    except ValueError:
        current_year = datetime.now().year
        error_msg = await message.answer(
            f"Год должен быть числом между 1980 и {current_year + 1}. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(productionYear=str(year))

    msg = await message.answer(
        "Введите VIN номер (17 символов):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.waiting_for_vin)

@admin_router.message(AddCarStates.waiting_for_vin)
async def process_vin_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    vin = message.text.upper().strip()

    if len(vin) != 17 or not all(c.isalnum() for c in vin):
        error_msg = await message.answer(
            "VIN должен содержать ровно 17 букв и цифр. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(vinNumber=vin)

    data = await state.get_data()

    confirm_text = (
        "Проверьте данные автомобиля:\n\n"
        f"🚗 Модель: {data['carModel']}\n"
        f"🔢 Гос. номер: {data['stateNumber']}\n"
        f"📅 Год выпуска: {data['productionYear']}\n"
        f"🔎 VIN: {data['vinNumber']}\n\n"
        "Всё верно?"
    )

    msg = await message.answer(
        confirm_text,
        reply_markup=await kb.confirm_car_addition_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddCarStates.confirmation)

@admin_router.callback_query(AddCarStates.confirmation, F.data == "confirm_car_addition")
async def finalize_car_addition(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_data = {
        "carModel": data['carModel'],
        "stateNumber": data['stateNumber'],
        "productionYear": data['productionYear'],
        "vinNumber": data['vinNumber']
    }

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    success = add_car_to_api(car_data, email, password)

    if success == 201:
        msg = await callback.message.answer("✅ Автомобиль успешно добавлен!")
    else:
        msg = await callback.message.answer("❌ Ошибка при добавлении автомобиля!")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)

@admin_router.callback_query(F.data == "cancel_car_addition")
async def cancel_car_addition(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Добавление автомобиля отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data.startswith("update_car_"))
async def start_updating_car(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_id = int(callback.data.split('_')[2])
    car = get_admin_car_by_id(car_id)

    if not car:
        await callback.message.answer("Автомобиль не найден")
        await state.clear()
        return

    await state.update_data(
        car_id=car_id,
        current_model=car.carModel,
        current_number=car.stateNumber,
        current_year=car.productionYear,
        current_vin=car.vinNumber
    )

    new_msg = await callback.message.answer(
        "Введите новую модель автомобиля:",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditCarStates.waiting_for_model)


@admin_router.message(EditCarStates.waiting_for_model)
async def process_car_model(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    await state.update_data(carModel=message.text)

    new_msg = await message.answer(
        "Введите новый гос. номер (например, А123БВ777):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditCarStates.waiting_for_number)


@admin_router.message(EditCarStates.waiting_for_number)
async def process_state_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    if len(message.text) < 6 or len(message.text) > 9:
        error_msg = await message.answer(
            "Номер должен содержать от 6 до 9 символов. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(stateNumber=message.text.upper())

    new_msg = await message.answer(
        "Введите год выпуска (например, 2020):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditCarStates.waiting_for_year)


@admin_router.message(EditCarStates.waiting_for_year)
async def process_production_year(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    try:
        year = int(message.text)
        current_year = datetime.now().year

        if year < 1980 or year > current_year + 1:
            raise ValueError
    except ValueError:
        current_year = datetime.now().year
        error_msg = await message.answer(
            f"Год должен быть числом между 1980 и {current_year + 1}. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(productionYear=str(year))

    new_msg = await message.answer(
        "Введите VIN номер (17 символов):",
        reply_markup=await kb.get_cancel_car_edit_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditCarStates.waiting_for_vin)


@admin_router.message(EditCarStates.waiting_for_vin)
async def process_vin_number(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    vin = message.text.upper().strip()

    if len(vin) != 17 or not all(c.isalnum() for c in vin):
        error_msg = await message.answer(
            "VIN должен содержать ровно 17 букв и цифр. Попробуйте снова:",
            reply_markup=await kb.get_cancel_car_edit_keyboard()
        )
        await state.update_data(last_bot_msg=error_msg.message_id)
        return

    await state.update_data(vinNumber=vin)

    data = await state.get_data()

    confirm_text = (
        "Проверьте данные автомобиля:\n\n"
        f"🚗 Модель: {data.get('carModel', data['current_model'])}\n"
        f"🔢 Гос. номер: {data.get('stateNumber', data['current_number'])}\n"
        f"📅 Год выпуска: {data.get('productionYear', data['current_year'])}\n"
        f"🔎 VIN: {data.get('vinNumber', data['current_vin'])}\n\n"
        "Всё верно?"
    )

    new_msg = await message.answer(
        confirm_text,
        reply_markup=await kb.confirm_car_update_buttons()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditCarStates.confirmation)


@admin_router.callback_query(EditCarStates.confirmation, F.data == "confirm_car_update")
async def finalize_car_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    car_data = {
        "carModel": data.get('carModel', data['current_model']),
        "stateNumber": data.get('stateNumber', data['current_number']),
        "productionYear": data.get('productionYear', data['current_year']),
        "vinNumber": data.get('vinNumber', data['current_vin'])
    }

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    success = update_car_in_api(data['car_id'], car_data, email, password)

    if success == 200:
        msg = await callback.message.answer("✅ Данные автомобиля успешно обновлены!")
    else:
        msg = await callback.message.answer("❌ Ошибка при обновлении данных!")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)


@admin_router.callback_query(F.data == "cancel_car_edit")
async def cancel_car_edit(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Редактирование автомобиля отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_admin_menu(callback, state)

