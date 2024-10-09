import flet as ft
import google.generativeai as genai
import pyttsx3  # Biblioteca para transformar texto em fala
import threading
import time
import asyncio
import speech_recognition as sr
import os


class Inicial:
    def __init__(self, page):
        self.page = page
        self.model = self.initialize_model()
        self.chat = self.model.start_chat(history=[])
        self.recent_messages = []  # Inicializa a lista de mensagens recentes
        self.build_chat_view()  # Chama a construção da interface

        # Instância do TTS em nível de classe
        self.lock = threading.Lock()  # Adiciona um lock para a fala
        self.speech_enabled = False  # Inicialize a variável para controle da fala
        self.typing_message = None  # Para gerenciar a mensagem de "Baymax está digitando"
        self.tts_engine = pyttsx3.init()
        self.speech_enabled = True  # Variável para controlar se a fala está ativada
        if not self.set_voice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        self.page.on_route_change = self.route_change  # Define o callback de mudança de rota

        self.show_notification = True  # Variável de controle para mostrar a notificação

        self.loading_screen()  # Exibe a tela de carregamento

        self.conversation_history = []  # Lista para armazenar histórico de conversas

    def loading_screen(self):
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

        # Aguarda 5 segundos antes de carregar a página inicial
        threading.Thread(target=self.delay_loading).start()

    def delay_loading(self):
        """Aguarda um tempo antes de carregar a página inicial."""
        threading.Event().wait(2)  # Aguardando 2 segundos
        self.page.go("/")  # Carrega a página inicial

    def set_voice(self):
        """Configura uma voz masculina para o motor de texto para fala (TTS)."""
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower():  # Verifica se a voz é masculina
                self.tts_engine.setProperty('voice', voice.id)
                return True
        return False  # Retorna False se não encontrou uma voz masculina

    def initialize_model(self):
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

    def route_change(self, route_event_or_str):
        """Atualiza a view de acordo com a rota."""
        self.page.views.clear()  # Limpa as views atuais
        route = route_event_or_str.route if hasattr(route_event_or_str, 'route') else route_event_or_str
        views = {
            "/": self.build_home_view,
            "/chatIAFlet": self.build_chat_view,
            "/sobre": self.build_about_view,
            "/contato": self.build_contact_view,
        }
        view_function = views.get(route, self.build_error_view)
        view_function()  # Chama a função de view correspondente

        # Limpar o conteúdo do chat ao voltar para a página inicial
        if route == "/":
            self.clear_chat_content()  # Limpa o conteúdo do chat

        self.page.update()  # Atualiza a página

    def build_home_view(self):
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
                        on_change=self.handle_navigation,
                    ),
                    ft.Text("Bem-vindo ao Assistente Baymax!", size=24),
                ],
            )
        )
        self.page.update()  # Atualiza a página

        if self.show_notification:
            self.show_welcome_notification("Usuário")  # Exibe notificação de boas-vindas

    def show_welcome_notification(self, usuario):
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
                ft.Checkbox(label="Não mostrar novamente", on_change=self.no_show_again),
                ft.ElevatedButton("Fechar", on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Adiciona o diálogo ao overlay
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()  # Atualiza a página para mostrar o novo diálogo

    def close_dialog(self, e):
        """Fecha o diálogo de boas-vindas."""
        if hasattr(self, 'dialog'):
            self.dialog.open = False  # Fecha o diálogo
            self.page.overlay.remove(self.dialog)  # Remove o diálogo da sobreposição
            self.page.update()  # Atualiza a página para refletir a mudança

    def no_show_again(self, e):
        """Ação para o checkbox 'Não mostrar novamente'."""
        self.show_notification = not e.control.value  # Atualiza a variável com base no estado do checkbox

    def hide_notification(self):
        """Oculta completamente a notificação da tela."""
        # Aqui você pode adicionar a lógica para ocultar outros elementos da UI, se necessário
        self.show_notification = False  # Ou outra lógica para controlar a exibição

    def handle_navigation(self, e):
        """Navega entre as diferentes páginas do aplicativo."""
        if e.control.selected_index == 0:
            self.page.go("/chatIAFlet")  # Navega para a página de chat IA
        elif e.control.selected_index == 1:
            self.page.go("/sobre")  # Navega para a página 'Sobre Nós'
        elif e.control.selected_index == 2:
            self.page.go("/contato")  # Navega para a página de contato
        elif e.control.selected_index == 3:
            self.page.go("/")  # Retorna para a página principal

    def build_chat_view(self):
        """Constrói a interface do chat com balões de fala."""
        self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        self.message_input = ft.TextField(hint_text="Digite sua mensagem...", expand=True, on_submit=self.send_message)

        # Botão para ativar/desativar a fala
        self.voice_button = ft.ElevatedButton(
            "Desativar Voz", on_click=self.toggle_voice, bgcolor=ft.colors.RED, color=ft.colors.WHITE
        )

        # Botão para ativar reconhecimento de voz
        self.mic_button = ft.ElevatedButton("Falar", on_click=self.start_voice_recognition, bgcolor=ft.colors.BLUE,
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
                            ft.ElevatedButton("Enviar", on_click=self.send_message, bgcolor=ft.colors.RED,
                                              color=ft.colors.WHITE),
                            ft.ElevatedButton("Limpar Chat", on_click=self.clear_chat, bgcolor=ft.colors.RED,
                                              color=ft.colors.WHITE),
                            self.mic_button  # Botão de microfone
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    self.voice_button,
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def toggle_voice(self, e):
        """Ativa ou desativa a fala."""
        self.speech_enabled = not self.speech_enabled
        self.voice_button.text = "Ativar Voz" if not self.speech_enabled else "Desativar Voz"
        self.page.update()

    def start_voice_recognition(self, e):
        """Inicia o reconhecimento de voz em uma thread separada."""
        threading.Thread(target=self.recognize_speech).start()

    def recognize_speech(self):
        """Reconhece a fala e envia como mensagem."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Ajustando o nível de ruído... Por favor, fale agora.")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                texto = recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {texto}")
                self.message_input.value = texto
                self.send_message(None)  # Chama o método de envio de mensagem
            except sr.UnknownValueError:
                print("Não consegui entender o que você disse.")
            except sr.RequestError as e:
                print(f"Erro no serviço de reconhecimento de fala: {e}")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

    def send_message(self, e):
        texto = self.message_input.value.strip()
        if texto.lower() == "sair":
            self.page.go("/")
            return

        if not texto:
            return

        if getattr(self, 'processing_message', False):
            return

        self.processing_message = True

        # Limpa a mensagem de "digitando" se estiver presente
        if self.typing_message:
            self.chat_box.controls.remove(self.typing_message)
            self.typing_message = None

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

            # Adiciona a mensagem de "Baymax está digitando"
            self.typing_message = ft.Container(
                content=ft.Text("Baymax está digitando...", size=16, color=ft.colors.YELLOW),
                bgcolor=ft.colors.GREY,
                padding=10,
                border_radius=10,
                alignment=ft.alignment.center_left,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(self.typing_message)
            self.page.update()  # Atualiza a interface para mostrar a mensagem "digitando"

            threading.Thread(target=self.handle_send_message, args=(texto,)).start()  # Envia em uma nova thread

        except Exception as e:
            error_bubble = ft.Container(
                content=ft.Text(f"Erro: {str(e)}", size=16, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_800,
                padding=10,
                border_radius=10,
                margin=ft.margin.only(bottom=5)
            )
            self.chat_box.controls.append(error_bubble)
            self.page.update()
        finally:
            self.processing_message = False

    def handle_send_message(self, texto):
        """Processa o envio da mensagem em uma nova thread."""
        response = self.chat.send_message(texto)

        # Adiciona a interação ao histórico
        self.conversation_history.append({"user": texto, "baymax": response.text})

        # Verifica se a resposta é válida
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

        # Adicione um print para depuração
        print(f"Baymax vai falar: {resposta_texto}")

        # Interrompe a fala anterior e fala a nova mensagem
        if self.speech_enabled:
            self.speak(resposta_texto)

        # Atraso para garantir que a interface seja atualizada antes do scroll
        threading.Timer(0.1, lambda: self.chat_box.scroll_to(self.chat_box.controls[-1])).start()

    def speak(self, text):
        """Faz o Baymax falar o texto fornecido."""
        try:
            if self.speech_enabled:
                with self.lock:  # Garante que só uma chamada possa executar a fala
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    print(f"Baymax falou: {text}")
        except Exception as e:
            print(f"Erro ao falar: {str(e)}")

    def clear_chat_content(self):
        """Limpa o conteúdo do chat."""
        if hasattr(self, 'chat_box'):
            self.chat_box.controls.clear()
            self.page.update()
        else:
            print("chat_box não foi inicializado.")

    def clear_chat(self, e):
        """Limpa o histórico de chat."""
        self.chat_box.controls.clear()
        self.page.update()

    def build_about_view(self):
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

    def build_contact_view(self):
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

    def build_back_button(self):
        """Cria o botão de voltar para a página inicial."""
        return ft.ElevatedButton(
            "Voltar",
            on_click=lambda e: self.page.go("/"),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
        )

    def build_error_view(self):
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
    page.window.width = 800  # Largura da janela
    page.window.height = 800  # Altura da janela
    page.bgcolor = ft.colors.WHITE  # Cor de fundo

    inicial = Inicial(page)  # Instancia a classe Inicial


if __name__ == "__main__":
    ft.app(target=main)
