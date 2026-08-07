"""dula-audit - libreria de calculo determinista del plugin de auditoria.

Principio innegociable: el modelo interpreta, decide y redacta; el script
calcula. Ningun cuadre, recalculo, amortizacion, extrapolacion de muestra o
comparacion numerica se hace "a ojo".
"""

__version__ = "1.1.0"

from . import (amortizaciones, analiticos, asientos, bitacora, calidad,
               comparador, cuadres, encargo, estado, excel_out, excepciones,
               financiacion, ingesta, leasing, materialidad, muestreo, perfil,
               plan_contable, traza)

__all__ = [
    "amortizaciones", "analiticos", "asientos", "bitacora", "calidad",
    "comparador", "cuadres", "encargo", "estado", "excel_out", "excepciones",
    "financiacion", "ingesta", "leasing", "materialidad", "muestreo", "perfil",
    "plan_contable", "traza",
]
