# Especificação de requisitos — biblioteca pessoal de álbuns

**Data:** 13/10/2026  
**Estado:** proposta para aprovação; nenhuma implementação autorizada.  
**Fonte principal:** [PROJECT_SCOPE.md](PROJECT_SCOPE.md).  
**Complementos:** esclarecimentos do usuário nesta conversa, registrados abaixo.

## 1. Objetivo, limites e interpretação

Aplicativo web pessoal para centralizar uma coleção escolhida de álbuns, organizá-la por artista, pesquisar seus registros, sortear o que ouvir e abrir links de streaming. O usuário inicial é o proprietário da biblioteca.

O MVP funciona localmente com Django, SQLite e templates HTML/CSS responsivos. Inclui biblioteca, página do artista, detalhes do álbum e formulário de cadastro/edição. As consultas a catálogos externos são realizadas no servidor Django. Dados persistidos devem permitir consulta e sorteio quando esses catálogos estiverem indisponíveis.

O acesso pelo navegador deve funcionar tanto em PC quanto em dispositivos móveis, com todas as funcionalidades do MVP disponíveis nos dois contextos. No MVP local, o celular acessa a mesma aplicação e biblioteca pela mesma rede local confiável, com o servidor em execução no computador e acesso de rede configurado explicitamente e documentado. Isso não inclui publicação na internet.

Não fazem parte do MVP: publicação, PostgreSQL, autenticação para serviço publicado, múltiplos usuários, compartilhamento, API pública, contas de streaming, reprodução interna, sincronização com Spotify, histórico de escuta, avaliações, tags, filtros avançados, sorteio sem repetição e importação/exportação em lote. Backup e restauração local fazem parte do MVP e não equivalem a importação/exportação em lote.

### 1.1 Origem e força dos requisitos

- **E — Escopo:** requisito explicitamente previsto no escopo aprovado.
- **U — Usuário:** decisão esclarecida nesta conversa.
- **D — Derivado:** condição necessária para consistência ou verificação de um requisito E/U, sem criar nova funcionalidade de negócio.
- **T — Proposta técnica:** proteção ou convenção recomendada para o MVP, sujeita à aprovação deste documento.
- **P — Pendente:** questão não decidida; alternativas e números não devem ser tratados como requisitos aprovados.

Os critérios de aceitação descrevem o comportamento que deverá ser verificado quando houver implementação. Requisitos T ainda são propostas. Critérios relacionados a P só podem ser concluídos depois da definição indicada na seção 10.

### 1.2 Esclarecimentos incorporados

| ID | Origem | Decisão |
| --- | --- | --- |
| DEC-01 | U | O usuário decide qual edição será salva. Mantém-se a regra do escopo de um registro por álbum; não há autorização para guardar duas edições como dois registros do mesmo álbum. |
| DEC-02 | U | É possível trocar a edição do MusicBrainz de um álbum já salvo. |
| DEC-03 | U | Na troca de edição, o usuário revisa os dados antes de salvar e os links de streaming existentes são preservados. |
| DEC-04 | U/T | O usuário delegou a escolha da forma de informar capas manuais. Adota-se URL de imagem opcional, junto da obtenção automática e da imagem padrão; upload de arquivo fica fora deste MVP. |
| DEC-05 | U | O aplicativo deve ser acessível tanto em PC quanto em dispositivos móveis, pelo navegador, com interface responsiva e funcionalidades equivalentes. |

## 2. Dados, entradas, saídas e restrições

Este é um modelo conceitual, não uma decisão sobre tabelas ou detalhes de implementação.

| Entidade/campo | Entrada esperada | Saída/uso esperado | Obrigatoriedade e validação |
| --- | --- | --- | --- |
| Álbum: identificador local | Gerado pelo aplicativo | Referência estável para detalhe, edição, remoção e sorteio | Obrigatório internamente; não depende da API externa (D). |
| Título | Texto manual ou sugerido pelo MusicBrainz | Listagens, detalhes, busca e aviso de duplicado | Obrigatório (E); rejeitar valor vazio ou composto somente por espaços (D). Limite de tamanho: P-04. |
| Artistas do álbum | Um ou mais artistas selecionados/informados | Associação do mesmo álbum às páginas dos artistas e à busca | Pelo menos um obrigatório (E); nomes não podem ser vazios (D). Identidade/normalização: P-02. |
| Ano | Valor manual ou sugerido pela edição escolhida | Informação opcional do álbum | Pode ficar ausente (E); formato, intervalo e significado: P-03. Não converter ausência em zero (D). |
| Edição externa | Resultado escolhido do MusicBrainz e identificação compatível | Proveniência e consulta de capa; troca de edição | Opcional no cadastro manual (D); não associar automaticamente uma edição a partir apenas de título/artista (E/D). |
| Capa | Resultado do Cover Art Archive ou URL manual | Imagem do álbum ou imagem padrão | Opcional (E/U); URL HTTP/HTTPS válida como proposta T; ausência ou falha da imagem exige alternativa visual. |
| Spotify | URL preenchida manualmente | Ação para abrir o destino externo | Opcional (E); protocolo seguro: T; restrição ao domínio Spotify: P-04. |
| Links adicionais | Pares de nome da plataforma e URL | Ações externas identificadas pelo nome | O conjunto pode ser vazio (E); cada item informado exige nome e URL completos (D). Quantidade e nomes repetidos: P-04. |
| Consulta à coleção | Texto de título ou artista | Álbuns locais correspondentes, ou estado sem resultados | Não altera registros; correspondência, acentos e consulta vazia: P-05. |
| Consulta ao MusicBrainz | Texto para pesquisa | Resultados de catálogo ou estado sem resultados/falha | Dados externos são sugestões; seleção e revisão precedem persistência (E). Campos e paginação: P-05. |
| Sorteio | Toda a biblioteca ou um artista | Um álbum elegível ou explicação de conjunto vazio | Não depende de ano, capa, links ou estado de escuta (E/D). |
| Confirmação de remoção | Álbum alvo e confirmação explícita | Registro removido ou operação cancelada | Cancelamento conserva o registro e suas associações (E/D). |
| Backup/restauração | Biblioteca local e cópia válida | Cópia recuperável e coleção restaurada | Procedimento documentado e verificado (E); armazenamento de capas deve ser contemplado (D). |

