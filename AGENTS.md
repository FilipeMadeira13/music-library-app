# Instruções para o Codex

## Fontes e escopo

- Leia `PROJECT_SCOPE.md`, `REQUIREMENTS.md` e `ARCHITECTURE.md` antes de alterar comportamentos. Consulte `BACKLOG.md`, quando disponível, e identifique os RF/CA/RN/SEG e decisões aplicáveis à tarefa.
- Respeite as decisões aprovadas P-01–09 e ADR-01–11. Se houver contradição entre fontes, apresente a divergência antes de alterar a decisão; não substitua decisões silenciosamente.
- Nesta etapa só existe a fundação do ambiente. Não implemente funcionalidades de negócio sem uma tarefa que as autorize. Não declare o MVP aceito com base nas verificações da fundação.
- Preserve alterações existentes do usuário. Não faça commit, push ou publicação sem solicitação.

## Arquitetura

- Python 3.13, Django 5.2 LTS, um app `library`, SQLite local e templates HTML no servidor. Sem SPA, API pública, PostgreSQL, Redis, Celery ou build Node no MVP.
- Views adaptam HTTP; forms validam entrada; `services.py` coordena gravações transacionais; `queries.py` concentra consultas; `validation.py` contém regras puras. ORM direto, sem camadas genéricas de repositório.
- Não faça chamadas externas em models, renderização ou dentro de transações. Integrações usam HTTPX síncrono e respeitam limites, TLS, origens fixas e contato real da arquitetura.
- Preserve `ATOMIC_REQUESTS=False`, SQLite `IMMEDIATE`, timeout de 3 s, revisões e transações curtas. Testes de concorrência exigem SQLite temporário em arquivo e conexões independentes.
- Não acrescente admin/autenticação nem entidades fora do escopo. As rotas de negócio ainda serão criadas por tarefas próprias.

## TDD e testes

1. Para cada comportamento autorizado, escreva o menor teste que demonstre o requisito e execute-o para confirmar a falha esperada (vermelho).
2. Implemente o mínimo para passar (verde), execute o teste e regressões pertinentes.
3. Refatore preservando comportamento e reexecute as verificações afetadas.
4. Acrescente casos extremos gradualmente. Não escreva todos os testes depois da implementação nem use testes que só repitam a implementação.
5. Infraestrutura/documentação usam verificações reproduzíveis; não invente regras de negócio ou testes artificiais para aumentar cobertura.

Use `unittest`, `unittest.mock` e o runner Django. Testes ficam em `library/tests/test_*.py`; a descoberta deve funcionar com `python manage.py test`. Use `SimpleTestCase` sem banco, `TestCase` para ORM e `TransactionTestCase` para commits/concorrência reais. Nunca teste na biblioteca ou nos backups reais. Simule APIs com transporte HTTPX substituível; não acesse catálogos em testes. Relógio e aleatoriedade devem ser controláveis. Playwright é a ferramenta de navegador; emulação não comprova celular real/LAN.

## Comandos obrigatórios

Ative `.venv` e execute `bash scripts/check.sh` antes de concluir alterações de código/configuração. O script roda dependências, Ruff, formatação, mypy estrito, checks Django, migrações pendentes, testes, coverage, collectstatic, smoke Waitress e diagnóstico. Para um ciclo TDD curto: `python manage.py test library.tests.test_modulo.Classe.test_caso` com `DJANGO_SECRET_KEY` no ambiente.

Novos models exigem migrações versionadas e `makemigrations --check --dry-run` aprovado. Mudanças em fluxos de navegador exigem os testes Playwright pertinentes, com Chromium/Firefox instalados. Reporte comandos, resultados e impedimentos reais; não chame testes não executados de aprovados. Avalie cobertura de ramos e casos do requisito; porcentagem isolada não demonstra aceite.

## Dependências, segurança e documentação

- Use `venv` e `pip`. Edite `requirements.in`/`requirements-dev.in`, regenere ambos os arquivos `.txt` com `pip-compile --generate-hashes --allow-unsafe` conforme README e verifique instalação limpa com `--require-hashes`. Não edite locks à mão. Mantenha dependências diretas e transitivas fixadas e confirme patches nas fontes oficiais.
- Use Ruff para lint/formatação e mypy estrito com django-stubs. Não desative verificações globalmente para esconder erros.
- Nunca grave segredos, `.env`, banco, backups ou respostas privadas no Git/logs. Exemplos de ambiente não contêm segredos. Mantenha CSRF, autoescape, hosts explícitos e bind loopback por padrão.
- WhiteNoise serve apenas `var/static`; nunca exponha `var` inteira. Um único processo Waitress com quatro threads; LAN só por configuração explícita conforme arquitetura.
- Atualize README/documentação afetada. Registre evidências e limites em `docs/acceptance.md`; contato externo, backup real, celular e medições continuam pendentes até verificação própria.
