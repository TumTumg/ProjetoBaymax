# MenuBaymax.py

from FuncoesFalas import FuncoesFalas

class MenuBaymax:
    def __init__(self):
        self.falafunc = FuncoesFalas()

    def menu(self):
        """Método principal que exibe o menu e executa as opções selecionadas."""
        while True:
            self.speak("Olá, eu sou o Baymax. Escolha uma opção:")
            menu_options = {
                "1": "Funções de fala",
                "2": "Procurar salas",
                "3": "Reciclagem e limpeza",
                "4": "Temperatura e umidade do ambiente",
                "5": "Biblioteca Senac SBC",
                "6": "Sair"
            }

            # Exibindo o menu principal
            self.speak("Escolha uma opção:")
            for key, value in menu_options.items():
                print(f"{key}: {value}")
            self.speak("Digite o número da opção desejada.")

            command = input("Digite o número da opção desejada: ")  # Leitura da opção do menu
            if command == "1":
                self.speak("Você selecionou Funções de fala. Vamos começar.")
                self.process_falas()
            elif command == "6":
                self.speak("Encerrando o programa. Até logo!")
                break
            else:
                self.speak("Opção não reconhecida. Por favor, tente novamente.")

    def speak(self, text):
        """Converte texto em fala."""
        self.falafunc.speak(text)

    def process_falas(self):
        """Método para processar comandos de fala e oferecer a opção de continuar ou sair."""
        self.speak("Iniciando funções de fala...")
        while True:
            self.speak("Você pode falar agora.")
            command = self.falafunc.takecommand()
            if command != "nenhum":
                response = self.falafunc.process_command(command)
                self.speak(response)

                if "sair" in command:
                    break

                # Adicionando a opção de continuar ou sair após a resposta
                self.speak("Digite 0 para sair ou 1 para continuar com funções de fala.")
                choice = self.falafunc.takecommand()

                if choice == "0":
                    self.speak("Encerrando funções de fala.")
                    break
                elif choice == "1":
                    self.speak("Continuando com funções de fala.")
                else:
                    self.speak("Opção não reconhecida. Continuando com funções de fala.")
            else:
                self.speak("Por favor, tente novamente.")

if __name__ == "__main__":
    menu = MenuBaymax()
    menu.menu()
