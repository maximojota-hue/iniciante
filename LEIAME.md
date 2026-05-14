# 🤖 Clube 3D Brasil — Automação Completa

Sistema end-to-end que elimina o trabalho manual de criar posts para o blog.
Roda automaticamente 1x por dia e publica posts direto no WordPress.

---

## ⚡ Instalação (primeira vez)

```bash
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar o navegador (para o scraper)
playwright install chromium

# 3. Configurar credenciais e horário
python setup.py

# 4. Registrar no Windows (executa automaticamente todo dia)
#    ⚠️ Execute o terminal como Administrador
python instalar_agendador.py
```

---

## 🚀 Uso diário

Após instalar, **não precisa fazer nada** — roda sozinho todo dia.

Para executar manualmente:

| Arquivo | O que faz |
|---|---|
| `executar_agora.bat` | Duplo clique — roda o pipeline completo agora |
| `iniciar.bat` | Inicia o agendador em loop (alternativa ao Task Scheduler) |

---

## 🔧 Comandos avançados (terminal)

```bash
# Pipeline completo
python main.py

# Limite de modelos
python main.py --limite 5

# Habilitar posts Top 10 por tema
python main.py --top10

# Só coletar dados do MakerWorld
python main.py --so-coletar

# Só gerar HTML (dados já coletados)
python main.py --so-gerar

# Só publicar (posts já gerados)
python main.py --so-publicar

# Ver histórico de execuções
python agendador.py --status

# Remover tarefa agendada do Windows
python instalar_agendador.py --remover
```

---

## 📁 Estrutura de arquivos

```
clube3d-automacao/
├── 📄 main.py                ← Pipeline principal
├── 📄 agendador.py           ← Agendador diário
├── 📄 setup.py               ← Configuração inicial
├── 📄 scraper.py             ← Módulo 1: coleta MakerWorld
├── 📄 gerador.py             ← Módulo 2: gera posts HTML
├── 📄 publisher.py           ← Módulo 3: publica no WordPress
├── 📄 instalar_agendador.py  ← Instala no Windows Task Scheduler
├── 🖱️  iniciar.bat            ← Inicia agendador (duplo clique)
├── 🖱️  executar_agora.bat     ← Executa pipeline agora (duplo clique)
├── 📄 requirements.txt       ← Dependências Python
├── 📄 afiliados_exemplo.json ← Modelo para criar afiliados.json
│
├── 🔒 config.json            ← Suas credenciais (NÃO compartilhe!)
├── 📊 status.json            ← Controle do que já foi processado
├── 📊 posts_gerados.json     ← Posts gerados aguardando publicação
├── 📊 posts_publicados.json  ← Histórico de posts publicados
│
├── 📂 downloads/             ← Modelos coletados do MakerWorld
│   └── modelo-{slug}/
│       ├── meta.json
│       ├── imagem-1.jpg
│       ├── imagem-2.jpg
│       └── modelo.3mf
│
└── 📂 logs/
    ├── agendador.log         ← Log de texto das execuções
    └── execucoes.json        ← Histórico estruturado
```

---

## 📋 Status dos módulos

| Módulo | Arquivo | Status |
|---|---|---|
| 1 — Scraper MakerWorld | `scraper.py` | ✅ Pronto |
| 2 — Gerador de Posts | `gerador.py` | ✅ Pronto |
| 3 — Publisher WordPress | `publisher.py` | ✅ Pronto |
| 4 — Agendador Automático | `agendador.py` | ✅ Pronto |

---

## ⚙️ Configurar Application Password no WordPress

Necessário para o publisher funcionar:

1. Acesse **WordPress → Usuários → Seu Perfil**
2. Role até **"Senhas de aplicativo"**
3. Nome: `Clube3D Bot`
4. Clique em **"Adicionar nova senha de aplicativo"**
5. Copie a senha gerada (formato: `xxxx xxxx xxxx xxxx xxxx xxxx`)
6. Cole no `python setup.py` quando solicitado
