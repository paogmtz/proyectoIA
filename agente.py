# Agente basado en metas: recorrer 10 km en menos de 50 minutos.
# Solo puede hacer 3 acciones: acelerar, mantener el ritmo o bajar el ritmo.
# Decide con if/elif/else a partir de lo que percibe.

META_MINUTOS = 50
SEGUNDOS_POR_KILOMETRO_PLAN = 296  # referencia: 4:56 por km, un poco menos
# de 5 minutos para llegar a la meta con margen
LIMITE_FRECUENCIA_ALTA = 170

PASO_VELOCIDAD = 0.6  # lo que sube o baja la velocidad con cada accion
VELOCIDAD_MINIMA = 11.5  # para no bajar tanto que ya no alcance la meta
VELOCIDAD_MAXIMA = 13.0
VELOCIDAD_INICIAL = 12.4


class AgenteMetas:
    def __init__(self):
        self.velocidad = VELOCIDAD_INICIAL
        # Estado interno: lo que recuerda de la iteracion anterior.
        self.frecuencia_anterior = None
        self.tendencia = "estable"

    def decidir(self, frecuencia_cardiaca, distancia, tiempo):
        # Compara con la vez anterior para saber si va subiendo,
        # bajando o estable. Solo se guarda como estado interno.
        if self.frecuencia_anterior is None:
            self.tendencia = "estable"
        elif frecuencia_cardiaca > self.frecuencia_anterior:
            self.tendencia = "subiendo"
        elif frecuencia_cardiaca < self.frecuencia_anterior:
            self.tendencia = "bajando"
        else:
            self.tendencia = "estable"
        self.frecuencia_anterior = frecuencia_cardiaca

        # Si el corazon pasa del limite, baja el ritmo.
        if frecuencia_cardiaca > LIMITE_FRECUENCIA_ALTA:
            self.velocidad = max(
                VELOCIDAD_MINIMA, self.velocidad - PASO_VELOCIDAD
            )
            return "bajar el ritmo"

        # Si va retrasado respecto a su plan, acelera.
        tiempo_esperado = distancia * SEGUNDOS_POR_KILOMETRO_PLAN
        if tiempo > tiempo_esperado:
            self.velocidad = min(
                VELOCIDAD_MAXIMA, self.velocidad + PASO_VELOCIDAD
            )
            return "acelerar"

        # Si va bien, mantiene el ritmo.
        return "mantener el ritmo"
