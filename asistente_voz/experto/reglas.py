# Reglas tipo sistema experto:
#   SI se cumplen las condiciones ENTONCES disparo esta accion
#
# Para agregar algo nuevo en clase:
# 1) pega otra Regla en la lista REGLAS
# 2) si la accion es nueva, registrala en motor.py (diccionario ACCIONES)

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from asistente_voz.experto.hechos import HechosComando


@dataclass(frozen=True)
class Regla:
    id: str
    descripcion: str
    condiciones: Callable[[HechosComando], bool]
    accion: str
    prioridad: int = 10  # gana la de numero mas alto


def _verbo_es(h: HechosComando, *ops: str) -> bool:
    return h.verbo is not None and h.verbo in ops


# Aqui estan las reglas. Mientras mas arriba en prioridad, primero se revisan.
REGLAS: list[Regla] = [
    Regla(
        id="reproducir_youtube",
        descripcion="SI parse ok Y verbo reproduce Y hay objeto -> YouTube",
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_es(h, "reproduce", "reproducir")
            and h.objeto_no_vacio
        ),
        accion="reproducir_youtube",
        prioridad=100,
    ),
    Regla(
        id="buscar_google",
        descripcion="SI parse ok Y verbo busca Y hay objeto -> Google",
        condiciones=lambda h: (
            h.parse_valido and _verbo_es(h, "busca", "buscar") and h.objeto_no_vacio
        ),
        accion="buscar_google",
        prioridad=100,
    ),
    Regla(
        id="abrir_aplicacion",
        descripcion="SI parse ok Y verbo abre Y conozco la app -> abrir",
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_es(h, "abre", "abrir", "inicia")
            and h.tiene_alias_app
        ),
        accion="abrir_aplicacion",
        prioridad=100,
    ),
    Regla(
        id="abrir_sin_app",
        descripcion="SI parse ok Y verbo abre pero no dijeron app -> pedirla",
        condiciones=lambda h: (
            h.parse_valido
            and _verbo_es(h, "abre", "abrir", "inicia")
            and not h.tiene_alias_app
        ),
        accion="pedir_aplicacion",
        prioridad=90,
    ),
    Regla(
        id="verbo_sin_accion",
        descripcion="SI parse ok pero nadie mas aplazo -> avisar",
        condiciones=lambda h: h.parse_valido and h.verbo is not None,
        accion="verbo_sin_accion",
        prioridad=1,
    ),
]


def listar_reglas() -> None:
    print("\n--- Reglas cargadas ---")
    for r in sorted(REGLAS, key=lambda x: (-x.prioridad, x.id)):
        print(f"  [{r.prioridad}] {r.id}: {r.descripcion}")
    print("---\n")