Nomes e títulos com caracteres Unicode e pontuação devem ser preservados na apresentação (T). Limites de campos não podem ser definidos silenciosamente durante a implementação. Dados externos passam pelas mesmas validações de persistência dos dados manuais (D).

## 3. Requisitos funcionais e critérios de aceitação

### RF-01 — Cadastrar manualmente (E)

**Entrada:** título, pelo menos um artista e campos opcionais. **Saída:** um álbum persistido, consultável na biblioteca e nas páginas dos artistas.

**Comportamento:** oferecer cadastro manual quando a busca não encontrar o álbum ou estiver indisponível. Ano, capa, links e identificação externa não são necessários para salvar. O formulário deve permitir múltiplos artistas.

**Aceitação:**

- CA-01.1: salvar título e um artista, sem nenhum campo opcional; o registro aparece na biblioteca e nos detalhes com os valores informados.
- CA-01.2: tentar salvar sem título ou sem artistas; apresentar erro associado ao campo e não criar registro.
- CA-01.3: salvar um álbum com dois artistas; ambos apontam para o mesmo registro local.
- CA-01.4: em busca sem resultados e em falha externa simulada, o usuário consegue concluir cadastro manual.
- CA-01.5: cadastrar um álbum básico em até 60 segundos em teste de uso; protocolo de medição conforme RNF-05/P-08.

### RF-02 — Pesquisar no MusicBrainz (E)

**Entrada:** consulta de catálogo. **Saída:** resultados disponíveis para escolha, estado sem resultados ou aviso de indisponibilidade.

**Comportamento:** executar chamadas pelo servidor; respeitar controle de frequência e cache. A pesquisa, por si só, não cadastra álbuns.

**Aceitação:**

- CA-02.1: com resposta válida contendo resultados, apresentar opções para seleção sem persistir registros na coleção.
- CA-02.2: com resposta vazia, informar ausência de resultados e disponibilizar cadastro manual.
- CA-02.3: com falha, limite, demora excedida ou resposta inválida, informar que a consulta não foi concluída e permitir cadastro manual.
- CA-02.4: observar a comunicação de rede e confirmar que consultas de catálogo passam pelo servidor Django.
- CA-02.5: repetir consulta dentro da janela configurada de cache e verificar reaproveitamento sem nova chamada externa; janela depende de P-06.

### RF-03 — Escolher edição, revisar e salvar dados importados (E/U)

**Entrada:** resultado selecionado e valores revisados. **Saída:** um registro local correspondente à edição escolhida.

**Comportamento:** não escolher nem combinar edições automaticamente. Exibir os dados disponíveis para revisão; permitir correção manual. Informação externa incompleta não elimina a validação de título/artistas. A apresentação deve permitir distinguir as edições com os dados que o catálogo fornecer (D); conjunto exato de campos depende de P-01.

**Aceitação:**

- CA-03.1: selecionar resultado; abrir revisão antes de persistir; alterar título e salvar, verificando o valor revisado.
- CA-03.2: cancelar revisão; confirmar que nenhum álbum foi criado.
- CA-03.3: selecionar edição sem título ou artistas completos; exigir correção antes do salvamento.
- CA-03.4: selecionar uma entre duas edições distintas; verificar que a identificação persistida corresponde à escolha do usuário.
- CA-03.5: após salvar e tornar as APIs indisponíveis, consultar e sortear o álbum com os dados persistidos.

### RF-04 — Obter, informar e exibir capa (E/U/T)

**Entrada:** identificação externa compatível ou URL manual opcional. **Saída:** capa disponível ou imagem padrão.

**Comportamento:** consultar o Cover Art Archive quando houver identificação compatível. Falha ou ausência de capa não impede salvar nem consultar o álbum. Permitir informar, substituir ou remover a URL manual. Ordem de precedência entre capa manual e automática depende de P-07.

**Aceitação:**

- CA-04.1: para uma identificação compatível com capa disponível, exibir a capa retornada.
- CA-04.2: sem identificação, sem capa, com falha do serviço ou com URL de imagem quebrada, exibir imagem padrão e manter os demais dados e ações disponíveis.
- CA-04.3: informar uma URL válida de imagem no cadastro manual; salvar e exibir a imagem; remover o valor e verificar a alternativa aplicável.
- CA-04.4: não bloquear persistência por indisponibilidade da capa.
- CA-04.5: falha de carregamento da imagem padrão não provoca um ciclo de tentativas nem impede leitura do título/artistas (T).

### RF-05 — Listar biblioteca e consultar detalhes (E)

