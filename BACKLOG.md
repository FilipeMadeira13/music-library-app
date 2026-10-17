# Backlog de desenvolvimento — biblioteca pessoal de álbuns

**Data:** 16/10/2026. **Estado:** BL-001–BL-003 concluídas e verificadas; BL-004–BL-062 permanecem planejadas. O aceite do MVP continua pendente.

Fontes aprovadas: [escopo](PROJECT_SCOPE.md), [requisitos](REQUIREMENTS.md) e [arquitetura](ARCHITECTURE.md), incluindo decisões DEC/T, P-01–09 e ADR-01–11 aprovadas em 14/10/2026. As referências RF, CA, RN, RNF, SEG, INT e P abaixo pertencem a REQUIREMENTS.md; seções arquiteturais e ADR pertencem a ARCHITECTURE.md. Não há necessidade de reabrir decisões aprovadas.

## Como executar este backlog

- Todas as tarefas abaixo pertencem ao **MVP obrigatório**. A ordem favorece uma biblioteca local utilizável antes do enriquecimento externo; os marcos intermediários não significam MVP completo.
- A numeração é uma ordem válida de execução: toda dependência aponta para uma tarefa anterior. Dependências são pré-requisitos diretos; as transitivas também precisam estar concluídas. Tarefas sem dependência entre si podem ser escolhidas conforme capacidade disponível.
- Cada tarefa entrega uma regra, operação ou comportamento observável. Executar ciclos curtos **vermelho → verde → refatoração**, começando pelo menor exemplo descrito em “Testes necessários” e adicionando os demais casos um por vez. Não acumular toda a fase para só então testar.
- Infraestrutura e documentação usam verificações reproduzíveis no lugar de testes artificiais. As tarefas finais de aceitação executam e registram protocolos; os testes de regras e fluxos são escritos nas respectivas tarefas de implementação.
- **DoD comum (D0), obrigatório em cada tarefa:** critérios de aceitação atendidos; testes indicados executados e aprovados; regressões relevantes aprovadas; nenhuma ampliação de escopo; documentação afetada atualizada; evidência/comandos registrados. Em código, preservar os limites arquiteturais e concluir a refatoração sem quebrar os testes. Cada “Definição de pronto” abaixo acrescenta uma evidência específica a D0.
- Testes usam bancos temporários e diretórios isolados; nenhuma biblioteca real é alterada. Integrações automatizadas são simuladas. Testes de concorrência usam SQLite em arquivo, conexões independentes e commits reais, conforme arquitetura §10.
- Dados operacionais não bloqueiam implementação: contato real antes de qualquer consulta real ao catálogo; ambiente e celular real antes de medir aceitação; destino do backup antes do uso com dados reais. Sem esses dados, registrar a verificação correspondente como pendente, nunca como aprovada.

## Ordem e marcos do MVP

| Prioridade / marco | Tarefas | Resultado verificável |
| --- | --- | --- |
| 1 — Fundação | BL-001–BL-010 | Projeto verificável, validação e persistência básica isoladas. |
| 2 — Cadastro local seguro | BL-011–BL-021 | Cadastro manual revisável com artistas, duplicados e reenvio controlados. |
| 3 — Coleção utilizável | BL-022–BL-035 | Consulta, manutenção, streaming, capas e sorteios locais. |
| 4 — Recuperação local | BL-036–BL-039 | Backup e restauração ensaiados antes do uso com dados reais. |
| 5 — Catálogos opcionais | BL-040–BL-053 | Pesquisa, revisão, capa automática e troca de edição resilientes. |
| 6 — Operação e aceite | BL-054–BL-062 | Execução cotidiana, LAN e evidências do MVP completo. |

## 1. Fundação

### BL-001 — Criar projeto e ambiente reproduzível

