from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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

