# -*- coding: utf-8 -*-
"""
Planificador de ritmo: la estrategia ANTES de dar el primer paso.

Un agente basado en metas no reacciona solo: formula una secuencia de
acciones para lograr su meta y la ejecuta (y corrige) sobre la marcha.
Aquí, la meta es "10 km en menos de 50 minutos terminando con energía".

La estrategia es repartir el esfuerzo kilómetro a kilómetro de forma que la
FC se mantenga en un valor objetivo razonable (ni muy alto, para no vaciar
el cuerpo, ni demasiado bajo, para poder cumplir el tiempo). Como subir
cuesta es más caro, en las pendientes el plan baja la velocidad, y en las
bajadas la recupera. El resultado es una tabla de particiones (splits)
que el agente consulta como su hoja de ruta.
"""

from dataclasses import dataclass

import agent.physiology as fisiologia
import agent.course as recorrido


@dataclass
class Division:
    """División de un kilómetro del plan (un split)."""

    km: int               # número del kilómetro (1..10)
    pendiente: float      # pendiente media de ese kilómetro (%)
    velocidad: float      # velocidad objetivo planificada (km/h)
    tiempo_s: float       # tiempo previsto para ese kilómetro (s)
    fc_media_pred: float  # FC media prevista durante ese kilómetro (bpm)


@dataclass
class Plan:
    """Plan completo: las 10 divisiones + los totales que predice."""

    fc_objetivo: float                    # FC que tratará de sostener (bpm)
    divisiones: list                      # lista de `Division`
    tiempo_total_s: float                 # tiempo total previsto (s)
    reserva_pred: float                   # reserva final de energía prevista (%)

    def ver(self):
        """Tabla legible de la estrategia (para el reporte)."""
        filas = []
        for d in self.divisiones:
            mm = int(d.tiempo_s // 60)
            ss = int(round(d.tiempo_s % 60))
            filas.append((d.km, d.pendiente, d.velocidad, f"{mm}:{ss:02d}"))
        return filas


class Planificador:
    """
    Crea el plan de dividido en particiones a partir de un valor de FC
    objetivo que el agente quiere mantener durante toda la carrera.
    """

    @staticmethod
    def crear_plan(fc_objetivo=160.0):
        """Devuelve un `Plan` para los 10 km del recorrido dado el objetivo."""
        divisiones = []
        gasto_total = 0.0

        for km in range(1, recorrido.TOTAL_KM + 1):
            # Pendiente del kilómetro que vamos a planificar.
            pendiente = recorrido.pendiente_en(km - 1)

            # Fatiga prevista AL INICIO de este km (la que arrastra desde
            # el kilómetro anterior).
            distancia_previa = km - 1
            velocidad = fisiologia.velocidad_para_fc(
                fc_objetivo, pendiente,
                fisiologia.FATIGA_POR_KM * distancia_previa,
            )
            tiempo_s = 3600.0 / velocidad

            # Durante el km la fatiga crece 0.5 bpm, así que la FC media
            # será el objetivo más medio escalón de desgaste.
            fc_media = fc_objetivo + fisiologia.FATIGA_POR_KM / 2.0
            gasto_total += fisiologia.costo_energia_km(fc_media)

            divisiones.append(Division(
                km=km,
                pendiente=pendiente,
                velocidad=velocidad,
                tiempo_s=tiempo_s,
                fc_media_pred=fc_media,
            ))

        total_s = sum(d.tiempo_s for d in divisiones)
        return Plan(
            fc_objetivo=fc_objetivo,
            divisiones=divisiones,
            tiempo_total_s=total_s,
            reserva_pred=max(0.0, 100.0 - gasto_total),
        )