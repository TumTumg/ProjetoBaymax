import flet as ft
import google.generativeai as genai
from styles import button_style, page_style  # Importando os estilos

def main(page: ft.Page):
    # Configuração da API do Gemini
    genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")

    # Configuração do modelo
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="...",
    )

    chat = model.start_chat(history=[])

    # Criação da interface de chat com rolagem
    chat_box = ft.Column(
        scroll="auto",  # Permite rolagem automática
        alignment=ft.MainAxisAlignment.START,  # Alinhamento das mensagens
        spacing=10  # Espaçamento entre as mensagens
    )

    message_input = ft.TextField(hint_text="Escreva sua mensagem...", expand=True)  # Expande para ocupar espaço

    def send_message(e):
        texto = message_input.value
        if texto.lower() == "sair":
            page.go("/")  # Volta para a página principal
            return

        try:
            # Adiciona a mensagem do usuário ao chat
            chat_box.controls.append(ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLUE_800))

            # Envia a mensagem ao modelo e obtém a resposta
            response = chat.send_message(texto)
            chat_box.controls.append(ft.Text(f"Baymax: {response.text}", size=16, color=ft.colors.GREEN_800))
            message_input.value = ""  # Limpa o campo de entrada
            page.update()  # Atualiza a página para mostrar a nova mensagem

            # Rola para a última mensagem
            chat_box.scroll_to(chat_box.controls[-1])  # Rola para a última mensagem
        except Exception as e:
            chat_box.controls.append(ft.Text(f"Erro: {e}", color=ft.colors.RED_600))

    # Permite o envio da mensagem com a tecla Enter
    message_input.on_submit = send_message

    # Botão de enviar
    send_button = ft.ElevatedButton("Enviar", on_click=send_message)

    # Criação da barra de navegação
    def navigate(e, path):
        page.go(path)

    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Home", on_click=lambda e: navigate(e, "/home"), style=button_style()),
            ft.ElevatedButton("Chat IA", on_click=lambda e: navigate(e, "/chatIAFlet.py"), style=button_style()),
            ft.ElevatedButton("Sobre Nós", on_click=lambda e: navigate(e, "/sobre"), style=button_style()),
            ft.ElevatedButton("Contato", on_click=lambda e: navigate(e, "/contato"), style=button_style()),
            ft.ElevatedButton("Sair", on_click=lambda e: page.window_close(), style=button_style()),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY  # Alinhamento dos botões
    )

    # Envolvendo a barra de navegação em um Container para aplicar o estilo
    nav_container = ft.Container(
        content=nav_bar,
        bgcolor=ft.colors.GREY_50,  # Alterado para um branco mais escuro
        padding=ft.Padding(top=10, right=10, bottom=10, left=10),
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=0, bottom_right=0)  # Bordas arredondadas na parte superior
    )

    # Criação do contêiner do chat
    chat_container = ft.Container(
        content=ft.Column(
            controls=[
                chat_box,
                ft.Row(controls=[message_input, send_button], alignment=ft.MainAxisAlignment.CENTER),  # Centraliza a barra de mensagem
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        ),
        bgcolor=ft.colors.WHITE,  # Fundo branco para o chat
        padding=ft.Padding(10, 10, 10, 10),  # Padding correto
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),  # Bordas arredondadas
        width=page.width - 40,  # Largura quase total da página
        height=page.height - 100,  # Altura da página, ajuste conforme necessário
        border=ft.border.all(1, ft.colors.GREY_400)  # Borda cinza clara
    )

    # Adiciona a barra de navegação e o contêiner de chat à página
    page.add(nav_container)
    page.add(chat_container)

    # Atualiza a página ao iniciar
    page.update()

# Configuração do aplicativo
ft.app(target=main)
