# Especificação de requisitos — biblioteca pessoal de álbuns

**Data:** 14/10/2026<br>
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
| DEC-06 | U | Álbuns distintos com título e artistas equivalentes são diferenciados pela data do lançamento original; datas de edições posteriores não criam novos álbuns. Precisão insuficiente ou datas coincidentes permanecem em P-01/P-03. |
| DEC-07 | U/D | Comparações de nomes e títulos ignoram caixa, acentos e espaços conforme a seção 2.1; a grafia original é preservada para exibição. Equivalência textual não comprova identidade de artistas homônimos. |
| DEC-08 | U | A lista de artistas inclui somente artistas com pelo menos um álbum associado. Retenção ou exclusão dos registros sem álbuns permanece em P-02. |
| DEC-09 | U | O ano principal é o do lançamento original, não o da edição escolhida. Armazenar separadamente o ano/data da edição é uma proposta, pendente em P-03. |
| DEC-10 | U | Anos de lançamento posteriores ao ano corrente não são aceitos, seja em entrada manual ou externa. Restrições a mês/dia futuros dentro do ano corrente permanecem em P-03. |
| DEC-11 | U | Uma capa manual definida tem prioridade sobre a automática, inclusive na revisão de troca de edição. Falha de carregamento não autoriza sobrescrever a escolha manual. |

## 2. Dados, entradas, saídas e restrições

Este é um modelo conceitual, não uma decisão sobre tabelas ou detalhes de implementação.

| Entidade/campo | Entrada esperada | Saída/uso esperado | Obrigatoriedade e validação |
| --- | --- | --- | --- |
| Álbum: identificador local | Gerado pelo aplicativo | Referência estável para detalhe, edição, remoção e sorteio | Obrigatório internamente; não depende da API externa (D). |
| Título | Texto manual ou sugerido pelo MusicBrainz | Listagens, detalhes, busca e aviso de duplicado | Obrigatório (E); rejeitar valor vazio ou composto somente por espaços (D). Limite de tamanho: P-04. |
| Artistas do álbum | Um ou mais artistas selecionados/informados | Associação do mesmo álbum às páginas dos artistas e à busca | Pelo menos um obrigatório (E); nomes não podem ser vazios (D). Comparação textual: seção 2.1; identidade de homônimos: P-02. |
| Ano principal / data do lançamento original | Valor manual ou sugestão externa identificada como lançamento original | Exibição do ano principal e diferenciação de álbuns homônimos | Opcional (E); ano não posterior ao corrente (U). Não inferir o original a partir da data de uma reedição, nem converter ausência em zero (D). Precisão, formato e limite inferior: P-03; ambiguidade: P-01. |
| Ano/data da edição escolhida (proposta T/P-03) | Valor manual ou data da edição externa selecionada | Contextualizar a edição e apoiar sua revisão, sem alterar a identidade do álbum | Armazenamento separado e opcional recomendado, ainda não aprovado; se adotado, sujeito à mesma proibição de ano futuro. Não substitui a data original. |
| Edição externa | Resultado escolhido do MusicBrainz e identificação compatível | Proveniência e consulta de capa; troca de edição | Opcional no cadastro manual (D); não associar automaticamente uma edição a partir apenas de título/artista (E/D). |
| Capa | Resultado do Cover Art Archive ou URL manual | Imagem do álbum ou imagem padrão | Opcional (E/U); URL HTTP/HTTPS válida como proposta T; manual tem prioridade sobre automática (U); ausência ou falha da imagem exige alternativa visual conforme RF-04. |
| Spotify | URL preenchida manualmente | Ação para abrir o destino externo | Opcional (E); protocolo seguro: T; restrição ao domínio Spotify: P-04. |
| Links adicionais | Pares de nome da plataforma e URL | Ações externas identificadas pelo nome | O conjunto pode ser vazio (E); cada item informado exige nome e URL completos (D). Quantidade e nomes repetidos: P-04. |
| Consulta à coleção | Texto de título ou artista | Álbuns locais correspondentes, ou estado sem resultados | Não altera registros; normalização: seção 2.1; tipo de correspondência e consulta vazia: P-05. |
| Consulta ao MusicBrainz | Texto para pesquisa | Resultados de catálogo ou estado sem resultados/falha | Dados externos são sugestões; seleção e revisão precedem persistência (E). Campos e paginação: P-05. |
| Sorteio | Toda a biblioteca ou um artista | Um álbum elegível ou explicação de conjunto vazio | Não depende de ano, capa, links ou estado de escuta (E/D). |
| Confirmação de remoção | Álbum alvo e confirmação explícita | Registro removido ou operação cancelada | Cancelamento conserva o registro e suas associações (E/D). |
| Backup/restauração | Biblioteca local e cópia válida | Cópia recuperável e coleção restaurada | Procedimento documentado e verificado (E); armazenamento de capas deve ser contemplado (D). |

