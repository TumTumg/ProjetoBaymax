import google.generativeai as genai
from pyfirmata import Arduino, util
import time

genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")

portaArduino = 'COM3'
placa = Arduino(portaArduino)
ledPin = 13
placa.digital[ledPin].write(0)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("Qual o sentido da vida?", stream=True)

for chunk in response:
    print(chunk.text)
    print("_" * 80)

    # Exemplo de controle com o Arduino durante o streaming
    print("Acendendo o LED...")
    placa.digital[ledPin].write(1)
    time.sleep(2)
    print("Desligando o LED...")
    placa.digital[ledPin].write(0)

placa.exit()
