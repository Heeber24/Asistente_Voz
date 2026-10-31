"""Sistema experto del asistente: hechos, reglas de producción y motor de inferencia.

Los estudiantes pueden ampliar:
- hechos.py  → qué datos se guardan tras el parseo
- reglas.py  → condiciones SI … ENTONCES … (añadir Regla nuevas)
- motor.py   → cómo se elige y aplica la regla (normalmente no hace falta tocarlo)
"""

# Imports perezosos vía atributos para no forzar cargar acciones/TTS al inspeccionar el paquete.

__all__ = [
    "HechosComando",
    "hechos_desde_analisis",
    "ResultadoInferencia",
    "inferir",
    "REGLAS",
]


def __getattr__(name: str):
    if name in ("HechosComando", "hechos_desde_analisis"):
        from asistente_voz.experto import hechos as _hechos

        return getattr(_hechos, name)
    if name in ("ResultadoInferencia", "inferir"):
        from asistente_voz.experto import motor as _motor

        return getattr(_motor, name)
    if name == "REGLAS":
        from asistente_voz.experto.reglas import REGLAS as _REGLAS

        return _REGLAS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
