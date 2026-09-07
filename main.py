# -*- coding: utf-8 -*-
"""
Punto de entrada del avance: simula la carrera del agente de running.

Uso (desde la carpeta del proyecto):
    python3 main.py
"""

from agent.simulation import simular_carrera


if __name__ == "__main__":
    resultado = simular_carrera()
    resultado.mostrar()