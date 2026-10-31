# Utilidades de texto.
# El reconocedor (o el teclado) nos tira la frase "cruda".
# Aqui la dejamos pareja: minusculas, sin acentos, partida en tokens.

from __future__ import annotations

import string


def normalize(texto: str) -> str:
    # Minusculas + sin acentos para que "Alexá" y "alexa" coincidan
    if not texto:
        return ""
    s = texto.strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        s = s.replace(a, b)
    return s


def tokenizar(comando: str) -> list[str]:
    # Parte la frase en palabras y les quita signos raros (?, !, comillas, etc.)
    basura = string.punctuation + "¿¡«»"
    partes = []
    for palabra in comando.split():
        limpia = palabra.strip(basura)
        if limpia:
            partes.append(limpia)
    return partes


def poner_wake_word_primera(
    tokens: list[str],
    wake_words: frozenset[str],
    *,
    verbos: frozenset[str],
) -> list[str]:
    # A veces Google transcribe al reves: "reproduce alexa luis miguel".
    # Si el primer token es un verbo y mas adelante viene la wake word,
    # la movemos al frente para que la CFG la acepte.
    if not tokens or tokens[0] in wake_words:
        return tokens

    # Si ni siquiera empieza con verbo, no tocamos nada
    if tokens[0] not in verbos:
        return tokens

    for i, t in enumerate(tokens):
        if t in wake_words:
            verbo = tokens[0]
            # wake + verbo + lo que habia entre medio + el resto
            return [tokens[i], verbo] + tokens[1:i] + tokens[i + 1 :]

    return tokens
