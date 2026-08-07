# Modelo de informe de auditoría de cuentas anuales

> **Versión normativa: NIA-ES 700 (Revisada), 705 (Revisada), 706 (Revisada), 570
> (Revisada), 720 (Revisada), 510, 600 (Revisada) y 710, según la redacción dada
> por la Resolución del ICAC de 22 de enero de 2026 (BOE-A-2026-2234, BOE de
> 30/01/2026).**
>
> **Reglas de aplicación — son dos puertas distintas, no una:**
>
> | Elemento | Se aplica a |
> |---|---|
> | Apartado sobre el impuesto sobre sociedades (§ B.1) | Cuentas anuales de ejercicios iniciados **desde el 22/06/2025**, aunque el encargo se contratara antes |
> | Resto de modificaciones del bloque de informe | Encargos **contratados o iniciados desde el 01/01/2026**, con independencia del ejercicio auditado |
>
> Ante solapamiento dudoso, `redaccion-informe` selecciona el modelo **más
> completo** y lo deja documentado como `[JUICIO-AUDITOR]`.
>
> ⚠️ `[VERIFICAR-LITERAL-ICAC]` — El texto de los párrafos marcados con esta
> etiqueta reproduce el contenido y la estructura exigidos, pero **no ha podido
> contrastarse carácter a carácter contra el PDF oficial del ICAC** (dominio no
> accesible desde el entorno de generación). **Contrástelo una vez antes del
> primer uso real** y elimine la marca. El resto del modelo no lleva la etiqueta.

---

## Estructura del informe

```
INFORME DE AUDITORÍA DE CUENTAS ANUALES EMITIDO POR UN AUDITOR INDEPENDIENTE

A los [socios / accionistas] de [DENOMINACIÓN SOCIAL COMPLETA]:

A. INFORME SOBRE LAS CUENTAS ANUALES
   A.1  Opinión [/ Opinión con salvedades / Opinión desfavorable / Opinión denegada]
   A.2  Fundamento de la opinión [/ Fundamento de la opinión con salvedades ...]
   A.3  [Incertidumbre material relacionada con la empresa en funcionamiento]   ← si procede
   A.4  [Cuestiones clave de la auditoría]                                      ← EIP; voluntario en el resto
   A.5  [Párrafo de énfasis]                                                    ← si procede
   A.6  [Otras cuestiones]                                                      ← si procede
   A.7  Otra información: informe de gestión                                    ← si existe
   A.8  Responsabilidad de los administradores en relación con las cuentas anuales
   A.9  Responsabilidades del auditor en relación con la auditoría de las cuentas anuales

B. INFORME SOBRE OTROS REQUERIMIENTOS LEGALES Y REGLAMENTARIOS
   B.1  Informe relativo al impuesto sobre sociedades o impuestos de naturaleza
        idéntica o análoga                                                      ← OBLIGATORIO desde 2026
   B.2  [Informe adicional para la comisión de auditoría]                       ← EIP
   B.3  [Periodo de contratación]                                               ← EIP
   B.4  [Servicios prestados distintos de los de auditoría]                     ← EIP

[Firma] — [Nombre y apellidos], inscrito en el ROAC con el nº [XXXXX]
[Denominación de la sociedad de auditoría], inscrita en el ROAC con el nº [SXXXX]
[Localidad], a [fecha del informe]
```

---

## A.1 — Opinión

### Opinión favorable (no modificada)

> **Opinión**
>
> Hemos auditado las cuentas anuales de **[DENOMINACIÓN SOCIAL]** (la Sociedad),
> que comprenden el balance a **[fecha de cierre]**, la cuenta de pérdidas y
> ganancias, el estado de cambios en el patrimonio neto, [el estado de flujos de
> efectivo] y la memoria correspondientes al ejercicio terminado en dicha fecha.
>
> En nuestra opinión, las cuentas anuales adjuntas expresan, en todos los
> aspectos significativos, la imagen fiel del patrimonio y de la situación
> financiera de la Sociedad a **[fecha de cierre]**, así como de sus resultados
> [y flujos de efectivo] correspondientes al ejercicio terminado en dicha fecha,
> de conformidad con el marco normativo de información financiera que resulta de
> aplicación (que se identifica en la nota **[X]** de la memoria) y, en
> particular, con los principios y criterios contables contenidos en el mismo.

