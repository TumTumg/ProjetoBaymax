import serial
import time
from twilio.rest import Client

# Função para enviar notificação por SMS usando Twilio
def enviarNotificacaoSMS(mensagem):
    accountSid = 'ACce2ebc80788f9fc1b5092c9912bc5a6a'
    authToken = '009a9936262b6c31cf287b3bf72838ec'
    fromNumber = '+13133296130'
    toNumbers = ['+5511949937625']

    client = Client(accountSid, authToken)

    for number in toNumbers:
        try:
            message = client.messages.create(
                body=mensagem,
                from_=fromNumber,
                to=number
            )
            print(f"Notificação SMS enviada para {number}: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar SMS para {number}: {e}")

# Função principal de monitoramento
def main():
    print("Iniciando Assistente de Monitoramento de Temperatura, Fumaça e Umidade")

    porta = "COM3"  # Altere para a porta onde o Arduino está conectado
    baudRate = 9600
    limiteTemperatura = 30.0
    limiteFumaca = 200  # Sensibilidade para fumaça
    limiteUmidade = 80.0
    temperaturaAnterior = None
    fumacaAnterior = None
    umidadeAnterior = None

    try:
        arduino = serial.Serial(porta, baudRate)
        time.sleep(2)
        print("Conexão com Arduino estabelecida.")
    except serial.SerialException:
        print("Erro ao conectar ao Arduino na porta", porta)
        return "Saindo"

    try:
        while True:
            if arduino.in_waiting > 0:
                dados = arduino.readline().decode("utf-8").strip()
                print("Recebido do Arduino:", dados)

                if "Temperatura Celcius:" in dados:
                    temperatura = float(dados.split(":")[1].strip())
                    if temperatura > limiteTemperatura:
                        if temperaturaAnterior is None or temperatura != temperaturaAnterior:
                            mensagem = f"Alerta: Temperatura alta! Atual: {temperatura}°C."
                            print(mensagem)  # Exibir alerta no terminal
                            enviarNotificacaoSMS(mensagem)
                            temperaturaAnterior = temperatura

                if "Fumaca MQ-2:" in dados:
                    fumaca = int(dados.split(":")[1].strip())
                    if fumaca > limiteFumaca:
                        if fumacaAnterior is None or fumaca != fumacaAnterior:
                            mensagem = f"Alerta: Fumaça detectada! Valor MQ-2: {fumaca}."
                            print(mensagem)  # Exibir alerta no terminal
                            enviarNotificacaoSMS(mensagem)
                            fumacaAnterior = fumaca

                if "Umidade Relativa:" in dados:
                    umidade = float(dados.split(":")[1].strip())
                    if umidade > limiteUmidade:
                        if umidadeAnterior is None or umidade != umidadeAnterior:
                            mensagem = f"Alerta: Umidade alta! Atual: {umidade}%."
                            print(mensagem)  # Exibir alerta no terminal
                            enviarNotificacaoSMS(mensagem)
                            umidadeAnterior = umidade

                time.sleep(1)

    except KeyboardInterrupt:
        print("Leitura interrompida pelo usuário.")

    finally:
        arduino.close()
        return "Leitura do sensor finalizada."


if __name__ == '__main__':
    texto = main()
    print(texto)
 