Nomes e títulos com caracteres Unicode e pontuação devem ser preservados na apresentação (U). Limites de campos não podem ser definidos silenciosamente durante a implementação. Dados externos passam pelas mesmas validações de persistência dos dados manuais (D).

### 2.1 Comparação de nomes e títulos (U/D)

Para comparar títulos e nomes de artistas na coleção local, produzir uma chave separada do texto de exibição: decompor Unicode em NFD, aplicar case folding Unicode (comparação sem distinção de caixa), decompor novamente em NFD, remover marcas combinantes de acentuação e remover todos os caracteres de espaço em branco Unicode, inclusive tabulações e quebras de linha. Assim, `ÁGUA`, `agua` e ` A gua ` são equivalentes. Pontuação e demais caracteres não são removidos; não há transliteração nem equivalência automática entre apelidos, traduções ou nomes artísticos diferentes.

A remoção de espaços vale também entre palavras: `A B` e `AB` têm a mesma chave. Colisões de normalização exigem revisão; não autorizam fundir artistas ou álbuns. O valor informado/revisado permanece separado para exibição, sem ser substituído pela chave. Um valor cuja chave fique vazia é inválido. A mesma normalização vale para a consulta local e seus campos comparados; correspondência parcial, consulta vazia e ordenação continuam em P-05. A forma de consultar o catálogo externo não é determinada por essa chave.

### 2.2 Lançamento original, edição e identificação (U/D)

O álbum conceitual mantém um identificador local e uma edição escolhida. A data usada para diferenciar álbuns distintos com título e artistas equivalentes é a do **lançamento original de cada álbum**, não a data de cada edição. Um álbum originalmente lançado em 1990 e sua reedição de 2020 continuam sendo um álbum; outro álbum de mesmo título e artistas, originalmente lançado em 2005, pode ter registro próprio. Trocar a edição não altera por si só a data original nem cria um registro.

Comparar títulos pela seção 2.1 e conjuntos de identidades de artistas sem considerar a ordem. Nomes equivalentes ajudam a localizar candidatos, mas a distinção de artistas homônimos depende de P-02. Comprovado que se trata de álbuns distintos, datas originais diferentes permitem distingui-los; diferença na data de edição não basta. Mesma data original também não prova que se trata do mesmo álbum.

Ano/data original continua opcional: ausência ou precisão insuficiente não pode ser preenchida com uma data inventada ou com a data da edição. Nesses casos, o aviso de possível duplicado e a revisão continuam aplicáveis; a resolução da ambiguidade entre homônimos depende de P-01/P-03. Não estabelecer unicidade rígida apenas por nome/título/data antes dessas definições.

### 2.3 Validação temporal já definida (U/D)

Qualquer ano de lançamento informado deve ser um ano inteiro, não posterior ao ano corrente na data da gravação, segundo a data local configurada da aplicação. A regra se aplica ao lançamento original e, se aprovado seu armazenamento, à edição escolhida, no cadastro, edição e troca de edição, inclusive para sugestões externas. Um ano futuro exige correção ou remoção do campo opcional antes de salvar; não deve ser aceito silenciosamente. Ausência é distinta de zero. Formato de entrada, limite inferior, suporte a mês/dia e rejeição de datas futuras dentro do ano corrente dependem de P-03.

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
- CA-01.6: tentar salvar ano posterior ao corrente, manualmente ou por sugestão externa; recusar o valor e permitir corrigi-lo ou deixar o campo opcional ausente, sem gravação parcial.

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

