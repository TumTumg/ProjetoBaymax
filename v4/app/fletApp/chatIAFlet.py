import flet as ft
import google.generativeai as genai
from pyfirmata import Arduino
import time


def main(page: ft.Page):
    # Configuração da API do Gemini
    genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")

    # Conexão com o Arduino
    portaArduino = 'COM3'  # Substitua 'COM1' pela porta correta
    placa = Arduino(portaArduino)

    # Configuração do pino
    ledPin = 13
    placa.digital[ledPin].write(0)

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

    # Criação da interface de chat
    chat_box = ft.Column()  # Cria um layout vertical para o chat
    message_input = ft.TextField(hint_text="Escreva sua mensagem...")

    def send_message(e):
        texto = message_input.value
        if texto.lower() == "sair":
            page.go("/")  # Volta para a página principal
            return

        try:
            response = chat.send_message(texto)
            chat_box.controls.append(ft.Text(f"Baymax: {response.text}"))
            message_input.value = ""  # Limpa o campo de entrada
            page.update()  # Atualiza a página para mostrar a nova mensagem

            # Controle com o Arduino
            placa.digital[ledPin].write(1)  # Liga o LED
            time.sleep(2)
            placa.digital[ledPin].write(0)  # Desliga o LED
        except Exception as e:
            chat_box.controls.append(ft.Text(f"Erro: {e}"))

    # Adiciona os controles à página
    page.add(chat_box, message_input, ft.ElevatedButton("Enviar", on_click=send_message))

    # Encerrar a comunicação com o Arduino quando a página é fechada
    def cleanup(e):
        placa.exit()

    page.on_close = cleanup

