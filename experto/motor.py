"""Motor de inferencia: evalúa hechos contra reglas y dispara una acción.

Estrategia (sencilla a propósito, para clase):
- Recorre las reglas ordenadas por prioridad descendente.
- La primera cuyo ``condiciones(hechos)`` sea verdadera gana (forward chaining
  de un solo disparo por petición).
- Si el parse falló, no se evalúan reglas de dominio: se responde el error
  sintáctico.

Así se valida de forma profesional el esquema:
    parse válido ∧ verbo = X ∧ objeto cumple Y  →  ejecuta Z / responde W
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from acciones import (
    ejecutar_abrir_aplicacion,
    ejecutar_busqueda_google,
    ejecutar_reproducir_youtube,
)
from config import MOSTRAR_HECHOS_INFERENCIA
from experto.hechos import HechosComando
from experto.reglas import REGLAS, Regla


@dataclass
class ResultadoInferencia:
    regla: Regla | None
    accion: str
    explicacion: str
    hechos: HechosComando


Hablar = Callable[[str], None]


def _reglas_ordenadas() -> list[Regla]:
    return sorted(REGLAS, key=lambda r: (-r.prioridad, r.id))


def inferir(hechos: HechosComando) -> ResultadoInferencia:
    """Elige la acción a partir de los hechos (sin efectos secundarios)."""
    if not hechos.parse_valido:
        msg = hechos.mensaje_error_sintactico or "La frase no es válida según la gramática."
        return ResultadoInferencia(
            regla=None,
            accion="error_sintactico",
            explicacion=msg,
            hechos=hechos,
        )

    for regla in _reglas_ordenadas():
        try:
            dispara = bool(regla.condiciones(hechos))
        except Exception as e:  # noqa: BLE001 — demo de aula: no tumbar el bucle
            print(f"[motor] Regla {regla.id} lanzó error al evaluar: {e}")
            continue
        if dispara:
            return ResultadoInferencia(
                regla=regla,
                accion=regla.accion,
                explicacion=regla.descripcion,
                hechos=hechos,
            )

    return ResultadoInferencia(
        regla=None,
        accion="sin_regla",
        explicacion="Ninguna regla de la base de conocimiento coincidió con los hechos.",
        hechos=hechos,
    )


def _accion_reproducir_youtube(hechos: HechosComando, hablar: Hablar) -> None:
    ejecutar_reproducir_youtube(hechos.objeto, hablar)


def _accion_buscar_google(hechos: HechosComando, hablar: Hablar) -> None:
    ejecutar_busqueda_google(hechos.objeto, hablar)


def _accion_abrir_aplicacion(hechos: HechosComando, hablar: Hablar) -> None:
    assert hechos.alias_app is not None
    ejecutar_abrir_aplicacion(hechos.alias_app, hablar)


def _accion_pedir_aplicacion(hechos: HechosComando, hablar: Hablar) -> None:
    print("Di: notepad, word, edge o documento.")
    hablar("Di qué aplicación abrir: bloc de notas, Word o Edge.")


def _accion_verbo_sin_accion(hechos: HechosComando, hablar: Hablar) -> None:
    hablar(
        f"Entendí el verbo {hechos.verbo}, pero no hay una regla de acción "
        "definida para él en la base de conocimiento."
    )


def _accion_error_sintactico(hechos: HechosComando, hablar: Hablar) -> None:
    msg = hechos.mensaje_error_sintactico or "Esa frase no coincide con la gramática."
    print(f"(Sintaxis) [{hechos.codigo_error_sintactico}] {msg}")
    hablar(msg)


def _accion_sin_regla(hechos: HechosComando, hablar: Hablar) -> None:
    hablar("No encontré una regla que aplique a tu petición.")


# Tabla acción → función. Los estudiantes registran aquí acciones nuevas.
ACCIONES: dict[str, Callable[[HechosComando, Hablar], None]] = {
    "reproducir_youtube": _accion_reproducir_youtube,
    "buscar_google": _accion_buscar_google,
    "abrir_aplicacion": _accion_abrir_aplicacion,
    "pedir_aplicacion": _accion_pedir_aplicacion,
    "verbo_sin_accion": _accion_verbo_sin_accion,
    "error_sintactico": _accion_error_sintactico,
    "sin_regla": _accion_sin_regla,
}


def ejecutar_resultado(resultado: ResultadoInferencia, hablar: Hablar) -> None:
    """Aplica el efecto de la acción inferida (TTS + lado del sistema)."""
    if MOSTRAR_HECHOS_INFERENCIA:
        print("\n--- Base de hechos (petición actual) ---")
        print(resultado.hechos.resumen())
        if resultado.regla:
            print(f"  regla disparada = {resultado.regla.id}")
        print(f"  acción          = {resultado.accion}")
        print("--- fin hechos ---\n")

    fn = ACCIONES.get(resultado.accion)
    if fn is None:
        hablar(f"La acción «{resultado.accion}» no está registrada en el motor.")
        print(f"[motor] Acción desconocida: {resultado.accion}")
        return
    fn(resultado.hechos, hablar)
