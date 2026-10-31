"""Gramática libre de contexto (CFG) NLTK: validación y árbol sintáctico.

Flujo didáctico
---------------
1. El texto ya normalizado llega como lista de tokens.
2. Se construye una *plantilla* de parseo (para verbos de objeto abierto
   la cola se resume en el comodín ``__objeto__``; el resto se parsea literal).
3. ``ChartParser`` intenta generar uno o más árboles. Si hay árbol → frase válida.
4. Se imprime el árbol para que el estudiante vea cómo el parser estructura la frase.

Ampliación en clase
-------------------
- Añade terminales en ``config.WAKE_WORDS`` / ``VERBOS`` / ``APPS_LEXICO``.
- O añade producciones a mano en ``_producciones_extra()`` si necesitas
  patrones más ricos (p. ej. ``VP -> V PREP N``).
La CFG se regenera desde la config para no desalinear vocabulario y reglas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import nltk
from nltk.tree import Tree

from config import (
    APPS_LEXICO,
    DETERMINANTES,
    MOSTRAR_ARBOL_PARSE,
    VERBOS,
    VERBOS_OBJETO_ABIERTO,
    WAKE_WORDS,
)


@dataclass
class AnalisisSintactico:
    """Resultado del analizador sintáctico (lo que alimenta la base de hechos)."""

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


def _alts(palabras: frozenset[str] | set[str] | list[str]) -> str:
    return " | ".join(f"'{p}'" for p in sorted(palabras))


def _producciones_extra() -> str:
    """Hueco para que el estudiante añada producciones CFG a mano."""
    return ""


def construir_gramatica_texto() -> str:
    """Arma el string CFG a partir de config (wake, verbos, apps, determinantes)."""
    av = _alts(WAKE_WORDS)
    v = _alts(VERBOS)
    det = _alts(DETERMINANTES) if DETERMINANTES else "'el'"
    apps = _alts(APPS_LEXICO) if APPS_LEXICO else "'notepad'"
    extra = _producciones_extra().strip()
    bloque_extra = f"\n{extra}" if extra else ""
    # S  → wake + sintagma verbal
    # VP → solo verbo | verbo + objeto abierto | verbo + (det) + app del léxico cerrado
    # OBJ → comodín para consultas libres (YouTube / Google)
    return f"""
