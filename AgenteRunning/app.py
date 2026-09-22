import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow 
from PySide6.QtWidgets import QMessageBox,  QProgressBar, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from agente import Usuario
from mundo import Mundo

class AgenteRunningApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agente de Running Virtual")
        self.resize(400, 500)

        # Objeto usuario y mundo
        self.usuario = None
        self.mundo = None

        # Velocidad inicial del corredor kmh
        self.velocidad_actual = 10.0

        # Timer para la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_simulacion)
        self.intervalo_ms = 30

        # Stack de pantallas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Vistas
        self.stacked_widget.addWidget(self.crear_pagina_formulario())
        self.stacked_widget.addWidget(self.crear_pagina_reto())
        self.stacked_widget.addWidget(self.crear_pagina_carrera())
        self.stacked_widget.addWidget(self.crear_pagina_resumen())


    # Primera pantalla formulario
    def crear_pagina_formulario(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("Agente de Running Virtual")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 35px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        form = QFormLayout()

        self.txt_nombre = QLineEdit()
        self.txt_edad = QLineEdit()

        self.cmb_nivel = QComboBox()
        self.cmb_nivel.addItems(["Principiante", "Intermedio", "Avanzado"])

        self.cmb_condicion = QComboBox()
        self.cmb_condicion.addItems(["Ninguna", "Hipertensión", "Asma"])

        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("Edad:", self.txt_edad)
        form.addRow("Nivel de Experiencia:", self.cmb_nivel)
        form.addRow("Condición Médica:", self.cmb_condicion)

        layout.addLayout(form)

        # Checkbox de autorización
        self.chk_autorizacion = QCheckBox(
            "Autorizo el uso de mis datos de salud para el cálculo del reto y monitoreo."
        )
        layout.addWidget(self.chk_autorizacion)

        btn_generar = QPushButton("calcular meta")
        btn_generar.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 10px;")
        btn_generar.clicked.connect(self.procesar_formulario)
        layout.addWidget(btn_generar)

        return widget

    def procesar_formulario(self):
        # Validar campo de nombre
        nombre = self.txt_nombre.text().strip()
        if not nombre:
            nombre = "Atleta"

        # Validar edad
        try:
            edad = int(self.txt_edad.text())
            if edad <= 0 or edad > 100:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Error de Entrada", "ingresa una edad válida")
            return

        # Validar casilla de autorización
        if not self.chk_autorizacion.isChecked():
            QMessageBox.warning(
                self, "autorización requerida", "por tu seguridad necesitas tener autorización para entrenar")
            return

        nivel = self.cmb_nivel.currentText().lower()
        condicion_sel = self.cmb_condicion.currentText().lower()

        # Mapear condiciones para agente.py
        if condicion_sel == "hipertensión":
            condiciones = ["hipertension"]
        elif condicion_sel == "asma":
            condiciones = ["asma"]
        else:
            condiciones = []

        # Instanciar el agente Usuario
        try:
            self.usuario = Usuario(
                nombre=nombre,
                edad=edad,
                nivel=nivel,
                condiciones=condiciones,
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al crear usuario", str(e))
            return

        # Construir texto informativo para la vista del reto
        condicion_texto = (
            ", ".join(self.usuario.condiciones).capitalize()
            if self.usuario.condiciones
            else "Ninguna"
        )

        texto_reto = f"""
        <b>Atleta:</b> {self.usuario.nombre}<br>
        <b>Edad:</b> {self.usuario.edad} años<br>
        <b>Nivel:</b> {self.usuario.nivel.capitalize()}<br>
        <b>Condición Médica:</b> {condicion_texto}<br></span><br>
        <b>Meta Propuesta:</b></span><br>
        <b>Distancia:</b> {self.usuario.distancia_km:.1f} km<br>
        <b>Tiempo Estimado:</b> {self.usuario.tiempo_min} minutos
        """
        self.lbl_detalles_reto.setText(texto_reto)
        self.stacked_widget.setCurrentIndex(1)

    #reto calculado
    def crear_pagina_reto(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        # 1. Título sin margen inferior exagerado
        lbl_titulo = QLabel("Tu reto personalizado")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white;"
        )
        layout.addWidget(lbl_titulo)

        # 2. Detalles del reto sin fondo blanco y con letra más grande
        self.lbl_detalles_reto = QLabel("")
        self.lbl_detalles_reto.setAlignment(Qt.AlignCenter)
        self.lbl_detalles_reto.setStyleSheet(
            "font-size: 16px; color: white; background: transparent; padding: 10px;"
        )
        layout.addWidget(self.lbl_detalles_reto)

        # 3. Botones
        btn_iniciar = QPushButton("iniciar reto")
        btn_iniciar.setStyleSheet(
            "background-color: blue; color: white; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 5px;"
        )
        btn_iniciar.clicked.connect(self.iniciar_simulacion)
        layout.addWidget(btn_iniciar)

        btn_volver = QPushButton("Modificar Datos")
        btn_volver.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(btn_volver)

        return widget

    # Carrera en vivo
    def crear_pagina_carrera(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl_titulo = QLabel("entrenamiento en curso")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_titulo)

        self.lbl_indicacion_agente = QLabel("MANTENERSE")
        self.lbl_indicacion_agente.setAlignment(Qt.AlignCenter)
        self.lbl_indicacion_agente.setStyleSheet("font-size: 14px; background-color: coral; color: black; padding: 10px;")
        layout.addWidget(self.lbl_indicacion_agente)

        self.lbl_tiempo_restante = QLabel("Tiempo Restante: --:--")
        self.lbl_distancia_recorrida = QLabel("Distancia: 0.00 / 0.00 km")
        self.lbl_frecuencia_cardiaca = QLabel("Frecuencia Cardíaca: -- bpm")

        for lbl in [
            self.lbl_tiempo_restante,
            self.lbl_distancia_recorrida,
            self.lbl_frecuencia_cardiaca,
        ]:
            lbl.setStyleSheet(
                "font-size: 15px; color: #ffffff; font-weight: bold; margin-top: 5px;"
            )
            layout.addWidget(lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        return widget

    def iniciar_simulacion(self):
        self.mundo = Mundo(distancia_meta_km=self.usuario.distancia_km)
        self.velocidad_actual = 11.0
        self.progress_bar.setValue(0)
        self.stacked_widget.setCurrentIndex(2)
        self.timer.start(self.intervalo_ms)

    def actualizar_simulacion(self):
        fc_actual = self.mundo.sensor_frecuencia_cardiaca()

        # Evaluación en tiempo real por el agente
        indicacion = self.usuario.evaluar_esfuerzo(fc_actual)

        # Ajuste dinámico de velocidad según la indicación
        if "Acelerar" in indicacion:
            self.velocidad_actual = min(16.0, self.velocidad_actual + 0.2)
        elif "Frenar" in indicacion or "ALERTA" in indicacion:
            self.velocidad_actual = max(5.0, self.velocidad_actual - 0.4)

        # Avanzar la simulación del mundo
        self.mundo.avanzar(self.velocidad_actual)

        # Cálculos de interfaz
        distancia_meta = self.usuario.distancia_km
        tiempo_meta_seg = self.usuario.tiempo_min * 60

        porcentaje = min(
            100,
            int((self.mundo.distancia_kilometros / distancia_meta) * 100),
        )
        self.progress_bar.setValue(porcentaje)

        segundos_restantes = max(0, tiempo_meta_seg - self.mundo.tiempo_segundos)
        min_rest = segundos_restantes // 60
        seg_rest = segundos_restantes % 60

        # Cambiar color según la indicación
        if "ALERTA" in indicacion:
            bg_color = "#dc3545"
        elif "Acelerar" in indicacion:
            bg_color = "#ffc107"
        else:
            bg_color = "#28a745"

        self.lbl_indicacion_agente.setStyleSheet(f"""
            QLabel {{
                font-size: 16px; 
                font-weight: bold; 
                color: #ffffff; 
                background-color: {bg_color}; 
                border-radius: 10px; 
                padding: 15px;
            }}
        """)

        self.lbl_tiempo_restante.setText(
            f"Tiempo Restante: {min_rest:02d}:{seg_rest:02d}"
        )
        self.lbl_distancia_recorrida.setText(
            f"Distancia: {self.mundo.distancia_kilometros:.2f} / {distancia_meta:.2f} km"
        )
        self.lbl_frecuencia_cardiaca.setText(f"Frecuencia Cardíaca: {fc_actual} bpm")
        self.lbl_indicacion_agente.setText(f"{indicacion.upper()}")

        # Verificar si completó el reto o se acabó el tiempo
        if (
            self.mundo.distancia_kilometros >= distancia_meta
            or segundos_restantes <= 0
        ):
            self.finalizar_simulacion()

    def finalizar_simulacion(self):
        self.timer.stop()
        self.mostrar_resumen()

    #Página de término
    def crear_pagina_resumen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        self.lbl_resumen_titulo = QLabel("Sesión Finalizada")
        self.lbl_resumen_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_resumen_titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #28a745;"
        )
        layout.addWidget(self.lbl_resumen_titulo)

        self.lbl_resumen_detalles = QLabel("")
        self.lbl_resumen_detalles.setAlignment(Qt.AlignCenter)
        self.lbl_resumen_detalles.setStyleSheet("""
            QLabel {
                font-size: 14px; 
                background-color: #ffffff; 
                color: #1a1a1a; 
                border: 1px solid #cccccc; 
                border-radius: 8px; 
                padding: 15px;
            }
        """)
        layout.addWidget(self.lbl_resumen_detalles)

        btn_inicio = QPushButton("Volver al Inicio")
        btn_inicio.setStyleSheet(
            "background-color: #007bff; color: white; padding: 10px; border-radius: 5px;"
        )
        btn_inicio.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
        layout.addWidget(btn_inicio)

        return widget

    def mostrar_resumen(self):
        distancia = self.mundo.distancia_kilometros
        tiempo_seg = self.mundo.tiempo_segundos
        minutos = tiempo_seg // 60
        segundos = tiempo_seg % 60

        distancia_meta = self.usuario.distancia_km
        porcentaje_cumplido = min(100, (distancia / distancia_meta) * 100)
        meta_lograda = porcentaje_cumplido >= 100

        if meta_lograda:
            self.lbl_resumen_titulo.setText(
                f"Meta Cumplida"
            )
            self.lbl_resumen_titulo.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #28a745;"
            )
        else:
            self.lbl_resumen_titulo.setText(
                "Sesión finalizada"
            )
            self.lbl_resumen_titulo.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #dc3545;"
            )

        resumen_txt = f"""
        <b>Atleta:</b> {self.usuario.nombre}<br>
        <b>Porcentaje de la Sesión Completado:</b> {porcentaje_cumplido:.1f}%<br>
        <b>Distancia Recorrida:</b> {distancia:.2f} km de {distancia_meta:.2f} km<br>
        <b>Tiempo Utilizado:</b> {minutos:02d}:{segundos:02d} min<br>
        """
        self.lbl_resumen_detalles.setText(resumen_txt)
        self.stacked_widget.setCurrentIndex(3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgenteRunningApp()
    window.show()
    sys.exit(app.exec())