### Opinión con salvedades

> **Opinión con salvedades**
>
> Hemos auditado las cuentas anuales de **[DENOMINACIÓN SOCIAL]** (la Sociedad),
> que comprenden [...].
>
> En nuestra opinión, **excepto por los efectos de la cuestión descrita** /
> **excepto por los posibles efectos de la cuestión descrita** en la sección
> «Fundamento de la opinión con salvedades» de nuestro informe, las cuentas
> anuales adjuntas expresan, en todos los aspectos significativos, la imagen fiel
> [...].

*Se usa «los efectos» cuando la salvedad procede de una incorrección material
(el efecto es conocido) y «los posibles efectos» cuando procede de una limitación
al alcance (el efecto no se ha podido determinar).*

### Opinión desfavorable

> **Opinión desfavorable**
>
> [...] En nuestra opinión, **debido a la significatividad de la cuestión
> descrita** en la sección «Fundamento de la opinión desfavorable», las cuentas
> anuales adjuntas **no expresan** la imagen fiel del patrimonio y de la
> situación financiera de la Sociedad a [fecha], ni de sus resultados [y flujos
> de efectivo] correspondientes al ejercicio terminado en dicha fecha, de
> conformidad con el marco normativo de información financiera que resulta de
> aplicación.

### Opinión denegada (abstención)

> **Opinión denegada**
>
> Se nos ha contratado para auditar las cuentas anuales de **[DENOMINACIÓN
> SOCIAL]**, que comprenden [...].
>
> **No expresamos una opinión** sobre las cuentas anuales adjuntas de la
> Sociedad. Debido a la muy significativa importancia de la cuestión descrita en
> la sección «Fundamento de la opinión denegada» de nuestro informe, **no hemos
> podido obtener evidencia de auditoría que proporcione una base suficiente y
> adecuada para expresar una opinión** de auditoría sobre estas cuentas anuales.

**Nota:** en la opinión denegada el párrafo abre con «Se nos ha contratado para
auditar», nunca con «Hemos auditado».

---

## A.2 — Fundamento de la opinión

### Fundamento de la opinión (favorable)

> **Fundamento de la opinión**
>
> Hemos llevado a cabo nuestra auditoría de conformidad con la normativa
> reguladora de la actividad de auditoría de cuentas vigente en España. Nuestras
> responsabilidades de acuerdo con dichas normas se describen más adelante en la
> sección «Responsabilidades del auditor en relación con la auditoría de las
> cuentas anuales» de nuestro informe.
>
> Somos independientes de la Sociedad de conformidad con los requerimientos de
> ética, incluidos los de independencia, que son aplicables a nuestra auditoría
> de las cuentas anuales en España según lo exigido por la normativa reguladora
> de la actividad de auditoría de cuentas. En este sentido, no hemos prestado
> servicios distintos a los de la auditoría de cuentas ni han concurrido
> situaciones o circunstancias que, de acuerdo con lo establecido en la citada
> normativa reguladora, hayan afectado a la necesaria independencia de modo que
> se haya visto comprometida.
>
> Consideramos que la evidencia de auditoría que hemos obtenido proporciona una
> base suficiente y adecuada para nuestra opinión.

### Fundamento de la opinión con salvedades — por incorrección material

> **Fundamento de la opinión con salvedades**
>
> **[Descripción precisa del hecho, con su cuantificación.]** Ejemplo:
>
> La Sociedad mantiene registrado en el epígrafe «Deudores comerciales y otras
> cuentas a cobrar» del balance a [fecha] un saldo de **[importe]** euros
> correspondiente a **[descripción]**, cuya antigüedad supera los [X] meses y
> respecto del cual no se ha registrado corrección valorativa alguna. De acuerdo
> con el marco normativo de información financiera aplicable, debería haberse
> reconocido un deterioro por importe de **[importe]** euros. En consecuencia,
> el epígrafe «Deudores comerciales y otras cuentas a cobrar» del activo
> corriente y el patrimonio neto se encuentran sobrevalorados en **[importe]**
> euros, y el resultado del ejercicio antes de impuestos se encuentra
> sobrevalorado en **[importe]** euros.
>
> Hemos llevado a cabo nuestra auditoría de conformidad con la normativa
> reguladora de la actividad de auditoría de cuentas vigente en España. [...
> resto igual que en el fundamento de opinión favorable ...]
>
> Consideramos que la evidencia de auditoría que hemos obtenido proporciona una
> base suficiente y adecuada para nuestra opinión con salvedades.

