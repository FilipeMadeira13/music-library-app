"""Diagnóstico local sem imprimir variáveis de ambiente ou segredos."""

import platform
import sqlite3

import django

print(f"Python: {platform.python_version()}")
print(f"SQLite: {sqlite3.sqlite_version}")
print(f"Django: {django.get_version()}")
