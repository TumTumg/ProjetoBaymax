from flask import render_template, request, jsonify
from . import create_app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def api_message():
    user_message = request.json.get('message', '')
    # Process the message and interact with your model here
    # For now, we will echo the message for testing
    return jsonify({"response": f"Você disse: {user_message}"})