**Comportamento:** não escolher nem combinar edições automaticamente. Exibir os dados disponíveis para revisão; permitir correção manual. Informação externa incompleta não elimina a validação de título/artistas ou de anos informados. Distinguir a data original da data da edição; se o original for desconhecido, mantê-lo ausente em vez de copiar a data da reedição. A apresentação deve permitir distinguir as edições com os dados que o catálogo fornecer (D); conjunto exato de campos depende de P-01.

**Aceitação:**

- CA-03.1: selecionar resultado; abrir revisão antes de persistir; alterar título e salvar, verificando o valor revisado.
- CA-03.2: cancelar revisão; confirmar que nenhum álbum foi criado.
- CA-03.3: selecionar edição sem título ou artistas completos; exigir correção antes do salvamento.
- CA-03.4: selecionar uma entre duas edições distintas; verificar que a identificação persistida corresponde à escolha do usuário.
- CA-03.5: após salvar e tornar as APIs indisponíveis, consultar e sortear o álbum com os dados persistidos.

### RF-04 — Obter, informar e exibir capa (E/U/T)

**Entrada:** identificação externa compatível ou URL manual opcional. **Saída:** capa disponível ou imagem padrão.

**Comportamento:** consultar o Cover Art Archive quando houver identificação compatível. Falha ou ausência de capa não impede salvar nem consultar o álbum. Permitir informar, substituir ou remover a URL manual. Quando houver capa manual definida, ela tem prioridade sobre a automática e não é sobrescrita por novas consultas ou troca de edição. Sem manual, usar automática disponível; sem ambas, imagem padrão. Se a manual falhar, exibir imagem padrão sem remover a URL nem substituí-la silenciosamente pela automática. Remover explicitamente a manual permite voltar à automática ou, na ausência desta, à padrão. Retenção das imagens permanece em P-07.

**Aceitação:**

- CA-04.1: sem capa manual definida e com identificação compatível e capa disponível, exibir a capa retornada.
- CA-04.2: sem nenhuma capa utilizável segundo a precedência definida, ou com URL manual quebrada, exibir imagem padrão e manter os demais dados e ações disponíveis; falha da consulta automática não impede exibir uma manual válida.
- CA-04.3: informar uma URL válida de imagem no cadastro manual; salvar e exibir a imagem; remover o valor e verificar a alternativa aplicável.
- CA-04.4: não bloquear persistência por indisponibilidade da capa.
- CA-04.5: falha de carregamento da imagem padrão não provoca um ciclo de tentativas nem impede leitura do título/artistas (T).
- CA-04.6: com capas manual e automática, exibir a manual; uma nova obtenção automática ou troca de edição conserva essa prioridade. Se a manual quebrar, exibir a padrão e conservar a URL manual; removê-la explicitamente reativa a automática disponível.

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

**Comportamento:** um álbum colaborativo pertence a cada artista associado, mantendo um único registro. Listar somente artistas com pelo menos um álbum associado, inclusive após edição ou remoção do último vínculo. Aplicar a normalização da seção 2.1; homônimos e retenção/exclusão de registros sem álbuns permanecem em P-02. A ausência na lista não implica exclusão física; acessos diretos e sorteios devem continuar tratando conjunto vazio ou identificador inexistente conforme RF-14–15.

**Aceitação:**

- CA-06.1: cadastrar álbuns de artistas diferentes; abrir cada artista e verificar que aparecem apenas seus álbuns.
- CA-06.2: cadastrar colaboração entre A e B; verificar o mesmo identificador local nas páginas de A e B, sem duplicação na biblioteca.
- CA-06.3: retirar B do álbum por edição; o álbum deixa de aparecer na página de B e permanece na de A. Se esse era o último vínculo de B, B deixa de aparecer na lista de artistas.
- CA-06.4: remover o último álbum associado a um artista; esse artista não aparece na lista. Os artistas que ainda têm álbuns permanecem visíveis.

### RF-07 — Pesquisar a coleção local (E)

**Entrada:** texto de título ou artista. **Saída:** álbuns correspondentes ou aviso de ausência de resultados.

**Comportamento:** pesquisar dados persistidos sem depender de catálogos. Um álbum associado a vários artistas deve aparecer uma única vez no resultado (D). Normalizar consulta, nomes e títulos conforme seção 2.1. Tipo de correspondência e demais detalhes dependem de P-05.

**Aceitação:**

