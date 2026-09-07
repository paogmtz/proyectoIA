# Simula la carrera segundo a segundo: el agente percibe, decide y el mundo avanza.
from mundo import Mundo
from agente import AgenteMetas


def mm_ss(segundos):
    return f"{int(segundos // 60)}:{int(segundos % 60):02d}"


mundo = Mundo()
agente = AgenteMetas()

energia = 100
fc_km = 0
n_km = 0
km_actual = 0

while mundo.distancia < 10:
    # 1. El agente percibe el entorno con sus sensores.
    fc = mundo.sensor_fc()
    distancia = mundo.sensor_distancia()

    # 2. El agente decide que hacer para acercarse a su meta.
    agente.decidir(fc, distancia, mundo.tiempo)

    # 3. El mundo avanza un segundo con esa decision.
    mundo.avanzar(agente.velocidad)

    # Cada kilometro cerrado se calcula cuanta energia gasto.
    fc_km += fc
    n_km += 1
    if int(mundo.distancia) > km_actual:
        media = fc_km / n_km
        if media > 165:
            energia -= 9  # ir muy revolucionado gasta mas
        else:
            energia -= 6
        print(f"Km {km_actual + 1}: FC media {media:.0f}, energia {energia}%")
        km_actual += 1
        fc_km = 0
        n_km = 0

print(f"\nTiempo final: {mm_ss(mundo.tiempo)} (meta: menos de 50:00)")
print(f"FC maxima: {mundo.fc_max} bpm")
print(f"Alertas de bajar el ritmo: {agente.alertas}")
if mundo.tiempo < 50 * 60 and energia > 0:
    print("META CUMPLIDA")
else:
    print("META NO CUMPLIDA")
