"""Genera los ficheros de prueba sinteticos del banco de pruebas.

No son datos de ningun cliente: se construyen de forma determinista con semilla
fija para que los resultados de los tests sean reproducibles.

Reproducen deliberadamente la suciedad del mundo real:
  - cabeceras precedidas de filas de titulo, NIF y fechas
  - cuentas de 10 digitos y 8 grupos
  - importes en formato espanol con separador de miles
  - tres ficheros de leasing con nomenclaturas de columna distintas
  - una diferencia introducida a proposito entre memoria y balance
"""

from __future__ import annotations

import json
import os
import random

import pandas as pd
from openpyxl import Workbook

AQUI = os.path.dirname(os.path.abspath(__file__))
FIXT = os.path.join(AQUI, "fixtures")
EJERCICIO = 2025
CIERRE = pd.Timestamp("2025-12-31")

random.seed(20250101)


def cif_sintetico() -> str:
    """CIF de sociedad ficticia, calculado en ejecucion.

    Se calcula en vez de escribirse para que el repositorio no contenga ningun
    identificador con digito de control valido: el verificador de privacidad
    (`scripts/comprobar_privacidad.py`) no distingue uno real de uno inventado
    que valide, y con razon.
    """
    cuerpo = "0000000"
    pares = sum(int(d) for d in cuerpo[1::2])
    impares = sum(sum(divmod(int(d) * 2, 10)) for d in cuerpo[0::2])
    return "B" + cuerpo + str((10 - (pares + impares) % 10) % 10)


def _euro(x: float) -> str:
    """Formato espanol: 1.234.567,89"""
    return f"{x:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def _escribe(path: str, cabeceras: list[str], filas: list[list],
             preambulo: list[list] | None = None, hoja: str = "Hoja1") -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = hoja
    for p in (preambulo or []):
        ws.append(p)
    ws.append(cabeceras)
    for f in filas:
        ws.append(f)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# Sociedad sintetica: TRANSPORTES SINTETICOS SL
# ---------------------------------------------------------------------------
CUENTAS = {
    "1000000000": "Capital social",
    "1120000000": "Reserva legal",
    "1130000000": "Reservas voluntarias",
    "1144000000": "Reserva de capitalizacion",
    "1200000000": "Remanente",
    "1290000000": "Resultado del ejercicio",
    "1740000001": "Acreedores por arrendamiento financiero a largo plazo",
    "1700000001": "Deudas a largo plazo con entidades de credito",
    "2180000001": "Elementos de transporte",
    "2810000001": "Amortizacion acumulada de elementos de transporte",
    "2160000001": "Mobiliario",
    "2810000002": "Amortizacion acumulada de mobiliario",
    "4000000001": "Proveedores - COMBUSTIBLES DEL NORTE SL",
    "4000000002": "Proveedores - TALLERES MECANICOS SA",
    "4300000001": "Clientes - LOGISTICA PENINSULAR SA",
    "4300000002": "Clientes - DISTRIBUIDORA CENTRO SL",
    "4650000000": "Remuneraciones pendientes de pago",
    "4720000000": "HP IVA soportado",
    "4750000000": "HP acreedora por IVA",
    "4760000000": "Organismos de la Seguridad Social acreedores",
    "4751000000": "HP acreedora por retenciones",
    "5240000001": "Acreedores por arrendamiento financiero a corto plazo",
    "5200000001": "Deudas a corto plazo con entidades de credito",
    "5720000001": "Bancos c/c - BANCO DEL NORTE",
    "5720000002": "Bancos c/c - CAJA DEL SUR",
    "6000000000": "Compras de mercaderias",
    "6210000000": "Arrendamientos y canones",
    "6280000000": "Suministros",
    "6400000000": "Sueldos y salarios",
    "6420000000": "Seguridad Social a cargo de la empresa",
    "6620000000": "Intereses de deudas",
    "6810000000": "Amortizacion del inmovilizado material",
    "7000000000": "Ventas de mercaderias",
    "7050000000": "Prestaciones de servicios",
    "2500000000": "Inversiones financieras a largo plazo en instrumentos de patrimonio",
    "1330000000": "Ajustes por valoracion en activos financieros a valor razonable",
    "8000000000": "Perdidas en activos financieros a valor razonable con cambios en el PN",
    "9000000000": "Beneficios en activos financieros a valor razonable con cambios en el PN",
}


