---
description: Flujo 1 — Crea el encargo y arranca la aceptación y la independencia.
argument-hint: <cliente> <ejercicio> [PGC|PGC-PYMES|PGC-CONSOLIDADO]
---

Arranca un encargo nuevo: $ARGUMENTS

1. Crea la estructura de carpetas y el estado del encargo:

```bash
dula nuevo "<ruta-base>/<CLIENTE>/<EJERCICIO>" "<CLIENTE>" <EJERCICIO> --marco <MARCO>
```

2. Invoca la skill `estimacion-y-aceptacion` y sigue sus dos procedimientos:
   `estimacion-encargo` (perfil, horas y honorarios) y
   `aceptacion-e-independencia` (amenazas, incompatibilidades, prevención del
   blanqueo, competencia y recursos, y comunicación con el auditor predecesor si
   es primer encargo). La decisión de aceptación y la de precio se toman juntas.

3. Genera la declaración de independencia y la carta de encargo adaptada.

**No avances a planificación** hasta que la fase de aceptación esté marcada como
`completa` en `encargo.json`.