**Entrada:** acesso à biblioteca ou identificador local. **Saída:** coleção ou detalhes do álbum solicitado.

**Comportamento:** permitir chegar a título, artistas, dados opcionais existentes e ações de edição, remoção e streaming. Identificadores inexistentes recebem tratamento próprio.

**Aceitação:**

- CA-05.1: com álbuns cadastrados, localizar um registro na biblioteca e consultar seus dados persistidos.
- CA-05.2: com coleção vazia, apresentar estado compreensível e acesso ao cadastro.
- CA-05.3: com APIs indisponíveis, listagem e detalhes continuam disponíveis; capas podem usar imagem padrão.
- CA-05.4: solicitar identificador inexistente; apresentar registro não encontrado sem erro interno exposto.

### RF-06 — Listar artistas e seus álbuns (E)

**Entrada:** acesso à organização por artista e escolha de um artista. **Saída:** artistas da coleção e álbuns associados ao escolhido.

**Comportamento:** um álbum colaborativo pertence a cada artista associado, mantendo um único registro. Tratamento de artistas sem álbuns e nomes equivalentes depende de P-02.

**Aceitação:**

- CA-06.1: cadastrar álbuns de artistas diferentes; abrir cada artista e verificar que aparecem apenas seus álbuns.
- CA-06.2: cadastrar colaboração entre A e B; verificar o mesmo identificador local nas páginas de A e B, sem duplicação na biblioteca.
- CA-06.3: retirar B do álbum por edição; o álbum deixa de aparecer na página de B e permanece na de A.

### RF-07 — Pesquisar a coleção local (E)

**Entrada:** texto de título ou artista. **Saída:** álbuns correspondentes ou aviso de ausência de resultados.

**Comportamento:** pesquisar dados persistidos sem depender de catálogos. Um álbum associado a vários artistas deve aparecer uma única vez no resultado (D). Detalhes da correspondência dependem de P-05.

**Aceitação:**

- CA-07.1: pesquisar o título completo de um álbum conhecido e encontrar seu registro.
- CA-07.2: pesquisar o nome completo de um artista e encontrar seus álbuns, inclusive colaborações.
- CA-07.3: usar termo que não corresponda a registros; apresentar resultado vazio, sem alterar a coleção.
- CA-07.4: executar os casos anteriores com APIs externas indisponíveis e obter os mesmos registros.
- CA-07.5: verificar ausência de linhas duplicadas quando mais de uma associação satisfizer a busca.

### RF-08 — Editar informações (E)

**Entrada:** registro existente e valores revisados. **Saída:** mesmo registro atualizado ou erros de validação.

**Comportamento:** permitir editar título, artistas, ano, capa e links. Validar os campos como no cadastro. Cancelar não altera o registro. Colisão com outro álbum exige o mesmo fluxo de revisão de RF-10 (D).

**Aceitação:**

- CA-08.1: alterar dados obrigatórios e opcionais; verificar novos valores na biblioteca, detalhes, busca e páginas dos artistas.
- CA-08.2: remover todos os artistas ou tornar título vazio; recusar alteração e conservar o estado anterior.
- CA-08.3: cancelar edição; verificar que os dados persistidos permanecem iguais.
- CA-08.4: editar para uma combinação de título/artistas já existente; indicar possível duplicado sem combinar automaticamente registros.

### RF-09 — Trocar a edição do MusicBrainz (U)

**Entrada:** álbum existente, nova edição escolhida e dados revisados. **Saída:** mesmo registro local associado à nova edição.

**Comportamento:** possibilitar busca/seleção de outra edição e revisão dos valores de título, artistas, ano e capa antes de salvar. Preservar os links de streaming existentes durante essa troca. A troca não cria um segundo registro do mesmo álbum nem sobrescreve silenciosamente dados revisados.

**Aceitação:**

- CA-09.1: escolher nova edição; antes de confirmar, verificar que a biblioteca conserva os dados anteriores.
- CA-09.2: revisar os valores propostos e salvar; verificar o mesmo identificador local, a nova edição e os valores confirmados.
- CA-09.3: confirmar que Spotify e todos os links adicionais anteriores permanecem iguais após a troca.
- CA-09.4: cancelar ou provocar falha de obtenção da nova edição; verificar preservação integral do registro anterior.
- CA-09.5: trocar por edição cuja combinação título/artistas colida com outro registro; acionar RF-10, sem alteração automática.

### RF-10 — Avisar possível duplicado e revisar o existente (E/U)

**Entrada:** tentativa de salvar o mesmo título e conjunto de artistas de registro existente. **Saída:** aviso e acesso à revisão do registro existente.

**Comportamento:** manter um registro por álbum. A ordem dos artistas não muda o conjunto. Não combinar registros automaticamente. O usuário decide qual edição manter por revisão do registro existente, com troca conforme RF-09 quando aplicável. A equivalência de grafias depende de P-02; a distinção entre álbuns diferentes com título/artistas idênticos depende de P-01.

**Aceitação:**

- CA-10.1: cadastrar uma combinação já persistida, com a mesma grafia; receber aviso e conseguir revisar o registro existente.
- CA-10.2: tentar a mesma combinação com artistas em ordem invertida; receber o mesmo aviso.
- CA-10.3: escolher outra edição do mesmo álbum no fluxo de revisão; verificar que permanece um registro, atualizado somente após confirmação.
- CA-10.4: cancelar a revisão; verificar que a coleção não foi alterada.
- CA-10.5: título igual e conjunto de artistas diferente não deve, por esse motivo isolado, ser considerado o mesmo álbum.

