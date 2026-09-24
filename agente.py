# agente.py
class Usuario:
    def __init__(self, nombre: str, edad: int, nivel: str, condiciones: list):

        self.nombre = nombre
        self.edad = edad
        
        niveles_validos = ['principiante', 'intermedio', 'avanzado','experto']
        condiciones_validas = ['hipertension', 'asma']

        # Validación y normalización de nivel
        if nivel.lower() in niveles_validos:
            self.nivel = nivel.lower()
        else:
            raise ValueError(f"Nivel inválido. Debe pertenecer a: {niveles_validos}")

        # Normalización de condiciones médicas
        self.condiciones = [c.lower() for c in condiciones if c.lower() in condiciones_validas]

        # Cálculos de Frecuencia Cardíaca
        self.fc_maxima = self.calcular_fc_maxima()
        self.factor_nivel = self.obtener_factor_nivel()
        self.factor_condicion = self.obtener_factor_condicion()
        self.fc_objetivo = self.calcular_fc_objetivo()

        # Cálculo de Meta de Entrenamiento (Tiempo y Distancia)
        self.distancia_km, self.tiempo_min = self.calcular_meta_entrenamiento()

    def calcular_fc_maxima(self):
        # Fórmula de Tanaka
        return 208 - (0.7 * self.edad)

    def obtener_factor_nivel(self):
        if self.nivel == 'principiante':
            return 0.65  
        elif self.nivel == 'intermedio':
            return 0.75  
        elif self.nivel in ['avanzado', 'experto']:
            return 0.85  
        return 0.65

    def obtener_factor_condicion(self):
        # Si presenta ambas condiciones, los factores se combinan
        factor = 1.0
        if 'hipertension' in self.condiciones:
            factor *= 0.85
        if 'asma' in self.condiciones:
            factor *= 0.90
        return factor

    def calcular_fc_objetivo(self):
        intensidad_final = self.factor_nivel * self.factor_condicion
        return self.fc_maxima * intensidad_final

    def calcular_meta_entrenamiento(self):
        """
        Propone una meta razonable y segura de distancia (km) y tiempo (minutos)
        basándose en el nivel, la edad y las afecciones médicas del usuario.
        """
        # 1. Parámetros base según nivel (distancia y ritmo medio min/km)
        if self.nivel == 'principiante':
            distancia = 3.0
            ritmo_min_km = 8.0  # 8 min por km (caminata a paso ligero / trote suave)
        elif self.nivel == 'intermedio':
            distancia = 5.0
            ritmo_min_km = 6.5  # 6.5 min por km
        else:  # Avanzado / Experto
            distancia = 8.0
            ritmo_min_km = 5.5  # 5.5 min por km

        # 2. Ajuste por edad (> 50 años)
        if self.edad > 50:
            distancia *= 0.85

        # 3. Ajustes por condiciones médicas
        if 'asma' in self.condiciones:
            distancia *= 0.80     # Se reduce distancia para evitar hiperventilación
            ritmo_min_km += 1.0   # Ritmo más pausado

        if 'hipertension' in self.condiciones:
            ritmo_min_km += 0.5   # Se incrementa el tiempo estimado para mantener FC controlada

        tiempo_total = distancia * ritmo_min_km


        # Tres retos posibles respecto de la meta base.
        opciones = {
            "Conservador": 0.80,
            "Estándar": 1.00,
            "Ambicioso": 1.20,
        }

        # Cuánto penaliza el agente un reto más exigente.
        penalizacion = {
            "principiante": 6.0,
            "intermedio": 5.0,
            "avanzado": 4.0,
            "experto":4.0
        }[self.nivel]

        if self.edad > 50:
            penalizacion += 1.5

        penalizacion += 1.5 * len(self.condiciones)

        def utilidad(factor):
            beneficio = 10 * factor
            costo_exigencia = penalizacion * factor**2
            return beneficio - costo_exigencia

        self.reto_elegido, factor_elegido = max(
            opciones.items(),
            key=lambda opcion: utilidad(opcion[1])
        )

        return (
            round(distancia * factor_elegido, 1),
            round(tiempo_total * factor_elegido)
        )

    def evaluar_esfuerzo(self, fc_actual: float) -> str:
        """
        Evalúa las pulsaciones en tiempo real y devuelve la indicación correspondiente.
        """
        limite_peligro = self.fc_maxima * 0.85 
        margen_tolerancia = 5
        limite_inferior = self.fc_objetivo - margen_tolerancia
        limite_superior = self.fc_objetivo + margen_tolerancia

        if fc_actual > limite_peligro:
            return "ALERTA: Frecuencia cardíaca muy alta, frena INMEDIATAMENTE"
        if fc_actual < limite_inferior:
            return "Acelerar"
        elif fc_actual > limite_superior:
            return "Frenar"
        else:
            return "Mantenerse"
