from pyfirmata import Arduino, util
import time

# Substitua 'COM1' pela porta correta
portaArduino = 'COM3'
placa = Arduino(portaArduino)

# Teste de comunicação
print("Conectando ao Arduino...")
time.sleep(2)
print("Conectado com sucesso!")

# Testa acender e apagar o LED
ledPin = 13
placa.digital[ledPin].write(1)  # Liga o LED
time.sleep(2)
placa.digital[ledPin].write(0)  # Desliga o LED
print("Teste concluído.")

# Encerrar a comunicação
placa.exit()
