# Handoff — clube3d-automacao

**Data:** 2026-05-07  
**Projeto:** Automação WordPress — Clube 3D Brasil + Helio Brinquedos  
**Stack:** Python 3.14 / Tkinter / WordPress REST API / Claude API (Anthropic)  
**SO:** Windows 11 / PowerShell  
**Pasta:** `C:\Users\jcarlos\Documents\New project\clube3d-automacao-codex\`

---

## 1. Estrutura de Arquivos

```
clube3d-automacao/
├── app_gui.py               # GUI principal — Clube 3D Brasil (ponto de entrada)
├── app_helio.py             # GUI standalone — Helio Brinquedos (separado)
├── publisher.py             # WordPress REST API client
├── scraper.py               # Scraper MakerWorld + Printables (via planilha xlsx)
├── gerador.py               # Gera posts HTML de modelos STL (GeradorPostsV2)
├── seo_writer.py            # Gera posts SEO por URL (YouTube, site genérico)
├── gerar_posts_manuais.py   # Posts manuais (sem scraping)
├── cluster.py               # Agrupamento de posts por cluster SEO
├── monetizacao.py           # Blocos de afiliados MercadoLivre
├── corrigir_helio_seo.py    # Script avulso — fix alt text / slug / noindex no Helio
├── corrigir_meta_helio.py   # Script avulso — preenche meta desc via Claude Haiku
├── ativar_yoast_meta_api.php# Plugin WP — registra campos Yoast na REST API
├── .env                     # Credenciais (NÃO comitar)
├── config.json              # Config salva pela GUI (sem credenciais)
├── posts_gerados.json       # Fila de posts prontos para publicar
├── posts_publicados.json    # Histórico Clube 3D
├── posts_helio.json         # Histórico Helio Brinquedos
├── status.json              # Status por slug (coletado/gerado/publicado/erro)
├── afiliados.json           # Produtos afiliados ML carregados na GUI
└── HANDOFF.md               # Este arquivo
```

---

## 2. Como Rodar

```powershell
# Dependências
pip install requests anthropic pandas openpyxl beautifulsoup4 pillow

# App principal — Clube 3D Brasil
python app_gui.py

# App Helio Brinquedos (separado, credenciais próprias)
python app_helio.py

# Scripts avulsos do Helio
python corrigir_helio_seo.py       # Fix alt text, slug, noindex em batch
python corrigir_meta_helio.py      # Preenche meta desc via Claude Haiku
python corrigir_meta_helio.py --dry-run   # Mostra sem salvar
```

---

## 3. Credenciais e Variáveis de Ambiente

### `.env` (na raiz do projeto)
```env
ANTHROPIC_API_KEY=sk-ant-api03-...   # Claude API — gerador de posts + Helio vision

# Clube 3D Brasil — WordPress Application Password
WP_USER=seu_email@exemplo.com
WP_PASS=xxxx xxxx xxxx xxxx xxxx xxxx

# Helio Brinquedos — WordPress Application Password
HELIO_WP_URL=https://heliobrinquedos.clube3dbrasil.com
HELIO_WP_USER=seu_usuario
HELIO_WP_PASS=xxxx xxxx xxxx xxxx xxxx xxxx
HELIO_WA_NUMBER=5521981536073

