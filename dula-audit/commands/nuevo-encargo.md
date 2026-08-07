---
description: Crea la carpeta y el estado de un encargo nuevo, y arranca la fase de aceptación
argument-hint: <cliente> <ejercicio> [PGC|PGC-PYMES|PGC-CONSOLIDADO]
---

Arranca un encargo nuevo: $ARGUMENTS

1. Crea la estructura de carpetas y el estado del encargo:

```bash
export PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/shared/scripts
python3 -m dula.cli nuevo "<ruta-base>/<CLIENTE>/<EJERCICIO>" "<CLIENTE>" <EJERCICIO> --marco <MARCO>
```

2. Invoca `aceptacion-e-independencia` para evaluar amenazas, incompatibilidades,
   prevención del blanqueo, competencia y recursos, y comunicación con el auditor
   predecesor si es primer encargo.

3. Si aún no se ha fijado precio, invoca `estimacion-encargo` primero: la
   decisión de aceptación y la de precio se toman juntas.

4. Genera la declaración de independencia y la carta de encargo adaptada.

**No avances a planificación** hasta que la fase de aceptación esté marcada como
`completa` en `encargo.json`.
