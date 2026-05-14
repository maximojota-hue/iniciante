# Análise de Nicho — Geek + Impressão 3D
**clube3dbrasil.com · 2026-05-06**

---

## 1. Diagnóstico do Nicho

### Oportunidade identificada
O cruzamento **fandom geek + impressão 3D** é pouco explorado em PT-BR. Buscadores têm alta demanda por termos como "pokémon stl grátis" e "naruto impressão 3d", mas a maioria dos resultados é em inglês ou espanhol — nicho praticamente vazio para um blog maker brasileiro.

### Por que esse nicho funciona para clube3dbrasil.com
- Público já engajado: makers brasileiros são consumidores de anime, games e filmes
- Intenção de busca transacional (querem baixar e imprimir)
- Potencial de monetização dupla: afiliados (filamento/impressora) + conteúdo de valor para AdSense
- Competição fraca: sites em PT-BR não têm clusters de conteúdo organizados sobre o tema

---

## 2. Os 4 Clusters — Análise Comparativa

| # | Cluster | Volume estimado | Competição PT-BR | Monetização | Prioridade |
|---|---------|----------------|-----------------|-------------|-----------|
| 1 | **STL Geek** (anime/games/filmes) | Alto | Baixa | Afiliados + AdSense | ✅ Imediata |
| 2 | **Iniciantes** (Cura/Orca/configs) | Muito alto | Média | AdSense + Cursos | Agosto 2026 |
| 3 | **Filamentos** (PLA/PETG/ABS/TPU) | Alto | Média-alta | Afiliados diretos | Setembro 2026 |
| 4 | **Renda Extra** (Shopee/Elo7/afiliados) | Médio | Baixa | Alta intenção comercial | Outubro 2026 |

### Gaps encontrados nos clusters originais

**Técnico — cluster.py:**
- "STL Geek" não estava no `TOPIC_KEYWORDS` → risco de posts não se interligarem automaticamente
- **Fix aplicado:** 26 palavras-chave de fandom adicionadas ao dicionário

**Editorial — seo_writer.py:**
- Ângulo de curadoria de fandom não existia no `_WEB_CAT_ANGULO`
- Sem orientação sobre sites de download (Printables/Thingiverse), filamentos por cor do personagem, potencial Shopee/Elo7
- **Fix aplicado:** ângulo "STL Geek" adicionado com instruções específicas para curadoria de modelos por fandom

---

## 3. Estratégia de Conteúdo — Cluster 1 STL Geek

### Estrutura de posts: Pilar + Suporte
- **10 pilares** (post abrangente por fandom): todos os personagens, onde baixar, filamento ideal
- **10 suportes** (post específico): um personagem/item com guia técnico detalhado

### Por que pilar + suporte
- Pilares capturam volume alto ("naruto stl grátis")
- Suportes capturam cauda longa ("como imprimir goku super sayajin")
- Interlinks automáticos entre os dois aumentam autoridade e tempo na página

### Fandoms selecionados (ordem por volume de busca estimado)
1. Pokémon
2. Minecraft
3. Naruto
4. Dragon Ball
5. Marvel
6. One Piece
7. Demon Slayer
8. Star Wars
9. Zelda
10. Funko Pop

---

## 4. Calendário Editorial — Cluster 1

**Período:** 12 mai – 17 jul 2026 · **Ritmo:** 2x/semana (seg + qui)

| # | Data | Fandom | Tipo | Keyword-alvo |
|---|------|--------|------|-------------|
| 01 | 12/05 | Pokémon | pilar | pokémon stl grátis impressão 3d |
| 02 | 15/05 | Minecraft | pilar | minecraft stl grátis impressão 3d |
| 03 | 19/05 | Naruto | pilar | naruto stl grátis impressão 3d |
| 04 | 22/05 | Dragon Ball | pilar | dragon ball stl grátis impressão 3d |
| 05 | 26/05 | Pokémon | suporte | como imprimir pikachu 3d |
| 06 | 29/05 | Marvel | pilar | marvel stl grátis impressão 3d |
| 07 | 02/06 | One Piece | pilar | one piece stl grátis impressão 3d |
| 08 | 05/06 | Naruto | suporte | akatsuki impressão 3d stl grátis |
| 09 | 09/06 | Demon Slayer | pilar | demon slayer stl grátis impressão 3d |
| 10 | 12/06 | Dragon Ball | suporte | como imprimir goku super sayajin 3d |
| 11 | 16/06 | Star Wars | pilar | star wars stl grátis impressão 3d |
| 12 | 19/06 | Marvel | suporte | como imprimir homem aranha 3d |
| 13 | 23/06 | Zelda | pilar | zelda stl grátis impressão 3d |
| 14 | 26/06 | One Piece | suporte | chapéu de palha luffy impressão 3d stl |
| 15 | 30/06 | Funko Pop | pilar | como fazer funko pop impressão 3d stl grátis |
| 16 | 03/07 | Demon Slayer | suporte | como imprimir máscara tanjiro 3d |
| 17 | 07/07 | Minecraft | suporte | como imprimir creeper 3d iniciante |
| 18 | 10/07 | Star Wars | suporte | capacete darth vader impressão 3d stl grátis |
| 19 | 14/07 | Zelda | suporte | triforce zelda impressão 3d stl grátis |
| 20 | 17/07 | Pokémon | suporte | eevee evoluções impressão 3d stl grátis |

