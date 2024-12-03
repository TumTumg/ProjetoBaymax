import serial
import time
from twilio.rest import Client
import subprocess

# Função para enviar mensagens na rede
def enviar_mensagem_rede(destinatario, mensagem):
    try:
        # Comando para enviar a mensagem na rede
        comando = f"msg * /server:{destinatario} {mensagem}"
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Mensagem enviada para {destinatario}: {mensagem}")
        else:
            print(f"Erro ao enviar mensagem: {result.stderr}")
    except Exception as e:
        print(f"Erro ao executar o comando: {e}")

# Função para enviar notificação por SMS usando Twilio
def enviar_notificacao_sms(temperatura):
    # Informações do Twilio (substitua pelos dados da sua conta)
    account_sid = ''
    auth_token = ''
    from_number = '+13133296130'  # Seu número Twilio
    to_numbers = ['+5511949937625']  # Lista de números de telefone para enviar SMS

    # Configuração da mensagem
    mensagem = f"Atenção: Temperatura elevada detectada! Temperatura atual: {temperatura}°C."

    # Criação do cliente Twilio
    client = Client(account_sid, auth_token)

    # Envio da notificação por SMS para os números na lista
    for number in to_numbers:
        print(f"Enviando mensagem para: {number}")  # Log para verificar qual número está sendo processado
        try:
            message = client.messages.create(
                body=mensagem,
                from_=from_number,
                to=number
            )
            print(f"Notificação SMS enviada para {number}: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar SMS para {number}: {e}")  # Log de erro caso aconteça algum problema

# Função principal de monitoramento
# Função principal de monitoramento
def main():
    print("Iniciando Assistente de Monitoramento de Temperatura e Umidade")

    porta = "COM5"  # Ajuste para a porta correta do seu Arduino
    baud_rate = 9600  # Taxa de comunicação definida no Arduino
    limite_temperatura = 30.0  # Limite de temperatura para envio de alerta
    temperatura_anterior = None  # Variável para controlar quando a temperatura excede o limite

    try:
        arduino = serial.Serial(porta, baud_rate)
        time.sleep(2)  # Aguarda a conexão com o Arduino
        print("Conexão com Arduino estabelecida.")
    except serial.SerialException:
        print("Erro ao conectar ao Arduino na porta", porta)
        return "Saindo"

    try:
        while True:
            if arduino.in_waiting > 0:  # Verifica se há dados para ler
                dados = arduino.readline().decode("utf-8").strip()
                print("Recebido do Arduino:", dados)

                # Verifica se a leitura contém temperatura e converte para float
                if "Temperatura Celcius:" in dados:
                    temperatura = float(dados.split(":")[1].strip())
                    print(f"Temperatura recebida: {temperatura}°C")  # Log para depuração

                    # Verifica se a temperatura excedeu o limite de 30 graus
                    if temperatura > limite_temperatura:
                        # Envia a notificação apenas quando a temperatura exceder o limite
                        if temperatura_anterior is None or temperatura != temperatura_anterior:
                            enviar_notificacao_sms(temperatura)
                            temperatura_anterior = temperatura  # Atualiza a temperatura anterior

                            # Enviar mensagem pela rede com o comando msg
                            destinatario = "192.168.15.12"  # Endereço IP ou nome do computador na rede
                            mensagem = f"Temperatura elevada detectada! Temperatura atual: {temperatura}°C"
                            enviar_mensagem_rede(destinatario, mensagem)

                time.sleep(1)  # Intervalo para a próxima leitura

    except KeyboardInterrupt:
        print("Leitura interrompida pelo usuário.")

    finally:
        arduino.close()
        return "Leitura do sensor finalizada."


if __name__ == '__main__':
    texto = main()
    print(texto)

