document.addEventListener('click', function (e) {
    try {
        // allows for elements inside TH
        function findElementRecursive(element, tag) {
            return element.nodeName === tag ? element : findElementRecursive(element.parentNode, tag);
        }
        var descending_th_class_1 = 'dir-d';
        var ascending_th_class_1 = 'dir-u';
        var ascending_table_sort_class = 'asc';
        var no_sort_class = 'no-sort';
        var null_last_class = 'n-last';
        var table_class_name = 'sortable';
        var alt_sort_1 = e.shiftKey || e.altKey;
        var element = findElementRecursive(e.target, 'TH');
        var tr = element.parentNode;
        var thead = tr.parentNode;
        var table = thead.parentNode;
        function reClassify(element, dir) {
            element.classList.remove(descending_th_class_1);
            element.classList.remove(ascending_th_class_1);
            if (dir)
                element.classList.add(dir);
        }
        function getValue(element) {
            var _a;
            var value = alt_sort_1 ? element.dataset.sortAlt : (_a = element.dataset.sort) !== null && _a !== void 0 ? _a : element.textContent;
            return value;
        }
        if (thead.nodeName === 'THEAD' && // sortable only triggered in `thead`
            table.classList.contains(table_class_name) &&
            !element.classList.contains(no_sort_class) // .no-sort is now core functionality, no longer handled in CSS
        ) {
            var column_index_1;
            var nodes = tr.cells;
            var tiebreaker_1 = parseInt(element.dataset.sortTbr);
            // Reset thead cells and get column index
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i] === element) {
                    column_index_1 = parseInt(element.dataset.sortCol) || i;
                }
                else {
                    reClassify(nodes[i], '');
                }
            }
            var dir = descending_th_class_1;
            // Check if we're sorting ascending or descending
            if (element.classList.contains(descending_th_class_1) ||
                (table.classList.contains(ascending_table_sort_class) && !element.classList.contains(ascending_th_class_1))) {
                dir = ascending_th_class_1;
            }
            // Update the `th` class accordingly
            reClassify(element, dir);
            var reverse_1 = dir === ascending_th_class_1;
            var sort_null_last_1 = table.classList.contains(null_last_class);
            var compare_1 = function (a, b, index) {
    var x = getValue(b.cells[index]);
    var y = getValue(a.cells[index]);

    if (sort_null_last_1) {
        if (x === '' && y !== '') {
            return -1;
        }
        if (y === '' && x !== '') {
            return 1;
        }
    }

    // Parse the values as floats for proper decimal sorting
    var floatX = parseFloat(x);
    var floatY = parseFloat(y);

    // Check for NaN (non-numeric values) and use localeCompare for strings
    if (isNaN(floatX) || isNaN(floatY)) {
        return reverse_1 ? y.localeCompare(x) : x.localeCompare(y);
    }

    // Compare as floats
    var temp = floatX - floatY;
    return reverse_1 ? -temp : temp;
};
            // loop through all tbodies and sort them
            for (var i = 0; i < table.tBodies.length; i++) {
                var org_tbody = table.tBodies[i];
                // Put the array rows in an array, so we can sort them...
                var rows = [].slice.call(org_tbody.rows, 0);
                // Sort them using Array.prototype.sort()
                rows.sort(function (a, b) {
                    var bool = compare_1(a, b, column_index_1);
                    return bool === 0 && !isNaN(tiebreaker_1) ? compare_1(a, b, tiebreaker_1) : bool;
                });
                // Make an empty clone
                var clone_tbody = org_tbody.cloneNode();
                // Put the sorted rows inside the clone
                clone_tbody.append.apply(clone_tbody, rows);
                // And finally replace the unsorted tbody with the sorted one
                table.replaceChild(clone_tbody, org_tbody);
            }
        }
    }
    catch (error) {
        // console.log(error)
    }
});

function myFunction() {
  // Объявить переменные
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  // Перебирайте все строки таблицы и скрывайте тех, кто не соответствует поисковому запросу
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}
