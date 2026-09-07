# -*- coding: utf-8 -*-
"""
El agente basado en metas: el entrenador virtual de running.

Un agente basado en metas ya no solo reacciona (reflejo simple) ni solo
predice (basado en modelos): tiene una META explícita y toma una secuencia
de decisiones para cumplirla.  Su ciclo, segundo a segundo, es:

    1. PERCIBIR   : leer los sensores (frecuencia cardíaca + GPS).
    2. ACTUALIZAR : incorporar la percepción a su modelo interno.
    3. REVISAR    : al cerrar cada kilómetro, comparar plan vs realidad y,
                    si se está desviando de la meta, REPLANIFICAR el ritmo
                    objetivo de los kilómetros que faltan.
    4. ACTUAR     : pedirle al cuerpo la velocidad que mantiene la FC
                    objetivo en el terreno actual (con el desgaste actual).

La meta de este avance:
    - Completar 10 km en menos de 50 minutos.
    - Sin superar nunca 168 bpm (techo de seguridad del plan).
    - Terminando con al menos 8% de reserva de energía ("con energía").

Como red de seguridad extra, el agente conserva un reflejo de emergencia:
si el sensor marca más de 168 bpm, baja la velocidad de inmediato ese
segundo, antes de volver a su estrategia de metas.
"""

from dataclasses import dataclass

from agent.internal_model import ModeloInterno
from agent.planner import Planificador
import agent.course as recorrido


# ---------------------------------------------------------------------------
# La meta, escrita como datos y no escondida en el código.  Así, cambiar la
# meta (p. ej. "10 km en 45 minutos") no obliga a reescribir al agente.
# ---------------------------------------------------------------------------
@dataclass
class Meta:
    distancia_km: float = 10.0     # distancia que hay que completar
    tiempo_limite_s: float = 3000  # 50 minutos expresados en segundos
    fc_max: float = 168.0          # techo de FC que nunca debe superarse
    reserva_min: float = 8.0       # reserva mínima de energía al final (%)


def _mm_ss(segundos):
    """Convierte 2989 s en el texto '49:49' para los reportes."""
    return f"{int(segundos // 60)}:{int(round(segundos % 60)):02d}"