---

## 5. Execução — Resultado do dia

### Posts gerados e publicados
- **Script:** `gerar_cluster1_geek.py` → Claude API (haiku) → `posts_gerados.json`
- **20/20 posts** publicados em WordPress
- **WP IDs:** 2764 – 2802
- **Custo estimado:** ~$0,16 (haiku a $0,008/post)

### Imagens featured
- **Fonte:** Pollinations.ai (gratuito, sem API key)
- **Script:** `gerar_imagens_cluster1.py`
- **20/20 imagens** geradas e vinculadas via `featured_media`
- **Media IDs:** 2804 – 2823
- **Resolução:** 1280×720 px, modelo flux
- **Cache local:** `imagens_cluster1/`

### Ajustes técnicos aplicados

| Arquivo | Mudança |
|---------|---------|
| `cluster.py` | Adicionado `"STL Geek": [26 keywords de fandom]` ao `TOPIC_KEYWORDS` |
| `seo_writer.py` | Adicionado ângulo `"STL Geek"` em `_WEB_CAT_ANGULO` com instruções de curadoria |
| `seo_writer.py` | `_build_system_prompt()` passa `categoria` para injetar ângulo correto |
| `seo_writer.py` | `gerar_post_seo()` repassa `categoria` para o system prompt |
| `gerar_cluster1_geek.py` | Novo script — 20 posts com metadados completos |
| `gerar_imagens_cluster1.py` | Novo script — Pollinations + WP upload + featured_media |
| `dashboard.html` | Dashboard visual de controle da pipeline |

---

## 6. Próximos Passos

### Cluster 2 — Iniciantes (agosto 2026)
**Keywords-alvo:** como usar Cura, configurar Orca slicer, primeira impressão 3d, camada de adesão
**Ação:** criar `gerar_cluster2_iniciantes.py` + ângulo seo_writer

### Cluster 3 — Filamentos (setembro 2026)
**Keywords-alvo:** melhor filamento pla, diferença pla petg, temperatura impressão abs, tpu flexível impressão
**Ação:** criar `gerar_cluster3_filamentos.py` + ângulo seo_writer

### Cluster 4 — Renda Extra (outubro 2026)
**Keywords-alvo:** vender impressão 3d shopee, ganhar dinheiro impressora 3d, quanto custa impressão 3d, como precificar
**Ação:** criar `gerar_cluster4_renda.py` + ângulo seo_writer

### SEO on-page — pendências da auditoria anterior
- ⏳ Schema JSON-LD BlogPosting nos posts editoriais
- ⏳ Alt text nas imagens secundárias dentro dos posts
- ⏳ robots.txt: `Disallow: /wp-admin/` via cPanel
- ⏳ Confirmar og:type=article ativo no Yoast

---

## 7. Arquivos de Referência

```
clube3d-automacao/
├── cluster.py                      # ClusterManager v3.0 — STL Geek adicionado
├── seo_writer.py                   # ângulo STL Geek em _WEB_CAT_ANGULO
├── gerar_cluster1_geek.py          # 20 posts Cluster 1
├── gerar_imagens_cluster1.py       # imagens featured via Pollinations
├── dashboard.html                  # painel de controle visual
├── posts_gerados.json              # rascunhos antes de publicar
├── posts_publicados.json           # log pós-publicação (wp_id, slug, url)
└── imagens_cluster1/               # cache local das 20 imagens
```

---

*Gerado em 2026-05-06 · Claude Sonnet 4.6 · clube3d-automacao pipeline*
