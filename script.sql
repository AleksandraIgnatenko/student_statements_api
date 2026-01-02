CREATE TABLE statement.groups (
    group_id SERIAL PRIMARY KEY,
    group_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE statement.students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    second_name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    group_id INTEGER REFERENCES groups(group_id) ON DELETE SET NULL
);

CREATE TABLE statement.subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE statement.grades (
    grade_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    grade_numeric smallint NOT NULL,
    grade_ects CHAR(1) NOT NULL,
    date_recorded DATE NOT NULL DEFAULT CURRENT_DATE
);
