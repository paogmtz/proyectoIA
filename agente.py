# Agente basado en metas: quiere terminar 10 km en menos de 50 minutos.
# Detecta el entorno con sus sensores y decide solo con if/else.

# Meta y plan del agente.
META_MINUTOS = 50
RITMO_PLAN_SEGUNDOS_POR_KILOMETRO = 300  # su plan: 5 minutos por km
TOLERANCIA_RETRASO_SEGUNDOS = 20  # cuanto puede atrasarse antes de apretar

# Velocidades que usa segun la situacion (km/h).
VELOCIDAD_INICIAL = 12.0
VELOCIDAD_RITMO_PLAN = 12.4
VELOCIDAD_AJUSTE_SUAVE = 12.2
VELOCIDAD_RECUPERACION = 11.9
VELOCIDAD_PARA_RECUPERAR_TIEMPO = 12.6

# Limites de frecuencia cardiaca para sus decisiones.
LIMITE_ALERTA_CORAZON = 170  # si pasa de aqui, baja el ritmo
LIMITE_CORAZON_RECUPERADO = 165  # hasta aqui debe bajar para retomar el plan
LIMITE_CORAZON_ALTO = 165  # si pasa de aqui, afloja un poco


class AgenteMetas:
    def __init__(self):
        self.velocidad = VELOCIDAD_INICIAL
        self.numero_alertas = 0
        self.en_alerta = False  # para contar cada alerta una sola vez

    def decidir(self, frecuencia_cardiaca, distancia, tiempo):
        # Si el corazon pasa del limite, baja el ritmo y no lo sube
        # hasta que se recupere (para no subir y bajar a cada rato).
        if frecuencia_cardiaca > LIMITE_ALERTA_CORAZON:
            self.velocidad = VELOCIDAD_RECUPERACION
            if not self.en_alerta:
                self.numero_alertas += 1
                self.en_alerta = True
            return "baja el ritmo"
        if self.en_alerta:
            if frecuencia_cardiaca < LIMITE_CORAZON_RECUPERADO:
                self.en_alerta = False
            else:
                self.velocidad = VELOCIDAD_RECUPERACION
                return "baja el ritmo"

        # Si va tarde respecto a su plan, acelera para recuperar.
        tiempo_esperado = distancia * RITMO_PLAN_SEGUNDOS_POR_KILOMETRO
        if tiempo > tiempo_esperado + TOLERANCIA_RETRASO_SEGUNDOS:
            self.velocidad = VELOCIDAD_PARA_RECUPERAR_TIEMPO
            return "acelera para recuperar"

        # Si el corazon va alto aunque vaya a tiempo, afloja un poco.
        if frecuencia_cardiaca > LIMITE_CORAZON_ALTO:
            self.velocidad = VELOCIDAD_AJUSTE_SUAVE
            return "afloja un poco"

        # Si todo va bien, sigue el ritmo del plan.
        self.velocidad = VELOCIDAD_RITMO_PLAN
        return "mantiene el ritmo"
