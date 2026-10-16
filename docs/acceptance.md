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

## BL-001 — Fundação validada em checkout limpo

**Estado: aprovado**, em 15/10/2026 (America/Fortaleza), somente para BL-001/D0. O usuário aprovou explicitamente a execução desta tarefa nesta sessão. As seções anteriores preservam o registro da preparação inicial; a conclusão de BL-001 decorre das verificações abaixo. BL-002 e as demais tarefas continuam planejadas.

**Rastreabilidade:** recorte de ambiente de RNF-01; arquitetura §§2–4; ADR-01/03/10; suíte operacional O-ENV de TEST_STRATEGY.md. RNF-01 completo depende das páginas, persistência e LAN/celular das tarefas futuras. Nenhum CA funcional ou aceite geral de SEG/P é declarado aprovado por estas verificações.

**Versão e isolamento:** commit-base `4d89e7a9c4819825ffccb19cbd34f874dabe5a60` (`Cria estratégia de testes`), workspace inicialmente limpo. Clone local independente com `--no-hardlinks` em `/tmp/music-library-bl001-zQwR85/checkout`, também inicialmente limpo. Criado novo `.venv` com `include-system-site-packages = false`, sem reutilizar os pacotes do ambiente original. O interpretador previamente instalado foi reutilizado, conforme o pré-requisito do README; sua compilação não foi repetida.

**Ambiente observado:** Linux/WSL2 x86_64, kernel `6.6.87.2-microsoft-standard-WSL2`, glibc 2.39; Python 3.13.16, SQLite 3.45.1 e Django 5.2.18, iguais no workspace e no clone. Não foi usado dataset de álbuns. Configuração, segredo gerado localmente e eventual arquivo SQLite do ensaio de instalação ficaram no clone temporário; os testes informaram banco não utilizado.

