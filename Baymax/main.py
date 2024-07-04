import requests
from flask import Flask, request, jsonify, send_file
from camera import CameraModule
from proximity_sensors import ProximitySensors
import io

app = Flask(__name__)

# URL base para OpenStreetMap
OSM_BASE_URL = "https://nominatim.openstreetmap.org"

class MapsAPI:
    def get_directions(self, start_lat, start_lon, end_lat, end_lon):
        # Obter direções entre dois pontos usando o Nominatim
        # Nominatim não fornece direções diretamente, mas podemos obter a rota usando outras fontes
        return {'error': 'Direções não suportadas por Nominatim'}

    def get_map_image(self, center_lat, center_lon):
        # Obter imagem do mapa usando o OpenStreetMap
        static_map_url = f"https://staticmap.openstreetmap.de/staticmap.php?center={center_lat},{center_lon}&zoom=13&size=600x300"
        return static_map_url

camera = CameraModule()
proximity_sensor = ProximitySensors(pin=17)  # Defina o pino GPIO apropriado

@app.route('/directions', methods=['GET'])
def directions():
    start_lat = request.args.get('start_lat')
    start_lon = request.args.get('start_lon')
    end_lat = request.args.get('end_lat')
    end_lon = request.args.get('end_lon')

    if not all([start_lat, start_lon, end_lat, end_lon]):
        return jsonify({'error': 'Parâmetros insuficientes'}), 400

    maps = MapsAPI()
    directions_data = maps.get_directions(start_lat, start_lon, end_lat, end_lon)
    return jsonify(directions_data)

@app.route('/map_image', methods=['GET'])
def map_image():
    center_lat = request.args.get('center_lat')
    center_lon = request.args.get('center_lon')
    if not all([center_lat, center_lon]):
        return jsonify({'error': 'Parâmetros insuficientes'}), 400

    maps = MapsAPI()
    image_url = maps.get_map_image(center_lat, center_lon)
    return jsonify({'map_image_url': image_url})

@app.route('/capture_image', methods=['GET'])
def capture_image():
    image_data = camera.capture_image()
    return send_file(io.BytesIO(image_data), mimetype='image/jpeg')

@app.route('/sensor_status', methods=['GET'])
def sensor_status():
    if proximity_sensor.is_visitor_near():
        return jsonify({'status': 'Visitante detectado'})
    else:
        return jsonify({'status': 'Nenhum visitante detectado'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
