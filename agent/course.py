# -*- coding: utf-8 -*-
"""
Recorrido de la carrera: 10 kilómetros con su perfil de pendientes.

El corredor conoce de antemano el perfil (es lo que le permite planificar),
por eso el recorrido vive en su propio módulo: tanto el cuerpo real como el
agente lo consultan para saber qué terreno les espera en cada punto.
"""

# ---------------------------------------------------------------------------
# Pendiente media (en %) de cada kilómetro del recorrido.  Positivo = subida,
# negativo = bajada, cero = llano.  Hay una cuesta fuerte en el km 3.
# ---------------------------------------------------------------------------
KM_POR_SEGMENTO = [2, 4, 6, -3, 0, 3, 1, -4, 0, 2]

TOTAL_KM = len(KM_POR_SEGMENTO)   # 10 km


def pendiente_en(distaniencia_km):
    """
    Devuelve la pendiente (porcentaje) de la cuesta sobre la que está
    corriendo la persona a la distancia dada.

    Al simular segundo a segundo, la distancia crece de forma continua;
    usamos la pendiente del kilómetro que la persona está recorriendo.
    """
    segmento = max(0, min(int(distaniencia_km), TOTAL_KM - 1))
    return KM_POR_SEGMENTO[segmento]