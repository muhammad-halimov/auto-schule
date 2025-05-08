from aiogram.utils.keyboard import InlineKeyboardBuilder
import calendar
from datetime import datetime
from aiogram.types import InlineKeyboardButton
from aiogram_calendar import SimpleCalendarCallback


class RussianSimpleCalendar:
    @staticmethod
    async def start_calendar(
            year: int = datetime.now().year,
            month: int = datetime.now().month,
            allowed_days: str = None  # Теперь это строка (например, "пн, ср")
    ):
        builder = InlineKeyboardBuilder()

        # Словарь для соответствия русских названий дней и их номеров
        day_mapping = {
            'пн': 0, 'вт': 1, 'ср': 2, 'чт': 3,
            'пт': 4, 'сб': 5, 'вс': 6
        }

        # Конвертируем разрешенные дни в числовые значения
        allowed_day_numbers = []

        if allowed_days and isinstance(allowed_days, str):
            days_list = [day.strip().lower() for day in allowed_days.split(',') if day.strip()]
            allowed_day_numbers = [day_mapping[day] for day in days_list if day in day_mapping]

        month_names = [
            'Январь', 'Февраль', 'Март', 'Апрель',
            'Май', 'Июнь', 'Июль', 'Август',
            'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]

        # Навигационная строка (передаем allowed_days в callback_data)
        builder.row(
            InlineKeyboardButton(text="<<",
                                 callback_data=SimpleCalendarCallback(act="IGNORE").pack()),
            InlineKeyboardButton(text="",
                                 callback_data=SimpleCalendarCallback(act="PREV-YEAR", year=year, month=month,
                                                                      day=0).pack()),
            InlineKeyboardButton(text="<",
                                 callback_data=SimpleCalendarCallback(act="PREV-MONTH", year=year, month=month,
                                                                      day=0).pack()),
            InlineKeyboardButton(text=f"{month_names[month - 1]} {year}",
                                 callback_data=SimpleCalendarCallback(act="IGNORE", year=year, month=month,
                                                                      day=0).pack()),
            InlineKeyboardButton(text=">",
                                 callback_data=SimpleCalendarCallback(act="NEXT-MONTH", year=year, month=month,
                                                                      day=0).pack()),
            InlineKeyboardButton(text=">>",
                                 callback_data=SimpleCalendarCallback(act="NEXT-YEAR", year=year, month=month,
                                                                      day=0).pack()),
            InlineKeyboardButton(text="",
                                 callback_data=SimpleCalendarCallback(act="IGNORE").pack()),
            width=5
        )

        # Дни недели
        week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        builder.row(*[
            InlineKeyboardButton(
                text=day,
                callback_data=SimpleCalendarCallback(act="IGNORE").pack()
            )
            for day in week_days
        ], width=7)

        # Дни месяца (фильтрация по allowed_days)
        month_cal = calendar.monthcalendar(year, month)

        for week in month_cal:
            for day in week:
                if day == 0:
                    builder.add(InlineKeyboardButton(
                        text=" ",
                        callback_data=SimpleCalendarCallback(act="IGNORE").pack()
                    ))
                else:
                    date = datetime(year=year, month=month, day=day)
                    weekday_num = date.weekday()

                    if not allowed_days or weekday_num in allowed_day_numbers:
                        builder.add(InlineKeyboardButton(
                            text=f"{day}",
                            callback_data=SimpleCalendarCallback(
                                act="DAY", year=year, month=month, day=day, allowed_days=allowed_days
                            ).pack()
                        ))
                    else:
                        builder.add(InlineKeyboardButton(
                            text="·",
                            callback_data=SimpleCalendarCallback(act="IGNORE").pack()
                        ))

            builder.adjust(7)

        # Кнопка отмены (также передаем allowed_days, если нужно)
        builder.row(
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=SimpleCalendarCallback(act="CANCEL", allowed_days=allowed_days).pack()
            )
        )

        return builder.as_markup()