### RF-11 — Remover álbum com confirmação (E)

**Entrada:** álbum e confirmação explícita. **Saída:** remoção persistida ou cancelamento.

**Comportamento:** identificar o álbum na confirmação. Remover suas associações e links da coleção; preservar os demais álbuns. O destino de artistas sem álbuns depende de P-02. Não se exige lixeira ou recuperação individual.

**Aceitação:**

- CA-11.1: cancelar a confirmação; o álbum permanece disponível.
- CA-11.2: confirmar; o álbum deixa de aparecer em biblioteca, busca, páginas de artista e conjuntos de sorteio.
- CA-11.3: remover uma colaboração; nenhum dos artistas mantém associação com o álbum removido e os demais álbuns permanecem intactos.
- CA-11.4: acessar depois o identificador removido; receber estado de registro não encontrado.

### RF-12 — Manter e abrir links de streaming (E)

**Entrada:** Spotify opcional e pares adicionais de plataforma/URL. **Saída:** navegação externa ao destino informado.

**Comportamento:** links são manuais e corrigíveis. Não garantir reprodução, disponibilidade ou correspondência com a mesma edição. Não exigir integração com contas de streaming. Forma de abertura em aba/janela é uma escolha de interface (T), sem login interno obrigatório.

**Aceitação:**

- CA-12.1: salvar Spotify e dois links adicionais; verificar nomes e destinos nos detalhes e abrir cada URL correspondente.
- CA-12.2: corrigir ou remover link; verificar atualização do destino ou ausência da ação.
- CA-12.3: sem links, indicar ausência de links ou omitir ações sem destino; o álbum continua consultável e elegível ao sorteio.
- CA-12.4: com link externo indisponível, continuar permitindo consultar o álbum e editar a URL; não prometer detectar disponibilidade antecipadamente.
- CA-12.5: localizar álbum conhecido com link e abri-lo em até três interações a partir da biblioteca, conforme RNF-05/P-08.

### RF-13 — Sortear toda a biblioteca (E)

**Entrada:** solicitação de sorteio global. **Saída:** um álbum da coleção, com acesso aos seus detalhes/links quando existentes.

**Comportamento:** cada registro tem probabilidade 1/N para N álbuns elegíveis. Colaborações não recebem peso adicional. Sorteios consecutivos podem repetir resultados. Não aplicar filtros de escuta, ano, capa ou links.

**Aceitação:**

- CA-13.1: com conjunto conhecido, toda saída pertence ao conjunto de álbuns persistidos.
- CA-13.2: com um único álbum, todas as execuções retornam esse álbum.
- CA-13.3: verificar por inspeção do método de seleção que há uma participação por registro e probabilidades iguais; amostra estatística isolada não comprova uniformidade.
- CA-13.4: verificar que o método não exclui o último resultado; repetição é permitida, sem exigir que aconteça em uma amostra específica.
- CA-13.5: com APIs indisponíveis, obter resultado normalmente, respeitando o desempenho local.

### RF-14 — Sortear por artista (E)

**Entrada:** artista escolhido. **Saída:** um álbum associado a esse artista ou aviso de conjunto vazio.

**Comportamento:** probabilidade 1/N entre os N álbuns do artista, incluindo colaborações uma única vez. Sorteio global e por artista são opções distintas; não se deduz sorteio dos resultados da pesquisa.

**Aceitação:**

- CA-14.1: com álbuns de A, B e colaboração A/B, sortear por A; retornar somente álbum de A ou colaboração A/B.
- CA-14.2: verificar que a colaboração participa uma vez, com a mesma chance dos demais álbuns de A.
- CA-14.3: com um único álbum associado, retornar esse álbum.
- CA-14.4: com artista inexistente, informar registro não encontrado; com artista válido sem álbuns, explicar ausência de elegíveis sem retornar outro artista.

### RF-15 — Tratar conjunto vazio (E/D)

**Entrada:** tentativa de sortear coleção vazia ou conjunto de artista sem álbuns. **Saída:** explicação e orientação adequada.

**Aceitação:**

- CA-15.1: na biblioteca vazia, explicar que é necessário cadastrar um álbum antes de sortear e permitir chegar ao cadastro.
- CA-15.2: no conjunto vazio de um artista, informar que não há álbuns desse artista para sortear; não informar incorretamente que toda a biblioteca está vazia.
- CA-15.3: em ambos os casos, não gerar erro interno nem escolher álbum fora do conjunto solicitado.

### RF-16 — Persistir, documentar backup e restaurar (E)

**Entrada:** dados confirmados, reinício da aplicação e execução das instruções de backup/restauração. **Saída:** coleção íntegra e recuperável.

**Comportamento:** documentar como criar uma cópia consistente do SQLite, onde guardá-la e como restaurá-la. Informar quais arquivos são necessários além do banco, se houver. Backups não exigem botão na interface, agendamento nem nuvem. Frequência e retenção não estão definidas (P-09).

**Aceitação:**

- CA-16.1: salvar álbuns, artistas, edição e links; reiniciar e verificar todos os valores e associações.
- CA-16.2: criar cópia seguindo as instruções; restaurar em ambiente local de teste separado e verificar contagens, títulos, artistas, vínculos, edições e URLs.
- CA-16.3: verificar consulta e sorteio da coleção restaurada com APIs indisponíveis.
- CA-16.4: testar cópia ausente, inválida ou incompatível; informar falha e preservar a biblioteca atual antes de qualquer substituição destrutiva (T).
- CA-16.5: se a capa for apenas referência externa, a documentação explica que backup preserva a referência e que a imagem pode ficar indisponível.

