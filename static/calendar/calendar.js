document.addEventListener('DOMContentLoaded', function() {
    // Функция для проверки високосного года
function isLeapYear(year) {
        return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    }

    // Функция для получения числа дней в феврале
function getFebDays(year) {
        return isLeapYear(year) ? 29 : 28;
    }

    // Функция для генерации календаря
function generateCalendar(month, year) {
        let calendarDay = document.querySelector('.calendar-day');
        calendarDay.innerHTML = '';

        let calendarHeaderYear = document.querySelector('#year');
        let daysOfMonth = [31, getFebDays(year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        let currDate = new Date();

        let monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
        let monthPicker = document.querySelector('#month-picker');
        monthPicker.innerHTML = monthNames[month];
        calendarHeaderYear.innerHTML = year;

        let firstDay = new Date(year, month, 1);
        let startDay = 1; // Понедельник

        for (let i = 0; i <= daysOfMonth[month] + (firstDay.getDay() - startDay) - 1; i++) {
            let day = document.createElement('div');
            if (i >= (firstDay.getDay() - startDay)) {
                day.classList.add('calendarDayHover');
                day.innerHTML = i - (firstDay.getDay() - startDay) + 1;
                day.innerHTML += `<span></span><span></span><span></span><span></span>`;
                if (
                    i - (firstDay.getDay() - startDay) + 1 === currDate.getDate() &&
                    year === currDate.getFullYear() &&
                    month === currDate.getMonth()
                ) {
                    day.classList.add('currDate');
                }
            }
            calendarDay.appendChild(day);
        }

        // Добавляем обработчики событий для каждой даты, ссылок и кнопок
        addEventListeners();
    }

    // Обработчик события для отображения списка месяцев
    document.querySelector('.month-picker').onclick = () => {
        document.querySelector('.month-list').classList.toggle('show');
    };

    // Получаем элемент с месяцами
    let monthList = document.querySelector('.month-list');

    // Добавляем обработчики событий для выбора месяца
    monthList.querySelectorAll('div').forEach((monthDiv, index) => {
        monthDiv.addEventListener('click', () => {
            monthList.classList.remove('show');
            currMonth.value = index;
            generateCalendar(currMonth.value, currYear.value);
        });
    });

    // Обработчики событий для смены года
    document.querySelector('#prev-year').onclick = () => {
        --currYear.value;
        generateCalendar(currMonth.value, currYear.value);
    };

    document.querySelector('#next-year').onclick = () => {
        ++currYear.value;
        generateCalendar(currMonth.value, currYear.value);
    };

    // Добавляем обработчики событий для каждой даты, ссылок и кнопок
function addEventListeners() {
        let selectedDateText = document.getElementById('selected-date-text');
        let selectedDateInput = document.getElementById('selected-date-input'); // Новое скрытое поле
        let calendar = document.querySelector('.calendar'); // Родительский контейнер

        const userId = localStorage.getItem('user.id');
        console.log(userId);

        calendar.addEventListener('click', (event) => {
            // Проверяем, на каком элементе был клик
            let target = event.target;

            if (target.tagName === 'DIV') {
                // Клик на div элементе календаря
                let selectedDate = new Date(currYear.value, currMonth.value, parseInt(target.textContent));
                let currentDatePlus3Days = new Date();
                currentDatePlus3Days.setDate(currentDatePlus3Days.getDate() + 3); // Текущая дата +3 дня

                let currentDatePlus30Days = new Date();
                currentDatePlus30Days.setDate(currentDatePlus30Days.getDate() + 14); // Текущая дата +30

                let formattedDate = selectedDate.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });

                if (selectedDate <= currentDatePlus3Days) {
                    selectedDateText.style.color = 'red';
                } else {
                    selectedDateText.style.color = 'green';
                }

                if (selectedDate > currentDatePlus30Days) {
                    selectedDateText.style.color = 'red';
                }

                selectedDateText.textContent = formattedDate;
                // Функция для отправки AJAX-запроса
                console.log(selectedDate);

                sendAjaxRequest(formatDateToYYYYMMDD(selectedDate));

                // Устанавливаем значение скрытого поля
                selectedDateInput.value = formatDateToYYYYMMDD(selectedDate);
            } else if (target.tagName === 'A') {
                // Клик на ссылке
                // Добавьте здесь логику для обработки кликов на ссылках
                window.location.href = target.href; // Пример: перенаправление на ссылку
            } else if (target.tagName === 'BUTTON') {
                // Клик на кнопке
                // Добавьте здесь логику для обработки кликов на кнопках
                console.log('Клик на кнопке: ' + target.textContent);
            }
        });
    }

    let currDate = new Date();
    let currMonth = { value: currDate.getMonth() };
    let currYear = { value: currDate.getFullYear() };

    // Генерируем календарь при загрузке страницы
    generateCalendar(currMonth.value, currYear.value);

    // Функция для отправки AJAX-запроса
function sendAjaxRequest(selectedDate) {
    // Создать объект для AJAX-запроса
    var xhr = new XMLHttpRequest();
    // Создать объект с данными для отправки на сервер
    var data = 'date=' + selectedDate;
    // Получение CSRF-токена из cookies
    var csrftoken = getCookie('csrftoken');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/work/ajax/', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', csrftoken); // Добавление CSRF-токена
    // Отправить данные
    xhr.send(data);
    // Определить обработчик события при завершении запроса
    xhr.onreadystatechange = function () {
        console.log(xhr.status);

        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                // Обработать успешный ответ от сервера
                var responseData = JSON.parse(xhr.responseText);
                // Добавьте здесь логику для обновления данных на вашей странице
                console.log(responseData);
                updateAppointmentsTable(responseData.appointments, responseData.user);
            } else {
                // Обработать ошибку при запросе
                console.error('Произошла ошибка при запросе.');
            }
        }
    };
}

