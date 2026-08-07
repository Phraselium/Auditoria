---
name: archivo-y-cierre
description: 'Ensambla el archivo final: índice, referencias cruzadas, conservación y registro de uso de IA.'
when_to_use: 'Úsala tras la firma del informe, para cerrar el archivo, o cuando haya que localizar documentación de un encargo anterior. Términos: ensambla, archivo, encargo, dentro, normativo, índice, completo, papeles, referencias, cruzadas, control, versiones, registro, conservarse.'
argument-hint: '[carpeta-del-encargo]'
---

# Archivo y cierre

> **Al invocarla, empieza por aquí.** Presenta en pantalla, en tres
> líneas y antes de hacer nada:
>
> 1. **Qué necesito:** el encargo con todas sus fases cerradas y el informe firmado.
> 2. **Qué vas a recibir:** papel 9.9 con el índice completo y el control de plazos de conservación.
> 3. **El comando exacto** que voy a ejecutar, con las rutas reales.
>
> Si falta algo de lo anterior, pídelo y **no lo inventes**.

## El plazo

El archivo debe ensamblarse **oportunamente tras la fecha del informe** (NIA-ES
230.14 y NIGC1-ES). El plazo de referencia habitual es de **60 días** desde la
fecha del informe. Pasado ese momento, **no se puede eliminar ni descartar
documentación** antes de que finalice el periodo de conservación, y toda
modificación posterior debe dejar constancia de:

- **Quién** la hizo y **cuándo**.
- **Qué** motivo la justifica.
- **Qué efecto** tiene sobre las conclusiones alcanzadas.

Modificar un papel de trabajo después del ensamblado sin dejar ese rastro es una
de las incidencias más graves que puede detectar una inspección.

## Contenido mínimo del archivo

| Sección | Contenido |
|---|---|
| `0.x` | Carta de encargo, aceptación, evaluación de independencia firmada por todo el equipo, comprobaciones de blanqueo |
| `1.x` | Entendimiento de la entidad, materialidad (todas sus versiones), mapa de riesgos, diseño de pruebas, PBC |
| `2.x` | Ingesta, cuadres, comparador documental, test de asientos |
| `A` a `N` | Papeles de área, cada uno con conclusión y riesgos vinculados |
| `8.x` | Sumario de incorrecciones, carta de manifestaciones firmada, comunicaciones |
| `9.x` | Informe firmado, verificación previa a la firma, revisión de calidad, revisión de calidad del encargo si procede |

Más: los **ficheros fuente** recibidos del cliente con su huella SHA-256, y el
`uso-ia.log`.

## Índice y referencias cruzadas

El índice se genera desde `encargo.json`: referencia, título, fichero, estado,
conclusión y riesgos cubiertos. Las referencias cruzadas conectan cada papel con
los riesgos que responde y con las incorrecciones que propone.

**El criterio de suficiencia** (NIA-ES 230.8): un auditor experimentado sin
conexión previa con el encargo debe poder entender, a partir del archivo y sin
preguntar nada, la naturaleza, momento y alcance de los procedimientos, sus
resultados, la evidencia obtenida, y las cuestiones significativas y las
conclusiones alcanzadas sobre ellas.

## Conservación

| Documentación | Plazo |
|---|---|
| Archivo del encargo | **5 años** desde la fecha del informe (art. 30 LAC) |
| Documentación de prevención del blanqueo | **10 años** |
| Documentación con datos personales | Mientras exista obligación legal de conservación; después, supresión (RGPD/LOPDGDD) |

## Seguridad y confidencialidad

La documentación del cliente está sujeta a **deber de secreto** (art. 31 LAC).
Requisitos prácticos, en la línea de la ISO/IEC 27001 en lo que aporta estructura
al sistema de calidad del despacho:

- Acceso restringido al equipo del encargo.
- Copia de seguridad **con restauración probada** — una copia que nunca se ha
  restaurado no es una copia.
- Cifrado del soporte cuando salga de las instalaciones del despacho.
- Registro de accesos en encargos sensibles.
- Procedimiento de supresión al vencer el plazo de conservación.

## Registro de asistencia por IA

`uso-ia.log` recoge, por cada ejecución: skill, versión del plugin, ficheros de
entrada **con su huella SHA-256**, salidas generadas, parámetros, conclusión y
**quién validó el resultado**. Lo exige el sistema de gestión de la calidad
(NIGC1-ES) y da estructura al uso responsable de IA en un servicio de interés
público (ISO/IEC 42001).

Se alimenta **solo** con ejecuciones lanzadas con `--encargo`. Antes de cerrar el
archivo:

```bash
dula validar <encargo> --listar    # ninguna debe quedar sin validar
```

`revision-de-calidad` en modo completo escribe la versión legible del registro en
`02-documentos/Registro de asistencia automatizada.txt`, que es la que se archiva.

## Outputs

- `01-papeles/9.9 Indice del archivo.xlsx`
- Archivo ensamblado y bloqueado.
- Registro de conservación con la fecha de vencimiento.

## Checklist de autoverificación

- [ ] Todos los papeles registrados en `encargo.json` están físicamente en el
      archivo.
- [ ] Todos los papeles tienen conclusión y riesgos vinculados.
- [ ] Los ficheros fuente están archivados con su huella.
- [ ] El informe firmado y la carta de manifestaciones firmada están incluidos.
- [ ] La revisión de calidad se ejecutó **sin bloqueantes** antes de la firma.
- [ ] El ensamblado se ha completado dentro del plazo desde la fecha del informe.
- [ ] Está registrada la fecha de vencimiento del periodo de conservación.
- [ ] `uso-ia.log` está completo, **sin ejecuciones pendientes de validar**, y su
      versión legible archivada en `02-documentos`.