**Patches e locks:** reconfirmados Python 3.13.16 na [lista oficial](https://www.python.org/downloads/) e na [publicação da versão](https://www.python.org/downloads/release/python-31316/), e Django 5.2.18 na [tabela oficial de suporte](https://www.djangoproject.com/download/). Consultadas também as publicações de [HTTPX 0.28.1](https://pypi.org/project/httpx/0.28.1/), [Waitress 3.0.2](https://pypi.org/project/waitress/3.0.2/), [WhiteNoise 6.12.0](https://pypi.org/project/whitenoise/6.12.0/) e [tzdata](https://pypi.org/project/tzdata/). Não houve atualização de dependências nem edição dos locks. Inspeção reproduzida com `re`/`pathlib`: 13 entradas de execução e 34 de desenvolvimento, todas com `==` e hashes SHA-256; as 13 versões de execução coincidem entre os locks. Após instalar, `importlib.metadata.version` confirmou cada versão dos dois arquivos no novo ambiente. A instalação com hashes e `pip check` verificaram a resolução fixada para Python 3.13.

### Preparação reproduzida

Na raiz do workspace, foram executados os seguintes comandos, cada um com saída zero, salvo o bloqueio de rede descrito adiante:

```bash
mktemp -d /tmp/music-library-bl001-XXXXXX
# Diretório retornado nesta execução: /tmp/music-library-bl001-zQwR85
git clone --no-hardlinks /home/cfili/Projetos/music-library-app /tmp/music-library-bl001-zQwR85/checkout
cd /tmp/music-library-bl001-zQwR85/checkout
/home/cfili/Projetos/music-library-app/.python/bin/python3.13 -m venv .venv
.venv/bin/python -m pip install --no-cache-dir --require-hashes -r requirements-dev.txt
source .venv/bin/activate
```

Em seguida foram reproduzidos os passos do README: criação de `var`, `var/backups` e `var/static` com modo 700; cópia de `.env.example` para `.env` com modo 600; geração de segredo aleatório com `secrets.token_urlsafe(64)` sem exibir seu valor; carregamento com `set -a`, `source .env`, `set +a`. O segredo não foi registrado nem versionado.

### Comandos e resultados

| Local / verificação | Comando | Esperado e observado |
| --- | --- | --- |
| Clone / instalação nova | `python -m pip install --no-cache-dir --require-hashes -r requirements-dev.txt` | Aprovado: pacotes instalados do PyPI com hashes, sem erro de compatibilidade; pip fixado já fornecido pelo novo venv. Não foi feita instalação separada do lock de execução. |
| Clone / configuração | `python manage.py check` | Aprovado: zero problemas. |
| Clone / preparação do banco | `python manage.py migrate` | Aprovado: nenhuma migração a aplicar; não existem modelos de negócio. |
| Clone / descoberta nativa | `python manage.py test --verbosity 2` | Aprovado: quatro testes descobertos e aprovados em 2,688 s, banco não utilizado. |
| Clone / versões | `python scripts/diagnostics.py` | Aprovado: Python 3.13.16, SQLite 3.45.1, Django 5.2.18. |
| Workspace / regressão integrada | `source .venv/bin/activate` e `bash scripts/check.sh` | Aprovado, saída 0: pip check, Ruff, 34 arquivos formatados, mypy estrito em 25 arquivos, checks Django, migrações, quatro testes em 4,816 s, collectstatic e smoke Waitress. |
| Clone / regressão integrada | `source .venv/bin/activate` e `bash scripts/check.sh` | Aprovado, saída 0: mesmas etapas, quatro testes em 4,419 s e smoke Waitress real com quatro threads, loopback e `DEBUG=False`. |
| Workspace e clone / integridade inicial e após ensaio | `git status --short` | Saída vazia em ambos antes da atualização documental de encerramento. Os artefatos/segredos temporários não aparecem no Git. |
| Workspace / revisão documental final | `git diff --check` | Aprovado: sem erros de whitespace; diff restrito aos três documentos de encerramento. |

O teste existente `EnvironmentTests.test_library_loads_without_business_models` comprova o carregamento de `library` pelo runner, sem modelos de negócio, conforme BL-001. Os outros três testes existentes foram preservados e executados como regressões de configuração e HTTP. Inspeção da estrutura confirmou `config`, o único app `library`, migrações e módulos reservados, sem camadas genéricas ou implementação de negócio.

**Red/Green/Refactor:** não se aplica um novo ciclo de comportamento: a fundação já existia e nenhum comportamento ausente foi encontrado. Conforme a exceção de infraestrutura da skill complete-tdd e do backlog, foram usadas verificações reproduzíveis, sem fabricar falha ou acrescentar testes artificiais. Não houve criação de testes, alteração de código ou refatoração. As aprovações acima são evidências da infraestrutura existente, não um Green posterior a um Red nesta sessão.

**Falhas de ambiente resolvidas:** a primeira instalação no sandbox saiu com código 1 por DNS bloqueado para `pypi.org`; a repetição autorizada fora do sandbox terminou com código 0. Os primeiros checks integrados, no workspace e no clone, saíram com código 1 ao abrir socket (`PermissionError`); as repetições autorizadas fora do sandbox terminaram com código 0. Essas falhas não são Red de TDD. O aviso de cache pip indisponível no sandbox não impediu `pip check`.

**Cobertura e limites:** relatórios combinados de ambos os checks: 99%, 58 instruções e 12 ramos, com um ramo parcial na iteração de origens CSRF (`config/settings.py`, `38->36`). O aviso `no-data-collected` veio do processo auxiliar do smoke; WSGI foi medido no filho, com 100%. Não há lacuna no carregamento do app identificada por esse ramo, nem conclusão de BL-002. A porcentagem não comprova requisitos funcionais. Sem fluxos de navegador nesta tarefa, Playwright/Chromium/Firefox não foram executados/instalados. CI remota, catálogos reais, backup, celular/LAN e medições de uso/desempenho continuam não executados nesta tarefa.

**Encerramento de D0:** critérios de BL-001 comprovados, checks e regressões aplicáveis aprovados, escopo arquitetural preservado e evidências registradas. Alterados somente `BACKLOG.md`, `README.md` e este registro; sem commit, push ou publicação. A tarefa encerra aqui, sem avançar para BL-002 e sem declarar o MVP aceito.

## BL-002 — Configuração local e arquivos privados

**Data:** 15/10/2026, America/Fortaleza. **Aprovação:** resposta explícita “sim” do usuário à execução da BL-002 nesta sessão. **Estado:** concluída; aceite do MVP pendente. Base `ffbe696` com alterações locais desta tarefa, sem commit. Ambiente Linux x86_64, Python 3.13.16, SQLite 3.45.1 e Django 5.2.18, `.venv` existente. Nenhuma dependência alterada.

**Rastreabilidade:** RNF-01/09; SEG-01/08/09; arquitetura §§3/6.2/8; ADR-02/08. Não há RF/CA/RN de negócio implementado nesta tarefa. P-01–09 e ADR-01–11 preservados. BL-001 já concluída; nenhuma outra tarefa executada.

### Comportamento e ciclo Red → Green → Refactor

A fundação já tinha segredo externo obrigatório, fuso configurável com padrão `America/Fortaleza`, hosts explícitos sem curingas, configuração SQLite IMMEDIATE/timeout 3 s/`ATOMIC_REQUESTS=False`, `.gitignore`, `.env.example` sem segredo e instruções de proteção local. Esses comportamentos foram verificados, sem fabricar Red.

A lacuna encontrada foi aceitar `LIBRARY_DATABASE_PATH` dentro de `STATIC_ROOT`, contrariando SEG-08. Agora a inicialização lança `ImproperlyConfigured` com mensagem sem ecoar o caminho. A guarda verifica tanto a árvore informada quanto o destino resolvido, cobrindo subpastas, `..` e links simbólicos.

Comandos dos testes, após ativar `.venv` (segredo de teste efêmero gerado no ambiente, sem imprimir seu valor):

```bash
source .venv/bin/activate
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
python manage.py test library.tests.test_configuration.ConfigurationTests.test_database_inside_static_root_is_rejected --verbosity 2
python manage.py test library.tests.test_configuration library.tests.test_environment --verbosity 2
```

| Etapa | Resultado esperado e observado |
| --- | --- |
| Red, antes de alterar settings | Primeiro comando: saída 1, um teste com dois subcasos falhando em `assertNotEqual(result.returncode, 0)`, pois a configuração aceitava banco direto nos estáticos e em subpasta (`0 == 0`). Falha do comportamento, sem conexão ao banco. |
| Green, após guarda de caminhos | Segundo comando: saída 0, cinco testes aprovados em 2,747 s, incluindo o mesmo teste do Red. |
| Extremos e configurações existentes | Segundo comando novamente: saída 0, dez testes aprovados em 3,043 s. Acrescentados raiz dos estáticos, `..`, link simbólico temporário, pasta irmã `static-private`, defaults isolados do ambiente, configuração explícita válida e segredos inválidos. Esses casos passaram de primeira; não representam novos ciclos Red. |
| Refactor/verificação | `STATIC_ROOT` definido antes da guarda e caminho do banco compartilhado entre validação e backend; sem necessidade de abstração adicional. Ruff format ajustou quebra de linha. Checks completos após a formatação aprovaram os dez testes e demais regressões. |

Seis testes novos em `library/tests/test_configuration.py`, com `SimpleTestCase` e subprocessos de ambiente controlado. O snapshot emitido pelos subprocessos contém somente configurações selecionadas, nunca o segredo. Os quatro testes existentes foram preservados e executados, incluindo os ambientes inválidos e respostas HTTP privadas. Nenhum teste abriu biblioteca ou backup real; links simbólicos usam diretório temporário e apontam para a árvore pública sem criar banco nela.

### Privacidade e checks finais

Verificação reproduzível do Git executada via `subprocess.run`, com asserções de retorno/conteúdo:

```bash
git check-ignore --no-index --stdin <<'PATHS'
.env
.env.local
var/library.sqlite3
var/library.sqlite3-journal
var/backups/copy.sqlite3
var/backups/snapshot.backup
private/library.db
private/library.db-wal
PATHS
git ls-files -ci --exclude-standard
git ls-files --error-unmatch .env.example
git check-ignore --no-index .env.example
```

**Aprovado:** os oito caminhos privados foram ignorados; nenhum arquivo ignorado estava rastreado; `.env.example` estava rastreado e não ignorado (último comando retorna 1, esperado). Leitura somente de `.env.example` confirmou a linha `DJANGO_SECRET_KEY=` vazia. Nenhum segredo real foi lido/exibido. README e operação agora explicitam `umask 077`, modos 600/700, restrição de destino e limites da validação automática.

| Verificação | Resultado observado |
| --- | --- |
| `source .venv/bin/activate` e `bash scripts/check.sh` no sandbox | Interrompido com saída 1 no smoke: `PermissionError` ao criar socket. Antes disso, dependências, Ruff, 35 arquivos formatados, mypy estrito (26 arquivos), checks Django, migrações, dez testes (6,264 s) e collectstatic passaram. Não é Red. |
| Mesmo comando fora do sandbox, após autorização | **Aprovado**, saída 0: todas as etapas, dez testes em 6,146 s, sem uso de banco pelo runner, nenhuma migração pendente, collectstatic com zero assets e smoke Waitress real (loopback, quatro threads, `DEBUG=False`, 404 sem traceback e URLs privadas inacessíveis). Diagnóstico confirmou versões acima. |
| Cobertura combinada | 100% no recorte atual: 61 instruções, 14 ramos; nenhum ramo parcial em settings. Relatórios locais XML/HTML. O aviso `no-data-collected` do auxiliar do smoke não impediu a coleta WSGI no filho nem a conclusão dos checks. Percentual não comprova aceite funcional. |

**Limites:** não há detecção automática de armazenamento em rede/pasta sincronizada, imposição de permissões nem proteção contra um operador copiar ou criar links para arquivos privados nos estáticos. Essas responsabilidades estão documentadas. Journal padrão preservado, sem WAL obrigatório. Nenhum fluxo de navegador mudou; Playwright não foi executado. CI remota, contato externo, backup real, celular/LAN e medições continuam não executados nesta tarefa. Instalação limpa não foi repetida: dependências inalteradas, evidência própria na BL-001. Nenhum impedimento restante para BL-002.

**Arquivos alterados:** `config/settings.py`, `library/tests/test_configuration.py` (novo), `.env.example`, `README.md`, `docs/operations.md`, `BACKLOG.md` e este registro. D0 de BL-002 atendido com verificações aplicáveis aprovadas; nenhuma funcionalidade de negócio, commit, push ou publicação. A execução encerra nesta tarefa.
