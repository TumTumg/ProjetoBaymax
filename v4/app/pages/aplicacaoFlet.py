import tensorflow as tf
import numpy as np
from sklearn.preprocessing import LabelEncoder
import flet as ft
import google.generativeai as genai
import pyttsx3
import threading
import os
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error
from keras import Sequential
from tensorflow.keras.models import Sequential
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.layers import Input, Dense


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

    def _checkConnection(self):
        """Verifica se a conexão com o banco de dados está ativa."""
        if self.connection is None or not self.connection.is_connected():
            self.createConnection()

    def createUser(self, email, cpf, nomeCompleto, telefone, senha):
        """Insere um novo usuário no banco de dados."""
        self._checkConnection()
        try:
            with self.connection.cursor() as cursor:
                comando = 'INSERT INTO usuario (email, cpf, nomeCompleto, telefone, senha) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(comando, (email, cpf, nomeCompleto, telefone, senha))
                self.connection.commit()
                print(f"Usuário '{nomeCompleto}' criado com sucesso.")
        except Error as e:
            print(f"Erro ao criar usuário: {e}")

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
        self._checkConnection()
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
        self._checkConnection()
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

    def salvarConversa(self, idUsuario, mensagemUsuario, respostaBaymax):
        """Salva a conversa no banco de dados."""
        self._checkConnection()
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO conversa (idUsuario, mensagemUsuario, respostaBaymax)
                VALUES (%s, %s, %s)
            """
            valores = (idUsuario, mensagemUsuario, respostaBaymax)
            cursor.execute(query, valores)
            self.connection.commit()  # Confirma a transação
            print("Conversa salva no banco de dados com sucesso!")
        except Error as e:
            print(f"Erro ao salvar conversa no banco de dados: {e}")
        finally:
            cursor.close()


class NeuralNetwork:
    def __init__(self):
        self.models = {}  # Armazena modelos para cada usuário
        self.encoder = LabelEncoder()  # Codifica labels de saída
        self.conversation_data = {}  # Armazena pares de entrada/saída por ID de usuário
        self.vectorizer = TfidfVectorizer()  # Para codificação de mensagens
        self.message_pool = []  # Para armazenar mensagens

    def createModel(self, user_id):
        model = Sequential()
        model.add(Input(shape=(128,)))  # Mantenha a forma de entrada
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))  # Use sigmoid para saída binária

        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def encode_message(self, message):
        """Codifica a mensagem usando o vectorizer, se já estiver ajustado."""
        if len(self.message_pool) < 30:  # Use o mesmo número mínimo
            raise ValueError("O vectorizer não foi ajustado porque há menos de 30 mensagens.")
        return self.vectorizer.transform([message]).toarray()

    def learn(self, user_id, user_message, response):
        """Adiciona um par de mensagem-resposta aos dados de conversação e treina o modelo do usuário."""
        if user_id not in self.conversation_data:
            self.conversation_data[user_id] = []  # Inicializa a lista para o novo usuário

        self.conversation_data[user_id].append((user_message, response))

        # Atualiza o pool de mensagens e ajusta o vectorizer se necessário
        self.message_pool.append(user_message)  # Adiciona a mensagem ao pool

        # Verifica se o número de mensagens é suficiente
        if len(self.message_pool) >= 30:  # Ajustado para 30 mensagens
            self.vectorizer.fit(self.message_pool)  # Ajusta o vectorizer
        else:
            print(f"Aguardando mais mensagens para ajustar o vectorizer. Mensagens atuais: {len(self.message_pool)}")

        # Codifica a mensagem, se o vectorizer foi ajustado
        if len(self.message_pool) >= 30:
            X = np.array([self.encode_message(user_message)])  # Codifica a mensagem
            y = np.array([1 if response.lower() == "útil" else 0])  # Usa 'útil' como rótulo

            # Treina o modelo para o usuário específico
            self.trainModel(user_id, X, y)

    def trainModel(self, user_id, X, y):
        print(f"Forma de X antes do treinamento: {X.shape}")
        print(f"Forma de y antes do treinamento: {y.shape}")

        if X.shape[1] != 128:
            raise ValueError("A dimensão de entrada não é a esperada.")

        model = self.createModel(user_id)  # Criando o modelo para o usuário
        model.fit(X, y, epochs=10, batch_size=32)  # Ajuste conforme necessário
        self.models[user_id] = model  # Armazena o modelo após o treinamento

    def fitVectorizer(self, training_data):
        """Ajusta o vectorizer com dados de treinamento."""
        self.vectorizer.fit(training_data)

    def processData(self, texto, resposta_texto):
        X = self.vectorizer.transform([texto]).toarray()  # Garante que seja uma matriz 2D
        y = np.array([1 if resposta_texto.lower() == "útil" else 0])  # Mapear resposta

        # Asegure-se de que `X` tenha o formato correto
        print("Forma de X antes do treinamento:", X.shape)
        print("Forma de y antes do treinamento:", y.shape)

        # Verifica se `y` precisa ser transformado
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)  # Transforma em uma matriz 2D

        # Verifica a forma de X e y
        if X.shape[0] != y.shape[0]:
            raise ValueError("X e y devem ter o mesmo número de amostras.")

        # Define expected_input_dim como 128 para compatibilidade
        expected_input_dim = 128
        if X.shape[1] != expected_input_dim:
            raise ValueError("A dimensão de entrada não é a esperada.")

        return X, y

    def predict(self, user_id, input_message):
        """Faz uma previsão com base na entrada do usuário usando o modelo."""
        if user_id not in self.models:
            raise ValueError("Modelo não encontrado para o usuário.")

        model = self.models[user_id]
        X = self.encode_message(input_message)  # Codifica a mensagem
        prediction = model.predict(X)

        return "útil" if prediction[0][0] >= 0.5 else "não útil"

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
        self.speech_queue = []  # Fila de fala
        self.neuralNetwork = NeuralNetwork()  # Inicializando a rede neural
        self.db = Database(user='root', password='')  # Conexão com o banco de dados
        self.db.createConnection()  # Tenta estabelecer a conexão
        self.user_id = None  # ID do usuário atual, precisa ser definido após login

        if not self.setVoice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        self.page.on_route_change = self.routeChange
        self.loadingScreen()
        self.conversation_history = []

    def close(self):
        """Fecha a conexão com o banco de dados ao encerrar a aplicação."""
        self.db.closeConnection()

    def save_conversation(self, user_id, user_message, response):
        """Salva a conversa e atualiza o modelo."""
        self.db.salvarConversa(user_id, user_message, response)  # Salva no banco
        self.neuralNetwork.learn(user_id, user_message, response)  # Atualiza o modelo
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
        try:
            genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real
        except Exception as e:
            print(f"Erro ao configurar a API do Gemini: {e}")
            return None  # Retorna None se a configuração falhar

        # Lendo o arquivo .txt com a configuração do system_instruction
        try:
            with open("system_instruction.txt", "r", encoding="utf-8") as file:
                system_instruction = file.read().strip()
        except FileNotFoundError:
            system_instruction = "default_instruction"  # Instrução padrão caso o arquivo não seja encontrado
            print("Arquivo 'system_instruction.txt' não encontrado. Usando instrução padrão.")
        except UnicodeDecodeError as e:
            print(f"Erro ao ler o arquivo: {e}")
            system_instruction = "default_instruction"  # Instrução padrão em caso de erro

        # Configuração do modelo
        try:
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
        except Exception as e:
            print(f"Erro ao inicializar o modelo: {e}")
            return None

    def initializeNeuralNetworkModel():
        """Inicializa a rede neural para aprendizado contínuo."""
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

        model = Sequential()
        model.add(Input(shape=(128,)))  # Ajuste o tamanho da entrada conforme o seu problema
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='linear'))  # Ajuste conforme o tipo de saída (regressão ou classificação)

        # Compilar o modelo
        model.compile(optimizer='adam', loss='mean_squared_error',
                      metrics=['mae'])  # Use Mean Absolute Error para melhor interpretação
        return model

    def fetchTrainingData(self):
        """Busca os dados de treinamento do banco de dados."""
        query = "SELECT * FROM usuario"  # Ajuste a consulta conforme necessário

        try:
            cursor = self.db.connection.cursor()  # Use a conexão do banco de dados
            cursor.execute(query)
            result = cursor.fetchall()

            # Processar os dados para treinar a rede neural
            data = []
            labels = []
            for row in result:
                # Supondo que row[1] seja a característica e row[2] o rótulo
                data.append([row[1]])  # Substitua por suas características
                labels.append(row[2])  # Substitua pelo rótulo correspondente

            return np.array(data), np.array(labels)  # Retorna como arrays NumPy
        except mysql.connector.Error as e:
            print(f"Erro ao buscar dados do banco: {e}")
            return None, None  # Retorna None se houver erro

    def trainNeuralNetwork(self, data, labels):
        """Treina a rede neural com os dados fornecidos."""
        if data is None or labels is None:
            print("Dados ou rótulos inválidos. O treinamento não pode prosseguir.")
            return None

        model = self.initializeNeuralNetworkModel()
        if model is None:
            print("Modelo de rede neural não foi inicializado.")
            return None

        # Treine a rede neural
        try:
            model.fit(data, labels, epochs=10, batch_size=32)  # Ajuste os parâmetros conforme necessário
            print("Rede neural treinada com sucesso.")
            return model  # Retorne o modelo treinado
        except Exception as e:
            print(f"Erro ao treinar a rede neural: {e}")
            return None

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



    def prepareInputData(self, message):
        """Transforma a mensagem do usuário em dados numéricos para o treinamento."""
        # Esta função precisa ser personalizada conforme a natureza dos dados
        return np.random.rand(10)  # Exemplo de vetor com 10 features

    def prepareOutputData(self, message):
        """Transforma a resposta do Baymax em dados numéricos para o treinamento."""
        # Esta função precisa ser personalizada conforme a natureza dos dados
        return np.random.randint(2)  # Exemplo de saída binária (0 ou 1)
    def toggleVoice(self, e):
        """Ativa ou desativa a fala."""
        self.speech_enabled = not self.speech_enabled
        self.voice_button.text = "Ativar Voz" if not self.speech_enabled else "Desativar Voz"
        self.page.update()

    def startVoiceRecognition(self, e):
        """Inicia o reconhecimento de voz em uma thread separada."""
        threading.Thread(target=self.recognizeSpeech).start()

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
            user_bubble = ft.Container(
                content=ft.Text(f"Você: {texto}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.GREEN_400,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(user_bubble)

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

            threading.Thread(target=self.handleSendMessage, args=(texto,)).start()

        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            self.processing_message = False

    def handleSendMessage(self, texto):
        """Processa o envio da mensagem em uma nova thread."""
        if not texto.strip():
            print("Mensagem vazia, não enviando.")
            return

        print(f"handleSendMessage chamado com texto: '{texto}'")  # Debug: Contagem de chamadas

        # Verifica se a função está sendo chamada múltiplas vezes
        if hasattr(self, 'sending_message') and self.sending_message:
            print("Mensagem já em envio, evitando duplicação.")
            return

        # Marca que uma mensagem está sendo enviada
        self.sending_message = True

        # Envia a mensagem e obtém a resposta
        print(f"Enviando mensagem: {texto}")  # Debug: Mensagem do usuário
        response = self.chat.send_message(texto)

        # Verifica se a resposta foi recebida
        if hasattr(response, 'text'):
            resposta_texto = response.text
            print(f"Resposta do Baymax: {resposta_texto}")  # Debug: Resposta do Baymax
        else:
            resposta_texto = "Desculpe, não consegui entender."

        # Salva a conversa no banco de dados
        usuario_id = self.user_id if self.user_id else 1  # Usa o ID do usuário atual ou 1
        self.db.salvarConversa(usuario_id, texto, resposta_texto)

        # Adiciona a nova mensagem do usuário ao chat
        user_bubble = ft.Container(
            content=ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLACK),
            bgcolor=ft.colors.LIGHT_GREEN,
            padding=10,
            border_radius=10,
            alignment=ft.alignment.center_right,
            margin=ft.margin.only(bottom=5)
        )

        # Adiciona a mensagem do usuário ao chat
        self.chat_box.controls.append(user_bubble)
        print("Mensagem do usuário adicionada ao chat.")  # Debug: Confirmação da mensagem do usuário

        # Remover a mensagem "Baymax está digitando..." se existir
        if hasattr(self, 'typing_message'):
            self.chat_box.controls.remove(self.typing_message)
            print("Mensagem 'Baymax está digitando...' removida.")  # Debug: Confirmação da remoção

        # Adiciona a nova mensagem do Baymax ao chat
        baymax_bubble = ft.Container(
            content=ft.Text(f"Baymax: {resposta_texto}", size=16, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED,
            padding=10,
            border_radius=10,
            alignment=ft.alignment.center_left,
            margin=ft.margin.only(bottom=5)
        )

        # Adiciona a mensagem do Baymax ao chat
        self.chat_box.controls.append(baymax_bubble)
        print("Mensagem do Baymax adicionada ao chat.")  # Debug: Confirmação da mensagem do Baymax

        # Limpa o campo de entrada
        self.message_input.value = ""

        # Atualiza a página para refletir as novas mensagens
        self.page.update()

        # Faz o Baymax falar a resposta
        self.speak(resposta_texto)  # Chama o método para fazer o Baymax falar

        # Marca que o envio foi concluído
        self.sending_message = False

    def salvarFeedback(self, idConversa, avaliacao):
        """Salva o feedback no banco de dados."""
        try:
            cursor = self.connection.cursor()
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
        finally:
            cursor.close()

    def speak(self, text):
        """Faz o Baymax falar o texto fornecido."""
        if self.speech_enabled:
            try:
                with self.lock:  # Garante acesso seguro a threads
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    print(f"Baymax falou: {text}")
            except Exception as e:
                print(f"Erro ao falar: {str(e)}")
        else:
            print("Voz desativada, não falando.")

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

