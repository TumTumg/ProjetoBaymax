import serial

class Hardware:
    def __init__(self, gps_port, baud_rate):
        self.gps_port = gps_port
        self.baud_rate = baud_rate
        self.gps_serial = None

    def initialize_gps(self):
        self.gps_serial = serial.Serial(self.gps_port, self.baud_rate)

    def read_gps_data(self):
        if self.gps_serial:
            return self.gps_serial.readline().decode('utf-8')
        return None

    def initialize_touchscreen(self):
        # Código específico para inicialização do touchscreen
        pass

    def initialize_camera(self):
        # Código específico para inicialização da câmera
        pass
