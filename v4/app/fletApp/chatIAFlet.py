import flet as ft
import google.generativeai as genai
from styles import button_style  # Importando os estilos

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

    message_input = ft.TextField(hint_text="Escreva sua mensagem...", width=300)

    def send_message(e):
        texto = message_input.value.strip()
        if texto.lower() == "sair":
            page.go("/")  # Volta para a página principal
            return

        if not texto:  # Verifica se a mensagem não está vazia
            return

        try:
            # Adiciona a mensagem do usuário ao chat
            chat_box.controls.append(ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLUE_800))

            # Envia a mensagem ao modelo e obtém a resposta
            response = chat.send_message(texto)
            chat_box.controls.append(ft.Text(f"Baymax: {response.text}", size=16, color=ft.colors.RED))
            message_input.value = ""  # Limpa o campo de entrada
            page.update()  # Atualiza a página para mostrar a nova mensagem

            # Rola para a última mensagem
            chat_box.scroll_to(chat_box.controls[-1])  # Rola para a última mensagem
        except Exception as e:
            chat_box.controls.append(ft.Text(f"Erro: {e}", color=ft.colors.RED_600))
            page.update()  # Atualiza a página para mostrar a mensagem de erro

    # Permite o envio da mensagem com a tecla Enter
    message_input.on_submit = send_message

    # Botão de enviar
    send_button = ft.ElevatedButton("Enviar", on_click=send_message, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE)

    # Criação do contêiner para o chat
    chat_container = ft.Container(
        content=chat_box,
        bgcolor=ft.colors.WHITE,
        padding=20,
        border_radius=10,
        height=500,
        width=400,
        alignment=ft.alignment.top_left,
        border=ft.border.all(1, ft.colors.GREY_300)
    )

    # Layout da página
    page.add(
        ft.Row(
            [
                chat_container,  # Retângulo do lado direito
                ft.Column(
                    controls=[
                        message_input,
                        send_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )
    )

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Seu Assistente Baymax"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ElevatedButton("Chat IA", on_click=lambda _: page.go("/chatIAFlet.py")),
                    ft.ElevatedButton("Sobre Nós", on_click=lambda _: page.go("/sobre")),
                    ft.ElevatedButton("Contato", on_click=lambda _: page.go("/contato")),
                    ft.ElevatedButton("Sair", on_click=lambda e: page.window_close()),
                ],
            )
        )
        if page.route == "/chatIAFlet.py":
            page.views.append(
                ft.View(
                    "/chatIAFlet.py",
                    [
                        ft.AppBar(title=ft.Text("Chat IA"), bgcolor=ft.colors.SURFACE_VARIANT),
                        chat_container,  # Retângulo do lado direito
                        ft.Row(
                            controls=[
                                message_input,
                                send_button,
                            ],
                        ),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        elif page.route == "/sobre":
            page.views.append(
                ft.View(
                    "/sobre",
                    [
                        ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        elif page.route == "/contato":
            page.views.append(
                ft.View(
                    "/contato",
                    [
                        ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    # Atualiza a página ao iniciar
    page.update()

# Chamada da função main para iniciar a aplicação
if __name__ == "__main__":
    ft.app(target=main)
