# Modelos de solicitud de confirmación externa (NIA-ES 505)

> **Regla común:** las solicitudes las envía **el auditor**, no el cliente, y las
> respuestas se reciben **directamente** en el despacho. Una confirmación que pasa
> por las manos del cliente no es evidencia externa.

---

## 1. Confirmación bancaria

> Se envía a **todas** las entidades con las que la entidad haya operado durante
> el ejercicio, **aunque cierren con saldo cero**. Es la única forma de probar la
> integridad del pasivo financiero.

**«ENTIDAD FINANCIERA»** — «Domicilio»

Muy señores nuestros:

En nuestra condición de auditores de **«DENOMINACIÓN»**, NIF «XXXXXXXXX», y
debidamente autorizados por la entidad —autorización que se adjunta—, les
solicitamos que nos remitan **directamente a nuestro despacho** la siguiente
información **referida a «fecha de cierre»**:

1. Saldos de **todas** las cuentas corrientes, de ahorro, a plazo y de cualquier
   otra naturaleza, con su numeración, divisa y titularidad.
2. **Personas autorizadas** a disponer de dichas cuentas y régimen de disposición.
3. **Préstamos y créditos** concedidos: importe inicial, capital pendiente, tipo,
   vencimiento, periodicidad, garantías y cuadro de amortización.
4. **Líneas de crédito, pólizas, confirming y factoring**: límite concedido,
   dispuesto, vencimiento y, en el factoring, si es **con o sin recurso**.
5. **Avales, garantías y afianzamientos** prestados por la entidad por cuenta del
   cliente, con su importe, beneficiario y vencimiento.
6. **Pignoraciones, prendas y cualquier limitación** a la disponibilidad de saldos
   o activos.
7. Efectos descontados pendientes de vencimiento y remesas en gestión de cobro.
8. Instrumentos financieros derivados contratados y su valor razonable.
9. Cualquier otro **riesgo, directo o indirecto**, vigente a la fecha indicada.

Rogamos nos indiquen expresamente si alguno de los apartados **no procede**, en
lugar de omitirlo.

Respuesta a: «dirección postal y correo electrónico del despacho».

---

## 2. Confirmación de saldos de clientes o proveedores

**«NOMBRE DEL TERCERO»** — «Domicilio»

Muy señores nuestros:

En relación con la auditoría de las cuentas anuales de **«DENOMINACIÓN»**,
correspondiente al ejercicio terminado el «fecha», les rogamos confirmen
**directamente a nuestro despacho** el saldo que mantenían con dicha entidad a la
citada fecha.

Según los registros contables de «DENOMINACIÓN», el saldo a su favor / a favor de
«DENOMINACIÓN» a «fecha de cierre» asciende a **«importe» euros**.

☐ **Conforme** con el saldo indicado.

☐ **No conforme.** El saldo según nuestros registros es de __________ euros.
  Detalle de las diferencias (facturas, abonos o pagos en tránsito):

| Fecha | Documento | Importe | Concepto |
|---|---|---|---|
| | | | |

Les rogamos indiquen también si existen **acuerdos comerciales especiales**
(descuentos por volumen, rappels pendientes de liquidar, depósitos, consignaciones
o mercancía en depósito) vigentes a la fecha indicada.

Fecha: ______  Firma y sello: ______  Nombre y cargo: ______

> **Confirmación negativa** (se responde solo en caso de disconformidad):
> úsala solo si el riesgo valorado es bajo, la población es de saldos numerosos y
> pequeños, y no se espera un porcentaje relevante de excepciones. Aporta mucha
> menos evidencia que la positiva: la ausencia de respuesta no prueba conformidad.

---

## 3. Solicitud de información a abogados

> Se envía a **todos** los abogados y asesores jurídicos que hayan facturado
> durante el ejercicio, identificados por la cuenta 623 — **no solo a los que la
> dirección declare**. El abogado que ha facturado y del que la dirección no habla
> es exactamente el que hay que circularizar.

**«DESPACHO DE ABOGADOS»** — «Domicilio»

Muy señores nuestros:

En relación con la auditoría de las cuentas anuales de **«DENOMINACIÓN»**
correspondientes al ejercicio terminado el «fecha de cierre», y por indicación de
la dirección de la entidad, les rogamos nos informen **directamente** sobre:

1. **Litigios, reclamaciones y procedimientos** en curso a la fecha indicada, y
   los surgidos hasta la fecha de su respuesta, en los que la entidad sea parte,
   indicando en cada uno:
   - Naturaleza del asunto y órgano ante el que se sustancia.
   - Cuantía reclamada.
   - **Evaluación del desenlace probable** y, si es posible, del importe estimado.
   - Fase procesal y calendario previsto.
2. Asuntos en los que hayan sido consultados y que puedan derivar en
   responsabilidad para la entidad, aunque no exista aún procedimiento.
3. **Honorarios devengados y pendientes de facturar** a la fecha de cierre.
4. Confirmación de que nos han informado de **todos** los asuntos que llevan de la
   entidad.

Si su intervención se ha limitado a asuntos que no generan contingencia, rogamos
nos lo indiquen expresamente.

Respuesta a: «dirección del despacho».

---

## 4. Control de la circularización

Se lleva en un fichero procesable por
`financiacion.seguimiento_confirmaciones()`, con las columnas: `Entidad`,
`Fecha envío`, `Fecha respuesta`, `Saldo confirmado`, `Saldo contable`, `Avales`,
`Avales contabilizados`.

| Código | Incidencia | Severidad |
|---|---|---|
| `CIR-001` | No consta el envío | **BLOQUEANTE** |
| `CIR-002` | Enviada sin respuesta | RESOLVER |
| `CIR-010` | Saldo confirmado ≠ saldo contable | RESOLVER |
| `CIR-020` | Avales o garantías revelados y no desglosados | RESOLVER |

**Sin respuesta y sin procedimiento alternativo suficiente hay limitación al
alcance.** Los procedimientos alternativos (cobros y pagos posteriores, examen de
documentación soporte) deben documentarse **y evaluarse expresamente en cuanto a
su suficiencia** — no basta con ejecutarlos.