- **Estado:** concluída em 15/10/2026, após aprovação explícita do usuário nesta sessão. Fundação existente validada em checkout limpo, sem alterações de código; D0 e comandos em [docs/acceptance.md](docs/acceptance.md#bl-001--fundação-validada-em-checkout-limpo).
- **Objetivo:** preparar Python 3.13, Django 5.2 LTS, projeto `config`, app `library` e runner nativo de testes.
- **Requisitos relacionados:** RNF-01; arquitetura §§2–4; ADR-01/03/10.
- **Dependências:** nenhuma.
- **Critérios de aceitação:** instalação em ambiente vazio funciona; dependências diretas/transitivas de execução e desenvolvimento ficam fixadas após verificar patches compatíveis; `manage.py check` e runner executam; estrutura segue a arquitetura, sem camadas genéricas.
- **Testes necessários:** instalação limpa, checks do Django e teste mínimo de carregamento do app; registrar versões de Python/SQLite.
- **Riscos e casos extremos:** versão de Python incompatível; dependência transitiva não fixada; teste usando banco real.
- **Definição de pronto:** D0 + comandos de preparação e teste reproduzidos a partir de checkout limpo.

### BL-002 — Configurar ambiente local e arquivos privados

- **Estado:** concluída em 15/10/2026, após aprovação explícita do usuário nesta sessão. Configuração privada verificada e banco na árvore de estáticos recusado; D0 e evidências Red/Green em [docs/acceptance.md](docs/acceptance.md#bl-002--configuração-local-e-arquivos-privados).
- **Objetivo:** definir configuração explícita, segredo externo, SQLite privado e fuso local.
- **Requisitos relacionados:** RNF-01/09; SEG-01/08/09; arquitetura §§3/6.2/8; ADR-02/08.
- **Dependências:** BL-001.
- **Critérios de aceitação:** fuso inicial `America/Fortaleza`; segredo fora do Git; banco/backups ignorados e fora dos estáticos; hosts específicos; `ATOMIC_REQUESTS=False`, escrita IMMEDIATE e timeout de banco de 3 s; sem WAL obrigatório.
- **Testes necessários:** carregar configurações válidas/inválidas e conferir opções do backend; verificar exclusão dos arquivos privados no Git.
- **Riscos e casos extremos:** configuração insegura por ausência de variável; banco em pasta sincronizada/rede; ano corrente fixado em constante.
- **Definição de pronto:** D0 + `.env.example` sem segredos e instruções de caminhos/permissões locais.

### BL-003 — Normalizar títulos e nomes

- **Estado:** concluída em 16/10/2026, após solicitação do usuário para executar a próxima tarefa. Função pura e validação de chave vazia verificadas por TDD; D0 e evidências em [docs/acceptance.md](docs/acceptance.md#bl-003--normalização-de-títulos-e-nomes).
- **Objetivo:** implementar uma função pura de chave textual compartilhada, mantendo a grafia de exibição.
- **Requisitos relacionados:** §2.1; DEC-07; RF-07/10; SEG-03; arquitetura §6.1.
- **Dependências:** BL-001.
- **Critérios de aceitação:** NFD → casefold → NFD → remoção de marcas combinantes e todo whitespace Unicode; pontuação permanece; chave vazia é inválida; `ÁGUA`, `agua` e ` A gua ` são equivalentes.
- **Testes necessários:** tabela com Unicode composto/decomposto, casefold, tabulação, quebra de linha, espaços internos, pontuação e somente marcas/espaços.
- **Riscos e casos extremos:** colisão `A B`/`AB`; normalização usada indevidamente como prova de identidade; perda do texto original.
- **Definição de pronto:** D0 + função determinística testada sem HTTP ou banco.

### BL-004 — Interpretar datas parciais e intervalos

- **Objetivo:** representar ausência, ano, ano/mês e data completa sem inventar componentes.
- **Requisitos relacionados:** §2.2; P-03; CA-01.7/05.5/10.9; arquitetura §6.1.
- **Dependências:** BL-001.
- **Critérios de aceitação:** aceitar `AAAA`, `AAAA-MM`, `AAAA-MM-DD`, de 0001 em diante; validar calendário gregoriano; precisão derivada; comparar intervalos e ordenar por início, ausentes ao fim e título/ID no desempate.
- **Testes necessários:** bissextos, ano zero, formatos inválidos, dia sem mês, mês sem ano, `1990`/`1990-05` sobrepostos e `1990-05`/`1990-06` separados; ordenação com precisão mista.
- **Riscos e casos extremos:** preencher janeiro/dia 1 no armazenamento; tratar sobreposição como identidade; perder zeros à esquerda na apresentação.
- **Definição de pronto:** D0 + representação e comparação puras preservam componentes ausentes.

### BL-005 — Rejeitar componentes temporais futuros

- **Objetivo:** validar original e edição contra a data local no momento da gravação.
- **Requisitos relacionados:** §2.3; DEC-09/10; RN-14; CA-01.6–7/09.6–7; P-03.
- **Dependências:** BL-002, BL-004.
- **Critérios de aceitação:** rejeitar ano, mês ou dia conhecido futuro; ausência é válida e distinta de zero; original e edição são independentes; relógio local substituível em testes.
- **Testes necessários:** hoje, amanhã, mês futuro no ano atual, virada de ano/fuso e original/edição com cada precisão.
- **Riscos e casos extremos:** usar UTC ou data de inicialização; formulário aberto antes de mudar o ano; sugestão externa futura aceita sem validação.
- **Definição de pronto:** D0 + mesmos validadores disponíveis aos caminhos manual e importado.

### BL-006 — Validar tamanhos e URLs

- **Objetivo:** centralizar limites de campos e política de URLs antes da persistência.
- **Requisitos relacionados:** §2; P-04; CA-12.6; SEG-04/10; arquitetura §8.
- **Dependências:** BL-001.
- **Critérios de aceitação:** título/artista/desambiguação até 500 caracteres Unicode; plataforma 100; consulta 300; URL 2.048, contando antes de normalizar. Links/capas HTTP/HTTPS sem credenciais; Spotify somente HTTPS e host `open.spotify.com`; sem restrição adicional de caminho.
- **Testes necessários:** limite exato e limite +1, caracteres Unicode, esquemas proibidos, credenciais, subdomínio/domínio impostor e URL malformada.
- **Riscos e casos extremos:** aceitar `open.spotify.com.evil.example`; truncar valores; requisitar URL para validá-la.
- **Definição de pronto:** D0 + funções puras recusam entradas inválidas sem chamadas de rede.

### BL-007 — Persistir identidade de artista

- **Objetivo:** criar `Artist` e sua migração com PK estável, grafia, chave, MBID confirmado opcional e descrição.
- **Requisitos relacionados:** RF-06; DEC-07/08; P-02; arquitetura §6.1; ADR-05.
- **Dependências:** BL-002, BL-003, BL-006.
- **Critérios de aceitação:** nomes normalizados são indexados e não únicos; dois homônimos podem ter PKs distintos; MBID e descrição não se tornam prova automática de identidade.
- **Testes necessários:** aplicar migração em banco temporário, persistir homônimos e Unicode e verificar campos/índice.
- **Riscos e casos extremos:** unicidade indevida por nome/descrição; excluir identidade para resolver colisão.
- **Definição de pronto:** D0 + migração versionada e round-trip de todos os campos comprovado.

### BL-008 — Persistir álbum e datas independentes

- **Objetivo:** criar `Album` com identidade local, metadados e representação aprovada de original/edição.
- **Requisitos relacionados:** RF-01/03/09/10; RN-04/14/15; P-01/03/07; arquitetura §6.1.
- **Dependências:** BL-002, BL-003, BL-004, BL-006.
- **Critérios de aceitação:** campos de título/chave, duas datas por componentes anuláveis, MBIDs de release/release-group opcionais, nota, duas URLs de capa, Spotify, revisão e token único; constraints estruturais das datas; sem unicidade por título/data e sem JSON bruto.
- **Testes necessários:** migração, round-trip das precisões/ausências, constraints de componentes e unicidade do token; dois álbuns com título igual permitidos pelo modelo.
- **Riscos e casos extremos:** confundir original com reedição; precisão redundante; restrição de banco tentar validar ano corrente.
- **Definição de pronto:** D0 + modelo/migração preservam todos os opcionais sem componentes artificiais.

### BL-009 — Persistir créditos de artistas

- **Objetivo:** criar `AlbumArtist` com associação única e posição do crédito.
- **Requisitos relacionados:** RF-01/06; RN-03; CA-06.2/06.5; arquitetura §6.1.
- **Dependências:** BL-007, BL-008.
- **Critérios de aceitação:** par álbum/artista único; posição preserva apresentação; exclusão do álbum remove vínculos e mantém artistas.
- **Testes necessários:** colaboração A/B, repetição do par, ordem de créditos, cascata e preservação de artistas.
- **Riscos e casos extremos:** transformar ordem em identidade; cascata apagar artista compartilhado.
- **Definição de pronto:** D0 + integridade referencial e comportamento de exclusão demonstrados.

### BL-010 — Persistir links adicionais

- **Objetivo:** criar `StreamingLink` com plataforma, URL e posição.
- **Requisitos relacionados:** RF-12; RN-12; P-04; arquitetura §6.1.
- **Dependências:** BL-008.
- **Critérios de aceitação:** álbum admite zero links ou vários, inclusive nomes repetidos; ordem preservada; exclusão do álbum remove somente seus links.
- **Testes necessários:** round-trip, plataformas repetidas, ordem e cascata sem afetar outro álbum.
- **Riscos e casos extremos:** unicidade indevida de plataforma; links órfãos.
- **Definição de pronto:** D0 + migração e associações verificadas em banco temporário.

## 2. Cadastro local seguro

### BL-011 — Selecionar ou criar identidade de artista

- **Objetivo:** resolver explicitamente artistas existentes e homônimos no serviço de gravação.
- **Requisitos relacionados:** RF-06; CA-06.5–6; §10.1; P-02; RNF-06.
- **Dependências:** BL-007, BL-009.
- **Critérios de aceitação:** nomes equivalentes oferecem candidatos; usuário escolhe PK ou cria outra identidade; criar homônimo exige descrição diferenciadora; ID repetido é deduplicado com indicação; artista sem álbum é reutilizável.
- **Testes necessários:** seleção existente, criação explícita, homônimo sem descrição, PK inexistente, MBID inválido e mesmo PK repetido.
- **Riscos e casos extremos:** fundir artistas por nome/MBID; criar artistas durante mera validação; resolver corrida fora da escrita serializada.
- **Definição de pronto:** D0 + resolução utilizável dentro da transação, sem gravação antecipada do formulário.

### BL-012 — Localizar candidatos a álbum duplicado

- **Objetivo:** consultar candidatos por título normalizado e conjunto exato de IDs de artistas.
- **Requisitos relacionados:** RF-10; CA-10.1–2/10.5–7/10.9; RN-04–06; P-01/03.
- **Dependências:** BL-003, BL-004, BL-009, BL-011.
- **Critérios de aceitação:** ordem dos artistas não interfere; conjunto diferente não coincide só pelo título; edição atual é excluída dos próprios candidatos; intervalos originais contextualizam revisão sem decidir identidade.
- **Testes necessários:** A/B versus B/A, A versus A/B, homônimos com PKs distintos, grafias equivalentes e datas ausentes/sobrepostas/separadas.
- **Riscos e casos extremos:** comparar apenas quantidade de artistas; data da reedição liberar duplicado; `release-group` virar chave única.
- **Definição de pronto:** D0 + consulta compartilhada retorna candidatos sem modificar registros.

### BL-013 — Exigir revisão de identidade ambígua

- **Objetivo:** definir a regra de aprovação de novo álbum diante de candidatos.
- **Requisitos relacionados:** RF-10; CA-10.3–4/10.7–9; §10.1; P-01; RN-04–06.
- **Dependências:** BL-012.
- **Critérios de aceitação:** oferecer primeiro revisão do existente; novo álbum distinto exige confirmação humana; com original ausente/sobreposto/coincidente, exigir também nota; data diferente não prova distinção; nova edição do mesmo álbum encaminha à manutenção do registro único.
- **Testes necessários:** cancelar, confirmar sem nota no caso ambíguo, confirmar com nota, originais distintos comprovados e tentativa de segunda edição do mesmo álbum.
- **Riscos e casos extremos:** botão genérico “continuar” autorizar múltiplas edições; confirmação tratar semântica impossível de verificar como certeza automática.
- **Definição de pronto:** D0 + resultado explícito de revisão/recusa/autorização, sem fusões automáticas.

### BL-014 — Criar álbum atomicamente

- **Objetivo:** salvar álbum, artistas e vínculos em uma operação transacional curta.
- **Requisitos relacionados:** RF-01/10; RN-02–06/14; RNF-06; SEG-03; arquitetura §6.2; ADR-08.
- **Dependências:** BL-005, BL-006, BL-008, BL-009, BL-011, BL-013.
- **Critérios de aceitação:** título e pelo menos um artista obrigatórios; no máximo 30 artistas; revalidar datas, identidades e candidatos dentro de `atomic` IMMEDIATE antes de criar registros; erro desfaz toda a operação; sem rede dentro da transação.
- **Testes necessários:** mínimo válido, colaboração, obrigatórios inválidos, 30/31 artistas e falha injetada entre álbum/vínculos; duas criações concorrentes com tokens distintos e candidato igual em SQLite em arquivo.
- **Riscos e casos extremos:** pré-validação não evitar corrida; artista órfão por falha; sucesso antes de commit; banco cheio.
- **Definição de pronto:** D0 + rollback completo e segunda gravação observando a primeira comprovados.

### BL-015 — Tornar criação idempotente

- **Objetivo:** controlar clique duplo/reenvio com token de criação assinado e único.
- **Requisitos relacionados:** RF-10; RNF-06; arquitetura §6.2; ADR-08.
- **Dependências:** BL-014.
- **Critérios de aceitação:** mesmo token e conteúdo retornam resultado já confirmado; conteúdo alterado orienta revisão do existente; token adulterado é recusado; tokens distintos continuam sujeitos aos candidatos.
- **Testes necessários:** reenvio sequencial e simultâneo em conexões independentes, conteúdo divergente, assinatura inválida e rollback antes do commit.
- **Riscos e casos extremos:** depender apenas de PRG ou trava de thread; criar segundo álbum após resposta perdida.
- **Definição de pronto:** D0 + uma única criação confirmada nos testes concorrentes de reenvio.

### BL-016 — Montar formulário manual e créditos

- **Objetivo:** capturar campos de álbum e escolhas de artistas sem salvar durante validação.
- **Requisitos relacionados:** RF-01/06; CA-01.1–3/01.6–7/06.5; RNF-07/08; P-02–04.
- **Dependências:** BL-005, BL-006, BL-011, BL-014.
- **Critérios de aceitação:** título, artistas e datas independentes com erros associados; selecionar/criar homônimo explicitamente; entradas válidas preservadas; linhas de artistas acessíveis; total de formset limitado antes do processamento, inclusive POST forjado.
- **Testes necessários:** forms/formsets com mínimo válido, erros, ID repetido, 30/31 artistas, total adulterado e datas futuras.
- **Riscos e casos extremos:** controles dependerem só de JavaScript/hover; erro apagar os créditos digitados.
- **Definição de pronto:** D0 + formulário validado sem efeito persistente e com rótulos identificáveis.

### BL-017 — Manter links no formulário e na criação

- **Objetivo:** adicionar Spotify e pares adicionais à gravação atômica.
- **Requisitos relacionados:** RF-12; CA-12.1/12.3/12.6; P-04; RNF-06/07.
- **Dependências:** BL-006, BL-010, BL-014, BL-016.
- **Critérios de aceitação:** até 20 links adicionais; nome/URL completos por item; nomes repetidos válidos; Spotify opcional; limite de formset aplicado antes de instanciar itens; erro em um link impede toda a criação.
- **Testes necessários:** zero/dois/20/21 links, pares incompletos, plataformas repetidas, URL inválida e falha entre inserções com rollback.
- **Riscos e casos extremos:** tratar linha vazia como link válido; salvar álbum antes de validar links.
- **Definição de pronto:** D0 + criação e formulário usam a mesma política de limites e URLs.

### BL-018 — Criar base de navegação responsiva

- **Objetivo:** fornecer template base, CSS local, mensagens e controles acessíveis reutilizáveis.
- **Requisitos relacionados:** RNF-02/07/08/09; SEG-03/08; arquitetura §§2/8.
- **Dependências:** BL-001.
- **Critérios de aceitação:** navegação por biblioteca/artistas/cadastro; HTML semântico, foco visível, labels e mensagens sem dados internos; adaptação sem rolagem horizontal; sem CDN ou build frontend.
- **Testes necessários:** renderização/escape de texto e verificação inicial por teclado nos viewports 1366×768, 390×844 e 844×390.
- **Riscos e casos extremos:** nomes/URLs longos quebrando layout; ações acessíveis somente por hover.
- **Definição de pronto:** D0 + base reutilizável com verificação de foco e largura registrada.

### BL-019 — Publicar fluxo HTTP de cadastro manual

- **Objetivo:** conectar GET do formulário e POST de criação com CSRF e PRG.
- **Requisitos relacionados:** RF-01; CA-01.1–4; SEG-02/03/10; RNF-07; arquitetura §5.1.
- **Dependências:** BL-015, BL-016, BL-017, BL-018.
- **Critérios de aceitação:** cadastro abre sem catálogo e grava por POST; formulário inválido conserva entradas; limite de corpo 256 KiB antes de processar coleções; CSRF ativo; sucesso redireciona para confirmação do registro por URL local.
- **Testes necessários:** GET sem gravação, POST válido/inválido, CSRF com enforcement, corpo no limite/acima, reenvio e APIs bloqueadas.
- **Riscos e casos extremos:** proteção existir apenas no navegador; redirecionar para URL arbitrária; afirmar sucesso em falha de persistência.
- **Definição de pronto:** D0 + fluxo manual completo exercitado por cliente HTTP do Django.

### BL-020 — Apresentar revisão de possível duplicado

- **Objetivo:** tornar o aviso e a resolução de identidade acessíveis no cadastro.
- **Requisitos relacionados:** RF-10; CA-10.1–9; P-01/02/03; RNF-07/08.
- **Dependências:** BL-013, BL-019.
- **Critérios de aceitação:** apresentar candidatos, datas/precisão e acesso por ID ao existente; confirmação/nota conforme BL-013; cancelamento não grava; POST final revalida candidatos, sem confiar em aviso/flag do cliente.
- **Testes necessários:** aviso com ordem invertida, notas ausentes/presentes, cancelamento e candidato criado entre prévia e confirmação.
- **Riscos e casos extremos:** fundir álbuns; perda de dados do formulário; permitir segunda edição por confirmação ambígua.
- **Definição de pronto:** D0 + percurso de aviso, revisão e novo álbum distinto testado sem mutação antecipada.

### BL-021 — Tratar falhas e contenção de escrita

- **Objetivo:** transformar lock, armazenamento indisponível e falhas intermediárias em resultado de falha compreensível.
- **Requisitos relacionados:** RNF-06/07/09; RF-10; §8; arquitetura §6.2.
- **Dependências:** BL-019, BL-020.
- **Critérios de aceitação:** timeout de lock de 3 s, rollback e nenhuma repetição automática; formulário preservado quando possível; sem traceback/sucesso falso; logs de categoria sem segredos ou conteúdo pessoal bruto.
- **Testes necessários:** lock real por conexão independente em SQLite temporário; falha de armazenamento simulada e exceção intermediária; inspecionar resposta/logs.
- **Riscos e casos extremos:** `select_for_update()` dar falsa garantia em SQLite; log conter token/consulta; retries duplicarem gravações.
- **Definição de pronto:** D0 + contenção real e falha controlada deixam banco anterior íntegro.

## 3. Coleção utilizável

### BL-022 — Listar biblioteca e abrir detalhes

- **Objetivo:** consultar registros persistidos com paginação e navegação local.
- **Requisitos relacionados:** RF-05; CA-05.1–5; RNF-03; P-03/05; arquitetura §5.3.
- **Dependências:** BL-009, BL-010, BL-018, BL-019.
- **Critérios de aceitação:** páginas de 50, ordem título normalizado/ID; detalhes mostram grafias, créditos, original/edição e precisões separadas; estado vazio permite cadastrar; ID ausente retorna 404; helper de ordenação temporal atende CA-05.5 sem adicionar filtro ao produto.
- **Testes necessários:** 0/1/51 registros, desempates, datas mistas, PK inexistente, API bloqueada e número limitado de consultas com muitos artistas/links.
- **Riscos e casos extremos:** N+1; detalhes consultarem catálogo; álbum excluído entre lista e abertura.
- **Definição de pronto:** D0 + biblioteca/detalhe funcionam com metadados locais e sem rede externa.

### BL-023 — Listar artistas e seus álbuns

- **Objetivo:** navegar por identidades de artistas com visibilidade baseada em vínculos.
- **Requisitos relacionados:** RF-06; CA-06.1–6; RN-03/16; P-02/05.
- **Dependências:** BL-022.
- **Critérios de aceitação:** lista apenas artistas com álbuns, ordem nome normalizado/ID e paginação de 50; página restringe álbuns ao PK; colaboração usa mesmo álbum; artista retido sem vínculos tem página vazia; PK inexistente retorna 404.
- **Testes necessários:** artistas A/B, colaboração, homônimos, 51 artistas, artista sem vínculo e inspeção de consultas para evitar N+1.
- **Riscos e casos extremos:** filtrar por nome e misturar homônimos; excluir fisicamente artista oculto.
- **Definição de pronto:** D0 + lista e página de artista demonstram identidade estável e conjunto correto.

### BL-024 — Pesquisar coleção local

- **Objetivo:** buscar parcialmente por título ou artista usando as chaves aprovadas.
- **Requisitos relacionados:** RF-07; CA-07.1–6 e complemento §10.3; P-05; RNF-03.
- **Dependências:** BL-003, BL-006, BL-022, BL-023.
- **Critérios de aceitação:** mesma normalização da gravação; OR de título/artista sem duplicar colaboração; vazio normalizado mostra todos; 300 caracteres no máximo; ordem título/ID e páginas de 50 mantêm a consulta; sem resultado tem mensagem própria.
- **Testes necessários:** título/artista parcial, acentos/caixa/espaços, pontuação, vazio, somente whitespace, limite, colaborações e navegação entre páginas com APIs bloqueadas.
- **Riscos e casos extremos:** usar `icontains` SQLite como normalização; duplicar linha por join; consulta vazia esconder registros.
- **Definição de pronto:** D0 + resultados únicos e estáveis, com consulta preservada na paginação.

### BL-025 — Atualizar álbum com revisão otimista

- **Objetivo:** criar operação de edição atômica sobre o mesmo ID local.
- **Requisitos relacionados:** RF-08/10/12; CA-08.1–4/12.2; RNF-06; arquitetura §6.2; ADR-08.
- **Dependências:** BL-014, BL-017, BL-021.
- **Critérios de aceitação:** editar título, artistas, datas, capa e links; recalcular chave; conferir revisão dentro da escrita e incrementá-la; revalidar duplicados; conflito/falha mantém versão anterior; remover último vínculo não apaga artista.
- **Testes necessários:** atualização completa, obrigatórios inválidos, colisão, rollback entre relações/links e duas edições concorrentes com a mesma revisão em banco em arquivo.
- **Riscos e casos extremos:** last-write-wins; serviço chamar catálogo dentro da transação; sobrescrever links parcialmente.
- **Definição de pronto:** D0 + edição desatualizada é rejeitada e não perde alteração confirmada.

### BL-026 — Oferecer formulário HTTP de edição

- **Objetivo:** expor a edição reutilizando validação, revisão e tratamento de conflitos.
- **Requisitos relacionados:** RF-08; CA-08.1–4; RF-06/10; SEG-02; RNF-07/08.
- **Dependências:** BL-020, BL-022, BL-025.
- **Critérios de aceitação:** GET preenche formulário; POST válido usa revisão; cancelar conserva registro; erro/conflito mantém dados submetidos e oferece versão atual; mudanças aparecem em busca e artistas; revisão de duplicado também funciona na edição.
- **Testes necessários:** HTTP de edição/cancelamento, CSRF, revisão adulterada/antiga, remoção do último vínculo e colisão com outro álbum.
- **Riscos e casos extremos:** recarregar formulário silenciosamente e apagar trabalho; GET modificar estado; ID removido durante edição.
- **Definição de pronto:** D0 + percurso de edição e conflito validado com duas versões do formulário.

### BL-027 — Remover álbum atomicamente

- **Objetivo:** excluir álbum, vínculos e links preservando artistas e outros registros.
- **Requisitos relacionados:** RF-11; CA-11.2–4/06.4/06.6; RNF-06; arquitetura §6.2.
- **Dependências:** BL-021, BL-025.
- **Critérios de aceitação:** exigir revisão atual; exclusão em transação curta; manter artistas órfãos; falha reverte tudo; edição concorrente impede excluir versão não revisada.
- **Testes necessários:** colaboração, artista compartilhado, último álbum, falha injetada e corrida real editar/excluir com conexões independentes.
- **Riscos e casos extremos:** apagar artista compartilhado; exclusão desatualizada; confirmar remoção de algo já removido.
- **Definição de pronto:** D0 + cascatas e conflito de revisão comprovados sem dano aos demais registros.

### BL-028 — Confirmar remoção pela interface

- **Objetivo:** exigir confirmação explícita por POST antes de remover.
- **Requisitos relacionados:** RF-11; CA-11.1–4; RN-11; SEG-02; RNF-07/08.
- **Dependências:** BL-023, BL-024, BL-026, BL-027.
- **Critérios de aceitação:** GET identifica álbum sem excluir; cancelar conserva dados; POST com CSRF/revisão remove; álbum some de lista, busca e artistas; acesso posterior retorna 404; conflito não mostra sucesso.
- **Testes necessários:** GET, cancelar, POST, CSRF ausente, exclusão repetida e confirmação aberta antes de uma edição.
- **Riscos e casos extremos:** remoção por link/prefetch; artista sem álbuns ainda aparecer na lista.
- **Definição de pronto:** D0 + efeitos visíveis e cancelamento verificados por HTTP.

### BL-029 — Abrir streaming nos detalhes

- **Objetivo:** apresentar ações externas identificadas pelos nomes e URLs salvos.
- **Requisitos relacionados:** RF-12; CA-12.1–4; RN-12; SEG-03/07.
- **Dependências:** BL-022, BL-026.
- **Critérios de aceitação:** Spotify e links adicionais abrem destino salvo; nova aba usa `rel="noopener noreferrer"`; sem links não há ação vazia; nomes escapados; nenhum teste de disponibilidade é feito pelo servidor.
- **Testes necessários:** nomes/destinos, nomes repetidos, ausência, URL corrigida/removida, texto malicioso escapado e atributos de nova aba.
- **Riscos e casos extremos:** link fora do ar; URL de outra edição; plataforma duplicada escondida pelo template.
- **Definição de pronto:** D0 + ações correspondem exatamente aos valores persistidos e permanecem corrigíveis.

### BL-030 — Aplicar precedência de capas

- **Objetivo:** escolher URL de apresentação sem sobrescrever dados de capa.
- **Requisitos relacionados:** RF-04; CA-04.2–4/04.6; DEC-11; RN-15; P-07; ADR-06.
- **Dependências:** BL-006, BL-022, BL-026.
- **Critérios de aceitação:** manual → automática → padrão; remoção explícita da manual reativa alternativa; nenhuma URL é baixada pelo Django; consulta automática futura não substitui manual.
- **Testes necessários:** combinações de ausência/manual/automática, substituir/remover manual e inspeção de ausência de fetch no servidor.
- **Riscos e casos extremos:** manual quebrada ser removida automaticamente; escolha de capa depender de rede na renderização.
- **Definição de pronto:** D0 + política única de apresentação testada com URLs persistidas.

### BL-031 — Exibir capa com fallback sem loop

- **Objetivo:** renderizar imagem remota ou padrão mantendo conteúdo e ações acessíveis.
- **Requisitos relacionados:** RF-04; CA-04.2/04.5–6; RNF-02/08; SEG-05; arquitetura §8.
- **Dependências:** BL-018, BL-030.
- **Critérios de aceitação:** falha de imagem troca uma vez para padrão; falha da padrão não reinicia tentativas; manual quebrada conserva URL e não tenta automática; `img` com alternativa textual, dimensões e `referrerpolicy="no-referrer"`; lazy loading nas listas.
- **Testes necessários:** Playwright interceptando imagem válida, quebrada, conteúdo não-imagem e padrão quebrada; verificar número de tentativas e ausência de layout cortado.
- **Riscos e casos extremos:** loop de `onerror`; nome longo com imagem ausente; imagem remota excessiva no navegador.
- **Definição de pronto:** D0 + fallback demonstrado no navegador sem alterar URLs do banco.

### BL-032 — Sortear uniformemente conjunto global

- **Objetivo:** selecionar um álbum entre todos os registros locais elegíveis.
- **Requisitos relacionados:** RF-13; CA-13.1–5; RN-08–10/13; ADR-07; arquitetura §5.3.
- **Dependências:** BL-009, BL-022.
- **Critérios de aceitação:** materializar uma consulta com um item por álbum; usar `random.choice`; opcionais ausentes não excluem; permitir repetição; sem COUNT + offset, PK aleatória ou ordenação aleatória no banco.
- **Testes necessários:** zero/um/muitos, lacunas de PK, colaboração, sem opcionais e cada posição por fonte aleatória substituída; bloquear APIs e inspecionar consultas/algoritmo.
- **Riscos e casos extremos:** peso adicional por colaboração; teste estatístico instável como prova; filtro implícito de pesquisa.
- **Definição de pronto:** D0 + elegibilidade e uniformidade estrutural demonstradas deterministicamente.

### BL-033 — Sortear conjunto de artista

- **Objetivo:** reutilizar seleção uniforme restringindo pelo ID do artista.
- **Requisitos relacionados:** RF-14/15; CA-14.1–4/15.2–3; P-02; RN-08–10.
- **Dependências:** BL-023, BL-032.
- **Critérios de aceitação:** somente álbuns associados ao PK; colaboração participa uma vez; artista retido sem vínculos produz vazio; artista inexistente é distinguido; sem fallback para conjunto global.
- **Testes necessários:** A, B e colaboração A/B; zero/um/muitos; artista homônimo, inexistente e sem álbuns; todas as posições elegíveis.
- **Riscos e casos extremos:** restringir por nome; retornar álbum de outro artista ao esvaziar conjunto.
- **Definição de pronto:** D0 + conjunto e seleção corretos para todos os estados do artista.

### BL-034 — Expor sorteios e estados vazios

- **Objetivo:** oferecer ações distintas global/por artista com orientação contextual.
- **Requisitos relacionados:** RF-13–15; CA-15.1–3; RNF-02/07/08; arquitetura §5.1/5.3.
- **Dependências:** BL-018, BL-022, BL-028, BL-032, BL-033.
- **Critérios de aceitação:** POST com CSRF seguido de detalhe; biblioteca vazia orienta cadastro; artista vazio explica ausência própria; PK inválido e álbum removido após seleção têm 404 tratado; pesquisa não muda universo do sorteio global.
- **Testes necessários:** HTTP dos dois sorteios, conjunto vazio, repetição controlada, CSRF e exclusão entre seleção/abertura; APIs bloqueadas.
- **Riscos e casos extremos:** sorteio disparado por prefetch; texto confundir artista vazio com biblioteca vazia.
- **Definição de pronto:** D0 + ações utilizáveis por teclado/toque e sem resultado fora do conjunto.

### BL-035 — Comprovar persistência e fluxos locais

- **Objetivo:** manter regressão curta de ponta a ponta da biblioteca independente de APIs.
- **Requisitos relacionados:** RF-01/05–08/10–16; CA-03.5/16.1; RNF-02/03/08.
- **Dependências:** BL-024, BL-026, BL-028, BL-029, BL-031, BL-034.
- **Critérios de aceitação:** cadastrar colaboração sem opcionais, editar, buscar, abrir streaming, sortear e remover; reiniciar aplicação conservando IDs, datas, relações e URLs; mesmas operações locais funcionam com catálogos bloqueados.
- **Testes necessários:** reutilizar testes existentes e adicionar apenas percurso Playwright essencial e reinício com SQLite temporário persistente; checar foco/toque e ausência de chamadas ao catálogo.
- **Riscos e casos extremos:** teste usar banco em memória e não demonstrar reinício; duplicar toda suíte em E2E lento.
- **Definição de pronto:** D0 + evidência do marco local, sem declarar MVP completo ou metas de uso já cumpridas.

## 4. Recuperação local

### BL-036 — Gerar snapshot consistente do SQLite

- **Objetivo:** criar cópia temporária pela API de backup SQLite enquanto a biblioteca pode receber gravações.
- **Requisitos relacionados:** RF-16; CA-16.2; RNF-10; P-09; arquitetura §6.3; ADR-11.
- **Dependências:** BL-002, BL-010, BL-014.
- **Critérios de aceitação:** `sqlite3.Connection.backup` produz snapshot íntegro; validar integridade/FKs antes de publicar; falha descarta temporário e mantém cópia anterior; sem copiar arquivo vivo por `cp`.
- **Testes necessários:** banco em arquivo com gravação concorrente, integridade e falha de destino/falta de espaço simulada.
- **Riscos e casos extremos:** snapshot parcial; arquivo final parecer válido antes de concluído; tocar banco real nos testes.
- **Definição de pronto:** D0 + cópia consistente comprovada com conexões reais concorrentes.

### BL-037 — Disponibilizar comando manual de backup

- **Objetivo:** expor geração de cópia validada e metadados de recuperação por comando local.
- **Requisitos relacionados:** RF-16; RNF-10; SEG-08/09; P-07/09; arquitetura §6.3.
- **Dependências:** BL-036.
- **Critérios de aceitação:** destino explícito; versão da aplicação/esquema, data e instruções acompanham cópia; publicação só após validação; sem sobrescrita destrutiva implícita, agenda ou limpeza automática; URLs incluídas, conteúdo remoto não incluído.
- **Testes necessários:** comando com destino válido, inexistente/sem permissão, colisão de nome e falha ao publicar metadados/cópia.
- **Riscos e casos extremos:** backup em diretório público; metadados não corresponderem à cópia; cópia só no mesmo disco.
- **Definição de pronto:** D0 + comando executável com diretório isolado e mensagens sem sucesso parcial.

### BL-038 — Validar candidato à restauração

- **Objetivo:** inspecionar backup em área temporária antes de alterar a biblioteca atual.
- **Requisitos relacionados:** RF-16; CA-16.4; RNF-10; arquitetura §6.3; ADR-11.
- **Dependências:** BL-037.
- **Critérios de aceitação:** verificar formato/integridade SQLite, FKs e compatibilidade de migrações/versão; arquivo incompatível é recusado sem migração silenciosa; validação não modifica origem nem banco ativo.
- **Testes necessários:** backup válido, truncado/corrompido, FKs inválidas, arquivo não SQLite e esquema antigo/mais novo incompatível.
- **Riscos e casos extremos:** aceitar apenas porque o arquivo abre; tentar recuperar arquivo incompatível sobre o banco atual.
- **Definição de pronto:** D0 + inspeção isolada distingue candidatos recuperáveis de inválidos.

### BL-039 — Restaurar offline preservando recuperação anterior

- **Objetivo:** substituir biblioteca somente após validação e preservação de cópia recuperável da atual.
- **Requisitos relacionados:** RF-16; CA-16.1–4; RNF-10; SEG-09; P-09; arquitetura §6.3.
- **Dependências:** BL-035, BL-038.
- **Critérios de aceitação:** comando requer servidor parado conforme procedimento explícito; preservar biblioteca anterior antes de substituir; falha de substituição não remove recuperação; reiniciar instância isolada e conferir valores completos; consulta/sorteio funcionam com APIs bloqueadas.
- **Testes necessários:** restauração válida, falha antes/durante substituição, arquivo incompatível e comparação de identidades, créditos, datas/precisões, edições, revisões, tokens e todas as URLs.
- **Riscos e casos extremos:** servidor ainda escrever; backup antigo exigir versão compatível; URLs expiradas não invalidarem metadados restaurados.
- **Definição de pronto:** D0 + ensaio reproduzível preserva banco/cópia anteriores nos cenários de falha.

## 5. Catálogos opcionais

### BL-040 — Restringir destinos e configurar cliente externo

- **Objetivo:** criar transporte HTTPX síncrono com origens fixas, TLS e identificação da aplicação.
- **Requisitos relacionados:** INT-01/02; SEG-05/06; P-06; arquitetura §§7/8; ADR-04.
- **Dependências:** BL-001, BL-002.
- **Critérios de aceitação:** URLs construídas de origens HTTPS fixas e MBIDs válidos; TLS não pode ser desativado; redirects automáticos desabilitados, rejeitando destinos arbitrários; User-Agent com nome/versão/contato real; sem contato, consulta indisponível e cadastro manual preservado.
- **Testes necessários:** transporte simulado para MBID inválido, certificado inválido, redirects privados/arbitrários, User-Agent e ausência de contato; zero rede real na suíte.
- **Riscos e casos extremos:** URL de capa manual virar destino do servidor; usar valor de formulário como URL completa de catálogo.
- **Definição de pronto:** D0 + fronteira de rede testada sem necessidade de contato real para testes simulados.

### BL-041 — Limitar tempo e tamanho das respostas

- **Objetivo:** encerrar chamada ou fluxo externo antes de exceder orçamento aprovado.
- **Requisitos relacionados:** INT-01/02; SEG-10; RNF-07; P-06; arquitetura §7.
- **Dependências:** BL-040.
- **Critérios de aceitação:** conexão 2 s, leitura/escrita 3 s, pool 1 s; prazo total por chamada 5 s e fluxo 15 s, incluindo esperas; etapas respeitam saldo; até 2 MiB de JSON descomprimido com leitura incremental; validar tipo/estrutura; sem imagens binárias.
- **Testes necessários:** relógio/transporte substituídos, partes lentas contínuas, compressão, Content-Length ausente/incorreto, tamanho exato/+1 e JSON/tipo inválido; sequência esgotando saldo do fluxo.
- **Riscos e casos extremos:** timeout de leitura não limitar duração total; medir bytes comprimidos; enriquecimento ultrapassar orçamento.
- **Definição de pronto:** D0 + testes sem espera real demonstram prazos e limites inclusive em streaming lento.

### BL-042 — Controlar admissão e cadência externa

- **Objetivo:** coordenar chamadas concorrentes em um processo sem esgotar threads locais.
- **Requisitos relacionados:** INT-01/02; SEG-10; P-06; arquitetura §7; ADR-04.
- **Dependências:** BL-041.
- **Critérios de aceitação:** no máximo um fluxo de catálogo ativo, demais recebem ocupado; todas as chamadas MusicBrainz compartilham controlador, uma em andamento e inícios separados por ≥1,1 s; CAA tem controlador separado com mesma cadência local; espera inicial de 1,1 s após reinício; sem trava de banco.
- **Testes necessários:** concorrência entre pesquisa/detalhes/release-group, controlador CAA separado, admissão ocupada e reinício com relógio monotônico simulado.
- **Riscos e casos extremos:** get/set não ser trava; quatro threads ficarem em fila; múltiplos processos romperem limite.
- **Definição de pronto:** D0 + testes concorrentes comprovam admissão/cadência compartilhadas sem sleeps reais.

### BL-043 — Compartilhar pausa por fornecedor

- **Objetivo:** tratar 429/503 como falha controlada com pausa e nova tentativa manual limitada.
- **Requisitos relacionados:** CA-02.3; INT-01/02; P-06; arquitetura §7.
- **Dependências:** BL-042.
- **Critérios de aceitação:** nenhuma retentativa automática; Retry-After válido respeitado, 30 s quando ausente; pausa por fornecedor observada por todos os caminhos; falha não se torna “sem resultados”; nova tentativa manual obedece pausa e taxa.
- **Testes necessários:** 429/503, Retry-After em segundos/data e inválido/ausente, pausa em chamada concorrente e expiração com relógio controlado.
- **Riscos e casos extremos:** retry em laço; pausa de um fornecedor aplicada ao outro; header inválido quebrar atendimento.
- **Definição de pronto:** D0 + contagem de chamadas prova ausência de repetição automática.

### BL-044 — Reaproveitar consultas com cache limitado

- **Objetivo:** armazenar resultados externos recentes com limites e sincronização.
- **Requisitos relacionados:** RF-02; CA-02.5; INT-01/02; P-06; arquitetura §7.
- **Dependências:** BL-043.
- **Critérios de aceitação:** até 200 entradas/16 MiB totais; sucesso 15 min, vazio real 60 s; chave fornecedor/operação/parâmetros/página; falha não cacheada como vazio; hit imediato mesmo com fluxo ocupado; reconsultar cache após adquirir admissão.
- **Testes necessários:** hits, expiração, limites/evicção, chave por página/operação, concorrência da mesma consulta, exceção e cache vazio descartado após reinício.
- **Riscos e casos extremos:** entradas mutáveis compartilhadas; memória ilimitada; duas misses gerarem chamadas repetidas indevidas.
- **Definição de pronto:** D0 + cache concorrente respeita limites e não oculta falhas do fornecedor.

### BL-045 — Adaptar pesquisa MusicBrainz

- **Objetivo:** traduzir consulta literal em resultados paginados de edições.
- **Requisitos relacionados:** RF-02; CA-02.1–5; INT-01; P-05/06; arquitetura §5.2.
- **Dependências:** BL-006, BL-044.
- **Critérios de aceitação:** texto livre de título/artista até 300 caracteres com escape da sintaxe externa; 20 releases por página, relevância do fornecedor; não obter detalhes de cada item; nenhuma entidade salva; falha e vazio distintos.
- **Testes necessários:** consulta com operadores/caracteres reservados, paginação, lista válida/vazia/incompleta e estrutura inválida; verificar número de chamadas e ausência de gravações.
- **Riscos e casos extremos:** tratar consulta como linguagem avançada; relevância escolher edição automaticamente.
- **Definição de pronto:** D0 + adaptador produz sugestões conhecidas e nunca decide identidade.

### BL-046 — Obter detalhes da edição selecionada

- **Objetivo:** carregar somente a release escolhida e seu original quando houver proveniência adequada.
- **Requisitos relacionados:** RF-03; CA-03.1/03.3–4; DEC-09; P-01/03; INT-01.
- **Dependências:** BL-005, BL-045.
- **Critérios de aceitação:** release.date alimenta edição; original vem de fonte identificada como original, via release-group quando disponível; ausência do original continua ausente; apresentar país, formato, gravadora/catálogo, data da edição e MBID disponíveis; dados incompletos são revisáveis.
- **Testes necessários:** reedição 2020/original 1990, original desconhecido, release-group ausente/falhando, título/artistas faltantes e prazo do fluxo esgotado no enriquecimento.
- **Riscos e casos extremos:** copiar data da edição para original; armazenar release-group como identidade única; rejeitar todo resultado incompleto sem permitir correção.
- **Definição de pronto:** D0 + sugestões separam explicitamente original, edição e proveniência sem gravar álbum.

### BL-047 — Obter referência opcional de capa no CAA

- **Objetivo:** enriquecer edição compatível com URL de miniatura frontal.
- **Requisitos relacionados:** RF-04; CA-04.1/04.4; INT-02; P-06/07; ADR-06.
- **Dependências:** BL-006, BL-044, BL-046.
- **Critérios de aceitação:** consultar apenas MBID compatível selecionado; extrair/validar URL frontal quando disponível; 404, timeout, limite ou JSON inválido deixam capa ausente; respeitar saldo do fluxo; nenhum binário é baixado ou persistido.
- **Testes necessários:** capa encontrada, sem frontal, 404, erro, URL inválida, prazo esgotado e MBID ausente; verificar cadastro não bloqueado.
- **Riscos e casos extremos:** usar limite do MusicBrainz como regra oficial do CAA; requisitar URL retornada no servidor.
- **Definição de pronto:** D0 + enriquecimento devolve URL opcional sem efeito persistente.

### BL-048 — Apresentar busca externa e seleção

- **Objetivo:** oferecer página de catálogo com escolha explícita e caminho manual em qualquer resultado.
- **Requisitos relacionados:** RF-02; CA-02.1–4; RF-01; RNF-02/07/08/09.
- **Dependências:** BL-018, BL-019, BL-045.
- **Critérios de aceitação:** resultados e paginação acessíveis; escolher edição não salva; vazio, ocupado, pausa e falha são distinguíveis com opção manual; comunicação de catálogo ocorre somente no Django; não renderizar HTML externo como seguro.
- **Testes necessários:** HTTP de cada estado e percurso de seleção; XSS em resultado; inspecionar rede do navegador e zero gravações durante pesquisa.
- **Riscos e casos extremos:** falha parecer ausência de álbum; mostrar traceback/resposta bruta; perder consulta ao paginar.
- **Definição de pronto:** D0 + escolha e fallback manual utilizáveis por teclado e toque.

### BL-049 — Preparar revisão importada sem persistência

- **Objetivo:** preencher formulário revisável com detalhes e proveniência validável.
- **Requisitos relacionados:** RF-03; CA-03.1–4; SEG-03; RNF-07; arquitetura §5.2.
- **Dependências:** BL-016, BL-017, BL-020, BL-046, BL-047, BL-048.
- **Critérios de aceitação:** revisão mostra dados da edição escolhida, original e capa separadamente; permite corrigir campos; metadados de proveniência protegidos contra adulteração; cancelar não cria nada; expiração/adulteração orienta revisão ou cadastro manual preservando texto; sem álbum provisório.
- **Testes necessários:** edição selecionada entre duas, correção de obrigatório ausente, proveniência adulterada/expirada, cancelar e expiração do cache após abrir formulário.
- **Riscos e casos extremos:** aceitar MBID arbitrário no POST; salvar depender de cache ainda válido; artista externo virar associação sem confirmação local.
- **Definição de pronto:** D0 + formulário revisável preparado sem gravação e sem vinculação automática de homônimos.

### BL-050 — Confirmar cadastro importado pelo serviço comum

- **Objetivo:** salvar somente os dados revisados usando a mesma integridade do cadastro manual.
- **Requisitos relacionados:** RF-01/03/04/10; CA-01.6/03.1–5/04.4; RN-02–06/13/14; SEG-03.
- **Dependências:** BL-015, BL-021, BL-030, BL-049.
- **Critérios de aceitação:** revalidar limites, datas, identidades e duplicados no POST; nenhuma consulta externa dentro da transação ou exigida após revisão válida; ID da release corresponde à escolha; falha de capa não impede salvar; depois de salvo funciona sem APIs.
- **Testes necessários:** título corrigido, artista incompleto, data futura, resposta acima dos limites sem truncamento, candidato duplicado e POST após APIs/cache ficarem indisponíveis; rollback.
- **Riscos e casos extremos:** caminho importado contornar validação; nova edição gerar segundo registro; prioridade da capa manual perdida.
- **Definição de pronto:** D0 + cadastro importado testado até consulta/sorteio offline do registro confirmado.

### BL-051 — Trocar edição preservando dados protegidos

- **Objetivo:** implementar operação específica de troca no álbum existente.
- **Requisitos relacionados:** RF-09/10; CA-09.1–7; RN-04/07/14/15; RNF-06; arquitetura §5.2.
- **Dependências:** BL-025, BL-030, BL-046, BL-047.
- **Critérios de aceitação:** conferir revisão e duplicados na escrita; manter ID, original independente e Spotify/todos os links carregados do banco; manual permanece salvo salvo substituição/remoção explícita; revisar automática da nova edição; alterar somente após confirmação.
- **Testes necessários:** original 1990/edições 2020 e 2025, data própria ausente, campos de links omitidos/adulterados, manual preservada/removida explicitamente, conflito de revisão e falha intermediária com rollback.
- **Riscos e casos extremos:** `ModelForm.save()` apagar links omitidos; rede segurar transação; reedição substituir data original.
- **Definição de pronto:** D0 + serviço preserva integralmente links e identidade nos testes de sucesso/falha.

### BL-052 — Oferecer revisão HTTP de troca de edição

- **Objetivo:** conectar busca/seleção ao álbum existente com cancelamento e revisão antes do POST.
- **Requisitos relacionados:** RF-09; CA-09.1–7; RF-10; SEG-02; RNF-07/08.
- **Dependências:** BL-026, BL-048, BL-049, BL-051.
- **Critérios de aceitação:** dados antigos permanecem até confirmar; mostrar original/edição e capa separadamente; links preservados não são sobrescritos pelo cliente; cancelamento ou falha externa conserva tudo; aviso de duplicado e conflito exibem orientação; CSRF e revisão obrigatórios.
- **Testes necessários:** percurso HTTP/navegador de selecionar, revisar, confirmar/cancelar; falha externa; colisão; duas abas e exclusão durante revisão.
- **Riscos e casos extremos:** origem da troca se perder na navegação; formulário antigo sobrescrever nova edição.
- **Definição de pronto:** D0 + usuário troca edição mantendo mesmo ID e verifica preservação de links/capa manual.

### BL-053 — Verificar integração externa sob falhas

- **Objetivo:** consolidar regressão curta dos fluxos de catálogo e disponibilidade da coleção durante consulta lenta.
- **Requisitos relacionados:** RF-01–04/09; INT-01/02; RNF-03/07/09; SEG-05/06/10; P-06.
- **Dependências:** BL-031, BL-034, BL-050, BL-052.
- **Critérios de aceitação:** falha/limite de catálogo nunca bloqueia caminho manual ou consulta/sorteio local; ocupado respeita admissão; logs informam categoria/fornecedor/duração/status sem consulta completa, token ou JSON bruto.
- **Testes necessários:** executar regressões existentes e um percurso Playwright com catálogo lento/503 e consulta local concorrente; verificar mensagens e logs; sem duplicar testes unitários de transporte.
- **Riscos e casos extremos:** threads esgotadas; 503 virar cache vazio; campo digitado desaparecer após falha.
- **Definição de pronto:** D0 + disponibilidade local durante falha externa demonstrada antes da medição final.

## 6. Operação e aceite do MVP

### BL-054 — Executar com Waitress e WhiteNoise

- **Objetivo:** preparar execução cotidiana em um processo e quatro threads com `DEBUG=False`.
- **Requisitos relacionados:** RNF-01/09; SEG-01/08; arquitetura §§2/8; ADR-09.
- **Dependências:** BL-002, BL-018, BL-031.
- **Critérios de aceitação:** bind padrão em `127.0.0.1`; `collectstatic` e WhiteNoise servem somente `STATIC_ROOT`; CSS/JS/padrão disponíveis; banco/backups/configurações não acessíveis; um único processo documentado; sem depender de `runserver` na operação cotidiana.
- **Testes necessários:** smoke test de inicialização real com `DEBUG=False`, quatro threads configuradas, estáticos, 404/erro sem traceback e tentativas de ler arquivos privados.
- **Riscos e casos extremos:** pasta `var` inteira publicada; dois processos invalidarem cache/taxa; ausência de segredo impedir diagnóstico claro.
- **Definição de pronto:** D0 + início/parada e smoke test do servidor cotidiano reproduzíveis.

### BL-055 — Documentar instalação e operação pela LAN

- **Objetivo:** explicar operação local e habilitação explícita do celular na rede confiável.
- **Requisitos relacionados:** RNF-01; SEG-01/02/09; DEC-05; arquitetura §8.
- **Dependências:** BL-039, BL-040, BL-054.
- **Critérios de aceitação:** README e `docs/operations.md` cobrem instalação, migração, estáticos, início/parada, hosts específicos, IP de escuta, origem CSRF sem wildcard e firewall restrito; mesma rede/servidor ativo; mudança de IP e diagnóstico; explicar acesso de leitura/escrita sem autenticação e ausência de exposição pública.
- **Testes necessários:** seguir instruções em ambiente local limpo; conferir loopback por padrão e configuração LAN explícita sem desligar CSRF.
- **Riscos e casos extremos:** Wi-Fi isolar clientes; servidor desligado; recomendar túnel/port forwarding ou wildcard como solução.
- **Definição de pronto:** D0 + roteiro operacional executável, sem declarar conectividade real do celular antes de BL-058.

### BL-056 — Documentar e ensaiar recuperação por uma pessoa

- **Objetivo:** tornar backup/restauração reproduzíveis sem conhecimento implícito.
- **Requisitos relacionados:** RF-16; RNF-10; SEG-08/09; P-07/09; §10.4.
- **Dependências:** BL-037, BL-038, BL-039, BL-055.
- **Critérios de aceitação:** roteiro inclui escolha do destino antes de dados reais, permissões, recomendação de cópia externa ao disco, antes de migrações/após manutenção, frequência/retenção do proprietário, servidor parado na restauração, versão compatível e teste isolado; sem agenda/limpeza automática; explicar que URLs não preservam imagens.
- **Testes necessários:** executar roteiro do início ao fim em diretórios isolados, incluindo erro de arquivo inválido e recuperação da biblioteca anterior; conferir todos os dados de CA-16.2–4 com APIs bloqueadas.
- **Riscos e casos extremos:** destino operacional ainda não informado; períodos sem cópia perderem alterações; restaurar diretamente sobre a coleção real no ensaio.
- **Definição de pronto:** D0 + passos e resultado do ensaio registrados; destino real preenchido antes da liberação para dados reais.

### BL-057 — Registrar ambiente e dataset de aceitação

- **Objetivo:** preparar evidência reproduzível para medir os critérios aprovados.
- **Requisitos relacionados:** RNF-02/04/05; P-08; §10.4; arquitetura §10.
- **Dependências:** BL-035, BL-053, BL-054.
- **Critérios de aceitação:** `docs/acceptance.md` registra SO, CPU/RAM, disco, versões app/Python/SQLite, navegadores/rede e modelo/versão do celular escolhido; dataset reproduzível de 1.000 álbuns inclui Unicode, colaborações, homônimos, datas ausentes/parciais, links e registros sem opcionais; cada RF/CA tem campo de resultado/evidência.
- **Testes necessários:** gerar dataset em banco isolado, conferir contagens e invariantes; reproduzir geração com mesmos parâmetros; registrar dados operacionais reais antes da medição.
- **Riscos e casos extremos:** usar só dados simples; emulação apresentada como celular real; ambiente ainda não disponível tratado como aprovado.
- **Definição de pronto:** D0 + ambiente e dataset identificados; evidências ausentes explicitamente pendentes.

### BL-058 — Aceitar fluxos em PC e celular real

- **Objetivo:** verificar equivalência funcional, responsividade, teclado e toque no protocolo P-08.
- **Requisitos relacionados:** RF-01–15; RNF-01/02/07/08; SEG-01; P-08; DEC-05.
- **Dependências:** BL-052, BL-053, BL-055, BL-057.
- **Critérios de aceitação:** fluxos essenciais de cadastro manual/importado, revisão/duplicado, edição/troca, remoção, biblioteca/artista/detalhe, busca, streaming e sorteios concluídos; incluir erros/vazios; Chromium/Firefox PC 1366×768, emulação 390×844 e 844×390, celular real retrato/paisagem na LAN acessando a mesma biblioteca; sem rolagem horizontal, corte ou ação só por hover.
- **Testes necessários:** executar percursos Playwright já construídos na matriz; complementar manualmente toque, teclado/foco e conexão LAN no celular; conferir capa manual/automática/padrão e falha da padrão.
- **Riscos e casos extremos:** emulação não comprovar LAN; texto/URLs longos; navegador móvel escolhido indisponível.
- **Definição de pronto:** D0 + matriz com resultados e evidências por fluxo/dispositivo; falhas corrigidas e rechecadas antes do aceite.

### BL-059 — Medir desempenho local com 1.000 álbuns

- **Objetivo:** verificar limite de 2 s para biblioteca, busca e sorteios no ambiente registrado.
- **Requisitos relacionados:** RNF-04; CA-13.5; P-08; arquitetura §§9/10.
- **Dependências:** BL-053, BL-054, BL-057, BL-058.
- **Critérios de aceitação:** servidor pronto, 30 execuções por operação local, sem chamadas de catálogo; registrar primeira, demais tempos, máximo e p95; nenhuma ultrapassa 2 s do envio até HTML/controles utilizáveis, excluindo carregamento de imagens; separar tempos de servidor/navegador; testar também leitura/sorteio em PC/celular durante catálogo lento.
- **Testes necessários:** medições repetíveis de listagem, pesquisa representativa e sorteios global/por artista; inspecionar consultas/N+1 se falhar; corrigir causa e repetir operações afetadas.
- **Riscos e casos extremos:** reportar só média/p95 e ocultar máximo; incluir imagens terceiras no tempo; lock de escrita de 3 s ser confundido com meta de leitura.
- **Definição de pronto:** D0 + dataset, procedimento e tempos brutos registrados com conclusão sustentada pelos valores.

### BL-060 — Medir metas de cadastro e abertura de streaming

- **Objetivo:** demonstrar cadastro manual em até 60 s e streaming em até três interações desde a biblioteca.
- **Requisitos relacionados:** CA-01.5/12.5; RNF-05; P-08; arquitetura §10.
- **Dependências:** BL-058.
- **Critérios de aceitação:** cadastro do formulário vazio utilizável à confirmação; streaming parte da biblioteca pronta e inclui busca, detalhe e link quando necessários; clique/toque/submissão por teclado contam como interação; texto registrado como entrada, sem contar caractere a caractere; registrar duração e sequência reais.
- **Testes necessários:** teste de uso no PC e celular com álbum básico e álbum conhecido com link, segundo convenção aprovada; ajustar fluxo se falhar e repetir cenário afetado.
- **Riscos e casos extremos:** excluir submissão da contagem; começar com detalhe já aberto; afirmar meta com base só em teste de código.
- **Definição de pronto:** D0 + evidências das duas metas por contexto de uso registrado.

### BL-061 — Auditar segurança e integridade do MVP completo

- **Objetivo:** consolidar evidências das proteções aprovadas sem ampliar o produto.
- **Requisitos relacionados:** SEG-01–10; RNF-06/07/09; RF-10; arquitetura §§6–10.
- **Dependências:** BL-028, BL-039, BL-053, BL-054, BL-055, BL-058.
- **Critérios de aceitação:** todos os caminhos de gravação usam serviço, POST/CSRF, limites e revisão aplicáveis; autoescape/ORM preservados; URLs/SSRF/TLS, orçamento externo, privacidade de logs/arquivos e configuração loopback/LAN verificados; nenhuma rede dentro da transação.
- **Testes necessários:** executar testes existentes de segurança e concorrência real, incluindo cadastro com token igual/distinto, edição/troca/exclusão desatualizada, lock e rollback; preencher matriz SEG com evidência e cobrir somente lacunas encontradas.
- **Riscos e casos extremos:** confiar em mock para provar lock; endpoint novo contornar serviço; logs exporem dados externos/pessoais.
- **Definição de pronto:** D0 + SEG-01–10 e cenários de integridade com evidência, sem vulnerabilidade conhecida no recorte verificado.

### BL-062 — Fechar aceite e instruções de entrega do MVP

- **Objetivo:** consolidar rastreabilidade e verificações finais da entrega local.
- **Requisitos relacionados:** RF-01–16; RNF-01–10; INT-01/02; SEG-01–10; P-01–09; escopo aprovado.
- **Dependências:** BL-056, BL-059, BL-060, BL-061.
- **Critérios de aceitação:** cada RF/CA e decisão aplicável tem resultado/evidência em `docs/acceptance.md`; contato real configurado antes de eventual chamada real e destino de backup definido antes de dados reais; checks, migrações, suíte e smoke `DEBUG=False` aprovados; README explica limitações das URLs/remotos e operação em processo único; nenhum resultado pendente é chamado de aprovado.
- **Testes necessários:** `manage.py check`, `makemigrations --check --dry-run`, suíte Django/Playwright aplicável e smoke operacional; revisar evidências já produzidas de LAN, recuperação, desempenho e uso sem repetir medições aprovadas sem motivo. Consulta real de fumaça é opcional, manual e condicionada ao contato/taxa.
- **Riscos e casos extremos:** declarar MVP pronto com celular/backup/metas não verificados; confundir entrega local com autorização para publicar.
- **Definição de pronto:** D0 + todos os critérios obrigatórios comprovados, instruções reproduzíveis e nenhuma pendência impeditiva do uso local acordado.

## Rastreabilidade de cobertura

As tarefas acima detalham os critérios; esta matriz permite verificar cobertura sem substituir a leitura das fontes. Intervalos de IDs incluem todos os itens intermediários.

| Requisito / decisão | Tarefas principais |
| --- | --- |
| RF-01 — cadastro manual | BL-003–BL-006, BL-011, BL-014–BL-021, BL-035, BL-060 |
| RF-02 — busca externa | BL-040–BL-045, BL-048, BL-053 |
| RF-03 — revisão/importação | BL-046, BL-049–BL-050, BL-053 |
| RF-04 — capas | BL-006, BL-030–BL-031, BL-047, BL-049–BL-053 |
| RF-05 — biblioteca/detalhes | BL-022, BL-035; CA-05.5 também BL-004 |
| RF-06 — artistas/colaboração | BL-007, BL-009, BL-011, BL-016, BL-023, BL-025–BL-028 |
| RF-07 — busca local | BL-003, BL-024, BL-035 |
| RF-08 — edição | BL-025–BL-026 |
| RF-09 — troca de edição | BL-046, BL-049, BL-051–BL-052 |
| RF-10 — identidade/duplicados | BL-011–BL-015, BL-020–BL-021, BL-025–BL-026, BL-050–BL-052 |
| RF-11 — remoção | BL-027–BL-028 |
| RF-12 — streaming | BL-006, BL-010, BL-017, BL-025–BL-026, BL-029, BL-060 |
| RF-13 — sorteio global | BL-032, BL-034–BL-035 |
| RF-14 — sorteio por artista | BL-033–BL-035 |
| RF-15 — conjuntos vazios | BL-022–BL-024, BL-032–BL-034 |
| RF-16 — persistência/recuperação | BL-035–BL-039, BL-056 |
| RN-01–16 | Sem estado de escuta (BL-008/BL-032); obrigatórios/colaboração (BL-009/BL-014); identidade (BL-011–BL-015); troca (BL-051); sorteios (BL-032–BL-034); remoção (BL-027–BL-028); streaming (BL-029); independência (BL-035/BL-053); original (BL-004–BL-005); capa (BL-030–BL-031); artistas visíveis (BL-023/BL-028) |
| RNF-01/02/03 | BL-001–BL-002, BL-018, BL-035, BL-053–BL-055, BL-058 |
| RNF-04/05 | BL-057, BL-059–BL-060 |
| RNF-06/07/09 | BL-014–BL-021, BL-025–BL-028, BL-039, BL-049–BL-053, BL-061 |
| RNF-08/10 | BL-016/BL-018 e respectivos fluxos, BL-058; BL-036–BL-039, BL-056 |
| INT-01/02 | BL-040–BL-047, BL-053 |
| SEG-01/02/03 | BL-002, BL-055, BL-058; BL-019/BL-026/BL-028/BL-034/BL-052; BL-003–BL-006 e validação/escape nos fluxos; auditoria BL-061 |
| SEG-04/05/06/07 | BL-006; BL-030–BL-031/BL-040/BL-047; BL-040; BL-029; auditoria BL-061 |
| SEG-08/09/10 | BL-002/BL-021/BL-054; BL-037–BL-039/BL-055–BL-056; BL-006/BL-016–BL-019/BL-041–BL-044; auditoria BL-061 |
| P-01/02/03 | BL-012–BL-013/BL-020/BL-046; BL-007/BL-011/BL-023; BL-004–BL-005/BL-008/BL-022/BL-051 |
| P-04/05/06 | BL-006/BL-014/BL-016–BL-019; BL-022–BL-024/BL-045/BL-048; BL-040–BL-044 |
| P-07/08/09 | BL-030–BL-031/BL-047/BL-056; BL-057–BL-060; BL-036–BL-039/BL-056 |
| ADR-01–11 | BL-001/BL-002 (01–03/10), BL-040–BL-044 (04), BL-011–BL-013 (05), BL-030–BL-031 (06), BL-032–BL-033 (07), BL-014–BL-015/BL-025/BL-027 (08), BL-054 (09), BL-036–BL-039 (11) |

## Fora deste backlog

Permanecem fora do MVP: publicação na internet, autenticação de serviço publicado, PostgreSQL, múltiplos usuários, API pública, SPA, filas distribuídas, sincronização/contas de streaming, reprodução interna, histórico de escuta, avaliações, tags, filtros avançados, sorteio sem repetição, importação/exportação em lote, upload/download local de capas e backup agendado. Evoluções exigem backlog próprio após o aceite local; não são dependências ocultas destas tarefas.
