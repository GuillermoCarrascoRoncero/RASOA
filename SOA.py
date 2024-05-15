from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import csv
import os
import json
import paho.mqtt.client as mqtt
import threading
from datetime import datetime
from statistics import mean

app = Flask(__name__)
CORS(app, resources={r"/webservice": {"origins": "http://localhost:8080"}})

CSV_FILE = 'sensor_data.csv'

def save_sensor_data(data):
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([data['temperature'], data['humidity'], data['co2'], data['volatiles'], data['date']])

def on_connect(client, userdata, flags, rc, properties):
    print("Conectado con mqtt " + str(rc))
    client.subscribe("sensor-topic")

def on_message(client, userdata, msg):
    print("Recibido: " + msg.topic + " " + str(msg.payload))
    try:
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        m_in = json.loads(m_decode)  

        save_sensor_data({
            'temperature': m_in['temperatura'],
            'humidity': m_in['humedad'],
            'co2': m_in['co2' ],
            'volatiles': m_in['volatiles'],
            'date': datetime.utcnow()
        })
        
    except KeyError as e:
        print("Error con el JSON: {e}")

@app.route('/wsdl', methods=['GET'])
def wsdl():
    with open('docs/api-description.xml', 'r') as f:
        wsdl_content = f.read()
    return Response(wsdl_content, content_type='application/xml')

@app.route('/webservice', methods=['POST'])
@cross_origin()
def webservice():

    fecha_inicio = datetime.strptime(request.form['startDate'], '%Y-%m-%d')
    fecha_final = datetime.strptime(request.form['endDate'], '%Y-%m-%d')

    muestras = []
    with open(CSV_FILE, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S.%f')
            if fecha_inicio <= date <= fecha_final:
                muestras.append({
                    'temperature': float(row['Temperature']),
                    'humidity': float(row['Humidity']),
                    'co2': float(row['CO2']),
                    'volatiles': float(row['Volatiles'])
                })

    if not muestras:
        return Response(response="No hay datos dentro del rango de fechas especificado", status=404)

    temperatura_media = round(mean([data['temperature'] for data in muestras]), 2)
    humedad_media = round(mean([data['humidity'] for data in muestras]), 2)
    co2_media = round(mean([data['co2'] for data in muestras]), 2)
    volatiles_media = round(mean([data['volatiles'] for data in muestras]), 2)
    num_muestras = len(muestras)
    fecha = f"{fecha_inicio.strftime('%Y-%m-%d')} to {fecha_final.strftime('%Y-%m-%d')}"
    
    soap_response = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <SensorDataStatistics>
                <Temperature>{temperatura_media}</Temperature>
                <Humidity>{humedad_media}</Humidity>
                <CO2>{co2_media}</CO2>
                <Volatiles>{volatiles_media}</Volatiles>
                <NumSamples>{num_muestras}</NumSamples>
                <DateRange>{fecha}</DateRange>
            </SensorDataStatistics>
        </soap:Body>
    </soap:Envelope>"""

    return Response(response=soap_response, content_type='text/xml; charset=utf-8')


if __name__ == '__main__':

    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Temperature', 'Humidity', 'CO2', 'Volatiles', 'Date'])
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)

    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.start()

    app.run(debug=True)
