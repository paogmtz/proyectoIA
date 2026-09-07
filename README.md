# proyectoIA — Agente de Running

Avance: un agente basado en metas que corre 10 km simulados en Python.

    python3 main.py

- `mundo.py`: tiempo, distancia y frecuencia cardiaca (simulados).
  El unico sensor es el de frecuencia cardiaca.
- `agente.py`: el agente. Su meta es recorrer 10 km en menos de 50 minutos.
  Solo puede acelerar, mantener el ritmo o bajar el ritmo.
- `main.py`: crea el mundo y el agente, repite percibir-decidir-avanzar
  hasta los 10 km y muestra el resultado cada minuto.