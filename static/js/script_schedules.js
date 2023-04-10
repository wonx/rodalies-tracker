
var dfSelect = document.getElementById("df-select");
var dfTable = document.getElementById("df-table");

dfSelect.addEventListener("change", function() {
    var selectedValue = dfSelect.options[dfSelect.selectedIndex].value;
    var selectedData = dfs.find(df => df.name === selectedValue);
    var keys = selectedData.columns;
    var tableHtml = "<table><thead><tr>";
    keys.forEach(function(key) {
        tableHtml += "<th>" + key + "</th>";
    });
    tableHtml += "</tr></thead><tbody>";
    selectedData.data.forEach(function(row) {
        tableHtml += "<tr>";
        keys.forEach(function(key) {
            tableHtml += "<td>" + row[key] + "</td>";
        });
        tableHtml += "</tr>";
    });
    tableHtml += "</tbody></table>";
    dfTable.innerHTML = tableHtml;
});