- CA-07.1: pesquisar o título completo de um álbum conhecido e encontrar seu registro.
- CA-07.2: pesquisar o nome completo de um artista e encontrar seus álbuns, inclusive colaborações.
- CA-07.3: usar termo que não corresponda a registros; apresentar resultado vazio, sem alterar a coleção.
- CA-07.4: executar os casos anteriores com APIs externas indisponíveis e obter os mesmos registros.
- CA-07.5: verificar ausência de linhas duplicadas quando mais de uma associação satisfizer a busca.
- CA-07.6: pesquisar título e artista variando caixa, acentos e espaços; obter os mesmos registros, preservando a grafia original na exibição. Se houver homônimos, a busca pode retornar álbuns de ambos sem fundir suas identidades.

### RF-08 — Editar informações (E)

**Entrada:** registro existente e valores revisados. **Saída:** mesmo registro atualizado ou erros de validação.

**Comportamento:** permitir editar título, artistas, ano, capa e links. Validar os campos como no cadastro. Cancelar não altera o registro. Colisão com outro álbum exige o mesmo fluxo de revisão de RF-10 (D).

**Aceitação:**

- CA-08.1: alterar dados obrigatórios e opcionais; verificar novos valores na biblioteca, detalhes, busca e páginas dos artistas.
- CA-08.2: remover todos os artistas ou tornar título vazio; recusar alteração e conservar o estado anterior.
- CA-08.3: cancelar edição; verificar que os dados persistidos permanecem iguais.
- CA-08.4: editar para uma combinação de título/artistas já existente; aplicar RF-10 considerando a data original, sem combinar automaticamente registros.

### RF-09 — Trocar a edição do MusicBrainz (U)

**Entrada:** álbum existente, nova edição escolhida e dados revisados. **Saída:** mesmo registro local associado à nova edição.

**Comportamento:** possibilitar busca/seleção de outra edição e revisão dos valores de título, artistas, data original e capa antes de salvar; se aprovado em P-03, revisar separadamente a data da edição. Não substituir o ano original pelo da nova edição. Conservar a capa manual enquanto o usuário não a substituir ou remover explicitamente. Preservar os links de streaming existentes durante essa troca. A troca não cria um segundo registro do mesmo álbum nem sobrescreve silenciosamente dados revisados.

**Aceitação:**

- CA-09.1: escolher nova edição; antes de confirmar, verificar que a biblioteca conserva os dados anteriores.
- CA-09.2: revisar os valores propostos e salvar; verificar o mesmo identificador local, a nova edição e os valores confirmados.
- CA-09.3: confirmar que Spotify e todos os links adicionais anteriores permanecem iguais após a troca.
- CA-09.4: cancelar ou provocar falha de obtenção da nova edição; verificar preservação integral do registro anterior.
- CA-09.5: trocar por edição cuja combinação título/artistas gere candidato a duplicado; aplicar RF-10 considerando a data original, sem alteração automática.
- CA-09.6: trocar uma edição de 2020 por uma de 2025 de álbum original de 1990; manter o ano principal 1990 e o mesmo identificador local. A capa manual existente continua prioritária salvo alteração explícita na revisão.

### RF-10 — Avisar possível duplicado e revisar o existente (E/U)

**Entrada:** tentativa de salvar título equivalente e o mesmo conjunto de artistas de registro existente, considerando a data original conforme seção 2.2. **Saída:** aviso e acesso à revisão do registro existente.

**Comportamento:** manter um registro por álbum. A ordem dos artistas não muda o conjunto. Não combinar registros automaticamente. O usuário decide qual edição manter por revisão do registro existente, com troca conforme RF-09 quando aplicável. Aplicar a normalização da seção 2.1 e a distinção pela data original da seção 2.2. Coincidência de título/artistas gera candidato à revisão, não bloqueio absoluto: álbuns comprovadamente distintos com datas originais diferentes podem coexistir. Edições posteriores do mesmo álbum continuam em um único registro. Datas ausentes, parciais ou coincidentes e homônimos não resolvidos permanecem em P-01/P-02/P-03; não os tratar como iguais ou distintos automaticamente.

**Aceitação:**

