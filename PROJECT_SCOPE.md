# Biblioteca pessoal de álbuns — definição do MVP

## Objetivo e usuário

Criar um aplicativo web pessoal para centralizar álbuns, organizá-los por artista e ajudar você a escolher o que ouvir por sorteio, com acesso às plataformas de streaming.

O usuário inicial será você. A biblioteca representará uma coleção escolhida, sem distinguir álbuns ouvidos, pendentes ou adquiridos.

A primeira entrega funcionará localmente, com Django, SQLite e templates HTML/CSS responsivos, acessíveis pelo navegador tanto em PC quanto em dispositivos móveis. Todas as funcionalidades do MVP deverão ser utilizáveis com mouse/teclado no PC e por toque no celular, com conteúdo e controles adaptados ao tamanho da tela.

Para acessar pelo celular no MVP local, o servidor deverá estar em execução no computador e permitir acesso pela mesma rede local confiável, mediante configuração explícita e documentada. Publicação na internet e PostgreSQL ficam para uma etapa posterior.

## Funcionalidades e decisões do MVP

- **Cadastrar álbuns:** pesquisar no MusicBrainz, escolher um resultado e revisar os dados antes de salvar. Oferecer cadastro manual quando a busca não encontrar o álbum ou estiver indisponível.
- **Dados do álbum:** título e pelo menos um artista obrigatórios; ano, capa e links opcionais. Permitir múltiplos artistas em colaborações.
- **Capas:** consultar o Cover Art Archive quando houver identificação compatível; exibir uma imagem padrão quando não houver capa.
- **Manter a coleção:** editar informações e remover álbuns com confirmação.
- **Organizar e pesquisar:** listar artistas, visualizar seus álbuns e pesquisar a coleção por título ou artista.
- **Abrir streaming:** oferecer um campo para Spotify e links adicionais com nome da plataforma, preenchidos manualmente.
- **Sortear:** escolher entre toda a biblioteca ou os álbuns de um artista. Cada álbum elegível terá a mesma chance; sorteios consecutivos poderão repetir resultados.
- **Tratar biblioteca vazia:** explicar que é necessário cadastrar um álbum antes de sortear.

Será mantido um registro por álbum, usando a edição escolhida no cadastro. Uma nova tentativa de cadastrar o mesmo título e conjunto de artistas deverá indicar um possível duplicado e permitir revisar o registro existente.

A interface terá biblioteca, página do artista, detalhes do álbum e formulário de cadastro/edição. As consultas externas ocorrerão no servidor Django; os dados salvos permitirão consultar e sortear sem depender das APIs. Não haverá API pública nem integração com contas de streaming no MVP.

## Dependências, riscos e evolução

- **Catálogos externos:** resultados podem apresentar ambiguidades, dados incompletos ou ausência de capas. A escolha do resultado e a edição manual permanecem disponíveis.
- **Limites de consulta:** controlar requisições e reaproveitar consultas recentes, respeitando o limite médio de uma requisição por segundo do MusicBrainz. [Documentação oficial](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting).
- **Identificação:** títulos iguais e diferentes edições exigem revisão humana; não combinar registros automaticamente.
- **Links:** podem ficar indisponíveis ou apontar para outra edição. Permitir correção; não prometer reprodução dentro do aplicativo.
- **Dados pessoais:** incluir instruções de backup e restauração da biblioteca local.

Ficam para versões futuras: histórico de escuta, avaliações, tags, filtros avançados, sorteio sem repetição, importação/exportação em lote, sincronização com Spotify, compartilhamento e múltiplos usuários.

Antes da publicação, definir orçamento e hospedagem entre as opções propostas, adicionar autenticação, migrar para PostgreSQL e validar backup e restauração.

## Metas e critérios de aceitação

- Cadastrar manualmente um álbum básico em até um minuto, em teste de uso.
- Localizar um álbum conhecido e abrir seu streaming em até três interações a partir da biblioteca.
- Carregar listagem, pesquisa e sorteio em até dois segundos com 1.000 álbuns no ambiente local de teste, excluindo consultas externas.
- Verificar que o sorteio retorna apenas álbuns do conjunto escolhido, inclusive quando há somente um álbum.
- Validar cadastro manual e por busca, edição, remoção, colaboração entre artistas e aviso de possível duplicado.
- Validar os fluxos do MVP em navegador de PC e de celular, sem rolagem horizontal da página, conteúdo cortado ou ações dependentes apenas de passar o mouse; confirmar acesso à mesma biblioteca pelo celular na rede local configurada.
- Validar ausência de capa, falha ou limite da API, ausência de links e biblioteca vazia.
- Confirmar persistência após reiniciar a aplicação e recuperação por backup.