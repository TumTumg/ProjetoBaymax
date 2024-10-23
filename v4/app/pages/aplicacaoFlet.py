import flet as ft
import google.generativeai as genai
import pyttsx3
import threading
import os
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host='localhost', user='root', password='', database='baymax'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def createConnection(self):
        """Cria uma conexão com o banco de dados MySQL."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print(f"Conexão com o banco de dados '{self.database}' foi bem-sucedida.")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            self.connection = None

    def closeConnection(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão com o banco de dados fechada.")

    def createUser(self, email, cpf, nomeCompleto, telefone, senha):
        """Insere um novo usuario no banco de dados."""
        try:
            cursor = self.connection.cursor()
            comando = 'INSERT INTO usuario (email, cpf, nomeCompleto, telefone, senha) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(comando, (email, cpf, nomeCompleto, telefone, senha))
            self.connection.commit()
            print(f"Usuário '{nomeCompleto}' criado com sucesso.")
        except Error as e:
            print(f"Erro ao criar usuário: {e}")
        finally:
            cursor.close()

    def readUserByEmail(self, email):
        """Lê um usuário do banco de dados pelo email."""
        try:
            cursor = self.connection.cursor()
            comando = 'SELECT * FROM usuario WHERE email = %s'
            cursor.execute(comando, (email,))
            resultado = cursor.fetchone()
            return resultado
        except Error as e:
            print(f"Erro ao ler usuário: {e}")
            return None
        finally:
            cursor.close()

    def updateUser(self, emailAntigo, emailNovo, senhaNova, nomeCompletoNovo, telefoneNovo):
        """Atualiza um usuário existente no banco de dados."""
        try:
            cursor = self.connection.cursor()
            comando = 'UPDATE usuario SET email = %s, senha = %s, nomeCompleto = %s, telefone = %s WHERE email = %s'
            cursor.execute(comando, (emailNovo, senhaNova, nomeCompletoNovo, telefoneNovo, emailAntigo))
            self.connection.commit()
            print(f"Usuário '{emailAntigo}' atualizado para '{emailNovo}'.")
        except Error as e:
            print(f"Erro ao atualizar usuário: {e}")
        finally:
            cursor.close()

    def deleteUser(self, email):
        """Deleta um usuário do banco de dados."""
        try:
            cursor = self.connection.cursor()
            comando = 'DELETE FROM usuario WHERE email = %s'
            cursor.execute(comando, (email,))
            self.connection.commit()
            print(f"Usuário '{email}' deletado com sucesso.")
        except Error as e:
            print(f"Erro ao deletar usuário: {e}")
        finally:
            cursor.close()

class Inicial:
    def __init__(self, page):
        self.page = page
        self.model = self.initializeModel()
        self.chat = self.model.start_chat(history=[])
        self.recentMessages = []
        self.buildChatView()
        self.buildHomeView()
        self.chat_box = ft.Column()
        self.lock = threading.Lock()
        self.typing_message = None
        self.tts_engine = pyttsx3.init()
        self.speech_enabled = True
        self.speech_queue = []  # Aqui está a definição do speechQueue
        if not self.setVoice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        self.page.on_route_change = self.routeChange
        self.loadingScreen()
        self.conversation_history = []
        self.db = Database(user='root', password='')  # Conexão com o banco de dados
        self.db.createConnection()  # Tenta estabelecer a conexão

    def close(self):
        self.db.closeConnection()

    def loadingScreen(self):
        """Exibe a tela de carregamento."""
        self.imagePath = "../Imagens/BaymaxOi.png"
        if not os.path.isfile(self.imagePath):
            print(f"Erro: A imagem '{self.imagePath}' não foi encontrada.")
            imageContent = ft.Text("Imagem não encontrada.", color=ft.colors.RED)  # Mensagem de erro
        else:

            imageContent = ft.Image(
                src=self.imagePath,
                width=700,  # Defina a largura desejada
                height=700,  # Defina a altura desejada
                fit=ft.ImageFit.CONTAIN
            )

        loadingContent = ft.Stack(
            [

                ft.Container(
                    content=imageContent,
                    alignment=ft.alignment.bottom_right,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text("Seu Assistente Baymax", size=32, color=ft.colors.WHITE),
                    alignment=ft.alignment.top_center,
                    margin=ft.margin.only(bottom=70),
                ),
                ft.Container(
                    content=ft.Image(
                        src="../Imagens/acesso.png",
                        fit=ft.ImageFit.CONTAIN,
                        width=200,  # Define a largura da imagem
                        height=200  # Define a altura da imagem
                    ),
                    alignment=ft.alignment.bottom_left,
                ),
            ]
        )

        self.page.views.append(
            ft.View(
                "/loading",
                [
                    ft.Container(
                        content=loadingContent,
                        bgcolor=ft.colors.RED,
                        expand=True,  # Faz o fundo vermelho ocupar toda a tela
                    ),
                ],
            )

        )

        self.page.update()

        threading.Thread(target=self.delayLoading).start()

    def delayLoading(self):
        """Aguarda um tempo antes de carregar a tela de boas-vindas."""
        threading.Event().wait(3)
        self.buildWelcomeView()  # Chama a nova tela de boas-vindas

    def buildWelcomeView(self, e=None):
        """Constrói a tela de boas-vindas com fundo vermelho e retângulo centralizado e responsivo."""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/welcome",
                [
                    # Fundo da página vermelho
                    ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    # Balão de fala para "Novo por aqui?"
                                    ft.Container(
                                        content=ft.Text("Novo por aqui?", size=24, color=ft.colors.BLACK),
                                        padding=10,
                                        bgcolor=ft.colors.WHITE,  # Fundo branco do balão
                                        border=ft.border.all(2, ft.colors.BLACK),
                                        border_radius=10,
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(bottom=10),  # Margem abaixo
                                    ),

                                    # Botão "Cadastrar"
                                    ft.ElevatedButton(
                                        "Cadastrar",
                                        on_click=self.buildSignupView,
                                        bgcolor=ft.colors.RED_800,
                                        style=ft.ButtonStyle(
                                            color=ft.colors.BLACK,
                                            side=ft.BorderSide(3, ft.colors.BLACK),
                                        ),
                                        width=160,  # Largura reduzida em 20%
                                        height=40,  # Altura reduzida em 20%
                                    ),

                                    # Imagem superior
                                    ft.Image(
                                        src="../Imagens/inicial.png",
                                        fit=ft.ImageFit.CONTAIN,
                                        width=200,  # Largura fixa da imagem
                                        height=200,  # Altura fixa da imagem
                                    ),

                                    ft.Container(
                                        content=ft.Text("Já tem uma conta?", size=24, color=ft.colors.BLACK),
                                        padding=10,
                                        bgcolor=ft.colors.WHITE,  # Fundo branco do balão
                                        border=ft.border.all(2, ft.colors.BLACK),
                                        border_radius=10,
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(top=10),  # Margem acima
                                    ),

                                    # Segunda imagem
                                    ft.Image(
                                        src="../Imagens/olhando.png",
                                        fit=ft.ImageFit.CONTAIN,
                                        width=150,  # Largura fixa da imagem
                                        height=150,  # Altura fixa da imagem
                                    ),

                                    # Botão "Entrar"
                                    ft.ElevatedButton(
                                        "Entrar",
                                        on_click=self.buildLoginView,
                                        bgcolor=ft.colors.RED_800,
                                        style=ft.ButtonStyle(
                                            color=ft.colors.BLACK,
                                            side=ft.BorderSide(3, ft.colors.BLACK),
                                        ),
                                        width=160,  # Largura reduzida em 20%
                                        height=40,  # Altura reduzida em 20%
                                    ),

                                    # Botão "Sair"
                                    ft.ElevatedButton(
                                        "Sair",
                                        on_click=self.closeApp,
                                        bgcolor=ft.colors.RED_800,
                                        style=ft.ButtonStyle(
                                            color=ft.colors.BLACK,
                                            side=ft.BorderSide(3, ft.colors.BLACK),
                                        ),
                                        width=160,  # Largura reduzida em 20%
                                        height=40,  # Altura reduzida em 20%
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,  # Centraliza verticalmente os itens
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                # Centraliza horizontalmente os itens
                            ),
                            bgcolor=ft.colors.WHITE,  # Fundo do retângulo branco
                            border=ft.border.all(3, ft.colors.BLACK),  # Borda preta de 3px
                            padding=20,  # Espaçamento interno (padding)
                            margin=ft.margin.symmetric(vertical=20),  # Margem reduzida no topo e embaixo
                            width=400,  # Largura fixa do retângulo
                            # Altura do retângulo adaptável, sem especificar a altura diretamente
                            alignment=ft.alignment.center,  # Centraliza o retângulo dentro do container
                        ),
                        bgcolor=ft.colors.RED,  # Fundo da página vermelho
                        expand=True,  # Garante que o container ocupe toda a página
                        alignment=ft.alignment.center,  # Centraliza todo o conteúdo da página
                    )
                ]
            )
        )
        self.page.update()

    def buildLoginView(self, e=None):
        """Constrói a tela de login."""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/login",
                [
                    ft.Column(
                        controls=[
                            ft.AppBar(title=ft.Text("Login"), bgcolor=ft.colors.SURFACE_VARIANT),
                            ft.Column(
                                controls=[
                                    ft.TextField(label="Email", width=300),
                                    ft.TextField(label="Senha", width=300, password=True),
                                    ft.ElevatedButton("Entrar", on_click=self.handleLogin, bgcolor=ft.colors.BLUE),
                                    ft.TextButton("Voltar", on_click=self.buildWelcomeView, style=ft.ButtonStyle(
                                        color=ft.colors.WHITE,
                                        bgcolor=ft.colors.GREY_400,
                                    )),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    )
                ]
            )
        )
        self.page.update()

    def buildSignupView(self, e):
        """Constrói a tela de cadastro."""
        self.page.views.clear()

        # Armazene referências para os campos
        self.email_field = ft.TextField(label="Email", width=200)
        self.cpf_field = ft.TextField(label="CPF", width=200)
        self.nome_field = ft.TextField(label="Nome Completo", width=200)
        self.telefone_field = ft.TextField(label="Telefone", width=200)
        self.senha_field = ft.TextField(label="Senha", width=200, password=True)
        self.senha_confirmacao_field = ft.TextField(label="Confirmação da Senha", width=200, password=True)

        # Contêiner principal com fundo e bordas
        signup_container = ft.Container(
            content=ft.Column(
                controls=[
                    # Balão de fala para "Preencha os dados abaixo"
                    ft.Container(
                        content=ft.Text("Preencha os dados abaixo", size=24, color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,  # Fundo branco do balão
                        border=ft.border.all(2, ft.colors.BLACK),
                        border_radius=10,
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(bottom=10),  # Margem abaixo
                    ),
                    self.email_field,
                    self.cpf_field,
                    self.nome_field,
                    self.telefone_field,
                    self.senha_field,
                    self.senha_confirmacao_field,
                    ft.ElevatedButton(
                        "Cadastrar",
                        on_click=self.handleSignup,
                        bgcolor=ft.colors.RED_800,  # Cor do botão
                        style=ft.ButtonStyle(
                            color=ft.colors.BLACK,
                            side=ft.BorderSide(3, ft.colors.BLACK),
                        ),
                        width=160,  # Largura do botão
                        height=40,  # Altura do botão
                    ),
                    ft.TextButton(
                        "Voltar",
                        on_click=self.buildWelcomeView,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREY_400,
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Centraliza verticalmente os itens
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.colors.WHITE,  # Cor de fundo do contêiner
            border=ft.border.all(3, ft.colors.BLACK),  # Borda preta de 3px
            padding=20,  # Espaçamento interno (padding)
            margin=ft.margin.symmetric(vertical=20),  # Margem reduzida no topo e embaixo
            width=400,  # Largura fixa do retângulo
            alignment=ft.alignment.center,  # Centraliza o retângulo dentro do container
            border_radius=10,  # Bordas arredondadas
        )

        self.page.views.append(
            ft.View(
                "/signup",
                [
                    ft.AppBar(title=ft.Text("Cadastrar"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Container(
                        content=ft.Stack(  # Usando Stack para sobreposição
                            controls=[
                                # Contêiner para a imagem
                                ft.Container(
                                    content=ft.Image(
                                        src="../Imagens/cadastro.png",  # Caminho da imagem
                                        fit=ft.ImageFit.CONTAIN,
                                        width=200,  # Largura fixa da imagem
                                        height=200,  # Altura fixa da imagem
                                    ),
                                    margin=ft.margin.only(bottom=20),  # Margem abaixo da imagem
                                    alignment=ft.alignment.center,  # Centraliza a imagem dentro do contêiner
                                ),
                                ft.Container(  # Coloca o signup_container por cima da imagem
                                    content=signup_container,  # Contêiner de cadastro
                                    alignment=ft.alignment.center,  # Centraliza o contêiner de cadastro
                                )
                            ],
                        ),
                        bgcolor=ft.colors.RED,  # Fundo da página vermelho
                        expand=True,  # Garante que o container ocupe toda a página
                        alignment=ft.alignment.center,  # Centraliza todo o conteúdo da página
                    ),
                ]
            )
        )

        self.page.update()

    def closeApp(self, e):  # Adicione o parâmetro `e`
        """Fecha o aplicativo."""
        self.db.closeConnection()  # Fecha a conexão com o banco de dados, se necessário
        os._exit(0)  # Comando para fechar o aplicativo

    def handleSignup(self, e):
        """Lida com o cadastro do usuário."""
        email = self.email_field.value
        cpf = self.cpf_field.value
        nome_completo = self.nome_field.value
        telefone = self.telefone_field.value
        senha = self.senha_field.value
        senha_confirmacao = self.senha_confirmacao_field.value

        if senha == senha_confirmacao:
            self.db.createUser(email, cpf, nome_completo, telefone, senha)  # Chamando o método de cadastro
            snackbar = ft.SnackBar(ft.Text("Usuário Cadastrado Com Sucesso!"), open=True)
            self.page.add(snackbar)
            self.page.update()
            threading.Timer(3.0, lambda: self.buildLoginView())  # Redireciona para a tela de login após 3 segundos
        else:
            snackbar = ft.SnackBar(ft.Text("As senhas não correspondem!"), open=True)
            self.page.add(snackbar)
            self.page.update()

    def handleLogin(self, e):
        """Lida com a autenticação do usuário."""
        loginView = self.page.views[-1]  # Acessa a última view (a de login)

        # Verifica se os campos de email e senha estão dentro de um Column
        controls = loginView.controls[0].controls[1].controls  # Ajuste para acessar o Column correto

        email = controls[0].value
        senha = controls[1].value

        try:
            user = self.db.readUserByEmail(email)
            if user and user[5] == senha:  # Verifica se o usuário existe e se a senha está correta
                print(f"Usuário '{email}' autenticado com sucesso.")
                self.page.go("/")  # Navega para a tela principal
            else:
                self.showErrorDialog("Email ou senha incorretos.")
        except Exception as error:
            print(f"Erro ao autenticar: {error}")
            self.showErrorDialog("Erro ao autenticar. Tente novamente.")

    def showErrorDialog(self, message):
        """Exibe um diálogo de erro."""
        alertDialog = ft.AlertDialog(
            title=ft.Text("Erro de Autenticação"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.closeDialog(alertDialog))
            ],
        )
        self.page.overlay.append(alertDialog)  # Atualização do método deprecated
        alertDialog.open()
        self.page.update()

    def closeDialog(self, dialog):
        self.page.overlay.remove(dialog)
        self.page.update()

    def setVoice(self):
        """Define a voz a ser usada pelo motor TTS."""
        try:
            voices = self.tts_engine.getProperty('voices')  # Corrigido aqui para usar 'tts_engine'
            # Tente encontrar uma voz masculina
            for voice in voices:
                if "male" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    print(f"Voz definida para: {voice.name}")
                    return True
            return False  # Se não encontrou voz masculina
        except Exception as e:
            print(f"Erro ao definir a voz: {str(e)}")
            return False

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
            system_instruction=system_instruction   # Usando a instrução do arquivo
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
                            ft.NavigationBarDestination(icon=ft.icons.HOME, label="Home"),  # Botão Home
                            ft.NavigationBarDestination(icon=ft.icons.CHAT, label="Chat"),
                            ft.NavigationBarDestination(icon=ft.icons.INFO, label="Sobre"),
                        ],
                        on_change=self.handleNavigation,
                    ),
                    ft.Text("Bem-vindo ao Assistente Baymax!", size=24),
                ],
            )
        )
        self.page.update()  # Atualiza a página

    def handleNavigation(self, e):
        """Navega entre as diferentes páginas do aplicativo."""
        if e.control.selected_index == 0:
            self.page.go("/")  # Navega para a página Home
        elif e.control.selected_index == 1:
            self.page.go("/chatIAFlet")  # Navega para a página de chat IA
        elif e.control.selected_index == 2:
            self.page.go("/sobre")  # Navega para a página 'Sobre'

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

    def speak_next(self):
        """Fala a próxima mensagem da fila, se houver."""
        if self.speech_queue:
            text_to_speak = self.speech_queue.pop(0)  # Remove a primeira mensagem da fila
            self.speak(text_to_speak)  # Faz o Baymax falar

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
                    self.buildBackButton(),
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
                    self.buildBackButton(),
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

