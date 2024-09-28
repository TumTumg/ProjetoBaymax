import flet as ft
import google.generativeai as genai
import pyttsx3  # Importa a biblioteca de texto para fala
import threading


class Inicial:
    def __init__(self, page):
        self.page = page
        self.model = self.initialize_model()  # Inicializa o modelo aqui
        self.chat = self.model.start_chat(history=[])  # Inicializa o chat com o histórico vazio

        self.tts_engine = pyttsx3.init()  # Inicializa o motor de TTS
        if not self.set_voice():  # Configura a voz masculina e verifica se foi bem-sucedido
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")
        self.page.on_route_change = self.route_change  # Define a função de mudança de rota
        self.build_home_view()  # Constrói a view inicial

    def set_voice(self):
        """Configura a voz masculina para o motor de TTS."""
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower():  # Procura uma voz masculina
                self.tts_engine.setProperty('voice', voice.id)
                return True  # Retorna True se uma voz masculina foi encontrada
        return False  # Retorna False se nenhuma voz masculina foi encontrada

    def initialize_model(self):
        # Configuração da API do Gemini
        genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real

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
            system_instruction="..."  # Insira a string correta aqui
        )

        return model

    def route_change(self, route_event_or_str):
        self.page.views.clear()  # Limpa as views atuais

        # Verifica se o argumento é uma string (rota direta) ou um evento de mudança de rota
        route = route_event_or_str.route if hasattr(route_event_or_str, 'route') else route_event_or_str

        # Mapeamento das rotas
        views = {
            "/": self.build_home_view,
            "/chatIAFlet": self.build_chat_view,
            "/sobre": self.build_about_view,
            "/contato": self.build_contact_view,
        }

        view_function = views.get(route, self.build_error_view)  # Usa a rota obtida
        view_function()  # Chama a função de visualização correspondente
        self.page.update()  # Atualiza a página

    def build_home_view(self):
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
                        on_change=self.handle_navigation,
                    ),
                    ft.Text("Bem-vindo ao Assistente Baymax!", size=24),  # Componente inicial
                ],
            )
        )
        self.page.update()  # Atualiza a página após adicionar a view

        # Exibe a notificação de boas-vindas
        self.show_welcome_notification("Usuário")  # Substitua "Usuário" pelo nome do usuário real

    def show_welcome_notification(self, usuario):
        """Exibe uma notificação de boas-vindas ao usuário."""
        notification_text = (
            f"Bem Vindo {usuario}!\n"
            "---Novidades!---\n"
            "- Apresentamos o chat IA\n"
            "- Novas Funcionalidades!\n"
            "- Correção de bugs\n"
            "- Suporte ao usuário\n"
            "- Promoção à saúde\n"
            "- Biblioteca Senac\n"
            "- Auxílio em eventos\n"
            "-----//-----\n"
            "Por quê você mesmo não dá uma olhada?"
        )

        self.page.snackbar = ft.Snackbar(
            content=ft.Text(notification_text),
            action="Explorar",
            on_action=self.explore  # Ação ao clicar no botão
        )
        self.page.snackbar.open = True  # Abre o Snackbar
        self.page.update()

    def explore(self, e):
        """Função chamada quando o usuário clica em 'Explorar'."""
        print("Explorar clicado!")  # Aqui você pode adicionar a lógica para direcionar o usuário à seção desejada

    def handle_navigation(self, e):
        # Manipula a navegação entre as diferentes views
        if e.control.selected_index == 0:  # Chat IA
            self.page.route = "/chatIAFlet"
        elif e.control.selected_index == 1:  # Sobre Nós
            self.page.route = "/sobre"
        elif e.control.selected_index == 2:  # Contato
            self.page.route = "/contato"
        else:  # Sair
            self.page.close()

        self.route_change(self.page.route)  # Atualiza a rota após a seleção

    def build_chat_view(self):
        # Layout de chat com uma caixa de entrada de mensagens e o histórico de conversas
        self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        self.message_input = ft.TextField(hint_text="Digite sua mensagem...", expand=True, on_submit=self.send_message)

        self.page.views.append(
            ft.View(
                "/chatIAFlet",
                [
                    ft.AppBar(title=ft.Text("Chat IA"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Container(self.chat_box, expand=True, padding=10),
                    ft.Row(
                        controls=[
                            self.message_input,
                            ft.ElevatedButton("Enviar", on_click=self.send_message, bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                            ft.ElevatedButton("Limpar Chat", on_click=self.clear_chat, bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    # Adiciona o botão de voltar na mesma linha
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def send_message(self, e):
        texto = self.message_input.value.strip()
        if texto.lower() == "sair":
            self.page.go("/")  # Volta para a página principal
            return

        if not texto:
            return

        if getattr(self, 'processing_message', False):  # Verifica se já está processando uma mensagem
            return

        self.processing_message = True  # Define que está processando uma mensagem

        try:
            # Adiciona a mensagem do usuário
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLUE_800),
                    ],
                    alignment=ft.MainAxisAlignment.END  # Alinha a mensagem à direita
                )
            )

            # Envia a mensagem e recebe a resposta
            response = self.chat.send_message(texto)

            # Exibe a resposta na interface
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Baymax: {response.text}", size=16, color=ft.colors.RED),
                    ],
                    alignment=ft.MainAxisAlignment.START  # Alinha a resposta à esquerda
                )
            )

            # Limpa o campo de entrada
            self.message_input.value = ""

            # Atualiza a página para mostrar as mensagens
            self.page.update()

            # Faz o Baymax "falar" a resposta após um breve atraso usando threading
            threading.Timer(0.1, self.speak, args=[response.text]).start()  # Espera 0.1 segundos antes de falar

            # Rolagem para a última mensagem
            self.chat_box.scroll_to(self.chat_box.controls[-1])
        except Exception as e:
            # Adiciona um erro à caixa de chat se algo falhar
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Erro: {str(e)}", size=16, color=ft.colors.RED),
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            )
            self.page.update()
        finally:
            self.processing_message = False  # Libera a flag de processamento

    def speak(self, text):
        """Transforma texto em fala."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Erro ao falar: {str(e)}")  # Registra qualquer erro no TTS

    def clear_chat(self, e):
        """Limpa o histórico de chat."""
        self.chat_box.controls.clear()  # Limpa os controles de chat
        self.page.update()  # Atualiza a página

    def build_about_view(self):
        # Visualização da página "Sobre"
        self.page.views.append(
            ft.View(
                "/sobre",
                [
                    ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Esta é a página sobre o assistente Baymax.", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def build_contact_view(self):
        # Visualização da página "Contato"
        self.page.views.append(
            ft.View(
                "/contato",
                [
                    ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Esta é a página de contato.", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def build_back_button(self):
        """Constrói um botão de voltar."""
        return ft.ElevatedButton("Voltar", on_click=lambda e: self.page.go("/"))

    def build_error_view(self):
        """Exibe uma página de erro."""
        self.page.views.append(
            ft.View(
                "/error",
                [
                    ft.AppBar(title=ft.Text("Erro"), bgcolor=ft.colors.RED),
                    ft.Text("Erro: Página não encontrada.", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()


def main(page: ft.Page):
    # Inicializa o assistente Baymax
    page.title = "Assistente Baymax"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 600
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.WHITE
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    }
    app = Inicial(page)  # Instancia o assistente
    page.go("/")  # Inicia na página inicial


ft.app(target=main)
