# Estratégia de testes — biblioteca pessoal de álbuns

**Data:** 15/10/2026 (America/Fortaleza). **Estado:** planejamento; não implementa funcionalidades nem declara critérios aprovados.

## 1. Fontes, limites e rastreabilidade

Fontes: [escopo](PROJECT_SCOPE.md), [requisitos](REQUIREMENTS.md), [arquitetura](ARCHITECTURE.md), [backlog](BACKLOG.md) e [instruções do projeto](AGENTS.md). Preservam-se DEC-01–11, P-01–09 e ADR-01–11 aprovados. Esta estratégia detalha a arquitetura §10 e os testes necessários do backlog; não cria decisões de produto.

Existe somente a fundação do ambiente, descrita em [README.md](README.md) e [docs/acceptance.md](docs/acceptance.md). As suítes abaixo são **planejadas**, salvo as verificações de ambiente já registradas nesse documento. A fundação não comprova aceite funcional. Não se incluem autenticação, admin, múltiplos usuários, API pública, publicação, histórico de escuta ou infraestrutura adicional.

Particularidades das fontes, preservadas sem renumeração:

- `CA-07.5` aparece em RF-07 como ausência de duplicação e em requisitos §10.3 como busca parcial, vazio, ordem e paginação. A matriz cobre cumulativamente as duas descrições.
- `CA-10.8–9`, anunciado em RF-10, é detalhado como `CA-10.8` e `CA-10.9` em §10.3. Os critérios adicionais de outros RF nessa seção também são obrigatórios.
- A arquitetura e o backlog descrevem o estado documental de sua elaboração; o README e as evidências registram a fundação posterior. Isso não permite considerar BL-001/002 ou qualquer outra tarefa integralmente aceita sem verificar seu D0.

Cada teste futuro deve mencionar os IDs de requisito/CA aplicáveis em nome, docstring ou tabela de rastreabilidade. Os IDs de suíte deste documento identificam grupos de comportamentos, não nomes obrigatórios de funções. Cada linha da matriz exige os exemplos positivos e negativos descritos, escritos gradualmente junto da tarefa autorizada.

## 2. Prioridades e invariantes

Prioridade de execução por risco, sem remover obrigatoriedade dos demais testes:

| Prioridade | Invariante / regra crítica | Fonte | Evidência principal |
| --- | --- | --- | --- |
| Alta | Uma gravação confirmada é completa; qualquer falha conserva o estado anterior, sem sucesso falso. Álbum exige título e artista. | RN-02, RNF-06/07, ADR-08 | I-GR, C-DB, H-WR |
| Alta | Identidade local é estável; colaboração é um álbum e um vínculo por artista. Ordem dos créditos não muda conjunto de identidade nem peso. | RN-03/04, P-02 | I-ID, I-GR, I-SO |
| Alta | Normalização gera candidatos, nunca fusão. Título equivalente e conjunto exato de IDs exigem revisão; nomes, MBIDs e datas não provam identidade. | RN-05/06, P-01/02/03, ADR-05 | U-TX, I-ID, E-ID |
| Alta | Reedição mantém registro único; original e edição são independentes. Nenhum componente temporal conhecido pode ser futuro na gravação. | RN-04/07/14, DEC-09/10 | U-DT, I-TR |
| Alta | Trocar edição preserva ID, Spotify, todos os links e capa manual salvo ação explícita sobre a capa. | RN-07/15, DEC-03/11 | I-TR, H-WR, E-EX |
| Alta | Mesmo token não cria duas vezes; revisões antigas não sobrescrevem nem removem versão atual. Tokens diferentes revalidam candidatos na escrita serializada. | ADR-08, arquitetura §6.2 | C-DB |
| Alta | Backup é consistente; restauração valida antes de substituir e mantém recuperação anterior. | RF-16, P-09, ADR-11 | O-BK |
| Alta | Entrada manual, externa e POST forjado passam por validação de servidor; GET não grava, POST exige CSRF. | SEG-02/03/04/10 | U-LM, H-SEC, H-WR |
| Alta | Rede do servidor usa somente integrações conhecidas com TLS, orçamento finito e taxa compartilhada; não busca URLs manuais. | INT-01/02, SEG-05/06/10, ADR-04 | X-CT, X-LIM, C-EXT |
| Média | Leitura, busca e sorteio dependem dos dados locais, inclusive após reinício/restauração. | RN-13, RNF-03 | I-QU, I-SO, O-BK, E-LO |
| Média | Sorteio uniforme por registro elegível, sem filtros por opcionais, pesquisa ou último resultado. Artista vazio não recorre ao global. | RN-01/08/09/10, ADR-07 | I-SO |
| Média | Artista sem vínculo permanece armazenado, oculto da lista e acessível com conjunto vazio. | RN-16, P-02 | I-ID, I-QU |
| Média | Capa manual precede automática; manual quebrada usa padrão sem mudar URLs. Falha da padrão não gera ciclo. | RN-15, P-07, ADR-06 | U-CP, E-IM |
| Média | Destinos de streaming são os informados, corrigíveis; nenhuma garantia de disponibilidade ou reprodução. | RN-12, SEG-07 | H-SEC, E-ST |
| Média | PC e celular usam a mesma biblioteca; controles essenciais funcionam por teclado/toque, sem corte ou hover obrigatório. | RNF-01/02/08, P-08 | E-UI, A-LAN |
| Média | Operações locais cumprem 2 s com 1.000 álbuns; cadastro 60 s e streaming três interações. | RNF-04/05 | A-PERF, A-USO |

## 3. Contratos de entrada e saída

Verificar entradas pela fronteira pública adequada: função pura, operação de serviço, cliente HTTP, comando ou navegador. Não fixar assinaturas, textos exatos de mensagem ou estrutura interna de objetos antes da implementação.

