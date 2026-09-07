# Mundo simulado: solo tiene tiempo, distancia y frecuencia cardiaca.
# El unico sensor es el de frecuencia cardiaca.
# La distancia y el tiempo son variables del entorno, no sensores.

import random

FRECUENCIA_CARDIACA_INICIAL = 150
FRECUENCIA_CARDIACA_MINIMA = 150  # corriendo, las pulsaciones no bajan de aqui
FRECUENCIA_CARDIACA_MAXIMA = 185

# Velocidad a la que las pulsaciones se mantienen estables.
VELOCIDAD_EQUILIBRIO = 12.0

# Cada segundo se sortea si la frecuencia cardiaca cambia o se mantiene.
# Sube de 0 a 1 y baja de 0 a 2: el cuerpo se recupera mas rapido
# de lo que se cansa.
CAMBIO_MINIMO = 0
CAMBIO_MAXIMO_SUBIDA = 1
CAMBIO_MAXIMO_BAJADA = 2

DISTANCIA_META_KILOMETROS = 10
SEGUNDOS_POR_HORA = 3600


class Mundo:
    def __init__(self):
        self.tiempo_segundos = 0
        self.distancia_kilometros = 0.0
        self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_INICIAL

    def sensor_frecuencia_cardiaca(self):
        return self.frecuencia_cardiaca

    def avanzar(self, velocidad):
        self.tiempo_segundos += 1
        self.distancia_kilometros += velocidad / SEGUNDOS_POR_HORA

        # Mas rapido que el equilibrio -> tiende a subir.
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
