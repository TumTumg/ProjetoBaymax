import google.generativeai as genai
from pyfirmata import Arduino
import pyttsx3
import time
import speech_recognition as sr

def main():
    assistenteFalante = True
    ligarMicrofone = True

    # Configuração da API do Gemini
    genai.configure(api_key="SuaChaveAPI")

    # Conexão com o Arduino
    portaArduino = 'COM3'
    placa = Arduino(portaArduino)
    ledPin = 13
    placa.digital[ledPin].write(0)

    # Configuração do modelo Gemini
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config
    )
    chat = model.start_chat(history=[])

    # Configuração do assistente falante
    if assistenteFalante:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 180)
        voz = 1
        engine.setProperty('voice', voices[voz].id)

    # Configuração do reconhecimento de voz
    if ligarMicrofone:
        r = sr.Recognizer()
        mic = sr.Microphone()

    bemVindo = "# Bem Vindo ao chat IA do Baymax! #"
    print(len(bemVindo) * "#")
    print(bemVindo)
    print(len(bemVindo) * "#")
    print("###   Diga 'desligar' para encerrar    ###")
    print("")

    while True:
        if ligarMicrofone:
            with mic as fonte:
                r.adjust_for_ambient_noise(fonte)
                print("Fale alguma coisa (ou diga 'desligar')")
                try:
                    audio = r.listen(fonte, timeout=10)
                    texto = r.recognize_google(audio, language="pt-BR")
                    print("Você disse: {}".format(texto))
                except sr.WaitTimeoutError:
                    print("Tempo de escuta expirado. Não ouvi nada.")
                    texto = ""
                except Exception as e:
                    print("Não entendi o que você disse. Erro:", e)
                    texto = ""
        else:
            texto = input("Escreva sua mensagem (ou 'desligar'): ")

        if texto.lower() == "desligar":
            break

        if texto.strip():
            try:
                response = chat.send_message(texto)
                print("Gemini:", response.text, "\n")

                if assistenteFalante:
                    engine.say(response.text)
                    engine.runAndWait()
            except Exception as e:
                print("Erro ao enviar mensagem para o modelo:", e)
        else:
            print("Texto vazio, não enviando para o modelo.")

        # Exemplo de controle com o Arduino
        print("Acendendo o LED...")
        placa.digital[ledPin].write(1)
        time.sleep(2)
        print("Desligando o LED...")
        placa.digital[ledPin].write(0)

    placa.exit()
    print("Encerrando Chat")

if __name__ == '__main__':
    main()