### Fundamento de la opinión con salvedades — por limitación al alcance

> No hemos podido asistir al recuento físico de existencias a [fecha], por
> haberse producido nuestro nombramiento con posterioridad a dicha fecha. No ha
> sido posible verificar por medios alternativos las cantidades en existencias,
> que figuran registradas en el balance por importe de **[importe]** euros. En
> consecuencia, no hemos podido determinar si era necesario practicar algún
> ajuste sobre dicho importe, ni sobre el resultado del ejercicio.

**Regla de redacción:** la salvedad se cuantifica **siempre** que sea posible. Si
no lo es, hay que **explicar por qué** no lo es. Un informe con salvedad sin
cifra y sin explicación de la imposibilidad es una incidencia de inspección.

---

## A.3 — Incertidumbre material relacionada con la empresa en funcionamiento

*Cuando existe incertidumbre material pero el desglose de la memoria es adecuado,
la opinión NO se modifica: se incluye esta sección separada.*

> **Incertidumbre material relacionada con la empresa en funcionamiento**
>
> Llamamos la atención sobre la nota **[X]** de la memoria adjunta, en la que se
> indica que **[descripción del hecho: pérdidas acumuladas, patrimonio neto
> negativo, incumplimiento de covenants, fondo de maniobra negativo...]**. Estas
> condiciones, junto con **[otros factores]**, indican la existencia de una
> incertidumbre material que puede generar dudas significativas sobre la
> capacidad de la Sociedad para continuar como empresa en funcionamiento.
> Nuestra opinión no ha sido modificada en relación con esta cuestión.

*Si el desglose NO es adecuado, la incertidumbre se convierte en salvedad
(opinión con salvedades o desfavorable). Si el uso del principio de empresa en
funcionamiento no es adecuado, la opinión es desfavorable.*

---

## A.5 — Párrafo de énfasis

> **Párrafo de énfasis**
>
> Llamamos la atención sobre la nota **[X]** de la memoria adjunta, en la que se
> describe **[la cuestión]**. Nuestra opinión no ha sido modificada en relación
> con esta cuestión.

*El énfasis solo cabe sobre información **ya recogida** en las cuentas anuales.
Si la información no está, no procede un énfasis: procede una salvedad.*

---

## A.7 — Otra información: informe de gestión

> **Otra información: informe de gestión**
>
> La otra información comprende exclusivamente el informe de gestión del
> ejercicio **[X]**, cuya formulación es responsabilidad de los administradores
> de la Sociedad y no forma parte integrante de las cuentas anuales.
>
> Nuestra opinión de auditoría sobre las cuentas anuales no cubre el informe de
> gestión. Nuestra responsabilidad sobre el informe de gestión, de conformidad
> con lo exigido por la normativa reguladora de la actividad de auditoría de
> cuentas, consiste en evaluar e informar sobre la concordancia del informe de
> gestión con las cuentas anuales, a partir del conocimiento de la entidad
> obtenido en la realización de la auditoría de las citadas cuentas y sin incluir
> información distinta de la obtenida como evidencia durante la misma. Asimismo,
> nuestra responsabilidad consiste en evaluar e informar de si el contenido y
> presentación del informe de gestión son conformes a la normativa que resulta de
> aplicación. Si, basándonos en el trabajo que hemos realizado, concluimos que
> existen incorrecciones materiales, estamos obligados a informar de ello.
>
> Sobre la base del trabajo realizado, según lo descrito en el párrafo anterior,
> la información que contiene el informe de gestión concuerda con la de las
> cuentas anuales del ejercicio **[X]** y su contenido y presentación son
> conformes a la normativa que resulta de aplicación.

---

## A.8 — Responsabilidad de los administradores