| Fronteira | Entrada e condições | Saída observável / erro e estado preservado |
| --- | --- | --- |
| Normalização | Texto Unicode de título, artista ou consulta | NFD → casefold → NFD → remover marcas combinantes e todo whitespace Unicode; pontuação preservada, sem transliteração. Grafia original separada. Chave vazia invalida nome/título; consulta normalizada vazia mostra todos. |
| Datas | Ausência, `AAAA`, `AAAA-MM`, `AAAA-MM-DD`; original e edição separados; data local injetável | Componentes presentes preservados e precisão derivada; 0001 até hoje, calendário gregoriano válido; sem ano zero, mês sem ano ou dia sem mês. Intervalos só para comparação, sem janeiro/dia 1 artificial no banco. Erro identifica o campo, sem gravação parcial. |
| Texto e coleções | Título/artista/desambiguação ≤500 caracteres Unicode; plataforma ≤100; consulta local/externa ≤300; URL ≤2.048; ≤30 artistas e ≤20 links adicionais; POST ≤256 KiB | Limites contados antes da normalização; excedente rejeitado sem truncar, inclusive importação. Totais forjados de formset limitados antes de processar itens. Par de link exige nome e URL; linha adicional inteiramente vazia não cria link. Nomes de plataforma repetidos são válidos. |
| URLs | HTTP/HTTPS sem credenciais; Spotify HTTPS com host exato `open.spotify.com`, sem restringir caminho a álbum | URL válida persistida e usada como destino/imagem. Esquemas executáveis/locais, URL malformada, credenciais e domínio Spotify impostor recusados. Validação não consulta a URL. Não se exige bloquear URL privada de imagem no formulário: a proteção aprovada é ausência de fetch no servidor. |
| Artistas e identidade | IDs locais selecionados ou criação explícita; MBID opcional validado e confirmado | Nome equivalente oferece candidatos. Homônimo novo exige descrição diferenciadora; mesmo ID repetido gera indicação e um vínculo. ID inexistente ou adulterado não cria associação. MBID/nome/descrição não promovem fusão automática. |
| Duplicados | Título normalizado + conjunto exato de IDs, sem ordem; datas originais opcionais | Aviso e acesso ao existente, sem mutação antecipada. Novo álbum comprovadamente distinto requer confirmação; original ausente/sobreposto/coincidente exige também nota. Cancelar/omitir nota conserva coleção. Reedição encaminha à troca no registro existente. |
| Criação/edição/remoção | Campos revisados; token assinado na criação; revisão atual nas alterações | Sucesso só após commit, mesmo ID na edição/troca. Reenvio idêntico devolve registro confirmado; conteúdo diferente com mesmo token orienta revisão. Assinatura inválida, conflito, lock ou erro não alteram estado nem anunciam sucesso. |
| Troca de edição | Álbum, revisão, release selecionada e campos revisados; instrução explícita para remover/substituir capa manual | Dados antigos até confirmação; ID e links carregados do banco preservados mesmo se omitidos/adulterados no cliente. Original independente da edição; falha/cancelamento preserva tudo. |
| Consultas locais | Termo opcional ou ID; páginas de 50 | Busca parcial na chave de título OU artista; resultados únicos, título normalizado/ID; artistas por nome normalizado/ID. Paginação conserva consulta. ID inexistente/removido é 404; artista retido sem álbum é página válida vazia. Ordenação temporal, quando usada, por início de intervalo, ausência ao fim, título/ID no desempate. |
| Sorteio | Global ou ID de artista; fonte aleatória substituível | Um álbum do snapshot elegível ou orientação contextual; uma participação por álbum, chance 1/N. Não filtra por busca, opcionais ou histórico. Artista inexistente é 404; removido após seleção pode resultar em 404 tratado. |
| HTTP de páginas | GET de leitura/pesquisa/confirmação; POST de gravação e sorteios, com CSRF | HTML renderizado no servidor; PRG em sucesso; erro de campo com valores preservados quando possível. GET não altera dados. Não fixar código para formulário inválido; 404 e rejeição de segurança distinguem-se de sucesso/erro interno. Redirecionamento de sucesso é local. |
| Catálogos | Consulta literal escapada, página de 20 releases; detalhes somente da seleção; MBIDs válidos e origens HTTPS fixas | Sugestões revisáveis, nunca persistência nem escolha automática. Vazio real, ocupado, pausa e falha distintos. Data da release é da edição; original só de fonte identificada. Sem contato, indisponibilidade controlada e caminho manual. |
| Capa e streaming | URLs opcionais persistidas | Manual → automática → padrão; manual quebrada → padrão sem apagar manual nem tentar automática. Remoção explícita reativa alternativa. Imagem é `img`, não documento remoto. Link abre destino salvo; indisponibilidade externa não compromete dados locais. |
| Backup/restore | Destino explícito, arquivo candidato, versão/esquema, servidor parado na restauração | Backup temporário validado antes de publicar com metadados. Restore verifica SQLite/FKs/migrações, mantém recuperação atual e só então substitui. Erro claro em inválido/incompatível/sem espaço, sem migração silenciosa nem perda da cópia anterior. |

### Limites externos que integram o contrato

`X-LIM` deve verificar os valores exatos e cruzamentos de limites, além do caminho normal:

- MusicBrainz: um fluxo de catálogo ativo, uma chamada em andamento, intervalo entre inícios ≥1,1 s para pesquisa/detalhes/release-group; após reinício, espera inicial ≥1,1 s. CAA tem controlador separado com a mesma cadência **local**, não uma alegação sobre sua política oficial.
- Fluxo completo ≤15 s, incluindo espera por taxa e chamadas sequenciais; cada chamada ≤5 s e limitada pelo saldo restante. Conexão 2 s, leitura/escrita 3 s por etapa, pool 1 s. Testar resposta contínua lenta que não excede timeout individual, mas excede prazo total.
- JSON descomprimido ≤2 MiB por chamada, aferido incrementalmente mesmo sem `Content-Length` ou com valor falso. Testar limite exato e +1 byte, compressão, estrutura/tipo inválidos e JSON malformado; servidor não baixa binários de imagem.
- Cache concorrente ≤200 entradas e ≤16 MiB totais; sucesso 15 min, vazio real 60 s; chave inclui fornecedor/operação/parâmetros/página. Verificar antes/no vencimento/depois, isolamento entre chaves e ausência de resultado mutável contaminado por outro consumidor. Não exigir algoritmo específico de evicção.
- Hit de cache atende imediatamente mesmo com fluxo ocupado; miss concorrente não cria fila ilimitada. Reconsulta após admissão evita chamada redundante. Falha não se transforma em vazio cacheado. Reinício descarta cache.
- Sem retry automático. 429/503 geram falha e pausa compartilhada por fornecedor; `Retry-After` válido em segundos/data é respeitado; ausência usa 30 s. Cabeçalho inválido não quebra atendimento; caracterizar fallback seguro na tarefa BL-043, sem presumir uma nova regra de produto. Nova tentativa manual respeita pausa e taxa.

## 4. Suítes e níveis

### Unitários, sem banco ou rede

Usar `SimpleTestCase`, `unittest` e `subTest` para tabelas de exemplos. Resultado esperado deve ser literal ou calculado por um oráculo independente, nunca pelo próprio algoritmo sob teste.

| ID | Arquivo futuro sugerido | Comportamentos necessários |
| --- | --- | --- |
| U-TX | `test_validation.py` | Unicode composto/decomposto; `ÁGUA`/`agua`/` A gua `; `A B`/`AB`; NBSP, tabulação, newline e marcas; casefold (`Straße`/`STRASSE`); pontuação diferencia `A-B` de `AB`; rejeitar nome só de marcas/espaços; preservar grafia original. |
| U-DT | `test_validation.py` | Quatro precisões/ausência, zeros à esquerda, 0001, zero, formatos quebrados, mês 0/13, dias impossíveis, 1900 não bissexto/2000 bissexto; hoje/amanhã, mês/ano futuro e virada de ano/fuso; sobreposição e separação de intervalos; ordenação estável sem inventar componentes. |
| U-LM | `test_validation.py` | Cada limite exato e +1 antes de normalizar; caracteres Unicode versus bytes do POST; URLs válidas, protocolos proibidos, credenciais, hosts impostores e subdomínios Spotify; HTTP Spotify recusado, caminhos HTTPS legítimos aceitos. |
| U-FM | `test_forms.py` | Obrigatórios; pares incompletos; datas independentes; IDs repetidos; limites 30/31 artistas, 20/21 links; totais de formset negativos/adulterados/excessivos; zero efeito persistente da validação. Casos que consultam identidades usam `TestCase`, não se simulam regras do ORM. |
| U-CP | `test_validation.py` ou `test_views.py` | Tabela de precedência de capas, substituição/remoção explícita, ausência de mutação ao escolher URL. Falha de carregamento pertence ao navegador. |

