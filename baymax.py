import pyttsx3
import speech_recognition as sr

# Inicialize o pyttsx3 com o driver padrão
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Configura as propriedades de voz (opcional)

# Função para converter texto em fala
def speak(text):
    engine.say(text)
    print(text)
    engine.runAndWait()

# Função para capturar e reconhecer comandos de voz
def takecommand():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Ouvindo...")
            r.adjust_for_ambient_noise(source, duration=1)
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5, phrase_time_limit=5)

        try:
            print("Reconhecendo...")
            query = r.recognize_google(audio, language='pt-BR')
            print(f"Usuário disse: {query}")
            return query

        except sr.UnknownValueError:
            speak("Não entendi o que você disse. Por favor, tente novamente.")
            return "nenhum"
        except sr.RequestError:
            speak("Erro ao conectar ao serviço de reconhecimento de fala.")
            return "nenhum"

    except sr.WaitTimeoutError:
        speak("Tempo de espera esgotado. Nenhum som detectado.")
        return "nenhum"
    except Exception as e:
        speak(f"Erro inesperado: {e}")
        return "nenhum"

# Função principal que mantém a conversa
def main():
    speak("Olá, eu sou o Baymax")
    while True:
        command = takecommand()
        if command != "nenhum":
            speak(f"Você disse: {command}")
            if "sair" in command.lower():
                speak("Encerrando o programa. Até logo!")
                break  # Encerra o loop se o usuário disser "sair"
        else:
            speak("Por favor, tente novamente.")

if __name__ == "__main__":
    main()
