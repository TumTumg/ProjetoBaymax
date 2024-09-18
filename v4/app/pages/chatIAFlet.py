import flet as ft
import google.generativeai as genai
from styles import button_style  # Importando os estilos

class Chat:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()  # Configura a página e o chat

    def setup_page(self):
        try:
            self.page.title = "Baymax - Assistente Virtual"
            self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

            # Configuração da API do Gemini
            genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real

            # Configuração do modelo
            self.generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=self.generation_config,
                system_instruction="...",
            )

            self.chat = self.model.start_chat(history=[])
            self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
            self.message_input = ft.TextField(hint_text="Escreva sua mensagem...", expand=True)

            self.create_interface()  # Cria a interface do chat

        except Exception as e:
            self.page.add(ft.Text(f"Erro ao inicializar a aplicação: {str(e)}", color=ft.colors.RED_600))
            self.page.update()

    def create_interface(self):
        self.message_input.on_submit = self.send_message  # Envia mensagem ao pressionar Enter
        send_button = ft.ElevatedButton("Enviar", on_click=self.send_message, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE)
        back_button = ft.ElevatedButton("Voltar à Página Inicial", on_click=lambda _: self.page.go("/aplicacaoFlet"),
                                        bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE)
        clear_button = ft.ElevatedButton("Limpar Chat", on_click=lambda _: self.clear_chat(), bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)

        chat_container = ft.Container(
            content=self.chat_box,
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True,
            alignment=ft.alignment.top_left,
            border=ft.border.all(1, ft.colors.GREY_300)
        )

        self.page.add(
            ft.Column(
                [
                    chat_container,  # Retângulo do chat
                    ft.Row(
                        [
                            self.message_input,
                            send_button,
                            clear_button,
                            back_button
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    )
                ],
                expand=True,
                spacing=10
            )
        )

        self.page.update()  # Atualiza a página após adicionar os componentes

    def send_message(self, e):
        texto = self.message_input.value.strip()
        if texto.lower() == "sair":
            self.page.go("/")  # Volta para a página principal
            return

        if not texto:
            return

        try:
            # Adiciona a mensagem do usuário
            self.chat_box.controls.append(ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLUE_800))
            # Envia a mensagem e recebe a resposta
            response = self.chat.send_message(texto)
            self.chat_box.controls.append(ft.Text(f"Baymax: {response.text}", size=16, color=ft.colors.RED))
            self.message_input.value = ""  # Limpa o campo de entrada
            self.page.update()
            self.chat_box.scroll_to(self.chat_box.controls[-1])  # Rolagem para a última mensagem
        except Exception as e:
            # Adiciona um erro à caixa de chat se algo falhar
            self.chat_box.controls.append(ft.Text(f"Erro: {str(e)}", color=ft.colors.RED_600))
            self.page.update()

    def clear_chat(self):
        self.chat_box.controls.clear()  # Limpa o chat
        self.page.update()

# Chamada da função main para iniciar a aplicação
def main(page: ft.Page):
    Chat(page)  # Cria uma instância da classe Chat

if __name__ == "__main__":
    ft.app(target=main)