def genera_diario() -> pd.DataFrame:
    """Construye el diario. El balance se deriva de el, asi cuadra por construccion."""
    apuntes: list[dict] = []
    n = [0]
    usuarios = ["ADMIN", "ADMIN", "ADMIN", "MJPEREZ", "MJPEREZ", "LGARCIA"]

    def asiento(fecha: str, lineas: list[tuple[str, float, float]], concepto: str,
                usuario: str | None = None) -> None:
        n[0] += 1
        u = usuario or random.choice(usuarios)
        for cuenta, debe, haber in lineas:
            apuntes.append({"asiento": n[0], "fecha": fecha, "cuenta": cuenta,
                            "descripcion": concepto, "debe": round(debe, 2),
                            "haber": round(haber, 2), "usuario": u,
                            "documento": f"DOC{n[0]:05d}"})

    # 1. Apertura
    apertura = {
        "1000000000": (0, 60000.00), "1120000000": (0, 12000.00),
        "1130000000": (0, 188500.00), "1144000000": (0, 9000.00),
        "1200000000": (0, 21400.00),
        "2180000001": (742000.00, 0), "2810000001": (0, 268400.00),
        "2160000001": (38000.00, 0), "2810000002": (0, 15200.00),
        "1740000001": (0, 196800.00), "5240000001": (0, 74300.00),
        "1700000001": (0, 41000.00), "5200000001": (0, 18500.00),
        "4300000001": (81400.00, 0), "4300000002": (34600.00, 0),
        "4000000001": (0, 44300.00), "4000000002": (0, 12600.00),
        "5720000001": (52300.00, 0), "5720000002": (13700.00, 0),
    }
    total_d = sum(v[0] for v in apertura.values())
    total_h = sum(v[1] for v in apertura.values())
    assert abs(total_d - total_h) < 0.01, f"apertura descuadrada {total_d} vs {total_h}"
    asiento("01/01/2025", [(c, d, h) for c, (d, h) in apertura.items()],
            "Asiento de apertura", "ADMIN")

    # 2. Ventas mensuales
    for mes in range(1, 13):
        for j in range(6):
            base = round(random.uniform(8000, 26000), 2)
            iva = round(base * 0.21, 2)
            dia = min(2 + j * 4, 28)
            cliente = "4300000001" if j % 2 == 0 else "4300000002"
            cuenta_ing = "7000000000" if j % 3 else "7050000000"
            asiento(f"{dia:02d}/{mes:02d}/2025",
                    [(cliente, base + iva, 0), (cuenta_ing, 0, base),
                     ("4750000000", 0, iva)],
                    f"Factura de venta {mes:02d}/{j + 1:02d}")

    # 3. Compras y gastos
    for mes in range(1, 13):
        for cuenta, rango in (("6000000000", (5000, 14000)),
                              ("6280000000", (900, 2600)),
                              ("6210000000", (1200, 1800))):
            base = round(random.uniform(*rango), 2)
            iva = round(base * 0.21, 2)
            prov = "4000000001" if cuenta == "6000000000" else "4000000002"
            asiento(f"{min(random.randint(3, 27), 28):02d}/{mes:02d}/2025",
                    [(cuenta, base, 0), ("4720000000", iva, 0),
                     (prov, 0, base + iva)],
                    f"Factura recibida {cuenta[:3]} {mes:02d}")

    # 4. Nominas
    for mes in range(1, 13):
        bruto = 38500.00
        ss_emp = round(bruto * 0.315, 2)
        retencion = round(bruto * 0.15, 2)
        ss_trab = round(bruto * 0.0635, 2)
        liquido = round(bruto - retencion - ss_trab, 2)
        asiento(f"28/{mes:02d}/2025",
                [("6400000000", bruto, 0), ("6420000000", ss_emp, 0),
                 ("4650000000", 0, liquido), ("4751000000", 0, retencion),
                 ("4760000000", 0, round(ss_emp + ss_trab, 2))],
                f"Nomina {mes:02d}/2025", "MJPEREZ")

    # 5. Cobros y pagos
    for mes in range(1, 13):
        asiento(f"05/{mes:02d}/2025",
                [("5720000001", 92000.00, 0), ("4300000001", 0, 92000.00)],
                f"Cobro clientes {mes:02d}")
        asiento(f"06/{mes:02d}/2025",
                [("5720000002", 38000.00, 0), ("4300000002", 0, 38000.00)],
                f"Cobro clientes {mes:02d}")
        asiento(f"20/{mes:02d}/2025",
                [("4000000001", 22000.00, 0), ("5720000001", 0, 22000.00)],
                f"Pago proveedores {mes:02d}")
        asiento(f"21/{mes:02d}/2025",
                [("4000000002", 6500.00, 0), ("5720000002", 0, 6500.00)],
                f"Pago proveedores {mes:02d}")
        asiento(f"10/{mes:02d}/2025",
                [("4650000000", 26000.00, 0), ("4760000000", 14700.00, 0),
                 ("4751000000", 5775.00, 0), ("5720000001", 0, 46475.00)],
                f"Pago nominas y seguros sociales {mes:02d}", "MJPEREZ")

    # 6. Cuotas de arrendamiento financiero y prestamo
    for mes in range(1, 13):
        asiento(f"01/{mes:02d}/2025",
                [("5240000001", 6191.67, 0), ("6620000000", 1240.00, 0),
                 ("4720000000", 1300.25, 0), ("5720000001", 0, 8731.92)],
                f"Cuota leasing {mes:02d}")
        asiento(f"02/{mes:02d}/2025",
                [("5200000001", 1541.67, 0), ("6620000000", 168.00, 0),
                 ("5720000001", 0, 1709.67)],
                f"Cuota prestamo {mes:02d}")

    # 7. Reclasificacion corriente/no corriente y amortizacion
    asiento("31/12/2025",
            [("1740000001", 74300.00, 0), ("5240000001", 0, 74300.00)],
            "Reclasificacion deuda leasing a corto plazo", "ADMIN")
    asiento("31/12/2025",
            [("1700000001", 18500.00, 0), ("5200000001", 0, 18500.00)],
            "Reclasificacion prestamo a corto plazo", "ADMIN")
    asiento("31/12/2025",
            [("6810000000", 96800.00, 0), ("2810000001", 0, 93000.00),
             ("2810000002", 0, 3800.00)],
            "Dotacion amortizacion del ejercicio", "ADMIN")

    # 8. Grupos 8 y 9: ingresos y gastos imputados al patrimonio neto.
    #    Su presencia hace que el balance tenga 8 grupos, como en las entidades
    #    grandes, y verifica que la ingesta y el mapeo los tratan correctamente.
    asiento("30/06/2025", [("2500000000", 12000.00, 0), ("9000000000", 0, 12000.00)],
            "Valoracion a valor razonable de instrumentos de patrimonio", "ADMIN")
    asiento("31/12/2025", [("9000000000", 12000.00, 0), ("1330000000", 0, 12000.00)],
            "Traspaso al patrimonio neto de beneficios por valoracion", "ADMIN")
    asiento("30/09/2025", [("8000000000", 4500.00, 0), ("2500000000", 0, 4500.00)],
            "Valoracion a valor razonable de instrumentos de patrimonio", "ADMIN")
    asiento("31/12/2025", [("1330000000", 4500.00, 0), ("8000000000", 0, 4500.00)],
            "Traspaso al patrimonio neto de perdidas por valoracion", "ADMIN")

    # 9. Asientos deliberadamente inusuales (para el test de asientos del diario)
    asiento("28/12/2025", [("4300000001", 50000.00, 0), ("7000000000", 0, 50000.00)],
            "", "LGARCIA")                                    # sin descripcion + fin de ejercicio + redondo
    asiento("25/12/2025", [("6280000000", 12000.00, 0), ("5720000002", 0, 12000.00)],
            "Regularizacion suministros", "LGARCIA")          # festivo + redondo
    asiento("30/12/2025", [("7050000000", 0, 18000.00), ("1130000000", 18000.00, 0)],
            "Ajuste", "LGARCIA")                              # ingreso sin contrapartida normal

    df = pd.DataFrame(apuntes)

    # 10. Regularizacion: cierra grupos 6 y 7 contra la 129
    ingresos = df[df["cuenta"].str.startswith("7")]["haber"].sum() - \
        df[df["cuenta"].str.startswith("7")]["debe"].sum()
    gastos = df[df["cuenta"].str.startswith("6")]["debe"].sum() - \
        df[df["cuenta"].str.startswith("6")]["haber"].sum()
    resultado = round(ingresos - gastos, 2)

    lineas: list[tuple[str, float, float]] = []
    for cuenta in sorted(df["cuenta"].unique()):
        if not cuenta.startswith(("6", "7")):
            continue
        sub = df[df["cuenta"] == cuenta]
        saldo = round(sub["debe"].sum() - sub["haber"].sum(), 2)
        if saldo > 0:
            lineas.append((cuenta, 0.0, saldo))
        elif saldo < 0:
            lineas.append((cuenta, -saldo, 0.0))
    lineas.append(("1290000000", 0.0, resultado) if resultado >= 0
                  else ("1290000000", -resultado, 0.0))
    n[0] += 1
    for cuenta, debe, haber in lineas:
        apuntes.append({"asiento": n[0], "fecha": "31/12/2025", "cuenta": cuenta,
                        "descripcion": "Regularizacion de ingresos y gastos",
                        "debe": round(debe, 2), "haber": round(haber, 2),
                        "usuario": "ADMIN", "documento": f"DOC{n[0]:05d}"})

    return pd.DataFrame(apuntes), round(resultado, 2), apertura


