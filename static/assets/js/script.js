// Инициализация календаря
$(document).ready(function() {
    $('#datepicker').datepicker({
        format: 'dd/mm/yyyy',
        autoclose: true
    });
});

// Обработчик клика по кнопке выбора времени
$('#datepicker').on('changeDate', function() {
    $('#timeModal').modal('show');
});

// Обработчик клика по кнопке подтверждения времени
$('#confirmTime').on('click', function() {
    var startTime = $('#startTime').val();
    var endTime = $('#endTime').val();

    // Вывести выбранный временной промежуток (можно заменить на вашу логику)
    alert('Выбран временной промежуток: ' + startTime + ' - ' + endTime);

    // Закрыть модальное окно
    $('#timeModal').modal('hide');
});
