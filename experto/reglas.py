# Reglas de produccion del sistema experto.
# Formato clasico:
#   SI se cumplen las condiciones ENTONCES disparo esta accion
#
# Ejemplo:
#   SI parse_valido Y verbo=reproduce Y hay objeto
#   ENTONCES reproducir_youtube
#
# Para ampliar en clase:
#   1) agrega otra Regla a la lista REGLAS
#   2) si la accion es nueva, registrala en motor.py (diccionario ACCIONES)

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from experto.hechos import HechosComando


@dataclass(frozen=True)
class Regla:
    id: str
    descripcion: str
    # condiciones es una funcion que recibe hechos y regresa True/False
    condiciones: Callable[[HechosComando], bool]
    # nombre de la accion (tiene que existir en motor.ACCIONES)
    accion: str
    # si varias reglas aplican, gana la de prioridad mas alta
    prioridad: int = 10


def _verbo_es(h: HechosComando, *ops: str) -> bool:
    # Atajo para no repetir "h.verbo in (...)" en cada regla
    return h.verbo is not None and h.verbo in ops


# Lista de reglas. El motor las ordena por prioridad (de mayor a menor).
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
    # Esta va al final a proposito (prioridad baja).
    # Si el parse esta bien pero ninguna regla de arriba aplico, avisamos.
    Regla(
        id="verbo_sin_accion",
        descripcion="SI parse ok pero nadie mas aplico -> avisar",
        condiciones=lambda h: h.parse_valido and h.verbo is not None,
        accion="verbo_sin_accion",
        prioridad=1,
    ),
]


def listar_reglas() -> None:
    # Imprime las reglas al arrancar (sirve para la demo en clase)
    print("\n--- Reglas cargadas ---")
    for r in sorted(REGLAS, key=lambda x: (-x.prioridad, x.id)):
        print(f"  [{r.prioridad}] {r.id}: {r.descripcion}")
    print("---\n")
