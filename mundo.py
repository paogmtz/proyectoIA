# Mundo simulado: el cuerpo del corredor, el terreno y los sensores.
# Todo son reglas simples con if/else, no hay formulas.

import random

# Terreno de cada kilometro.
TERRENO_PLANO = 0
TERRENO_SUBIDA = 1
TERRENO_BAJADA = -1
TERRENO_POR_KILOMETRO = [
    TERRENO_PLANO, TERRENO_SUBIDA, TERRENO_SUBIDA, TERRENO_BAJADA,
    TERRENO_PLANO, TERRENO_SUBIDA, TERRENO_PLANO, TERRENO_BAJADA,
    TERRENO_PLANO, TERRENO_PLANO,
]

# Estado inicial y limites del cuerpo.
FRECUENCIA_CARDIACA_INICIAL = 150
FRECUENCIA_CARDIACA_MINIMA = 60
FRECUENCIA_CARDIACA_MAXIMA = 185

# Velocidad a la que las pulsaciones se mantienen estables en plano.
VELOCIDAD_EQUILIBRIO = 12.2

# Cada segundo se sortea si la frecuencia cardiaca cambia (1) o se mantiene (0).
CAMBIO_MINIMO_POR_SEGUNDO = 0
CAMBIO_MAXIMO_POR_SEGUNDO = 1

# El terreno pega menos seguido que la velocidad, para que el agente
# siempre pueda recuperar el control bajando el ritmo.
INTERVALO_EFECTO_TERRENO_SEGUNDOS = 3

DISTANCIA_META_KILOMETROS = 10
SEGUNDOS_POR_HORA = 3600


class Mundo:
    def __init__(self):
        self.tiempo_segundos = 0
        self.distancia_kilometros = 0.0
        self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_INICIAL
        self.frecuencia_cardiaca_maxima = FRECUENCIA_CARDIACA_INICIAL

    def pendiente_actual(self):
        kilometro = int(self.distancia_kilometros)
        if kilometro >= DISTANCIA_META_KILOMETROS:
            return TERRENO_PLANO
        return TERRENO_POR_KILOMETRO[kilometro]

    # Sensores: lo unico que el agente puede "ver" del mundo.
    def sensor_frecuencia_cardiaca(self):
        return self.frecuencia_cardiaca

    def sensor_distancia(self):
        return self.distancia_kilometros

    # Avanza un segundo con la velocidad que pide el agente.
    def avanzar(self, velocidad):
        self.tiempo_segundos += 1
        self.distancia_kilometros += velocidad / SEGUNDOS_POR_HORA

        # El cuerpo reacciona a la velocidad: ir rapido sube las
        # pulsaciones e ir lento las baja. Cada segundo se sortea si
        # cambian o se mantienen.
        if velocidad > VELOCIDAD_EQUILIBRIO:
            self.frecuencia_cardiaca += random.randint(
                CAMBIO_MINIMO_POR_SEGUNDO, CAMBIO_MAXIMO_POR_SEGUNDO
            )
        elif velocidad < VELOCIDAD_EQUILIBRIO:
            self.frecuencia_cardiaca -= random.randint(
                CAMBIO_MINIMO_POR_SEGUNDO, CAMBIO_MAXIMO_POR_SEGUNDO
            )

        # El terreno tambien afecta: la subida cuesta y la bajada recupera.
        if self.tiempo_segundos % INTERVALO_EFECTO_TERRENO_SEGUNDOS == 0:
            if self.pendiente_actual() == TERRENO_SUBIDA:
                self.frecuencia_cardiaca += random.randint(
                    CAMBIO_MINIMO_POR_SEGUNDO, CAMBIO_MAXIMO_POR_SEGUNDO
                )
            elif self.pendiente_actual() == TERRENO_BAJADA:
                self.frecuencia_cardiaca -= random.randint(
                    CAMBIO_MINIMO_POR_SEGUNDO, CAMBIO_MAXIMO_POR_SEGUNDO
                )

        if self.frecuencia_cardiaca > FRECUENCIA_CARDIACA_MAXIMA:
            self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_MAXIMA
        if self.frecuencia_cardiaca < FRECUENCIA_CARDIACA_MINIMA:
            self.frecuencia_cardiaca = FRECUENCIA_CARDIACA_MINIMA
        if self.frecuencia_cardiaca > self.frecuencia_cardiaca_maxima:
            self.frecuencia_cardiaca_maxima = self.frecuencia_cardiaca
