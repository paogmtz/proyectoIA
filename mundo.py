import random

FRECUENCIA_CARDIACA_MINIMA = 60
FRECUENCIA_CARDIACA_MAXIMA = 195  # Se puede ajustar según el usuario
VELOCIDAD_EQUILIBRIO = 12.0

CAMBIO_MINIMO = 0
CAMBIO_MAXIMO_SUBIDA = 1
CAMBIO_MAXIMO_BAJADA = 2

SEGUNDOS_POR_HORA = 3600


class Mundo:
    def __init__(self, usuario, fc_inicial: int = 75):
        self.usuario = usuario
        self.tiempo_segundos = 0
        self.distancia_kilometros = 0.0
        self.distancia_meta_km = usuario.distancia_km
        self.frecuencia_cardiaca = fc_inicial

    def sensor_frecuencia_cardiaca(self) -> int:
        return round(self.frecuencia_cardiaca)

    def avanzar(self, velocidad: float):
        self.tiempo_segundos += 1
        self.distancia_kilometros += velocidad / SEGUNDOS_POR_HORA

        # Valor al que tenderían las pulsaciones a esta velocidad.
        # A 11 km/h, tienden a la frecuencia objetivo de ESTE usuario.
        frecuencia_deseada = 75 + (
            self.usuario.fc_objetivo - 75
        ) * (velocidad / 11.0)

        # Las pulsaciones se acercan poco a poco; no saltan inmediatamente.
        self.frecuencia_cardiaca += (
            frecuencia_deseada - self.frecuencia_cardiaca
        ) * 0.05

        # Límites de la simulación.
        self.frecuencia_cardiaca = max(
            60,
            min(self.frecuencia_cardiaca, self.usuario.fc_maxima)
        )