### Integração com ORM e HTTP

Usar `TestCase` para round-trip e consultas. Usar cliente Django com `enforce_csrf_checks=True` para segurança; obter token pelo fluxo real, sem desativar middleware. Nos serviços, chamar operações públicas e conferir estado relido do banco e respostas; não espionar cada chamada interna.

| ID | Arquivos futuros sugeridos | Comportamentos necessários |
| --- | --- | --- |
| I-ID | `test_queries.py`, `test_writes.py` | Candidatos por conjunto exato, A/B versus B/A, A versus A/B e A/B versus C/D; homônimos com PKs distintos; excluir o próprio álbum dos candidatos em edição; datas não decidem identidade; confirmação/nota, cancelamento e revalidação final; artista retido e reutilizado. |
| I-GR | `test_writes.py` | Mínimo válido e colaboração; obrigatórios e limites em todos os caminhos; associação única, crédito/links na ordem de apresentação, nomes de plataforma repetidos; FKs/cascatas, tokens únicos e constraints estruturais de datas. Falhas entre álbum/artistas/vínculos/links revertem tudo; excluir não altera outros álbuns nem apaga artistas. |
| I-TR | `test_writes.py` | Edição/troca mantém ID; chave de título atualizada afeta busca/candidatos; original e edição opcionais/independentes; links omitidos/adulterados não substituem os persistidos na troca; capa manual conservada, removida/substituída só explicitamente; conflito e falha revertem conjunto completo. |
| I-QU | `test_queries.py` | 0/1/50/51 registros; paginação, ordem/desempates e consulta mantida; OR título/artista parcial normalizado sem repetir colaborações; homônimos retornam identidades separadas; artistas com/sem vínculos; consultas locais sem rede. Comparar contagem de queries para poucos/muitos créditos e links e limitar crescimento N+1, sem congelar SQL textual. |
| I-SO | `test_draw.py` | Zero/um/muitos, PKs com lacunas, sem opcionais, colaboração uma vez e artista correto; fonte controlada força cada posição e o mesmo resultado consecutivo. Inspeção do método e conjunto passado à seleção demonstram participação única e escolha uniforme; amostra estatística não é prova. Verificar snapshot de uma consulta conforme ADR-07, sem COUNT/offset ou sorteio de intervalo de PK. |
| H-WR | `test_views.py` | GET sem mutação, POST válido/inválido, PRG local, cancelar, revisão antiga, token adulterado/reenviado, candidato surgindo após prévia; dados digitados e links preservados; nenhum sucesso antes de commit; 404 após exclusão e para IDs inválidos; corpo 256 KiB/+1 rejeitado antes do processamento excessivo. |
| H-SEC | `test_views.py`, `test_integrations.py` | POST sem CSRF/token inválido/origem indevida rejeitado em cada fluxo; textos HTML/script e payload SQL tratados como dados sem alterar consulta/DOM; URLs inválidas submetidas diretamente; nova aba com `noopener noreferrer`; imagens com `no-referrer`, dimensões, alt e lazy loading em lista; sem fetch de capa/streaming pelo servidor; respostas/logs sem segredo, token, caminho, consulta pessoal completa ou JSON bruto. |

Asserts de arquitetura só onde verificam decisão explícita: constraints, snapshot do sorteio, queries sem N+1 e ausência de rede dentro da transação. Não exigir nome de helper, sequência de chamadas ORM, HTML completo, CSS interno ou texto integral de mensagem. Preferir IDs locais, conjunto de resultados, valores, erro associado ao campo e ação disponível.

### Concorrência e commits reais

`C-DB` (`test_concurrency.py`): `TransactionTestCase` ou subprocessos equivalentes, **SQLite temporário em arquivo**, conexões independentes criadas em cada thread/processo, commits reais, barreiras/eventos e deadlines para detectar deadlock. Não reutilizar conexão entre threads nem usar SQLite em memória para provar lock. Iniciar após dados de preparação commitados; encerrar workers/conexões e remover arquivos mesmo em falha.

| Cenário sincronizado | Oráculo |
| --- | --- |
| Dois envios com mesmo token/conteúdo; resposta perdida seguida de reenvio | Uma criação confirmada e mesmo ID retornado; conteúdo divergente orienta revisar, sem segunda gravação. |
| Tokens distintos, mesmo candidato, ambos após prévia sem duplicado | Segunda escrita observa a primeira, exige revisão e não cria duplicado automaticamente; sem prometer dedução semântica de álbuns ambíguos. |
| Duas edições ou edição/troca com mesma revisão | Uma alteração confirma; a outra informa conflito e preserva a vencedora e os dados submetidos para revisão. |
| Edição versus exclusão; troca versus exclusão; exclusão repetida | Não excluir versão não revisada nem ressuscitar registro; conflito ou 404 conforme estado final, sem sucesso falso. |
| Conexão independente segura lock de escrita além do timeout | Falha controlada após timeout configurado de 3 s, sem retry ou alteração parcial. Verificar tempo com tolerância de agendamento documentada; não exigir igualdade exata de relógio. |
| Falha depois de iniciar gravação e antes/depois de relações/links | Estado anterior completo após rollback, incluindo ausência de artistas novos órfãos; repetição posterior permitida conforme token confirmado ou não. |
| Coleção muda enquanto se sorteia | Resultado pertence ao snapshot selecionado; remoção posterior resulta em 404 tratado. Coordenar momentos com eventos, sem depender de corrida aleatória. |

Erros de disco cheio/permissão podem ser injetados de forma controlada na fronteira de persistência/arquivo. Isso comprova tratamento/rollback, não prova lock; o teste de lock usa o banco real isolado. Não encher o disco do usuário.

`C-EXT` (`test_integrations.py`): threads reais, transporte fake bloqueado por eventos e relógio monotônico controlado. Registrar inícios, simultaneidade máxima, chamadas e estado de ocupado; pesquisa/detalhes/release-group compartilham taxa e pausa, CAA é independente. Testar liberação de admissão/locks também após exceção e cache hit enquanto um fluxo espera. Não usar sleeps reais para TTL/cadência; não simular o próprio lock que se pretende verificar.

## 5. Dependências externas e testes de contrato

