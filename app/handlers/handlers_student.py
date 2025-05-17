import asyncio
import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile, URLInputFile
from aiogram_calendar import SimpleCalendarCallback

import app.keyboards.static_keyboard as static_kb
import app.keyboards.keyboard as kb
from app.APIhandlers.APIhandlersAutodrome import get_autodrome_by_id
from app.APIhandlers.APIhandlersCategory import get_category_by_id
from app.APIhandlers.APIhandlersCourse import get_course_by_id, get_courses_progress_by_id, get_test_by_course_id, \
    StudentAnswer, save_test_results
from app.APIhandlers.APIhandlersDriveLesson import post_instructor_lesson
from app.APIhandlers.APIhandlersInstructor import get_instructor_by_id
from app.APIhandlers.APIhandlersLesson import get_lesson_by_id, lesson_marked
from app.APIhandlers.APIhandlersSchedule import get_drive_schedule_by_id
from app.APIhandlers.APIhandlersStudent import get_my_schedule_by_id, cancel_lesson_by_id
from app.APIhandlers.APIhandlersUser import UserStorage, update_user_data
from app.calendar import RussianSimpleCalendar
from app.handlers.handlers import StudentCourseStates, EditStudentStates, ScheduleStates, MyScheduleStates, TestStates
from config_local import profile_photos, lessons_videos

student_router = Router()

storage = UserStorage()

JSON_DATA_DIR = "data/json/"


@student_router.callback_query(F.data == "student_info")
async def student_info(callback: CallbackQuery):
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
                    reply_markup=static_kb.student_info
                )
                return
            except Exception as url_error:
                print(f"URL send failed, trying FSInputFile: {url_error}")
                await callback.message.answer_photo(
                    photo=FSInputFile(user.image),
                    caption=info_text,
                    parse_mode='HTML',
                    reply_markup=static_kb.student_info
                )
                return
        except Exception as e:
            print(f"Both photo sending methods failed: {e}")

    await callback.message.answer(
        info_text,
        parse_mode='HTML',
        reply_markup=static_kb.student_info
    )


async def handle_back_to_student_menu(message: Message, user_id):
    user = storage.get_user(user_id)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    if not user:
        await message.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await message.answer(
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=static_kb.student_main
    )


@student_router.callback_query(F.data == "back_to_student_menu")
async def back_to_student_menu(callback: CallbackQuery, state: FSMContext):
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
        f'Привет, {user.surname} {user.name}, Ваша роль Студент',
        reply_markup=static_kb.student_main
    )


@student_router.callback_query(F.data == 'student_courses')
async def show_student_courses(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали просмотр ваших курсов')

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user = storage.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Данные пользователя не найдены")
        return

    markup = await kb.inline_student_courses(id=user.id)
    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=markup
    )

    await state.set_state(StudentCourseStates.waiting_for_id)


@student_router.callback_query(StudentCourseStates.waiting_for_id)
async def handle_student_course_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        course_id = int(callback.data)
        course = get_course_by_id(course_id)
        email = storage.get_user(callback.from_user.id).email
        password = storage.get_credentials(callback.from_user.id).password
        progress = get_courses_progress_by_id(course_id, email, password)

        if not course:
            await callback.message.answer("Курс не найден",
                                          reply_markup=static_kb.student_course_back_button)
            await state.clear()
            return

        message_text = (
            f"🧑‍🏫 Информация о курсе:\n\n"
            f"▫️ <b>Название:</b> {course.title}\n"
            f"▫️ <b>Описание:</b> {course.description}\n"
            f"▫️ <b>Прогресс курса:</b> {progress}%\n\n"
            f"▫️ <b>Занятия и тест на курсе:</b>\n"
        )

        await callback.message.answer(message_text, parse_mode='HTML',
                                      reply_markup=await kb.inline_lessons_by_course(course_id))

        await state.clear()
        await state.set_state(StudentCourseStates.waiting_for_lesson_id)
    except Exception as e:
        print(f"Error: {e}")
        await callback.answer("❌ Произошла ошибка")
        await state.clear()


