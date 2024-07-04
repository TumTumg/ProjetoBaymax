import pyttsx3
import speech_recognition as sr

class Baymax:
    def __init__(self):
        # Inicializa o pyttsx3 com o driver padrão
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)  # Configura as propriedades de voz (opcional)

    # Função para converter texto em fala
    def speak(self, text):
        self.engine.say(text)
        print(text)
        self.engine.runAndWait()

    # Função para capturar e reconhecer comandos de voz
    def takecommand(self):
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
                self.speak("Não entendi o que você disse. Por favor, tente novamente.")
                return "nenhum"
            except sr.RequestError:
                self.speak("Erro ao conectar ao serviço de reconhecimento de fala.")
                return "nenhum"

        except sr.WaitTimeoutError:
            self.speak("Tempo de espera esgotado. Nenhum som detectado.")
            return "nenhum"
        except Exception as e:
            self.speak(f"Erro inesperado: {e}")
            return "nenhum"

if __name__ == "__main__":
    baymax = Baymax()
    baymax.speak("Olá, eu sou o Baymax")
    command = baymax.takecommand()
    if command != "nenhum":
        baymax.speak(f"Você disse: {command}")