`X-CT` e `X-LIM` ficam em `test_integrations.py` (divisão futura por tamanho, se necessário). O cliente HTTPX real recebe transporte substituível; respostas e falhas são locais e determinísticas. Toda suíte automatizada deve falhar diante de tentativa de acesso real a catálogo. Fixtures descrevem o subconjunto consumido do contrato, não cópias de dados privados.

| Dependência | Contrato a verificar na saída e na entrada | Casos de quebra |
| --- | --- | --- |
| MusicBrainz — pesquisa | Origem fixa HTTPS, User-Agent com aplicação/versão/contato de teste, parâmetros literais escapados, página com 20 releases e ordem de relevância conservada; MBID validado; não buscar detalhes de cada item | Vazio real, obrigatórios ausentes, campos extras tolerados, tipos/estrutura errados, 429/503, 4xx/5xx, timeout/rede/TLS, redirect arbitrário/privado, JSON grande/malformado. Nenhum álbum salvo. |
| MusicBrainz — release/release-group | Detalhes somente do selecionado; `release.date` → edição; original apenas da proveniência adequada; preservar país, formato, gravadora/catálogo e MBID disponíveis para revisão | Duas releases do mesmo álbum, original desconhecido, release-group ausente/falho, dados incompletos e futuros. Campos opcionais ausentes permitem revisão manual; não copiar data da edição. |
| CAA — metadados da release | MBID compatível, URL de miniatura frontal validada; controlador separado; enriquecimento opcional dentro do saldo | 404, sem frontal, URL inválida, timeout, limite/pausa, resposta inválida e orçamento esgotado. Retornar ausência de capa sem impedir salvar; não requisitar binário retornado. |
| Provedores de imagem e streaming no navegador | `img` ou link apontam ao valor salvo, fallback/abertura seguros | Imagem inválida, 404, URL expirada e destino fora do ar interceptados no Playwright. Não testar uptime, reprodução, login ou equivalência de edição do terceiro; não existe API Spotify no MVP. |
| HTTPX/TLS | Configuração de verificação TLS ativa, origens/redirects e limites aplicados; erro de certificado traduzido | Transporte fake lança erro de certificado para testar tratamento; isso não demonstra handshake TLS. Se necessária regressão do handshake, usar servidor HTTPS local efêmero com certificado não confiável e confirmar rejeição pelo cliente real, sem `verify=False`. |
| SQLite/Django/Waitress/WhiteNoise | Constraints/migrações, commit/backup, métodos/CSRF, HTML e estáticos em servidor real | Verificações I-GR/C-DB/O-BK/O-ENV; não simular o banco ou servidor na evidência que depende deles. |

Fixtures de contrato devem ter referência à especificação oficial indicada em arquitetura §§5/7 e requisitos §6, data de preparação e campos exercitados. Ao implementar/atualizar adaptador, conferir a especificação oficial vigente e registrar divergências antes de alterar decisões aprovadas. Um fake testa compatibilidade com o contrato registrado, não disponibilidade atual do fornecedor. Consulta real de fumaça é opcional/manual, com contato real e taxa respeitada; não integra CI nem exige segredo. Não adicionar dependência de serviço de contratos ou conta externa.

Testar proveniência assinada adulterada/expirada, MBID/IDs forjados e expiração do cache após abrir revisão: preservar campos digitados, oferecer revisão/manual e não exigir nova rede para salvar revisão ainda válida. Sem contato configurado, nenhuma chamada sai e o caminho manual continua utilizável.

## 6. End-to-end e aceitação operacional

Usar Playwright para Python com `StaticLiveServerTestCase` conforme necessário, navegador e servidor ligados ao banco temporário. Seletores por papel/rótulo/nome acessível; expectativas sobre ações e dados, sem snapshots completos. Catálogos são substituídos no servidor (interceptar só o navegador não simula HTTPX); imagens e streaming são interceptados no navegador. Não abrir serviços reais nem usar biblioteca pessoal.

| ID | Percurso essencial e verificações |
| --- | --- |
| E-LO | Cadastrar colaboração mínima → biblioteca → artistas/detalhes → pesquisar → editar/adicionar links → sortear global/artista → cancelar remoção → confirmar remoção. Conferir mesmo ID e visibilidade; APIs bloqueadas. Reinício é complementar em O-BK, com processo e arquivo persistente temporário. |
| E-ID | Candidato com grafia normalizada e ordem invertida → revisar existente → cancelar; caso distinto ambíguo exige confirmação/nota; homônimos com descrição associados aos IDs corretos. Conferir coleção antes/depois. |
| E-EX | Buscar → selecionar uma de duas releases → corrigir dados incompletos → revisar → cancelar/salvar. Trocar edição existente e confirmar ID, original, links e manual preservados. Exercitar indisponível/503/ocupado/vazio, acesso manual, proveniência expirada e duas abas com conflito. |
| E-IM | Manual/automática/padrão, remover manual, imagem não válida/quebrada e padrão quebrada. Contar tentativas: uma troca para padrão, nenhum ciclo nem tentativa da automática substituindo manual quebrada. Título/ações continuam acessíveis e URLs do banco não mudam. |
| E-ST | Abrir Spotify e dois links nomeados, capturar destino/aba e proteção de opener; corrigir/remover; simular destino fora do ar e voltar para editar. Sem links, ausência de ação vazia e sorteio continua possível. |
| E-UI | Executar os percursos acima em Chromium e Firefox, PC 1366×768 e emulação 390×844/844×390. Incluir nomes/URLs longos, erros e vazios; teclado, foco visível, labels/erros, alt e toque; verificar largura da página e inspeção visual de cortes/controles. Sem ações exclusivas de hover. Não repetir em navegador todas as combinações unitárias. |
| E-OC | Uma consulta de catálogo lenta/503 em andamento enquanto outro contexto acessa biblioteca, busca, escreve e sorteia; novos fluxos externos informam ocupado, cache hit continua; navegação local permanece disponível. Confirmar comportamento em Waitress real para evidência das quatro threads. |

