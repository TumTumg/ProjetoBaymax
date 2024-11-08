import logging
import flet as ft
import google.generativeai as genai
import pyttsx3
import queue
from queue import Queue
import threading
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error



class Database:
    def __init__(self, user, password):
        self.connection = None
        self.cursor = None
        self.user = user
        self.password = password
        self.createConnection()

    def createConnection(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user=self.user,
                password=self.password,
                database='baymax'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Conexão com o banco de dados 'baymax' foi bem-sucedida.")
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def closeConnection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Conexão com o banco de dados fechada.")

    def _checkConnection(self):
        if self.connection is None or not self.connection.is_connected():
            self.createConnection()

    def createUser(self, email, cpf, nomeCompleto, telefone, senha):
        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                comando = 'INSERT INTO usuario (email, cpf, nomeCompleto, telefone, senha) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(comando, (email, cpf, nomeCompleto, telefone, senha))
                self.connection.commit()
                print(f"Usuário '{nomeCompleto}' criado com sucesso.")
        except mysql.connector.Error as e:
            print(f"Erro ao criar usuário: {e}")
        except Exception as e:
            print(f"Erro inesperado ao criar usuário: {e}")

    def readUserByEmail(self, email):
        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                comando = 'SELECT * FROM usuario WHERE email = %s'
                cursor.execute(comando, (email,))
                resultado = cursor.fetchone()
                return resultado
        except Error as e:
            print(f"Erro ao ler usuário: {e}")
            return None

    def updateUser(self, emailAntigo, emailNovo, senhaNova, nomeCompletoNovo, telefoneNovo):
        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                comando = 'UPDATE usuario SET email = %s, senha = %s, nomeCompleto = %s, telefone = %s WHERE email = %s'
                cursor.execute(comando, (emailNovo, senhaNova, nomeCompletoNovo, telefoneNovo, emailAntigo))
                self.connection.commit()
                print(f"Usuário '{emailAntigo}' atualizado para '{emailNovo}'.")
        except Error as e:
            print(f"Erro ao atualizar usuário: {e}")

    def deleteUser(self, email):
        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                comando = 'DELETE FROM usuario WHERE email = %s'
                cursor.execute(comando, (email,))
                self.connection.commit()
                print(f"Usuário '{email}' deletado com sucesso.")
        except Error as e:
            print(f"Erro ao deletar usuário: {e}")

    def salvarConversa(self, usuario_id, mensagem_usuario, resposta_baymax):
        """Salva a conversa se o `usuario_id` for válido."""
        if usuario_id is None:
            print("Aviso: ID do usuário está nulo, conversa não será salva.")
            return False  # Retornando False se o ID for inválido

        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO conversa (idUsuario, mensagemUsuario, respostaBaymax, dataHora) "
                    "VALUES (%s, %s, %s, NOW())",
                    (usuario_id, mensagem_usuario, resposta_baymax)
                )
                self.connection.commit()
                print("Conversa salva com sucesso.")
                return True  # Retorna True se a operação for bem-sucedida
        except Exception as e:
            print(f"Erro ao salvar conversa: {e}")
            return False  # Retorna False se ocorrer algum erro


