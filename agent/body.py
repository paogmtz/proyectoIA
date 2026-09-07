# -*- coding: utf-8 -*-
"""
El "cuerpo real" simulado del corredor.

Este módulo representa el MUNDO, no al agente. Simula la fisiología de la
persona a lo largo de la carrera: avanza la distancia, calcula la FC real
según la fisiología (`physiology`) y anota cuánta energía ("reserva") va
gastando en cada kilómetro.

Habitualmente los agentes perciben y actúan; aquí "actuar" significa darle
una velocidad al cuerpo (lo que pide el agente) y el cuerpo responde con un
nuevo estado (FC, distancia, fatiga). La persona no puede sostener la
velocidad exacta que le piden, así que se le añade un pequeño error de
seguimiento.
"""

import random

import agent.physiology as fisiologia
import agent.course as recorrido


class RunnerBody:
    """Simulación del atleta: su estado interno y su respuesta a la orden."""

    def __init__(self):
        # --- Estado interno del cuerpo en cada instante ---
        self.distancia_km = 0.0
        self.tiempo_s = 0
        self.velocidad_actual = 0.0
        self.pendiente_actual = 0.0
        self.ultima_fc_bpm = fisiologia.FC_REPOSO_BPM

        # --- Datos acumulados para el reporte final ---
        self._fc_acumulada = 0.0        # suma de FC real del kilómetro en curso
        self._segs_km = 0               # segundos del kilómetro en curso
        self._fc_por_km = []            # FC media real de cada kilómetro cerrado
        self.fc_maxima_real = 0.0       # pico de FC alcanzado en toda la carrera

    # ------------------------------------------------------------------
    # Fatiga acumulada (en bpm).  Crece con la distancia: cada kilómetro
    # recorrido añade FATIGA_POR_KM pulsaciones a la FC de base.
    # ------------------------------------------------------------------
    def fatiga_bpm(self):
        return fisiologia.FATIGA_POR_KM * self.distancia_km

    # ------------------------------------------------------------------
    # Avanza un segundo. `velocidad_pedida` es la orden del agente.
    # ------------------------------------------------------------------
    def paso(self, velocidad_pedida_kmh):
        # La persona no sigue la orden a la perfección: +-0.8% de error.
        self.velocidad_actual = velocidad_pedida_kmh * (1.0 + random.gauss(0.0, 0.008))
        self.velocidad_actual = max(0.0, min(20.0, self.velocidad_actual))

        self.tiempo_s += 1
        # Un segundo a esa velocidad recorre (km/h / 3600) kilómetros.
        self.distancia_km += self.velocidad_actual / 3600.0

        # La pendiente se depende del punto del recorrido.
        self.pendiente_actual = recorrido.pendiente_en(self.distancia_km)

        # FC "verdadera" que produce el cuerpo en este instante.
        self.ultima_fc_bpm = fisiologia.frecuencia_cardiaca(
            self.velocidad_actual, self.pendiente_actual, self.fatiga_bpm()
        )
        self._fc_acumulada += self.ultima_fc_bpm
        self._segs_km += 1
        self.fc_maxima_real = max(self.fc_maxima_real, self.ultima_fc_bpm)

        # Si cerramos un kilómetro, guardamos la FC media real DE ESE km
        # (se divide entre los segundos de ese kilómetro, no del total).
        if len(self._fc_por_km) < recorrido.TOTAL_KM:
            if self.distancia_km >= len(self._fc_por_km) + 1:
                media_km = self._fc_acumulada / max(1, self._segs_km)
                self._fc_por_km.append(media_km)
                self._fc_acumulada = 0.0
                self._segs_km = 0

    # ------------------------------------------------------------------
    # Estado meteorológico ... de reporte.
    # ------------------------------------------------------------------
    @property
    def energia_reserva(self):
        """Reserva de energía final (100 - total gastada), en porcentaje.

        Gasta lo que la FC media de cada kilómetro indique; si gasta más de
        100 se dice que la persona "se vacía" (no pasó de un kilómetro).
        """
        gastado = sum(fisiologia.costo_energia_km(km) for km in self._fc_por_km)
        return max(0.0, 100.0 - gastado)

    @property
    def estado_final(self):
        """Resumen del cuerpo al terminar, listo para el reporte."""
        return {
            "tiempo_s": self.tiempo_s,
            "distancia_km": self.distancia_km,
            "fc_maxima_real": self.fc_maxima_real,
            "fc_por_km": list(self._fc_por_km),
            "energia_reserva": self.energia_reserva,
        }