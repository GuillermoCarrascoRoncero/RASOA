<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Data Statistics</title>
</head>
<body>
    <h1>Sensor Data Statistics</h1>
    <form id="soapForm" action="http://localhost:5000/webservice" method="POST">
        <label for="startDate">Start Date:</label>
        <input type="date" id="startDate" name="startDate" required><br><br>
        <label for="endDate">End Date:</label>
        <input type="date" id="endDate" name="endDate" required><br><br>
        <button type="submit">Submit</button>
    </form>
    
    <!-- Aquí se mostrará la respuesta SOAP -->
    <div id="soapResponse">
        <h2>Respuesta SOAP</h2>
        <p id="temperature">Temperatura: </p>
        <p id="humidity">Humedad: </p>
        <p id="co2">CO2: </p>
        <p id="volatiles">Volátiles: </p>
        <p id="numSamples">Número de Muestras: </p>
        <p id="dateRange">Rango de Fechas: </p>
    </div>
    
    <script>
        document.getElementById("soapForm").addEventListener("submit", function(event) {
            event.preventDefault();
            
            var formData = new FormData(this);
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "http://localhost:5000/webservice", true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var response = xhr.responseXML;
                    document.getElementById("temperature").innerText += response.querySelector("Temperature").textContent;
                    document.getElementById("humidity").innerText += response.querySelector("Humidity").textContent;
                    document.getElementById("co2").innerText += response.querySelector("CO2").textContent;
                    document.getElementById("volatiles").innerText += response.querySelector("Volatiles").textContent;
                    document.getElementById("numSamples").innerText += response.querySelector("NumSamples").textContent;
                    document.getElementById("dateRange").innerText += response.querySelector("DateRange").textContent;
                }
            };
            xhr.send(formData);
        });
    </script>
</body>
</html>
