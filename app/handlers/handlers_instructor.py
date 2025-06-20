import asyncio
import re
from copy import deepcopy
from datetime import datetime, date

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendarCallback

from app.APIhandlers.APIhandlersAutodrome import get_autodrome_by_id
from app.APIhandlers.APIhandlersCategory import get_category_by_id, get_price_by_category_id
from app.APIhandlers.APIhandlersDriveLesson import get_instructor_lesson_by_id, delete_instructor_lesson_from_api, \
    create_instructor_lesson, update_instructor_lesson
from app.APIhandlers.APIhandlersInstructor import get_instructor_by_id
from app.APIhandlers.APIhandlersSchedule import (instructor_drive_schedule, delete_schedule_from_api,
                                                 get_drive_schedule_by_id, update_schedule, add_schedule)
from app.APIhandlers.APIhandlersUser import get_user_by_id
from app.calendar import RussianSimpleCalendar
from app.handlers.handlers import (EditInstructorScheduleStates, AddInstructorScheduleStates,
                                   InstructorDriveLessonState, AddInstructorLessonStates, EditInstructorLessonStates)
from app.handlers.handlers_admin import delete_previous_messages
from app.handlers.handlers_teacher import MessageManager
from app.keyboards import static_keyboard as static_kb
from app.keyboards import keyboard as kb
from app.utils.jsons_creator import UserStorage
from config_local import profile_photos

instructor_router = Router()
storage = UserStorage()

JSON_DATA_DIR = "data/json/"
DEFAULT_PROFILE_PHOTO = "static/img/default.jpg"


async def handle_back_to_instructor_menu(update: Message | CallbackQuery, state: FSMContext) -> None:
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
        f'Привет, {user.get("surname", "")} {user.get("name", "")}, Ваша роль Инструктор',
        reply_markup=static_kb.instructor_main
    )


@instructor_router.callback_query(F.data == "instructor_info")
async def get_instructor_info(callback: CallbackQuery) -> None:
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
        reply_markup=static_kb.instructor_info
    )


@instructor_router.callback_query(F.data == "back_to_instructor_menu")
async def back_to_instructor_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await handle_back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "instructor_schedule")
async def instructor_schedule_by_id(callback: CallbackQuery):
    await MessageManager.safe_delete(callback.message)

    user_id = storage.get_user_credentials(callback.from_user.id).db_id
    schedule = instructor_drive_schedule(user_id)

    if schedule == 0:
        await callback.message.answer("Расписание не найдено",
                                      reply_markup=await kb.inline_no_schedule_action())
        return

    autodrome = get_autodrome_by_id(schedule.autodrome_id)
    category = get_category_by_id(schedule.category_id)
    instructor = get_instructor_by_id(schedule.instructor_id)
    price = get_price_by_category_id(schedule.category_id)
    days = ', '.join(schedule.days_of_week) if isinstance(schedule.days_of_week, list) else schedule.days_of_week

    await callback.message.answer(text=f"📅 Информация о расписании {schedule.id}:\n\n"
                                       f"⏱ Время: {datetime.fromisoformat(schedule.time_from).strftime('%H:%M')} - "
                                       f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}\n\n"
                                       f"📆 Дни: {days}\n\n"
                                       f"🏁 Автодром: {autodrome.title}\n\n"
                                       f"📋 Категория: {category.title}\n\n"
                                       f"👤 Инструктор: {instructor.surname} {instructor.name}"
                                       f" {instructor.patronymic}\n\n"
                                       f"💲 Цена: {price} ₽ \n\n",
                                       parse_mode="HTML",
                                       reply_markup=await kb.inline_instuctor_schedule_action(schedule.id))


@instructor_router.callback_query(F.data.startswith('delete_instructor_schedule_'))
async def delete_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[3])
    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password
    result = delete_schedule_from_api(schedule_id, email, password)

    if result == 204:
        result_msg = await callback.message.answer(text="✅ Удаление успешно")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_instructor_menu(callback, state)
    else:
        result_msg = await callback.message.answer(text="❌ Удаление не удалось")
        await asyncio.sleep(2)
        await result_msg.delete()
        await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data.startswith("update_instructor_schedule_"))
