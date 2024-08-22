import flet as ft
from styles import button_style, page_style  # Importando os estilos

def main(page: ft.Page):
    page.title = "Projeto Baymax"
    page.bgcolor = page_style()["bgcolor"]  # Definindo o fundo da página

    # Função para navegar entre páginas
    def navigate(e, path):
        page.go(path)

    # Criação da barra de navegação
    nav_bar = ft.Row(
        controls=[
            ft.ElevatedButton("Home", on_click=lambda e: navigate(e, "/home"), style=button_style()),
            ft.ElevatedButton("Chat IA", on_click=lambda e: navigate(e, "/chatIAFlet.py"), style=button_style()),  # Navega para o arquivo chatIAFlet.py
            ft.ElevatedButton("Sobre Nós", on_click=lambda e: navigate(e, "/sobre"), style=button_style()),
            ft.ElevatedButton("Contato", on_click=lambda e: navigate(e, "/contato"), style=button_style()),
            ft.ElevatedButton("Sair", on_click=lambda e: page.window_close(), style=button_style()),  # Fecha o aplicativo
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY  # Alinhamento dos botões
    )

    # Envolvendo a barra de navegação em um Container para aplicar o estilo
    nav_container = ft.Container(
        content=nav_bar,
        bgcolor=ft.colors.GREY_50,  # Alterado para um branco mais escuro
        padding=ft.Padding(top=10, right=10, bottom=10, left=10),
        border_radius=ft.BorderRadius(10, 10, 0, 0)  # Bordas arredondadas apenas na parte superior
    )

    # Adiciona a barra de navegação à página
    page.add(nav_container)

    # Outros conteúdos da página
    page.add(ft.Text("Bem-vindo ao Projeto Baymax!"))

# Configuração do aplicativo
ft.app(target=main)
