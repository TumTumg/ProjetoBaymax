import pyttsx3
import speech_recognition as sr
import datetime

class Baymax:
    def __init__(self):
        # Inicialize o pyttsx3 com o driver padrão
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)  # Configura as propriedades de voz (opcional)
        self.recognizer = sr.Recognizer()

        # Lista de tarefas
        self.listaTarefas = []

        # Dicionário de comandos e respostas
        self.listaComandos = {
            "como vai": self.responder_como_vai,
            "olá": self.responder_ola,
            "ajuda": self.responder_ajuda,
            "qual o seu nome": self.responder_nome,
            "o que você pode fazer": self.responder_o_que_fazer,
            "que horas são": self.responder_horas,
            "conte uma piada": self.responder_piada,
            "quem é seu criador": self.responder_criador,
            "obrigado": self.responder_obrigado,
            "adicionar tarefa": self.adicionar_tarefa,
            "listar tarefas": self.listar_tarefas,
            "clima": self.responder_clima,
            "sair": self.responder_sair,
            "onde estou": self.responder_localizacao,
            "notícias": self.responder_noticias,
            "dica de saúde": self.responder_dica_saude,
            "cálculo": self.responder_calculo,
            "fatos interessantes": self.responder_fatos_interessantes
        }

    def falar(self, texto):
        """Função para converter texto em fala"""
        self.engine.say(texto)
        print(texto)
        self.engine.runAndWait()

    def capturar_comando(self):
        """Função para capturar e reconhecer comandos de voz"""
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
                self.falar("Não entendi o que você disse. Por favor, tente novamente.")
                return "nenhum"
            except sr.RequestError:
                self.falar("Erro ao conectar ao serviço de reconhecimento de fala.")
                return "nenhum"

        except sr.WaitTimeoutError:
            self.falar("Tempo de espera esgotado. Nenhum som detectado.")
            return "nenhum"
        except Exception as e:
            self.falar(f"Erro inesperado: {e}")
            return "nenhum"

    def processar_comando(self, comando):
        """Função para processar o comando reconhecido e retornar a resposta correspondente"""
        for key in self.listaComandos:
            if key in comando:
                return self.listaComandos[key](comando)
        return "Desculpe, não entendi o comando."

    def responder_como_vai(self, comando):
        return "Estou funcionando bem, obrigado por perguntar!"

    def responder_ola(self, comando):
        return "Olá! Como posso ajudar você hoje?"

    def responder_ajuda(self, comando):
        return "Você pode me pedir para saber mais sobre comandos disponíveis."

    def responder_nome(self, comando):
        return "Eu sou o Baymax, seu assistente pessoal."

    def responder_o_que_fazer(self, comando):
        return "Posso conversar com você, adicionar tarefas à sua lista, contar piadas, fornecer a hora atual e muito mais."

    def responder_horas(self, comando):
        now = datetime.datetime.now()
        return f"Agora são {now.hour} horas e {now.minute} minutos."

    def responder_piada(self, comando):
        return "Por que o livro de matemática se suicidou? Porque tinha muitos problemas."

    def responder_criador(self, comando):
        return "Eu fui criado por um desenvolvedor muito talentoso."

    def responder_obrigado(self, comando):
        return "De nada! Estou aqui para ajudar."

    def adicionar_tarefa(self, comando):
        self.falar("Qual tarefa você gostaria de adicionar?")
        tarefa = self.capturar_comando()
        if tarefa != "nenhum":
            self.listaTarefas.append(tarefa)
            return f"Tarefa '{tarefa}' adicionada à lista."
        else:
            return "Não consegui entender a tarefa. Por favor, tente novamente."

    def listar_tarefas(self, comando):
        if self.listaTarefas:
            tarefas = "\n".join(self.listaTarefas)
            return f"Suas tarefas são:\n{tarefas}"
        else:
            return "Sua lista de tarefas está vazia."

    def responder_clima(self, comando):
        return "O clima está ótimo para um passeio!"

    def responder_sair(self, comando):
        return "Encerrando o programa. Até logo!"

    def responder_localizacao(self, comando):
        return "Você está na sua localização atual. Eu ainda não tenho a capacidade de determinar a localização exata."

    def responder_noticias(self, comando):
        return "Desculpe, ainda não consigo buscar notícias. Que tal perguntar sobre outra coisa?"

    def responder_dica_saude(self, comando):
        return "Lembre-se de beber água regularmente e fazer pausas para se alongar durante o dia."

    def responder_calculo(self, comando):
        return "Desculpe, ainda não consigo realizar cálculos. Talvez em uma versão futura."

    def responder_fatos_interessantes(self, comando):
        return "Você sabia que o coração de um camarão está em sua cabeça?"

    def main(self):
        """Função principal que mantém a conversa"""
        self.falar("Olá, eu sou o Baymax")
        while True:
            comando = self.capturar_comando()
            if comando != "nenhum":
                resposta = self.processar_comando(comando)
                self.falar(resposta)
                if "sair" in comando:
                    break
            else:
                self.falar("Por favor, tente novamente.")

if __name__ == "__main__":
    baymax = Baymax()
    baymax.main()
s