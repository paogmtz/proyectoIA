# -*- coding: utf-8 -*-
"""
Modelo interno del agente.

El agente no conoce "directamente" el mundo: solo recibe percepciones. Por
eso mantiene un *modelo interno*, una representación mental del cuerpo y
del terreno que le permite PREDECIR qué va a pasar antes de que ocurra.

Concretamente este modelo sabe:
    - Predecir la FC para una velocidad y una pendiente dadas.
    - Invertir esa cuenta: "si quiero sostener 160 bpm en esta cuesta,
      debo ir a X km/h".
    - Llevar estadísticas de lo observado (FC media por km, tiempos).
    - Proyectar el tiempo final y la reserva de energía final si sigue
      como va ahora, que es lo que le permite vigilar su meta.

Usa las mismas ecuaciones de `physiology`: por eso sus predicciones se
parecen tanto a la realidad simulada. No es conocimiento mágico, es el
mismo "mundo" visto desde dentro del agente.
"""

import agent.physiology as fisiologia
import agent.course as recorrido


class ModeloInterno:
    """Representación interna del cuerpo y del recorrido que tiene el agente."""

    LOCALIZADO_KM = recorrido.TOTAL_KM

    def __init__(self):
        # --- Predicción (conocimiento sobre el mundo) ---
        # Nada que guardar aquí: la predicción sale de `physiology`, que ya
        # la conoce cuando el agente se crea.

        # --- Estadísticas de lo observado (memoria del agente) ---
        self._segs_total = 0          # segundos acumulados de la carrera
        self._distancia_observada = 0.0
        self._vel_acum = 0.0          # suma de velocidades observadas
        self._n_obs_vel = 0           # nº de observaciones de velocidad

        self._km_actual = 0           # kilómetro en curso (0 = todavía no)
        self._sum_fc_km = 0.0         # suma de FC dentro del km en curso
        self._segs_km = 0             # segundos transcurridos en el km en curso
        self._fc_media_por_km = []    # FC media observada de cada km cerrado
        self._tiempos_por_km = []     # tiempo real de cada km cerrado

    # ------------------------------------------------------------------
    # La función inversa: la "palanca" del agente sobre el cuerpo.
    # ------------------------------------------------------------------
    def velocidad_para_fc(self, fc_objetivo, pendiente_pct, distancia_actual):
        """Velocidad (km/h) que pedirá el agente para sostener la FC objetivo."""
        fatiga = fisiologia.FATIGA_POR_KM * distancia_actual
        return fisiologia.velocidad_para_fc(fc_objetivo, pendiente_pct, fatiga)

    # ------------------------------------------------------------------
    # Cada segundo el agente incorpora la nueva percepción a su memoria.
    # ------------------------------------------------------------------
    def observar(self, percepcion):
        self._segs_total += 1
        self._segs_km += 1
        self._distancia_observada = percepcion.distancia_km
        self._sum_fc_km += percepcion.fc_bpm
        self._vel_acum += percepcion.velocidad_kmh
        self._n_obs_vel += 1

        # ¿Cruzamos la meta de un kilómetro? Guardamos su FC media y tiempo.
        if self._km_actual < self.LOCALIZADO_KM and \
                percepcion.distancia_km >= self._km_actual + 1:
            self._fc_media_por_km.append(self._sum_fc_km / max(1, self._segs_km))
            self._tiempos_por_km.append(self._segs_km)
            self._sum_fc_km = 0.0
            self._segs_km = 0
            self._km_actual += 1

    # ------------------------------------------------------------------
    # Proyecciones: ¿qué pasará si el agente sigue como va?
    # ------------------------------------------------------------------
    def velocidad_media(self):
        """Velocidad media observada hasta ahora (km/h)."""
        return self._vel_acum / max(1, self._n_obs_vel)

    def proyeccion_tiempo_fin(self):
        """Segundos estimados hasta cruzar la meta si mantiene el ritmo."""
        restante_km = max(0.0, self.LOCALIZADO_KM - self._distancia_observada)
        if self.velocidad_media() <= 0.01:
            return float("inf")
        segundos_restantes = restante_km / self.velocidad_media() * 3600.0
        return self._segs_total + segundos_restantes

    def proyeccion_reserva(self, fc_objetivo):
        """Reserva de energía final (%) estimada según lo observado.

        Suma el gasto real de los kilómetros ya cerrados más una predicción
        del gasto de los kilómetros que faltan al ritmo objetivo actual.
        """
        gasto_real = sum(fisiologia.costo_energia_km(fc) for fc in self._fc_media_por_km)
        cerrados = len(self._fc_media_por_km)
        restantes = self.LOCALIZADO_KM - cerrados
        # La FC media de cada km futuro será aprox. el objetivo (+1/2 bpm del
        # desgaste que crece durante ese kilómetro).
        fc_futura = fc_objetivo + fisiologia.FATIGA_POR_KM / 2.0
        gasto_futuro = restantes * fisiologia.costo_energia_km(fc_futura)
        return max(0.0, 100.0 - (gasto_real + gasto_futuro))

    def detalle_km(self, indice):
        """Datos observados del kilómetro `indice` (1er = índice 0)."""
        if indice < len(self._fc_media_por_km):
            return {
                "fc_media": self._fc_media_por_km[indice],
                "tiempo_s": self._tiempos_por_km[indice],
            }
        return None