# Simula la carrera segundo a segundo: el agente percibe, decide y el mundo avanza.
from mundo import Mundo, DISTANCIA_META_KILOMETROS
from agente import AgenteMetas, META_MINUTOS

SEGUNDOS_POR_MINUTO = 60


def formato_minutos_segundos(segundos):
    return f"{int(segundos // SEGUNDOS_POR_MINUTO)}:{int(segundos % SEGUNDOS_POR_MINUTO):02d}"


mundo = Mundo()
agente = AgenteMetas()

frecuencia_acumulada_kilometro = 0
segundos_kilometro = 0
kilometro_actual = 0

while mundo.distancia_kilometros < DISTANCIA_META_KILOMETROS:
    # 1. El agente percibe el entorno con sus sensores.
    frecuencia_cardiaca = mundo.sensor_frecuencia_cardiaca()
    distancia = mundo.sensor_distancia()

    # 2. El agente decide que hacer para acercarse a su meta.
    agente.decidir(frecuencia_cardiaca, distancia, mundo.tiempo_segundos)

    # 3. El mundo avanza un segundo con esa decision.
    mundo.avanzar(agente.velocidad)

    # Cada kilometro cerrado se muestra su frecuencia media.
    frecuencia_acumulada_kilometro += frecuencia_cardiaca
    segundos_kilometro += 1
    if int(mundo.distancia_kilometros) > kilometro_actual:
        frecuencia_media = frecuencia_acumulada_kilometro / segundos_kilometro
        print(f"Km {kilometro_actual + 1}: FC media {frecuencia_media:.0f}")
        kilometro_actual += 1
        frecuencia_acumulada_kilometro = 0
        segundos_kilometro = 0

print(f"\nTiempo final: {formato_minutos_segundos(mundo.tiempo_segundos)} (meta: menos de 50:00)")
print(f"FC maxima: {mundo.frecuencia_cardiaca_maxima} bpm")
print(f"Alertas de bajar el ritmo: {agente.numero_alertas}")
if mundo.tiempo_segundos < META_MINUTOS * SEGUNDOS_POR_MINUTO:
    print("META CUMPLIDA")
else:
    print("META NO CUMPLIDA")