- CA-10.1: cadastrar uma combinação já persistida, com a mesma grafia e data original, ou com data insuficiente para concluir a distinção; receber aviso e conseguir revisar o registro existente.
- CA-10.2: tentar a mesma combinação com artistas em ordem invertida; receber o mesmo aviso.
- CA-10.3: escolher outra edição do mesmo álbum no fluxo de revisão; verificar que permanece um registro, atualizado somente após confirmação.
- CA-10.4: cancelar a revisão; verificar que a coleção não foi alterada.
- CA-10.5: título igual e conjunto de artistas diferente não deve, por esse motivo isolado, ser considerado o mesmo álbum.
- CA-10.6: variar caixa, acentos e espaços do título e dos nomes dos mesmos artistas; identificar o mesmo candidato, preservando a grafia de exibição.
- CA-10.7: cadastrar dois álbuns realmente distintos de título/artistas equivalentes com datas originais conhecidas e diferentes (1990 e 2005); permitir registros distintos identificados por essas datas. Tentar cadastrar a reedição de 2020 do primeiro; revisar seu registro de 1990, sem criar terceiro álbum.
- CA-10.8 (condicionado a P-01/P-03): definir e verificar a resolução de colisões com data ausente, parcial ou coincidente antes de concluir o fluxo desses casos.

### RF-11 — Remover álbum com confirmação (E)

**Entrada:** álbum e confirmação explícita. **Saída:** remoção persistida ou cancelamento.

**Comportamento:** identificar o álbum na confirmação. Remover suas associações e links da coleção; preservar os demais álbuns. Artistas que ficarem sem álbuns deixam de aparecer na lista (U); retenção ou exclusão física desses registros depende de P-02. Não se exige lixeira ou recuperação individual.

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
- CA-16.2: criar cópia seguindo as instruções; restaurar em ambiente local de teste separado e verificar contagens, grafias originais, identidades de artistas, vínculos, datas originais e sua precisão (se aprovada), edições e URLs de capas manuais/automáticas e streaming; incluir datas da edição se seu armazenamento for aprovado.
- CA-16.3: verificar consulta e sorteio da coleção restaurada com APIs indisponíveis.
- CA-16.4: testar cópia ausente, inválida ou incompatível; informar falha e preservar a biblioteca atual antes de qualquer substituição destrutiva (T).
- CA-16.5: se a capa for apenas referência externa, a documentação explica que backup preserva a referência e que a imagem pode ficar indisponível.

## 4. Regras de negócio

| ID | Regra | Origem / verificação |
| --- | --- | --- |
| RN-01 | A coleção não distingue álbuns ouvidos, pendentes ou adquiridos. | E / RF-01, RF-13. |
| RN-02 | Título e pelo menos um artista são obrigatórios; ano, capa e links são opcionais. | E / CA-01.1–2. |
| RN-03 | Colaboração associa um único álbum a múltiplos artistas. | E / CA-06.2. |
| RN-04 | Há um registro por álbum e uma edição escolhida pelo usuário. | E/U / RF-03, RF-09, RF-10, seção 2.2; P-01/P-03 para identidade ambígua. |
| RN-05 | Título normalizado e mesmo conjunto de artistas identificam candidatos à revisão; álbuns distintos são diferenciados pela data original, sem usar a data de reedição para criar registros. | E/U/D / RF-10, seções 2.1–2.2. |
| RN-06 | Não combinar registros nem escolher edição automaticamente. | E / CA-03.4, CA-10.3–4. |
| RN-07 | Troca de edição exige revisão e preserva links de streaming. | U / CA-09.1–4. |
| RN-08 | Toda a biblioteca ou os álbuns de um artista são os conjuntos disponíveis para sorteio. | E / RF-13–14. |
| RN-09 | Todos os álbuns elegíveis têm a mesma chance; repetições consecutivas são válidas. | E / CA-13.3–4, CA-14.2. |
| RN-10 | Ausência de capa, ano ou links não exclui álbum do sorteio. | E/D / RF-13–14. |
| RN-11 | Remoção exige confirmação. | E / RF-11. |
| RN-12 | Links são informados manualmente e abrem destinos externos; reprodução não é garantida. | E / RF-12. |
| RN-13 | Dados revisados e salvos sustentam consulta e sorteio sem disponibilidade das APIs. | E / CA-03.5, CA-13.5. |
| RN-14 | O ano principal representa o lançamento original; nenhum ano de lançamento informado pode ser futuro. | U / seção 2.3, CA-01.6, CA-09.6. |
| RN-15 | Capa manual definida tem prioridade sobre a automática. | U / RF-04, CA-04.6. |
| RN-16 | Artistas sem álbuns associados não aparecem na lista de artistas. | U / CA-06.3–4. |

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
| Ano ou URL inválidos | Recusar valor e identificar campo; ano futuro é inválido conforme seção 2.3. Precisão e demais regras de data dependem de P-03. | Registro anterior na edição. | Seção 2, SEG-04. |
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
| Clique duplo/reenvio ou duas gravações concorrentes | Aplicar validação de duplicado também na gravação; evitar estado parcial. | Regra de um registro por álbum. | RF-10, RNF-06; normalização conforme seção 2.1; identidade ambígua depende de P-01/P-02/P-03. |
| Backup inválido ou restauração interrompida | Informar falha; procedimento deve preservar cópia recuperável da biblioteca anterior. | Dados atuais ou cópia consistente para recuperação. | CA-16.4. |

