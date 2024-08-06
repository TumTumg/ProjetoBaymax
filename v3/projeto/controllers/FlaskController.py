from flask import Flask, request, jsonify
from ..services.BaymaxService import BaymaxService
from ..services.MapsService import MapsService
from ..dao.HardwareDAO import HardwareDAO

def createApp():
    app = Flask(__name__)

    baymaxService = BaymaxService()
    mapsService = MapsService()
    hardwareDAO = HardwareDAO("/dev/ttyUSB0")

    @app.route('/directions', methods=['GET'])
    def directions():
        startLat = request.args.get('startLat')
        startLon = request.args.get('startLon')
        endLat = request.args.get('endLat')
        endLon = request.args.get('endLon')

        if not all([startLat, startLon, endLat, endLon]):
            return jsonify({'error': 'Parâmetros insuficientes para obter direções'}), 400

        directions = mapsService.getDirections(startLat, startLon, endLat, endLon)
        return jsonify(directions)

    @app.route('/map', methods=['GET'])
    def map():
        centerLat = request.args.get('centerLat')
        centerLon = request.args.get('centerLon')

        if not all([centerLat, centerLon]):
            return jsonify({'error': 'Parâmetros insuficientes para obter mapa'}), 400

        mapImageUrl = mapsService.getMapImage(centerLat, centerLon)
        return jsonify({'mapImageUrl': mapImageUrl})

    @app.route('/hardware/blink', methods=['POST'])
    def blinkHardware():
        data = request.get_json()
        pin = data.get('pin')
        times = data.get('times')

        if pin is None or times is None:
            return jsonify({'error': 'Parâmetros insuficientes para acionar o hardware'}), 400

        try:
            hardwareDAO.blinkLED(pin, times)
            return jsonify({'status': 'LED blinked'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
