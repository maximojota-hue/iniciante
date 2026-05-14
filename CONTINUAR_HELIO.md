# Continuidade - HelioBrinquedos

Data: 2026-05-07

## Decisao Estrategica

O melhor caminho para o HelioBrinquedos e recomecar com uma instalacao WordPress limpa, em vez de tentar remendar a instalacao atual.

Posicionamento recomendado:

> Site editorial-comercial de colecionaveis vintage e cultura retro.

Nicho:

- Brinquedos antigos
- Relogios vintage
- Games classicos
- Action figures
- Objetos colecionaveis dos anos 70, 80, 90 e 2000

O site nao deve ser apenas loja nem apenas blog. O ideal e misturar:

- Acervo a venda
- Guias de colecionador
- Cultura retro/geek
- Paginas de cluster para SEO

## Estrutura Recomendada

```text
HelioBrinquedos
├── Acervo a Venda
│   ├── Brinquedos Antigos
│   ├── Relogios Vintage
│   ├── Games Classicos
│   └── Action Figures
├── Cultura Retro
│   ├── Anos 70
│   ├── Anos 80
│   ├── Anos 90
│   └── Anos 2000
├── Guias de Colecionador
│   ├── Como Avaliar
│   ├── Como Conservar
│   └── Quanto Vale
└── Sobre / Contato / WhatsApp
```

## SEO Recomendado

### Produto

Cada produto deve ter:

- Titulo claro com marca, modelo, tipo e raridade
- Fotos reais
- Alt text descritivo
- Estado do produto
- Decada
- Marca
- Origem
- O que acompanha
- Historia
- Por que e raro
- Preco ou faixa de valor
- Botao WhatsApp
- Links internos para posts relacionados
- Schema Product + Offer quando houver preco

### Conteudo Editorial

Categorias sugeridas:

- Anos 70
- Anos 80
- Anos 90
- Anos 2000
- Filmes classicos
- Series antigas
- Desenhos nostalgicos
- Games retro
- Tokusatsu
- Brinquedos brasileiros
- Relogios digitais vintage

Exemplos de posts:

- 10 brinquedos dos anos 80 que viraram raridade
- A historia dos relogios Casio com jogo
- Por que o Genius da Estrela marcou uma geracao
- Jaspion: por que virou febre no Brasil
- Game Boy, Master System e Mega Drive: nostalgia dos anos 90

## Monetizacao

Prioridades:

1. Venda direta por WhatsApp dos itens reais
2. AdSense nos posts editoriais
3. Afiliados Mercado Livre/Amazon/Shopee
4. Links internos para produtos proprios
5. Futuramente marketplace/loja com WooCommerce se houver estoque suficiente

Recomendacao: nao iniciar com WooCommerce pesado. Comecar com WordPress leve, posts bem estruturados, botao WhatsApp e schema.

## Estado Tecnico Atual

Projeto de trabalho:

```text
C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex
```

Arquivos importantes:

- `app_helio.py`: app standalone do Helio
- `.env.helio`: credenciais do Helio
- `publisher.py`: cliente WordPress REST API
- `HANDOFF.md`: handoff geral do projeto
- `helio_rest_route_fix.php`: plugin criado para REST/Yoast
- `helio_permalink_emergency_fix.php`: plugin emergencial de permalink

Problema atual do site existente:

- Homepage abre
- REST via `?rest_route=` funciona
- URLs publicas bonitas tiveram problema de rewrite/permalink
- `/index.php/slug/` chegou a funcionar para posts
- Tentativas de plugin emergencial nao resolveram totalmente a navegacao antiga/cache

Conclusao tecnica:

> A instalacao atual nao e uma boa base. Melhor recriar o WordPress do subdominio com instalacao limpa.

## Plano Para Recomeçar

1. Fazer backup:
   - Exportar posts pelo WordPress
   - Baixar `wp-content/uploads`
   - Guardar tema atual se quiser reaproveitar
   - Guardar `posts_helio.json`

2. Recriar WordPress no subdominio:
   - Instalar limpo em `heliobrinquedos.clube3dbrasil.com`
   - Antes de plugins/tema, testar:
     - `/wp-json/`
     - `/wp-sitemap.xml`
     - um post teste com permalink

3. Configurar base:
   - Tema leve
   - Yoast SEO
   - Application Password nova
   - Links permanentes funcionando
   - Search Console
   - Sitemap

4. Adaptar automacao:
   - Confirmar novas credenciais em `.env.helio`
   - Testar `app_helio.py` publicando rascunho
   - Garantir preenchimento de Yoast, excerpt, imagem destacada e schema

5. Construir conteudo:
   - 10 paginas/produtos reais
   - 5 posts evergreen de cultura retro
   - 4 paginas de cluster principais

## Proxima Conversa

Retomar por:

1. Definir arquitetura do novo WordPress
2. Escolher tema/plugin minimo
3. Planejar tipos de conteudo e slugs
4. Ajustar automacao para o novo site limpo