def genera_sumas_y_saldos(diario: pd.DataFrame, apertura: dict) -> pd.DataFrame:
    agg = diario.groupby("cuenta").agg(debe=("debe", "sum"), haber=("haber", "sum"))
    agg = agg.round(2).reset_index()
    agg["saldo"] = (agg["debe"] - agg["haber"]).round(2)
    agg["descripcion"] = agg["cuenta"].map(CUENTAS).fillna("")
    agg["apertura"] = agg["cuenta"].map(
        lambda c: round(apertura.get(c, (0, 0))[0] - apertura.get(c, (0, 0))[1], 2))
    return agg[["cuenta", "descripcion", "debe", "haber", "saldo", "apertura"]]


def genera_leasings() -> list[str]:
    """Tres ficheros con nomenclaturas distintas: 100 contratos en total."""
    rutas: list[str] = []

    # -- Fichero 1: cuadro de "BANCO DEL NORTE", 40 contratos ----------------
    filas = []
    for i in range(40):
        importe = round(random.uniform(45000, 135000), 2)
        plazo = random.choice([48, 60, 72])
        tipo = random.uniform(0.045, 0.078)
        r = (1 + tipo) ** (1 / 12) - 1
        # La opcion de compra equivale a una cuota y forma parte de los pagos
        # minimos: el cuadro de la entidad la incluye en el descuento.
        anualidad = (1 - (1 + r) ** -plazo) / r
        cuota = round(importe / (anualidad + (1 + r) ** -plazo), 2)
        opcion = round(cuota, 2)
        filas.append([
            f"BN-LEA-{i + 1:04d}", "BANCO DEL NORTE",
            f"Camion tractora {2019 + i % 6} mat. {1000 + i:04d}-KLM",
            f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{2021 + i % 4}",
            _euro(importe), plazo, _euro(cuota), "Mensual", f"{tipo * 100:.3f}",
            _euro(opcion), _euro(importe * 1.06), 8,
        ])
    rutas.append(_escribe(
        os.path.join(FIXT, "leasings_banco_norte.xlsx"),
        ["Nº Contrato", "Entidad", "Descripcion del bien", "Fecha inicio",
         "Importe financiado", "Nº cuotas", "Cuota mensual", "Periodicidad",
         "Tipo interes (%)", "Opcion de compra", "Valor razonable", "Vida util"],
        filas,
        preambulo=[["BANCO DEL NORTE, S.A."],
                   ["Relacion de operaciones de arrendamiento financiero"],
                   [f"Cliente: TRANSPORTES SINTETICOS SL   NIF: {cif_sintetico()}"],
                   ["Fecha de emision: 15/01/2026"], []],
        hoja="Operaciones"))

    # -- Fichero 2: cuadro de "CAJA DEL SUR", 35 contratos, otra nomenclatura -
    filas = []
    for i in range(35):
        importe = round(random.uniform(18000, 62000), 2)
        periodicidad = random.choice(["Trimestral", "Mensual"])
        meses = random.choice([36, 48, 60])
        pa = 4 if periodicidad == "Trimestral" else 12
        n = int(meses * pa / 12)
        tipo = random.uniform(0.052, 0.089)
        r = (1 + tipo) ** (1 / pa) - 1
        anualidad = (1 - (1 + r) ** -n) / r
        cuota = round(importe / (anualidad + (1 + r) ** -n), 2)
        filas.append([
            f"CS{i + 1:03d}", "CAJA DEL SUR", f"Remolque frigorifico REF-{i + 1:03d}",
            f"{random.randint(1, 28):02d}/0{random.randint(1, 9)}/{2022 + i % 3}",
            importe, meses, cuota, periodicidad, round(tipo, 5),
            round(cuota, 2), round(importe * 1.04, 2), 7,
        ])
    # tres contratos con problemas deliberados
    filas.append(["CS900", "CAJA DEL SUR", "Carretilla elevadora", "10/03/2023",
                  0, 48, 0, "Mensual", 0.06, 0, 0, 5])          # sin datos
    filas.append(["CS901", "CAJA DEL SUR", "Furgoneta reparto", "01/06/2023",
                  95000, 36, 1200, "Mensual", 0.05, 500, 98000, 6])  # incoherente
    filas.append(["CS902", "CAJA DEL SUR", "Grua auxiliar", "15/09/2024",
                  42000, 60, 830, "Mensual", 0.065, 830, 44000, 9])  # normal
    rutas.append(_escribe(
        os.path.join(FIXT, "leasings_caja_sur.xlsx"),
        ["Referencia", "Arrendador", "Activo", "Fecha contrato", "Principal",
         "Plazo (meses)", "Importe cuota", "Frecuencia", "TIN", "Valor residual",
         "Valor contado", "Vida util (anos)"],
        filas,
        preambulo=[["CAJA DEL SUR"], ["Detalle de arrendamientos financieros"], []],
        hoja="Detalle"))

    # -- Fichero 3: hoja propia de la entidad, 25 contratos, con confianza OCR
    filas = []
    for i in range(25):
        importe = round(random.uniform(9000, 30000), 2)
        plazo = random.choice([24, 36, 48])
        tipo = random.uniform(0.06, 0.12)
        r = (1 + tipo) ** (1 / 12) - 1
        cuota = round(importe * r / (1 - (1 + r) ** -plazo), 2)
        conf = 0.95 if i % 5 else 0.62   # 5 contratos con baja confianza de OCR
        filas.append([
            f"INT-{i + 1:03d}", "RENTING TECNOLOGICO SL",
            f"Equipo informatico lote {i + 1}",
            f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/2024",
            importe, plazo, cuota, "Mensual", round(tipo, 4), 0, 0, 4, conf,
        ])
    rutas.append(_escribe(
        os.path.join(FIXT, "leasings_internos.xlsx"),
        ["id", "entidad", "descripcion", "fecha inicio", "importe financiado",
         "n cuotas", "cuota", "periodicidad", "tipo interes", "opcion compra",
         "valor razonable", "vida util", "confianza"],
        filas,
        preambulo=[["Relacion interna de contratos - extraccion Data Sniper"], []],
        hoja="Contratos"))
    return rutas