Não exigir código HTTP específico para erros de formulário sem escolher o fluxo técnico. Rejeições de segurança e registros não encontrados precisam ser distinguíveis de sucesso e de erro interno nos testes.

## 9. Casos extremos e cobertura

| Caso | Resultado esperado / pendência |
| --- | --- |
| Zero álbuns | Biblioteca vazia compreensível; sorteio orienta cadastrar. |
| Um álbum, inclusive sem ano/capa/links | Sempre retorna esse álbum no conjunto elegível. |
| Colaboração com múltiplos artistas | Um registro, visível para cada artista e contado uma vez em cada sorteio. |
| Título igual com artistas distintos | Não classificar como mesmo álbum somente pelo título. |
| Mesmo título/artistas com diferentes edições | Edições do mesmo álbum ficam no registro único; álbuns distintos são diferenciados pela data original. Datas insuficientes/coincidentes: P-01/P-03. |
| Artistas em ordem diferente | Mesmo conjunto para aviso de duplicado. |
| Nomes/títulos com acentos, caixa diferente ou espaços | Comparação equivalente pela seção 2.1, preservando a grafia original na exibição; sem fusão automática. |
| Artistas homônimos, inclusive com mesmo ano de formação ou sem esse dado | Ano isolado não garante identidade; solução proposta na seção 10.1, pendente em P-02. |
| Data original ausente/parcial ou igual em álbuns homônimos | Não inventar componentes nem presumir identidade; resolução pendente em P-01/P-03. |
| Ano de lançamento futuro em entrada manual ou externa | Recusar o valor; corrigir ou remover campo opcional antes de salvar. |
| Mesmo artista informado duas vezes | Não ampliar peso do álbum nem duplicar linha; escolha entre deduplicar ou rejeitar o campo: P-02. |
| Dados externos faltantes | Revisão permite completar; não salvar sem obrigatórios. |
| Troca de edição com capa diferente/ausente | Revisão antes da gravação; links e prioridade da capa manual preservados. Remoção/substituição manual exige ação explícita; retenção de imagens: P-07. |
| Exclusão do último álbum de um artista | Artista sai da lista; nenhum álbum elegível para seu sorteio. Retenção/exclusão do registro: P-02. |
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

As decisões DEC-01–11 resolvem a referência ao lançamento original, normalização textual, visibilidade de artistas sem álbuns, proibição de anos futuros e prioridade da capa manual, além dos esclarecimentos anteriores. As pendências abaixo abrangem somente aspectos ainda não decididos. As avaliações nas seções 10.1–10.3 são recomendações, não decisões aprovadas.