| ID operacional | Procedimento e aceite |
| --- | --- |
| O-ENV | Instalação limpa com hashes, versões/locks coerentes, diagnóstico, checks, migrações aplicadas em banco temporário, teste de configuração válida/inválida; smoke Waitress real, um processo/quatro threads, loopback e `DEBUG=False`; estáticos CSS/JS/padrão via WhiteNoise, 404/erros sem traceback; banco/backups/segredo/configuração inacessíveis por HTTP. Seguir README/operations sem conhecimento implícito. |
| O-BK | Salvar dataset rico em SQLite temporário em arquivo → encerrar/reiniciar aplicação → comparar todos os valores e IDs. Backup com escritor concorrente: validar integridade/FKs e estado transacional completo, sem exigir instante único do snapshot. Validar metadados e publicação só ao final. Restaurar offline em instância separada, comparar contagens, grafias, identidades/MBIDs, posições/vínculos, original/edição e precisões, nota, revisão/token, capas e todos os links. Bloquear APIs e consultar/sortear após recuperação. |
| O-BK (falhas) | Ausente/não SQLite/truncado/corrompido, FK inválida, migrações incompatíveis antigas/novas, destino inexistente/sem permissão, colisão, sem espaço e falha ao publicar metadados ou substituir arquivo; preservar origem, banco/cópia anterior e não anunciar sucesso parcial. Permissões testadas em ambiente em que tenham efeito, sem presumir resultado sob usuário privilegiado. Ensaiar roteiro por uma pessoa e registrar resultado; explicar URLs remotas, destino/frequência/retenção do proprietário, cópia antes de migrações/manutenção e risco do mesmo disco. |
| A-LAN | Registrar hardware/SO/versões, rede e modelo/navegador do celular. Habilitar LAN explicitamente, hosts/origens específicos, CSRF ativo e porta restrita à rede confiável. PC e celular real acessam e alteram a mesma biblioteca isolada; retrato/paisagem e toque nos fluxos RF-01–15, erros e vazios. Seguir diagnóstico com servidor desligado/rede isolada/IP alterado. Emulação não comprova LAN. Sem autenticação, dispositivos com acesso à porta podem ler/escrever: verificar documentação, não inventar perfis/permissões de usuário. |
| A-PERF | Dataset reproduzível de 1.000 álbuns e servidor pronto; 30 execuções por operação (biblioteca, busca representativa, sorteio global e por artista), sem catálogo. Guardar tempos brutos, primeira execução, máximo e p95, servidor e navegador separados. Medir do envio a HTML/controles utilizáveis, excluindo imagens externas: **nenhuma execução >2 s**. PC/celular também exercitados com catálogo lento. Registrar método de cálculo de p95 e ambiente; média/p95 isolados não aprovam máximo. |
| A-USO | No PC e celular, cadastro básico do formulário vazio utilizável à confirmação ≤60 s; localizar álbum conhecido e abrir streaming em ≤3 interações desde a biblioteca pronta. Contar clique/toque/submissão por teclado; texto é entrada registrada, não uma interação por caractere. Guardar sequência/duração reais; automação de velocidade de digitação não substitui teste de uso. |

## 7. Fixtures, dados, relógios e isolamento

- Criar pequenos construtores de dados de teste explícitos, usando ORM/serviços conforme a fronteira; evitar fixture global enorme, IDs dependentes da ordem e dependências entre testes. Casos inválidos destinados a constraints podem usar ORM direto no teste, sem tornar esse caminho uma operação suportada do produto.
- Base local: biblioteca vazia; álbum único sem opcionais; A, B, C e dois artistas homônimos com descrições/PKs diferentes; álbum A, B e colaboração A/B; mesmo título com conjuntos distintos; originais 1990/2005 e reedições 2020/2025; originais ausente, `1990`, `1990-05`, `1990-06` e data completa. Incluir créditos invertidos e PK repetida.
- Textos: grafias Unicode originais, compostos/decompostos, whitespace Unicode, pontuação, nomes longos, HTML/script e aspas/payload SQL; URLs `example.test`/domínios reservados com conteúdo interceptado, protocolos proibidos, credenciais e Spotify impostor. Nenhum token/URL privada ou resposta bruta real no repositório/log.
- Capas: nenhuma, automática somente, manual somente, ambas, manual quebrada, não imagem, padrão quebrada. Links: zero/dois, plataformas repetidas, incompletos e limites 20/21. Álbuns/artistas para paginação 0/1/50/51; artistas 30/31; construir textos no limite e +1 e POST medido em bytes para 256 KiB.
- Fixtures JSON mínimas em `library/tests/fixtures/`: pesquisa válida/vazia, duas edições, detalhes/release-group, original desconhecido, CAA frontal/ausente; variantes de campos opcionais e tipos inválidos. Gerar respostas grandes/comprimidas/fragmentadas em memória, sem versionar megabytes de JSON. Status, cabeçalhos e chunks controlados pelo transporte.
- Injetar data local fixa (por exemplo, 15/10/2026) e relógio monotônico independente; testar também virada anual e fusos com datas locais distintas no mesmo instante. Não usar data corrente do host nos resultados esperados. Controlar expiração/Retry-After e assinatura temporal; fonte aleatória seleciona posições conhecidas. Não exigir que repetição aconteça por acaso.
- Bancos/backup/configurações e relatórios privados em diretórios temporários, com limpeza garantida; não copiar coleção real. Reinício usa **mesmo arquivo temporário** entre processos; testes independentes usam arquivos distintos. Não limpar diretórios do usuário. Capturar logs com valores sentinela de teste para provar ausência de vazamento.
- Dataset de desempenho com semente e parâmetros registrados, contagem exata de 1.000 álbuns, mistura documentada de Unicode, colaborações, homônimos, datas parciais/ausentes, links e sem opcionais. Conferir invariantes e reprodução; a distribuição escolhida deve ficar registrada, sem inventar quotas de produto.

Mocks se restringem às fronteiras: HTTPX, relógios, aleatoriedade e falhas de I/O. Não mockar serviço inteiro no teste que pretende comprovar sua transação, nem ORM no teste de busca, nem lock no teste de contenção. Aplicar patch onde a dependência é usada, evitando acoplamento à decomposição privada.

## 8. Matriz de critérios de aceitação funcionais

Cada linha define testes **necessários, ainda planejados**. Referências E/O/A complementam o menor teste de regra/integração; não substituem a cobertura específica. Intervalos na coluna BL incluem todas as tarefas intermediárias.

