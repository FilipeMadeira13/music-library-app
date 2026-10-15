"""Verifica Waitress com DEBUG=False, sem acessar a biblioteca real."""

import os
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def main() -> None:
    environment = {**os.environ, "DJANGO_DEBUG": "false", "DJANGO_ALLOWED_HOSTS": "127.0.0.1"}
    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "waitress",
            "--host=127.0.0.1",
            f"--port={port}",
            "--threads=4",
            "config.wsgi:application",
        ],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 10
        while True:
            if process.poll() is not None:
                raise RuntimeError("Waitress encerrou antes de responder.")
            try:
                urlopen(f"http://127.0.0.1:{port}/", timeout=1).close()
            except HTTPError as response:
                if response.code != 404:
                    raise RuntimeError(f"Status inesperado: {response.code}") from response
                response.close()
                break
            except URLError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Waitress não respondeu em 10 segundos.") from None
                time.sleep(0.1)
            else:
                raise RuntimeError("A fundação ainda não deve ter rota de negócio em /.")
        for path in ("/", "/var/library.sqlite3", "/var/backups/copy.sqlite3", "/.env"):
            try:
                urlopen(f"http://127.0.0.1:{port}{path}", timeout=2).close()
            except HTTPError as response:
                body = response.read()
                response.close()
                if response.code != 404 or b"Traceback" in body:
                    raise RuntimeError(f"Resposta insegura ou inesperada em {path}.") from response
            else:
                raise RuntimeError(f"Caminho privado ou não implementado acessível: {path}")
        print(
            "Smoke Waitress: OK (loopback, quatro threads, DEBUG=False, 404 e caminhos privados)."
        )
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
