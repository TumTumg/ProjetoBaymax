# camera.py

import cv2
import io

class CameraModule:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # 0 é o ID padrão para a primeira câmera

    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError("Falha ao capturar imagem da câmera")
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            raise RuntimeError("Falha ao codificar imagem em JPEG")
        return buffer.tobytes()

    def __del__(self):
        self.camera.release()
