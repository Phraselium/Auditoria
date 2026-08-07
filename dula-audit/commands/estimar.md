---
description: Flujo 2 — Perfil de complejidad, horas, honorarios y decisión go/no-go.
argument-hint: <ruta-del-balance> [ruta-del-diario]
---

Estima el encargo a partir de: $ARGUMENTS

Invoca `estimacion-encargo`. Secuencia:

1. Ingiere el balance (y el diario si está) y comprueba que los cuadres pasan.
   Sin cuadres, el recuento de cuentas y saldos no es fiable.
2. Extrae del balance los drivers cuantitativos.
3. Pregunta al socio **en una sola tanda** los drivers cualitativos que no se
   deducen del balance: automatización de la facturación, nº de leasings, nº de
   instrumentos de financiación, historial de respuesta del cliente, primer
   encargo, consolidación, EIP.
4. Calcula el perfil, las horas por área y categoría, el rango y el punto muerto.
5. Presenta el **informe de decisión go/no-go en una página**, con los tres
   factores que más encarecen y su palanca de abaratamiento.

Si no hay `shared/references/tarifas.json`, advierte expresamente de que los
honorarios salen `[PENDIENTE-CLIENTE]` y no los inventes.