> **Responsabilidad de los administradores en relación con las cuentas anuales**
>
> Los administradores son responsables de formular las cuentas anuales adjuntas,
> de forma que expresen la imagen fiel del patrimonio, de la situación financiera
> y de los resultados de la Sociedad, de conformidad con el marco normativo de
> información financiera aplicable a la entidad en España, y del control interno
> que consideren necesario para permitir la preparación de cuentas anuales libres
> de incorrección material, debida a fraude o error.
>
> En la preparación de las cuentas anuales, los administradores son responsables
> de la valoración de la capacidad de la Sociedad para continuar como empresa en
> funcionamiento, revelando, según corresponda, las cuestiones relacionadas con
> la empresa en funcionamiento y utilizando el principio contable de empresa en
> funcionamiento excepto si los administradores tienen intención de liquidar la
> Sociedad o de cesar sus operaciones, o bien no exista otra alternativa
> realista.

---

## A.9 — Responsabilidades del auditor

> **Responsabilidades del auditor en relación con la auditoría de las cuentas anuales**
>
> Nuestros objetivos son obtener una seguridad razonable de que las cuentas
> anuales en su conjunto están libres de incorrección material, debida a fraude o
> error, y emitir un informe de auditoría que contiene nuestra opinión.
>
> Seguridad razonable es un alto grado de seguridad pero no garantiza que una
> auditoría realizada de conformidad con la normativa reguladora de la actividad
> de auditoría de cuentas vigente en España siempre detecte una incorrección
> material cuando existe. Las incorrecciones pueden deberse a fraude o error y se
> consideran materiales si, individualmente o de forma agregada, puede preverse
> razonablemente que influyan en las decisiones económicas que los usuarios toman
> basándose en las cuentas anuales.
>
> En el Anexo de este informe de auditoría se incluye una descripción más
> detallada de nuestras responsabilidades en relación con la auditoría de las
> cuentas anuales. Esta descripción, que se encuentra en la(s) página(s)
> **[X-Y]**, forma parte integrante de nuestro informe de auditoría.

---

## B.1 — Informe relativo al impuesto sobre sociedades ⭐ NUEVO (2026)

> ### 🔴 Lo que esta sección **no** es
>
> **No trata de la contabilización del impuesto sobre beneficios.** No tiene
> relación con la conciliación entre el resultado contable y la base imponible,
> con los activos y pasivos por impuesto diferido ni con las contingencias
> fiscales. Todo eso sigue en el área J (`area-fiscal`) y en la nota de situación
> fiscal de la memoria.
>
> Esta sección responde a la **disposición adicional undécima de la LAC**,
> introducida por la **Ley 28/2022** para transponer el art. 48 *ter* de la
> Directiva 2013/34/UE (redacción de la Directiva (UE) 2021/2101): el **informe
> público de transparencia fiscal país por país**.
>
> **Umbral:** sociedades matrices últimas cuya **cifra de negocios consolidada
> haya superado 750 millones de euros en cada uno de los dos últimos ejercicios
> consecutivos** (y determinadas filiales y sucursales de grupos extracomunitarios).
>
> **Consecuencia práctica para Dula Auditores:** en la práctica totalidad de la
> cartera del despacho el resultado será la **redacción de entidad NO obligada**.
> El plugin verifica el umbral automáticamente y solo eleva a `[JUICIO-AUDITOR]`
> cuando la cifra de negocios consolidada se aproxima al límite.

### Variante 1 — La entidad NO estaba obligada (caso general en Dula)

> **Informe relativo al impuesto sobre sociedades o impuestos de naturaleza
> idéntica o análoga**
>
> `[VERIFICAR-LITERAL-ICAC]`
>
> De acuerdo con lo previsto en la disposición adicional undécima de la Ley
> 22/2015, de 20 de julio, de Auditoría de Cuentas, informamos de que la Sociedad
> **no estaba obligada**, en el ejercicio inmediatamente anterior al que se
> refieren las cuentas anuales adjuntas, a publicar el informe relativo al
> impuesto sobre sociedades o impuestos de naturaleza idéntica o análoga a que se
> refiere dicha disposición.

### Variante 2 — La entidad estaba obligada y publicó el informe

