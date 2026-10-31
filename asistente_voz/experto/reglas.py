"""Reglas de producción del sistema experto (SI condiciones ENTONCES acción).

Formato clásico:
    SI parse_valido Y verbo ∈ {reproduce, reproducir} Y objeto_no_vacio
    ENTONCES ejecutar reproducir_youtube

Para ampliar en clase:
1. Añade un ``Regla(...)`` a la lista ``REGLAS`` (abajo).
2. Si la acción es nueva, regístrala en ``asistente_voz.experto.motor.ACCIONES``.
3. Si necesitas un hecho nuevo, extiende ``HechosComando`` en ``hechos.py``.

La prioridad más alta gana cuando varias reglas disparan a la vez.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from asistente_voz.experto.hechos import HechosComando

Condicion = Callable[[HechosComando], bool]


@dataclass(frozen=True)
class Regla:
    id: str
    descripcion: str
    condiciones: Condicion
    accion: str
    prioridad: int = 10


def _verbo_en(hechos: HechosComando, *verbos: str) -> bool:
    return hechos.verbo is not None and hechos.verbo in verbos


# ---------------------------------------------------------------------------
# Base de reglas — los estudiantes añaden más entradas aquí.
# ---------------------------------------------------------------------------
REGLAS: list[Regla] = [
    Regla(
        id="reproducir_youtube",
        descripcion=(
            "SI parse válido Y verbo es reproduce/reproducir Y hay objeto "
            "ENTONCES reproducir en YouTube"
        ),
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_en(h, "reproduce", "reproducir")
            and h.objeto_no_vacio
        ),
        accion="reproducir_youtube",
        prioridad=100,
    ),
    Regla(
        id="buscar_google",
        descripcion=(
            "SI parse válido Y verbo es busca/buscar Y hay objeto "
            "ENTONCES buscar en Google"
        ),
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_en(h, "busca", "buscar")
            and h.objeto_no_vacio
        ),
        accion="buscar_google",
        prioridad=100,
    ),
    Regla(
        id="abrir_aplicacion",
        descripcion=(
            "SI parse válido Y verbo es abre/abrir/inicia Y hay alias de app "
            "ENTONCES abrir esa aplicación"
        ),
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_en(h, "abre", "abrir", "inicia")
            and h.tiene_alias_app
        ),
        accion="abrir_aplicacion",
        prioridad=100,
    ),
    Regla(
        id="abrir_sin_app",
        descripcion=(
            "SI parse válido Y verbo es abre/abrir/inicia Y NO hay alias de app "
            "ENTONCES pedir el nombre de la aplicación"
        ),
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_en(h, "abre", "abrir", "inicia")
            and not h.tiene_alias_app
        ),
        accion="pedir_aplicacion",
        prioridad=90,
    ),
    Regla(
        id="sin_regla_para_verbo",
        descripcion=(
            "SI parse válido Y hay verbo pero ninguna regla de dominio aplicó "
            "ENTONCES avisar que falta acción en la base de reglas"
        ),
        condiciones=lambda h: h.parse_valido and h.verbo is not None,
        accion="verbo_sin_accion",
        prioridad=1,  # comodín de baja prioridad
    ),
]


def listar_reglas() -> None:
    """Imprime las reglas cargadas (útil al inicio de una demo en clase)."""
    print("\n--- Reglas de inferencia cargadas ---")
    for r in sorted(REGLAS, key=lambda x: (-x.prioridad, x.id)):
        print(f"  [{r.prioridad:>3}] {r.id}: {r.descripcion}")
    print("--- fin reglas ---\n")
