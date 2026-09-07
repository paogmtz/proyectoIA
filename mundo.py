# Mundo simulado: el cuerpo del corredor, el terreno y los sensores.
# Todo son reglas simples con if/else, no hay formulas.

# Terreno de cada kilometro: 0 = plano, 1 = subida, -1 = bajada.
TERRENO = [0, 1, 1, -1, 0, 1, 0, -1, 0, 0]


class Mundo:
    def __init__(self):
        self.tiempo = 0      # segundos de carrera
        self.distancia = 0.0  # km recorridos
        self.fc = 150        # pulsaciones (empieza trotando suave)
        self.fc_max = 150

    def pendiente(self):
        km = int(self.distancia)
        if km >= 10:
            return 0
        return TERRENO[km]

    # Sensores: lo unico que el agente puede "ver" del mundo.
    def sensor_fc(self):
        return self.fc

    def sensor_distancia(self):
        return self.distancia

    # Avanza un segundo con la velocidad que pide el agente.
    def avanzar(self, velocidad):
        self.tiempo += 1
        self.distancia += velocidad / 3600

        # El cuerpo reacciona a la velocidad: ir rapido sube las
        # pulsaciones e ir lento las baja.
        if self.tiempo % 2 == 0:
            if velocidad > 12.2:
                self.fc += 1
            elif velocidad < 12.2:
                self.fc -= 1

        # El terreno tambien afecta: la subida cuesta y la bajada recupera.
        if self.tiempo % 4 == 0:
            if self.pendiente() > 0:
                self.fc += 1
            elif self.pendiente() < 0:
                self.fc -= 1

        if self.fc > 185:
            self.fc = 185
        if self.fc < 60:
            self.fc = 60
        if self.fc > self.fc_max:
            self.fc_max = self.fc
