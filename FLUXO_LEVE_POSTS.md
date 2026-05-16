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

## Fluxo De Personagens 3D Por Pasta

Use quando o post for sobre um personagem/modelo 3D com fotos locais e uma pagina externa para baixar o arquivo.

1. Crie uma pasta para o personagem.
2. Coloque dentro dela as fotos do modelo.
3. Coloque tambem um atalho `.url` apontando para a pagina de download do modelo.
4. Abra `abrir_preparador_personagem.bat`.
5. Selecione a pasta do personagem.
6. Informe a keyword, se quiser.
7. Clique em `Gerar pacote`.
8. Cole no chat o bloco `CRIAR_POST_PERSONAGEM_3D_COM_PASTA`.

Quando o usuario colar `CRIAR_POST_PERSONAGEM_3D_COM_PASTA`, o Codex deve:

- usar as fotos da pasta como base visual;
- criar um post original em PT-BR sobre o personagem/modelo 3D;
- orientar material, cor, escala, suporte e cuidados de impressao;
- no final do post, inserir CTA para baixar/acessar a pagina do modelo;
- configurar o link final para abrir em nova aba com `rel="noopener noreferrer"`;
- publicar como rascunho no WordPress;
- atualizar `CONTROLE_POSTS.md`.