## 4. Regras de negócio

| ID | Regra | Origem / verificação |
| --- | --- | --- |
| RN-01 | A coleção não distingue álbuns ouvidos, pendentes ou adquiridos. | E / RF-01, RF-13. |
| RN-02 | Título e pelo menos um artista são obrigatórios; ano, capa e links são opcionais. | E / CA-01.1–2. |
| RN-03 | Colaboração associa um único álbum a múltiplos artistas. | E / CA-06.2. |
| RN-04 | Há um registro por álbum e uma edição escolhida pelo usuário. | E/U / RF-03, RF-09, RF-10; P-01 para identidade ambígua. |
| RN-05 | Mesmo título e conjunto de artistas geram aviso de possível duplicado e revisão humana. | E / RF-10; normalização pendente. |
| RN-06 | Não combinar registros nem escolher edição automaticamente. | E / CA-03.4, CA-10.3–4. |
| RN-07 | Troca de edição exige revisão e preserva links de streaming. | U / CA-09.1–4. |
| RN-08 | Toda a biblioteca ou os álbuns de um artista são os conjuntos disponíveis para sorteio. | E / RF-13–14. |
| RN-09 | Todos os álbuns elegíveis têm a mesma chance; repetições consecutivas são válidas. | E / CA-13.3–4, CA-14.2. |
| RN-10 | Ausência de capa, ano ou links não exclui álbum do sorteio. | E/D / RF-13–14. |
| RN-11 | Remoção exige confirmação. | E / RF-11. |
| RN-12 | Links são informados manualmente e abrem destinos externos; reprodução não é garantida. | E / RF-12. |
| RN-13 | Dados revisados e salvos sustentam consulta e sorteio sem disponibilidade das APIs. | E / CA-03.5, CA-13.5. |

## 5. Requisitos não funcionais

| ID | Requisito | Origem | Critério verificável |
| --- | --- | --- | --- |
| RNF-01 | Execução local com Django, SQLite e templates HTML/CSS, com acesso pelo PC e pelo celular na mesma rede local configurada. | E/D | Iniciar em ambiente local, verificar persistência SQLite e páginas renderizadas pela aplicação; seguir a documentação de acesso de rede e abrir pelo celular a mesma biblioteca do PC, com o servidor em execução. |
| RNF-02 | Interface responsiva e funcionalidades equivalentes em PC e dispositivos móveis, com mouse/teclado e toque. | E/U/D | Nos navegadores e viewports de PC e celular acordados em P-08, concluir cadastro manual e por busca, revisão/troca de edição, edição, remoção com confirmação, navegação por biblioteca/artista/detalhes, pesquisa, abertura de streaming e sorteio global/por artista. Verificar também erros e estados vazios, sem rolagem horizontal da página, conteúdo cortado ou controles essenciais inacessíveis; nenhuma ação pode depender apenas de hover. |
| RNF-03 | Independência dos catálogos para leitura e sorteio. | E | Bloquear APIs externas e executar RF-05–07, RF-13–15 com dados já salvos; permitir imagem padrão. Links externos continuam dependentes de internet. |
| RNF-04 | Listagem, pesquisa local e sorteio em até 2 segundos com 1.000 álbuns, excluindo consultas externas. | E | Medir cada operação no ambiente e protocolo definidos em P-08; guardar tempos observados e dataset. Não declarar cumprimento antes de definir medição. |
| RNF-05 | Cadastro manual básico em até 1 minuto; localizar álbum conhecido e abrir streaming em até 3 interações desde a biblioteca. | E | Executar teste de uso com álbum básico e álbum conhecido contendo link; registrar duração e interações segundo P-08. |
| RNF-06 | Integridade de gravações. | D/T | Falha durante cadastro, edição, troca de edição ou remoção não deixa álbum parcialmente gravado, associação órfã ou links parcialmente alterados; verificar com falha controlada. |
| RNF-07 | Erros compreensíveis e preservação dos dados digitados quando possível. | D/T | Em validação inválida ou falha externa, indicar correção/alternativa sem afirmar sucesso; conferir manutenção dos campos preenchidos. |
| RNF-08 | Acesso básico por teclado e rótulos claros. | T | Navegar controles essenciais com teclado, perceber foco e identificar campos e erros; imagens possuem alternativa textual adequada. Não implica certificação de acessibilidade. |
| RNF-09 | Diagnóstico sem expor informações internas na interface. | T | Registrar categoria de falha técnica; usuário recebe mensagem sem traceback, segredo ou caminho interno. |
| RNF-10 | Backup e restauração reproduzíveis. | E | Uma pessoa consegue seguir a documentação e executar CA-16.2 sem conhecimento não documentado. |

## 6. Integrações e desempenho externo

### INT-01 — MusicBrainz (E/T)