| ID | Tipo | Questão ainda aberta e impacto | Pergunta para decisão |
| --- | --- | --- | --- |
| P-01 | Identificação residual | A data original diferencia álbuns distintos, mas pode faltar, ter pouca precisão ou coincidir. Datas de reedição não resolvem essa ambiguidade. | Como confirmar e registrar álbuns distintos nesses casos: identificador externo do álbum, nota de desambiguação ou outro dado revisado? Quais campos de edição (país, formato, gravadora etc.) apresentar? Ver seções 10.2–10.3. |
| P-02 | Identidade de artistas e retenção | Normalização e ocultação de artistas sem álbuns estão decididas. Falta distinguir homônimos, tratar repetição do mesmo artista no formulário e definir retenção dos registros sem vínculos. | Aprovar a proposta da seção 10.1, incluindo diferenciação manual sem ano de formação? Deduplicar ou rejeitar artista repetido? Manter ou excluir registros sem álbuns e qual resposta dar ao acesso direto após exclusão? |
| P-03 | Precisão e dados temporais adicionais | Ano principal original e proibição de anos futuros estão decididos. Faltam precisão, formatos, limite inferior e armazenamento da data da edição. | Aceitar ano, ano/mês e data completa conforme seção 10.2? Como ordenar datas parciais/ausentes? Rejeitar mês/dia futuro dentro do ano corrente? Qual limite inferior e formato de entrada? Aprovar o campo separado e opcional de ano/data da edição recomendado na seção 10.3? |
| P-04 | Incompleto | Limites de campos/links e validade específica do campo Spotify não estão definidos. | Há limites desejados? O campo Spotify deve aceitar apenas URLs de spotify.com? Links de uma mesma plataforma podem aparecer várias vezes? Os limites técnicos poderão ser propostos para aprovação antes da implementação. |
| P-05 | Vago | Pesquisa não define correspondência, campos externos, ordenação, paginação ou tratamento de consulta vazia. | Busca local deve aceitar parte do título/artista, usando a normalização já definida? Consulta vazia mostra toda a biblioteca? Quais campos de pesquisa externa e ordenações são necessários? |
| P-06 | Incompleto técnico | Não foram definidos validade/tamanho do cache, timeout, retries, tamanho máximo de resposta nem limites do Cover Art Archive. | Autoriza definir esses valores como configuração técnica documentada, respeitando os fornecedores e mantendo fallback manual? O contato para User-Agent também precisa ser informado antes das chamadas reais. |
| P-07 | Retenção de imagens | Prioridade da manual, preservação na troca de edição e alternativa visual estão definidas em RF-04/RF-09. Falta decidir armazenamento das imagens. | É necessário guardar imagens localmente ou basta manter referências com imagem padrão quando indisponíveis? Como reter e incluir arquivos no backup, caso haja armazenamento local? |
| P-08 | Critério incompleto | Metas de tempo/interações sem hardware, navegador, dataset, rede, cache, repetições, início/fim ou contagem de interação. PC e dispositivos móveis definidos como contextos obrigatórios, mas sem navegadores e viewports de teste definidos. | Qual ambiente será usado? Como contar digitação/cliques e medir carregamento? Quais navegadores e viewports de PC e celular validar, incluindo retrato e paisagem no celular? Essas definições devem ser registradas antes de declarar as metas cumpridas. |
| P-09 | Incompleto operacional | Backup sem frequência, retenção ou preferência de destino. | Basta procedimento manual documentado, executado pelo usuário, ou existe rotina desejada? Agendamento automático não está no escopo atual. |

### 10.1 Avaliação de artistas homônimos — proposta T/P-02

O ano de formação pode ajudar a diferenciar bandas ou grupos, mas não é uma chave suficiente: pode ser desconhecido, aproximado ou coincidente entre homônimos, além de haver dissoluções e reformações. Para artistas solo, formação não tem o mesmo significado; nascimento e início de carreira são dados diferentes e não devem ser convertidos automaticamente em “formação”. Torná-lo obrigatório impediria cadastros legítimos.

Recomenda-se um identificador local estável para cada artista, independente do nome e das datas, com identificador externo quando disponível e confirmado, e uma descrição curta de desambiguação revisada pelo usuário (por exemplo, tipo de artista, país ou cidade e período de atividade). Ano de formação seria metadado opcional apenas quando aplicável; início de carreira ou nascimento, se desejados, exigem definição própria. A descrição deve permitir distinguir as opções na seleção e na listagem. Nome normalizado igual gera candidatos para seleção/revisão, sem fusão automática. Se faltarem dados externos e datas, permitir distinguir manualmente dois artistas por essa descrição é a alternativa recomendada. A obrigatoriedade da descrição nos casos ambíguos e os metadados oferecidos ainda precisam de confirmação.

Após aprovação, verificar homônimos com anos diferentes, iguais e ausentes, artista solo sem formação e associação de cada álbum ao artista correto. Até lá, normalização textual não equivale a identidade confirmada.

### 10.2 Avaliação de datas parciais — proposta T/P-01/P-03

