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

1. Crie uma pasta para o personagem ou uma pasta mae de categoria, por exemplo `pokemon`.
2. Dentro da pasta mae, crie uma subpasta para cada personagem/modelo.
3. Em cada subpasta, coloque as fotos do modelo.
4. Coloque tambem um atalho `.url` apontando para a pagina de download do modelo.
5. Abra `abrir_preparador_personagem.bat`.
6. Selecione a pasta do personagem ou a pasta mae da categoria.
7. Deixe marcado `Ler subpastas e gerar varios pacotes` para processar varias subpastas.
8. Informe a keyword somente quando for uma pasta unica; em lote, a keyword sera inferida pelo link/atalho de cada pasta.
9. Se quiser monetizar, selecione ate 3 afiliados nos dropdowns.
10. Para produto novo, preencha nome, link e foto em `Cadastrar novo afiliado`; isso atualiza `CONTROLE_AFILIADOS.md` e regenera `AFILIADOS_CADASTRADOS.html`.
11. Clique em `Gerar pacote(s)`.
12. Cole no chat o bloco `CRIAR_POST_PERSONAGEM_3D_COM_PASTA` ou `CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS`.

O preparador identifica automaticamente:

- a categoria do conjunto pela pasta mae, como `pokemon`;
- o personagem pela subpasta e pelo `.url`;
- a keyword pelo nome do atalho ou pelo slug do link, como `Pokemon Pikachu`;
- as fotos de cada pacote, priorizando arquivos `download*.jpg` como capa.
- ate 3 afiliados escolhidos no preparador, que entram no campo `afiliados` do pacote.

Quando o usuario colar `CRIAR_POST_PERSONAGEM_3D_COM_PASTA`, o Codex deve:

- usar as fotos da pasta como base visual;
- criar um post original em PT-BR sobre o personagem/modelo 3D;
- orientar material, cor, escala, suporte e cuidados de impressao;
- no final do post, inserir CTA para baixar/acessar a pagina do modelo;
- configurar o link final para abrir em nova aba com `rel="noopener noreferrer"`;
- publicar como rascunho no WordPress;
- atualizar `CONTROLE_POSTS.md`.

Quando o usuario colar `CRIAR_VARIOS_POSTS_PERSONAGEM_3D_COM_PASTAS`, o Codex deve:

- tratar cada item do JSON como um post separado;
- criar os rascunhos em sequencia;
- manter a categoria do conjunto em `fonte.categoria_personagem`;
- atualizar `CONTROLE_POSTS.md` para cada rascunho criado;
- avisar quais posts foram criados e quais ficaram pendentes, se algum falhar.
