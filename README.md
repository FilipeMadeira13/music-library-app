# Biblioteca pessoal de álbuns

Fundação de desenvolvimento do monólito aprovado em [ARCHITECTURE.md](ARCHITECTURE.md). Ainda não existem modelos, páginas ou operações de negócio. A URL `/` retorna **404**, inclusive com o servidor funcionando. As fontes de requisitos são [PROJECT_SCOPE.md](PROJECT_SCOPE.md) e [REQUIREMENTS.md](REQUIREMENTS.md).

## Pré-requisitos

- Python **3.13.16**, patch da linha aprovada verificado em 15/10/2026 ([Python oficial](https://www.python.org/downloads/)). `.python-version` registra essa versão; não instala o interpretador automaticamente.
- Git e acesso ao PyPI para instalar dependências. Não são necessários Node, Docker ou um serviço de banco de dados.
- SQLite fornecido pelo Python, com banco em disco local, fora de pasta sincronizada/rede.

A aplicação usa Django **5.2.18 LTS**, patch consultado na [tabela oficial](https://www.djangoproject.com/download/), HTTPX, Waitress e WhiteNoise. Ferramentas de desenvolvimento: runner Django/unittest, Playwright, Ruff, mypy/django-stubs, coverage e pip-tools. `tzdata` disponibiliza o fuso IANA também em sistemas sem essa base.

## Instalação (Linux/macOS, Bash)

Neste workspace, `.venv` usa o Python 3.13.16 preparado em `.python/bin/python3.13`; ambos são locais e ignorados pelo Git. Para novos checkouts, instale esse interpretador antes dos passos abaixo.

Na raiz do checkout, com Python 3.13.16 instalado:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --require-hashes -r requirements-dev.txt
umask 077
install -d -m 700 var var/backups var/static
cp .env.example .env
chmod 600 .env
python - <<'PY'
from pathlib import Path
import secrets
p = Path('.env')
p.write_text(p.read_text().replace('DJANGO_SECRET_KEY=', 'DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64), 1))
PY
set -a
source .env
set +a
python manage.py check
python manage.py migrate
```

O último comando não cria tabelas de negócio nesta fundação. A pasta `var/` precisa existir antes do primeiro acesso SQLite e não é versionada. No Windows, use `py -3.13 -m venv .venv` e `.venv\Scripts\Activate.ps1`; configure as variáveis com `$env:NOME='valor'` no PowerShell e restrinja acesso à pasta pelo Windows. O `.env` fornecido usa sintaxe Bash; o Django não o carrega automaticamente.

Para instalar só execução, use `python -m pip install --require-hashes -r requirements.txt`. Não configure um segundo servidor para a mesma biblioteca.

## Configuração

| Variável | Uso / padrão |
| --- | --- |
| `DJANGO_SECRET_KEY` | Obrigatória; segredo aleatório de pelo menos 50 caracteres, gerado localmente. Sem fallback fixo. |
| `DJANGO_DEBUG` | `false`; aceita apenas `true`/`false`. Use `true` apenas no desenvolvimento. |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost`; lista separada por vírgulas de hosts/IPs específicos, sem curingas. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Vazia; quando necessária, lista de origens completas específicas, incluindo esquema e porta. |
| `DJANGO_TIME_ZONE` | `America/Fortaleza`; fuso IANA válido. |
| `LIBRARY_DATABASE_PATH` | Vazia usa `var/library.sqlite3`; alternativa exige caminho absoluto em disco local privado, fora de `var/static`, inclusive via link simbólico. |
| `MUSICBRAINZ_CONTACT` | Reservada para a futura integração, ainda não implementada. Preencher contato real antes de chamadas reais. |

`.env`, ambientes virtuais, banco, backups, caches e relatórios ficam fora do Git. `.env.example` contém somente exemplos, sem segredo. SQLite usa transações `IMMEDIATE`, timeout de 3 segundos e `ATOMIC_REQUESTS=False`. CSRF e autoescape permanecem ativos.

A inicialização recusa banco na árvore dos estáticos, também em subpastas ou por caminho com `..`/link simbólico. A escolha de disco local sem sincronização/rede e a proteção das permissões continuam sob responsabilidade do proprietário; a configuração não detecta esses tipos de armazenamento nem ajusta permissões automaticamente. Mantenha `umask 077` também no shell que iniciar o servidor e criar backups; proteja arquivos privados já existentes com modo 600 e diretórios com modo 700 (ou permissões equivalentes no Windows). O journal padrão é preservado, sem exigir WAL.

## Execução

Desenvolvimento, após carregar o ambiente:

```bash
export DJANGO_DEBUG=true
python manage.py runserver 127.0.0.1:8000
```

Execução local com a configuração cotidiana aprovada:

```bash
export DJANGO_DEBUG=false
python manage.py collectstatic --noinput
python -m waitress --host=127.0.0.1 --port=8000 --threads=4 config.wsgi:application
```

Encerre com `Ctrl+C`. Use um único processo e quatro threads. WhiteNoise serve somente `var/static/`, nunca o banco ou os backups. Nesta etapa não há assets da aplicação, portanto `collectstatic` pode informar zero arquivos. A implementação das páginas/estáticos e sua verificação funcional ocorrerá nas tarefas correspondentes.

Consulte [docs/operations.md](docs/operations.md) para configuração explícita de LAN e limitações operacionais.

## Verificações e TDD

```bash
source .venv/bin/activate
bash scripts/check.sh
```

O script gera um segredo efêmero apenas se não houver segredo exportado e executa:

1. Integridade das dependências (`pip check`).
2. Lint/análise estática (`ruff check`) e formatação (`ruff format --check`).
3. Tipagem estrita (`mypy`, com plugin Django).
4. Checks Django e ausência de migrações pendentes.
5. Runner Django/unittest com cobertura de ramos; relatórios terminal, XML e HTML.
6. `collectstatic`, smoke Waitress real em loopback/porta temporária com `DEBUG=False` e diagnóstico Python/SQLite/Django.

Os testes de configuração usam subprocessos para verificar erros antes da inicialização. Os testes HTTP não usam banco; o smoke verifica 404 sem traceback e inacessibilidade das URLs privadas. A BL-003 acrescenta testes puros de normalização Unicode em `library/tests/test_validation.py`, sem banco ou rede. Os relatórios `htmlcov/index.html` e `coverage.xml` são locais/ignorados; nenhuma meta numérica arbitrária foi introduzida. Avalie casos e ramos dos requisitos ao adicionar funcionalidades.

`library.validation.text_key(value)` produz a chave compartilhada para títulos e nomes: NFD → casefold → NFD → remoção de marcas Unicode e whitespace. Preserva pontuação, não translitera e lança `ValueError` se a chave ficar vazia. O chamador mantém a grafia original para exibição; equivalência de chaves apenas gera candidatos, sem comprovar identidade. Busca local e persistência serão conectadas nas respectivas tarefas; consulta vazia será tratada pelo fluxo de busca.

Para um ciclo TDD, carregue `.env`, escreva o teste e confirme a falha esperada; implemente o mínimo, execute o teste e refatore:

```bash
python manage.py test library.tests.test_environment --verbosity 2
python -m ruff format .
bash scripts/check.sh
```

Novos testes ficam em `library/tests/test_*.py`. O runner padrão deve descobri-los. Bancos/diretórios de teste sempre temporários; concorrência exige SQLite em arquivo com conexões independentes, conforme arquitetura. Integrações automatizadas devem ser simuladas, sem chamadas reais.

Playwright está nas dependências de desenvolvimento. Quando existirem percursos de navegador, prepare Chromium/Firefox:

```bash
python -m playwright install --with-deps chromium firefox
```

Esse comando pode exigir instalação de bibliotecas do SO. Não é necessário para as verificações atuais, que não possuem páginas/fluxos de navegador. Emulação móvel não substitui celular real.

## Atualização de dependências

As entradas `.in` registram dependências diretas e limites; os `.txt` fixam **todas** as versões transitivas e hashes. `requirements-dev.txt` contém também execução, sob as mesmas versões do lock de execução. Para atualizar, confirme versões/compatibilidade nas fontes oficiais, use Python 3.13.16 e a versão de pip-tools do lock de desenvolvimento:

```bash
python -m piptools compile --upgrade --generate-hashes --allow-unsafe --strip-extras --resolver=backtracking --output-file=requirements.txt requirements.in
python -m piptools compile --upgrade --generate-hashes --allow-unsafe --strip-extras --resolver=backtracking --output-file=requirements-dev.txt requirements-dev.in
python -m pip install --require-hashes -r requirements-dev.txt
bash scripts/check.sh
```

O arquivo de desenvolvimento inclui `-c requirements.txt`, garantindo as mesmas dependências de execução. Não edite os locks manualmente. Valide também instalação em um novo `venv`, sem reaproveitar os pacotes já instalados. Não use `pip freeze` para misturar pacotes alheios ao projeto.

## Estrutura e CI

- `config/`: settings, URLs e WSGI.
- `library/`: único app; módulos reservados, migrações, integrações, templates, estáticos e testes.
- `scripts/`: verificações, smoke e diagnóstico sem segredos.
- `docs/`: operação e registro de evidências.
- `var/`: dados privados locais e estáticos coletados, ignorados.
- [AGENTS.md](AGENTS.md): limites arquiteturais, TDD, testes e instruções para Codex.

A [CI do GitHub Actions](.github/workflows/ci.yml) executa em push/pull request com Python de `.python-version`, instalação com hashes, os mesmos checks locais e artefatos de cobertura. O segredo de testes é efêmero; não exige segredo no GitHub. Nenhuma publicação/deploy é configurada. O workflow remoto só pode ter resultado após ser executado no GitHub.

As evidências e limitações desta preparação estão em [docs/acceptance.md](docs/acceptance.md). A [BL-001 foi verificada em checkout limpo](docs/acceptance.md#bl-001--fundação-validada-em-checkout-limpo), com instalação em `venv` novo e execução dos checks completos. A [BL-002 verificou configuração local e arquivos privados](docs/acceptance.md#bl-002--configuração-local-e-arquivos-privados), incluindo recusa de banco na árvore de estáticos. A [BL-003 verificou a normalização textual](docs/acceptance.md#bl-003--normalização-de-títulos-e-nomes). As demais tarefas e o aceite funcional do MVP continuam pendentes.