| CA | Resultado a comprovar | Suítes | Backlog principal |
| --- | --- | --- | --- |
| CA-01.1 | Mínimo sem opcionais persiste e aparece com grafia informada | I-GR, H-WR, E-LO | BL-014, BL-016, BL-019 |
| CA-01.2 | Sem título/artistas: erro de campo, zero criação | U-FM, I-GR, H-WR | BL-014, BL-016, BL-019 |
| CA-01.3 | Dois artistas apontam ao mesmo álbum | I-GR, I-QU, E-LO | BL-009, BL-014, BL-019 |
| CA-01.4 | Busca vazia e falha permitem concluir manual | H-WR, E-EX | BL-019, BL-048, BL-053 |
| CA-01.5 | Cadastro básico ≤60 s | A-USO | BL-060 |
| CA-01.6 | Ano futuro manual/externo recusado, correção/ausência sem parcial | U-DT, I-GR, H-WR | BL-005, BL-016, BL-050 |
| CA-01.7 | Precisões, ausência, calendário/bissexto e futuro em original/edição | U-DT, I-GR | BL-004–BL-005, BL-008, BL-016 |
| CA-02.1 | Resultados selecionáveis sem persistência | X-CT, H-WR, E-EX | BL-045, BL-048 |
| CA-02.2 | Vazio real informa ausência e permite manual | X-CT, E-EX | BL-045, BL-048 |
| CA-02.3 | Rede/limite/timeout/inválido distinguem falha de vazio | X-CT, X-LIM, E-EX | BL-040–BL-045, BL-048, BL-053 |
| CA-02.4 | Rede de catálogo sai do Django, não do navegador | X-CT, E-EX | BL-040, BL-048 |
| CA-02.5 | Repetição dentro do TTL não faz nova chamada | X-LIM, C-EXT | BL-044 |
| CA-03.1 | Revisão antecede gravação; título corrigido é salvo | H-WR, I-GR, E-EX | BL-049–BL-050 |
| CA-03.2 | Cancelar revisão não cria álbum | H-WR, E-EX | BL-049 |
| CA-03.3 | Detalhes incompletos exigem corrigir obrigatórios | X-CT, U-FM, H-WR | BL-046, BL-049–BL-050 |
| CA-03.4 | MBID persistido é o da edição selecionada entre duas | X-CT, I-GR, E-EX | BL-046, BL-049–BL-050 |
| CA-03.5 | Consulta/sorteio após salvar funcionam sem APIs | I-QU, I-SO, E-LO | BL-035, BL-050, BL-053 |
| CA-04.1 | Sem manual, capa automática compatível é exibida | X-CT, U-CP, E-IM | BL-030–BL-031, BL-047 |
| CA-04.2 | Sem capa utilizável/manual quebrada usa padrão; manual válida resiste a falha automática | U-CP, E-IM | BL-030–BL-031, BL-053 |
| CA-04.3 | URL manual salva/exibe; remoção aplica alternativa | U-CP, H-WR, E-IM | BL-006, BL-030–BL-031 |
| CA-04.4 | Falha de capa não impede persistir | X-CT, I-GR, E-EX | BL-047, BL-050 |
| CA-04.5 | Padrão quebrada não causa loop nem impede leitura | E-IM | BL-031 |
| CA-04.6 | Prioridade manual em nova consulta/troca; quebra conserva URL, remoção reativa automática | U-CP, I-TR, E-IM | BL-030–BL-031, BL-051–BL-052 |
| CA-05.1 | Biblioteca e detalhes mostram dados persistidos | I-QU, E-LO | BL-022 |
| CA-05.2 | Vazio compreensível com cadastro acessível | H-WR, E-UI | BL-022 |
| CA-05.3 | Biblioteca/detalhes disponíveis sem APIs | I-QU, E-LO | BL-022, BL-035 |
| CA-05.4 | ID inexistente recebe 404 sem erro interno | H-WR | BL-022 |
| CA-05.5 | Ordem temporal mista, ausentes ao fim, desempate, sem componentes artificiais | U-DT, I-QU | BL-004, BL-022 |
| CA-06.1 | Página de artista contém somente seus álbuns | I-QU, E-LO | BL-023 |
| CA-06.2 | Colaboração usa mesmo ID em A/B, uma linha global | I-GR, I-QU, E-LO | BL-009, BL-023 |
| CA-06.3 | Retirar B altera páginas e oculta B se último vínculo | I-TR, I-QU, H-WR | BL-025–BL-026 |
| CA-06.4 | Último álbum removido oculta artista sem afetar demais | I-GR, I-QU, H-WR | BL-027–BL-028 |
| CA-06.5 | Homônimos exigem descrição; PK repetida não duplica vínculo/peso e gera indicação | I-ID, U-FM, I-SO, E-ID | BL-007, BL-011, BL-016 |
| CA-06.6 | Identidade retida, lista omite, URL/conjunto/sorteio vazios corretos | I-ID, I-QU, I-SO | BL-023, BL-027–BL-028, BL-033 |
| CA-07.1 | Título completo encontra álbum | I-QU, E-LO | BL-024 |
| CA-07.2 | Nome do artista encontra seus álbuns e colaborações | I-QU | BL-024 |
| CA-07.3 | Termo sem correspondência mostra vazio sem mutação | I-QU, H-WR | BL-024 |
| CA-07.4 | Mesmos resultados anteriores com APIs bloqueadas | I-QU, E-LO | BL-024, BL-035 |
| CA-07.5 (RF-07 e §10.3) | Sem duplicação, busca parcial normalizada, vazio todos, ordem/páginas de 50 | U-TX, I-QU, H-WR | BL-003, BL-024 |
| CA-07.6 | Caixa/acentos/espaços equivalentes, grafia e homônimos preservados | U-TX, I-QU | BL-003, BL-024 |
| CA-08.1 | Atualização aparece em biblioteca/detalhes/busca/artistas | I-TR, H-WR, E-LO | BL-025–BL-026 |
| CA-08.2 | Obrigatórios inválidos conservam registro anterior | U-FM, I-TR, H-WR | BL-025–BL-026 |
| CA-08.3 | Cancelar edição conserva tudo | H-WR, E-LO | BL-026 |
| CA-08.4 | Colisão na edição exige revisão, sem fusão | I-ID, I-TR, H-WR | BL-025–BL-026 |
| CA-09.1 | Selecionar/revisar nova edição não altera biblioteca antes de confirmar | H-WR, E-EX | BL-051–BL-052 |
| CA-09.2 | Confirmação atualiza edição/valores no mesmo ID | I-TR, E-EX | BL-051–BL-052 |
| CA-09.3 | Spotify e todos os links anteriores permanecem iguais | I-TR, E-EX | BL-051–BL-052 |
| CA-09.4 | Cancelamento/falha externa conserva registro integral | X-CT, H-WR, E-EX | BL-051–BL-052 |
| CA-09.5 | Nova combinação com candidato exige RF-10 | I-ID, I-TR, H-WR | BL-051–BL-052 |
| CA-09.6 | Original 1990, troca 2020→2025 conserva original/ID/manual prioritária | U-DT, I-TR, E-EX | BL-005, BL-051–BL-052 |
| CA-09.7 | Data própria opcional da edição revisada independente do original | U-DT, I-TR, H-WR | BL-008, BL-051–BL-052 |
| CA-10.1 | Mesmo título/conjunto/data ou original insuficiente avisa e permite revisar | I-ID, E-ID | BL-012–BL-013, BL-020 |
| CA-10.2 | Ordem invertida dos artistas mantém candidato | I-ID, E-ID | BL-012, BL-020 |
| CA-10.3 | Outra edição atualiza único registro só após confirmação | I-ID, I-TR, E-EX | BL-013, BL-051–BL-052 |
| CA-10.4 | Cancelar revisão não altera coleção | H-WR, E-ID | BL-020 |
| CA-10.5 | Mesmo título com conjunto diferente não prova mesmo álbum | I-ID | BL-012 |
| CA-10.6 | Grafias normalizadas localizam mesmo candidato sem perder exibição | U-TX, I-ID | BL-003, BL-012, BL-020 |
| CA-10.7 | Distintos originais 1990/2005 coexistem; reedição 2020 revisa o de 1990 | I-ID, I-TR, E-ID | BL-012–BL-013, BL-020, BL-051 |
| CA-10.8 | Original ausente/sobreposto/igual exige confirmação e nota; cancelar/sem nota não cria | I-ID, H-WR, E-ID | BL-013, BL-020 |
| CA-10.9 | Intervalos 1990/1990-05 sobrepõem, maio/junho não; sem dedução automática de identidade | U-DT, I-ID | BL-004, BL-012–BL-013 |
| CA-11.1 | Cancelar confirmação conserva álbum | H-WR, E-LO | BL-028 |
| CA-11.2 | Confirmar remove de biblioteca/busca/artistas/sorteio | I-GR, I-QU, I-SO, E-LO | BL-027–BL-028 |
| CA-11.3 | Remover colaboração limpa vínculos/links e preserva outros álbuns/artistas | I-GR, H-WR | BL-027–BL-028 |
| CA-11.4 | ID removido responde 404 | H-WR | BL-028 |
| CA-12.1 | Spotify e dois links têm nomes/destinos corretos e abrem | I-GR, E-ST | BL-017, BL-029 |
| CA-12.2 | Correção/remoção reflete destino ou ausência da ação | I-TR, E-ST | BL-025–BL-026, BL-029 |
| CA-12.3 | Sem links não há ação vazia; continua consultável/sorteável | I-SO, E-ST | BL-017, BL-029, BL-032 |
| CA-12.4 | Destino indisponível mantém consulta e correção possíveis | E-ST | BL-029 |
| CA-12.5 | Streaming aberto em ≤3 interações desde biblioteca | A-USO | BL-060 |
| CA-12.6 | Limites exatos/+1, protocolos, Spotify/credenciais, plataformas repetidas; sem truncar/parcial | U-LM, U-FM, I-GR, H-SEC | BL-006, BL-014, BL-016–BL-019 |
| CA-13.1 | Toda saída pertence à biblioteca persistida | I-SO | BL-032 |
| CA-13.2 | Um álbum sempre é selecionado | I-SO | BL-032 |
| CA-13.3 | Uma participação por álbum e seleção uniforme por inspeção/posições controladas | I-SO | BL-032 |
| CA-13.4 | Último resultado permanece elegível; repetição controlada permitida | I-SO | BL-032 |
| CA-13.5 | Sorteio sem APIs e desempenho local cumprido | I-SO, A-PERF | BL-032, BL-035, BL-059 |
| CA-14.1 | A retorna somente álbum A ou colaboração A/B | I-SO | BL-033 |
| CA-14.2 | Colaboração participa uma vez com mesma chance | I-SO | BL-033 |
| CA-14.3 | Único álbum do artista é retornado | I-SO | BL-033 |
| CA-14.4 | Artista inexistente 404, retido vazio orienta sem outro artista | I-SO, H-WR | BL-033–BL-034 |
| CA-15.1 | Biblioteca vazia orienta cadastrar e permite acesso | H-WR, E-UI | BL-034 |
| CA-15.2 | Artista vazio informa ausência contextual | I-SO, H-WR, E-UI | BL-033–BL-034 |
| CA-15.3 | Vazios sem erro interno ou resultado fora do conjunto | I-SO, H-WR | BL-032–BL-034 |
| CA-16.1 | Reinício conserva valores/associações | O-BK | BL-035, BL-039 |
| CA-16.2 | Backup/restore isolado conserva todos os dados e precisões especificados | O-BK | BL-036–BL-039, BL-056 |
| CA-16.3 | Restaurada consulta/sorteia sem APIs | O-BK | BL-039, BL-056 |
| CA-16.4 | Ausente/inválido/incompatível/falha preserva biblioteca/cópia anterior | O-BK | BL-038–BL-039, BL-056 |
| CA-16.5 | Documento explica preservação de URL, sem garantia de imagem | O-BK, revisão documental | BL-037, BL-056 |

