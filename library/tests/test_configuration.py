"""BL-002: configuração privada local (RNF-01/09, SEG-01/08/09, ADR-02/08)."""

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.test import SimpleTestCase


class ConfigurationTests(SimpleTestCase):
    def load_configuration(self, **overrides: str) -> subprocess.CompletedProcess[str]:
        environment = {
            name: value
            for name, value in os.environ.items()
            if not name.startswith(("DJANGO_", "LIBRARY_"))
        }
        environment.update({"DJANGO_SECRET_KEY": secrets.token_urlsafe(64), **overrides})
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "import json; import config.settings as s; "
                "print(json.dumps({key: getattr(s, key) for key in "
                "('DEBUG', 'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS', 'TIME_ZONE', "
                "'USE_TZ', 'DATABASES')}, default=str))",
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

    def test_database_inside_static_root_is_rejected(self) -> None:
        """SEG-08: banco não pode ficar na árvore pública do WhiteNoise."""
        for path in (
            settings.STATIC_ROOT,
            settings.STATIC_ROOT / "library.sqlite3",
            settings.STATIC_ROOT / "nested" / "library.sqlite3",
            settings.STATIC_ROOT.parent / "private" / ".." / "static" / "library.sqlite3",
        ):
            with self.subTest(path=path):
                result = self.load_configuration(LIBRARY_DATABASE_PATH=str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
                self.assertNotIn(str(path), result.stderr)

    def test_database_symlink_into_static_root_is_rejected(self) -> None:
        """SEG-08: um caminho alternativo não contorna a separação dos estáticos."""
        with TemporaryDirectory() as directory:
            alias = Path(directory) / "public-alias"
            alias.symlink_to(settings.STATIC_ROOT, target_is_directory=True)
            result = self.load_configuration(LIBRARY_DATABASE_PATH=str(alias / "library.sqlite3"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured", result.stderr)

    def test_default_configuration_is_private_and_local(self) -> None:
        """RNF-01, SEG-01/08, ADR-02/08: defaults sem depender do ambiente do runner."""
        result = self.load_configuration()
        self.assertEqual(result.returncode, 0, result.stderr)
        configuration = json.loads(result.stdout)
        self.assertEqual(configuration["TIME_ZONE"], "America/Fortaleza")
        self.assertTrue(configuration["USE_TZ"])
        self.assertFalse(configuration["DEBUG"])
        self.assertEqual(configuration["ALLOWED_HOSTS"], ["127.0.0.1", "localhost"])
        self.assertEqual(configuration["CSRF_TRUSTED_ORIGINS"], [])
        database = configuration["DATABASES"]["default"]
        self.assertEqual(database["NAME"], str(settings.BASE_DIR / "var" / "library.sqlite3"))
        self.assertEqual(database["ENGINE"], "django.db.backends.sqlite3")
        self.assertFalse(database["ATOMIC_REQUESTS"])
        self.assertEqual(database["OPTIONS"], {"transaction_mode": "IMMEDIATE", "timeout": 3})

    def test_explicit_local_configuration_is_loaded_without_creating_database(self) -> None:
        """BL-002: caminhos privados alternativos e opções explícitas válidas."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "library.sqlite3"
            result = self.load_configuration(
                LIBRARY_DATABASE_PATH=str(path),
                DJANGO_TIME_ZONE="UTC",
                DJANGO_DEBUG="true",
                DJANGO_ALLOWED_HOSTS=" localhost , 192.168.1.20 ",
                DJANGO_CSRF_TRUSTED_ORIGINS=" http://192.168.1.20:8000 , https://localhost:8443 ",
            )
            self.assertFalse(path.exists())
        self.assertEqual(result.returncode, 0, result.stderr)
        configuration = json.loads(result.stdout)
        self.assertEqual(configuration["DATABASES"]["default"]["NAME"], str(path))
        self.assertEqual(configuration["TIME_ZONE"], "UTC")
        self.assertTrue(configuration["DEBUG"])
        self.assertEqual(configuration["ALLOWED_HOSTS"], ["localhost", "192.168.1.20"])
        self.assertEqual(
            configuration["CSRF_TRUSTED_ORIGINS"],
            ["http://192.168.1.20:8000", "https://localhost:8443"],
        )

    def test_static_directory_name_does_not_block_private_sibling(self) -> None:
        path = settings.STATIC_ROOT.with_name("static-private") / "library.sqlite3"
        result = self.load_configuration(LIBRARY_DATABASE_PATH=str(path))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_secrets_are_rejected_without_echoing_them(self) -> None:
        """RNF-09, SEG-08: segredo ausente, curto ou repetitivo impede inicialização."""
        for secret in ("", "short-test-secret", "x" * 64):
            with self.subTest(kind="invalid secret", length=len(secret)):
                result = self.load_configuration(DJANGO_SECRET_KEY=secret)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
                if secret:
                    self.assertNotIn(secret, result.stdout + result.stderr)
