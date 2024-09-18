import flet as ft
from flet import Page
from chatIAFlet import main as chat_main  # Importa a função main do chatIAFlet


class Inicial:
    def __init__(self, page: Page):
        self.page = page
        self.page.on_route_change = self.route_change
        self.page.go("/")  # Carrega a view inicial

    def route_change(self, route):
        self.page.views.clear()  # Limpa as views atuais

        # Mapeamento das rotas
        views = {
            "/": self.build_home_view,
            "/chatIAFlet": self.load_chat,  # Alterado para uma rota sem .py
            "/sobre": self.build_about_view,
            "/contato": self.build_contact_view,
        }

        view_function = views.get(self.page.route, self.build_error_view)
        view_function()

        self.page.update()

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
                ],
            )
        )

    def load_chat(self):
        try:
            chat_main(self.page)  # Tenta chamar a função main do arquivo chatIAFlet.py
        except Exception as e:
            self.build_error_view(str(e))

    def build_about_view(self):
        self.page.views.append(
            ft.View(
                "/sobre",
                [
                    ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ElevatedButton("Voltar para Home", on_click=lambda _: self.page.go("/")),
                ],
            )
        )

    def build_contact_view(self):
        self.page.views.append(
            ft.View(
                "/contato",
                [
                    ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                    # Adicione campos de entrada aqui se necessário
                    ft.ElevatedButton("Voltar para Home", on_click=lambda _: self.page.go("/")),
                ],
            )
        )

    def build_error_view(self, error_message="Ocorreu um erro"):
        self.page.views.append(
            ft.View(
                "/erro",
                [
                    ft.AppBar(title=ft.Text("Erro ao Carregar"), bgcolor=ft.colors.RED_600),
                    ft.Text(f"Ocorreu um erro: {error_message}", color=ft.colors.RED_800),
                    ft.ElevatedButton("Voltar para Home", on_click=lambda _: self.page.go("/")),
                ],
            )
        )

    def handle_navigation(self, e):
        """Função para lidar com a navegação ao clicar em um item da nav bar."""
        destinations = ["/chatIAFlet", "/sobre", "/contato", None]
        route = destinations[e.control.selected_index]

        if route:
            self.page.go(route)
        else:
            self.page.window_close()


# Chamada da função main para iniciar a aplicação
def main(page: Page):
    Inicial(page)  # Cria uma instância da classe Inicial


if __name__ == "__main__":
    ft.app(target=main)
