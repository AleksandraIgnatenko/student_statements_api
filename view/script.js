const API_BASE = 'http://127.0.0.1:8004';

async function loadGroups() {
    try {
        const response = await fetch(`${API_BASE}/groups`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const groups = await response.json();
        const select = document.getElementById('group_name');
        select.innerHTML = '<option value="">Выберите группу</option>';
        groups.forEach(group => {
            const option = document.createElement('option');
            option.value = group.group_name;
            option.textContent = group.group_name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки групп:', error);
        alert('Не удалось загрузить список групп: ' + (error.message || 'Неизвестная ошибка'));
    }
}

document.getElementById('student-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        surname: document.getElementById('surname').value.trim(),
        first_name: document.getElementById('first_name').value.trim(),
        second_name: document.getElementById('second_name').value.trim(),
        group_name: document.getElementById('group_name').value
    };

    if (!data.surname || !data.first_name || !data.second_name || !data.group_name) {
        alert('Пожалуйста, заполните все поля.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/students`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Студент успешно добавлен!');
            document.getElementById('student-form').reset();
            loadStudents(); // обновить список студентов
        } else {
            const err = await response.json().catch(() => ({}));
            alert('Ошибка при добавлении студента: ' + (err.detail || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        alert('Не удалось добавить студента: ' + (error.message || 'Проверьте подключение к серверу'));
    }
});

async function loadStudents() {
    const list = document.getElementById('students-list');
    list.innerHTML = '<li>Загрузка...</li>';

    try {
        const response = await fetch(`${API_BASE}/students`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const students = await response.json();
        if (students.length === 0) {
            list.innerHTML = '<li>Нет студентов</li>';
        } else {
            list.innerHTML = students.map(s => 
                `<li>${s.surname} ${s.first_name} ${s.second_name} (${s.group_name}) — ID: ${s.student_id}</li>`
            ).join('');
        }
    } catch (error) {
        console.error('Ошибка загрузки студентов:', error);
        list.innerHTML = '<li style="color:red;">Ошибка загрузки студентов</li>';
        alert('Не удалось загрузить студентов: ' + (error.message || 'Проверьте подключение'));
    }
}

document.getElementById('load-students').addEventListener('click', loadStudents);

document.getElementById('load-report').addEventListener('click', async () => {
    const studentIdInput = document.getElementById('report-student-id');
    const studentId = studentIdInput.value.trim();

    if (!studentId || isNaN(studentId) || parseInt(studentId) <= 0) {
        alert('Пожалуйста, введите корректный ID студента (целое положительное число).');
        return;
    }

    const output = document.getElementById('report-output');
    output.innerHTML = '<p>Загрузка отчёта...</p>';

    try {
        const response = await fetch(`${API_BASE}/report/student/${studentId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const report = await response.json();

        if (report.student && report.student.error) {
            output.innerHTML = `<p style="color:red;">${report.student.error}</p>`;
            return;
        }

        const avg = report.average_grade || 0;
        output.innerHTML = `
            <h3>Студент: ${report.student.surname} ${report.student.first_name} ${report.student.second_name}</h3>
            <p><strong>Средний балл:</strong> ${avg} (предметов: ${report.total_subjects})</p>
            <h4>Оценки:</h4>
            ${
                report.grades && report.grades.length > 0
                    ? `<ul>
                        ${report.grades.map(g => 
                            `<li><strong>${g.subject_name}:</strong> ${g.grade_numeric} (${g.grade_ects})</li>`
                        ).join('')}
                      </ul>`
                    : '<p>Нет оценок</p>'
            }
        `;
    } catch (error) {
        console.error('Ошибка загрузки отчёта:', error);
        output.innerHTML = `<p style="color:red;">Ошибка: ${error.message || 'Не удалось загрузить отчёт'}</p>`;
        alert('Не удалось загрузить отчёт: ' + (error.message || 'Проверьте ID и подключение'));
    }
});

// Загрузка списка предметов
async function loadSubjects() {
    const select = document.getElementById('grade-subject');
    if (!select) return; // если формы ещё нет
    
    select.innerHTML = '<option value="">Загрузка...</option>';
    
    try {
        const response = await fetch(`${API_BASE}/grades/subjects`);
        if (!response.ok) throw new Error(`Ошибка ${response.status}`);
        const subjects = await response.json();
        select.innerHTML = '<option value="">Выберите предмет</option>';
        subjects.forEach(subject => {
            const opt = document.createElement('option');
            opt.value = subject;
            opt.textContent = subject;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value="">Ошибка загрузки</option>';
        console.error('Не удалось загрузить предметы:', err);
    }
}


document.getElementById('grade-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        student_id: parseInt(document.getElementById('grade-student-id').value.trim()),
        subject_name: document.getElementById('grade-subject').value,
        grade_numeric: parseInt(document.getElementById('grade-numeric').value.trim()),
        grade_ects: document.getElementById('grade-ects').value.trim().toUpperCase()
    };

    if (!data.student_id || !data.subject_name || !data.grade_numeric || !data.grade_ects) {
        alert('Заполните все поля');
        return;
    }
    if (data.grade_numeric < 60 || data.grade_numeric > 100) {
        alert('Оценка должна быть от 60 до 100');
        return;
    }
    if (!['A', 'B', 'C', 'D', 'E'].includes(data.grade_ects)) {
        alert('ECTS должен быть A, B, C, D или E');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/grades`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Оценка успешно сохранена!');
            document.getElementById('grade-form').reset();
        } else {
            const err = await response.json().catch(() => ({}));
            alert('Ошибка: ' + (err.detail || 'Неизвестная ошибка'));
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    loadGroups();
    //loadStudents(); 
    loadSubjects();
});