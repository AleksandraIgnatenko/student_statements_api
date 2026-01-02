import csv
import random

TARGET_RECORDS = 100

groups = [
    "Б22-524", "Б22-504", "Б22-514", "Б22-534",
    "Б22-544", "Б22-554", "Б22-564", "Б22-511"
]

subjects = [
    "Организация обработки баз данных",
    "Экономика программной инженерии",
    "Проектирование и архитектура программных систем",
    "Предиктивный анализ данных",
    "Моделирование систем",
    "Биологически мотивированные когнитивные архитектуры",
    "Динамические интеллектуальные системы"
]

first_names = ["Иван", "Сергей", "Алексей", "Дмитрий", "Евгений", "Максим", "Андрей", "Роман", "Павел", "Никита"]
surnames = ["Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров", "Соколов", "Михайлов", "Новиков", "Фёдоров"]
patronymics = ["Иванович", "Сергеевич", "Алексеевич", "Дмитриевич", "Евгеньевич", "Максимович", "Андреевич", "Романович", "Павлович", "Никитич"]

def numeric_to_ects(grade):
    if 90 <= grade <= 100:
        return "A"
    elif 85 <= grade <= 89:
        return "B"
    elif 75 <= grade <= 84:
        return "C"
    elif 70 <= grade <= 74:
        return "D"
    elif 60 <= grade <= 69:
        return "E"
    else:
        return "F"


students = []
student_id = 1
records = []

while len(records) < TARGET_RECORDS:
    first_name = random.choice(first_names)
    second_name = random.choice(patronymics)
    surname = random.choice(surnames)
    group_name = random.choice(groups)
    
    num_grades = min(random.randint(1, 5), TARGET_RECORDS - len(records))
    
    for _ in range(num_grades):
        subject_name = random.choice(subjects)
        grade_numeric = random.randint(60, 100)
        grade_ects = numeric_to_ects(grade_numeric)
        
        records.append({
            "student_id": student_id,
            "first_name": first_name,
            "second_name": second_name,
            "surname": surname,
            "group_name": group_name,
            "subject_name": subject_name,
            "grade_numeric": grade_numeric,
            "grade_ects": grade_ects
        })
    
    student_id += 1

records = records[:TARGET_RECORDS]

with open("data.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
