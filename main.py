# Carrera simulada: el agente percibe, decide y el mundo avanza.
from mundo import Mundo, DISTANCIA_META_KILOMETROS
from agente import AgenteMetas, META_MINUTOS

SEGUNDOS_POR_MINUTO = 60


def formato_minutos_segundos(segundos):
    minutos = segundos // SEGUNDOS_POR_MINUTO
    resto = segundos % SEGUNDOS_POR_MINUTO
    return f"{minutos}:{resto:02d}"


# 1. Se crea el mundo.
mundo = Mundo()

# 2. Se crea el agente.
agente = AgenteMetas()

# 7. Se repite hasta recorrer los 10 km.
while mundo.distancia_kilometros < DISTANCIA_META_KILOMETROS:
    # 3. Se obtiene la frecuencia cardiaca del sensor.
    frecuencia_cardiaca = mundo.sensor_frecuencia_cardiaca()

    # 4 y 5. Se le da al agente frecuencia, distancia y tiempo, y decide.
    accion = agente.decidir(
        frecuencia_cardiaca, mundo.distancia_kilometros, mundo.tiempo_segundos
    )

    # 6. El mundo avanza un segundo con la velocidad elegida.
    mundo.avanzar(agente.velocidad)

    # Se muestra informacion cada minuto, no cada segundo.
    if mundo.tiempo_segundos % SEGUNDOS_POR_MINUTO == 0:
        minutos = mundo.tiempo_segundos // SEGUNDOS_POR_MINUTO
        print(
            f"Tiempo: {minutos} min | "
            f"Distancia: {mundo.distancia_kilometros:.2f} km | "
            f"FC: {frecuencia_cardiaca} bpm | "
            f"Acción: {accion}"
        )

print(f"\nTiempo final: {formato_minutos_segundos(mundo.tiempo_segundos)}")
print(f"Distancia recorrida: {mundo.distancia_kilometros:.2f} km")
if mundo.tiempo_segundos < META_MINUTOS * SEGUNDOS_POR_MINUTO:
    print("META CUMPLIDA")
else:
    print("META NO CUMPLIDA")
