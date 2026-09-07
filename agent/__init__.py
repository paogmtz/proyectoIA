"""
Paquete `agent`: implementación modular de un agente inteligente de running.

Evolución planteada en clase:
    1) Reflejo simple      -> (pendiente) Umbral FC > 170 -> "baja el ritmo".
    2) Basado en modelos   -> (pendiente) Estado interno que simula el cuerpo.
    3) Basado en metas     -> (este avance) Planifica el ritmo km a km para
                              cumplir una meta antes de dar el primer paso.

El paquete está organizado para que los tipos 1 y 2 puedan añadirse más
adelante sin tocar lo que ya existe. Cada módulo tiene una única misión:

    physiology      : ecuaciones que describen el cuerpo (compartidas).
    course          : el recorrido de 10 km y su perfil de pendientes.
    sensor          : los sensores del agente (percepción del mundo).
    body            : el "cuerpo real" simulado que el agente percibe.
    internal_model  : el modelo mental que el agente mantiene del mundo.
    planner         : genera la estrategia de ritmo para cumplir la meta.
    goal_agent      : el propio agente basado en metas (cerebro).
    simulation      : monta el mundo + sensores + agente y simula la carrera.
"""