- Controlar consultas no servidor e reaproveitar consultas recentes. O limite do escopo é, em média, uma requisição por segundo.
- A [documentação oficial de limites do MusicBrainz](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting), consultada em 13/10/2026, informa limite médio por IP e rejeição com HTTP 503 quando excedido; também exige User-Agent que identifique a aplicação e permita contato com o responsável.
- O controle deve abranger todas as chamadas do aplicativo ao MusicBrainz, incluindo pesquisa e obtenção de detalhes; cliques concorrentes não podem multiplicar a taxa permitida (D/T).
- Timeout finito, cache, eventual retry e limites de tamanho da resposta devem ser configurados. Seus valores estão pendentes em P-06. Não criar repetição ilimitada nem disparar novamente em laço após falha (T).
- Não interpretar HTTP 503 como ausência de resultados. Uma falha global do serviço também pode produzir esse status.

**Verificação:** inspecionar requisições e User-Agent; executar consultas concorrentes e observar controle de frequência; simular 503 e resposta inválida; verificar estado de falha e opção manual; repetir consulta dentro da validade do cache e verificar ausência de nova chamada.

### INT-02 — Cover Art Archive (E)

Consultar quando houver identificação compatível; tratar capa como enriquecimento opcional. Sua indisponibilidade não deve impedir nenhuma operação essencial da coleção. O limite do MusicBrainz não deve ser atribuído automaticamente ao Cover Art Archive. Identificação compatível, estratégia de obtenção, limites específicos e retenção de capas dependem de P-01/P-06/P-07.

**Verificação:** simular capa encontrada, não encontrada, timeout e resposta inválida; verificar capa ou alternativa visual e ausência de bloqueio do cadastro.

## 7. Segurança aplicável ao MVP local

As medidas abaixo são propostas técnicas T, sem ampliar o produto para autenticação ou múltiplos usuários. O uso local pressupõe proteção pelo sistema operacional e, quando habilitado acesso pelo celular, uma rede local confiável; ele não oferece separação de usuários dentro do aplicativo.

| ID | Requisito técnico | Critério verificável |
| --- | --- | --- |
| SEG-01 | Configuração padrão de execução restrita ao loopback; oferecer configuração explícita e documentada para acesso por dispositivos na mesma rede local confiável. | Verificar endereço de escuta, hosts permitidos e instruções de acesso pelo celular; com a configuração habilitada, acessar a mesma biblioteca pelo PC e pelo celular. Documentar que outros dispositivos com acesso ao servidor nessa rede poderão acessar a biblioteca, pois não há autenticação no MVP. Não configurar exposição à internet; publicação requer a etapa futura prevista no escopo. |
| SEG-02 | Operações persistentes devem usar método de escrita e proteção CSRF do Django; abrir URL de leitura não pode remover ou editar dados. | Requisição de escrita sem token válido é rejeitada; acesso por GET a confirmação não remove álbum. |
| SEG-03 | Validar entradas no servidor, incluindo dados externos; escapar textos nos templates e usar acesso parametrizado ao banco. | Conteúdo HTML/script em título, artista e plataforma é exibido como texto; entrada maliciosa não altera consultas nem execução da página. |
| SEG-04 | Aceitar URLs HTTP/HTTPS e rejeitar protocolos executáveis ou locais, como javascript:, data: e file:, nos links e capas. | Submeter URLs proibidas diretamente ao servidor e verificar erro sem persistência. Regras adicionais de domínio/tamanho: P-04. |
| SEG-05 | Requisições externas do servidor usam destinos conhecidos das integrações; URL manual de capa não deve ser buscada pelo servidor sem proteção contra SSRF. | Tentar URL local/privada e redirecionamento para destino privado; não permitir acesso do servidor a arquivos, loopback, rede privada ou serviços de metadados. Se a imagem for carregada no navegador, verificar que não houve fetch no servidor. |
| SEG-06 | Verificar TLS em conexões HTTPS do servidor; não desativar validação para contornar falhas. | Certificado inválido produz falha controlada e não consulta insegura. |
| SEG-07 | Abrir links externos sem permitir acesso indevido à janela de origem, quando usada nova aba. | Verificar proteção de opener nas ações externas que abrem nova aba. |
| SEG-08 | Não expor segredos, banco local, backups, dados de configuração ou traceback nas páginas. | Verificar respostas de erro e ausência de banco/backups em diretórios servidos como arquivos públicos. |
| SEG-09 | Documentar proteção de arquivos de biblioteca e backup pelo sistema operacional. | Instruções identificam arquivos sensíveis, acesso local e local de armazenamento; não exigem nuvem nem serviço externo. |
| SEG-10 | Definir limites de campos, resposta externa e espera para evitar consumo ilimitado de recursos. | Entradas acima dos limites acordados e respostas excessivas geram falha controlada; números dependem de P-04/P-06. |

Capas carregadas por URL e links de streaming dependem de terceiros. A estratégia escolhida para imagens deve ser documentada, inclusive eventual envio de requisições do navegador ao provedor. Não se exige proxy de imagens, varredura de links, criptografia de backup nem autenticação no MVP local.

## 8. Tratamento de erros e validações

