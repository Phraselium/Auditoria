# Programa de trabajo — Área F: Arrendamientos

**Cuentas:** 174 acreedores por arrendamiento financiero a largo plazo · 524 a
corto plazo · 21x/22x el activo arrendado · 281x su amortización acumulada ·
662 intereses · 621 arrendamientos operativos

Los procedimientos se acumulan: el perfil ESTÁNDAR incluye los del LIGERO, y el
COMPLEJO los de ambos. La simplificación del perfil LIGERO **no autoriza a
recortar por debajo de lo defendible**: si un hallazgo la invalida,
`escalado-del-encargo` eleva el perfil y avisa de qué trabajo se ha quedado corto.

## Perfil LIGERO

1. Inventario completo de contratos vivos, consolidando los ficheros de todas las entidades financieras.
2. **Recálculo del 100 % de la población** con `leasing.procesa_lote()`: tipo implícito, cuadro de cuotas, carga financiera y reparto corriente/no corriente. Al ser determinista y cubrir toda la población, **no procede muestreo para la verificación aritmética**.
3. Clasificación financiero/operativo motivada indicador a indicador (NRV 8ª PGC).
4. Conciliación de la deuda viva recalculada con los saldos contables de las cuentas 174 y 524.
5. Verificación de la periodificación de la carga financiera del ejercicio contra la cuenta 662.
6. Generación del cuadro de vencimientos por ejercicio para el desglose de memoria.
7. Verificación del desglose de la nota de arrendamientos contra el cuadro generado.

## Perfil ESTANDAR

1. Todo lo del perfil LIGERO.
2. **Muestreo dirigido de contratos para verificación documental completa**: los de mayor importe financiado, los de confianza de extracción inferior a 0,85, y los clasificados como DUDOSO.
3. Verificación del alta del activo arrendado en el inmovilizado y de su amortización, que debe seguir el mismo criterio que los activos en propiedad de naturaleza análoga.
4. Contraste del tipo implícito recalculado con el declarado por la entidad, e investigación de las diferencias superiores a 0,25 p.p.
5. Verificación de los contratos cancelados anticipadamente durante el ejercicio y del cálculo de su resultado.
6. Revisión de los arrendamientos operativos: cuotas reconocidas como gasto y pagos mínimos futuros por plazos, para el desglose de memoria.
7. Verificación de las opciones de compra ejercitadas en el ejercicio y de su registro.

## Perfil COMPLEJO

1. Todo lo del perfil ESTÁNDAR.
2. Muestreo estadístico MUS sobre la población de contratos para la verificación documental.
3. Revisión de contratos de sale and lease back y de su tratamiento (NRV 8ª.3).
4. Verificación de subarrendamientos y de arrendamientos con cláusulas de renta variable o de actualización.
5. Revisión de arrendamientos con partes vinculadas y de sus condiciones.
6. Análisis de la sensibilidad de la clasificación en los contratos próximos a los umbrales de los indicadores.

## Riesgos que responde este programa

| Riesgo | Afirmaciones |
|---|---|
| Arrendamiento financiero clasificado como operativo | clasificación, integridad |
| Carga financiera mal periodificada | exactitud, corte |
| Cuadro de cuotas no actualizado por refinanciación o cancelación anticipada | exactitud |
| Deuda viva recalculada distinta del saldo contable | exactitud, valoración |
| Desglose de vencimientos ausente o incompleto | desglose |
| Activo arrendado no dado de alta o amortizado con criterio distinto | existencia, valoración |

## Documentación a solicitar al cliente (PBC de esta área)

- **Cuadros de amortización de todas las entidades financieras, en Excel, no en PDF.** Es la petición que más horas ahorra de toda la PBC.
- Relación interna de contratos vivos a la fecha de cierre.
- Contratos completos de los arrendamientos de mayor importe.
- Facturas de cuota de un mes de muestra por entidad.
- Detalle de contratos cancelados anticipadamente y de opciones de compra ejercitadas durante el ejercicio.
- Valor razonable del bien en el origen y vida útil estimada, para los contratos en que no consten en el cuadro (son los dos datos que más veces faltan y los que bloquean la clasificación).
