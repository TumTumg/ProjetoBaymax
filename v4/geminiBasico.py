import google.generativeai as genai
from pyfirmata import Arduino, util
import time

# Configuração da API do Gemini
genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")

# Conexão com o Arduino
portaArduino = 'COM3'  # Substitua 'COM3' pela porta correta
placa = Arduino(portaArduino)

# Configuração do pino
ledPin = 13  # Exemplo: utilizando o pino 13 para controlar um LED
placa.digital[ledPin].write(0)  # Certifique-se que o LED está desligado inicialmente

# Configuração do modelo Gemini
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("Qual o sentido da vida?")

print(response.text)

# Exemplo de controle com o Arduino
print("Acendendo o LED...")
placa.digital[ledPin].write(1)  # Liga o LED
time.sleep(2)  # Mantém o LED aceso por 2 segundos
print("Desligando o LED...")
placa.digital[ledPin].write(0)  # Desliga o LED

# Encerrar a comunicação
placa.exit()
