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
        let selectedDateInput = document.getElementById('date-input'); // Новое скрытое поле
        let calendar = document.querySelector('.calendar'); // Родительский контейнер

        calendar.addEventListener('click', (event) => {
            // Проверяем, на каком элементе был клик
            let target = event.target;

            if (target.tagName === 'DIV') {
                // Клик на div элементе календаря
                let selectedDate = new Date(currYear.value, currMonth.value, parseInt(target.textContent));
                let currentDatePlus3Days = new Date();
                currentDatePlus3Days.setDate(currentDatePlus3Days.getDate() + 3); // Текущая дата +3 дня

                let currentDatePlus30Days = new Date();
                currentDatePlus30Days.setDate(currentDatePlus30Days.getDate() + 30); // Текущая дата +30

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

                // Устанавливаем значение скрытого поля
                selectedDateInput.value = selectedDate.toISOString().split('T')[0];
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
});