async def start_updating_instructor_schedule(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    schedule_id = int(callback.data.split('_')[3])
    schedule = get_drive_schedule_by_id(schedule_id)

    if not schedule:
        await callback.message.answer("Расписание не найдено")
        return

    days = schedule.days_of_week
    if isinstance(days, str):
        days = [d.strip() for d in days.split(",")] if days else []

    schedule_dict = {
        'id': schedule.id,
        'time_from': schedule.time_from,
        'time_to': schedule.time_to,
        'days_of_week': days.copy(),
        'notice': schedule.notice,
        'autodrome_id': schedule.autodrome_id,
        'category_id': schedule.category_id,
        'instructor_id': schedule.instructor_id
    }

    await state.update_data(
        original_schedule=deepcopy(schedule_dict),
        current_schedule=deepcopy(schedule_dict)
    )

    await show_admin_schedule_edit_options(callback, state)
    await state.set_state(EditInstructorScheduleStates.waiting_for_choose)


async def show_admin_schedule_edit_options(update: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    schedule = data['current_schedule']

    autodrome = get_autodrome_by_id(schedule.get('autodrome_id'))
    category = get_category_by_id(schedule.get('category_id'))

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Время начала: {datetime.fromisoformat(schedule.get('time_from')).strftime('%H:%M')}",
                    callback_data="edit_schedule_instructor_time_from")
    keyboard.button(text=f"Время окончания: {datetime.fromisoformat(schedule.get('time_to')).strftime('%H:%M')}",
                    callback_data="edit_schedule_instructor_time_to")
    keyboard.button(text=f"Дни недели: {schedule.get('days_of_week')}", callback_data="edit_schedule_instructor_days")
    keyboard.button(text=f"Примечание: {schedule.get('notice', 'отсутствует')[:20]}...",
                    callback_data="edit_schedule_instructor_notice")
    keyboard.button(text=f"Автодром: {autodrome.title if autodrome else 'Не указан'}",
                    callback_data="edit_schedule_instructor_autodrome")
    keyboard.button(text=f"Категория: {category.title if category else 'Не указана'}",
                    callback_data="edit_schedule_instructor_category")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_schedule_editing_instructor")
    keyboard.button(text="❌ Отменить", callback_data="cancel_instructor_schedule_edit")
    keyboard.adjust(1)

    try:
        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
    except TelegramBadRequest:
        if isinstance(update, CallbackQuery):
            await update.message.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )
        else:
            await update.answer(
                "Что вы хотите изменить в расписании? (нажмите на пункт для редактирования)",
                reply_markup=keyboard.as_markup()
            )

    await state.set_state(EditInstructorScheduleStates.waiting_for_choose)


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_choose,
    F.data.startswith("edit_schedule_instructor_")
)
async def process_admin_schedule_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[3:]
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    print(choice)
    if choice == ['time', 'from']:
        msg = await callback.message.answer(
            "Выберите время начала занятия:",
            reply_markup=await kb.get_instructor_time_keyboard(f"{kb.INSTRUCTOR_TIME_PREFIX}from")
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_time_from)

    elif choice == ['time', 'to']:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_instructor_time_keyboard(f"{kb.INSTRUCTOR_TIME_PREFIX}to")
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_time_to)

    elif choice == ['days']:
        data = await state.get_data()
        current_days = data['current_schedule'].get('days_of_week', "")
        if isinstance(current_days, str):
            current_days = [d.strip() for d in current_days.split(",")] if current_days else []
        print(current_days)
        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_instructor_days_keyboard(current_days if current_days else [])
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_days)

    elif choice == ["notice"]:
        msg = await callback.message.answer(
            "Введите новое примечание или отправьте '-' чтобы оставить текущее:",
            reply_markup=await kb.get_cancel_instructor_schedule_edit_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_notice)

    elif choice == ["autodrome"]:
        msg = await callback.message.answer(
            "Выберите автодром:",
            reply_markup=await kb.inline_instructor_schedule_edit_autodrome()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_autodrome)

    elif choice == ["category"]:
        msg = await callback.message.answer(
            "Выберите категорию:",
            reply_markup=await kb.inline_instructor_schedule_edit_category()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorScheduleStates.waiting_for_category)

    await callback.answer()


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.INSTRUCTOR_TIME_PREFIX}from_")
)
async def process_instructor_time_from(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    current_time_to = datetime.fromisoformat(data['current_schedule']['time_to']).time()

    if time_obj >= current_time_to:
        msg = await callback.message.answer("Время начала должно быть раньше времени окончания!")
        await asyncio.sleep(3)
        await MessageManager.safe_delete(msg)
        return

    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()
    data['current_schedule']['time_from'] = iso_time
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.INSTRUCTOR_TIME_PREFIX}to_")
)
async def process_instructor_time_to(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    current_time_from = datetime.fromisoformat(data['current_schedule']['time_from']).time()

    if time_obj <= current_time_from:
        msg = await callback.message.answer("Время окончания должно быть позже времени начала!")
        await asyncio.sleep(3)
        await MessageManager.safe_delete(msg)
        return

    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()
    data['current_schedule']['time_to'] = iso_time
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_days,
    F.data.startswith(kb.INSTRUCTOR_DAY_PREFIX))