class Inicial:
    def __init__(self, page, conn=None, session_id=None, loop=None):
        """Inicializa a aplicação Baymax com configurações essenciais de UI, modelo, banco de dados e TTS."""
        self.page = page
        self.font_size = 16  # Defina um valor inicial para font_size

        # Inicialização do modelo e chat
        self.model = self.initializeModel()
        self.chat = self.model.start_chat(history=[])
        self.recentMessages = []

        # Inicialização do chat_box
        self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        self.buildChatView()  # Constrói a interface do chat
        self.buildHomeView()  # Constrói a interface inicial
        self.processing_message = False
        self.message_input = ft.TextField()

        # Variáveis para armazenar o texto do feedback e a avaliação selecionada
        self.feedbackText = ""
        self.avaliacao = ""

        # Inicialização da rede neural e configurações de TTS
        self.lock = threading.Lock()
        self.tts_engine = pyttsx3.init()
        self.speech_enabled = True
        self.speech_queue = Queue()

        # **AQUI**: Definindo o atributo speech_messages
        self.speech_messages = []  # Lista para armazenar as mensagens faladas

        # Conexão com o banco de dados
        self.db = Database(user='root', password='')
        self.db.createConnection()  # Estabelece a conexão com o banco
        self.user_id = None  # ID do usuário atual, definido após login

        # Configura voz do TTS
        if not self.setVoice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        # Configura a mudança de rota
        self.page.on_route_change = self.routeChange
        self.loadingScreen()

        # Carrega o histórico de conversas do usuário (se `user_id` estiver definido)
        if self.user_id is not None:
            self.loadUserHistory()

        # Inicialização da fonte padrão
        self.font_size = 16
        self.updateFontSize()  # Atualiza o tamanho da fonte inicialmente
        self.loadingScreen()

    def speak(self, text):
        """Faz o Baymax falar a resposta utilizando o TTS."""
        if self.speech_enabled:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

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

    def closeApp(self, e=None):
        """Fecha o aplicativo."""
        self.page.window_destroy()  # Fecha o aplicativo completamente

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
                                            color=ft.colors.WHITE,  # Cor das letras em branco
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
                                            color=ft.colors.WHITE,  # Cor das letras em branco
                                            side=ft.BorderSide(3, ft.colors.BLACK),
                                        ),
                                        width=160,  # Largura reduzida em 20%
                                        height=40,  # Altura reduzida em 20%
                                    ),

                                    # Botão "Sair"
                                    ft.ElevatedButton(
                                        "Sair",
                                        on_click=self.closeApp,  # Chama a função closeApp
                                        bgcolor=ft.colors.RED_800,
                                        style=ft.ButtonStyle(
                                            color=ft.colors.WHITE,  # Cor das letras em branco
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
        """Constrói a tela de login com fundo vermelho e retângulo centralizado e responsivo."""
        self.page.views.clear()

        # Criar os campos de entrada
        self.email_field = ft.TextField(label="Email", width=200, color=ft.colors.BLACK)
        self.senha_field = ft.TextField(label="Senha", width=200, password=True, color=ft.colors.BLACK)

        # Campo de mensagem para mostrar a mensagem de sucesso de cadastro, se houver
        self.login_message_field = ft.Text(
            self.success_message if hasattr(self, 'success_message') else "",
            size=16,
            color=ft.colors.GREEN if hasattr(self, 'success_message') else ft.colors.BLACK,
            visible=hasattr(self, 'success_message')
        )
        # Remove a mensagem de sucesso após exibir
        if hasattr(self, 'success_message'):
            del self.success_message

        # Criar o container do retângulo branco com bordas arredondadas
        white_rectangle = ft.Container(
            content=ft.Column(
                controls=[
                    self.login_message_field,  # Coloca a mensagem de sucesso logo acima dos campos de entrada
                    self.email_field,
                    self.senha_field,
                    ft.ElevatedButton(
                        "Entrar",
                        on_click=self.handleLogin,
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
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.colors.WHITE,  # Fundo do retângulo branco
            border=ft.border.all(3, ft.colors.BLACK),  # Borda preta de 3px
            padding=20,  # Espaçamento interno (padding)
            width=400,  # Largura fixa do retângulo
            height=300,  # Altura fixa do retângulo
            border_radius=10,  # Adiciona bordas arredondadas
            alignment=ft.alignment.center,  # Centraliza o retângulo dentro do container
        )

        # Criar a coluna que conterá o conteúdo
        login_column = ft.Column(
            controls=[
                ft.AppBar(title=ft.Text("Login"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Container(
                    content=white_rectangle,  # Apenas o retângulo branco com a mensagem dentro
                    expand=True,  # Garante que o container ocupe toda a página
                    alignment=ft.alignment.center,  # Centraliza todo o conteúdo da página
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,  # Garante que a coluna ocupe toda a altura disponível
        )

        # Fundo da página vermelho
        self.page.views.append(
            ft.View(
                "/login",
                [
                    ft.Container(
                        content=login_column,
                        bgcolor=ft.colors.RED,  # Fundo da página vermelho
                        expand=True,  # Garante que o container ocupe toda a página
                    )
                ]
            )
        )
        self.page.update()  # Atualiza a página após todas as alterações

    def autenticar_usuario(self, email, senha):
        """Autentica o usuário e retorna o ID do usuário, se válido."""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                database='baymax',
                user='root',
                password=''
            )
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM usuario WHERE email = %s AND senha = %s", (email, senha))
            usuario = cursor.fetchone()

            if usuario:
                print(f"Usuário '{usuario[0]}' autenticado com sucesso.")
                return usuario[0]  # Retorna o ID do usuário
            else:
                print("Email ou senha incorretos.")
                return None
        except mysql.connector.Error as e:
            print(f"Erro ao acessar o banco de dados: {e}")
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    def updateLoginMessage(self, message, visible):
        """Atualiza a mensagem de login."""
        self.login_message_field.text = message
        self.login_message_field.visible = visible
        print(
            f"Mensagem de erro: '{self.login_message_field.text}' visível: {self.login_message_field.visible}")  # Para depuração
        self.page.update()  # Atualiza a página para refletir as mudanças

    def handleLogin(self, e):
        """Lida com a autenticação do usuário e armazena o ID."""
        email = self.email_field.value
        senha = self.senha_field.value

        try:
            user_id = self.autenticar_usuario(email, senha)
            if user_id:
                self.user_id = user_id  # Define o ID do usuário autenticado
                print(f"Usuário autenticado com ID: {self.user_id}")
                self.page.go("/")
                self.login_message_field.visible = False
            else:
                self.updateLoginMessage("Email ou senha incorretos.", True)
        except Exception as error:
            print(f"Erro ao autenticar: {error}")
            self.updateLoginMessage("Erro ao autenticar. Tente novamente.", True)

    def buildSignupView(self, e):
        """Constrói a tela de cadastro."""
        self.page.views.clear()

        # Armazene referências para os campos
        self.email_field = ft.TextField(label="Email", width=200, color=ft.colors.BLACK)
        self.cpf_field = ft.TextField(label="CPF", width=200, color=ft.colors.BLACK)
        self.nome_field = ft.TextField(label="Nome Completo", width=200, color=ft.colors.BLACK)
        self.telefone_field = ft.TextField(label="Telefone", width=200, color=ft.colors.BLACK)
        self.senha_field = ft.TextField(label="Senha", width=200, password=True, color=ft.colors.BLACK)
        self.senha_confirmacao_field = ft.TextField(
            label="Confirmação da Senha", width=200, password=True, color=ft.colors.BLACK
        )

        # Campo de mensagem invisível
        self.signup_message_field = ft.Text(
            "Campos em branco ou senhas não coincidem.",
            size=16,
            color=ft.colors.RED,
            visible=False  # Começa invisível
        )

        # Função para processar o cadastro
        def process_signup(e):
            email = self.email_field.value
            cpf = self.cpf_field.value
            nomeCompleto = self.nome_field.value
            telefone = self.telefone_field.value
            senha = self.senha_field.value
            senha_confirmacao = self.senha_confirmacao_field.value

            # Verifique se os campos estão preenchidos
            if not email or not cpf or not nomeCompleto or not telefone or not senha:
                self.signup_message_field.value = "Preencha todos os campos."
                self.signup_message_field.color = ft.colors.RED
                self.signup_message_field.visible = True
                self.page.update()
                return

            # Verifique se as senhas coincidem
            if senha != senha_confirmacao:
                self.signup_message_field.value = "As senhas não coincidem."
                self.signup_message_field.color = ft.colors.RED
                self.signup_message_field.visible = True
                self.page.update()
                return

            # Insira o usuário no banco de dados
            try:
                self.db.createUser(email, cpf, nomeCompleto, telefone, senha)
                # Mensagem de sucesso
                self.success_message = "Usuário cadastrado com sucesso!"
                self.buildLoginView()  # Redireciona para a página de login
            except Exception as e:
                # Mensagem de erro
                self.signup_message_field.value = f"Erro ao cadastrar: {e}"
                self.signup_message_field.color = ft.colors.RED
                self.signup_message_field.visible = True

            self.page.update()

        # Botão para processar o cadastro com o estilo solicitado
        signup_button = ft.ElevatedButton(
            text="Cadastrar",
            on_click=process_signup,
            bgcolor=ft.colors.RED_800,  # Cor do botão
            style=ft.ButtonStyle(
                color=ft.colors.BLACK,
                side=ft.BorderSide(3, ft.colors.BLACK),
            ),
            width=160,  # Largura do botão
            height=40,  # Altura do botão
        )

        # Contêiner principal com fundo e bordas (diminuído para largura 300 e altura ajustada)
        signup_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text("Preencha os dados abaixo", size=24, color=ft.colors.BLACK),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                        border=ft.border.all(2, ft.colors.BLACK),
                        border_radius=10,
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(bottom=10),
                    ),
                    self.email_field,
                    self.cpf_field,
                    self.nome_field,
                    self.telefone_field,
                    self.senha_field,
                    self.senha_confirmacao_field,
                    self.signup_message_field,  # Campo de mensagem
                    signup_button,
                    ft.TextButton(
                        "Voltar",
                        on_click=self.buildWelcomeView,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREY_400,
                        )
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(3, ft.colors.BLACK),
            padding=20,
            margin=ft.margin.symmetric(vertical=20),
            width=300,  # Diminui a largura do formulário
            height=600,  # Ajuste de altura
            alignment=ft.alignment.center,
            border_radius=10,
        )

        # A imagem deve ficar à direita do formulário
        signup_layout = ft.Row(
            controls=[
                signup_container,  # Formulário de cadastro
                ft.Container(
                    content=ft.Image(
                        src="../Imagens/cadastro.png",
                        fit=ft.ImageFit.CONTAIN,
                        width=200,
                        height=200,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(left=20),  # Espaço entre o formulário e a imagem
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Centraliza o conteúdo da row
            spacing=20,  # Define o espaço entre o formulário e a imagem
        )

        # Adicionando a view ao layout sem AppBar
        self.page.views.append(
            ft.View(
                "/signup",
                [
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                signup_layout,
                            ]
                        ),
                        bgcolor=ft.colors.RED,
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                ],
            )
        )
        self.page.update()


    def handleSignup(self, e):
        """Lida com o cadastro do usuário."""
        # Armazena os valores dos campos
        email = self.email_field.value
        cpf = self.cpf_field.value
        nome_completo = self.nome_field.value
        telefone = self.telefone_field.value
        senha = self.senha_field.value
        senha_confirmacao = self.senha_confirmacao_field.value

        # Verifique se algum dos campos está vazio
        if not email or not cpf or not nome_completo or not telefone or not senha or not senha_confirmacao:
            self.updateSignupMessage("Todos os campos devem ser preenchidos.")
            return

        # Verifique se as senhas correspondem
        if senha != senha_confirmacao:
            self.updateSignupMessage("As senhas não correspondem!")
            return

        try:
            # Supondo que você tenha um método de cadastro no banco de dados
            self.db.createUser(email, cpf, nome_completo, telefone, senha)  # Chamando o método de cadastro
            self.updateSignupMessage("Usuário cadastrado com sucesso!")  # Mensagem de sucesso
            threading.Timer(3.0, self.routeLoginCadastro).start()  # Redireciona para a tela de login após 3 segundos
        except Exception as error:
            logging.error(f"Erro ao cadastrar o usuário: {error}")
            self.updateSignupMessage("Erro ao cadastrar. Tente novamente.")

    def updateSignupMessage(self, message):
        # Acesse a view de cadastro
        signupView = self.page.views[-1]
        # Acesse o contêiner onde a mensagem será exibida
        message_container = signupView.controls[0].content.controls[7]  # Ajuste o índice conforme necessário
        message_container.value = message
        message_container.visible = True  # Torna a mensagem visível
        self.page.update()

    def routeLoginCadastro(self):
        """Redireciona para a tela de login após o cadastro."""
        self.buildLoginView()  # Chama a função que constrói a tela de login

    def showErrorDialog(self, message):
        """Exibe um diálogo de erro com a mensagem especificada."""
        try:
            # Cria um objeto AlertDialog com a mensagem de erro
            alertDialog = ft.AlertDialog(
                title=ft.Text("Erro"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("Fechar", on_click=lambda e: self.page.overlay.remove(alertDialog))
                ]
            )
            # Adiciona o diálogo à sobreposição da página e o abre
            self.page.overlay.append(alertDialog)
            alertDialog.open = True
        except Exception as error:
            print(f"Erro ao exibir o diálogo de erro: {error}")

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
        # Implemente a inicialização do modelo
        pass
        """Configura o modelo de IA com a API do Gemini."""
        try:
            genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real
        except Exception as e:
            print(f"Erro ao configurar a API do Gemini: {e}")
            return None

        try:
            with open("system_instruction.txt", "r", encoding="utf-8") as file:
                self.system_instruction = file.read().strip()
        except FileNotFoundError:
            self.system_instruction = "default_instruction"
            print("Arquivo 'system_instruction.txt' não encontrado. Usando instrução padrão.")
        except UnicodeDecodeError as e:
            print(f"Erro ao ler o arquivo: {e}")
            self.system_instruction = "default_instruction"

        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50,
                    # AUMENTANDO O TAMANHO DA MENSAGEM
                    "max_output_tokens": 5000000,  # Aumente para x tokens
                    "response_mime_type": "text/plain",
                },
                system_instruction=self.system_instruction
            )
            return model
        except Exception as e:
            print(f"Erro ao inicializar o modelo: {e}")
            return None


    def buildAppBar(self):
        """Constrói a AppBar universal para todas as páginas com menu de configurações estilizado."""
        # Ícone do usuário
        user_icon = ft.IconButton(
            icon=ft.icons.ACCOUNT_CIRCLE,
            on_click=None,
            tooltip="Perfil de Usuário"
        )

        def logout_action(e):
            """Função de logout para redefinir o estado e redirecionar para a página de boas-vindas."""
            print("Iniciando logout...")
            self.is_authenticated = False
            self.current_user = None
            self.page.views.clear()
            self.buildWelcomeView()
            self.page.go("/welcome")
            self.page.update()

        def login_action(e):
            """Função de login que autentica o usuário e redireciona para a página inicial."""
            self.is_authenticated = True
            self.current_user = "Usuário Teste"
            if self.is_authenticated:
                print(f"Usuário '{self.current_user}' autenticado com sucesso.")
                self.page.views.clear()
                self.buildHomeView()
                self.page.go("/")
                self.page.update()
            else:
                print("Falha na autenticação. Verifique suas credenciais.")

        # Menu de configurações com ícones e textos brancos
        settings_menu = ft.MenuBar(
            controls=[
                ft.SubmenuButton(
                    content=ft.Icon(ft.icons.SETTINGS, tooltip="Configurações", color=ft.colors.WHITE),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Fonte", color=ft.colors.WHITE),
                            on_click=self.openSettings
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Sair", color=ft.colors.RED),
                            on_click=logout_action
                        ),
                    ],
                ),
            ]
        )

        return ft.AppBar(
            title=ft.Text("Projeto Baymax", size=20, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED_800,
            actions=[user_icon, settings_menu]
        )

    def openSettings(self, e):
        """Abre a página de configurações com ajuste de fonte."""
        print("Abrindo configurações...")
        settings_dialog = ft.AlertDialog(
            title=ft.Text("Configurações", size=20, weight="bold", color=ft.colors.BLACK),
            content=ft.Column(
                controls=[
                    ft.Text("Tamanho da Fonte:", size=16, color=ft.colors.BLACK),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.icons.REMOVE, on_click=self.decreaseFontSize),
                            ft.Text(f"{self.font_size}px", size=16, color=ft.colors.BLACK),
                            ft.IconButton(icon=ft.icons.ADD, on_click=self.increaseFontSize),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: self.closeSettingsDialog(settings_dialog))
            ]
        )
        if settings_dialog not in self.page.overlay:
            self.page.overlay.append(settings_dialog)
        settings_dialog.open = True
        self.page.update()

    def closeSettingsDialog(self, settings_dialog):
        """Fecha o diálogo de configurações e atualiza a página."""
        settings_dialog.open = False
        self.page.update()

    def increaseFontSize(self, e):
        """Aumenta o tamanho da fonte e atualiza a fonte da página."""
        self.font_size += 2
        self.updateFontSize()
        self.page.update()

    def decreaseFontSize(self, e):
        """Diminui o tamanho da fonte e atualiza a fonte da página."""
        if self.font_size > 8:
            self.font_size -= 2
            self.updateFontSize()
            self.page.update()

    def updateFontSize(self):
        """Aplica o tamanho da fonte em todos os elementos na `buildHomeView`."""
        for view in self.page.views:
            for control in view.controls:
                self.applyFontSize(control)

    def applyFontSize(self, control):
        """Aplica a fonte específica para diferentes tipos de controles."""
        if isinstance(control, ft.Text):
            control.size = self.font_size
        elif isinstance(control, ft.TextField):
            control.size = self.font_size
        elif isinstance(control, ft.ElevatedButton):
            control.text_style = ft.TextStyle(size=self.font_size)
        elif isinstance(control, ft.Container) and control.content:
            self.applyFontSize(control.content)
        elif isinstance(control, (ft.Row, ft.Column, ft.ListView)):
            for item in control.controls:
                self.applyFontSize(item)

    def buildHomeView(self):
        """Constrói a página inicial aplicando o tamanho da fonte e deixando o contêiner se ajustar ao conteúdo automaticamente."""
        self.page.views.append(
            ft.View(
                "/",
                [
                    self.buildAppBar(),
                    ft.NavigationBar(
                        bgcolor=ft.colors.RED,
                        destinations=[
                            ft.NavigationBarDestination(icon=ft.icons.CHAT, label="Chat"),
                            ft.NavigationBarDestination(icon=ft.icons.HOME, label="Home"),
                            ft.NavigationBarDestination(icon=ft.icons.INFO, label="Sobre"),
                        ],
                        on_change=self.handleNavigation,
                    ),
                    ft.Container(
                        bgcolor=ft.colors.WHITE,
                        expand=True,
                        padding=20,
                        content=ft.ListView(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        "Novidades da Semana!!\nAtualizações no Software",
                                        size=self.font_size,
                                        color=ft.colors.BLACK,
                                        text_align=ft.TextAlign.CENTER,
                                        no_wrap=False  # Permite o texto expandir em múltiplas linhas
                                    ),
                                    bgcolor="#f0f0f0",
                                    padding=20,
                                    margin=ft.margin.only(bottom=20),
                                    border_radius=10,
                                    alignment=ft.alignment.center,
                                    border=ft.border.all(2, ft.colors.RED),
                                    expand=True  # Expande o contêiner com base no conteúdo do texto
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "EVENTOS SEMANAL:\nApresentação de PI, turma TI18N\ndas 19:30 até as 21:00, 08/11/2024",
                                        size=self.font_size,
                                        color=ft.colors.BLACK,
                                        text_align=ft.TextAlign.CENTER,
                                        no_wrap=False
                                    ),
                                    bgcolor="#f0f0f0",
                                    padding=20,
                                    margin=ft.margin.only(top=20),
                                    border_radius=10,
                                    alignment=ft.alignment.center,
                                    border=ft.border.all(2, ft.colors.RED),
                                    expand=True
                                ),
                            ],
                            auto_scroll=True,
                        ),
                    ),
                ],
            )
        )
        self.page.update()

    def handleNavigation(self, e):
        """Navega entre as diferentes páginas do aplicativo."""
        route = e.control.destinations[e.control.selected_index].label.lower()
        if route == "chat":
            self.routeChange("/chatIAFlet")  # Navega para a página de Chat
        elif route == "home":
            self.routeChange("/")  # Navega para a página Home
        elif route == "sobre":
            self.routeChange("/sobre")  # Navega para a página 'Sobre'
        elif route == "login":
            self.routeChange("/login")  # Navega para a página de Login
        elif route == "welcome":
            self.routeChange("/welcome")  # Navega para a página de Boas-Vindas
        elif route == "signup":
            self.routeChange("/signup")  # Navega para a página de Cadastro

    def routeChange(self, route_event_or_str):
        """Atualiza a view de acordo com a rota."""
        print(f"Changing route to: {route_event_or_str}")  # Log da rota
        self.page.views.clear()  # Limpa as views atuais
        route = route_event_or_str.route if hasattr(route_event_or_str, 'route') else route_event_or_str
        views = {
            "/chatIAFlet": self.buildChatView,
            "/": self.buildHomeView,
            "/sobre": self.buildAboutView,
            "/login": self.buildLoginView,  # Adiciona a página de Login
            "/welcome": self.buildWelcomeView,  # Adiciona a página de Boas-Vindas
            "/signup": self.buildSignupView,  # Adiciona a página de Cadastro
        }
        view_function = views.get(route, self.buildErrorView)
        view_function()  # Chama a função de view correspondente
        self.page.update()  # Atualiza a página

    def buildChatView(self):
        """Constrói a interface do chat com balões de fala e funcionalidade de copiar."""
        # Entrada de mensagem
        self.message_input = ft.TextField(
            hint_text="Digite sua mensagem...",
            expand=True,
            on_submit=self.sendMessage,
            color=ft.colors.BLACK,
        )

        # Botão para ativar/desativar a fala
        self.voice_button = ft.ElevatedButton(
            "Desativar Voz",
            on_click=self.toggleVoice,
            bgcolor=ft.colors.RED_800,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.colors.BLACK,
                side=ft.BorderSide(3, ft.colors.BLACK),
            ),
            width=160,
            height=40,
        )

        # Botão para ativar reconhecimento de voz
        self.mic_button = ft.ElevatedButton(
            "Falar",
            on_click=self.startVoiceRecognition,
            bgcolor=ft.colors.RED_800,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.colors.BLACK,
                side=ft.BorderSide(3, ft.colors.BLACK),
            ),
            width=160,
            height=40,
        )

        # Estilo do container do chat
        chat_container_style = {
            "expand": True,
            "padding": 10,
            "bgcolor": ft.colors.WHITE,
            "border_radius": 10,
        }

        # Monta a View com elementos organizados e AppBar universal
        self.page.views.append(
            ft.View(
                "/chatIAFlet",
                [
                    self.buildAppBar(),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    self.chat_box,
                                    **chat_container_style
                                ),
                                ft.Row(
                                    controls=[
                                        self.message_input,
                                        ft.ElevatedButton(
                                            "Enviar",
                                            on_click=self.sendMessage,
                                            bgcolor=ft.colors.RED_800,
                                            color=ft.colors.WHITE,
                                            style=ft.ButtonStyle(
                                                color=ft.colors.BLACK,
                                                side=ft.BorderSide(3, ft.colors.BLACK),
                                            ),
                                            width=160,
                                            height=40,
                                        ),
                                        ft.ElevatedButton(
                                            "Limpar Chat",
                                            on_click=self.clearChat,
                                            bgcolor=ft.colors.RED_800,
                                            color=ft.colors.WHITE,
                                            style=ft.ButtonStyle(
                                                color=ft.colors.BLACK,
                                                side=ft.BorderSide(3, ft.colors.BLACK),
                                            ),
                                            width=160,
                                            height=40,
                                        ),
                                        self.mic_button
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                                ft.Row(
                                    controls=[
                                        self.voice_button,
                                        self.buildBackButton(),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        bgcolor=ft.colors.WHITE,
                        expand=True,
                    )
                ],
            )
        )
        self.page.update()

    def buildAboutView(self):
        """Constrói a visualização da página 'Sobre' com a AppBar universal, ajustada para responsividade."""

        # Conteúdo da página 'Sobre' com ajuste de tamanho de fonte para melhor responsividade
        about_content = ft.Column(
            controls=[
                ft.Text("Bem-vindo ao Baymax!", size=self.page.window.width * 0.035, weight="bold",
                        color=ft.colors.BLACK),
                ft.Text(
                    "Baymax é um assistente virtual inovador, projetado para aprimorar a experiência dos usuários através de respostas rápidas e uma navegação intuitiva.",
                    size=self.page.window.width * 0.02, color=ft.colors.BLACK
                ),

                # Seção: Desafio e Solução
                self.createInfoSection(
                    title="Desafio e Solução",
                    content=(
                        "A busca por informações rápidas e precisas no campus pode ser desafiadora, especialmente em relação a horários de aulas, localização de instalações, eventos e detalhes sobre os cursos oferecidos. "
                        "Pensando nisso, o Baymax surge como um assistente virtual interativo, projetado para orientar visitantes e alunos em suas necessidades, fornecendo um suporte completo e eficiente."
                    ),
                    color=ft.colors.RED,
                ),

                # Seção: Propósito do Projeto
                self.createInfoSection(
                    title="Propósito do Projeto",
                    content=(
                        "O Projeto Baymax busca promover a acessibilidade e facilitar o cotidiano de alunos e visitantes ao integrar tecnologia de ponta de maneira dinâmica e acessível. "
                        "Nossa proposta é oferecer uma experiência envolvente que una funcionalidade e inovação, tornando o processo de busca por informações mais fluido e intuitivo."
                    ),
                    color=ft.colors.RED,
                ),

                # Seção: Missão
                self.createInfoSection(
                    title="Missão",
                    content=(
                        "Nossa missão é transformar a jornada dos alunos e visitantes ao campus, oferecendo informações precisas e suporte personalizado de forma ágil e confiável. "
                        "Baymax representa nosso compromisso com a excelência no atendimento e na comunicação, garantindo que todos os usuários se sintam bem-vindos e apoiados."
                    ),
                    color=ft.colors.RED,
                ),

                # Seção: Atualizações Futuras
                self.createInfoSection(
                    title="Evolução Contínua",
                    content=(
                        "Estamos comprometidos em manter o Baymax atualizado com novas funcionalidades e integrações com serviços educacionais, "
                        "garantindo que ele continue relevante e útil para toda a comunidade. A cada atualização, buscamos melhorar a experiência do usuário e expandir as possibilidades de interação."
                    ),
                    color=ft.colors.RED,
                ),

                # Seção: Como Utilizar o APP
                self.createInfoSection(
                    title="Como Utilizar o Baymax",
                    content=(
                        "Para tirar o máximo proveito do Baymax, comece interagindo pelo chat. Pergunte sobre horários de aulas, localização de salas, ou detalhes sobre eventos. "
                        "O assistente também pode fornecer informações sobre cursos e outros recursos disponíveis no campus. Navegue pela barra de navegação para acessar diferentes seções do aplicativo. "
                        "Sinta-se à vontade para explorar e descobrir tudo o que o Baymax tem a oferecer!"
                    ),
                    color=ft.colors.RED,
                ),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        )

        # Responsividade do container principal
        about_container = ft.Container(
            content=ft.Column(controls=[about_content], scroll=ft.ScrollMode.AUTO),
            width=self.page.window.width * 0.95,  # Aumenta a largura para 95% da tela
            height=self.page.window.height * 0.8,  # Aumenta a altura para 80% da tela
            padding=ft.padding.all(15),  # Aumenta o padding
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            alignment=ft.alignment.center,
        )

        # Container de feedback com responsividade
        feedback_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Avalie sua experiência:", size=self.page.window.width * 0.02, weight="bold",
                            color=ft.colors.BLACK),
                    ft.RadioGroup(
                        content=ft.Column(
                            controls=[
                                ft.Radio(value="útil", label="Útil"),
                                ft.Radio(value="não útil", label="Não Útil"),
                            ]
                        ),
                        on_change=lambda e: setattr(self, 'avaliacao', e.control.value)
                    ),
                    ft.TextField(
                        hint_text="Descreva sua experiência...",
                        multiline=True,
                        on_change=lambda e: setattr(self, 'feedback_text', e.control.value)
                    ),
                    ft.ElevatedButton(
                        text="Enviar Feedback",
                        on_click=self.submitFeedback
                    ),
                ],
                spacing=10
            ),
            width=self.page.window.width * 0.9,  # Ajusta para 90% da largura da janela
            padding=15,  # Aumenta o padding para melhor estética
            bgcolor=ft.colors.GREY,
            border_radius=10,
        )

        # Adicione `feedback_container` ao `about_content`
        about_content.controls.append(feedback_container)

        # Barra de navegação fixa
        navigation_bar = ft.NavigationBar(
            bgcolor=ft.colors.RED,
            destinations=[
                ft.NavigationBarDestination(icon=ft.icons.CHAT, label="Chat"),
                ft.NavigationBarDestination(icon=ft.icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.icons.INFO, label="Sobre"),
            ],
            on_change=self.handleNavigation,
        )

        # Adiciona a AppBar, contêiner de conteúdo, contêiner de feedback e barra de navegação fixa à página
        self.page.views.append(
            ft.View(
                "/about",
                bgcolor=ft.colors.WHITE,
                controls=[
                    self.buildAppBar(),
                    about_container,
                    navigation_bar
                ],
            )
        )
        self.page.update()

    def salvarFeedback(self, idConversa, avaliacao):
        """Salva o feedback no banco de dados."""
        self._checkConnection()  # Verifica se a conexão está ativa
        try:
            with self.connection.cursor() as cursor:
                query = """
                    INSERT INTO feedback (idConversa, avaliacao)
                    VALUES (%s, %s)
                """
                valores = (idConversa, avaliacao)
                cursor.execute(query, valores)
                self.connection.commit()
                print("Feedback salvo com sucesso!")
        except Error as e:
            print(f"Erro ao salvar feedback: {e}")

    def submitFeedback(self, e):
        self.feedbackText = self.feedback_text.value  # Captura o valor do campo de texto
        self.avaliacao = self.avaliacao_dropdown  # Corrige para capturar o valor diretamente se for uma string

        print(f"Feedback Text: '{self.feedbackText}', Avaliacao: '{self.avaliacao}'")  # Verificação

        if self.feedbackText and self.avaliacao:
            idConversa = ...  # lógica para obter idConversa
            self.db.salvarFeedback(idConversa, self.avaliacao)
            print("Feedback enviado com sucesso!")
        else:
            print("Preencha as informações de feedback.")

    def createInfoSection(self, title, content, color):
        """Cria uma seção de informação com título e conteúdo estilizados."""
        return ft.Column(
            controls=[
                ft.Text(title, size=22, weight="bold", color=color),
                ft.Text(content, size=16, color=ft.colors.BLACK),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
        )

    def buildBackButton(self):
        """Cria o botão de voltar para a página inicial."""
        return ft.ElevatedButton(
            "Voltar",
            on_click=lambda e: self.routeChange("/"),  # Use routeChange para navegar
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
        )

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
                self.sendMessageFromVoice(texto)  # Chama o método de envio de mensagem
        except sr.UnknownValueError:
            print("Não consegui entender o que você disse.")
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento de fala: {e}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    def startVoiceRecognition(self, e):
        """Inicia o reconhecimento de voz em uma thread separada."""
        threading.Thread(target=self.recognizeSpeech).start()

    def toggleVoice(self, e):
        """Ativa ou desativa a fala do Baymax."""
        self.speech_enabled = not self.speech_enabled  # Alterna o estado da fala
        if self.speech_enabled:
            self.voice_button.text = "Desativar Voz"
        else:
            self.voice_button.text = "Ativar Voz"
            if self.tts_engine and self.tts_engine.isBusy():
                self.tts_engine.stop()  # Interrompe a fala caso esteja em andamento
                print("Fala interrompida.")  # Imprime apenas uma vez
        self.page.update()

    def startSpeaking(self):
        """Inicia a fala do Baymax."""
        if self.speech_enabled:
            self.addToSpeechQueue("Estou pronto para ajudar!")  # Exemplo de fala inicial

    def stopSpeaking(self):
        """Para a fala do Baymax."""
        if hasattr(self, 'tts_engine'):
            self.tts_engine.stop()

    def sendMessage(self, e=None, texto=None):
        """Envia a mensagem do usuário (por texto ou voz) e exibe a resposta do Baymax."""
        if self.processing_message:
            print("Aguarde o processamento da mensagem anterior.")
            return

        self.processing_message = True
        self.message_input.disabled = True
        self.voice_button.disabled = True
        self.mic_button.disabled = True
        self.page.update()

        texto = texto or (self.message_input.value.strip() if e is not None else e)
        if not texto:
            self.processing_message = False
            self.message_input.disabled = False
            self.voice_button.disabled = False
            self.mic_button.disabled = False
            self.page.update()
            return

        if texto.lower() == "sair":
            self.page.go("/")
            self.processing_message = False
            return

        try:
            # Exibe a mensagem do usuário no chat
            user_bubble = ft.Container(
                content=ft.Text(f"Você: {texto}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_400,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(user_bubble)

            # Exibe mensagem temporária de "digitando" do Baymax
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

            # Obtém a resposta do modelo
            resposta_texto = None
            try:
                print(f"Texto enviado para o modelo: {texto}")
                response = self.chat.send_message(texto)
                resposta_texto = response.text if hasattr(response, 'text') else "Desculpe, não consegui entender."
                self.tempResponse = resposta_texto
                print(f"Resposta do modelo antes de ser salva: {resposta_texto}")
            except Exception as inner_error:
                print(f"Erro ao obter resposta do Baymax: {str(inner_error)}")
                resposta_texto = f"Erro ao processar sua mensagem: {str(inner_error)}"

            # Remove a mensagem "digitando" do Baymax
            if self.typing_message in self.chat_box.controls:
                self.chat_box.controls.remove(self.typing_message)

            # Exibe a resposta do Baymax no chat
            baymax_bubble = ft.Container(
                content=ft.Text(f"Baymax: {resposta_texto}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_left,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(baymax_bubble)

            if e is not None:
                self.message_input.value = ""
            self.page.update()

            if self.speech_enabled and self.tempResponse:
                self.speak(self.tempResponse)

            # Salvamento no banco de dados
            if self.user_id:
                conversa_data = {
                    'usuario_id': self.user_id,
                    'mensagem_usuario': str(texto),
                    'resposta_baymax': str(self.tempResponse)
                }
                try:
                    print("Tentando salvar conversa no banco de dados.")
                    self.db.salvarConversa(**conversa_data)
                    print("Conversa salva com sucesso.")
                except Exception as db_error:
                    print(f"Erro ao salvar conversa: {str(db_error)}")

            self.chat_box.scroll_to(self.chat_box.controls[-1])

            # Limite de mensagens no chat
            max_messages = 50
            if len(self.chat_box.controls) > max_messages:
                del self.chat_box.controls[:len(self.chat_box.controls) - max_messages]

        except Exception as e:
            print(f"Erro ao processar mensagem: {str(e)}")
            erro_texto = f"Ocorreu um erro inesperado: {str(e)}"
            baymax_bubble = ft.Container(
                content=ft.Text(f"Baymax: {erro_texto}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_left,
                margin=ft.margin.only(bottom=5),
                opacity=0
            )
            self.chat_box.controls.append(baymax_bubble)
            self.page.update()
        finally:
            self.processing_message = False
            self.message_input.disabled = False
            self.voice_button.disabled = False
            self.mic_button.disabled = False
            self.page.update()
            print("Processamento da mensagem finalizado.")

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
    page.bgcolor = ft.colors.WHITE  # Define o fundo padrão como branco (opcional)

    nicial = Inicial(page)

if __name__ == "__main__":
    ft.app(target=main)