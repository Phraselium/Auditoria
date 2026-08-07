---
description: Dónde está el encargo y cuál es el siguiente paso.
argument-hint: '[ruta-del-encargo]'
---

Estado del encargo: $ARGUMENTS

Invoca `estado-del-encargo`:

```bash
dula estado <carpeta-encargo>
```

Lee el estado de `encargo.json` y `uso-ia.log` —no de la memoria de la
conversación— y presenta fase, perfil, materialidad vigente, papeles concluidos y
pendientes, riesgos sin respuesta, excepciones por severidad, pendientes del
cliente ordenados por ruta crítica, desviación de horas y ejecuciones asistidas
sin validar.

Termina siempre con el **siguiente paso recomendado**, que debe ser una acción
concreta. Prioridad:

1. Excepciones bloqueantes → resolverlas.
2. Papel `2.1` sin concluir → los cuadres.
3. Pendientes de ruta crítica sin recibir → reclamarlos.
4. Riesgos sin respuesta → `diseno-de-pruebas`.
5. Áreas activas sin empezar → la de mayor saldo.
6. Todo cerrado → `/dula-audit:cerrar`.