| Situação | Resposta esperada | Estado que deve ser preservado | Verificação |
| --- | --- | --- | --- |
| Título vazio, artistas ausentes ou item de link incompleto | Erro junto ao campo, com instrução de correção. | Nenhuma gravação parcial; valores válidos preenchidos quando possível. | RF-01, RF-08, RNF-06–07. |
| Ano ou URL inválidos | Recusar valor e identificar campo; regras de ano dependem de P-03. | Registro anterior na edição. | Seção 2, SEG-04. |
| Possível duplicado | Aviso e acesso à revisão do existente; nenhuma fusão automática. | Registro existente e escolha do usuário. | RF-10. |
| MusicBrainz sem resultados | Explicar que a busca terminou sem encontrar resultados; permitir cadastro manual. | Coleção e dados do formulário. | CA-02.2. |
| Timeout, falha de rede, 503 ou outro erro de catálogo | Indicar indisponibilidade/consulta não concluída, permitir nova tentativa controlada e cadastro manual. | Coleção existente. | CA-02.3, INT-01. |
| Resposta externa malformada ou incompleta | Não confiar na estrutura recebida; informar falha ou exigir preenchimento na revisão, conforme o caso. | Nenhum registro inválido persistido. | CA-03.3, SEG-03. |
| Capa ausente ou imagem quebrada | Imagem padrão; título e demais ações acessíveis. | Cadastro e elegibilidade ao sorteio. | RF-04. |
| Link ausente | Sem ação de abertura com destino vazio. | Álbum consultável e sorteável. | CA-12.3. |
| Streaming fora do ar ou edição incorreta no destino | Permitir correção do link; a aplicação não garante detectar falha de terceiros. | Dados locais. | CA-12.4. |
| Álbum/artista inexistente ou removido | Estado de registro não encontrado e navegação de retorno. | Demais registros. | CA-05.4, CA-11.4, CA-14.4. |
| Biblioteca/conjunto vazio | Orientação contextual, sem erro interno ou resultado fora do conjunto. | Coleção atual. | RF-15. |
| Falha de persistência, banco bloqueado ou armazenamento sem espaço | Informar que não foi possível concluir; não mostrar sucesso antes da confirmação de gravação. | Estado anterior íntegro. | RNF-06–07. |
| Clique duplo/reenvio ou duas gravações concorrentes | Aplicar validação de duplicado também na gravação; evitar estado parcial. | Regra de um registro por álbum. | RF-10, RNF-06; equivalência depende de P-01/P-02. |
| Backup inválido ou restauração interrompida | Informar falha; procedimento deve preservar cópia recuperável da biblioteca anterior. | Dados atuais ou cópia consistente para recuperação. | CA-16.4. |

Não exigir código HTTP específico para erros de formulário sem escolher o fluxo técnico. Rejeições de segurança e registros não encontrados precisam ser distinguíveis de sucesso e de erro interno nos testes.

## 9. Casos extremos e cobertura

| Caso | Resultado esperado / pendência |
| --- | --- |
| Zero álbuns | Biblioteca vazia compreensível; sorteio orienta cadastrar. |
| Um álbum, inclusive sem ano/capa/links | Sempre retorna esse álbum no conjunto elegível. |
| Colaboração com múltiplos artistas | Um registro, visível para cada artista e contado uma vez em cada sorteio. |
| Título igual com artistas distintos | Não classificar como mesmo álbum somente pelo título. |
| Mesmo título/artistas com diferentes edições | Usuário revisa e escolhe a edição no registro único; títulos homônimos realmente distintos: P-01. |
| Artistas em ordem diferente | Mesmo conjunto para aviso de duplicado. |
| Nomes com acentos, caixa diferente, espaços extras ou nomes homônimos | Exibição preservada; equivalência para busca/identidade ainda pendente em P-02/P-05. |
| Mesmo artista informado duas vezes | Não ampliar peso do álbum nem duplicar linha; escolha entre deduplicar ou rejeitar o campo: P-02. |
| Dados externos faltantes | Revisão permite completar; não salvar sem obrigatórios. |
| Troca de edição com capa diferente/ausente | Revisão antes da gravação; links preservados; precedência de capa manual: P-07. |
| Exclusão do último álbum de um artista | Nenhum álbum elegível; visibilidade/remoção do artista: P-02. |
| Exclusão de álbum entre listagem e abertura | Registro não encontrado, sem falha interna. |
| Alteração da coleção durante sorteio | Resultado deve corresponder a conjunto local consistente no instante de seleção (T); remoção posterior pode produzir registro não encontrado. |
| Sorteios repetidos | Permitidos; não criar histórico nem exclusão do último resultado. |
| 1.000 álbuns, com colaborações | Cumprir meta local sem duplicar linhas ou pesos; distribuição do dataset: P-08. |
| Consulta excessivamente longa ou imagem/resposta externa muito grande | Limites controlados conforme SEG-10; valores: P-04/P-06. |
| APIs indisponíveis após reinício/restauração | Dados locais disponíveis; capa padrão se necessário. |
| URL válida que não aponta para imagem | Alternativa visual, sem impedir leitura do álbum. |
| Biblioteca recuperada por backup com URLs expiradas | Metadados, associações e sorteio funcionam; imagens/streaming não são garantidos. |
| Tela estreita, orientação retrato/paisagem e interação por toque | Conteúdo legível e controles utilizáveis, sem ações exclusivas de hover; navegadores e viewports de teste: P-08. |
| Celular sem acesso à rede local ou servidor desligado | A aplicação local não fica disponível; a documentação de acesso explica essas condições. |

## 10. Contradições potenciais, ambiguidades e lacunas

Não foi identificada contradição direta incontornável. Há tensões e pontos incompletos que impedem fechar alguns critérios. Os esclarecimentos DEC-01–05 resolveram a escolha de edição, possibilidade de troca, revisão/preservação de links, forma de informar capa manual e necessidade de acesso por PC e dispositivos móveis.

