# -*- coding: utf-8 -*-
"""
Fisiología simulada del corredor.

Aquí viven las *ecuaciones* que describen cómo responde el cuerpo durante
la carrera. Este módulo es el corazón del proyecto por dos motivos:

1. El cuerpo real (`body.RunnerBody`) las usa para generar los datos que
   el agente percibe a través de sus sensores.

2. El agente (basado en modelos y en metas) mantiene una copia de estas
   mismas ecuaciones dentro de su *modelo interno* (`internal_model`),
   de modo que puede predecir el futuro antes de que ocurra.

La frecuencia cardíaca (FC), que es el sensor más importante del proyecto,
se modela así, en pulsaciones por minuto (bpm):

    FC = FC_en_reposo
       + 7.5   * velocidad(km/h)        # esfuerzo base del movimiento
       + 0.10  * pendiente(%) * vel     # subir cuesta cuesta más
       + 0.03  * pendiente(%) * vel     # bajar cuesta alivia un poco
       + fatiga_acumulada(bpm)          # el desgaste sube ligeramente la FC

El término de pendiente es positivo cuando se sube (pendiente > 0) y
negativo cuando se baja (pendiente < 0), por eso se divide en dos tramos.

A partir de esta ecuación también se obtiene la *función inversa*: dado un
valor de FC que queremos mantener, ¿a qué velocidad debemos correr? Esa
respuesta es la que le permite al agente planificar y regular su ritmo.
"""

# ---------------------------------------------------------------------------
# Constantes fisiológicas del corredor simulado.
# ---------------------------------------------------------------------------
FC_REPOSO_BPM = 65.0     # pulsaciones en reposo (sensor montado en reposo)
FC_MAX_PLAN    = 168.0   # techo de FC que el agente NO quiere superar
COEF_VELOCIDAD = 7.5     # bpm por cada km/h de velocidad
COEF_SUBIDA    = 0.10    # bpm extra por cada % de pendiente * velocidad
COEF_BAJADA    = 0.03    # bpm de menos por cada % de pendiente * velocidad
FATIGA_POR_KM  = 0.5     # bpm de FC que añade cada kilómetro ya recorrido
ESCALA_ENERGIA = 9.5     # escala que convierte la FC de cada km en gasto de


# ---------------------------------------------------------------------------
# Cálculo directo: dada la velocidad y el terreno, ¿qué FC tendrá?  Está
# función la usa primero el cuerpo real (para simular la verdad) y demás
# el modelo interno del agente (para predecirla).
# ---------------------------------------------------------------------------
def frecuencia_cardiaca(velocidad_kmh, pendiente_pct, fatiga_bpm):
    """Devuelve la FC esperada (bpm) para una velocidad y un terreno dados."""

    # En subida la pendiente se cobra un "impuesto" mayor que en bajada.
    if pendiente_pct >= 0:
        efecto_terreno = COEF_SUBIDA * pendiente_pct
    else:
        efecto_terreno = COEF_BAJADA * pendiente_pct

    fc = FC_REPOSO_BPM
    fc += COEF_VELOCIDAD * velocidad_kmh
    fc += efecto_terreno * velocidad_kmh
    fc += fatiga_bpm
    return fc


# ---------------------------------------------------------------------------
# Función inversa: dado el terreno y la FC objetivo, ¿a qué velocidad correr?
# Es la herramienta de "control" del agente: le dice qué velocidad pedirle
# al cuerpo para que la FC se quede en el valor deseado.
# ---------------------------------------------------------------------------
def velocidad_para_fc(fc_objetivo, pendiente_pct, fatiga_bpm):
    """Devuelve la velocidad (km/h) necesaria para sostener la FC objetivo."""

    if pendiente_pct >= 0:
        efecto_terreno = COEF_SUBIDA * pendiente_pct
    else:
        efecto_terreno = COEF_BAJADA * pendiente_pct

    denominador = COEF_VELOCIDAD + efecto_terreno
    velocidad = (fc_objetivo - FC_REPOSO_BPM - fatiga_bpm) / denominador
    # Límites de seguridad: ni a paso de caminata ni a sprint imposible.
    return max(6.0, min(18.0, velocidad))


# ---------------------------------------------------------------------------
# Energía / desgaste.
# "Terminar con energía" se traduce a un costo por kilómetro: cuanto más alta
# sea la FC media de un kilómetro, más "energía" gasta ese kilómetro. El
# mecanismo valora la FC respecto al techo planificado (FC_MAX_PLAN).
# ---------------------------------------------------------------------------
def costo_energia_km(fc_media_km):
    """Gasto de energía (puntos 0..~10) para un kilómetro con FC_media dada."""

    exceso = max(0.0, fc_media_km - FC_REPOSO_BPM)
    base = FC_MAX_PLAN - FC_REPOSO_BPM
    return (exceso / base) * ESCALA_ENERGIA