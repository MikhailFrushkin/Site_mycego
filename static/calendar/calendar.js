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

    // Определение первого дня месяца
    let firstDay = new Date(year, month, 1);
    let startDay = 1; // Понедельник
    let dayOfWeek = firstDay.getDay();

    // Вычисляем сдвиг для начала месяца
    let shift = dayOfWeek - startDay;
    if (shift < 0) {
        shift = 7 + shift; // Чтобы сдвиг был положительным
    }

    // Сдвиг начальной даты на дни недели
    firstDay.setDate(1 - shift);

    // Переменные для отслеживания количества дней
    let dayCount = 0;
    let totalDaysToShow = 6 * 7; // 6 недель

    while (dayCount < totalDaysToShow) {
        let day = document.createElement('div');

        if (dayCount >= shift && dayCount < (daysOfMonth[month] + shift)) {
            // Выводим дату текущего месяца
            day.classList.add('calendarDayHover');
            day.innerHTML = firstDay.getDate();
            day.innerHTML += `<span></span><span></span><span></span><span></span>`;

            if (
                firstDay.getDate() === currDate.getDate() &&
                year === currDate.getFullYear() &&
                month === currDate.getMonth()
            ) {
                day.classList.add('currDate');
            }
        } else {
            // Пропускаем дни других месяцев
            day.classList.add('emptyDay');
            day.setAttribute('disabled', 'true');
        }

        calendarDay.appendChild(day);
        firstDay.setDate(firstDay.getDate() + 1);
        dayCount++;
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

function addEventListeners() {
    let selectedDateText = document.getElementById('selected-date-text');
    let selectedDateInput = document.getElementById('selected-date-input');
    let calendar = document.querySelector('.calendar');

    const userId = localStorage.getItem('user.id');
    console.log(userId);

    calendar.addEventListener('click', (event) => {
        let target = event.target;

        if (target.tagName === 'DIV') {
            let selectedDate = new Date(currYear.value, currMonth.value, parseInt(target.textContent));
            let currentDate = new Date();
            let currentWeek = getISOWeek(currentDate); // Получаем текущую неделю
            let targetWeek;

            if (currentDate.getDay() === 0) {
                targetWeek = currentWeek + 2; // Добавляем 2 недели для воскресенья
            } else {
                targetWeek = currentWeek + 1; // Добавляем 1 неделю для других дней
            }


            let startOfWeek = getStartOfWeek(currentDate, targetWeek); // Получаем начало целевой недели
            let endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 14); // Добавляем 13 дней к началу недели

            // Проверяем, входит ли выбранная дата в диапазон целевой недели
            if (selectedDate >= startOfWeek && selectedDate <= endOfWeek) {
                selectedDateText.style.color = 'green';
            } else {
                selectedDateText.style.color = 'red';
            }

            let formattedDate = selectedDate.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });
            selectedDateText.textContent = formattedDate;

            if (isValidDate(formatDateToYYYYMMDD(selectedDate))) {
                console.log(selectedDate);
                sendAjaxRequest(formatDateToYYYYMMDD(selectedDate));
            } else {
                console.log("Дата некорректна:", selectedDate);
            }

            selectedDateInput.value = formatDateToYYYYMMDD(selectedDate);
        } else if (target.tagName === 'A') {
            window.location.href = target.href;
        } else if (target.tagName === 'BUTTON') {
            console.log('Клик на кнопке: ' + target.textContent);
        }
    });

//    calendar.removeEventListener('click', clickHandler);
//    calendar.addEventListener('click', clickHandler);
}

// Функция для получения номера недели
function getISOWeek(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 4 - (d.getDay() || 7));
    const yearStart = new Date(d.getFullYear(), 0, 1);
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Функция для получения начала недели
function getStartOfWeek(date, weekNumber) {
    const d = new Date(date);
    d.setDate(d.getDate() + (weekNumber - getISOWeek(date)) * 7);
    d.setDate(d.getDate() - d.getDay()); // Установка на понедельник
    return d;
}

let currDate = new Date();
let currMonth = { value: currDate.getMonth() };
let currYear = { value: currDate.getFullYear() };

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

function isValidDate(dateString) {
    // Проверяем, является ли строка датой в формате год-месяц-день
    const regexDate = /^\d{4}-\d{2}-\d{2}$/;
    if (!regexDate.test(dateString)) {
        return false;
    }

    // Парсим строку в объект Date
    const dateObj = new Date(dateString);

    // Проверяем, является ли объект Date корректной датой
    if (isNaN(dateObj.getTime())) {
        return false;
    }

    // Проверяем, что год, месяц и день находятся в разумных пределах
    const year = dateObj.getFullYear();
    const month = dateObj.getMonth() + 1; // Месяцы в JavaScript начинаются с 0
    const day = dateObj.getDate();

    if (year < 1000 || year > 9999 || month < 1 || month > 12 || day < 1 || day > 31) {
        return false;
    }

    return true;
}

});