async def process_instructor_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.INSTRUCTOR_DAY_PREFIX, "")
    data = await state.get_data()

    current_days = data['current_schedule'].get('days_of_week', [])
    if isinstance(current_days, str):
        current_days = [d.strip() for d in current_days.split(",")] if current_days else []

    if day in current_days:
        current_days.remove(day)
        action = "удален"
    else:
        current_days.append(day)
        action = "добавлен"

    day_order = {'Пн': 0, 'Вт': 1, 'Ср': 2, 'Чт': 3, 'Пт': 4, 'Сб': 5, 'Вс': 6}
    current_days_sorted = sorted(current_days, key=lambda x: day_order.get(x, 7))

    data['current_schedule']['days_of_week'] = current_days_sorted
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.edit_reply_markup(
        reply_markup=await kb.get_instructor_days_keyboard(current_days_sorted)
    )
    await callback.answer(f"День {action}")


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_days,
    F.data == kb.INSTRUCTOR_DONE_PREFIX
)
async def process_instructor_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data['current_schedule'].get('days_of_week', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@instructor_router.message(EditInstructorScheduleStates.waiting_for_notice)
async def process_admin_notice(message: Message, state: FSMContext):

    data = await state.get_data()

    if 'last_message_id' in data:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=data['last_message_id']
            )
        except TelegramBadRequest:
            pass

    notice = message.text if message.text != '-' else None

    data['current_schedule']['notice'] = notice
    await state.update_data(current_schedule=data['current_schedule'])

    await MessageManager.safe_delete(message)
    await show_admin_schedule_edit_options(message, state)


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_autodrome,
    F.data.startswith("instructor_autodrome_")
)
async def process_admin_autodrome(callback: CallbackQuery, state: FSMContext):
    autodrome_id = int(callback.data.split('_')[2])

    data = await state.get_data()
    data['current_schedule']['autodrome_id'] = autodrome_id
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@instructor_router.callback_query(
    EditInstructorScheduleStates.waiting_for_category,
    F.data.startswith("instructor_category_")
)
async def process_admin_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[2])

    data = await state.get_data()
    data['current_schedule']['category_id'] = category_id
    await state.update_data(current_schedule=data['current_schedule'])

    await callback.message.delete()
    await show_admin_schedule_edit_options(callback, state)


@instructor_router.callback_query(F.data == "finish_schedule_editing_instructor")
async def finalize_admin_schedule_update(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_schedule']
    updated = data['current_schedule']

    def normalize_days(days):
        if days is None:
            return []
        if isinstance(days, str):
            return [d.strip() for d in days.split(",")] if days else []
        return days

    original_days = normalize_days(original['days_of_week'])
    updated_days = normalize_days(updated['days_of_week'])

    days_changed = set(original_days) != set(updated_days)

    changes = {}
    if days_changed:
        changes['days_of_week'] = updated_days

    for field in ['time_from', 'time_to', 'notice', 'autodrome_id', 'category_id']:
        if original[field] != updated[field]:
            changes[field] = updated[field]

    if changes:
        schedule_data = {
            "timeFrom": updated['time_from'],
            "timeTo": updated['time_to'],
            "daysOfWeek": ",".join(updated_days),
            "notice": updated['notice'],
            "autodrome": f"api/autodromes/{updated['autodrome_id']}",
            "category": f"api/categories/{updated['category_id']}"
        }

        credentials = storage.get_user_credentials(callback.from_user.id)
        update_result = update_schedule(
            schedule_id=original['id'],
            json=schedule_data,
            email=credentials.email,
            password=credentials.password
        )

        if update_result == 200:
            msg = await callback.message.answer("✅ Расписание успешно обновлено!")
        else:
            msg = await callback.message.answer("❌ Ошибка при обновлении расписания")
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")

    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "cancel_instructor_schedule_edit")
async def cancel_schedule_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Редактирование расписания отменено")
    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "add_instructor_schedule")
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
        reply_markup=await kb.get_instructor_time_keyboard(f"{kb.INSTRUCTOR_TIME_PREFIX}from")
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddInstructorScheduleStates.waiting_for_time_from)


