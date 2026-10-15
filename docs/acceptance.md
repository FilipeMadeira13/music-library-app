# Evidências da preparação do ambiente

**Data:** 15/10/2026 (America/Fortaleza). **Recorte:** ambiente de desenvolvimento, sem funcionalidades de negócio. Este registro não é aceite do MVP nem conclusão automática das tarefas do backlog.

## Ambiente verificado

- Linux x86_64; Python **3.13.16** compilado a partir do tarball oficial em `.python/`, com `.venv` recriado usando esse interpretador. O Python do sistema não foi alterado.
- SQLite **3.45.1**, Django **5.2.18**, HTTPX **0.28.1**, Waitress **3.0.2**, WhiteNoise **6.12.0**.
- Ruff **0.17.1**, mypy **2.4.0**, django-stubs **5.2.9**, coverage **7.16.2**, Playwright **1.64.0**, pip-tools **7.6.2**. Todas as dependências estão fixadas nos locks com hashes.
- Patches de Python/Django consultados nas fontes oficiais: [Python](https://www.python.org/downloads/) e [Django](https://www.djangoproject.com/download/).
- O Git já estava inicializado. `BACKLOG.md` já existia como arquivo não rastreado e foi preservado. Não houve commit, push ou execução remota de CI.

## Resultados executados

| Verificação | Comando / procedimento | Resultado |
| --- | --- | --- |
| Interpretador | `.venv/bin/python --version` | Python 3.13.16 |
| Instalação | `python -m pip install --no-cache-dir --require-hashes -r requirements-dev.txt` no ambiente recriado | Aprovada; dependências de execução/teste instaladas |
| Coerência dos locks | Comparação de nomes/versões fixas | 13 pacotes de execução presentes com versões idênticas entre os 34 pacotes do lock de desenvolvimento |
| Integridade | `python -m pip check` | Nenhuma dependência quebrada |
| Lint/análise estática | `python -m ruff check .` | Aprovado |
| Formatação | `python -m ruff format --check .` | 32 arquivos aprovados |
| Tipagem | `python -m mypy` | 25 arquivos sem problemas; modo estrito e plugin Django |
| Configuração Django | `python manage.py check` | Nenhum problema; nenhuma verificação silenciada |
| Migrações pendentes | `python manage.py makemigrations --check --dry-run` | Nenhuma alteração detectada; ainda não há modelos/migrações de negócio |
| Testes | `python -m coverage run manage.py test --verbosity 2` | 4 testes aprovados em 4,950 s; banco não utilizado |
| Estáticos | `python manage.py collectstatic --noinput` | Aprovado; zero arquivos de aplicação nesta etapa |
| Servidor real | Smoke com Waitress, loopback/porta temporária, quatro threads, `DEBUG=False` | Aprovado; `/` e URLs de arquivos privados respondem 404 sem traceback; processo encerrado ao final |
| Cobertura combinada | `coverage combine`, `coverage report`, `coverage xml`, `coverage html` | **99%** com ramos; 58 instruções executadas e um ramo não percorrido na validação de origens CSRF |
| Gitignore | `git check-ignore` sobre segredo, banco, backups, ambientes e relatórios | Privados/artefatos ignorados; `.env.example` versionável |
| Whitespace | `git diff --check` e comparação dos arquivos novos com `/dev/null` | Aprovado, sem alterar o backlog existente |
| Script Bash | `bash -n scripts/check.sh` | Sintaxe válida |

Os quatro testes verificam carregamento do app, configuração de banco/segurança, inacessibilidade de URLs privadas e rejeição de nove configurações inválidas em subprocessos. Esses subprocessos e o WSGI são incluídos na cobertura. A cobertura mede a pequena fundação existente; não indica cobertura dos requisitos funcionais futuros. Os módulos reservados não contêm implementação de negócio.

O comando integrado final foi `PATH="$PWD/.venv/bin:$PATH" bash scripts/check.sh`, com código de saída **0**. Os relatórios ficam em `coverage.xml` e `htmlcov/index.html`, ignorados pelo Git. Coverage emite um aviso de ausência de dados no processo auxiliar do smoke, que não importa a aplicação diretamente; o processo filho WSGI fornece os dados combinados (`config/wsgi.py`: 100%). Isso não impediu nenhum check.

A rede do sandbox bloqueou inicialmente a instalação via PyPI; a criação de sockets também foi bloqueada na primeira tentativa do smoke. Instalação e execução final foram realizadas com a permissão de ferramenta necessária, e ambas foram concluídas. Não há verificações pendentes por esses bloqueios.

## CI preparada

`.github/workflows/ci.yml` configura push/pull request, Python de `.python-version`, instalação com hashes, as mesmas verificações locais e upload dos relatórios. Nenhum resultado remoto é afirmado: o workflow ainda não foi executado no GitHub. Não há etapa de publicação.

## Pendências do aceite funcional

- Implementação e testes RF/CA/RN/INT/SEG por tarefa, inclusive modelos, transações, concorrência real, integrações simuladas e comandos de backup/restore.
- Assets e páginas reais, percursos Playwright em Chromium/Firefox; os binários de navegador não foram instalados porque não existem percursos nesta fundação.
- Contato real do MusicBrainz antes de chamadas reais, destino privado de backup antes de dados reais e ensaio de recuperação isolado.
- Identificação de CPU/RAM/disco, dataset de 1.000 álbuns, rede e celular real antes de medições conforme P-08; evidências de desempenho, usabilidade e LAN continuam pendentes.

Nenhum catálogo externo foi chamado, nenhuma coleção real foi alterada e o ambiente não foi publicado.
