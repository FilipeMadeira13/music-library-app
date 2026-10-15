# Operação local

Siga o README para instalar, configurar e iniciar. A preparação entrega somente o esqueleto: `/` retorna 404. Não há biblioteca funcional, backup/restore ou integrações implementadas.

## Arquivos privados e diagnóstico

- Mantenha banco, `.env` e backups acessíveis apenas ao proprietário. Em sistemas Unix, use `umask 077` antes de criar dados, diretórios com modo 700 e `.env` com modo 600. No Windows, ajuste permissões equivalentes.
- `var/` é ignorada pelo Git; WhiteNoise serve exclusivamente `var/static/`. Nunca copie dados privados para os estáticos. Um caminho alternativo de banco deve continuar privado, em disco local, fora de `STATIC_ROOT` e de pastas sincronizadas/de rede.
- A inicialização recusa `LIBRARY_DATABASE_PATH` na árvore de estáticos, inclusive subpastas, `..` e links simbólicos para essa árvore. Isso não detecta pastas sincronizadas/de rede nem aplica permissões: confira o destino escolhido e proteja também arquivos existentes (modo 600) e seus diretórios (700). Mantenha `umask 077` no shell de execução. Backups continuam em destino privado separado dos estáticos; não crie links para banco, `.env` ou backups dentro de `var/static`.
- Execute `python scripts/diagnostics.py` para registrar Python, SQLite e Django. `python manage.py check` valida a configuração; `bash scripts/check.sh` verifica a fundação inteira. Não imprima o ambiente ou o segredo nos logs.
- O segredo deve permanecer estável nas execuções normais. O segredo gerado pelo script de verificações é temporário e só atende testes.

## LAN confiável (configuração futura de uso)

O padrão é `127.0.0.1:8000`, acessível somente no PC. Para habilitar acesso pelo celular na mesma rede confiável, descubra o IP privado atual do PC e use esse IP exato, por exemplo:

```bash
export DJANGO_DEBUG=false
export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.20
python manage.py collectstatic --noinput
python -m waitress --host=192.168.1.20 --port=8000 --threads=4 config.wsgi:application
```

O endereço é ilustrativo: substitua pelo IP real e abra `http://IP-REAL:8000` no celular. Configure o firewall para permitir a porta somente a dispositivos/rede confiáveis. Qualquer dispositivo com acesso à porta poderá ler/alterar a coleção futura, pois não haverá autenticação. HTTP nesta LAN confiável segue a decisão aprovada; publicação na internet, túneis e redirecionamento de portas estão fora do escopo.

Acesso pela mesma origem não requer `CSRF_TRUSTED_ORIGINS`. Se houver uma necessidade real de origem adicional, informe a origem exata, por exemplo `http://192.168.1.20:8000`, sem curingas e sem desligar CSRF. Nunca use `ALLOWED_HOSTS=*`. Após mudança do IP, atualize host, bind e endereço no celular. Verifique isolamento de clientes Wi-Fi/firewall se não houver conexão; mantenha o servidor ativo. Emulação Playwright não comprova conectividade real.

Execute um único processo Waitress com quatro threads para a biblioteca. `runserver` é só para desenvolvimento. Pare com `Ctrl+C` antes de trocar configuração e reinicie carregando o ambiente atualizado.

## Recuperação ainda pendente

Backup e restauração são tarefas futuras: não há comandos próprios disponíveis. Antes de usar dados reais, escolher destino privado e ensaiar restauração em instância isolada; preferir cópia adicional em outro dispositivo. A arquitetura exige snapshot consistente, servidor parado na restauração e versão/esquema compatíveis. Não trate uma cópia casual do arquivo aberto como backup validado. Recomenda-se backup antes de migrações e após manutenção; frequência/retenção cabem ao proprietário, sem agenda ou limpeza automática. Períodos sem cópia podem perder alterações e URLs não preservam imagens.
