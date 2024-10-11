import flet as ft
import google.generativeai as genai
import pyttsx3
import threading
import os
import speech_recognition as sr
from db import Database

class Inicial:
    def __init__(self, page):
        self.page = page
        self.model = self.initializeModel()
        self.chat = self.model.start_chat(history=[])
        self.recent_messages = []
        self.buildChatView()
        self.chat_box = ft.Column()
        self.lock = threading.Lock()
        self.typing_message = None
        self.tts_engine = pyttsx3.init()
        self.speech_enabled = True
        if not self.setVoice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        self.page.on_route_change = self.routeChange
        self.show_notification = True
        self.loadingScreen()
        self.conversation_history = []  # Inicializa a lista de histórico de conversas
        self.db = Database(user='root', password='')  # Conexão com o banco de dados
        self.db.create_connection()  # Tenta estabelecer a conexão
        # Aqui você pode adicionar mais lógica do seu aplicativo

    def close(self):
        self.db.close_connection()


    def loadingScreen(self):
        """Exibe a tela de carregamento."""
        self.image_path = "C:/Users/decau/PycharmProjects/ProjetoBaymax/v4/app/Imagens/BaymaxOlá.png"

        # Verifica se a imagem existe
        if not os.path.isfile(self.image_path):
            print(f"Erro: A imagem '{self.image_path}' não foi encontrada.")
            image_content = ft.Text("Imagem não encontrada.", color=ft.colors.RED)  # Mensagem de erro
        else:
            image_content = ft.Image(src=self.image_path, width=self.page.width, height=self.page.height,
                                     fit=ft.ImageFit.CONTAIN)  # Imagem carregada

        loading_content = ft.Stack(
            [
                # Camada de fundo da imagem
                ft.Container(
                    content=image_content,
                    alignment=ft.alignment.bottom_right,  # Imagem no canto inferior direito
                    expand=True,
                ),
                # Texto de "Seu Assistente Baymax"
                ft.Container(
                    content=ft.Text("Seu Assistente Baymax", size=32, color=ft.colors.WHITE),
                    alignment=ft.alignment.top_center,  # Centraliza no topo
                    margin=ft.margin.only(bottom=80),  # Ajusta a margem para distanciar do topo
                ),
                # Texto de "Acesso Antecipado"
                ft.Container(
                    content=ft.Text("Acesso Antecipado", size=20, color=ft.colors.YELLOW_300),
                    alignment=ft.alignment.bottom_left,  # Posiciona no canto inferior esquerdo
                    margin=ft.margin.only(left=20, bottom=20),  # Ajusta a margem para distanciar do canto
                ),
            ]
        )

        # Configura a página com a tela de carregamento
        self.page.views.append(
            ft.View(
                "/loading",
                [
                    ft.Container(
                        content=loading_content,
                        bgcolor=ft.colors.RED,
                        width=self.page.width,
                        height=self.page.height,
                    ),
                ],
            )
        )
        self.page.update()

        # Aguarda 5 segundos antes de carregar a tela de login
        threading.Thread(target=self.delayLoading).start()

    def delayLoading(self):
        """Aguarda um tempo antes de carregar a tela de login."""
        threading.Event().wait(2)  # Aguardando 2 segundos
        self.buildLoginView()  # Carrega a tela de login

    def buildLoginView(self):
        """Constrói a tela de login."""
        self.page.views.clear()  # Limpa as views atuais
        self.page.views.append(
            ft.View(
                "/login",
                [
                    ft.AppBar(title=ft.Text("Login"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Column(
                        controls=[
                            ft.TextField(label="Usuário", width=300),
                            ft.TextField(label="Senha", width=300, password=True),
                            ft.ElevatedButton("Entrar", on_click=self.handleLogin, bgcolor=ft.colors.BLUE),
                            ft.TextButton("Cadastrar", on_click=self.buildSignupView, style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.GREEN_300,  # Cor de fundo
                            )),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
            )
        )
        self.page.update()

    def buildSignupView(self, e):
        """Constrói a tela de cadastro."""
        self.page.views.clear()  # Limpa as views atuais
        self.page.views.append(
            ft.View(
                "/signup",
                [
                    ft.AppBar(title=ft.Text("Cadastrar"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Column(
                        controls=[
                            ft.TextField(label="Usuário", width=300),  # index 0
                            ft.TextField(label="Senha", width=300, password=True),  # index 1
                            ft.TextField(label="Confirmação da Senha", width=300, password=True),  # index 2
                            ft.ElevatedButton("Cadastrar", on_click=self.handleSignup, bgcolor=ft.colors.GREEN),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
            )
        )
        self.page.update()

    def handleSignup(self, e):
        """Lida com o cadastro do usuário."""
        # Acessando a última view e pegando a coluna de controles
        signup_view = self.page.views[-1]
        controls = signup_view.controls[1].controls  # Acesse os controles dentro da coluna

        username = controls[0].value  # Usuário (TextField)
        password = controls[1].value  # Senha (TextField)
        confirm_password = controls[2].value  # Confirmação da Senha (TextField)

        # Lógica simples para verificação
        if password == confirm_password:
            # Aqui você pode adicionar lógica para armazenar o novo usuário
            print(f"Usuário {username} cadastrado com sucesso!")  # Exemplo de saída no console
            self.buildLoginView()  # Retorna à tela de login após cadastro
        else:
            ft.alert("As senhas não coincidem. Tente novamente.")  # Notificação de erro

    def handleLogin(self, e):
        """Lida com a autenticação do usuário."""
        username = self.page.views[-1].controls[1].controls[0].value  # Usuário
        password = self.page.views[-1].controls[1].controls[1].value  # Senha

        # Exemplo simples de autenticação (substitua pela sua lógica real)
        if username == "admin" and password == "senha123":  # Altere para a lógica de autenticação real
            self.page.go("/")  # Navega para a página inicial se autenticado
        else:
            # Cria um alerta com um botão para fechar
            alert_dialog = ft.AlertDialog(
                title=ft.Text("Erro de Autenticação"),
                content=ft.Text("Usuário ou senha incorretos. Tente novamente."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: alert_dialog.close())
                ],
            )

            self.page.dialog = alert_dialog  # Atribui o diálogo à página
            alert_dialog.open()  # Abre o diálogo
            self.page.update()  # Atualiza a página

    def setVoice(self):
        """Configura uma voz masculina para o motor de texto para fala (TTS)."""
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower():  # Verifica se a voz é masculina
                self.tts_engine.setProperty('voice', voice.id)
                return True
        return False  # Retorna False se não encontrou uma voz masculina

    def initializeModel(self):
        """Configura o modelo de IA com a API do Gemini."""
        genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real

        # Lendo o arquivo .txt com a configuração do system_instruction
        try:
            with open("system_instruction.txt", "r", encoding="utf-8") as file:
                system_instruction = file.read().strip()
        except FileNotFoundError:
            system_instruction = "default_instruction"  # Instrução padrão caso o arquivo não seja encontrado
            print("Arquivo 'system_instruction.txt' não encontrado. Usando instrução padrão.")
        except UnicodeDecodeError as e:
            print(f"Erro ao ler o arquivo: {e}")
            system_instruction = "default_instruction"  # Defina uma instrução padrão ou trate o erro de outra forma

        # Configuração do modelo
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 1024,
                "response_mime_type": "text/plain",
            },
            system_instruction=system_instruction  # Usando a instrução do arquivo
        )
        return model

    def routeChange(self, route_event_or_str):
        """Atualiza a view de acordo com a rota."""
        self.page.views.clear()  # Limpa as views atuais
        route = route_event_or_str.route if hasattr(route_event_or_str, 'route') else route_event_or_str
        views = {
            "/": self.buildHomeView,
            "/chatIAFlet": self.buildChatView,
            "/sobre": self.buildAboutView,
            "/contato": self.buildContactView,
        }
        view_function = views.get(route, self.buildErrorView)
        view_function()  # Chama a função de view correspondente

        # Limpar o conteúdo do chat ao voltar para a página inicial
        if route == "/":
            self.clearChatContent()  # Limpa o conteúdo do chat

        self.page.update()  # Atualiza a página

    def buildHomeView(self):
        """Constrói a página inicial."""
        self.page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Seu Assistente Baymax"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.NavigationBar(
                        destinations=[
                            ft.NavigationBarDestination(icon=ft.icons.CHAT, label="Chat IA"),
                            ft.NavigationBarDestination(icon=ft.icons.INFO, label="Sobre Nós"),
                            ft.NavigationBarDestination(icon=ft.icons.CONTACT_MAIL, label="Contato"),
                            ft.NavigationBarDestination(icon=ft.icons.EXIT_TO_APP, label="Sair"),
                        ],
                        on_change=self.handleNavigation,
                    ),
                    ft.Text("Bem-vindo ao Assistente Baymax!", size=24),
                ],
            )
        )
        self.page.update()  # Atualiza a página

        if self.show_notification:
            self.showWelcomeNotification("Usuário")  # Exibe notificação de boas-vindas

    def showWelcomeNotification(self, usuario):
        """Exibe uma notificação de boas-vindas ao usuário."""
        notification_text = (
            f"Bem-vindo {usuario}!\n"
            "---Novidades!---\n"
            "- Apresentamos o chat IA\n"
            "- Novas Funcionalidades!\n"
            "- Correção de bugs\n"
            "- Suporte ao usuário\n"
            "- Promoção à saúde\n"
            "- Biblioteca Senac\n"
            "- Auxílio em eventos\n"
            "-----//-----\n"
            "Por que você mesmo não dá uma olhada?"
        )

        # Limpar qualquer diálogo existente
        self.page.overlay.clear()

        # Criar o diálogo
        self.dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Bem-vindo!"),
            content=ft.Text(notification_text),
            actions=[
                ft.Checkbox(label="Não mostrar novamente", on_change=self.noShowAgain),
                ft.ElevatedButton("Fechar", on_click=self.closeDialog),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Adiciona o diálogo ao overlay
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()  # Atualiza a página para mostrar o novo diálogo

    def closeDialog(self, e):
        """Fecha o diálogo de boas-vindas."""
        if hasattr(self, 'dialog'):
            self.dialog.open = False  # Fecha o diálogo
            self.page.overlay.remove(self.dialog)  # Remove o diálogo da sobreposição
            self.page.update()  # Atualiza a página para refletir a mudança

    def noShowAgain(self, e):
        """Ação para o checkbox 'Não mostrar novamente'."""
        self.show_notification = not e.control.value  # Atualiza a variável com base no estado do checkbox

    def hideNotification(self):
        """Oculta completamente a notificação da tela."""
        # Aqui você pode adicionar a lógica para ocultar outros elementos da UI, se necessário
        self.show_notification = False  # Ou outra lógica para controlar a exibição

    def handleNavigation(self, e):
        """Navega entre as diferentes páginas do aplicativo."""
        if e.control.selected_index == 0:
            self.page.go("/chatIAFlet")  # Navega para a página de chat IA
        elif e.control.selected_index == 1:
            self.page.go("/sobre")  # Navega para a página 'Sobre Nós'
        elif e.control.selected_index == 2:
            self.page.go("/contato")  # Navega para a página de contato
        elif e.control.selected_index == 3:
            self.page.go("/")  # Retorna para a página principal

    def buildChatView(self):
        """Constrói a interface do chat com balões de fala."""
        self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        self.message_input = ft.TextField(hint_text="Digite sua mensagem...", expand=True, on_submit=self.sendMessage)

        # Botão para ativar/desativar a fala
        self.voice_button = ft.ElevatedButton(
            "Desativar Voz", on_click=self.toggleVoice, bgcolor=ft.colors.RED, color=ft.colors.WHITE
        )

        # Botão para ativar reconhecimento de voz
        self.mic_button = ft.ElevatedButton("Falar", on_click=self.startVoiceRecognition, bgcolor=ft.colors.BLUE,
                                            color=ft.colors.WHITE)

        self.page.views.append(
            ft.View(
                "/chatIAFlet",
                [
                    ft.AppBar(title=ft.Text("Chat IA"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Container(
                        self.chat_box,
                        expand=True,
                        padding=10,
                        bgcolor=ft.colors.GREY,
                        border_radius=10,
                        height=self.page.height - 100
                    ),
                    ft.Row(
                        controls=[
                            self.message_input,
                            ft.ElevatedButton("Enviar", on_click=self.sendMessage, bgcolor=ft.colors.RED,
                                              color=ft.colors.WHITE),
                            ft.ElevatedButton("Limpar Chat", on_click=self.clearChat, bgcolor=ft.colors.RED,
                                              color=ft.colors.WHITE),
                            self.mic_button  # Botão de microfone
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    self.voice_button,
                    self.buildBackButton(),
                ],
            )
        )
        self.page.update()

    def toggleVoice(self, e):
        """Ativa ou desativa a fala."""
        self.speech_enabled = not self.speech_enabled
        self.voice_button.text = "Ativar Voz" if not self.speech_enabled else "Desativar Voz"
        self.page.update()

    def startVoiceRecognition(self, e):
        """Inicia o reconhecimento de voz em uma thread separada."""
        threading.Thread(target=self.recognizeSpeech).start()

    def startVoiceRecognition(self, e):
        """Inicia o reconhecimento de voz em uma thread separada."""
        threading.Thread(target=self.recognizeSpeech).start()

    def recognizeSpeech(self):
        """Reconhece a fala e envia como mensagem."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()  # Certifique-se de que o microfone está ativo e funcionando

        # Verificação de disponibilidade do microfone
        try:
            with mic as source:
                print("Ajustando o nível de ruído... Por favor, fale agora.")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)  # Escuta até 5 segundos
                texto = recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {texto}")
                self.message_input.value = texto
                self.sendMessage(None)  # Chama o método de envio de mensagem
        except sr.UnknownValueError:
            print("Não consegui entender o que você disse.")
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento de fala: {e}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    def sendMessage(self, e):
        texto = self.message_input.value.strip()
        if texto.lower() == "sair":
            self.page.go("/")
            return

        if not texto:
            return

        if getattr(self, 'processing_message', False):
            return

        self.processing_message = True

        try:
            # Enviar a mensagem
            user_bubble = ft.Container(
                content=ft.Text(f"Você: {texto}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_400,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(user_bubble)

            # Simula que Baymax está digitando
            self.typing_message = ft.Container(
                content=ft.Text("Baymax está digitando...", size=16, color=ft.colors.YELLOW),
                bgcolor=ft.colors.GREY,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_left,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(self.typing_message)
            self.page.update()

            threading.Thread(target=self.handleSendMessage, args=(texto,)).start()  # Envia em uma nova thread

        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            self.processing_message = False



    def handleSendMessage(self, texto):
        """Processa o envio da mensagem em uma nova thread."""
        response = self.chat.send_message(texto)

        # Adiciona a interação ao histórico
        self.conversation_history.append({"user": texto, "baymax": response.text})

        if hasattr(response, 'text'):
            resposta_texto = response.text
        else:
            resposta_texto = "Desculpe, não consegui entender."

        # Remove a mensagem de "digitando"
        if self.typing_message:
            self.chat_box.controls.remove(self.typing_message)
            self.typing_message = None

        # Adiciona a nova mensagem do Baymax ao chat
        baymax_bubble = ft.Container(
            content=ft.Text(f"Baymax: {resposta_texto}", size=16, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED,
            padding=10,
            border_radius=10,
            alignment=ft.alignment.center_left,
            margin=ft.margin.only(bottom=5)
        )
        self.chat_box.controls.append(baymax_bubble)

        self.message_input.value = ""
        self.page.update()

        print(f"Baymax vai falar: {resposta_texto}")

        # Adiciona a fala à fila
        self.speech_queue.append(resposta_texto)
        self.speak_next()  # Inicia a fala se não estiver falando

    def speak(self, text):
        """Faz o Baymax falar o texto fornecido."""
        try:
            if self.speech_enabled:
                print(f"Iniciando fala: {text}")
                with self.lock:  # Garante que só uma chamada possa executar a fala
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    print(f"Baymax falou: {text}")
            else:
                print("Voz desativada, não falando.")
        except Exception as e:
            print(f"Erro ao falar: {str(e)}")

    def clearChatContent(self):
        """Limpa o conteúdo do chat."""
        if hasattr(self, 'chat_box'):
            self.chat_box.controls.clear()
            self.page.update()
        else:
            print("chat_box não foi inicializado.")

    def clearChat(self, e):
        """Limpa o histórico de chat."""
        self.chat_box.controls.clear()
        self.page.update()

    def buildAboutView(self):
        """Constrói a view 'Sobre Nós'."""
        self.page.views.append(
            ft.View(
                "/sobre",
                [
                    ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Aqui estão algumas informações sobre nós.", size=24),
                ],
            )
        )

    def buildContactView(self):
        """Constrói a view 'Contato'."""
        self.page.views.append(
            ft.View(
                "/contato",
                [
                    ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Entre em contato conosco.", size=24),
                ],
            )
        )

    def buildBackButton(self):
        """Cria o botão de voltar para a página inicial."""
        return ft.ElevatedButton(
            "Voltar",
            on_click=lambda e: self.page.go("/"),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
        )

    def buildErrorView(self):
        """Constrói a view de erro."""
        self.page.views.append(
            ft.View(
                "/error",
                [
                    ft.AppBar(title=ft.Text("Erro"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("A página solicitada não foi encontrada.", size=24),
                ],
            )
        )

def main(page: ft.Page):
        page.title = "Baymax - Seu Assistente Virtual"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.window.width = 800
        page.window.height = 800
        page.bgcolor = ft.colors.WHITE

        inicial = Inicial(page)

if __name__ == "__main__":
        ft.app(target=main)

