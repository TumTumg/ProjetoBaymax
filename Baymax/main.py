from flask import Flask, request, jsonify, send_file
from baymax import Baymax
from JarvisFirmata import JarvisFirmata
import io

app = Flask(__name__)

# Instância dos módulos
baymax = Baymax()
jarvis = JarvisFirmata()

@app.route('/voice_command', methods=['GET'])
def voice_command():
    command = baymax.takecommand()
    if command != "nenhum":
        baymax.speak(f"Você disse: {command}")
        return jsonify({'command': command})
    else:
        return jsonify({'error': 'Nenhum comando reconhecido'}), 400

@app.route('/arduino_control', methods=['GET'])
def arduino_control():
    result = jarvis.control_led()
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