## 9. Matriz transversal e cobertura do backlog

Os critérios verificáveis de RNF/SEG/INT são obrigatórios além dos CA funcionais. Cada RN está identificado na tabela de invariantes; esta matriz acrescenta evidências transversais.

| Requisito | Evidência necessária |
| --- | --- |
| RNF-01 | O-ENV + A-LAN: instalação/HTML/SQLite local e mesma biblioteca no celular. |
| RNF-02 | E-UI + A-LAN: todos os fluxos RF-01–15 e erros/vazios em PC/emulação/celular real. |
| RNF-03 | I-QU/I-SO/E-LO/O-BK: bloqueio de catálogo em consulta/busca/sorteio após salvar/reiniciar/restaurar. |
| RNF-04 | A-PERF: 1.000 álbuns, 30 execuções/operação e máximo ≤2 s. |
| RNF-05 | A-USO: tempos e sequência real de interações nos dois dispositivos. |
| RNF-06 | I-GR/I-TR/C-DB/O-BK: falhas, commits e rollback em cada operação composta. |
| RNF-07 | U-FM/H-WR/E-EX: erros associados, alternativa e valores preservados quando possível. |
| RNF-08 | E-UI/A-LAN: teclado, foco, labels/erros, alt e toque; sem afirmar certificação de acessibilidade. |
| RNF-09 | H-SEC/O-ENV: categoria de diagnóstico em logs e ausência de internos nas respostas. |
| RNF-10 | O-BK: uma pessoa reproduz roteiro completo sem passo implícito. |
| INT-01 | X-CT/X-LIM/C-EXT: contrato MusicBrainz, identificação, taxa/cache/pausa e falhas. |
| INT-02 | X-CT/X-LIM/E-IM: contrato CAA e enriquecimento opcional. |
| SEG-01 | O-ENV/A-LAN: loopback padrão, opção LAN explícita, hosts específicos e limitação sem autenticação documentada. |
| SEG-02 | H-SEC/H-WR: métodos e CSRF em criação, edição, troca, remoção e sorteios; GET sem mutação. |
| SEG-03 | U-LM/I-GR/H-SEC/X-CT: validação servidor de todos os caminhos, HTML escapado e SQL tratado como dado. |
| SEG-04 | U-LM/H-SEC: protocolos/hosts/credenciais verificados por POST direto e importação. |
| SEG-05 | X-CT/H-SEC/E-IM: origens fixas e redirects privados recusados; zero fetch servidor de capas manuais/retornadas e streaming. |
| SEG-06 | X-CT: TLS obrigatório e certificado inválido tratado; distinguir erro simulado de handshake real. |
| SEG-07 | H-SEC/E-ST: nova aba sem acesso à janela de origem. |
| SEG-08 | H-SEC/O-ENV/O-BK: respostas/logs/estáticos sem segredo, banco ou backup. |
| SEG-09 | O-ENV/O-BK/A-LAN: instruções e verificação de proteção local dos arquivos conforme SO. |
| SEG-10 | U-LM/U-FM/H-WR/X-LIM/C-EXT: entradas/corpo/formsets, resposta descomprimida, cache/admissão e tempo finitos. |

P-01/02/03 são cobertas por I-ID/U-DT/I-TR; P-04/05 por U-LM/U-FM/I-QU/X-CT; P-06 por X-CT/X-LIM/C-EXT; P-07 por U-CP/E-IM/O-BK; P-08 por E-UI/A-LAN/A-PERF/A-USO; P-09 por O-BK. ADR-01/02/03/09/10 são verificadas por O-ENV e revisão dos limites arquiteturais; ADR-04 por X-LIM/C-EXT; ADR-05 por I-ID; ADR-06 por E-IM; ADR-07 por I-SO; ADR-08 por C-DB; ADR-11 por O-BK.