> `[VERIFICAR-LITERAL-ICAC]`
>
> De acuerdo con lo previsto en la disposición adicional undécima de la Ley
> 22/2015, de 20 de julio, de Auditoría de Cuentas, informamos de que la Sociedad
> **estaba obligada** a publicar el informe relativo al impuesto sobre sociedades
> o impuestos de naturaleza idéntica o análoga correspondiente al ejercicio
> **[ejercicio anterior]**, y que dicho informe **ha sido publicado** en la forma
> prevista en la citada disposición.

### Variante 3 — La entidad estaba obligada y NO publicó el informe

> `[VERIFICAR-LITERAL-ICAC]`
>
> De acuerdo con lo previsto en la disposición adicional undécima de la Ley
> 22/2015, de 20 de julio, de Auditoría de Cuentas, informamos de que la Sociedad
> **estaba obligada** a publicar el informe relativo al impuesto sobre sociedades
> o impuestos de naturaleza idéntica o análoga correspondiente al ejercicio
> **[ejercicio anterior]**, y que dicho informe **no ha sido publicado** en la
> forma prevista en la citada disposición.

**Procedimiento de verificación asociado (papel 9.1):**

1. Obtener la cifra de negocios consolidada del grupo de los dos ejercicios
   anteriores. Si no hay grupo, la sección es automáticamente la Variante 1.
2. Si supera 750 M€ en ambos, comprobar la publicación en el **Registro
   Mercantil** y en la **página web** de la entidad, y dejar constancia de la
   fecha y de la URL consultada.
3. La conclusión se documenta en el papel de trabajo con su traza. **La
   declaración del informe no puede emitirse sin este papel.**

---

## B.2 a B.4 — Secciones adicionales para EIP

> **Informe adicional para la comisión de auditoría**
>
> La opinión expresada en este informe es coherente con el contenido de nuestro
> informe adicional para la comisión de auditoría de la Sociedad de fecha
> **[fecha]**.
>
> **Periodo de contratación**
>
> La Junta General Ordinaria de Accionistas celebrada el **[fecha]** nos nombró
> como auditores de la Sociedad por un periodo de **[X]** años, contados a partir
> del ejercicio finalizado a **[fecha]**.
>
> Con anterioridad, fuimos designados por acuerdo de la Junta General para el
> periodo de **[X]** años y hemos venido realizando el trabajo de auditoría de
> cuentas de forma ininterrumpida desde el ejercicio **[X]**.
>
> **Servicios prestados**
>
> Los servicios distintos de la auditoría de cuentas que hemos prestado a la
> Sociedad **[y a sus entidades vinculadas]** se detallan en la nota **[X]** de la
> memoria adjunta.

---

## Firma

```
[FIRMA]

[NOMBRE Y APELLIDOS DEL AUDITOR FIRMANTE]
Inscrito en el ROAC con el nº [XXXXX]

[DENOMINACIÓN DE LA SOCIEDAD DE AUDITORÍA]
Inscrita en el ROAC con el nº [SXXXX]

[Localidad], a [día] de [mes] de [año]
```

---

## Lista de verificación antes de la firma

Ejecutada automáticamente por `comparador.informe_vs_ccaa_definitivas()` y
verificada de nuevo por `revision-de-calidad`. Cualquier discrepancia es
**BLOQUEANTE**: no se firma.

- [ ] Denominación social **exacta**, incluida la forma societaria.
- [ ] NIF correcto.
- [ ] Ejercicio y fecha de cierre coincidentes con las cuentas anuales definitivas.
- [ ] Estados que se citan = estados efectivamente formulados (¿hay ECPN? ¿hay EFE?).
- [ ] Marco de información financiera **identificado y coincidente** con la nota de bases de presentación.
- [ ] Cifras citadas en las salvedades = cifras de las cuentas definitivas.
- [ ] Nota de la memoria a la que remiten los párrafos existe y trata de lo que se dice.
- [ ] **Sección B.1 presente** (obligatoria para ejercicios iniciados desde el 22/06/2025).
- [ ] Fecha del informe **no anterior** a la fecha de formulación ni a la obtención de la carta de manifestaciones.
- [ ] Nombre y nº de ROAC del firmante y de la sociedad de auditoría.
- [ ] Anexo de responsabilidades del auditor adjunto y con las páginas correctamente referenciadas.
