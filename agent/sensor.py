# -*- coding: utf-8 -*-
"""
Sensores del agente (la percepción del mundo).

Un agente solo puede decidir lo que alcanza a percibir. En este avance el
agente monta dos sensores, ambos simulados:

    - Sensor de frecuencia cardíaca : devuelve las pulsaciones reales del
      cuerpo + un pequeño ruido de medición (ningún sensor es perfecto).
    - Sensor de posición (GPS)      : distancia recorrida, velocidad y
      pendiente del terreno en este instante.

Cada segundo los sensores producen una `Percepción`, que es exactamente la
tupla de datos que el agente recibe del mundo.
"""

import random
from dataclasses import dataclass


@dataclass
class Percepcion:
    """Todo lo que el agente sabe del mundo en un instante concreto."""

    tiempo_s: float        # segundos transcurridos en la carrera
    distancia_km: float    # kilómetros recorridos hasta ahora
    velocidad_kmh: float   # velocidad actual
    pendiente_pct: float   # pendiente del terreno en este punto
    fc_bpm: float          # lectura del sensor de frecuencia cardíaca


class Sensores:
    """
    Lector virtual de los sensores.  Recibe una referencia al cuerpo real
    simulado (`RunnerBody`) y solo "lee" de él; nunca modifica su estado.
    """

    def __init__(self, cuerpo, ruido_fc=2.5):
        self.cuerpo = cuerpo
        # Desviación típica del ruido del sensor de FC (en bpm).
        self.ruido_fc = ruido_fc

    def leer(self):
        """Construye y devuelve una Percepcion a partir del estado del cuerpo."""
        fc_real = self.cuerpo.ultima_fc_bpm
        # Medición = valor real + ruido gaussiano (el sensor no es exacto).
        fc_leida = fc_real + random.gauss(0.0, self.ruido_fc)
        return Percepcion(
            tiempo_s=self.cuerpo.tiempo_s,
            distancia_km=self.cuerpo.distancia_km,
            velocidad_kmh=self.cuerpo.velocidad_actual,
            pendiente_pct=self.cuerpo.pendiente_actual,
            fc_bpm=fc_leida,
        )