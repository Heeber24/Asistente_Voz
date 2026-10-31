# Motor de inferencia bien simple:
# 1) si el parse fallo -> error sintactico
# 2) si no, revisa las reglas de mayor a menor prioridad
# 3) la primera que cumpla gana y ejecutamos su accion

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from asistente_voz.acciones import (
    ejecutar_abrir_aplicacion,
    ejecutar_busqueda_google,
    ejecutar_reproducir_youtube,
)
from asistente_voz.config import MOSTRAR_HECHOS
from asistente_voz.experto.hechos import HechosComando
from asistente_voz.experto.reglas import REGLAS, Regla

Hablar = Callable[[str], None]


@dataclass
class ResultadoInferencia:
    regla: Regla | None
    accion: str
    hechos: HechosComando


def inferir(hechos: HechosComando) -> ResultadoInferencia:
    if not hechos.parse_valido:
        return ResultadoInferencia(None, "error_sintactico", hechos)

    for regla in sorted(REGLAS, key=lambda r: (-r.prioridad, r.id)):
        if regla.condiciones(hechos):
            return ResultadoInferencia(regla, regla.accion, hechos)

    return ResultadoInferencia(None, "sin_regla", hechos)


# Cada clave es el nombre de accion que pusiste en reglas.py
def _reproducir(h: HechosComando, hablar: Hablar) -> None:
    ejecutar_reproducir_youtube(h.objeto, hablar)


def _buscar(h: HechosComando, hablar: Hablar) -> None:
    ejecutar_busqueda_google(h.objeto, hablar)


def _abrir(h: HechosComando, hablar: Hablar) -> None:
    ejecutar_abrir_aplicacion(h.alias_app or "", hablar)


def _pedir_app(h: HechosComando, hablar: Hablar) -> None:
    print("Di: notepad, word, edge o documento.")
    hablar("Di que aplicacion abrir: bloc de notas, Word o Edge.")


def _sin_accion(h: HechosComando, hablar: Hablar) -> None:
    hablar(f"Entendi «{h.verbo}», pero no hay regla de accion para ese verbo.")


def _error_sintaxis(h: HechosComando, hablar: Hablar) -> None:
    msg = h.mensaje_error_sintactico or "Esa frase no coincide con la gramatica."
    print(f"(Sintaxis) [{h.codigo_error_sintactico}] {msg}")
    hablar(msg)


def _sin_regla(h: HechosComando, hablar: Hablar) -> None:
    hablar("No encontre una regla que aplique a tu peticion.")


ACCIONES: dict[str, Callable[[HechosComando, Hablar], None]] = {
    "reproducir_youtube": _reproducir,
    "buscar_google": _buscar,
    "abrir_aplicacion": _abrir,
    "pedir_aplicacion": _pedir_app,
    "verbo_sin_accion": _sin_accion,
    "error_sintactico": _error_sintaxis,
    "sin_regla": _sin_regla,
}


def ejecutar_resultado(resultado: ResultadoInferencia, hablar: Hablar) -> None:
    if MOSTRAR_HECHOS:
        print("\n--- Hechos ---")
        print(resultado.hechos.resumen())
        if resultado.regla:
            print(f"  regla = {resultado.regla.id}")
        print(f"  accion = {resultado.accion}")
        print("---\n")

    fn = ACCIONES.get(resultado.accion)
    if fn is None:
        hablar(f"La accion «{resultado.accion}» no esta registrada.")
        return
    fn(resultado.hechos, hablar)
