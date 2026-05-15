# Guia rapido de postagem - Clube 3D Brasil

Este guia existe para voce abrir o projeto e seguir a mesma sequencia sem depender da memoria da conversa.

## Sequencia recomendada

1. Abra `abrir_instalador_gui.bat` ou rode `python instalador_gui.py`.
2. Clique em `Verificar ambiente`.
3. Clique em `Instalar dependencias` se ainda nao instalou.
4. Preencha WordPress, chave da IA, link do Telegram e planilha de afiliados.
5. Clique em `Salvar configuracao`.
6. Clique em `Testar WordPress`.
7. Clique em `Abrir app principal`.

## Para criar post baseado em paginas da web

1. No app principal, abra a aba `Post Web`.
2. Defina o tema do post com foco em busca brasileira, por exemplo `melhor filamento PLA para iniciantes`.
3. Antes de gerar o texto, separe o link afiliado e a foto do produto ou produtos.
4. Confirme se vai usar apenas esse afiliado ou se deseja adicionar/selecionar mais 1.
5. Use no maximo 3 afiliados por post.
6. Se nao houver produto afiliado para o tema, registre que o rascunho sera feito sem afiliado.
7. Use a pesquisa web BR + US quando quiser comparar paginas brasileiras e americanas.
8. Carregue a planilha de afiliados se o artigo tiver produto.
9. Selecione as fotos correspondentes aos produtos.
10. Gere o post SEO.
11. Publique como `draft` para revisar no WordPress.
12. Revise titulo, slug, meta description, imagem destacada, links internos, bloco afiliado e Yoast.
13. Publique quando estiver pronto.

## Para criar post baseado em YouTube

1. No app principal, abra a aba `YouTube`.
2. Cole a URL do video escolhido.
3. Antes de gerar o texto, separe o link afiliado e a foto do produto ou produtos.
4. Confirme se vai usar apenas esse afiliado ou se deseja adicionar/selecionar mais 1.
5. Use no maximo 3 afiliados por post.
6. Se nao houver afiliado para o tema, confirme que o rascunho sera feito sem afiliado.
7. Selecione a categoria correta.
8. Gere o post automatico.
9. Revise o rascunho no WordPress antes de publicar.

## Quando houver produto afiliado

1. Confirme o link afiliado e a foto correspondente antes de gerar o post.
2. Pergunte se sera usado mais 1 afiliado antes de escrever.
3. Use no maximo 3 afiliados por post.
4. Use imagem do produto dentro do texto.
5. Coloque link afiliado na imagem abrindo em nova aba.
6. Redimensione a imagem para nao quebrar a estetica do artigo.
7. Inclua um CTA claro, sem parecer propaganda agressiva.
8. Crie interlinks para posts relacionados do Clube 3D Brasil.

## Checklist final antes de publicar

- O post esta na categoria certa.
- O slug nao esta duplicado.
- A palavra-chave aparece no titulo, introducao e subtitulos.
- A imagem destacada esta chamativa e relacionada ao tema.
- O Yoast esta preenchido.
- Os links afiliados funcionam.
- Existe pelo menos um link interno para outro post.
- O aviso do Telegram esta configurado para posts publicados.
- O conteudo pode virar Pin no Pinterest.

## Atalho por linha de comando

Gerar post web como rascunho:

```bash
python gerar_post_web_pesquisa.py "tema do post" --categoria "Filamentos" --publicar
```

Gerar post web com pesquisa profunda:

```bash
python gerar_post_web_pesquisa.py "tema do post" --categoria "Filamentos" --completo --publicar
```

O modo padrao e mais rapido e economiza tokens. Use `--completo` apenas para posts importantes ou comparativos grandes.
