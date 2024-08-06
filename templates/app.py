from flask import Flask, request, jsonify, send_file
import io
from config import Config
from data_analysis import DataAnalysis
from hardware import Hardware
from guiarVisitantes import GuiarVisitantes
from proximity_sensors import ProximitySensors
from baymax import Baymax
import serial

app = Flask(__name__)

# Inicializando os componentes
data_analysis = DataAnalysis()
hardware = Hardware(Config.GPS_PORT, Config.BAUD_RATE)
hardware.initialize_gps()
guiar_visitantes = GuiarVisitantes()
proximity_sensor = ProximitySensors(pin=17)
baymax = Baymax()

@app.route('/directions', methods=['GET'])
def directions():
    start_lat = request.args.get('start_lat')
    start_lon = request.args.get('start_lon')
    end_lat = request.args.get('end_lat')
    end_lon = request.args.get('end_lon')

    if not all([start_lat, start_lon, end_lat, end_lon]):
        return jsonify({'error': 'Parâmetros insuficientes'}), 400

    directions_data = data_analysis.get_directions(
        (float(start_lat), float(start_lon)),
        (float(end_lat), float(end_lon))
    )
    return jsonify(directions_data)

@app.route('/map_image', methods=['GET'])
def map_image():
    center_lat = request.args.get('center_lat')
    center_lon = request.args.get('center_lon')
    if not all([center_lat, center_lon]):
        return jsonify({'error': 'Parâmetros insuficientes'}), 400

    image_url = f"https://staticmap.openstreetmap.de/staticmap.php?center={center_lat},{center_lon}&zoom=13&size=600x300"
    return jsonify({'map_image_url': image_url})

@app.route('/capture_image', methods=['GET'])
def capture_image():
    # Substitua pelo código para capturar a imagem da câmera
    return send_file(io.BytesIO(b"imagem"), mimetype='image/jpeg')

@app.route('/sensor_status', methods=['GET'])
def sensor_status():
    if proximity_sensor.is_visitor_near():
        return jsonify({'status': 'Visitante detectado'})
    else:
        return jsonify({'status': 'Nenhum visitante detectado'})

@app.route('/gps_data', methods=['GET'])
def gps_data():
    gps_data = hardware.read_gps_data()
    return jsonify({'gps_data': gps_data})

@app.route('/guide', methods=['GET'])
def guide():
    voice_data = request.args.get('voice_data')
    if not voice_data:
        return jsonify({'error': 'Dados de voz não fornecidos'}), 400

    try:
        guiar_visitantes.guiar(voice_data)
        return jsonify({'status': 'Instruções fornecidas com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['GET'])
def speak():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'Texto não fornecido'}), 400

    baymax.speak(text)
    return jsonify({'status': 'Texto falado com sucesso'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