def genera_inventario() -> str:
    filas = []
    for i in range(30):
        coste = round(random.uniform(12000, 95000), 2)
        coef = random.choice([0.16, 0.16, 0.10, 0.125])
        aa = round(coste * coef * random.randint(1, 4), 2)
        aa = min(aa, coste)
        dot = round(coste * coef, 2)
        filas.append([f"ELE-{i + 1:04d}", f"Vehiculo industrial {i + 1}",
                      "Elementos de transporte", "2180000001",
                      f"01/0{random.randint(1, 9)}/{2019 + i % 5}", "",
                      coste, 0, coef * 100, aa, dot, round(aa + dot, 2)])
    # dos elementos con incidencia deliberada
    filas.append(["ELE-9001", "Camion antiguo", "Elementos de transporte",
                  "2180000001", "01/01/2015", "", 48000, 0, 16, 48000, 7680,
                  55680])   # sobreamortizado
    filas.append(["ELE-9002", "Remolque nuevo", "Elementos de transporte",
                  "2180000001", "01/07/2025", "", 60000, 0, 16, 0, 9600, 9600])
    #             ^ alta a mitad de ano contabilizada por el ano completo
    return _escribe(
        os.path.join(FIXT, "inventario_inmovilizado.xlsx"),
        ["Codigo", "Descripcion", "Familia", "Cuenta", "Fecha alta", "Fecha baja",
         "Valor adquisicion", "Valor residual", "% Amortizacion",
         "Amortizacion acumulada inicial", "Dotacion", "Amortizacion acumulada final"],
        filas,
        preambulo=[["TRANSPORTES SINTETICOS SL"], ["Inventario de inmovilizado 2025"], []])


