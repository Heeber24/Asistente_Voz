# Base de hechos = lo que "sabemos" de la frase actual despues del parseo.
# El motor usa estos campos para ver que regla aplica.

from __future__ import annotations

from dataclasses import dataclass, field

from asistente_voz.config import APPS_LEXICO
from asistente_voz.gramatica import AnalisisSintactico


@dataclass
class HechosComando:
    parse_valido: bool = False
    wake: str | None = None
    verbo: str | None = None
    objeto: str = ""
    objeto_tokens: list[str] = field(default_factory=list)
    objeto_no_vacio: bool = False
    alias_app: str | None = None
    tiene_alias_app: bool = False
    codigo_error_sintactico: str | None = None
    mensaje_error_sintactico: str | None = None

    def resumen(self) -> str:
        lineas = [
            f"  parse_valido    = {self.parse_valido}",
            f"  wake            = {self.wake!r}",
            f"  verbo           = {self.verbo!r}",
            f"  objeto          = {self.objeto!r}",
            f"  alias_app       = {self.alias_app!r}",
        ]
        if self.codigo_error_sintactico:
            lineas.append(f"  error           = {self.codigo_error_sintactico}")
        return "\n".join(lineas)


def _buscar_app(tokens: list[str]) -> str | None:
    encontrada = None
    for t in tokens:
        if t in APPS_LEXICO:
            encontrada = t
    return encontrada


def hechos_desde_analisis(analisis: AnalisisSintactico) -> HechosComando:
    # Traducimos el AnalisisSintactico a hechos que entienden las reglas
    objeto = " ".join(analisis.objeto_tokens).strip()
    alias = _buscar_app(analisis.objeto_tokens) if analisis.objeto_tokens else None

    return HechosComando(
        parse_valido=analisis.valido,
        wake=analisis.wake,
        verbo=analisis.verbo,
        objeto=objeto,
        objeto_tokens=list(analisis.objeto_tokens),
        objeto_no_vacio=bool(objeto),
        alias_app=alias,
        tiene_alias_app=alias is not None,
        codigo_error_sintactico=analisis.codigo_error,
        mensaje_error_sintactico=analisis.mensaje_error,
    )
