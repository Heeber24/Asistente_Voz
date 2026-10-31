# Analizador sintactico con gramatica libre de contexto (CFG) usando NLTK.
#
# Idea del proyecto:
#   - Si la frase NO encaja en la gramatica -> no inventamos respuesta
#   - Si SI encaja -> armamos hechos y el sistema experto decide que hacer
#
# Flujo interno:
#   1) Checar errores obvios (falta wake word, falta verbo, etc.)
#   2) Armar una "plantilla" para el parser
#   3) Pedirle al ChartParser que genere el arbol
#   4) Si hay arbol, lo imprimimos para que se vea en clase

from __future__ import annotations

from dataclasses import dataclass, field

import nltk
from nltk.tree import Tree

from config import (
    APPS_LEXICO,
    DETERMINANTES,
    MOSTRAR_ARBOL,
    VERBOS,
    VERBOS_OBJETO_ABIERTO,
    WAKE_WORDS,
)


@dataclass
class AnalisisSintactico:
    # Resultado del analisis. Esto luego se convierte en hechos.
    valido: bool
    tokens: list[str] = field(default_factory=list)
    plantilla: list[str] = field(default_factory=list)
    wake: str | None = None
    verbo: str | None = None
    objeto_tokens: list[str] = field(default_factory=list)
    arbol: Tree | None = None
    arbol_texto: str = ""
    codigo_error: str | None = None
    mensaje_error: str | None = None


def _alts(palabras) -> str:
    # Convierte un set de palabras en: 'alexa' | 'siri' | 'google'
    # Asi lo podemos pegar directo en el string de la CFG
    return " | ".join(f"'{p}'" for p in sorted(palabras))


def construir_gramatica_texto() -> str:
    # Armamos la CFG leyendo el lexico de config.py
    # Asi no tienes que editar dos lados cuando agregas un verbo o una app.
    #
    # Producciones en corto:
    #   S   = wake + sintagma verbal
    #   VP  = verbo solo | verbo + objeto libre | verbo + (el/la) + app
    #   OBJ = comodin __objeto__ para "reproduce X" / "busca Y"
    return f"""
S -> AV VP
AV -> {_alts(WAKE_WORDS)}
VP -> V | V OBJ | V DET N | V N
DET -> {_alts(DETERMINANTES)}
N -> {_alts(APPS_LEXICO)}
V -> {_alts(VERBOS)}
OBJ -> '__objeto__'
""".strip()


# Parser global: se crea una vez al importar el modulo
_parser = nltk.ChartParser(nltk.CFG.fromstring(construir_gramatica_texto()))


def gramatica_actual() -> str:
    # Por si quieres imprimir la CFG en consola
    return construir_gramatica_texto()


def _indice_verbo(tokens: list[str]) -> int | None:
    # Busca el primer verbo despues de la wake word
    for i, tok in enumerate(tokens[1:], start=1):
        if tok in VERBOS:
            return i
    return None


def _error_previo(tokens: list[str]) -> AnalisisSintactico | None:
    # Antes de llamar al parser revisamos fallos faciles.
    # Asi el mensaje de error se entiende mejor en clase.

    if not tokens:
        return AnalisisSintactico(
            valido=False,
            codigo_error="SIN_TOKENS",
            mensaje_error="No recibí ninguna palabra para analizar.",
        )

    # Tiene que empezar con alexa / siri / google / cortana
    if tokens[0] not in WAKE_WORDS:
        wakes = ", ".join(sorted(WAKE_WORDS))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            codigo_error="FALTA_WAKE",
            mensaje_error=f"Empieza con una palabra de activacion ({wakes}).",
        )

    # Despues de la wake word debe venir un verbo conocido
    vi = _indice_verbo(tokens)
    if vi is None:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            codigo_error="SIN_VERBO",
            mensaje_error=f"No encontre un verbo conocido. Usa: {', '.join(sorted(VERBOS))}.",
        )

    # reproduce/busca necesitan decir QUE reproducir o buscar
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_OBJETO_ABIERTO and not cola:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            verbo=verbo,
            codigo_error="OBJETO_VACIO",
            mensaje_error=f"Despues de «{verbo}» tienes que decir que reproducir o buscar.",
        )

    # Si llegamos aqui, vale la pena intentar el parseo
    return None


def _plantilla(tokens: list[str]) -> tuple[list[str], str, list[str]]:
    # Prepara lo que realmente se le manda al parser.
    #
    # Caso abierto (reproduce / busca):
    #   "alexa reproduce luis miguel"  ->  ["alexa", "reproduce", "__objeto__"]
    # Asi no tenemos que meter todas las canciones del mundo en la CFG.
    #
    # Caso cerrado (abre):
    #   se parsea tal cual, porque las apps SI estan en el lexico N
    vi = _indice_verbo(tokens)
    assert vi is not None
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]

    if verbo in VERBOS_OBJETO_ABIERTO:
        return [tokens[0], verbo, "__objeto__"], verbo, cola

    return tokens, verbo, cola


def analizar_comando(
    tokens: list[str],
    *,
    mostrar_arbol: bool | None = None,
) -> AnalisisSintactico:
    # Funcion principal del modulo. La llama el agente.

    # Paso 1: errores obvios
    previo = _error_previo(tokens)
    if previo is not None:
        return previo

    # Paso 2: plantilla + verbo + cola
    plantilla, verbo, cola = _plantilla(tokens)
    wake = tokens[0]

    # Paso 3: pedir arboles al ChartParser de NLTK
    try:
        arboles = list(_parser.parse(plantilla))
    except (ValueError, RuntimeError) as e:
        # El detalle tecnico se queda en consola; al usuario le decimos algo simple
        print(f"(Debug parser) {e}")
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="ERROR_PARSER",
            mensaje_error="No pude entender esa peticion. Intentalo de nuevo con otra frase.",
        )

    # Si no salio ningun arbol, la frase no esta en el lenguaje de la CFG
    if not arboles:
        apps = ", ".join(sorted(APPS_LEXICO))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="FUERA_DE_GRAMATICA",
            mensaje_error=(
                f"La frase no cuadra con la gramatica. "
                f"Si usas «abre», prueba: {apps}."
            ),
        )

    # Paso 4: nos quedamos con el primer arbol y lo mostramos
    arbol = arboles[0]
    arbol_texto = arbol.pformat(margin=70)

    ver = MOSTRAR_ARBOL if mostrar_arbol is None else mostrar_arbol
    if ver:
        print("\n--- Arbol sintactico ---")
        print(f"Original : {' '.join(tokens)}")
        print(f"Plantilla: {' '.join(plantilla)}")
        print(arbol_texto)
        print("--- fin arbol ---\n")

    return AnalisisSintactico(
        valido=True,
        tokens=tokens,
        plantilla=plantilla,
        wake=wake,
        verbo=verbo,
        objeto_tokens=cola,
        arbol=arbol,
        arbol_texto=arbol_texto,
    )