# Facebook (não usados ativamente)
FB_PAGE_ID=1023224737542616
FB_PAGE_TOKEN=EAAWe...
```

### Helio Brinquedos
O `app_helio.py` lê credenciais do arquivo separado `.env.helio`, mantendo o app separado do Clube 3D e sem senha hardcoded no código.

```env
WP_URL=https://heliobrinquedos.clube3dbrasil.com
WP_USER=seu_usuario
WP_PASS=xxxx xxxx xxxx xxxx xxxx xxxx
WA=5521981536073
WP_ADMIN_PASS=
```

> **Regra:** Clube 3D lê `WP_USER` / `WP_PASS` do `.env`. Helio lê `WP_URL` / `WP_USER` / `WP_PASS` / `WA` do `.env.helio`. Os dois apps são independentes.

---

## 4. Dois Blogs — Arquitetura Separada

| Atributo | Clube 3D Brasil | Helio Brinquedos |
|----------|-----------------|------------------|
| URL | https://clube3dbrasil.com | https://heliobrinquedos.clube3dbrasil.com |
| App | `app_gui.py` | `app_helio.py` |
| Credenciais | `.env` WP_USER / WP_PASS | `.env.helio` WP_USER / WP_PASS |
| REST API | `/wp-json/wp/v2/` normal | `/?rest_route=` (rewrite nginx quebrado no HostGator) |
| Nicho | Impressão 3D, modelos STL | Brinquedos antigos, raridades, games clássicos |
| Histórico | `posts_publicados.json` | `posts_helio.json` |

---

## 5. publisher.py — Pontos Críticos

### Auto-fallback REST Route
HostGator tem rewrite nginx quebrado para `/wp-json/`. O `publisher.py` detecta automaticamente:

```python
# Em _request(): detecta 404 HTML → troca para ?rest_route= → refaz o request
if (r.status_code == 404 and not self.use_rest_route
        and "wp-json" in url and "<!DOCTYPE html>" in r.text[:200]):
    self.use_rest_route = True
    # refaz o request com nova URL /?rest_route=/wp/v2/...
