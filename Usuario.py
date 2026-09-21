class Usuario:
    def __init__(self, nombre, edad, nivel, condicion):
        self.nombre = nombre
        self.edad = edad
    
        niveles_validos = ['principiante', 'intermedio', 'experto']
        condiciones_validas = ['ninguna', 'hipertension', 'asma']
        if nivel.lower() in niveles_validos:
            self.nivel = nivel.lower()
        else:
            raise ValueError(f"Nivel inválido. Debe pertenecer a la siguientes opciones: {niveles_validos}")

        if condicion.lower() in condiciones_validas:
            self.condicion = condicion.lower()
        else:
            raise ValueError(f"Condición inválida. Debe de ser una de las siguientes: {condiciones_validas}")

        self.fc_maxima = self.calcular_fc_maxima()
        self.factor_nivel = self.obtener_factor_nivel()
        self.factor_condicion = self.obtener_factor_condicion()
        self.fc_objetivo = self.calcular_fc_objetivo()

    def calcular_fc_maxima(self):
        #fórmula de tanaka
        return 208 - (0.7 * self.edad)

    def obtener_factor_nivel(self):
        #factor por nivel
        if self.nivel == 'principiante':
            return 0.65  
        elif self.nivel == 'intermedio':
            return 0.75  
        elif self.nivel == 'experto':
            return 0.85  
        return 0.65 

    def obtener_factor_condicion(self):
        #los factores son aproximados médicos
        if self.condicion == 'hipertension':
            return 0.85  
        elif self.condicion == 'asma':
            return 0.90  
        else: # 'ninguna'
            return 1.0   # Sin reducción

    def calcular_fc_objetivo(self):
        #FC con base a los factores obtenidos arriba
        intensidad_final = self.factor_nivel * self.factor_condicion
        return self.fc_maxima * intensidad_final

    def evaluar_esfuerzo(self, fc_actual):
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

    def mostrar_perfil(self):
        print(f"--- Perfil de {self.nombre} ---")
        print(f"Edad: {self.edad} años")
        print(f"Nivel Físico: {self.nivel.capitalize()}")
        print(f"Condición Médica: {self.condicion.capitalize()}")
        print(f"FC Máxima: {self.fc_maxima:.1f} lpm")
        print(f"FC Objetivo Recomendada: {self.fc_objetivo:.1f} lpm")