S -> AV VP
AV -> {av}
VP -> V | V OBJ | V DET N | V N
DET -> {det}
N -> {apps}
V -> {v}
OBJ -> '__objeto__'
{bloque_extra}
""".strip()


def _cargar_parser() -> tuple[nltk.CFG, nltk.ChartParser]:
    texto = construir_gramatica_texto()
    cfg = nltk.CFG.fromstring(texto)
    return cfg, nltk.ChartParser(cfg)


_gramatica, _parser = _cargar_parser()


def recargar_gramatica() -> None:
    """Vuelve a leer la CFG (útil si en clase mutan config y quieren reintentar)."""
    global _gramatica, _parser
    _gramatica, _parser = _cargar_parser()


def gramatica_actual() -> str:
    """Texto de la CFG vigente (para imprimir en consola / demos)."""
    return construir_gramatica_texto()


def _indice_primer_verbo(tokens: list[str]) -> int | None:
    for i, tok in enumerate(tokens[1:], start=1):
        if tok in VERBOS:
            return i
    return None


def _diagnosticar_antes_de_parsear(tokens: list[str]) -> AnalisisSintactico | None:
    """Errores claros *antes* de invocar al ChartParser (mejor para el aula)."""
    if not tokens:
        return AnalisisSintactico(
            valido=False,
            codigo_error="SIN_TOKENS",
            mensaje_error="No recibí ninguna palabra para analizar.",
        )
    if tokens[0] not in WAKE_WORDS:
        muestra = " ".join(tokens[:12]) + ("…" if len(tokens) > 12 else "")
        wakes = ", ".join(sorted(WAKE_WORDS))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            codigo_error="FALTA_WAKE",
            mensaje_error=(
                f"La frase debe empezar con una palabra de activación ({wakes}). "
                f"Transcripción: {muestra}"
            ),
        )
    vi = _indice_primer_verbo(tokens)
    if vi is None:
        verbos = ", ".join(sorted(VERBOS))
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            codigo_error="SIN_VERBO",
            mensaje_error=(
                f"Tras «{tokens[0]}» no hay un verbo reconocido. "
                f"Verbos permitidos: {verbos}."
            ),
        )
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_OBJETO_ABIERTO and not cola:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            wake=tokens[0],
            verbo=verbo,
            codigo_error="OBJETO_VACIO",
            mensaje_error=(
                f"El verbo «{verbo}» necesita un complemento "
                f"(qué reproducir o qué buscar)."
            ),
        )
    return None


def _tokens_para_parser(tokens: list[str]) -> tuple[list[str], str, list[str]]:
    """Devuelve (plantilla, verbo, cola_objeto)."""
    vi = _indice_primer_verbo(tokens)
    assert vi is not None
    verbo = tokens[vi]
    cola = tokens[vi + 1 :]
    if verbo in VERBOS_OBJETO_ABIERTO:
        return [tokens[0], verbo, "__objeto__"], verbo, cola
    return tokens, verbo, cola


def _arbol_a_texto(arbol: Tree) -> str:
    return arbol.pformat(margin=70)


def _mensaje_fuera_de_gramatica(
    tokens: list[str], plantilla: list[str], verbo: str, cola: list[str]
) -> str:
    desconocidos = [t for t in plantilla if t not in _vocabulario_terminal()]
    if desconocidos:
        return (
            f"Hay palabras fuera del léxico de la gramática: {', '.join(desconocidos)}. "
            f"Para «{verbo}» con apps usa: {', '.join(sorted(APPS_LEXICO))}."
        )
    if verbo not in VERBOS_OBJETO_ABIERTO and cola:
        apps = ", ".join(sorted(APPS_LEXICO))
        return (
            f"La secuencia «{' '.join(tokens)}» no encaja en la CFG. "
            f"Con «{verbo}» prueba un nombre del léxico cerrado ({apps}), "
            f"opcionalmente con el/la/los/las."
        )
    return (
        f"La frase no cuadra con la gramática libre de contexto programada "
        f"(plantilla intentada: {' '.join(plantilla)})."
    )


def _vocabulario_terminal() -> set[str]:
    outs: set[str] = set(WAKE_WORDS) | set(VERBOS) | set(APPS_LEXICO) | set(DETERMINANTES)
    outs.add("__objeto__")
    return outs


def analizar_comando(
    tokens: list[str],
    *,
    mostrar_arbol: bool | None = None,
) -> AnalisisSintactico:
    """Analiza la frase: diagnóstico → plantilla → ChartParser → árbol o error."""
    previo = _diagnosticar_antes_de_parsear(tokens)
    if previo is not None:
        return previo

    plantilla, verbo, cola = _tokens_para_parser(tokens)
    wake = tokens[0]
    try:
        arboles = list(_parser.parse(plantilla))
    except (ValueError, RuntimeError) as e:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="ERROR_PARSER",
            mensaje_error=f"El analizador sintáctico falló: {e}",
        )

    if not arboles:
        return AnalisisSintactico(
            valido=False,
            tokens=tokens,
            plantilla=plantilla,
            wake=wake,
            verbo=verbo,
            objeto_tokens=cola,
            codigo_error="FUERA_DE_GRAMATICA",
            mensaje_error=_mensaje_fuera_de_gramatica(tokens, plantilla, verbo, cola),
        )

    arbol = arboles[0]
    arbol_texto = _arbol_a_texto(arbol)
    ver = mostrar_arbol if mostrar_arbol is not None else MOSTRAR_ARBOL_PARSE
    if ver:
        print("\n--- Árbol sintáctico (CFG / NLTK ChartParser) ---")
        print(f"Tokens originales : {' '.join(tokens)}")
        print(f"Plantilla parseada: {' '.join(plantilla)}")
        print(arbol_texto)
        if len(arboles) > 1:
            print(f"(Nota: el parser encontró {len(arboles)} árboles; se usa el primero.)")
        print("--- fin árbol ---\n")

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


# Compatibilidad con el nombre anterior (bool). Preferir analizar_comando().
def comando_valido_según_gramatica(tokens: list[str]) -> bool:
    return analizar_comando(tokens, mostrar_arbol=False).valido