```

Para forçar sempre `?rest_route=` (sem probe inicial):
```python
cfg["wp_use_rest_route"] = True
```

### User-Agent obrigatório
HostGator tem Mod_Security. Requests sem UA de browser real recebem 406:
```python
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
```

### term_exists (400) nas tags/categorias
WP retorna 400 `{"code":"term_exists","data":{"term_id":65}}` ao criar tag/categoria que já existe. O `publisher.py` trata isso diretamente no POST — **não é um erro fatal**, o ID é recuperado e o post é publicado normalmente. Não deve aparecer como ❌ no log.

```python
# _obter_ou_criar_tag / _obter_ou_criar_categoria:
# Faz POST direto via session (não via _request),
# trata 400+term_exists inline sem gerar log de erro.
```

### Upload de mídia
```python
media_id, media_url = pub.upload_media(caminho_foto, alt_text="texto do alt")
# Retorna (None, "") se falhar
```

---

## 6. app_gui.py — Abas e Funcionalidades

### Abas disponíveis

| Aba | Função |
|-----|--------|
| 📊 Dashboard | Resumo de posts publicados e status |
| ⚙️ Configurações | URL WP, credenciais, planilha, posts/dia |
| 💰 Afiliados | Gerenciar produtos ML para inserção automática |
| 🚀 Pipeline | **Fluxo principal:** Coletar → Gerar → Publicar |
| ✍️ Post SEO | Gera post SEO por URL (YouTube, site) via Claude |
| 🌐 Post Web | Gera post por URL com fotos |
| 🎬 YouTube | Gera post por vídeo YouTube |
| 📋 Posts Publicados | Histórico com link direto para cada post |

### Fluxo Pipeline (aba 🚀)

1. **Coletar** → `scraper.py` lê planilha xlsx → scrapa MakerWorld/Printables → salva `downloads/*/meta.json`
2. **Gerar Posts** → `gerador.py (GeradorPostsV2)` → gera HTML com blocos afiliados → salva `posts_gerados.json`
3. **📸 Imagens** → dialog para selecionar imagens manualmente (opcional)
4. **🚀 Publicar** → `publisher.py` lê `posts_gerados.json` → filtra pendentes via `status.json` → publica em paralelo (3 workers)
5. **▶ Pipeline Completo** → executa etapas 1+2+3 em sequência automática

### Comportamento do botão Publicar
- Clicando "🚀 Publicar": salva config silenciosamente → muda para aba Pipeline → inicia thread
- O log aparece na área preta da aba Pipeline em tempo real
- Barra de progresso anima enquanto roda
- Status "Concluído." aparece quando termina

### `_save_config(notify=False)`
Salva config.json + .env a cada operação. Só mostra popup "Configurações salvas" quando chamada com `notify=True` (botão explícito "💾 Salvar Configurações").

---

## 7. app_helio.py — Fluxo Completo

App standalone para publicar no Helio Brinquedos via análise de fotos (Claude Vision).

### Fluxo
1. Seleciona 1+ fotos do produto
2. "Analisar Fotos + Gerar Post" → Claude Vision (Haiku) → JSON estruturado
3. GUI preenche campos: título, keyword, meta, tags, HTML
4. Usuário revisa → "Publicar no WordPress"
5. Worker:
   - Upload de todas as fotos
   - Injeta foto 1 após intro (`<!-- HELIO_FOTO_PRINCIPAL -->` → block size-large)
   - Injeta fotos 2+ na seção Estado (`<!-- HELIO_FOTOS_GALERIA -->` → blocks size-medium)
   - Cria post com meta Yoast no payload
   - Define featured image
   - Salva histórico em `posts_helio.json`

### JSON retornado pelo Claude (campos obrigatórios)
```json
{
  "titulo": "Nome completo do produto",
  "subtitulo": "Título com keyword — para H2",
  "intro": "Parágrafo com keyword na 1ª ou 2ª frase",
  "marca": "...", "modelo": "...", "tipo": "...",
  "funcoes": "...", "tecnologia": "...", "decada": "anos 80",
  "acompanha": "...",
  "historia": "Parágrafo histórico",
  "por_que_raro": ["motivo 1", "motivo 2"],
  "raridade": 8,
  "tendencia": "Alta valorização",
  "valor_mercado": "R$ 300–600",
  "estado_produto": ["item 1", "item 2"],
  "veja_tambem": ["produto relacionado 1"],
  "links_externos": [{"titulo": "Wikipedia", "url": "https://pt.wikipedia.org/..."}],
  "yoast_keyphrase": "palavra-chave principal",
  "yoast_title": "Keyword — Título SEO até 55 chars",
  "yoast_meta": "Meta description com keyword, até 155 chars",
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Estrutura HTML gerado
```
<h2>🧸 {subtitulo}</h2>
<p>{intro}</p>
<!-- HELIO_FOTO_PRINCIPAL -->    ← foto 1 size-large
<h2>🔍 Detalhes do Produto</h2>
<h2>📜 História do Produto</h2>
<h2>💎 Por que este item é raro?</h2>
<h2>💰 Valor de Mercado</h2>
<h2>⭐ Classificação do Item</h2>
<h2>📦 Estado do Produto</h2>
<!-- HELIO_FOTOS_GALERIA -->     ← fotos 2+ size-medium
<h2>🛒 Disponível para Compra</h2>
<a href="https://wa.me/5521981536073?...">📱 Consultar via WhatsApp</a>
<h2>🔗 Veja também</h2>          ← links internos /?s=...
<h2>📚 Saiba Mais</h2>           ← links externos Wikipedia
```

---

## 8. Yoast SEO via REST API

### Situação
Campos `_yoast_wpseo_focuskw`, `_yoast_wpseo_title`, `_yoast_wpseo_metadesc` são protegidos (prefixo `_`) e **não graváveis via REST por padrão**.

### Solução (PENDENTE de ativação no WP)
Arquivo `ativar_yoast_meta_api.php` registra os campos via `register_post_meta()`.

**Opção A — Upload como plugin:**
WP Admin → Plugins → Adicionar Novo → Enviar Plugin → upload de `ativar_yoast_meta_api.php` → Ativar

**Opção B — Colar no functions.php:**
WP Admin → Aparência → Editor de Temas → `functions.php` → colar conteúdo (sem cabeçalho Plugin) → Atualizar

### Verificação após ativar
O log vai mostrar:
- `✅ Yoast focuskw salvo: ...` → funcionou
- `⚠️ Yoast focuskw não confirmado` → plugin não ativo

---

## 9. Problemas Conhecidos e Status

| Problema | Status | Solução |
|----------|--------|---------|
| `/wp-json/` 404 no Helio (nginx quebrado) | ✅ Resolvido | Auto-fallback `?rest_route=` em `publisher.py` |
| User-Agent truncado bloqueado por Mod_Security | ✅ Resolvido | UA Chrome 124 completo |
| `term_exists` 400 ao criar tag/categoria | ✅ Resolvido | Tratado inline no POST — não é erro fatal |
| Popup "Configurações salvas" ao clicar Publicar | ✅ Resolvido | `_save_config(notify=False)` por padrão |
| Botão Publicar não mudava de aba para mostrar log | ✅ Resolvido | `_run()` faz `nb.select(tab_pipeline)` |
| Helio misturado com Clube 3D (conflito de credenciais) | ✅ Resolvido | `app_helio.py` completamente separado |
| Yoast meta não salva via REST | ⏳ Pendente | Ativar `ativar_yoast_meta_api.php` no WP Admin |
| Alt text vazio nas imagens antigas do Helio | ✅ Resolvido | `corrigir_helio_seo.py` rodado (22 imagens) |
| Slug com emoji (Pachinko ID 72) | ✅ Resolvido | Slug corrigido |
| sample-page indexável | ✅ Resolvido | Movida para lixeira |

---

## 10. Pendências SEO — Helio Brinquedos

- [ ] Ativar `ativar_yoast_meta_api.php` no WP Admin
- [ ] Homepage title: encurtar para ≤60 chars
- [ ] Homepage meta desc: expandir para ~130 chars
- [ ] OG image homepage (Yoast → Social → Facebook → Default image)
- [ ] H1 duplicados: Space Warrior, Caminhão Papa Areia
- [ ] Google Search Console: submeter sitemap_index.xml
- [ ] Preços nos produtos (Product schema / rich snippets)

---

## 11. Arquitetura Interna — publisher.py

```python
class WordPressPublisher:
    def __init__(self, config: dict)
        # config keys: wp_url, wp_user, wp_app_password
        # opcional: wp_timeout (default 45s), wp_use_rest_route (default False)

    def _build_url(self, path: str) -> tuple[str, dict]
        # Gera URL respeitando use_rest_route
        # Se use_rest_route: /?rest_route=/wp/v2/{path}
        # Senão: /wp-json/wp/v2/{path}

    def _request(self, method, path, **kwargs) -> dict | list
        # Auto-fallback: 404 HTML → seta use_rest_route=True → retry
        # Status >= 400 → raise WordPressApiError

    def testar_conexao(self) -> bool
        # GET users/me → True/False

    def upload_media(self, filepath, alt_text="") -> tuple[int|None, str]
        # Upload de imagem → retorna (media_id, media_url)

    def publicar_post(self, post: dict, skip_if_exists=True) -> dict | None
        # Cria ou atualiza post no WP

    def publicar_lote(self, posts: list, workers=3, tentativas=3) -> list
        # ThreadPoolExecutor → publicar_post em paralelo
        # Testa conexão antes; abort se falhar
```

---

## 12. Arquitetura Interna — app_gui.py

### Classe `App(tk.Tk)`

**Variáveis de estado**
```python
self.log_queue          # Queue → Pipeline log
self.seo_log_queue      # Queue → Post SEO log
self.web_log_queue      # Queue → Post Web log
self.yt_log_queue       # Queue → YouTube log
self.config_data        # dict com valores de config.json
self.running            # bool — pipeline em andamento
self.seo_running        # bool — Post SEO em andamento
self.web_running        # bool — Post Web em andamento
self.yt_running         # bool — YouTube em andamento
self._cfg_vars          # dict[key → tk.StringVar] campos Configurações
```

**Métodos principais**
```python
_run(mode)              # Inicia operação: salva config → muda aba → start thread
_worker(mode)           # Thread: redireciona stdout → executa etapa → finally reset
_save_config(notify)    # Salva config.json + .env (notify=True mostra popup)
_ler_config_atual()     # Lê config.json + injeta WP_USER/WP_PASS do .env
_etapa_publicar(cfg)    # Lê posts_gerados.json → filtra pendentes → publicar_lote
_poll_log()             # 80ms timer → drena log_queue → atualiza Text widget
_set_buttons(enabled)   # Habilita/desabilita todos botões do Pipeline
_on_done()              # Para progress bar → "Concluído." → reload tabs
```

**`PROFILES` dict** (topo do arquivo, antes da classe)
```python
PROFILES = {
    "Clube 3D Brasil": {
        "wp_url": "https://clube3dbrasil.com",
        "wp_user": "",           # sobrescrito pelo .env WP_USER
        "wp_app_password": "",   # sobrescrito pelo .env WP_PASS
        "env_user_key": "WP_USER",
        "env_pass_key": "WP_PASS",
    },
}
```

---

## 13. Arquivos de Dados

| Arquivo | Formato | Descrição |
|---------|---------|-----------|
| `config.json` | JSON | URL WP, planilha, posts_por_dia, ml_afiliado_url |
| `.env` | texto | API keys, WP_USER, WP_PASS |
| `posts_gerados.json` | lista JSON | Posts prontos para publicar (gerados pelo SEO writer ou gerador) |
| `posts_publicados.json` | lista JSON | Histórico Clube 3D — posts publicados com sucesso |
| `posts_helio.json` | lista JSON | Histórico Helio Brinquedos |
| `status.json` | dict slug→status | Status por modelo: coletado / gerado / publicado / erro |
| `afiliados.json` | lista JSON | Produtos ML: nome, link, tipo |
| `downloads/*/meta.json` | JSON | Metadados de cada modelo coletado (título, URL, imagens, etc.) |

### Estrutura de um post em `posts_gerados.json`
```json
{
  "titulo": "...",
  "slug": "meu-post-slug",
  "content": "<p>HTML completo...</p>",
  "excerpt": "...",
  "status": "draft",
  "tags": ["tag1", "tag2"],
  "categories": ["Impressão 3D"],
  "featured_image_path": "",
  "yoast_keyphrase": "...",
  "yoast_title": "...",
  "yoast_meta": "...",
  "gerado_em": "2026-05-06T11:16:32",
  "origem": "seo_writer"
}
```

---

## 14. Fluxo de Debug — Publicar não funciona

Se clicar Publicar e "nada acontecer":

1. **Verificar aba Pipeline** — o log fica na aba 🚀 Pipeline (app muda automaticamente)
2. **Ver barra de progresso** — se animar, está rodando
3. **posts_gerados.json vazio ou todos publicados** → log mostra `⚠️ Nenhum post pendente`
4. **Autenticação falhou** → log mostra `❌ Falha na autenticação: ...`
5. **`self.running` travado** → fechar e reabrir o app
6. **Erro silencioso** → rodar pelo terminal: `python app_gui.py` e ver stderr

---

## 15. Observações Importantes

1. **Reiniciar o app** após qualquer mudança em `app_gui.py` — `importlib.reload` não recarrega a GUI.
2. **Senha admin WP ≠ Application Password** — REST API usa Application Password (com espaços).
3. **Mod_Security no HostGator** — qualquer request sem UA de browser recebe 406. Já corrigido.
4. **Tema Helio:** `heliobrinquedos-v4` com `hb_seo_meta()` no `functions.php` — lê `hb_seo_desc` e injeta `<meta name="description">`.
5. **Créditos Claude API** — necessários em console.anthropic.com para geração de posts e análise de fotos.
