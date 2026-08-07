# Índice de papeles de trabajo

Convención única del despacho. La aplican **todas** las skills.

| Ref. | Papel | Skill que lo genera |
|---|---|---|
| **0.1** | Aceptación y evaluación de independencia | `aceptacion-e-independencia` |
| **0.2** | Carta de encargo firmada | `aceptacion-e-independencia` |
| **0.3** | Estimación del encargo y decisión go/no-go | `estimacion-encargo` |
| **1.1** | Entendimiento de la entidad y su entorno | `entendimiento-entidad` |
| **1.2** | Pruebas de recorrido de los ciclos significativos | `entendimiento-entidad` |
| **1.4** | Materialidad (todas sus versiones) | `materialidad` |
| **1.5** | Mapa de riesgos y diseño de pruebas | `mapa-de-riesgos`, `diseno-de-pruebas` |
| **1.6** | Procedimientos analíticos preliminares | `analiticos` |
| **1.7** | Plan y solicitud de información (PBC) | `plan-y-solicitud-informacion` |
| **2.1** | Ingesta y cuadres de integridad | `ingesta-y-cuadres` |
| **2.8** | Test de asientos del diario | `test-asientos-diario` |
| **2.10** | Comparador documental | `comparador-documental` |
| **2.14** | Checklist de desgloses de memoria | `comparador-documental` |
| **A-1** | Inmovilizado: movimiento y recálculo de amortizaciones | `area-inmovilizado` |
| **A-2** | Inmovilizado: altas, bajas y existencia física | `area-inmovilizado` |
| **B-1** | Existencias: recuento y valoración | `area-existencias` |
| **B-2** | Existencias: corte y obsolescencia | `area-existencias` |
| **C-1** | Clientes: saldos, antigüedad y deterioro | `area-clientes-e-ingresos` |
| **C-2** | Ingresos: analítico mensual y corte de operaciones | `area-clientes-e-ingresos` |
| **C-3** | Circularización de clientes y procedimientos alternativos | `area-clientes-e-ingresos` |
| **D-1** | Tesorería: conciliaciones bancarias | `area-tesoreria-y-financiacion` |
| **D-2** | Confirmaciones bancarias y seguimiento | `area-tesoreria-y-financiacion` |
| **E-1** | Financiación: cartera, deuda viva y coste amortizado | `area-tesoreria-y-financiacion` |
| **E-2** | Covenants | `area-tesoreria-y-financiacion` |
| **F-1** | Arrendamientos: recálculo y clasificación | `area-arrendamientos` |
| **G-1** | Fondos propios: movimiento y actas | `area-fondos-propios-y-reservas` |
| **G-2** | Reservas indisponibles y restringidas | `area-fondos-propios-y-reservas` |
| **H-1** | Proveedores: saldos y conciliaciones | `area-proveedores-y-compras` |
| **H-2** | Búsqueda de pasivos no registrados | `area-proveedores-y-compras` |
| **I-1** | Personal: conciliación y analítico | `area-personal` |
| **J-1** | Fiscal: conciliación resultado ↔ base imponible | `area-fiscal` |
| **J-2** | Impuestos diferidos y su recuperabilidad | `area-fiscal` |
| **J-3** | Cuadres de IVA y retenciones | `area-fiscal` |
| **K-1** | Provisiones y circularización de abogados | `area-provisiones-y-contingencias` |
| **L-1** | Subvenciones: condiciones e imputación | `area-subvenciones` |
| **M-1** | Partes vinculadas: identificación y operaciones | `area-partes-vinculadas` |
| **N-1** | Hechos posteriores | `hechos-posteriores-y-empresa-en-funcionamiento` |
| **N-2** | Empresa en funcionamiento | `hechos-posteriores-y-empresa-en-funcionamiento` |
| **N-3** | Saldos de apertura (primeros encargos) | `saldos-apertura` |
| **8.1** | Sumario de incorrecciones | `evaluacion-de-incorrecciones` |
| **8.2** | Carta de manifestaciones firmada | `comunicaciones-y-manifestaciones` |
| **8.3** | Comunicación de deficiencias de control interno | `comunicaciones-y-manifestaciones` |
| **8.4** | Comunicación con los responsables del gobierno | `comunicaciones-y-manifestaciones` |
| **9.1** | Verificación del informe contra las cuentas definitivas | `redaccion-informe` |
| **9.2** | Revisión de calidad del archivo | `revision-de-calidad` |
| **9.3** | Revisión de calidad del encargo (NIGC2-ES), si procede | `revision-de-calidad` |
| **9.9** | Índice del archivo y control de conservación | `archivo-y-cierre` |

## Nomenclatura de fichero

`<REF> <Título breve>.xlsx` — por ejemplo `F-1 Arrendamientos.xlsx`.

## Referencias cruzadas

Cada papel registra en `encargo.json` los **riesgos que responde**. Cada
incorrección registra el **área** de la que procede. Así el índice se genera solo
y las referencias cruzadas no se mantienen a mano.