Recomenda-se suportar ano (`AAAA`), ano e mês (`AAAA-MM`) e data completa (`AAAA-MM-DD`), registrando explicitamente a precisão. Isso evita inventar janeiro ou o dia 1 quando apenas o ano/mês é conhecido. Os formatos aqui são propostas de representação, não uma decisão de interface ou armazenamento físico. Ausência total permanece permitida; não admitir mês/dia sem ano nem dia sem mês.

- **Validação proposta:** validar apenas os componentes presentes; mês entre 1 e 12 e dia válido para o mês/ano, incluindo anos bissextos. Aplicar a proibição já confirmada de ano futuro em qualquer precisão. Rejeitar mês ou dia futuro dentro do ano corrente é uma extensão a confirmar; a decisão sobre anos futuros não resolve esse ponto.
- **Ordenação proposta:** comparar o início do intervalo possível para obter uma ordem de apresentação, mantendo a precisão visível e usando título normalizado e identificador local como desempate; colocar datas ausentes por último. Esses valores de ordenação não seriam datas persistidas como se fossem exatas. Confirmar essa convenção e a direção da ordenação em P-03/P-05; outra alternativa é agrupar por ano e sinalizar a ordem desconhecida dentro dele.
- **Identificação proposta:** tratar cada data parcial como intervalo possível. `1990` e `2005` não se sobrepõem e podem diferenciar álbuns distintos; `1990` e `1990-05` se sobrepõem e não comprovam diferença; `1990-05` e `1990-06` não se sobrepõem. Intervalos sobrepostos, data ausente ou mesma data completa exigem revisão e eventual desambiguação adicional conforme P-01. A data, mesmo completa, não comprova sozinha que dois registros são o mesmo álbum.

Somente após aprovação, acrescentar casos de aceitação para ano isolado, ano/mês, data completa, ano bissexto, componentes inválidos, ordenação com precisão mista e colisões com intervalos sobrepostos. Não exigir dia e mês conhecidos para todo cadastro apenas porque a data auxilia a identificação.

### 10.3 Avaliação do ano/data da edição — proposta T/P-03

Vale a pena armazenar separadamente, de forma opcional, o ano ou a data da edição escolhida: ajuda a reconhecer uma reedição, conferir a seleção externa e explicar por que a edição de 2020 tem ano principal 1990. Esse dado acompanha a troca de edição após revisão e não participa da distinção entre álbuns conceituais nem substitui o original desconhecido. Seu armazenamento e a precisão aceita dependem de confirmação; não se cria um segundo álbum para preservar uma edição anterior. Um identificador externo de edição, por si só, também não prova que se trata de outro álbum. Para resolver P-01, pode-se avaliar um identificador externo no nível do álbum, distinto do identificador da edição, ou uma nota manual de desambiguação; a escolha permanece pendente.

**Tensões a observar:**

- Revisão de “possível duplicado” não prova identidade de um álbum; bloqueio absoluto por título/artistas pode impedir um caso legítimo de homônimo. A data original resolve os casos distinguíveis; P-01/P-03 tratam dados insuficientes/coincidentes sem introduzir múltiplas edições do mesmo álbum.
- A independência das APIs vale para metadados e sorteio; não promete streaming ou imagens remotas offline. Guardar imagens locais seria uma decisão adicional de retenção, ainda pendente.
- Meta de dois segundos não inclui consultas externas. O controle de taxa pode impor espera em pesquisas externas e não contradiz essa meta.
- Uso pessoal não torna seguro publicar sem autenticação. Publicação continua condicionada às decisões e alterações previstas no escopo.

## 11. Rastreabilidade e condição para aprovação

| Item do escopo | Requisitos principais |
| --- | --- |
| Cadastro manual e por busca | RF-01–03, INT-01. |
| Campos obrigatórios/opcionais e colaboração | Seção 2, RF-01, RF-06, RN-02–03. |
| Capas e imagem padrão | DEC-11, RF-04, RN-15, INT-02; P-07 apenas para retenção. |
| Identificação, nomes e datas de lançamento | DEC-06–07/09–10, seções 2.1–2.3, RF-09–10, RN-14, P-01–03. |
| Artistas visíveis e homônimos | DEC-08, RF-06, RN-16; proposta 10.1/P-02. |
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
