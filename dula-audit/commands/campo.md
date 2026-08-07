---
description: Flujo 4 — Ejecuta un área de trabajo de campo con su programa escalado.
argument-hint: <área — p.ej. arrendamientos, inmovilizado, fiscal, tesoreria>
---

Ejecuta el área: $ARGUMENTS

1. Comprueba que el papel `2.1` está `concluido`. Si no lo está, **no continúes**.
2. Invoca la skill `area-<área>` correspondiente, que a su vez usa `area-runner`
   para la mecánica.
3. Carga el programa del perfil vigente desde
   `${CLAUDE_PLUGIN_ROOT}/shared/references/programas/<área>.md`.
4. Ejecuta todos los procedimientos del programa, o documenta por qué alguno no
   se ha ejecutado.
5. Genera el papel de trabajo en formato estándar y regístralo en `encargo.json`
   con sus riesgos vinculados.
6. Registra los ajustes propuestos como incorrecciones.
7. Presenta el resumen en pantalla: **máximo 15 líneas**, solo conclusión y
   excepciones.

Si aparece un hallazgo que invalide la simplificación del perfil (indicio de
fraude, incorrección material, deficiencia significativa de control, duda sobre
empresa en funcionamiento, limitación al alcance, covenant incumplido, operación
vinculada no declarada), invoca `escalado-del-encargo` **antes de cerrar el área**.
