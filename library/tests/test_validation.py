"""Regras puras de entrada, sem banco ou chamadas externas."""

from django.test import SimpleTestCase

from library import validation


class TextKeyTests(SimpleTestCase):
    def test_equivalent_spellings_share_key_without_changing_display(self) -> None:
        """BL-003, §2.1/DEC-07: acentos, caixa e espaços não mudam a chave."""
        spellings = ("ÁGUA", "agua", " A gua ", "A\u0301GUA")
        for original in spellings:
            with self.subTest(original=original):
                self.assertEqual(validation.text_key(original), "agua")
        self.assertEqual(spellings, ("ÁGUA", "agua", " A gua ", "A\u0301GUA"))

    def test_unicode_keys_preserve_punctuation_and_do_not_transliterate(self) -> None:
        """BL-003/U-TX: casefold, whitespace, colisões e pontuação de §2.1."""
        examples = (
            ("Straße", "strasse"),
            ("STRASSE", "strasse"),
            ("\u1f88", "αι"),  # NFD antes do casefold preserva o iota subscrito.
            ("A\t\n\r\v\f B", "ab"),
            ("A\u00a0\u1680\u2003\u2028\u2029\u202f\u205f\u3000B", "ab"),
            ("A B", "ab"),
            ("AB", "ab"),
            ("A-B", "a-b"),
            ("D’Água! (Vol. 2)", "d’agua!(vol.2)"),
            ("Ø Ł Æ", "øłæ"),
            ("東京", "東京"),
            ("Ａ", "ａ"),  # Sem decomposição de compatibilidade.
            ("A\u034f\ufe0f", "a"),  # Marcas com classe combinante zero.
            ("A\u200bB", "a\u200bb"),  # Zero-width space não é whitespace Unicode.
        )
        for original, expected in examples:
            with self.subTest(original=original):
                self.assertEqual(validation.text_key(original), expected)

    def test_empty_normalized_key_is_invalid(self) -> None:
        """BL-003/SEG-03: título/nome sem chave significativa é inválido."""
        for original in ("", " \t\n\u00a0", "\u0301\u0308", " \u0301\u034f\ufe0f\u3000"):
            with self.subTest(original=original), self.assertRaises(ValueError):
                validation.text_key(original)