def genera_financiacion() -> str:
    filas = [
        ["PR-001", "BANCO DEL NORTE", "Prestamo", 185000, 0, 1709.67, 120,
         "01/03/2021", "01/03/2031", "Mensual", 4.25, 1850, "Hipotecaria", 22500],
        ["PO-001", "BANCO DEL NORTE", "Poliza de credito", 150000, 87400, 0, 0,
         "15/06/2024", "15/06/2026", "", 5.10, 0, "Personal", 87400],
        ["PO-002", "CAJA DEL SUR", "Poliza de credito", 80000, 92000, 0, 0,
         "01/09/2024", "01/09/2026", "", 5.75, 0, "", 92000],
        ["CF-001", "CAJA DEL SUR", "Confirming", 200000, 45300, 0, 0,
         "01/01/2025", "", "", 3.90, 0, "", 45300],
        ["AV-001", "BANCO DEL NORTE", "Aval", 60000, 60000, 0, 0,
         "10/05/2023", "10/05/2027", "", 1.20, 0, "Aval ante Administracion", 0],
    ]
    return _escribe(
        os.path.join(FIXT, "cartera_financiacion.xlsx"),
        ["Contrato", "Entidad", "Producto", "Limite concedido", "Dispuesto",
         "Cuota", "N cuotas", "Fecha inicio", "Vencimiento", "Periodicidad",
         "Tipo interes", "Gastos", "Garantia", "Saldo contable"],
        filas,
        preambulo=[["Cuadro de financiacion 2025"], []])