@student_router.callback_query(StudentCourseStates.waiting_for_lesson_id)
async def handle_student_course_id(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("test_"):
        await start_test(callback, state)
    else:

        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        lesson_id = int(callback.data)
        lesson = get_lesson_by_id(lesson_id)

        if not lesson:
            await callback.message.answer(
                "Занятие не найдено",
                reply_markup=static_kb.student_course_back_button
            )
            return

        video_urls = []
        for video in lesson.videos:
            video_urls.append(video['video'])

        message_text = (
            f"🧑‍🏫 Информация о занятии:\n\n"
            f"▫️ <b>Название:</b> {lesson.title}\n"
            f"▫️ <b>Тип:</b> {lesson.lesson_type}\n"
            f"▫️ <b>Описание:</b> {lesson.description}\n"
            f"▫️ <b>Дата:</b> {datetime.fromisoformat(lesson.date).strftime('%d.%m.%Y')}\n"
        )

        await callback.message.answer(
            message_text,
            parse_mode='HTML',
            reply_markup=await kb.get_videos_keyboard(video_urls=video_urls, lesson_id=lesson_id)
        )

        await state.set_state(StudentCourseStates.waiting_for_video_by_url)


@student_router.callback_query(StudentCourseStates.waiting_for_video_by_url)
async def get_video_by_url(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back_to_student_courses_list":
        await back_to_student_courses_list(callback, state)
        return

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    video_url = str(callback.data.split('_')[0])
    lesson_id = int(callback.data.split('_')[1])
    full_url = f"{lessons_videos}{video_url}"

    loading_msg = await callback.message.answer("⏳ Видео загружается, пожалуйста, подождите...")

    try:
        await callback.message.answer_video(
            video=URLInputFile(full_url),
            reply_markup=await kb.get_video_keyboard(lesson_id),
            read_timeout=30,
            write_timeout=30,
            connect_timeout=15
        )
    except TelegramEntityTooLarge:
        await callback.message.answer(
            f"⚠️ Видео слишком большое: [Смотреть по ссылке]({full_url})",
            parse_mode='HTML',
            reply_markup=static_kb.student_course_back_button
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при загрузке видео: {str(e)}",
            reply_markup=static_kb.student_course_back_button
        )
    finally:
        try:
            await loading_msg.delete()
        except TelegramBadRequest:
            pass
        await state.set_state(StudentCourseStates.waiting_for_mark)


@student_router.callback_query(StudentCourseStates.waiting_for_mark)
async def mark_video_lesson(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back_to_student_courses_list":
        await back_to_student_courses_list(callback, state)
        return

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    lesson_id = int(callback.data.split('_')[1])
    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    result = lesson_marked(lesson_id=lesson_id, email=email,
                           password=password)

    if result == 200:
        await callback.message.answer(text="Успешно отмечно",
                                      reply_markup=static_kb.student_course_back_button)
    else:
        await callback.message.answer(text="Не удалось отметить",
                                      reply_markup=static_kb.student_course_back_button)

    await state.clear()


@student_router.callback_query(F.data.startswith("test_"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    course_id = callback.data.split('_')[1]
    tests = get_test_by_course_id(course_id)

    if not tests:
        await callback.message.answer("Тесты для этого курса не найдены")
        return

    await state.update_data(
        tests=tests,
        current_question=0,
        correct_answers=0,
        student_answers=[],
        question_ids=[test.id for test in tests]
    )

    await show_next_question(callback, state)


async def show_next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tests = data['tests']
    current = data['current_question']

    if current >= len(tests):
        await finish_test(callback, state)
        return

    test = tests[current]

    await callback.message.answer(
        f"Вопрос {current + 1}/{len(tests)}:\n{test.question}",
        reply_markup=await kb.build_test_keyboard(test)
    )

    await state.set_state(TestStates.waiting_for_answer)


@student_router.callback_query(F.data.startswith("answer_"), StateFilter(TestStates.waiting_for_answer))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    _, answer_id = callback.data.split('_')
    answer_id = int(answer_id)

    data = await state.get_data()
    tests = data['tests']
    current = data['current_question']
    correct_answers = data['correct_answers']
    student_answers = data['student_answers']

    test = tests[current]
    selected_answer = next((a for a in test.answers if a['id'] == answer_id), None)

    await callback.message.delete()

    if selected_answer:
        is_correct = selected_answer['status']

        student_answers.append(StudentAnswer(
            question_id=test.id,
            question_text=test.question,
            answer_id=answer_id,
            answer_text=selected_answer['answerText'],
            is_correct=is_correct
        ))

        if is_correct:
            correct_answers += 1
            feedback_msg = await callback.message.answer("✅ Верно!")
        else:
            correct = next((a for a in test.answers if a['status']), None)
            feedback_msg = await callback.message.answer(
                f"❌ Неверно! Правильный ответ: {correct['answerText'] if correct else 'Не определен'}")

        await asyncio.sleep(2)
        await feedback_msg.delete()

    await state.update_data(
        current_question=current + 1,
        correct_answers=correct_answers,
        student_answers=student_answers
    )

    await show_next_question(callback, state)


async def finish_test(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = len(data['tests'])
    correct = data['correct_answers']
    percentage = (correct / total) * 100 if total > 0 else 0
    student_answers = data['student_answers']
    question_ids = data['question_ids']

    # Сначала отправляем отчет
    report_msg = await callback.message.answer(
        f"📝 Отчет по тесту:\n"
        f"Правильных ответов: {correct}\n"
        f"Успешность: {percentage:.1f}%"
    )

    email = storage.get_user(callback.from_user.id).email
    password = storage.get_credentials(callback.from_user.id).password

    await save_test_results(
        email=email,
        password=password,
        question_ids=question_ids,
        answers=student_answers
    )

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await asyncio.sleep(2)
    try:
        await report_msg.delete()
    except TelegramBadRequest:
        pass

    await back_to_student_courses_list(callback, state)
    await state.clear()




@student_router.callback_query(F.data == "back_to_student_courses_list")
async def back_to_student_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = storage.get_user(callback.from_user.id)

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(user_data.id))

    await state.set_state(StudentCourseStates.waiting_for_id)


@student_router.callback_query(F.data == "back_to_student_courses_list")
async def back_to_student_courses_list(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = storage.get_user(callback.from_user.id)

    await callback.message.answer(
        'Вот ваши курсы:',
        reply_markup=await kb.inline_student_courses(id=user_data.id))

    await state.clear()
    await state.set_state(StudentCourseStates.waiting_for_id)


@student_router.callback_query(F.data == "update_info")
async def start_editing(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    new_msg = await callback.message.answer(
        "Введите новую фамилию:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_surname)


@student_router.message(EditStudentStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
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
        "Теперь введите новое имя:",
        reply_markup=await kb.get_cancel_keyboard()
    )

    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_name)


@student_router.message(EditStudentStates.waiting_for_name)
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
        "Теперь введите новое отчество:",
        reply_markup=await kb.get_cancel_keyboard()
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
    await state.set_state(EditStudentStates.waiting_for_patronymic)


@student_router.message(EditStudentStates.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
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
        await handle_back_to_student_menu(message, telegram_user_id)
        return

    user_id = user.id
    user_pass = storage.get_credentials(telegram_user_id).password
    user_email = storage.get_user(telegram_user_id).email
    user_data = await state.get_data()

    update = update_user_data(
        user_id=user_id,
        surname=user_data.get('surname'),
        name=user_data.get('name'),
        patronymic=user_data.get('patronymic'),
        email=user_email,
        password=user_pass
    )
    print(update)
    if update == 200:
        if storage.update_user_from_api(telegram_user_id):
            result_msg = await message.answer("Данные успешно обновлены!")
        else:
            result_msg = await message.answer("Данные обновлены в системе, но возникла проблема с локальным хранилищем")

        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await state.clear()
        await handle_back_to_student_menu(message, telegram_user_id)
    else:
        result_msg = await message.answer("Ошибка обновления! Проверьте данные и попробуйте снова")
        await asyncio.sleep(1)
        try:
            await result_msg.delete()
        except TelegramBadRequest:
            pass
        await handle_back_to_student_menu(message, user_id)


@student_router.callback_query(F.data == "cancel_edit")
async def cancel_editing(callback: CallbackQuery, state: FSMContext):
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
    await back_to_student_menu(callback, state)


@student_router.callback_query(F.data == "drive_schedules")
async def show_drive_schedules(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        'Выберите инструктора у которого хотите посмотреть расписание:',
        reply_markup=await kb.inline_schedules()
    )
    await state.set_state(ScheduleStates.waiting_for_id)


@student_router.callback_query(ScheduleStates.waiting_for_id)
async def handle_schedule_id(callback: CallbackQuery, state: FSMContext):
    if callback.data == "cancel_schedule":
        await cancel_schedule_selection(callback, state)
        return

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        schedule_id = int(callback.data)
        schedule = get_drive_schedule_by_id(schedule_id)

        if not schedule:
            await callback.message.answer("🕒 Расписание не найдено")
            await state.clear()
            return

        autodrome = get_autodrome_by_id(schedule.autodrome_id)
        category = get_category_by_id(schedule.category_id)
        instructor = get_instructor_by_id(schedule.instructor_id)

        days = ', '.join(schedule.days_of_week) if isinstance(schedule.days_of_week, list) else schedule.days_of_week

        response = (
            "📅 Информация о расписании:\n\n"
            f"⏱ Время: {datetime.fromisoformat(schedule.time_from).strftime('%H:%M')} - "
            f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}\n\n"
            f"📆 Дни: {days}\n\n"
            f"🏁 Автодром: {autodrome.title}\n\n"
            f"📋 Категория: {category.title}\n\n"
            f"👤 Инструктор: {instructor.surname} {instructor.name} {instructor.patronymic}\n\n"
        )

        if schedule.notice:
            response += f"📝 Примечание: {schedule.notice}\n"

        await callback.message.answer(
            response,
            parse_mode="HTML",
            reply_markup=await kb.instructor_schedule(
                instructor_id=schedule.instructor_id,
                autodrome_id=schedule.autodrome_id,
                category_id=schedule.category_id,
                time_from=f"{datetime.fromisoformat(schedule.time_from).strftime('%H:%M')}",
                time_to=f"{datetime.fromisoformat(schedule.time_to).strftime('%H:%M')}",
                days=f"{days}"
            )
        )

    except (ValueError, AttributeError) as e:
        print(f"Error processing schedule: {e}")
        await callback.message.answer("❌ Ошибка обработки запроса")
    finally:
        await state.clear()


@student_router.callback_query(F.data == "cancel_schedule")
async def cancel_schedule_selection(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    user_data = storage.get_user(callback.from_user.id)
    if not user_data:
        await callback.answer("Данные пользователя не найдены. Пожалуйста, выполните /start")
        return

    await state.clear()
    await callback.message.answer(
        f'Привет, {user_data.surname} {user_data.name}, Ваша роль Студент',
        reply_markup=static_kb.student_main)


@student_router.callback_query(F.data.startswith("sign_up_"))
async def handle_sign_up(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        parts = callback.data[7:].split('_')
        if len(parts) != 7:
            raise ValueError("Неверный формат callback_data")

        await state.update_data(
            sign_up_instructor_id=int(parts[1]),
            sign_up_autodrome_id=int(parts[2]),
            sign_up_category_id=int(parts[3]),
            sign_up_time_from=parts[4],
            sign_up_time_to=parts[5],
            sign_up_days=parts[6]
        )

        await callback.message.answer(
            "Выберите дату для записи:",
            reply_markup=await RussianSimpleCalendar().start_calendar(allowed_days=parts[6])
        )
    except Exception as e:
        print(f"Error processing sign up: {e}")
        await callback.answer("❌ Ошибка при обработке записи", show_alert=True)


@student_router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    try:
        act = callback_data.act
        year = callback_data.year
        month = callback_data.month

        new_year = year
        new_month = month

        state_data = await state.get_data()
        allowed_days = state_data.get('sign_up_days')

        if act in ["PREV-YEAR", "NEXT-YEAR", "PREV-MONTH", "NEXT-MONTH"]:
            if act == "PREV-YEAR":
                new_year = year - 1
                new_month = month
            elif act == "NEXT-YEAR":
                new_year = year + 1
                new_month = month
            elif act == "PREV-MONTH":
                new_year = year
                new_month = month - 1
                if month == 1:
                    new_month = 12
                    new_year = year - 1
            elif act == "NEXT-MONTH":
                new_year = year
                new_month = month + 1
                if month == 12:
                    new_month = 1
                    new_year = year + 1

            await callback.message.edit_reply_markup(
                reply_markup=await RussianSimpleCalendar().start_calendar(
                    year=new_year,
                    month=new_month,
                    allowed_days=allowed_days
                )
            )
            return

        if act == "CANCEL":
            await cancel_schedule_selection(callback, state)
            return

        if act == "DAY":
            selected_date = datetime(
                year=callback_data.year,
                month=callback_data.month,
                day=callback_data.day
            )

            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            await state.update_data(selected_date=selected_date.strftime('%Y-%m-%d'))
            data = await state.get_data()

            email = storage.get_user(callback.from_user.id).email
            password = storage.get_credentials(callback.from_user.id).password

            await callback.message.answer(
                f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}",
                reply_markup=kb.generate_time_keyboard(
                    instructor_id=data.get('sign_up_instructor_id'),
                    selected_date=selected_date.strftime('%Y-%m-%d'),
                    email=email,
                    user_password=password,
                    time_from=data.get('sign_up_time_from'),
                    time_to=data.get('sign_up_time_to')
                )
            )
            return

        await callback.answer("Неизвестное действие с календарем", show_alert=True)

    except Exception as e:
        print(f"Error in calendar processing: {e}")
        await callback.answer("❌ Произошла ошибка при обработке календаря", show_alert=True)


@student_router.callback_query(F.data == "back_to_calendar")
async def back_to_calendar(callback: CallbackQuery, state: FSMContext):
    await back_to_student_menu(callback, state)


@student_router.callback_query(F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    time_str = callback.data.split('_')[1]
    data = await state.get_data()
    date_str = data.get('selected_date')
    full_datetime = f"{date_str} {time_str}"
    user_id = callback.from_user.id

    user_pass = storage.get_credentials(callback.from_user.id)
    if not user_pass:
        await callback.message.answer("❌ Данные пользователя не найдены")
        await state.clear()
        return

    await state.update_data(
        booking_datetime=full_datetime,
        booking_time_str=time_str,
        user_password=user_pass.password
    )

    try:
        result = post_instructor_lesson(
            user_id=callback.from_user.id,
            instructor_id=data.get('sign_up_instructor_id'),
            autodrome_id=data.get('sign_up_autodrome_id'),
            category_id=data.get('sign_up_category_id'),
            date_time=full_datetime,
            password=user_pass.password
        )

        if result == 201:
            instructor = get_instructor_by_id(data['sign_up_instructor_id'])
            autodrome = get_autodrome_by_id(data['sign_up_autodrome_id'])
            category = get_category_by_id(data['sign_up_category_id'])

            msg = await callback.message.answer(
                f"✅ Вы записаны на:\n"
                f"Дата и время: {full_datetime}\n"
                f"Инструктор: {instructor.surname} {instructor.name}\n"
                f"Автодром: {autodrome.title}\n"
                f"Категория: {category.title}"
            )
        else:
            msg = await callback.message.answer("❌ Ошибка при записи")

        await asyncio.sleep(2)
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass

    except Exception as e:
        print(f"Error processing booking: {e}")
        await callback.message.answer("❌ Произошла ошибка при обработке записи")
    finally:
        await state.clear()
        await handle_back_to_student_menu(callback.message, user_id)


@student_router.callback_query(F.data == "my_schedules")
async def check_my_schedules(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    credentials = storage.get_credentials(callback.from_user.id)
    if not credentials or not credentials.user:
        await callback.answer("Данные пользователя не найдены")
        return

    user = credentials.user
    await callback.message.answer(
        "Вот ваши ближайшие занятия:",
        reply_markup=await kb.inline_my_schedule(
            student_id=user.id,
            email=user.email,
            user_password=credentials.password
        )
    )
    await state.set_state(MyScheduleStates.waiting_for_id)


@student_router.callback_query(MyScheduleStates.waiting_for_id)
async def handle_my_schedule_id(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    try:
        schedule_id = int(callback.data)
        user = storage.get_user(callback.from_user.id)
        credentials = storage.get_credentials(callback.from_user.id)

        schedule_by_id = get_my_schedule_by_id(schedule_id, user.email, credentials.password)

        await callback.message.answer(
            text=f"✅ Вы записаны на:\n"
                 f"Дата и время: {schedule_by_id.date}\n"
                 f"Инструктор: {schedule_by_id.instructor['surname']} {schedule_by_id.instructor['name']}\n"
                 f"Автодром: {schedule_by_id.autodrome['title']}\n"
                 f"Категория: {schedule_by_id.category['title']}",
            reply_markup=await kb.get_cancel_my_lesson_keyboard(schedule_id)
        )
        await state.clear()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")


@student_router.callback_query(F.data.startswith("cancel_lesson_"))
async def cancel_lesson_handler(callback: CallbackQuery):
    try:
        schedule_id = int(callback.data.split("_")[-1])
        user = storage.get_user(callback.from_user.id)
        credentials = storage.get_credentials(callback.from_user.id)
        result = cancel_lesson_by_id(
            lesson_id=schedule_id,
            email=user.email,
            password=credentials.password
        )

        if result == 204:
            await callback.message.edit_text(
                text="❌ Запись успешно отменена",
                reply_markup=static_kb.back_to_my_schedules_menu
                )
            await callback.answer()
        else:
            await callback.answer("Не удалось отменить запись", show_alert=True)

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
