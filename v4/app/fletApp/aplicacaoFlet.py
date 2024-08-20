import flet as ft
import chatIAFlet  # Importando corretamente

def create_button(text, page=None):
    # Cria um botão e define o comportamento ao clicar
    if text == "Chat IA":
        return ft.ElevatedButton(text, on_click=lambda e: page.go("/chatIAFlet.py"))  # Adiciona a navegação para /chat
    else:
        return ft.ElevatedButton(text)  # Para outros botões, você pode definir outras funcionalidades conforme necessário

def main(page: ft.Page):
    page.title = "Projeto Baymax - Interface"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#FFFFFF"

    # Criando os botões
    buttons = [
        create_button("Chat IA", page),  # Passando a página para o botão de Chat IA
        create_button("Reciclagem e Limpeza"),
        create_button("Temperatura e Umidade"),
        create_button("Biblioteca SENAC"),
        create_button("Acompanhamento de Estudantes"),
        create_button("Conexão SIPAT"),
        create_button("Sobre Nós"),
        create_button("Contato"),
        create_button("Sair"),
    ]

    for button in buttons:
        page.add(button)

    # Define a rota para o chat IA
    page.route("/chat", chatIAFlet.main)

ft.app(target=main)
