"""Verificações da fundação, sem banco real ou integrações externas."""

import os
import subprocess
import sys
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase


class EnvironmentTests(SimpleTestCase):
    def test_library_loads_without_business_models(self) -> None:
        self.assertEqual(list(apps.get_app_config("library").get_models()), [])

    def test_local_database_and_security_configuration(self) -> None:
        database = settings.DATABASES["default"]
        self.assertEqual(database["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(database["OPTIONS"], {"transaction_mode": "IMMEDIATE", "timeout": 3})
        self.assertFalse(database["ATOMIC_REQUESTS"])
        database_name = database["NAME"]
        assert isinstance(database_name, (str, Path))
        self.assertTrue(Path(database_name).is_absolute())
        self.assertNotEqual(Path(database_name).parent, settings.STATIC_ROOT)
        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)
        self.assertEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 256 * 1024)

    def test_private_paths_are_not_served(self) -> None:
        for path in ("/var/library.sqlite3", "/var/backups/copy.sqlite3", "/.env"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertNotContains(response, "Traceback", status_code=404)

    def test_invalid_environment_fails_before_starting(self) -> None:
        cases = [
            {"DJANGO_SECRET_KEY": ""},
            {"DJANGO_DEBUG": "maybe"},
            {"DJANGO_ALLOWED_HOSTS": "*"},
            {"DJANGO_ALLOWED_HOSTS": ".example.com"},
            {"DJANGO_ALLOWED_HOSTS": ""},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.example.com"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "http://localhost/path"},
            {"LIBRARY_DATABASE_PATH": "relative.sqlite3"},
            {"DJANGO_TIME_ZONE": "Invalid/Timezone"},
        ]
        for overrides in cases:
            with self.subTest(overrides=overrides):
                environment = {
                    **os.environ,
                    "DJANGO_SETTINGS_MODULE": "config.settings",
                    **overrides,
                }
                result = subprocess.run(
                    [sys.executable, "-c", "import django; django.setup()"],
                    cwd=Path(__file__).resolve().parents[2],
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)
