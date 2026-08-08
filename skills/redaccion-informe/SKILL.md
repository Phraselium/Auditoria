---
name: redaccion-informe
description: Determina el tipo de opinión y redacta el informe conforme a los modelos vigentes de 2026.
when_to_use: 'Úsala cuando haya que decidir el tipo de opinión, redactar o revisar el informe, o comprobar si una incidencia tiene efecto en la opinión. Términos: determina, opinión, decisión, naturaleza, generalización, efecto, redacta, informe, auditoría, modelos, vigentes, resolución, sección, relativa.'
argument-hint: '[carpeta-del-encargo]'
---

# Redacción del informe

> **Al invocarla, empieza por aquí.** Presenta en pantalla, en tres
> líneas y antes de hacer nada:
>
> 1. **Qué necesito:** el sumario de incorrecciones, las conclusiones de cierre y las cuentas anuales definitivas.
> 2. **Qué vas a recibir:** el informe con la sección del Impuesto sobre Sociedades y la verificación 9.1 previa a la firma.
> 3. **El comando exacto** que voy a ejecutar, con las rutas reales.
>
> Si falta algo de lo anterior, pídelo y **no lo inventes**.

## Cuándo se dispara

- Cerrada la evaluación de incorrecciones y hay que decidir la opinión.
- Aparece una incidencia y el auditor pregunta si tiene efecto en el informe.
- Hay que redactar una salvedad, un énfasis o una sección de incertidumbre.
- Antes de la firma, para la verificación final.

## Inputs

`encargo.json` con materialidad vigente, sumario de incorrecciones, conclusiones
de `empresa-en-funcionamiento`, `hechos-posteriores` y `partes-vinculadas`, y las
cuentas anuales **definitivas**.

## 1. Árbol de decisión del tipo de opinión

Dos ejes. Se cruzan; no se decide "a ojo".

| | Efecto **material pero NO generalizado** | Efecto **material Y generalizado** |
|---|---|---|
| **Incorrección material** (las CCAA están mal) | Opinión **con salvedades** | Opinión **desfavorable** |
| **Limitación al alcance** (no se ha podido obtener evidencia) | Opinión **con salvedades** | Opinión **denegada** |

**Generalizado** significa que el efecto: (a) no se limita a elementos o partidas
concretas; (b) si se limitara, representa o podría representar una parte
sustancial de las cuentas; o (c) en el caso de los desgloses, es fundamental para
que los usuarios comprendan las cuentas.

**Reglas de redacción que se aplican automáticamente:**

- «excepto por **los efectos**» → incorrección material (el efecto es conocido).
- «excepto por **los posibles efectos**» → limitación al alcance (no se ha podido
  determinar).
- Opinión denegada → el párrafo abre con «**Se nos ha contratado para auditar**»,
  nunca con «Hemos auditado».
- La salvedad **se cuantifica siempre que sea posible**. Si no lo es, hay que
  **explicar por qué**. Una salvedad sin cifra y sin explicación de la
  imposibilidad es una incidencia de inspección segura (`CAL-063`).

## 2. Empresa en funcionamiento

| Situación | Efecto en el informe |
|---|---|
| Incertidumbre material **con** desglose adecuado en memoria | Sección «Incertidumbre material relacionada con la empresa en funcionamiento». **Opinión NO modificada** |
| Incertidumbre material **sin** desglose adecuado | Opinión con salvedades o desfavorable, según la generalización |
| Uso del principio de empresa en funcionamiento **no adecuado** | Opinión **desfavorable** |
| No se ha podido obtener evidencia sobre la valoración de la dirección | Opinión **denegada** |

## 3. Párrafo de énfasis vs. salvedad

El énfasis **solo cabe sobre información ya recogida en las cuentas anuales**. Si
la información no está, no procede un énfasis: procede una salvedad. Confundir
las dos cosas es el error más frecuente en informes de despachos pequeños.

## 4. Sección relativa al Impuesto sobre Sociedades ⭐

> **No trata de la contabilización del impuesto.** Responde a la **disposición
> adicional undécima de la LAC** (Ley 28/2022, transposición del art. 48 *ter* de
> la Directiva 2013/34/UE): el informe público de **transparencia fiscal país por
> país**, exigible a matrices últimas con **cifra de negocios consolidada > 750
> M€** en los dos últimos ejercicios consecutivos.

**Procedimiento (papel 9.1):**

1. Obtener la cifra de negocios consolidada del grupo de los dos ejercicios
   anteriores. **Si no hay grupo, la variante es automáticamente «no obligada».**
2. Si supera 750 M€ en ambos: comprobar la publicación en el Registro Mercantil y
   en la web de la entidad, dejando constancia de fecha y URL consultada.
3. La declaración del informe **no puede emitirse sin este papel**.

Las tres variantes de redacción están en
`plantillas/informe-auditoria.md` § B.1.

**Aplicación:** cuentas anuales de ejercicios iniciados **desde el 22/06/2025**,
aunque el encargo se contratara antes. Es una puerta distinta de la del resto de
modificaciones del bloque de informe (encargos contratados desde el 01/01/2026).

## 5. Otra información: informe de gestión (NIA-ES 720R)

Ejecuta `comparador-documental` en su modalidad informe de gestión ↔ CCAA. Si hay
incongruencia material y no se corrige, **debe describirse** en la sección «Otra
información».

## 6. Cuestiones clave de la auditoría

Obligatorias para EIP. En el resto de encargos son voluntarias: **no las incluyas
por defecto** en un encargo PYME. Añaden riesgo de inconsistencia con el archivo
sin aportar valor al usuario de unas cuentas abreviadas.

## 7. Verificación final — BLOQUEANTE

```bash
audita comparar --informe 02-documentos/informe.json \
    --ccaa-definitivas 00-fuentes/ccaa_definitivas.json \
    --papel "01-papeles/9.1 Verificacion previa a la firma.xlsx"
```

Contrasta denominación social, NIF, ejercicio, fecha de cierre, marco, modelo,
fecha de formulación y las cifras clave. **Cualquier discrepancia es bloqueante:
no se firma.**

## Outputs

- `02-documentos/Informe de auditoria <cliente> <ejercicio>.docx|md`
- `01-papeles/9.1 Verificacion previa a la firma.xlsx`
- Registro en `encargo.json` del tipo de opinión, la variante del apartado del
  impuesto y las secciones incluidas, del que se alimenta `revision-de-calidad`.

## Checklist de autoverificación

- [ ] El tipo de opinión sale del **árbol de decisión**, no de la costumbre.
- [ ] El sumario de incorrecciones no corregidas se ha contrastado contra la
      materialidad global antes de proponer opinión favorable.
- [ ] Cada salvedad está cuantificada o explica por qué no puede estarlo.
- [ ] Se usa «los efectos» / «los posibles efectos» según corresponda.
- [ ] **La sección B.1 del impuesto sobre sociedades está incluida**, con la
      variante correcta y su papel de soporte.
- [ ] Los párrafos marcados `[VERIFICAR-LITERAL-ICAC]` se han contrastado contra
      el PDF oficial del ICAC, o se ha advertido al socio de que están pendientes.
- [ ] Si hay incertidumbre de empresa en funcionamiento, la sección está incluida.
- [ ] Las cuestiones clave solo aparecen si el encargo es EIP o el socio las pide.
- [ ] La verificación `9.1` está ejecutada y **sin bloqueantes**.
- [ ] La fecha del informe **no es anterior** a la formulación ni a la obtención
      de la carta de manifestaciones.
- [ ] Constan nombre y nº de ROAC del firmante y de la sociedad de auditoría.