def genera_confirmaciones() -> str:
    filas = [
        ["BANCO DEL NORTE", "12/01/2026", "28/01/2026", 52300.00, 52300.00,
         "Aval 60.000 EUR ante Administracion", "Si"],
        ["CAJA DEL SUR", "12/01/2026", "02/02/2026", 11200.00, 13700.00,
         "Pignoracion de imposicion a plazo 25.000 EUR", ""],
        ["BANCO OCCIDENTAL", "", "", 0, 0, "", ""],
    ]
    return _escribe(
        os.path.join(FIXT, "confirmaciones_bancarias.xlsx"),
        ["Entidad", "Fecha envio", "Fecha respuesta", "Saldo confirmado",
         "Saldo contable", "Avales", "Avales contabilizados"], filas)


def genera_memoria_y_ccaa(sys_df: pd.DataFrame, resultado: float) -> dict:
    """Memoria y cuentas anuales, CON UNA DIFERENCIA DELIBERADA.

    La nota de deudas de la memoria declara 285.000,00 EUR cuando el balance
    arroja otro importe: es la diferencia que debe detectar el criterio de
    aceptacion nº3.
    """
    from audita import comparador  # import diferido: el path lo fija el test
    epigrafes = comparador.agrega_por_epigrafe(sys_df)

    def suma(*titulos: str) -> float:
        return round(sum(v for k, v in epigrafes.items()
                         if any(t in k for t in titulos)), 2)

    deudas_reales = round(
        suma("Deudas a largo plazo") + suma("Deudas a corto plazo"), 2)

    estados = {
        "Deudas con entidades de credito y por arrendamiento financiero": deudas_reales,
        "Clientes por ventas y prestaciones de servicios":
            suma("Deudores comerciales"),
        "Inmovilizado material": suma("Inmovilizado material"),
    }
    # >>> DIFERENCIA DELIBERADA: la memoria declara 4.850,00 EUR de mas <<<
    desgloses = dict(estados)
    desgloses["Deudas con entidades de credito y por arrendamiento financiero"] = \
        round(deudas_reales + 4850.00, 2)

    with open(os.path.join(FIXT, "memoria_desgloses.json"), "w", encoding="utf-8") as fh:
        json.dump(desgloses, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(FIXT, "estados_financieros.json"), "w", encoding="utf-8") as fh:
        json.dump(estados, fh, ensure_ascii=False, indent=2)

    texto = """NOTA 1. ACTIVIDAD DE LA EMPRESA

TRANSPORTES SINTETICOS SL se constituyo en 2015 y tiene por objeto social el
transporte de mercancias por carretera. Su domicilio social radica en Espana y su
moneda funcional es el euro.

NOTA 2. BASES DE PRESENTACION DE LAS CUENTAS ANUALES

Las cuentas anuales se han preparado a partir de los registros contables y se
presentan de acuerdo con el Plan General de Contabilidad de PYMES, de forma que
muestran la imagen fiel del patrimonio, de la situacion financiera y de los
resultados. No existen razones excepcionales que hayan obligado a dejar de
aplicar disposiciones legales en materia contable.

NOTA 3. APLICACION DE RESULTADOS

Se propone destinar el resultado del ejercicio a reservas voluntarias.

NOTA 4. NORMAS DE REGISTRO Y VALORACION

Se han aplicado los criterios de valoracion del inmovilizado material,
arrendamientos, instrumentos financieros, impuesto sobre beneficios e ingresos y
gastos recogidos en el marco normativo aplicable.

NOTA 5. INMOVILIZADO MATERIAL

El movimiento del inmovilizado material del ejercicio se detalla en el cuadro
adjunto, que recoge saldo inicial, altas, bajas y saldo final del coste y de la
amortizacion acumulada.

NOTA 7. ARRENDAMIENTOS Y OTRAS OPERACIONES DE NATURALEZA SIMILAR

La sociedad mantiene contratos de arrendamiento financiero sobre elementos de
transporte. El importe de las cuotas pendientes y de las cargas financieras
diferidas se detalla por vencimientos.

NOTA 8. ACTIVOS FINANCIEROS

Los activos financieros corresponden integramente a deudores comerciales y otras
cuentas a cobrar, valorados a su coste amortizado.

NOTA 9. PASIVOS FINANCIEROS

El importe total de las deudas con entidades de credito y por arrendamiento
financiero asciende a 285.000,00 euros al cierre del ejercicio, con el siguiente
desglose por vencimientos.

NOTA 10. FONDOS PROPIOS

El capital social esta integramente suscrito y desembolsado. La reserva legal
alcanza el importe minimo exigido por el articulo 274 de la Ley de Sociedades de
Capital. La sociedad mantiene dotada una reserva de capitalizacion indisponible
durante el plazo legal de mantenimiento.

NOTA 11. SITUACION FISCAL

Se detalla la conciliacion del resultado contable con la base imponible del
impuesto sobre sociedades y los ejercicios abiertos a inspeccion.

NOTA 18. OPERACIONES CON PARTES VINCULADAS

No se han realizado operaciones con partes vinculadas distintas de las
retribuciones al organo de administracion.

NOTA 19. OTRA INFORMACION

El numero medio de personas empleadas durante el ejercicio ha sido de 14.
"""
    ruta_txt = os.path.join(FIXT, "memoria_2025.txt")
    with open(ruta_txt, "w", encoding="utf-8") as fh:
        fh.write(texto)

    # memoria del ejercicio anterior con un parrafo identico (nota heredada)
    anterior = texto.replace("de 14.", "de 13.")
    with open(os.path.join(FIXT, "memoria_2024.txt"), "w", encoding="utf-8") as fh:
        fh.write(anterior)

    return {"desgloses": desgloses, "estados": estados,
            "diferencia_introducida": 4850.00, "epigrafes": epigrafes}


