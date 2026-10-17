"""Regras puras compartilhadas por formulários, consultas e operações."""

import unicodedata


def text_key(value: str) -> str:
    """Normalize conforme §2.1; rejeite chave vazia com ValueError.

    A chave apenas localiza candidatos, sem comprovar identidade. O chamador
    mantém o texto original para exibição; não há transliteração.
    """
    decomposed = unicodedata.normalize("NFD", value)
    folded = unicodedata.normalize("NFD", decomposed.casefold())
    key = "".join(
        character
        for character in folded
        if not unicodedata.category(character).startswith("M") and not character.isspace()
    )
    if not key:
        raise ValueError("O texto deve conter uma chave não vazia.")
    return key
