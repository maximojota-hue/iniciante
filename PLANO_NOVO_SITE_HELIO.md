# Plano do Novo Site - HelioBrinquedos

Data: 2026-05-07

## Objetivo

Criar uma instalacao WordPress limpa para o HelioBrinquedos, com foco em:

- venda direta de itens raros via WhatsApp;
- SEO organico para colecionaveis vintage;
- monetizacao com AdSense e afiliados;
- autoridade editorial em cultura retro/geek.

Posicionamento:

> HelioBrinquedos e um acervo editorial-comercial de colecionaveis vintage, brinquedos antigos, relogios raros, games classicos e cultura retro dos anos 70, 80, 90 e 2000.

## Estrutura de URL Recomendada

Usar slugs simples, permanentes e sem acento.

```text
/
/acervo/
/brinquedos-antigos/
/relogios-vintage/
/games-classicos/
/action-figures/
/cultura-retro/
/anos-70/
/anos-80/
/anos-90/
/anos-2000/
/guias/
/quanto-vale/
/como-conservar/
/sobre/
/contato/
```

## Tipos de Conteudo

### 1. Produto / Item do Acervo

Pode ser post normal com categoria `Acervo`, sem WooCommerce no inicio.

Campos essenciais:

- titulo
- slug
- marca
- modelo
- tipo
- decada
- estado/conservacao
- acompanha
- historia
- por que e raro
- valor/faixa de preco
- disponibilidade
- fotos reais
- WhatsApp CTA
- meta description
- imagem destacada
- tags

Schema recomendado:

- `Product`
- `Offer` quando houver preco
- `Article` como fallback editorial

### 2. Post Editorial

Conteudo para atrair trafego.

Exemplos:

- Brinquedos dos anos 80 que viraram raridade
- Historia dos relogios Casio com jogo
- Jaspion e a febre dos tokusatsus no Brasil
- Os games portateis LCD antes do Game Boy
- Como avaliar o estado de um brinquedo antigo

Schema:

- `Article`
- `FAQPage` quando houver perguntas frequentes

### 3. Pagina Cluster

Paginas-pilar para SEO.

Exemplos:

- Brinquedos Antigos
- Relogios Vintage
- Games Classicos
- Action Figures
- Anos 80

Cada pagina cluster deve linkar para:

- produtos do acervo;
- posts editoriais;
- subcategorias;
- contato/WhatsApp.

## Categorias Iniciais

```text
Acervo
Brinquedos Antigos
Relogios Vintage
Games Classicos
Action Figures
Cultura Retro
Anos 70
Anos 80
Anos 90
Anos 2000
Guias de Colecionador
Tokusatsu
Filmes e Series
Desenhos Nostalgicos
```

## Tags Iniciais

Usar tags com moderacao.

Exemplos:

```text
Estrela
Tec Toy
Casio
Bandai
McFarlane
Nintendo
Sega
Jaspion
Game Watch
LCD
Vintage
Colecionavel
Item Raro
Anos 80
Anos 90
```

## Plugins Minimos

Instalacao limpa deve comecar com poucos plugins.

Obrigatorios:

- Yoast SEO
- Site Kit by Google
- WP Mail SMTP, se formularios forem usados

Opcional depois:

- Redirection
- LiteSpeed Cache ou plugin de cache recomendado pela hospedagem
- Advanced Custom Fields, se quiser campos visuais no admin

Evitar no inicio:

- WooCommerce
- Page builders pesados
- muitos plugins de schema concorrentes

## Configuracoes Que Devem Ser Testadas Antes de Construir

Logo apos instalar o WordPress novo:

1. Criar post teste.
2. Salvar permalink.
3. Testar:

```text
https://heliobrinquedos.clube3dbrasil.com/wp-json/
https://heliobrinquedos.clube3dbrasil.com/wp-sitemap.xml
https://heliobrinquedos.clube3dbrasil.com/sitemap_index.xml
```

4. Confirmar que um post abre em URL amigavel:

```text
https://heliobrinquedos.clube3dbrasil.com/post-teste/
```

5. Confirmar que o editor salva sem erro de JSON.

Se qualquer um desses falhar, parar e corrigir hospedagem/permalink antes de importar conteudo.

## Homepage Recomendada

Secoes:

1. Hero simples com proposta:
   - HelioBrinquedos
   - Brinquedos raros, games classicos e colecionaveis que marcaram geracoes.

2. Acervo em Destaque:
   - cards de produtos reais

3. Categorias:
   - Brinquedos Antigos
   - Relogios Vintage
   - Games Classicos
   - Action Figures

4. Cultura Retro:
   - ultimos posts editoriais

5. Guia de Colecionador:
   - posts educativos

6. CTA WhatsApp:
   - "Tem interesse em algum item raro?"

## Automacao

O `app_helio.py` deve publicar inicialmente como `draft`.

Payload ideal:

- `title`
- `slug`
- `content`
- `excerpt`
- `status=draft`
- `featured_media`
- `tags`
- `categories`
- `meta` Yoast
- `meta` do tema ou ACF

Fluxo:

1. selecionar fotos;
2. Claude Vision gera JSON estruturado;
3. app cria post rascunho;
4. app envia imagem destacada e galeria;
5. app salva meta Yoast;
6. usuario revisa no WP;
7. usuario publica manualmente.

## Primeiros Conteudos Para Lançar

### Produtos / Acervo

1. Relogio Casio Aero Batics GA-7
2. Relogio Casio Space Warrior GS-16
3. Jogo eletronico Hook Tec Toy
4. Casio Cosmo Fighter CG-110
5. Casio Solar Shuttle CG-10
6. Caminhao Papa Areia Estrela
7. Action figure Jaspion Bandai
8. Wonder Woman McFarlane
9. Hulk Marvel Select
10. Fusca Herbie escala 1:18

### Posts Editoriais

1. Brinquedos dos anos 80 que viraram raridade
2. A historia dos relogios Casio com jogo
3. Games LCD portateis antes do Game Boy
4. Jaspion e a febre dos tokusatsus no Brasil
5. Como avaliar brinquedos antigos antes de comprar

## Decisao Final

Nao reconstruir como loja pesada inicialmente.

Construir como:

> WordPress leve + conteudo editorial + acervo comercial + WhatsApp + SEO estruturado.

WooCommerce fica para uma segunda fase, quando houver estoque, precos fixos e fluxo de pedidos mais maduro.

## Tema v5 Criado

Arquivo instalavel:

```text
C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\heliobrinquedos-v5.zip
```

Transformacoes aplicadas no tema:

- tema renomeado para `HelioBrinquedos v5`;
- home separada em `Acervo a venda` e `Cultura Retro`;
- posts com metacampos de produto usam layout comercial;
- posts sem metacampos de produto usam layout editorial;
- helpers `hb_is_product_post()` e `hb_is_editorial_post()`;
- Yoast passa a controlar title/canonical/description/Open Graph quando ativo;
- schema `Product` fica restrito a posts de produto;
- schema `Article` entra apenas para editorial quando Yoast nao estiver ativo;
- novos metacampos REST: `hb_modelo` e `hb_tipo`;
- `app_helio.py` ajustado para enviar categorias e campos do tema v5.
