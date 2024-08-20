from app import app
from flask import render_template, request
import json
import requests
from flask import session
from flask import redirect, url_for
import secrets

app.secret_key = secrets.token_hex(16)  # Isso irá gerar uma chave secreta hexadecimal de 16 bytes

app = Flask(__name__)

# Rota para o index
@app.route('/')
def index():
    return render_template('index.html')

# Rota para as funcionalidades
@app.route('/funcionalidades')
def funcionalidades():
    return render_template('funcionalidades.html')

# Rota para o IA
@app.route('/ia')
def ia():
    return render_template('IA.html')

# Rota para sobre nós
@app.route('/sobreNos')
def sobre_nos():
    return render_template('sobreNos.html')

# Rota para fechamento
@app.route('/fechamento')
def fechamento():
    return render_template('fechamento.html')

# Rota para arquivos estáticos (imagens)
@app.route('/imagens/<path:filename>')
def imagens(filename):
    return send_from_directory(os.path.join(app.root_path, 'Imagens'), filename)

if __name__ == '__main__':
    app.run(debug=True)
