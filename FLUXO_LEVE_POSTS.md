# Fluxo Leve Para Criar Posts

Objetivo: reduzir tempo e tokens no chat.

## Como usar

1. Abra `abrir_preparador_pacote_post.bat`.
2. Escolha `YouTube` ou `Pagina web`.
3. Cole a URL.
4. Informe keyword e categoria, se quiser.
5. Selecione foto de capa e ate 3 fotos extras.
6. Marque ate 3 afiliados.
7. Clique em `Gerar pacote`.
8. Cole no chat o bloco gerado.

## O que o pacote faz

- Extrai titulo, descricao, capitulos e transcricao compacta do YouTube com `yt-dlp`.
- Extrai titulo, descricao, headings e conteudo compacto de paginas web com ferramentas gratuitas.
- Junta capa, fotos e afiliados cadastrados.
- Gera `output/PACOTE_CODEX_POST.md` e copia o texto para a area de transferencia.

## Regra no chat

Quando o usuario colar `CRIAR_POST_CLUBE3D_COM_PACOTE`, o Codex deve:

- usar o pacote como contexto principal;
- nao rodar API externa de conteudo;
- criar o post em PT-BR;
- publicar como rascunho no WordPress;
- inserir afiliados com imagem clicavel, nova aba e `rel="noopener noreferrer sponsored"`;
- atualizar `CONTROLE_POSTS.md`.