def genera_encargo_con_defectos(resultado: float) -> str:
    """encargo.json con un papel sin conclusion y un riesgo sin respuesta.

    Es el fixture del criterio de aceptacion nº5.
    """
    from audita.encargo import Encargo
    carpeta = os.path.join(FIXT, "encargo_demo")
    enc = Encargo.crear(carpeta, "TRANSPORTES SINTETICOS SL", EJERCICIO, "PGC-PYMES")
    enc.datos["cliente"]["nif"] = cif_sintetico()
    enc.datos["perfil"] = {"perfil": "ESTANDAR", "puntuacion": 38}
    enc.datos["fases"] = {"aceptacion": "completa", "planificacion": "completa",
                          "campo": "en curso", "cierre": "pendiente"}
    enc.fija_materialidad({
        "magnitud": "cifra_negocios", "valor_magnitud": 1850000.0,
        "porcentaje": 0.0125, "global": 23125.0, "ejecucion": 15031.25,
        "insignificante": 1156.25, "perfil": "ESTANDAR",
        "fundamento": "Se toma la cifra de negocios por ser el resultado poco "
                      "representativo. Porcentaje en el punto medio del rango habitual.",
    })
    enc.añade_riesgo(id="R001", area="C", afirmacion="ocurrencia",
                     descripcion="Reconocimiento de ingresos antes del devengo en el "
                                 "corte de operaciones de diciembre",
                     espectro="alto", significativo=True, fraude=True,
                     respuestas=["C-1"])
    enc.añade_riesgo(id="R002", area="F", afirmacion="exactitud y valoracion",
                     descripcion="Clasificacion incorrecta de arrendamientos y calculo "
                                 "de la carga financiera",
                     espectro="medio", respuestas=["F-1"])
    # >>> RIESGO SIN RESPUESTA (criterio de aceptacion nº5) <<<
    enc.añade_riesgo(id="R003", area="E", afirmacion="integridad",
                     descripcion="Deuda financiera no registrada o avales no desglosados",
                     espectro="alto", significativo=True, respuestas=[])
    enc.registra_papel("C-1", "Clientes e ingresos", "01-papeles/C-1.xlsx",
                       "Se ha verificado el corte de operaciones sobre las ultimas "
                       "facturas del ejercicio sin excepciones significativas.",
                       ["R001"], "concluido")
    # >>> PAPEL SIN CONCLUSION (criterio de aceptacion nº5) <<<
    enc.registra_papel("F-1", "Arrendamientos", "01-papeles/F-1.xlsx", "",
                       ["R002"], "en curso")
    enc.guardar()
    return enc.ruta


