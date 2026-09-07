# Agente basado en metas: quiere terminar 10 km en menos de 50 minutos.
# Detecta el entorno con sus sensores y decide solo con if/else.


class AgenteMetas:
    def __init__(self):
        self.meta_minutos = 50
        self.ritmo_plan = 300  # su plan: 5 minutos por km, en segundos
        self.velocidad = 12.0  # km/h que le pide al cuerpo
        self.alertas = 0
        self.en_alerta = False  # para contar cada alerta una sola vez

    def decidir(self, fc, distancia, tiempo):
        # Si el corazon pasa de 170, baja el ritmo y no lo sube
        # hasta que baje de 165 (para no subir y bajar a cada rato).
        if fc > 170:
            self.velocidad = 11.9
            if not self.en_alerta:
                self.alertas += 1
                self.en_alerta = True
            return "baja el ritmo"
        if self.en_alerta:
            if fc < 165:
                self.en_alerta = False
            else:
                self.velocidad = 11.9
                return "baja el ritmo"

        # Si va tarde respecto a su plan, acelera para recuperar.
        esperado = distancia * self.ritmo_plan
        if tiempo > esperado + 20:
            self.velocidad = 12.6
            return "acelera para recuperar"

        # Si el corazon va alto aunque vaya a tiempo, afloja un poco.
        if fc > 165:
            self.velocidad = 12.2
            return "afloja un poco"

        # Si todo va bien, sigue el ritmo del plan.
        self.velocidad = 12.4
        return "mantiene el ritmo"
