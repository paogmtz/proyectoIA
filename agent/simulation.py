# -*- coding: utf-8 -*-
"""
Simulación de la carrera: junta el mundo, los sensores y el agente.

Cada segundo simulado ocurre lo mismo que en la vida real:
    1. Los sensores leen el estado del cuerpo (percepción).
    2. El agente decide la velocidad (acción).
    3. El cuerpo avanza un segundo con esa orden (efecto en el mundo).

Cuando el corredor cruza los 10 km, se arma el `Resultado` con el plan
inicial, lo que pasó de verdad en cada kilómetro, el resumen final y el
veredicto de la meta.  `main.py` lo único que hace es correr esto y
mostrarlo en pantalla.
"""

import random
from dataclasses import dataclass

import agent.course as recorrido
from agent.body import RunnerBody
from agent.sensor import Sensores
from agent.goal_agent import AgenteMetas, _mm_ss


@dataclass
class Resultado:
    """Todo lo que dejó la carrera simulada, listo para mostrarse."""

    agente: AgenteMetas
    cuerpo: RunnerBody

    # ------------------------------------------------------------------
    # Tablas y resúmenes para el reporte (todo en texto plano).
    # ------------------------------------------------------------------
    def lineas_plan(self):
        lineas = ["Km | Pend. | Vel. plan | Tiempo plan | FC prevista",
                  "---|-------|-----------|-------------|------------"]
        for d in self.agente.plan.divisiones:
            lineas.append(
                f"{d.km:>2} | {d.pendiente:>+4.0f}% | {d.velocidad:>7.2f} km/h | "
                f"{_mm_ss(d.tiempo_s):>9} | {d.fc_media_pred:>6.0f} bpm"
            )
        return lineas

    def lineas_reales(self):
        lineas = ["Km | Tiempo real | FC media real | Split plan",
                  "---|-------------|----------------|------------"]
        for i in range(recorrido.TOTAL_KM):
            obs = self.agente.modelo.detalle_km(i)
            plan = self.agente.plan.divisiones[i]
            if obs is None:      # por si la carrera se detuvo antes
                break
            lineas.append(
                f"{i + 1:>2} | {_mm_ss(obs['tiempo_s']):>9} | "
                f"{obs['fc_media']:>10.0f} bpm | {_mm_ss(plan.tiempo_s):>9}"
            )
        return lineas

    def mostrar(self):
        rep = self.cuerpo.estado_final
        ver = self.agente.veredicto(rep)

        print("=" * 64)
        print("  AGENTE DE RUNNING BASADO EN METAS  (avance del proyecto)")
        print("  Meta: 10 km en menos de 50:00, FC <= 168, reserva >= 8%")
        print("=" * 64)

        print("\n[1] ESTRATEGIA INICIAL DEL AGENTE (plan antes de arrancar)")
        print("\n".join(self.lineas_plan()))
        print(f"Proyección del plan: {_mm_ss(self.agente.plan.tiempo_total_s)} "
              f"y {self.agente.plan.reserva_pred:.1f}% de energía final.")

        print("\n[2] LO QUE PASÓ DE VERDAD, KILÓMETRO A KILÓMETRO")
        print("\n".join(self.lineas_reales()))

        print("\n[3] RESUMEN FINAL")
        print(f"  Tiempo final .... {_mm_ss(rep['tiempo_s'])} "
              f"(meta: menos de 50:00) -> {'OK' if ver['tiempo_ok'] else 'NO'}")
        print(f"  FC máxima ....... {rep['fc_maxima_real']:.0f} bpm "
              f"(techo: 168) -> {'OK' if ver['fc_ok'] else 'NO'}")
        print(f"  Energía final ... {rep['energia_reserva']:.1f}% "
              f"(mínimo: 8%) -> {'OK' if ver['energia_ok'] else 'NO'}")

        print("\n[4] VEREDICTO:", "META CUMPLIDA" if ver["meta_cumplida"] else "META NO CUMPLIDA")

        print("\n[5] BITÁCORA DE DECISIONES DEL AGENTE")
        for entrada in self.agente.bitacora:
            print("  - " + entrada)


def simular_carrera(semilla=7):
    """Corre la carrera completa y devuelve su `Resultado`.

    `semilla` fija el azar del simulador para que el resultado sea siempre
    el mismo (útil para presentar el avance en clase).  Cámbiala o quítala
    para ver otras carreras posibles.
    """
    random.seed(semilla)

    cuerpo = RunnerBody()          # el mundo real simulado
    sensores = Sensores(cuerpo)    # lo único que el agente puede percibir
    agente = AgenteMetas()         # el cerebro basado en metas

    # Bucle principal: percibir -> decidir -> avanzar un segundo.
    # Hay un tope de 10 minutos extra por si el agente fuese demasiado lento
    # (así la simulación siempre termina).
    tope_s = int(agente.meta.tiempo_limite_s) + 600
    while cuerpo.distancia_km < recorrido.TOTAL_KM and cuerpo.tiempo_s < tope_s:
        percepcion = agente.percibir(sensores)
        accion = agente.decidir(percepcion)
        cuerpo.paso(accion)

    # Última lectura para que el agente cierre el kilómetro 10 en su memoria.
    agente.cerrar_carrera(sensores)

    return Resultado(agente=agente, cuerpo=cuerpo)