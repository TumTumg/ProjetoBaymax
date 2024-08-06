from pyfirmata import Arduino, util
import time
import logging
from config import Config  # Certifique-se de que o caminho está correto


class HardwareDAO:
    def __init__(self, port):
        self.port = port
        self.board = None
        self.iterator = None
        self.connect()

    def connect(self):
        """Conecta ao Arduino e inicializa o iterator."""
        try:
            logging.info(f"Conectando ao Arduino na porta {self.port}")
            self.board = Arduino(self.port)
            self.iterator = util.Iterator(self.board)
            self.iterator.start()
            logging.info("Conexão com Arduino estabelecida com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao conectar ao Arduino na porta {self.port}: {e}")
            raise

    def blinkLED(self, pin, times=5, delay=1):
        """Acende e apaga o LED no pino especificado um número de vezes."""
        try:
            if not self.board:
                raise RuntimeError("Conexão com o Arduino não estabelecida.")

            pin = self.board.get_pin(f'd:{pin}:o')
            for _ in range(times):
                logging.info(f"Piscar LED no pino {pin}")
                pin.write(1)
                time.sleep(delay)
                pin.write(0)
                time.sleep(delay)
            logging.info("LED piscado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao piscar LED no pino {pin}: {e}")
            raise

    def readSensor(self, pin):
        """Lê o valor de um sensor no pino especificado."""
        try:
            if not self.board:
                raise RuntimeError("Conexão com o Arduino não estabelecida.")

            pin = self.board.get_pin(f'a:{pin}:i')
            value = pin.read()
            logging.info(f"Leitura do sensor no pino {pin}: {value}")
            return value
        except Exception as e:
            logging.error(f"Erro ao ler o sensor no pino {pin}: {e}")
            raise

    def close(self):
        """Fecha a conexão com o Arduino."""
        try:
            if self.board:
                self.board.exit()
                logging.info("Conexão com o Arduino fechada.")
        except Exception as e:
            logging.error(f"Erro ao fechar a conexão com o Arduino: {e}")


# Exemplo de uso:
if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    dao = None
    try:
        dao = HardwareDAO(Config.ARDUINO_PORT)  # Use Config aqui
        dao.blinkLED(pin=13, times=3)
        sensor_value = dao.readSensor(pin=0)
        print(f"Valor do sensor: {sensor_value}")
    except Exception as e:
        logging.error(f"Erro no HardwareDAO: {e}")
    finally:
        if dao:
            dao.close()