| ID | Tipo | Questão ainda aberta e impacto | Pergunta para decisão |
| --- | --- | --- | --- |
| P-01 | Ambiguidade / tensão | “Um registro por álbum” e igualdade por título/artistas não definem como distinguir dois álbuns realmente diferentes com esses mesmos valores. MusicBrainz pode apresentar obras e edições distintas. | Se forem álbuns diferentes com título e artistas idênticos, qual informação deve distingui-los? Quais dados da edição precisam aparecer para apoiar a escolha: data, país, formato, gravadora ou outros? |
| P-02 | Incompleto | Não há regra de identidade de artistas, normalização de possíveis duplicados, artista repetido ou artista sem álbuns. | Diferenças de caixa, acentos e espaços devem ser equivalentes? Como distinguir artistas homônimos? Artistas sem álbuns devem sumir da lista? Artista repetido no formulário deve ser removido automaticamente ou causar erro? |
| P-03 | Vago | “Ano” não define referência, formato ou intervalo. | O ano é o da edição escolhida ou do lançamento original do álbum? Anos futuros e datas parciais são aceitos? |
| P-04 | Incompleto | Limites de campos/links e validade específica do campo Spotify não estão definidos. | Há limites desejados? O campo Spotify deve aceitar apenas URLs de spotify.com? Links de uma mesma plataforma podem aparecer várias vezes? Os limites técnicos poderão ser propostos para aprovação antes da implementação. |
| P-05 | Vago | Pesquisa não define correspondência, campos externos, ordenação, paginação ou tratamento de consulta vazia. | Busca local deve aceitar parte do título/artista e ignorar caixa/acentos? Consulta vazia mostra toda a biblioteca? Quais campos de pesquisa externa e ordenações são necessários? |
| P-06 | Incompleto técnico | Não foram definidos validade/tamanho do cache, timeout, retries, tamanho máximo de resposta nem limites do Cover Art Archive. | Autoriza definir esses valores como configuração técnica documentada, respeitando os fornecedores e mantendo fallback manual? O contato para User-Agent também precisa ser informado antes das chamadas reais. |
| P-07 | Incompleto | Capa manual versus automática, retenção local e efeito da troca de edição sobre uma capa manual. | Capa manual tem prioridade sobre a automática? Na troca de edição, deve ser preservada como opção na revisão? É necessário guardar as imagens localmente ou basta referência com imagem padrão quando offline? |
| P-08 | Critério incompleto | Metas de tempo/interações sem hardware, navegador, dataset, rede, cache, repetições, início/fim ou contagem de interação. PC e dispositivos móveis definidos como contextos obrigatórios, mas sem navegadores e viewports de teste definidos. | Qual ambiente será usado? Como contar digitação/cliques e medir carregamento? Quais navegadores e viewports de PC e celular validar, incluindo retrato e paisagem no celular? Essas definições devem ser registradas antes de declarar as metas cumpridas. |
| P-09 | Incompleto operacional | Backup sem frequência, retenção ou preferência de destino. | Basta procedimento manual documentado, executado pelo usuário, ou existe rotina desejada? Agendamento automático não está no escopo atual. |

**Tensões a observar:**

- Revisão de “possível duplicado” não prova identidade de um álbum; bloqueio absoluto por título/artistas pode impedir um caso legítimo de homônimo. P-01 deve resolver isso sem introduzir múltiplas edições do mesmo álbum.
- A independência das APIs vale para metadados e sorteio; não promete streaming ou imagens remotas offline. Guardar imagens locais seria uma decisão adicional de retenção, ainda pendente.
- Meta de dois segundos não inclui consultas externas. O controle de taxa pode impor espera em pesquisas externas e não contradiz essa meta.
- Uso pessoal não torna seguro publicar sem autenticação. Publicação continua condicionada às decisões e alterações previstas no escopo.

## 11. Rastreabilidade e condição para aprovação

| Item do escopo | Requisitos principais |
| --- | --- |
| Cadastro manual e por busca | RF-01–03, INT-01. |
| Campos obrigatórios/opcionais e colaboração | Seção 2, RF-01, RF-06, RN-02–03. |
| Capas e imagem padrão | RF-04, INT-02, P-07. |
| Edição, remoção e revisão de duplicado | RF-08–11, RN-04–07, RN-11. |
| Biblioteca, artista, detalhes e pesquisa | RF-05–07. |
| Spotify e links adicionais | RF-12, SEG-04/07. |
| Sorteio uniforme global/por artista e vazio | RF-13–15, RN-08–10. |
| Execução local, tecnologias e consultas no servidor | RNF-01, RF-02, INT-01–02. |
| Acesso por PC e dispositivos móveis, interface responsiva e rede local | DEC-05, RNF-01–02, SEG-01, P-08. |
| Independência externa e persistência | RF-03, RF-16, RNF-03/06. |
| Cache e frequência MusicBrainz | RF-02, INT-01, P-06. |
| Backup e restauração | RF-16, RNF-10, SEG-08–09. |
| Metas de uso e desempenho | RNF-02/04/05, P-08. |
| Segurança aplicável | Seção 7; publicação fora do MVP. |

A aprovação deve indicar se aceita as propostas T e resolver ou adiar explicitamente as pendências P-01–09, com seus impactos. Adiar não autoriza implementar uma alternativa silenciosamente. Os critérios bloqueados por uma pendência continuam incompletos até sua definição; os demais podem ser avaliados como descritos.

Este documento não constitui implementação, plano de publicação nem autorização para iniciar código. A próxima etapa aguarda aprovação do usuário.
