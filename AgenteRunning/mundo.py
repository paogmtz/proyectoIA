import random

FRECUENCIA_CARDIACA_MINIMA = 100
FRECUENCIA_CARDIACA_MAXIMA = 195
VELOCIDAD_EQUILIBRIO = 12.0

CAMBIO_MINIMO = 0
CAMBIO_MAXIMO_SUBIDA = 1
CAMBIO_MAXIMO_BAJADA = 2

SEGUNDOS_POR_HORA = 3600


class Mundo:
    def __init__(self, distancia_meta_km: float, fc_inicial: int = 120):
        self.tiempo_segundos = 0
        self.distancia_kilometros = 0.0
        self.distancia_meta_km = distancia_meta_km
        self.frecuencia_cardiaca = fc_inicial

    def sensor_frecuencia_cardiaca(self) -> int:
        return self.frecuencia_cardiaca

    def avanzar(self, velocidad: float):
        self.tiempo_segundos += 1
        self.distancia_kilometros += velocidad / SEGUNDOS_POR_HORA

        # Mas rápido que el equilibrio -> tiende a subir.
        # Mas lento que el equilibrio -> tiende a bajar.
        if velocidad >= VELOCIDAD_EQUILIBRIO:
            self.frecuencia_cardiaca += random.randint(
                CAMBIO_MINIMO, CAMBIO_MAXIMO_SUBIDA
            )
        else:
            self.frecuencia_cardiaca -= random.randint(
                CAMBIO_MINIMO, CAMBIO_MAXIMO_BAJADA
            )

        if self.frecuencia_cardiaca > FRECUENCIA_CARDIACA_MAXIMA:
            self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_MAXIMA
        if self.frecuencia_cardiaca < FRECUENCIA_CARDIACA_MINIMA:
            self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_MINIMA