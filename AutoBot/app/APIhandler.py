import requests


class Instructor:
    def __init__(self, id, username, name, surname, patronymic, phone, email, dateOfBirth, license, hireDate, roles):
        self.id = id
        self.username = username
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.phone = phone
        self.email = email
        self.dateOfBirth = dateOfBirth
        self.license = license
        self.hireDate = hireDate
        self.roles = roles


class Car:
    def __init__(self, id, carMark, carModel, stateNumber, productionYear, vinNumber):
        self.id = id
        self.carMark = carMark
        self.carModel = carModel
        self.stateNumber = stateNumber
        self.productionYear = productionYear
        self.vinNumber = vinNumber


class Teacher:
    def __init__(self, id, username, name, surname, patronymic, phone, email, dateOfBirth, hireDate, roles, image):
        self.id = id
        self.username = username
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
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


teachers_list = []
instructors_list = []
cars_list = []
courses_list = []


def instructors():
    response = requests.get("http://195.133.38.45/api/instructors")
    instructors_json = response.json()

    for i in range(len(instructors_json)):
        instructors_list.append(Instructor(instructors_json[i]['id'],
                                           instructors_json[i]['username'],
                                           instructors_json[i]['name'],
                                           instructors_json[i]['surname'],
                                           instructors_json[i]['patronym'],
                                           instructors_json[i]['phone'],
                                           instructors_json[i]['email'],
                                           instructors_json[i]['dateOfBirth'],
                                           instructors_json[i]['license'],
                                           instructors_json[i]['hireDate'],
                                           instructors_json[i]['roles']))

    return instructors_list


def teachers():
    response = requests.get("http://195.133.38.45/api/teachers")
    teachers_json = response.json()

    for i in range(len(teachers_json)):
        teachers_list.append(Teacher(teachers_json[i]['id'],
                                     teachers_json[i]['username'],
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
    response = requests.get("http://195.133.38.45/api/cars")
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
    response = requests.get("http://195.133.38.45/api/courses")
    courses_json = response.json()

    for i in range(len(courses_json)):
        courses_list.append(Course(courses_json[i]['id'],
                                   courses_json[i]['title'],
                                   courses_json[i]['description']))

    return courses_list


def get_instructor_by_id(id):
    response = requests.get("http://195.133.38.45/api/instructors")
    instructors_json = response.json()

    for i in range(len(instructors_json)):
        if instructors_json[i]['id'] == id:
            return Instructor(instructors_json[i]['id'],
                              instructors_json[i]['username'],
                              instructors_json[i]['name'],
                              instructors_json[i]['surname'],
                              instructors_json[i]['patronym'],
                              instructors_json[i]['phone'],
                              instructors_json[i]['email'],
                              instructors_json[i]['dateOfBirth'],
                              instructors_json[i]['license'],
                              instructors_json[i]['hireDate'],
                              instructors_json[i]['roles'])


def get_teacher_by_id(id):
    response = requests.get("http://195.133.38.45/api/teachers")
    teachers_json = response.json()

    for i in range(len(teachers_json)):
        if teachers_json[i]['id'] == id:
            return Teacher(teachers_json[i]['id'],
                           teachers_json[i]['username'],
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
    response = requests.get("http://195.133.38.45/api/cars")
    cars_json = response.json()

    for i in range(len(cars_json)):
        if cars_json[i]['id'] == id:
            return Car(cars_json[i]['id'],
                       cars_json[i]['carMark']['title'],
                       cars_json[i]['carModel'],
                       cars_json[i]['stateNumber'],
                       cars_json[i]['productionYear'],
                       cars_json[i]['vinNumber'])
