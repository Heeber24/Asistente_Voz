# Base de hechos (memoria de trabajo).
# Despues del parseo, guardamos aqui lo importante de la frase:
# wake word, verbo, objeto, si hay app, si el parse fue valido, etc.
# Las reglas del experto solo miran estos campos.

from __future__ import annotations

from dataclasses import dataclass, field

from asistente_voz.config import APPS_LEXICO
from asistente_voz.gramatica import AnalisisSintactico


@dataclass
class HechosComando:
    # Hechos de UNA peticion del usuario

    # Salio bien el analisis sintactico?
    parse_valido: bool = False

    # Piezas basicas de la frase
    wake: str | None = None
    verbo: str | None = None
    objeto: str = ""
    objeto_tokens: list[str] = field(default_factory=list)
    objeto_no_vacio: bool = False

    # Solo aplica cuando el verbo es abre/abrir/inicia
    alias_app: str | None = None
    tiene_alias_app: bool = False

    # Si el parse fallo, aqui va el por que
    codigo_error_sintactico: str | None = None
    mensaje_error_sintactico: str | None = None

    def resumen(self) -> str:
        # Texto corto para imprimir en consola durante la demo
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
    # Busca si en la cola del comando viene notepad / word / edge / documento
    encontrada = None
    for t in tokens:
        if t in APPS_LEXICO:
            encontrada = t
    return encontrada


def hechos_desde_analisis(analisis: AnalisisSintactico) -> HechosComando:
    # Traduce el AnalisisSintactico (gramatica.py) a HechosComando
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