Todos os critérios próprios das tarefas do backlog também entram no D0; a coluna de escopo abaixo complementa a matriz CA e evita perder contratos técnicos sem CA dedicado.

| Tarefas | Critérios próprios / suítes necessárias |
| --- | --- |
| BL-001–BL-002 | Instalação limpa, patches/locks, configuração/privacidade/fuso e opções SQLite: O-ENV. |
| BL-003–BL-006 | Normalização, datas/intervalos/futuro, tamanhos e URLs: U-TX/U-DT/U-LM. |
| BL-007–BL-010 | Migrações, round-trip, constraints, índices aprovados, posições/cascatas e identidade não única por texto: I-GR/I-ID/O-ENV. |
| BL-011–BL-013 | Seleção/criação de artista, conjunto exato, ambiguidade/nota e revisão: I-ID. |
| BL-014–BL-015 | Criação atômica, 30 artistas, revalidação, token/assinatura/reenvio: I-GR/C-DB. |
| BL-016–BL-017 | Forms/formsets sem gravação antecipada, dados preservados e links até 20: U-FM/I-GR. |
| BL-018–BL-019 | Base responsiva, escape, CSRF/PRG, corpo 256 KiB: H-WR/H-SEC/E-UI. |
| BL-020–BL-021 | Revisão acessível, candidato entre prévia/POST, lock/armazenamento/logs: I-ID/H-WR/C-DB. |
| BL-022–BL-024 | Biblioteca/detalhes/artistas/busca, páginas de 50, sem N+1/rede: I-QU/H-WR. |
| BL-025–BL-028 | Edição e remoção atômicas com revisão, cancelamento e efeitos visíveis: I-TR/I-GR/H-WR/C-DB. |
| BL-029–BL-031 | Streaming, precedência/fallback, atributos seguros e nenhum fetch pelo servidor: U-CP/H-SEC/E-ST/E-IM. |
| BL-032–BL-034 | Snapshot uniforme global/artista e estados vazios/404/CSRF: I-SO/H-WR/C-DB. |
| BL-035 | Percurso local essencial, persistência após reinício: E-LO/O-BK. |
| BL-036–BL-039 | Snapshot SQLite, comando/metadados, inspeção isolada e restore offline: O-BK, inclusive escrita concorrente e falhas. |
| BL-040–BL-044 | TLS/origens/identificação, orçamentos, admissão/taxa, pausa/cache: X-CT/X-LIM/C-EXT. |
| BL-045–BL-047 | Pesquisa literal/páginas de 20, detalhes/proveniência/original, CAA opcional: X-CT/X-LIM. |
| BL-048–BL-050 | Busca HTTP, revisão sem provisório, proveniência adulterada/expirada, POST sem dependência de cache: H-WR/H-SEC/E-EX/I-GR. |
| BL-051–BL-053 | Troca com dados protegidos, duas abas, falha/consulta lenta e disponibilidade local: I-TR/C-DB/E-EX/E-OC. |
| BL-054–BL-056 | Smoke cotidiano, roteiro instalação/LAN e recuperação por pessoa: O-ENV/O-BK/A-LAN. |
| BL-057–BL-060 | Dataset/ambiente, matriz de dispositivos, LAN real, tempos e uso: E-UI/A-LAN/A-PERF/A-USO. |
| BL-061–BL-062 | Auditar matrizes SEG/CA, executar regressões/checks pertinentes e consolidar evidências/limites: todas as suítes aplicáveis, sem duplicar medições válidas sem motivo. |

## 10. Execução, evidências e condições de conclusão

Para cada tarefa de comportamento autorizada: escolher o menor exemplo observável, escrever teste e confirmar **falha esperada**, implementar o mínimo, passar teste/regressões pertinentes e refatorar com nova execução. Adicionar extremos gradualmente. Não escrever toda a suíte depois da implementação. Infraestrutura/documentação usam verificação reproduzível, sem testes artificiais para cobertura.

Testes ficam em `library/tests/test_*.py`, descobertos pelo runner Django. Os arquivos sugeridos neste documento não exigem criação antecipada. Comandos de referência para a implementação futura:

```bash
source .venv/bin/activate
# DJANGO_SECRET_KEY de teste deve estar no ambiente; nunca registrar seu valor.
python manage.py test library.tests.test_modulo.Classe.test_caso
python manage.py test
python manage.py makemigrations --check --dry-run
bash scripts/check.sh
```

`bash scripts/check.sh` é obrigatório ao concluir alterações de código/configuração e reúne dependências, Ruff/formatação, mypy estrito, checks Django, migrações pendentes, testes/coverage, collectstatic, smoke Waitress e diagnóstico. Instalação limpa deve usar `--require-hashes`. Novos modelos exigem migrações versionadas e aplicadas em banco temporário. Mudanças em fluxos exigem Playwright pertinente com Chromium/Firefox instalados conforme README; ausência de binário é impedimento, não teste aprovado. Testes de navegador/concorrência devem continuar descobertos pelo runner, com configuração explícita de arquivos temporários quando necessária.

Em cada mudança, executar primeiro o recorte afetado e depois as verificações exigidas; ampliar testes quando novas alterações/falhas justificarem. CI automatiza verificações determinísticas com fixtures/transporte local, sem contatos reais, coleções reais ou medições de uso humano. Ensaios de LAN, uso e desempenho pertencem ao ambiente registrado; não converter duração variável de CI em aceite P-08.

Cobertura de ramos serve para localizar caminhos não exercitados, sobretudo validação, rollback, conflito e fallback. Não se define porcentagem arbitrária como aceite. Um teste pode cobrir vários critérios, mas cada critério precisa de resultado e evidência própria. Revisão estrutural do sorteio complementa, sem substituir, testes de elegibilidade.

Registrar em `docs/acceptance.md`: RF/CA/RN/SEG/INT/P/BL relacionados, cenário/suíte/comando real, versão do código, data/ambiente/dataset, resultado esperado/observado, evidência e limites. Para navegador, registrar motor/viewport/dispositivo e capturas/traces pertinentes sem dados privados; para concorrência, ordem coordenada e estado final; para desempenho, tempos brutos/máximo/p95. Estados: **planejado, aprovado, falhou ou impedido**, com motivo; “não executado” nunca é aprovado.

O aceite final BL-062 exige critérios funcionais e técnicos comprovados, checks aplicáveis aprovados, fluxos PC/celular real, metas medidas e recuperação isolada reproduzida. Contato real deve existir antes de chamadas reais; ambiente/celular antes das medições; destino privado de backup antes de dados reais. Ausência desses dados não bloqueia testes simulados nem autoriza declarar metas cumpridas. Esta estratégia deixa todos os testes futuros planejados e não encerra nenhuma tarefa de implementação ou aceite.
