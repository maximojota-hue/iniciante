# 📱 Integração Facebook — Clube 3D Automação

## ✅ O que foi implementado

### 1. **Novo módulo: `facebook_publisher.py`**
- Publica posts na página Facebook via Graph API
- Integrado ao pipeline existente
- Mesmo padrão de erro/retry que o WordPress

### 2. **Nova aba: "📱 Facebook"**
- Status de conexão
- Histórico de posts publicados
- Botão para testar credenciais

### 3. **Integração automática no POST SEO**
- Quando publica no WordPress, também publica no Facebook
- Opção de habilitar/desabilitar na aba Configurações

### 4. **Credenciais no `.env`**
```env
FB_PAGE_ID=61584998482421
FB_PAGE_TOKEN=929852030051751|PqXL_tdHHp59yV8HRH6OJFz2GeU
```

---

## 🚀 Como usar

### **Passo 1: Habilitar na Configuração**
1. Abra a GUI: `python app_gui.py`
2. Vá para **⚙️ Configurações**
3. Mude **"Publicar no Facebook automaticamente?"** para `true`
4. Clique em **"💾 Salvar Configurações"**
5. Clique em **"🔌 Testar Conexão WP"** (testa WP + FB)

### **Passo 2: Testar Conexão Facebook**
1. Vá para **📱 Facebook**
2. Clique em **"✅ Testar Conexão"**
3. Se aparecer ✅, credenciais estão OK
4. Se aparecer ❌, confira FB_PAGE_ID e FB_PAGE_TOKEN no `.env`

### **Passo 3: Publicar Post com Facebook**
1. Vá para **✍️ Post SEO**
2. Gere um post normalmente (YouTube ou keyword)
3. Clique em **"🚀 Publicar"**
4. Escolha se quer `draft` ou `publish`
5. Resultado:
   - ✅ Post publicado no WordPress
   - ✅ Post compartilhado no Facebook (se habilitado)
   - ✅ Log aparece em ambas as abas

---

## 📊 O que é publicado no Facebook

```
Título: [Título do Post]
Descrição: [Primeiros 200 caracteres do conteúdo]
Imagem: [Thumbnail do post]
Link: [URL do post no WordPress]
```

---

## 🔧 Troubleshooting

### ❌ "Erro 400: Bad Request"
**Causa:** Token inválido ou expirado
**Solução:** Gere um novo token em [developers.facebook.com](https://developers.facebook.com) e atualize `.env`

### ❌ "Erro 403: Forbidden"
**Causa:** Token não tem permissão para publicar
**Solução:** No Meta Developers, adicione permissão `pages_manage_posts`

### ❌ "Erro 404: Page not found"
**Causa:** Page ID incorreto
**Solução:** Verifique se `FB_PAGE_ID` está correto em `.env`

### ✅ Tudo funciona?
- Check da aba **📱 Facebook** → ver histórico de posts
- Check do log em **✍️ Post SEO** → procure por "✅ Facebook:"

---

## 📝 Estrutura do Código

```
app_gui.py
├── _build_facebook_tab()      — Interface da aba Facebook
├── _fb_testar_conexao()       — Testa credenciais
├── _fb_log_append()           — Log na aba Facebook
└── _seo_publicar_worker()     — MODIFICADO para incluir FB
    └── Chama FacebookPublisher.publish_post()

facebook_publisher.py (NOVO)
├── class FacebookPublisher
│   ├── __init__(config)       — Setup com token/page_id
│   ├── publish_post()         — Publica post no FB
│   ├── get_page_insights()    — Busca dados da página
│   └── test_connection()      — Valida credenciais
└── class FacebookApiError     — Erros customizados
```

---

## 🎯 Fluxo Completo

```
[Post gerado no SEO]
      ↓
[Clica "🚀 Publicar"]
      ↓
[Publica no WordPress]
      ↓
[Se fb_publicar_automatico = true]
      ├→ Publica no Facebook
      ├→ Log em "📱 Facebook"
      └→ Log em "✍️ Post SEO"
      ↓
[Post visível em ambas plataformas]
```

---

## 💡 Dicas

1. **Teste com `draft` primeiro** — Mais seguro para validar o fluxo
2. **Customize a mensagem do Facebook** — Edite o método `publish_post()` em `facebook_publisher.py`
3. **Adicione hashtags** — Edite a mensagem em `facebook_publisher.py` linha ~74
4. **Aggende posts** — Facebook API suporta agendamento via parâmetro `scheduled_publish_time`

---

## 📞 Próximos passos (opcional)

- ✅ Integrar Instagram (mesma API Meta)
- ✅ Adicionar agendamento de posts
- ✅ Analytics/engajamento do Facebook
- ✅ Compartilhar em grupos (sem publicar na página)

---

**Status:** ✅ Implementado e testado
**Data:** 2026-05-01
**Versão:** 1.0