function formatDateToYYYYMMDD(date) {
    var year = date.getFullYear();
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var day = date.getDate().toString().padStart(2, '0');
    return year + '-' + month + '-' + day;
}

// Функция для обновления таблицы с записями
function updateAppointmentsTable(appointments, currentUser) {
    var tableBody = document.querySelector('.table-responsive-sm tbody');
    tableBody.innerHTML = '';

    for (var i = 0; i < appointments.length; i++) {
        var appointment = appointments[i];
        var canDelete = appointment.user === currentUser && !appointment.verified;
        console.log(appointment.id);
        var row = '<tr id="row-' + appointment.id + '">' +
            '<th scope="row">' + (i + 1) + '</th>' +
            '<td>' + appointment.user + '</td>' +
            '<td>' + appointment.date + '</td>' +
            '<td>' + appointment.start_time + '</td>' +
            '<td>' + appointment.end_time + '</td>' +
            '<td>' + appointment.duration + '</td>' +
            '<td>' + (appointment.verified ? 'Да' : 'Нет') + '</td>' +
            '<td>';

        if (canDelete) {
            row += '<button class="btn btn-danger" onclick="deleteAppointment(' + appointment.id + ')">Удалить</button>';
        } else {
            row += '<button class="btn btn-secondary" disabled>Удалить</button>';
        }

        row += '</td></tr>';

        tableBody.innerHTML += row;
    }
}

function deleteAppointment(appointmentId) {
    if (confirm("Вы уверены, что хотите удалить запись?")) {
        var xhr = new XMLHttpRequest();
        var csrftoken = getCookie('csrftoken');

        xhr.open('POST', '/work/delete_row/', true); // Replace '/work/delete/' with your actual delete endpoint
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-CSRFToken', csrftoken);

        var data = 'id=' + appointmentId;
        xhr.send(data);

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    // Handle success
                    var responseData = JSON.parse(xhr.responseText);
                    // You can update the table or perform any other action as needed
                    console.log(responseData);
                    var tableRow = document.getElementById('row-' + appointmentId);
                    if (tableRow) {
                        tableRow.parentNode.removeChild(tableRow);
                    }
                } else {
                    // Handle error
                    console.error('Произошла ошибка при удалении записи.');
                }
            }
        };
    }
}
});
