# Motor de inferencia.
# Recibe los hechos y decide que accion tocar.
#
# Estrategia bien simple (a proposito, para que se entienda en clase):
#   1) si el parse fallo -> accion error_sintactico
#   2) si no, revisa las reglas de mayor a menor prioridad
#   3) la primera que cumpla gana
#   4) ejecutamos la accion asociada
#
# Es el esquema:
#   parse valido Y verbo=X Y objeto cumple Y  ->  ejecuta Z / responde W

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from acciones import (
    ejecutar_abrir_aplicacion,
    ejecutar_busqueda_google,
    ejecutar_reproducir_youtube,
)
from config import MOSTRAR_HECHOS
from experto.hechos import HechosComando
from experto.reglas import REGLAS, Regla

# Tipo del callback que habla (normalmente GeneradorVoz.generar_voz)
Hablar = Callable[[str], None]


@dataclass
class ResultadoInferencia:
    # Lo que salio de inferir(): que regla gano y que accion hay que correr
    regla: Regla | None
    accion: str
    hechos: HechosComando


def inferir(hechos: HechosComando) -> ResultadoInferencia:
    # Solo decide. No ejecuta efectos todavia.

    # Si ni siquiera parseo, no evaluamos reglas de dominio
    if not hechos.parse_valido:
        return ResultadoInferencia(None, "error_sintactico", hechos)

    # Recorremos por prioridad (100 primero, luego 90, etc.)
    for regla in sorted(REGLAS, key=lambda r: (-r.prioridad, r.id)):
        if regla.condiciones(hechos):
            return ResultadoInferencia(regla, regla.accion, hechos)

    # Ninguna regla aplico (caso raro si tienes el comodín verbo_sin_accion)
    return ResultadoInferencia(None, "sin_regla", hechos)


# ----- implementacion de cada accion -----
# El nombre de la clave tiene que coincidir con regla.accion en reglas.py

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


# Tabla accion -> funcion. Si agregas una regla con accion nueva, registrala aqui.
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
    # Ya con la decision tomada, aplicamos el efecto (TTS + YouTube/Google/app)

    # En demo conviene ver los hechos y que regla gano
    if MOSTRAR_HECHOS:
        print("\n--- Hechos ---")
        print(resultado.hechos.resumen())
        if resultado.regla:
            print(f"  regla = {resultado.regla.id}")
        print(f"  accion = {resultado.accion}")
        print("---\n")

    fn = ACCIONES.get(resultado.accion)
    if fn is None:
        # Te falto registrar la accion en el diccionario de arriba
        hablar(f"La accion «{resultado.accion}» no esta registrada.")
        return

    fn(resultado.hechos, hablar)
