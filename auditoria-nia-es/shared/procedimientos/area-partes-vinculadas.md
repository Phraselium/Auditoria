# area-partes-vinculadas

> Área M — Identifica partes vinculadas, sus operaciones y el desglose de retribuciones.

> **Cuándo:** Úsala en todo encargo: la ausencia de operaciones vinculadas es una conclusión que hay que probar, no una presunción. Términos: identifica, partes, vinculadas, audita, operaciones, realizadas, saldos, pendientes, retribuciones, anticipos, órgano, administración, dirección, verifica.

> **Necesita:** `[carpeta-del-encargo]`

---
**Cuentas del área:** 16x deudas con grupo · 24x inversiones en grupo · 44x deudores varios · 55x cuentas con socios y administradores

La mecánica (carga del programa escalado, ejecución, generación del papel de
trabajo, conclusión y registro) la aporta la guía `areas-de-campo`. Aquí está el **criterio
específico del área** y su programa de trabajo.

## Riesgos típicos

| Riesgo | Afirmaciones |
|---|---|
| Partes vinculadas no identificadas por la dirección | integridad |
| Operaciones vinculadas realizadas fuera de condiciones de mercado | valoración, desglose |
| Retribuciones y anticipos al órgano de administración no desglosados | desglose |
| Operaciones vinculadas usadas para eludir controles o alterar el resultado | ocurrencia |

## Criterio específico del área

**La ausencia de operaciones vinculadas es una conclusión, no una presunción.**
«No hay» solo vale si se ha buscado. Fuentes de identificación que van más allá de
la manifestación de la dirección:

1. Cuentas del subgrupo 55 (cuentas corrientes con socios y administradores) y de
   los subgrupos 16 y 24.
2. Escrituras, nota simple del Registro Mercantil y libro de socios.
3. **Test de asientos del diario**: contrapartidas atípicas con cuentas 55x.
4. Proveedores y clientes con domicilio o administradores coincidentes.
5. Actas del órgano de administración.
6. Declaraciones fiscales: modelo 232 de operaciones vinculadas.

**El desglose de memoria no admite el criterio de importancia relativa por
importe** (art. 260 LSC y PGC 3ª parte). Se desglosan las operaciones y los saldos
por tipo y naturaleza, y las retribuciones y anticipos al órgano de administración
y a la alta dirección, sea cual sea su cuantía. Aplica una **materialidad
específica más baja** a esta área (`materialidad.especifica(mat, "M", ..., 0.25)`).

**Condiciones de mercado.** Si las operaciones no se han realizado en condiciones
de mercado, hay que evaluar el efecto contable y el fiscal (precios de
transferencia). Conéctalo con `area-fiscal`.

## Programa de trabajo

El programa escalado por perfil está en
`shared/references/programas/partes-vinculadas.md`. Se carga bajo demanda: no lo copies aquí.

## Ejecución

```bash
audita asientos 00-fuentes/diario.xlsx 2025-12-31 \
    --materialidad <MP> --papel "01-papeles/M-1 Partes vinculadas.xlsx"
```

## Checklist de autoverificación

Además de la checklist común de `areas-de-campo`:

- [ ] La identificación de partes vinculadas va más allá de la manifestación de la dirección.
- [ ] Se han revisado las cuentas 55x, 16x y 24x y el modelo 232.
- [ ] Las retribuciones y anticipos al órgano de administración están desglosados, sea cual sea su importe.
- [ ] Se ha aplicado una materialidad específica más baja a esta área.
- [ ] Las operaciones significativas fuera del curso normal del negocio están identificadas y evaluadas.
- [ ] Si se concluye que no hay operaciones vinculadas, consta cómo se ha llegado a esa conclusión.