def main() -> dict:
    os.makedirs(FIXT, exist_ok=True)
    diario, resultado, apertura = genera_diario()
    sys_df = genera_sumas_y_saldos(diario, apertura)

    # sumas y saldos con preambulo sucio e importes en formato espanol
    _escribe(os.path.join(FIXT, "sumas_y_saldos_2025.xlsx"),
             ["Cuenta", "Descripcion", "Debe", "Haber", "Saldo", "Saldo apertura"],
             [[r["cuenta"], r["descripcion"], _euro(r["debe"]), _euro(r["haber"]),
               _euro(r["saldo"]), _euro(r["apertura"])] for _, r in sys_df.iterrows()],
             preambulo=[["TRANSPORTES SINTETICOS SL"],
                        [f"NIF: {cif_sintetico()}"],
                        ["Balance de sumas y saldos"],
                        ["Periodo: 01/01/2025 a 31/12/2025"],
                        ["Emitido: 20/01/2026"], []],
             hoja="Sumas y saldos")

    _escribe(os.path.join(FIXT, "diario_2025.xlsx"),
             ["Nº Asiento", "Fecha", "Cuenta", "Concepto", "Debe", "Haber",
              "Usuario", "Documento"],
             [[r["asiento"], r["fecha"], r["cuenta"], r["descripcion"],
               r["debe"], r["haber"], r["usuario"], r["documento"]]
              for _, r in diario.iterrows()],
             preambulo=[["TRANSPORTES SINTETICOS SL"], ["Libro diario 2025"], []],
             hoja="Diario")

    # cierre del ejercicio anterior (cuadra con la columna de apertura)
    filas_ant = []
    for cuenta, (d, h) in apertura.items():
        saldo = round(d - h, 2)
        filas_ant.append([cuenta, CUENTAS.get(cuenta, ""), _euro(max(d, 0)),
                          _euro(max(h, 0)), _euro(saldo)])
    _escribe(os.path.join(FIXT, "sumas_y_saldos_2024.xlsx"),
             ["Cuenta", "Descripcion", "Debe", "Haber", "Saldo"], filas_ant,
             preambulo=[["Balance de cierre 2024"], []])

    rutas_leasing = genera_leasings()
    genera_inventario()
    genera_financiacion()
    genera_confirmaciones()
    info = genera_memoria_y_ccaa(sys_df, resultado)
    ruta_encargo = genera_encargo_con_defectos(resultado)

    resumen = {
        "cuentas": len(sys_df), "apuntes": len(diario),
        "asientos": int(diario["asiento"].nunique()),
        "resultado_ejercicio": resultado,
        "leasings": rutas_leasing,
        "diferencia_memoria": info["diferencia_introducida"],
        "encargo": ruta_encargo,
    }
    with open(os.path.join(FIXT, "_resumen.json"), "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)
    return resumen


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "scripts"))
    print(json.dumps(main(), ensure_ascii=False, indent=2))
