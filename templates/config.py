class Config:
    GPS_PORT = "COM1"  # Porta serial para GPS
    BAUD_RATE = 9600

    # Coordenadas iniciais e pontos de interesse
    INITIAL_COORDINATES = (0.0, 0.0)  # Substitua por coordenadas reais
    POINTS_OF_INTEREST = {
        "Auditorio": (0.0, 0.0),  # Substitua por coordenadas reais
        "Biblioteca": (0.0, 0.0),  # Substitua por coordenadas reais
        # Adicionar outros pontos de interesse
    }
