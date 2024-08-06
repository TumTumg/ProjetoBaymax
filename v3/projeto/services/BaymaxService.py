import pyttsx3
import speech_recognition as sr
import datetime

class BaymaxService:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)
        self.recognizer = sr.Recognizer()
        self.taskList = []
        self.commandList = {
            "como vai": self.answerHowAreYou,
            "olá": self.answerHello,
            "ajuda": self.answerHelp,
            "qual o seu nome": self.answerName,
            "o que você pode fazer": self.answerWhatCanYouDo,
            "que horas são": self.answerTime,
            "conte uma piada": self.answerJoke,
            "quem é seu criador": self.answerCreator,
            "obrigado": self.answerThankYou,
            "adicionar tarefa": self.addTask,
            "listar tarefas": self.listTasks,
            "clima": self.answerWeather,
            "sair": self.answerExit,
            "onde estou": self.answerLocation,
            "notícias": self.answerNews,
            "dica de saúde": self.answerHealthTip,
            "cálculo": self.answerCalculation,
            "fatos interessantes": self.answerInterestingFacts
        }

    def speak(self, text):
        self.engine.say(text)
        print(text)
        self.engine.runAndWait()

    def captureCommand(self):
        try:
            with sr.Microphone() as source:
                print("Ouvindo...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)

            try:
                print("Reconhecendo...")
                query = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"Usuário disse: {query}")
                return query.lower()

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

    def processCommand(self, command):
        for key in self.commandList:
            if key in command:
                return self.commandList[key](command)
        return "Desculpe, não entendi o comando."

    def answerHowAreYou(self, command):
        return "Estou funcionando bem, obrigado por perguntar!"

    def answerHello(self, command):
        return "Olá! Como posso ajudar você hoje?"

    def answerHelp(self, command):
        return "Você pode me pedir para saber mais sobre comandos disponíveis."

    def answerName(self, command):
        return "Eu sou o Baymax, seu assistente pessoal."

    def answerWhatCanYouDo(self, command):
        return "Posso conversar com você, adicionar tarefas à sua lista, contar piadas, fornecer a hora atual e muito mais."

    def answerTime(self, command):
        now = datetime.datetime.now()
        return f"Agora são {now.hour} horas e {now.minute} minutos."

    def answerJoke(self, command):
        return "Por que o livro de matemática se suicidou? Porque tinha muitos problemas."

    def answerCreator(self, command):
        return "Eu fui criado por um desenvolvedor muito talentoso."

    def answerThankYou(self, command):
        return "De nada! Estou aqui para ajudar."

    def addTask(self, command):
        self.speak("Qual tarefa você gostaria de adicionar?")
        task = self.captureCommand()
        if task != "nenhum":
            self.taskList.append(task)
            return f"Tarefa '{task}' adicionada à lista."
        else:
            return "Não consegui entender a tarefa. Por favor, tente novamente."

    def listTasks(self, command):
        if self.taskList:
            tasks = "\n".join(self.taskList)
            return f"Suas tarefas são:\n{tasks}"
        else:
            return "Sua lista de tarefas está vazia."

    def answerWeather(self, command):
        return "O clima está ótimo para um passeio!"

    def answerExit(self, command):
        return "Encerrando o programa. Até logo!"

    def answerLocation(self, command):
        return "Você está na sua localização atual. Eu ainda não tenho a capacidade de determinar a localização exata."

    def answerNews(self, command):
        return "Desculpe, ainda não consigo buscar notícias. Que tal perguntar sobre outra coisa?"

    def answerHealthTip(self, command):
        return "Lembre-se de beber água regularmente e fazer pausas para se alongar durante o dia."

    def answerCalculation(self, command):
        return "Desculpe, ainda não consigo realizar cálculos. Talvez em uma versão futura."

    def answerInterestingFacts(self, command):
        return "Você sabia que o coração de um camarão está em sua cabeça?"

    def main(self):
        self.speak("Olá, eu sou o Baymax")
        while True:
            command = self.captureCommand()
            if command != "nenhum":
                response = self.processCommand(command)
                self.speak(response)
                if "sair" in command:
                    break
            else:
                self.speak("Por favor, tente novamente.")
