import google.generativeai as genai
import PIL.Image
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

model = genai.GenerativeModel('gemini-pro-vision')

img = PIL.Image.open('bob_img.png')
response = model.generate_content(img)

print("Resposta 1:", response.text)

response = model.generate_content(["Descreva a imagem e depois diga quantos animais tem nessa imagem?", img])
response.resolve()

print("Resposta da pergunta", response.text)

# Exemplo de controle com o Arduino
print("Acendendo o LED...")
placa.digital[ledPin].write(1)
time.sleep(2)
print("Desligando o LED...")
placa.digital[ledPin].write(0)

placa.exit()
