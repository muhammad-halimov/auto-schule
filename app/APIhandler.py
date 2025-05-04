from typing import Optional

import requests
from config_local import api


class Student:
    def __init__(self, id, name, surname, patronymic, phone, email, contract, dateOfBirth, roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.contract = contract
        self.dateOfBirth = dateOfBirth
        self.roles = roles
        self.image = image


class Admin:
    def __init__(self, email, username):
        self.email = email
        self.username = username


class Instructor:
    def __init__(self, id, name, surname, patronymic, phone, email, dateOfBirth, license, hireDate, roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.dateOfBirth = dateOfBirth
        self.license = license
        self.hireDate = hireDate
        self.roles = roles
        self.image = image


class Car:
    def __init__(self, id, carMark, carModel, stateNumber, productionYear, vinNumber):
        self.id = id
        self.carMark = carMark
        self.carModel = carModel
        self.stateNumber = stateNumber
        self.productionYear = productionYear
        self.vinNumber = vinNumber


class Teacher:
    def __init__(self, id, name, surname, patronymic, phone, email, dateOfBirth, hireDate, roles, image):
        self.id = id
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.dateOfBirth = dateOfBirth
        self.hireDate = hireDate
        self.roles = roles
        self.image = image


class Course:
    def __init__(self, id, title, description, lessons):
        self.id = id
        self.title = title
        self.description = description
        self.lessons = lessons


class Lesson:
    def __init__(self, id, title, description, lesson_type, date):
        self.id = id
        self.title = title
        self.description = description
        self.lesson_type = lesson_type
        self.date = date


class Schedule:
    def __init__(self, id, time_from, time_to, days_of_week, notice, autodrome_title, category_title, instructor_name):
        self.id = id
        self.time_from = time_from
        self.time_to = time_to
        self.days_of_week = days_of_week
        self.notice = notice
        self.autodrome_title = autodrome_title
        self.category_title = category_title
        self.instructor_name = instructor_name


teachers_list = []
instructors_list = []
cars_list = []
courses_list = []
schedule_list = []


def instructors():
    response = requests.get(f"{api}instructors")
    instructors_json = response.json()

    for i in range(len(instructors_json)):
        instructors_list.append(Instructor(instructors_json[i]['id'],
                                           instructors_json[i]['name'],
                                           instructors_json[i]['surname'],
                                           instructors_json[i]['patronym'],
                                           instructors_json[i]['phone'],
                                           instructors_json[i]['email'],
                                           instructors_json[i]['dateOfBirth'],
                                           instructors_json[i]['license'],
                                           instructors_json[i]['hireDate'],
                                           instructors_json[i]['roles'],
                                           instructors_json[i]['image']))

    return instructors_list


def teachers():
    response = requests.get(f"{api}teachers")
    teachers_json = response.json()

    for i in range(len(teachers_json)):
        teachers_list.append(Teacher(teachers_json[i]['id'],
                                     teachers_json[i]['name'],
                                     teachers_json[i]['surname'],
                                     teachers_json[i]['patronym'],
                                     teachers_json[i]['phone'],
                                     teachers_json[i]['email'],
                                     teachers_json[i]['dateOfBirth'],
                                     teachers_json[i]['hireDate'],
                                     teachers_json[i]['roles'],
                                     teachers_json[i]['image']))

    return teachers_list


def cars():
    response = requests.get(f"{api}cars")
    cars_json = response.json()

    for i in range(len(cars_json)):
        cars_list.append(Car(cars_json[i]['id'],
                             cars_json[i]['carMark']['title'],
                             cars_json[i]['carModel'],
                             cars_json[i]['stateNumber'],
                             cars_json[i]['productionYear'],
                             cars_json[i]['vinNumber']))

    return cars_list


def courses():
    response = requests.get(f"{api}courses")
    courses_json = response.json()

    for i in range(len(courses_json)):
        courses_list.append(Course(courses_json[i]['id'],
                                   courses_json[i]['title'],
                                   courses_json[i]['description'],
                                   courses_json[i]['lessons']))

    return courses_list


def get_instructor_by_id(id):
    response = requests.get(f"{api}instructors")
    instructors_json = response.json()

    for i in range(len(instructors_json)):
        if instructors_json[i]['id'] == id:
            return Instructor(instructors_json[i]['id'],
                              instructors_json[i]['name'],
                              instructors_json[i]['surname'],
                              instructors_json[i]['patronym'],
                              instructors_json[i]['phone'],
                              instructors_json[i]['email'],
                              instructors_json[i]['dateOfBirth'],
                              instructors_json[i]['license'],
                              instructors_json[i]['hireDate'],
                              instructors_json[i]['roles'],
                              instructors_json[i]['image'])


def get_teacher_by_id(id):
    response = requests.get(f"{api}teachers")
    teachers_json = response.json()

    for i in range(len(teachers_json)):
        if teachers_json[i]['id'] == id:
            return Teacher(teachers_json[i]['id'],
                           teachers_json[i]['name'],
                           teachers_json[i]['surname'],
                           teachers_json[i]['patronym'],
                           teachers_json[i]['phone'],
                           teachers_json[i]['email'],
                           teachers_json[i]['dateOfBirth'],
                           teachers_json[i]['hireDate'],
                           teachers_json[i]['roles'],
                           teachers_json[i]['image'])


def get_car_by_id(id):
    response = requests.get(f"{api}cars")
    cars_json = response.json()

    for i in range(len(cars_json)):
        if cars_json[i]['id'] == id:
            return Car(cars_json[i]['id'],
                       cars_json[i]['carMark']['title'],
                       cars_json[i]['carModel'],
                       cars_json[i]['stateNumber'],
                       cars_json[i]['productionYear'],
                       cars_json[i]['vinNumber'])


def get_course_by_id(id):
    response = requests.get(f"{api}courses")
    courses_json = response.json()

    for i in range(len(courses_json)):
        if courses_json[i]['id'] == id:
            return Course(courses_json[i]['id'],
                          courses_json[i]['title'],
                          courses_json[i].get('description', ''),
                          courses_json[i]['lessons'])


def get_lesson_by_id(id):
    response = requests.get(f"{api}teacher_lessons/{id}")
    teacher_lesson_json = response.json()

    return Lesson(teacher_lesson_json['id'],
                  teacher_lesson_json['title'],
                  teacher_lesson_json['description'],
                  teacher_lesson_json['type'],
                  teacher_lesson_json['date'])


def user_is_authorized(id):
    response = requests.get(f"{api}users")
    users_json = response.json()

    for i in range(len(users_json)):
        if 'telegramId' in users_json[i] and users_json[i]['telegramId'] == str(id):
            if "ROLE_STUDENT" in users_json[i]['roles']:
                return Student(users_json[i]['id'],
                               users_json[i]['name'],
                               users_json[i]['surname'],
                               users_json[i]['patronym'],
                               users_json[i]['phone'],
                               users_json[i]['email'],
                               users_json[i]['contract'],
                               users_json[i]['dateOfBirth'],
                               users_json[i]['roles'],
                               users_json[i]['image'])
            elif "ROLE_ADMIN" in users_json[i]['roles']:
                return Admin(users_json[i]['email'],
                             users_json[i]['username'])
            elif "ROLE_TEACHER" in users_json[i]['roles']:
                return Teacher(users_json[i]['id'],
                               users_json[i]['name'],
                               users_json[i]['surname'],
                               users_json[i]['patronym'],
                               users_json[i]['phone'],
                               users_json[i]['email'],
                               users_json[i]['dateOfBirth'],
                               users_json[i]['hireDate'],
                               users_json[i]['roles'],
                               users_json[i]['image'])
            elif "ROLE_INSTRUCTOR" in users_json[i]['roles']:
                return Instructor(users_json[i]['id'],
                                  users_json[i]['name'],
                                  users_json[i]['surname'],
                                  users_json[i]['patronym'],
                                  users_json[i]['phone'],
                                  users_json[i]['email'],
                                  users_json[i]['dateOfBirth'],
                                  users_json[i]['license'],
                                  users_json[i]['hireDate'],
                                  users_json[i]['roles'],
                                  users_json[i]['image'])

    return 0


def student_courses(telegram_id):
    response = requests.get(f"{api}students")
    students_json = response.json()
    student_courses_list = []

    for student in students_json:
        if 'telegramId' in student and student['telegramId'] == str(telegram_id):
            if 'courses' in student and isinstance(student['courses'], list):
                for course in student['courses']:
                    student_courses_list.append(Course(
                        id=course['id'],
                        title=course['title'],
                        description=course.get('description', ''),
                        lessons=course.get('lessons', [])
                    ))
    return student_courses_list


def update_user_data(user_id, surname, name, patronymic, password):
    response_get = requests.get(f"{api}users")
    users_json = response_get.json()

    email = ""
    id = 0

    for i in range(len(users_json)):
        if 'telegramId' in users_json[i] and users_json[i]['telegramId'] == str(user_id):
            id = users_json[i]['id']
            email = users_json[i]['email']

    auth_json = {"email": email, "password": password}

    response_post = requests.post(f"{api}authentication_token", json=auth_json)

    user_json = {"surname": f"{surname}", "name": f"{name}", "patronym": f"{patronymic}"}

    headers = {
        "Authorization": f"Bearer {response_post.json()['token']}",
        "Content-Type": "application/merge-patch+json"
    }

    response = requests.patch(f"{api}users/{id}", json=user_json, headers=headers)

    return response.status_code


def drive_schedules():
    try:
        response = requests.get(f"{api}drive_schedules")
        response.raise_for_status()
        schedules_json = response.json()
    except Exception as e:
        print(f"Error fetching schedules: {e}")
        return []

    for item in schedules_json:
        try:
            schedule = Schedule(
                id=item.get('id', 'N/A'),
                time_from=item.get('timeFrom', 'Не указано'),
                time_to=item.get('timeTo', 'Не указано'),
                days_of_week=item.get('daysOfWeek', []),
                notice=item.get('notice', ''),
                autodrome_title=item.get('autodrome', {}).get('title', 'Не указан'),
                category_title=item.get('category', {}).get('title', 'Не указана'),
                instructor_name=(
                    f"{item.get('instructor', {}).get('surname', '')} "
                    f"{item.get('instructor', {}).get('name', '')} "
                    f"{item.get('instructor', {}).get('patronym', '')}"
                ).strip()
            )
            schedule_list.append(schedule)
        except KeyError as e:
            print(f"Error parsing schedule item: {e}")

    return schedule_list


def get_drive_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
    try:
        response = requests.get(f"{api}drive_schedules/{schedule_id}")
        response.raise_for_status()

        schedule_data = response.json()

        if not schedule_data:
            print(f"Schedule with ID {schedule_id} not found")
            return None

        return Schedule(
            id=schedule_data.get('id'),
            time_from=schedule_data.get('timeFrom', 'Не указано'),
            time_to=schedule_data.get('timeTo', 'Не указано'),
            days_of_week=schedule_data.get('daysOfWeek', []),
            notice=schedule_data.get('notice', ''),
            autodrome_title=schedule_data.get('autodrome', {}).get('title', 'Не указан'),
            category_title=schedule_data.get('category', {}).get('title', 'Не указана'),
            instructor_name=(
                f"{schedule_data.get('instructor', {}).get('surname', '')} "
                f"{schedule_data.get('instructor', {}).get('name', '')} "
                f"{schedule_data.get('instructor', {}).get('patronym', '')}"
            ).strip()
        )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching schedule {schedule_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing schedule {schedule_id}: {e}")
        return None
