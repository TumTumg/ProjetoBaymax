import flet as ft
from flet import Page


def main(page: Page):
    # Definições iniciais para chat_box, message_input e send_button
    chat_box = ft.Column()  # Caixa de chat como uma coluna
    message_input = ft.TextField(label="Digite sua mensagem aqui", width=300)  # Campo de entrada para mensagens
    send_button = ft.ElevatedButton("Enviar", on_click=lambda _: send_message())  # Botão para enviar mensagens

    def send_message():
        if message_input.value:
            chat_box.controls.append(ft.Text(f"Você: {message_input.value}"))  # Adiciona a mensagem à caixa de chat
            message_input.value = ""  # Limpa o campo de entrada
            page.update()  # Atualiza a página

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
                        chat_box,
                        message_input,
                        send_button,
                        ft.ElevatedButton("Voltar para Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        elif page.route == "/sobre":
            page.views.append(
                ft.View(
                    "/sobre",
                    [
                        ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Voltar para Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        elif page.route == "/contato":
            page.views.append(
                ft.View(
                    "/contato",
                    [
                        ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Voltar para Home", on_click=lambda _: page.go("/")),
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
