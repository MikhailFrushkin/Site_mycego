$(document).ready(function() {
        // Найдем все элементы, которые имеют класс "btn-center" и содержат атрибут data-bs-toggle
        $(".depth[data-bs-toggle]").click(function() {
            var target = $(this).attr("data-bs-target"); // Получим цель сворачиваемого блока
            $(".collapse").not(target).collapse("hide"); // Закроем все сворачиваемые блоки, кроме цели
        });
    });