@instructor_router.callback_query(
    AddInstructorScheduleStates.waiting_for_time_from,
    F.data.startswith(f"{kb.INSTRUCTOR_TIME_PREFIX}from_")
)
async def process_time_from(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split('_')[3]
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    iso_time = datetime.combine(datetime.today(), time_obj).isoformat()

    await state.update_data(time_from=iso_time)

    try:
        msg = await callback.message.edit_text(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_instructor_time_keyboard(f"{kb.INSTRUCTOR_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите время окончания занятия:",
            reply_markup=await kb.get_instructor_time_keyboard(f"{kb.INSTRUCTOR_TIME_PREFIX}to")
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddInstructorScheduleStates.waiting_for_time_to)


@instructor_router.callback_query(
    AddInstructorScheduleStates.waiting_for_time_to,
    F.data.startswith(f"{kb.INSTRUCTOR_TIME_PREFIX}to_")
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
            reply_markup=await kb.get_instructor_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)
    except TelegramBadRequest:
        msg = await callback.message.answer(
            "Выберите дни проведения занятий:",
            reply_markup=await kb.get_instructor_days_keyboard()
        )
        await state.update_data(last_bot_msg=msg.message_id)

    await state.set_state(AddInstructorScheduleStates.waiting_for_days)


@instructor_router.callback_query(
    AddInstructorScheduleStates.waiting_for_days,
    F.data.startswith(kb.INSTRUCTOR_DAY_PREFIX)
)
async def process_day_selection(callback: CallbackQuery, state: FSMContext):
    day = callback.data.replace(kb.INSTRUCTOR_DAY_PREFIX, "")
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    await state.update_data(selected_days=selected_days)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.get_instructor_days_keyboard(selected_days)
    )
    await callback.answer()


@instructor_router.callback_query(
    AddInstructorScheduleStates.waiting_for_days,
    F.data == kb.INSTRUCTOR_DONE_PREFIX
)
async def process_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if not selected_days:
        await callback.answer("Нужно выбрать хотя бы один день!")
        return

    days_str = ",".join(selected_days)
    await state.update_data(days_of_week=days_str)

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer(
        "Введите примечание (или отправьте '-' чтобы не добавлять):",
        reply_markup=await kb.get_cancel_instructor_schedule_edit_keyboard()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddInstructorScheduleStates.waiting_for_notice)


@instructor_router.message(AddInstructorScheduleStates.waiting_for_notice)
async def process_notice(message: Message, state: FSMContext):
    await delete_previous_messages(message, state)

    notice = message.text if message.text != '-' else None
    await state.update_data(notice=notice)

    msg = await message.answer(
        "Выберите автодром:",
        reply_markup=await kb.inline_instructor_schedule_edit_autodrome()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddInstructorScheduleStates.waiting_for_autodrome)


@instructor_router.callback_query(AddInstructorScheduleStates.waiting_for_autodrome,
                                  F.data.startswith("instructor_autodrome_"))
async def process_autodrome(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    autodrome_id = int(callback.data.split('_')[2])
    await state.update_data(autodrome=f"api/autodromes/{autodrome_id}")

    msg = await callback.message.answer(
        "Выберите категорию:",
        reply_markup=await kb.inline_instructor_schedule_edit_category()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddInstructorScheduleStates.waiting_for_category)


@instructor_router.callback_query(AddInstructorScheduleStates.waiting_for_category,
                                  F.data.startswith("instructor_category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    category_id = int(callback.data.split('_')[2])
    await state.update_data(category=f"api/categories/{category_id}")

    instructor_id = storage.get_user_credentials(callback.from_user.id).db_id
    await state.update_data(instructor=f"api/users/{instructor_id}")

    data = await state.get_data()

    time_from = datetime.fromisoformat(data['time_from']).strftime('%H:%M')
    time_to = datetime.fromisoformat(data['time_to']).strftime('%H:%M')
    days = data['days_of_week']
    notice = data.get('notice', 'отсутствует')

    autodrome = get_autodrome_by_id(int(data['autodrome'].split('/')[-1]))
    category = get_category_by_id(int(data['category'].split('/')[-1]))
    instructor = get_instructor_by_id(instructor_id)

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
        reply_markup=await kb.confirm_instructor_schedule_add_buttons()
    )
    await state.update_data(last_bot_msg=msg.message_id)
    await state.set_state(AddInstructorScheduleStates.confirmation)


@instructor_router.callback_query(AddInstructorScheduleStates.confirmation,
                                  F.data == "confirm_instructor_schedule_addition")
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

    email = storage.get_user_credentials(callback.from_user.id).email
    password = storage.get_user_credentials(callback.from_user.id).password

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
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "cancel_instructor_schedule_addition")
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
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "instructor_my_lessons")
async def get_instructors_lessons(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_id = storage.get_user_credentials(callback.from_user.id).db_id
    credentials = storage.get_user_credentials(callback.from_user.id)

    await callback.message.answer(text="Вот все ваши занятия ⬇️",
                                  reply_markup=await kb.inline_instructor_drive_lessons(user_id, credentials.email,
                                                                                        credentials.password))

    await state.set_state(InstructorDriveLessonState.waiting_for_id)


@instructor_router.callback_query(InstructorDriveLessonState.waiting_for_id)
async def get_instructors_lesson_by_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    if callback.data == "add_instructor_lesson":
        await start_add_instructor_lesson(callback, state)
    else:
        lesson_id = int(callback.data)
        credentials = storage.get_user_credentials(callback.from_user.id)
        lesson = get_instructor_lesson_by_id(lesson_id, credentials.email, credentials.password)

        info_text = (
            f"🧑‍🎓 Урок вождения {lesson.id}:\n\n"
            f"▫️ <b>Дата:</b> {datetime.fromisoformat(lesson.date).strftime("%Y-%m-%d %H:%M")}\n"
            f"▫️ <b>Инструктор:</b> {lesson.instructor.get('surname')} {lesson.instructor.get('name')}"
            f" {lesson.instructor.get('patronym', '')}\n"
            f"▫️ <b>Студент:</b> {lesson.student.get('surname')} {lesson.student.get('name')}"
            f" {lesson.student.get('patronym', '')}\n"
            f"▫️ <b>Автодром:</b> {lesson.autodrome.get('title')}\n"
            f"▫️ <b>Категория</b> {lesson.category.get('masterTitle')}"
        )

        await callback.message.answer(text=info_text,
                                      parse_mode="HTML",
                                      reply_markup=await kb.instructor_lesson_actions(lesson_id))

    await state.clear()


@instructor_router.callback_query(F.data.startswith('delete_instructor_lesson_'))
async def delete_instructor_lesson(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    lesson_id = int(callback.data.split('_')[3])
    credentials = storage.get_user_credentials(callback.from_user.id)

    result = delete_instructor_lesson_from_api(lesson_id, credentials.email, credentials.password)

    if result == 204:
        msg = await callback.message.answer("✅ Урок вождения удален")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_instructor_menu(callback, state)
    else:
        msg = await callback.message.answer("❌ Ошибка удаления")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)
        await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "add_instructor_lesson")
async def start_add_instructor_lesson(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.update_data({
        "instructor": f"api/users/{callback.from_user.id}",
        "student": None,
        "date": None,
        "autodrome": None,
        "category": None
    })

    msg = await callback.message.answer(
        "📅 Выберите дату урока:",
        reply_markup=await RussianSimpleCalendar().start_calendar()
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(AddInstructorLessonStates.waiting_for_date)
    print(await state.get_state())


@instructor_router.callback_query(
    AddInstructorLessonStates.waiting_for_date,
    SimpleCalendarCallback.filter()
)
async def process_add_lesson_date(
        callback: CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
):
    try:
        if callback_data.act == "DAY":
            selected_date = date(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            if selected_date < datetime.now().date():
                await callback.answer("❌ Нельзя выбрать прошедшую дату!", show_alert=True)
                return

            date_str = selected_date.strftime('%Y-%m-%d')
            await state.update_data(date=date_str)

            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            msg = await callback.message.answer(
                f"📅 Выбрана дата: {selected_date.strftime('%d.%m.%Y')}\n"
                "🕒 Выберите время начала урока:",
                reply_markup=kb.get_time_selection_keyboard_instructor_lesson()
            )
            await state.update_data(last_message_id=msg.message_id)
            await state.set_state(AddInstructorLessonStates.waiting_for_time)

        elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            calendar = RussianSimpleCalendar()
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
                reply_markup=await calendar.start_calendar(
                    year=new_year,
                    month=new_month
                )
            )

        elif callback_data.act == "CANCEL":
            await cancel_lesson_creation(callback, state)

    except Exception as e:
        print(f"Error processing calendar: {e}")
        await callback.answer("❌ Ошибка при обработке календаря", show_alert=True)


@instructor_router.callback_query(
    AddInstructorLessonStates.waiting_for_time,
    F.data.startswith("instructor_lesson_time_")
)
async def process_lesson_time(callback: CallbackQuery, state: FSMContext):
    try:
        time_str = callback.data.replace("instructor_lesson_time_", "")

        if not re.match(r"^\d{2}:\d{2}$", time_str):
            raise ValueError("Invalid time format")

        data = await state.get_data()
        if not data.get('date'):
            raise ValueError("Date not selected")

        await state.update_data(time=time_str)

        msg = await callback.message.edit_text(
            f"🕒 Выбрано время: {time_str}\n"
            "🏁 Выберите автодром:",
            reply_markup=await kb.get_autodromes_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(AddInstructorLessonStates.waiting_for_autodrome)

    except Exception as e:
        print(f"Error processing time: {e}")
        await callback.answer("❌ Ошибка при выборе времени", show_alert=True)
        await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(
    AddInstructorLessonStates.waiting_for_autodrome,
    F.data.startswith("autodrome_")
)
async def process_lesson_autodrome(callback: CallbackQuery, state: FSMContext):
    autodrome_id = callback.data.split("_")[1]
    await state.update_data(autodrome=f"api/autodromes/{autodrome_id}")

    msg = await callback.message.edit_text(
        "📋 Выберите категорию:",
        reply_markup=await kb.get_categories_keyboard()
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(AddInstructorLessonStates.waiting_for_category)


@instructor_router.callback_query(
    AddInstructorLessonStates.waiting_for_category,
    F.data.startswith("category_")
)
async def process_lesson_category(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[1]
    await state.update_data(category=f"api/categories/{category_id}")

    msg = await callback.message.edit_text(
        "👤 Выберите студента:",
        reply_markup=await kb.get_students_keyboard()
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(AddInstructorLessonStates.waiting_for_student)


@instructor_router.callback_query(
    AddInstructorLessonStates.waiting_for_student,
    F.data.startswith("student_")
)
async def process_lesson_student(callback: CallbackQuery, state: FSMContext):
    student_id = callback.data.split("_")[1]
    await state.update_data(student=f"api/users/{student_id}")

    data = await state.get_data()

    autodrome = get_autodrome_by_id(data['autodrome'].split('/')[-1])
    category = get_category_by_id(data['category'].split('/')[-1])
    student = get_user_by_id(int(student_id))

    lesson_datetime = datetime.fromisoformat(data['date'].replace('Z', ''))

    confirm_text = (
        "Проверьте данные урока:\n\n"
        f"📅 Дата: {lesson_datetime.strftime('%d.%m.%Y')}\n"
        f"🕒 Время: {lesson_datetime.strftime('%H:%M')}\n"
        f"🏁 Автодром: {autodrome.title}\n"
        f"📋 Категория: {category.title}\n"
        f"👤 Студент: {student.surname} {student.name}\n\n"
        "Создать урок?"
    )

    msg = await callback.message.edit_text(
        confirm_text,
        reply_markup=await kb.get_confirm_lesson_creation_keyboard()
    )
    await state.update_data(last_message_id=msg.message_id)
    await state.set_state(AddInstructorLessonStates.confirmation)


@instructor_router.callback_query(
    AddInstructorLessonStates.confirmation,
    F.data == "confirm_lesson_creation"
)
async def finalize_lesson_creation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    lesson_data = {
        "instructor": data['instructor'],
        "student": data['student'],
        "date": data['date'],
        "autodrome": data['autodrome'],
        "category": data['category']
    }

    credentials = storage.get_user_credentials(callback.from_user.id)
    result = create_instructor_lesson(lesson_data, credentials.email, credentials.password)

    if result == 201:
        await callback.message.edit_text("✅ Урок успешно создан!")
    else:
        await callback.message.edit_text("❌ Ошибка при создании урока")

    await asyncio.sleep(2)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "cancel_lesson_creation")
async def cancel_lesson_creation(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    msg = await callback.message.answer("Создание урока отменено")
    await asyncio.sleep(2)
    try:
        await msg.delete()
    except TelegramBadRequest:
        pass

    await state.clear()
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data.startswith('update_instructor_lesson_'))
async def start_instructor_lesson_editing(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split('_')[3])
    credentials = storage.get_user_credentials(callback.from_user.id)
    lesson = get_instructor_lesson_by_id(lesson_id, credentials.email, credentials.password)

    lesson_dict = {
        'id': lesson.id,
        'date': lesson.date,
        'autodrome': lesson.autodrome['id'],
        'category': lesson.category['id'],
        'student': lesson.student['id'],
        'instructor': lesson.instructor['id']
    }

    await state.update_data(
        original_lesson=deepcopy(lesson_dict),
        current_lesson=deepcopy(lesson_dict)
    )
    await show_instructor_lesson_edit_options(callback, state)
    await state.set_state(EditInstructorLessonStates.waiting_for_choose)


async def show_instructor_lesson_edit_options(
        update: Message | CallbackQuery,
        state: FSMContext,
        force_new_message: bool = False
):
    data = await state.get_data()
    lesson = data['current_lesson']

    lesson_date = datetime.fromisoformat(lesson['date'].replace('Z', ''))
    formatted_date = lesson_date.strftime('%d.%m.%Y %H:%M')

    if type(lesson['autodrome']) is int:
        autodrome = get_autodrome_by_id(lesson['autodrome'])
    else:
        autodrome_id = lesson['autodrome'].split('/')[-1]
        autodrome = get_autodrome_by_id(autodrome_id)
    if type(lesson['category']) is int:
        category = get_category_by_id(lesson['category'])
    else:
        category_id = lesson['category'].split('/')[-1]
        category = get_category_by_id(category_id)
    if type(lesson['student']) is int:
        student = get_user_by_id(int(lesson['student']))
    else:
        student_id = lesson['student'].split('/')[-1]
        student = get_user_by_id(int(student_id))

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"Дата и время: {formatted_date}", callback_data="edit_instructor_lesson_date")
    keyboard.button(text=f"Автодром: {autodrome.title}", callback_data="edit_instructor_lesson_autodrome")
    keyboard.button(text=f"Категория: {category.title}", callback_data="edit_instructor_lesson_category")
    keyboard.button(text=f"Студент: {student.get('surname')} {student.get('name')}",
                    callback_data="edit_instructor_lesson_student")
    keyboard.button(text="✅ Завершить редактирование", callback_data="finish_instructor_lesson_editing")
    keyboard.button(text="❌ Отменить", callback_data="cancel_instructor_lesson_editing")
    keyboard.adjust(1)

    message_text = "Что вы хотите изменить? (нажмите на пункт для редактирования)"

    if isinstance(update, CallbackQuery) and not force_new_message:
        try:
            await update.message.edit_text(
                message_text,
                reply_markup=keyboard.as_markup()
            )
        except TelegramBadRequest:
            await update.message.answer(
                message_text,
                reply_markup=keyboard.as_markup()
            )
    else:
        await update.message.answer(
            message_text,
            reply_markup=keyboard.as_markup()
        ) if isinstance(update, CallbackQuery) else await update.answer(
            message_text,
            reply_markup=keyboard.as_markup()
        )


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_choose,
    F.data.startswith("edit_instructor_lesson_")
)
async def process_instructor_lesson_edit_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split('_')[3]

    await MessageManager.safe_delete(callback.message)

    if choice == "date":
        msg = await callback.message.answer(
            "📅 Выберите новую дату:",
            reply_markup=await RussianSimpleCalendar().start_calendar()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorLessonStates.waiting_for_date)

    elif choice == "autodrome":
        msg = await callback.message.answer(
            "🏁 Выберите автодром:",
            reply_markup=await kb.get_autodromes_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorLessonStates.waiting_for_autodrome)

    elif choice == "category":
        msg = await callback.message.answer(
            "📋 Выберите категорию:",
            reply_markup=await kb.get_categories_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorLessonStates.waiting_for_category)

    elif choice == "student":
        msg = await callback.message.answer(
            "👤 Выберите студента:",
            reply_markup=await kb.get_students_keyboard()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorLessonStates.waiting_for_student)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_date,
    SimpleCalendarCallback.filter()
)
async def process_edit_lesson_date(
        callback: CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
):
    if callback_data.act == "DAY":
        selected_date = date(
            year=callback_data.year,
            month=callback_data.month,
            day=callback_data.day
        )

        if selected_date < datetime.now().date():
            await callback.answer("❌ Нельзя выбрать прошедшую дату!", show_alert=True)
            return

        await state.update_data(selected_date=selected_date.strftime('%Y-%m-%d'))

        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        msg = await callback.message.answer(
            f"📅 Выбрана дата: {selected_date.strftime('%d.%m.%Y')}\n"
            "🕒 Выберите время:",
            reply_markup=kb.get_time_selection_keyboard_instructor_lesson()
        )
        await state.update_data(last_message_id=msg.message_id)
        await state.set_state(EditInstructorLessonStates.waiting_for_time)

    elif callback_data.act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
        pass

    elif callback_data.act == "CANCEL":
        await callback.message.delete()
        await show_instructor_lesson_edit_options(callback, state)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_time,
    F.data.startswith("instructor_lesson_time_")
)
async def process_edit_lesson_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.replace("instructor_lesson_time_", "")
    data = await state.get_data()

    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        selected_date = datetime.strptime(data['selected_date'], '%Y-%m-%d').date()
        full_datetime = datetime.combine(selected_date, time_obj)

        if full_datetime < datetime.now():
            await callback.answer("❌ Нельзя выбрать прошедшее время!", show_alert=True)
            return

        iso_datetime = full_datetime.isoformat() + 'Z'

        current_lesson = data['current_lesson'].copy()
        current_lesson['date'] = iso_datetime
        await state.update_data(current_lesson=current_lesson)

        await MessageManager.safe_delete(callback.message)
        await show_instructor_lesson_edit_options(callback, state, force_new_message=True)
        await state.set_state(EditInstructorLessonStates.waiting_for_choose)

    except Exception as e:
        print(f"Error processing time: {e}")
        await callback.answer("❌ Ошибка при обработке времени", show_alert=True)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_time,
    F.data.startswith("instructor_lesson_time_")
)
async def process_edit_lesson_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.replace("instructor_lesson_time_", "")
    data = await state.get_data()

    full_datetime = f"{data['selected_date']}T{time_str}:00.000Z"

    current_lesson = data['current_lesson'].copy()
    current_lesson['date'] = full_datetime
    await state.update_data(current_lesson=current_lesson)

    await MessageManager.safe_delete(callback.message)
    await show_instructor_lesson_edit_options(callback, state, force_new_message=True)
    await state.set_state(EditInstructorLessonStates.waiting_for_choose)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_autodrome,
    F.data.startswith("autodrome_")
)
async def process_edit_lesson_autodrome(callback: CallbackQuery, state: FSMContext):
    autodrome_id = callback.data.split("_")[1]
    data = await state.get_data()

    current_lesson = data['current_lesson'].copy()
    current_lesson['autodrome'] = f"api/autodromes/{autodrome_id}"
    await state.update_data(current_lesson=current_lesson)

    await MessageManager.safe_delete(callback.message)
    await show_instructor_lesson_edit_options(callback, state, force_new_message=True)
    await state.set_state(EditInstructorLessonStates.waiting_for_choose)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_category,
    F.data.startswith("category_")
)
async def process_edit_lesson_category(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.split("_")[1]
    data = await state.get_data()

    current_lesson = data['current_lesson'].copy()
    current_lesson['category'] = f"api/categories/{category_id}"
    await state.update_data(current_lesson=current_lesson)

    await MessageManager.safe_delete(callback.message)
    await show_instructor_lesson_edit_options(callback, state, force_new_message=True)
    await state.set_state(EditInstructorLessonStates.waiting_for_choose)


@instructor_router.callback_query(
    EditInstructorLessonStates.waiting_for_student,
    F.data.startswith("student_")
)
async def process_edit_lesson_student(callback: CallbackQuery, state: FSMContext):
    student_id = callback.data.split("_")[1]
    data = await state.get_data()

    current_lesson = data['current_lesson'].copy()
    current_lesson['student'] = f"api/users/{student_id}"
    await state.update_data(current_lesson=current_lesson)

    await MessageManager.safe_delete(callback.message)
    await show_instructor_lesson_edit_options(callback, state, force_new_message=True)
    await state.set_state(EditInstructorLessonStates.waiting_for_choose)


@instructor_router.callback_query(F.data == "finish_instructor_lesson_editing")
async def finish_instructor_lesson_editing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['original_lesson']
    updated = data['current_lesson']

    changes = {}
    for key in ['date', 'autodrome', 'category', 'student']:
        if original[key] != updated[key]:
            changes[key] = updated[key]

    if changes:
        changes['id'] = original['id']
        credentials = storage.get_user_credentials(callback.from_user.id)

        result = update_instructor_lesson(
            lesson_data=changes,
            email=credentials.email,
            password=credentials.password
        )

        if result == 200:
            msg = await callback.message.answer("✅ Изменения сохранены!")
            await asyncio.sleep(2)
            await MessageManager.safe_delete(msg)
        else:
            msg = await callback.message.answer("❌ Ошибка при сохранении изменений")
            await asyncio.sleep(2)
            await MessageManager.safe_delete(msg)
    else:
        msg = await callback.message.answer("ℹ️ Нет изменений для сохранения")
        await asyncio.sleep(2)
        await MessageManager.safe_delete(msg)

    await state.clear()
    await back_to_instructor_menu(callback, state)


@instructor_router.callback_query(F.data == "cancel_instructor_lesson_editing")
async def cancel_instructor_lesson_editing(callback: CallbackQuery, state: FSMContext):
    await MessageManager.safe_delete(callback.message)
    await state.clear()
    await back_to_instructor_menu(callback, state)