class AgenteMetas:
    """Entrenador virtual que persigue su meta kilómetro a kilómetro."""

    def __init__(self, meta=None, fc_inicial=160.0):
        self.meta = meta or Meta()

        # El agente nace con su modelo interno (su "mapa mental" del cuerpo).
        self.modelo = ModeloInterno()

        # ...y con una estrategia creada ANTES de dar el primer paso: el
        # plan de ritmo que cree que le llevará a la meta.
        self.plan = Planificador.crear_plan(fc_objetivo=fc_inicial)
        self.fc_objetivo = fc_inicial

        # Bitácora: cada decisión importante queda registrada para poder
        # explicar después por qué el agente hizo lo que hizo.
        self.bitacora = []
        self.bitacora.append(
            f"Estrategia inicial: sostener ~{fc_inicial:.0f} bpm con un ritmo "
            f"adaptado a cada cuesta. Proyección del plan: {_mm_ss(self.plan.tiempo_total_s)} "
            f"y {self.plan.reserva_pred:.1f}% de energía final."
        )

        self._km_revisado = 0     # último kilómetro ya evaluado y corregido
        self._alerta_activa = False  # evita repetir la misma alerta cada segundo

        # Ventana corta de lecturas de FC para la alerta de seguridad: el
        # sensor tiene ruido, así que la alerta mira el promedio de los
        # últimos 5 segundos y no una sola lectura aislada.
        self._historial_fc = []

    # ------------------------------------------------------------------
    # 1 y 2. Percibir + actualizar el modelo interno.
    # ------------------------------------------------------------------
    def percibir(self, sensores):
        """Pide a los sensores la percepción de este segundo."""
        return sensores.leer()

    # ------------------------------------------------------------------
    # 4. Actuar: decidir la velocidad de este segundo.
    # ------------------------------------------------------------------
    def decidir(self, percepcion):
        """Devuelve la velocidad (km/h) que le pide al cuerpo este segundo."""

        # Primero actualiza su representación del mundo con lo percibido.
        self.modelo.observar(percepcion)

        # Si se cruzó la línea de un kilómetro, lo revisa (paso 3).
        if self.modelo._km_actual > self._km_revisado:
            self._revisar_kilometro()

        # Velocidad que sostiene la FC objetivo en ESTE terreno y con ESTE
        # desgaste acumulado (la "palanca" que le da su modelo interno).
        velocidad = self.modelo.velocidad_para_fc(
            self.fc_objetivo,
            percepcion.pendiente_pct,
            percepcion.distancia_km,
        )

        # Reflejo de seguridad: si la FC supera el techo, se baja el ritmo
        # de inmediato, sin esperar a la próxima revisión del kilómetro.
        # Se usa el promedio de los últimos 5 s para no reaccionar a un
        # simple pico de ruido del sensor.
        self._historial_fc.append(percepcion.fc_bpm)
        self._historial_fc = self._historial_fc[-5:]
        fc_suave = sum(self._historial_fc) / len(self._historial_fc)

        if fc_suave > self.meta.fc_max:
            velocidad *= 0.8
            # El objetivo también se ajusta a la baja, con un piso de 148.
            self.fc_objetivo = max(148.0, min(self.fc_objetivo, fc_suave - 4))
            if not self._alerta_activa:
                self.bitacora.append(
                    f"ALERTA de seguridad: FC {fc_suave:.0f} bpm > "
                    f"{self.meta.fc_max:.0f} bpm. Bajo el ritmo un 20%."
                )
                self._alerta_activa = True
        else:
            self._alerta_activa = False

        return velocidad

    def cerrar_carrera(self, sensores):
        """Lectura final tras cruzar la meta: cierra el último kilómetro.

        Durante la carrera el agente percibe ANTES de que el cuerpo avance;
        por eso el kilómetro 10 solo queda "cerrado" en su memoria si hace
        una última observación después del paso final.
        """
        self.modelo.observar(self.percibir(sensores))
        if self.modelo._km_actual > self._km_revisado:
            self._revisar_kilometro()

    # ------------------------------------------------------------------
    # 3. Revisar: al cerrar cada kilómetro se compara plan vs realidad y,
    # si la meta peligra, se corrige el ritmo objetivo de lo que falta.
    # ------------------------------------------------------------------
    def _revisar_kilometro(self):
        indice = self._km_revisado          # 0 = primer kilómetro cerrado
        observado = self.modelo.detalle_km(indice)
        planeado = self.plan.divisiones[indice]

        # ¿Cómo va respecto al tiempo y la energía si sigue así?
        proy_tiempo = self.modelo.proyeccion_tiempo_fin()
        proy_reserva = self.modelo.proyeccion_reserva(self.fc_objetivo)

        mensaje = (
            f"Km {indice + 1}: plan {_mm_ss(planeado.tiempo_s)}/FC "
            f"{planeado.fc_media_pred:.0f} -> real {_mm_ss(observado['tiempo_s'])}/FC "
            f"{observado['fc_media']:.0f}. "
        )

        # Corrección 1: si la proyección ya no cumple el tiempo, se aprieta.
        if proy_tiempo > self.meta.tiempo_limite_s and self.fc_objetivo < 166:
            self.fc_objetivo += 3
            mensaje += (
                f"Voy tarde (proyección {_mm_ss(proy_tiempo)} > 50:00): "
                f"subo el objetivo a {self.fc_objetivo:.0f} bpm."
            )
        # Corrección 2: si la energía final peligra, se afloja.
        elif proy_reserva < self.meta.reserva_min and self.fc_objetivo > 148:
            self.fc_objetivo -= 2
            mensaje += (
                f"La energía peligra (proyección {proy_reserva:.1f}% < "
                f"{self.meta.reserva_min:.0f}%): aflojo a {self.fc_objetivo:.0f} bpm."
            )
        # Sin peligro: se mantiene la estrategia.
        else:
            mensaje += "Dentro del plan; mantengo el ritmo objetivo."

        self.bitacora.append(mensaje)
        self._km_revisado += 1

    # ------------------------------------------------------------------
    # Veredicto final: ¿se cumplió la meta?  Se evalúa con los datos REALES
    # del cuerpo, no con lo que el agente cree.
    # ------------------------------------------------------------------
    def veredicto(self, reporte_cuerpo):
        tiempo_ok = reporte_cuerpo["tiempo_s"] <= self.meta.tiempo_limite_s
        fc_ok = reporte_cuerpo["fc_maxima_real"] <= self.meta.fc_max + 2.0
        energia_ok = reporte_cuerpo["energia_reserva"] >= self.meta.reserva_min
        return {
            "tiempo_ok": tiempo_ok,
            "fc_ok": fc_ok,
            "energia_ok": energia_ok,
            "meta_cumplida": tiempo_ok and fc_ok and energia_ok,
        }