# Limpieza basica del texto que llega del reconocedor o del teclado.
# Lo pasamos a minusculas, sin acentos y lo partimos en palabras (tokens).

from __future__ import annotations

import string


def normalize(texto: str) -> str:
    if not texto:
        return ""
    s = texto.strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        s = s.replace(a, b)
    return s


def tokenizar(comando: str) -> list[str]:
    # Quitamos signos raros que a veces mete el STT
    basura = string.punctuation + "¿¡«»"
    return [t for t in (w.strip(basura) for w in comando.split()) if t]


def poner_wake_word_primera(
    tokens: list[str],
    wake_words: frozenset[str],
    *,
    verbos: frozenset[str],
) -> list[str]:
    # A veces Google pone primero el verbo y luego "alexa".
    # Aqui reordenamos para que la wake word quede al inicio.
    if not tokens or tokens[0] in wake_words:
        return tokens
    if tokens[0] not in verbos:
        return tokens

    for i, t in enumerate(tokens):
        if t in wake_words:
            verbo = tokens[0]
            return [tokens[i], verbo] + tokens[1:i] + tokens[i + 1 :]
    return tokens
