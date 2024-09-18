# v4/app/__init__.py

from flet import Page
from .routes.routesApp import RoutesHandler  # Importa o manipulador de rotas

def main(page: Page):
    routes_handler = RoutesHandler(page)  # Cria uma instância do manipulador de rotas
    page.on_route_change = routes_handler.route_change  # Define a função de mudança de rota
    page.go("/")  # Carrega a view inicial
