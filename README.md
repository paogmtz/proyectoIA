# proyectoIA — Agente de Running (avance: agente basado en metas)

Entrenador virtual que corre 10 km simulados. Todo es simulado en Python,
sin dependencias externas: el cuerpo, los sensores y el terreno son un
modelo, y el agente decide el ritmo segundo a segundo.

## Cómo correrlo

Desde la carpeta del proyecto:

    python3 main.py

El resultado es siempre el mismo (semilla fija) para poder presentarlo.

## Qué hace el agente

Meta: 10 km en menos de 50 minutos, FC <= 168 bpm y reserva >= 8%.

1. Antes de arrancar, planifica una estrategia de ritmo km a km adaptada
   a las cuestas del recorrido (`agent/planner.py`).
2. Durante la carrera percibe el sensor de frecuencia cardíaca y el GPS,
   actualiza su modelo interno y regula la velocidad (`agent/goal_agent.py`).
3. Al cerrar cada kilómetro compara plan vs realidad y, si la meta peligra,
   corrige el ritmo objetivo de lo que falta.
4. Al final reporta estrategia, parciales, resumen y veredicto de la meta.

## Estructura del código

    main.py                 Punto de entrada (corre la simulación y la muestra).
    agent/physiology.py     Ecuaciones del cuerpo (FC, energía). Las usan tanto
                            el cuerpo real simulado como el modelo del agente.
    agent/course.py         Recorrido de 10 km con su perfil de pendientes.
    agent/sensor.py         Sensores: frecuencia cardíaca (con ruido) y GPS.
    agent/body.py           El "cuerpo real" simulado que el agente percibe.
    agent/internal_model.py Modelo interno del agente (predice y proyecta).
    agent/planner.py        Planificador: estrategia de ritmo antes de arrancar.
    agent/goal_agent.py     El agente basado en metas (percibe/decide/actúa).
    agent/simulation.py     Bucle percibir -> decidir -> avanzar, y el reporte.

## Siguientes pasos del proyecto

- `agent/simple_reflex.py` (pendiente): regla de umbral FC > 170.
- `agent/model_based.py` (pendiente): estado interno con fatiga y terreno.
- Comparar los tres tipos de agente sobre la misma carrera simulada.