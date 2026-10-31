"""Base de hechos del asistente (memoria de trabajo tras el parseo).

En un sistema experto clásico, los *hechos* son afirmaciones verdaderas
en el momento actual. Aquí se rellenan a partir del análisis sintáctico
y de un poco de conocimiento estático (p. ej. alias de aplicaciones).

Los estudiantes pueden añadir campos nuevos a ``HechosComando`` y
rellenarlos en ``hechos_desde_analisis`` para que las reglas los usen.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config import APPS_LEXICO, VERBOS_OBJETO_ABIERTO
from gramatica import AnalisisSintactico


def _alias_app_en_tokens(tokens: list[str]) -> str | None:
    found: str | None = None
    for t in tokens:
        if t in APPS_LEXICO:
            found = t
    return found



@dataclass
class HechosComando:
    """Hechos derivados de la frase actual (una petición del usuario)."""

    # --- sintaxis ---
    parse_valido: bool = False
    wake: str | None = None
    verbo: str | None = None
    objeto: str = ""
    objeto_tokens: list[str] = field(default_factory=list)
    plantilla: list[str] = field(default_factory=list)
    arbol_texto: str = ""
    codigo_error_sintactico: str | None = None
    mensaje_error_sintactico: str | None = None

    # --- semántica / dominio ---
    objeto_no_vacio: bool = False
    verbo_objeto_abierto: bool = False
    alias_app: str | None = None
    tiene_alias_app: bool = False

    def resumen(self) -> str:
        """Texto corto para demos en consola."""
        lineas = [
            f"  parse_valido     = {self.parse_valido}",
            f"  wake             = {self.wake!r}",
            f"  verbo            = {self.verbo!r}",
            f"  objeto           = {self.objeto!r}",
            f"  objeto_no_vacio  = {self.objeto_no_vacio}",
            f"  alias_app        = {self.alias_app!r}",
            f"  tiene_alias_app  = {self.tiene_alias_app}",
        ]
        if self.codigo_error_sintactico:
            lineas.append(f"  error_sintaxis   = {self.codigo_error_sintactico}")
        return "\n".join(lineas)


def hechos_desde_analisis(analisis: AnalisisSintactico) -> HechosComando:
    """Traduce el resultado del parser a hechos que entiende el motor."""
    objeto = " ".join(analisis.objeto_tokens).strip()
    alias = (
        _alias_app_en_tokens(analisis.objeto_tokens) if analisis.objeto_tokens else None
    )
    verbo = analisis.verbo
    return HechosComando(
        parse_valido=analisis.valido,
        wake=analisis.wake,
        verbo=verbo,
        objeto=objeto,
        objeto_tokens=list(analisis.objeto_tokens),
        plantilla=list(analisis.plantilla),
        arbol_texto=analisis.arbol_texto,
        codigo_error_sintactico=analisis.codigo_error,
        mensaje_error_sintactico=analisis.mensaje_error,
        objeto_no_vacio=bool(objeto),
        verbo_objeto_abierto=bool(verbo and verbo in VERBOS_OBJETO_ABIERTO),
        alias_app=alias,
        tiene_alias_app=alias is not None,
    )
