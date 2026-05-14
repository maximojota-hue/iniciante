"""
corrigir_politica_privacidade.py
Reescreve a Política de Privacidade do clube3dbrasil.com com todos os
requisitos obrigatórios para aprovação no Google AdSense + LGPD.

Execute: python corrigir_politica_privacidade.py
"""

import sys
import base64
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WP_URL  = "https://clube3dbrasil.com"
ENV_FILE = Path(".env")

POLITICA_TITULO = "Política de Privacidade"

POLITICA_HTML = """
<p><em>Última atualização: 02 de maio de 2026</em></p>

<p>O <strong>Clube 3D Brasil</strong> ("nós", "nosso" ou "site") está comprometido em proteger
a privacidade dos visitantes e usuários de <strong>https://clube3dbrasil.com</strong>.
Esta Política de Privacidade descreve como coletamos, usamos, armazenamos e protegemos suas
informações pessoais, em conformidade com a <strong>Lei Geral de Proteção de Dados (LGPD —
Lei nº 13.709/2018)</strong> e as políticas do <strong>Google AdSense</strong>.</p>

<p>Ao acessar ou usar nosso site, você concorda com os termos descritos nesta política.
Se não concordar com qualquer parte, recomendamos que não utilize o site.</p>

<!-- ─── 1 ─────────────────────────────────────────────────────── -->
<h2>1. Responsável pelo Tratamento de Dados</h2>
<p><strong>Nome:</strong> Clube 3D Brasil<br>
<strong>Responsável:</strong> Administrador do site<br>
<strong>E-mail:</strong> <a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a><br>
<strong>Localização:</strong> Rio de Janeiro – RJ, Brasil<br>
<strong>Site:</strong> https://clube3dbrasil.com</p>

<p>Para exercer seus direitos de titular de dados ou esclarecer dúvidas sobre esta política,
entre em contato diretamente pelo e-mail acima. Respondemos em até <strong>5 dias úteis</strong>.</p>

<!-- ─── 2 ─────────────────────────────────────────────────────── -->
<h2>2. Informações que Coletamos</h2>
<p>Coletamos dados de diferentes formas, dependendo da sua interação com o site:</p>

<h3>2.1 Dados de Navegação (automáticos)</h3>
<ul>
  <li>Endereço IP (anonimizado após 26 meses pelo Google Analytics)</li>
  <li>Tipo e versão do navegador</li>
  <li>Sistema operacional e dispositivo</li>
  <li>Páginas visitadas e tempo de permanência</li>
  <li>URL de origem (referrer) e termos de busca</li>
  <li>Data e hora de acesso</li>
</ul>

<h3>2.2 Dados Fornecidos Voluntariamente</h3>
<ul>
  <li><strong>Formulário de contato:</strong> nome e e-mail quando você nos envia uma mensagem</li>
  <li><strong>Comentários:</strong> nome, e-mail e conteúdo do comentário (se habilitado)</li>
  <li><strong>Newsletter:</strong> e-mail, caso você se inscreva para receber novidades</li>
</ul>

<h3>2.3 Cookies e Tecnologias Similares</h3>
<p>Utilizamos cookies para melhorar a experiência de navegação, exibir anúncios relevantes
e analisar o tráfego. Veja a seção 5 para detalhes completos.</p>

<!-- ─── 3 ─────────────────────────────────────────────────────── -->
<h2>3. Google AdSense e Publicidade</h2>
<p>Este site utiliza o <strong>Google AdSense</strong> para exibir anúncios. O Google, como
fornecedor terceiro, usa cookies — incluindo o <strong>cookie DART</strong> — para exibir
anúncios com base nas visitas anteriores dos usuários a este site e a outros sites na Internet.</p>

<h3>Como o Google usa seus dados para publicidade</h3>
<ul>
  <li>O Google pode usar cookies de publicidade para personalizar os anúncios exibidos</li>
  <li>Esses cookies registram visitas anteriores a este site e a outros sites parceiros da Rede de Display do Google</li>
  <li>Nenhum dado de identificação pessoal é compartilhado com o Google para fins publicitários</li>
</ul>

<h3>Como desativar a publicidade personalizada</h3>
<p>Você pode optar por não receber publicidade personalizada do Google através das seguintes opções:</p>
<ul>
  <li><a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer">
      Configurações de anúncios do Google</a></li>
  <li><a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer">
      Opt-out da Network Advertising Initiative (NAI)</a></li>
  <li>Configurações de cookies do seu navegador (veja seção 5)</li>
</ul>

<p>Para mais informações sobre como o Google usa dados, consulte:
<a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer">
Como o Google usa informações de sites ou aplicativos que usam nossos serviços</a>.</p>

<!-- ─── 4 ─────────────────────────────────────────────────────── -->
<h2>4. Google Analytics</h2>
<p>Utilizamos o <strong>Google Analytics 4 (GA4)</strong> para analisar o tráfego do site e
entender como os visitantes interagem com nosso conteúdo. O Google Analytics coleta dados de
navegação de forma anônima e agregada.</p>

<p><strong>O que o Google Analytics coleta:</strong></p>
<ul>
  <li>Número de visitantes e sessões</li>
  <li>Páginas mais acessadas e tempo médio de permanência</li>
  <li>Origem geográfica aproximada (cidade/estado)</li>
  <li>Dispositivos e navegadores utilizados</li>
  <li>Taxa de rejeição e fluxo de navegação</li>
</ul>

<p><strong>Importante:</strong> os dados são anônimos e não vinculados a qualquer informação
pessoal identificável. O IP é anonimizado automaticamente pelo GA4.</p>

<p>Para optar por não ser rastreado pelo Google Analytics, instale o
<a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">
complemento de desativação do Google Analytics</a>.</p>

<!-- ─── 5 ─────────────────────────────────────────────────────── -->
<h2>5. Política de Cookies</h2>
<p>Cookies são pequenos arquivos de texto armazenados no seu dispositivo quando você visita
um site. Utilizamos os seguintes tipos:</p>

<table style="width:100%;border-collapse:collapse;">
  <thead>
    <tr style="background:#f4f4f4;">
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">Tipo</th>
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">Finalidade</th>
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">Exemplos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;"><strong>Essenciais</strong></td>
      <td style="padding:8px;border:1px solid #ddd;">Funcionamento básico do site (login, segurança)</td>
      <td style="padding:8px;border:1px solid #ddd;">wordpress_logged_in, wp-settings</td>
    </tr>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;"><strong>Analíticos</strong></td>
      <td style="padding:8px;border:1px solid #ddd;">Análise de tráfego e comportamento (anônimo)</td>
      <td style="padding:8px;border:1px solid #ddd;">_ga, _gid, _ga_XXXXXXXX</td>
    </tr>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;"><strong>Publicitários</strong></td>
      <td style="padding:8px;border:1px solid #ddd;">Exibição de anúncios personalizados pelo Google AdSense</td>
      <td style="padding:8px;border:1px solid #ddd;">DART, IDE, test_cookie</td>
    </tr>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;"><strong>Preferências</strong></td>
      <td style="padding:8px;border:1px solid #ddd;">Lembrar configurações do usuário</td>
      <td style="padding:8px;border:1px solid #ddd;">theme, language</td>
    </tr>
  </tbody>
</table>

<h3>Como gerenciar cookies</h3>
<p>Você pode controlar ou desativar cookies nas configurações do seu navegador:</p>
<ul>
  <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer">Google Chrome</a></li>
  <li><a href="https://support.mozilla.org/pt-BR/kb/ative-e-desative-os-cookies-que-os-sites-usam" target="_blank" rel="noopener noreferrer">Mozilla Firefox</a></li>
  <li><a href="https://support.microsoft.com/pt-br/topic/excluir-e-gerenciar-cookies-168dab11-0753-043d-7c16-ede5947fc64d" target="_blank" rel="noopener noreferrer">Microsoft Edge</a></li>
  <li><a href="https://support.apple.com/pt-br/guide/safari/sfri11471/mac" target="_blank" rel="noopener noreferrer">Safari</a></li>
</ul>
<p><strong>Atenção:</strong> desativar cookies pode prejudicar o funcionamento de algumas funcionalidades do site.</p>

<!-- ─── 6 ─────────────────────────────────────────────────────── -->
<h2>6. Links de Afiliados — Amazon Associates</h2>
<p>O Clube 3D Brasil participa do <strong>Programa de Afiliados da Amazon Brasil (Amazon Associates)</strong>.
Alguns links neste site são links de afiliados: quando você clica em um desses links e realiza
uma compra, recebemos uma pequena comissão, sem custo adicional para você.</p>

<p>Isso nos ajuda a manter o site gratuito e continuar publicando conteúdo de qualidade.
Nossa opinião sobre os produtos é sempre independente — só recomendamos o que testamos ou
consideramos relevante para nossa comunidade.</p>

<p>Os preços e disponibilidade dos produtos são definidos pela Amazon e podem mudar a qualquer
momento sem aviso prévio.</p>

<!-- ─── 7 ─────────────────────────────────────────────────────── -->
<h2>7. Compartilhamento de Dados com Terceiros</h2>
<p>Não vendemos, alugamos nem comercializamos suas informações pessoais.
Compartilhamos dados <strong>apenas</strong> nas seguintes situações:</p>

<ul>
  <li><strong>Provedores de serviço:</strong> Google Analytics, Google AdSense e Amazon Associates,
      conforme descrito nesta política — cada um sujeito à sua própria política de privacidade</li>
  <li><strong>Obrigação legal:</strong> quando exigido por lei, decisão judicial ou autoridade competente</li>
  <li><strong>Proteção de direitos:</strong> para investigar ou prevenir fraudes, violações de segurança
      ou uso indevido do site</li>
</ul>

<p>Terceiros parceiros têm suas próprias políticas de privacidade. Recomendamos que você as consulte:</p>
<ul>
  <li><a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Política de Privacidade do Google</a></li>
  <li><a href="https://www.amazon.com.br/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ" target="_blank" rel="noopener noreferrer">Política de Privacidade da Amazon Brasil</a></li>
</ul>

<!-- ─── 8 ─────────────────────────────────────────────────────── -->
<h2>8. Seus Direitos — LGPD (Lei nº 13.709/2018)</h2>
<p>Como titular de dados pessoais, você tem os seguintes direitos garantidos pela LGPD:</p>

<ul>
  <li><strong>Acesso:</strong> solicitar confirmação de que tratamos seus dados e obter uma cópia</li>
  <li><strong>Correção:</strong> solicitar correção de dados incompletos, inexatos ou desatualizados</li>
  <li><strong>Anonimização / Bloqueio / Eliminação:</strong> solicitar que dados desnecessários ou
      tratados em desconformidade sejam anonimizados, bloqueados ou eliminados</li>
  <li><strong>Portabilidade:</strong> solicitar a transferência dos seus dados para outro fornecedor</li>
  <li><strong>Revogação de consentimento:</strong> retirar seu consentimento a qualquer momento,
      quando o tratamento for baseado em consentimento</li>
  <li><strong>Oposição:</strong> opor-se a tratamento realizado sem base em consentimento, em caso
      de descumprimento da LGPD</li>
  <li><strong>Informação sobre compartilhamento:</strong> saber com quais entidades públicas e
      privadas compartilhamos seus dados</li>
</ul>

<p>Para exercer qualquer um desses direitos, entre em contato pelo e-mail:
<a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a>.
Atendemos em até <strong>15 dias corridos</strong>, conforme prazo legal.</p>

<!-- ─── 9 ─────────────────────────────────────────────────────── -->
<h2>9. Segurança dos Dados</h2>
<p>Adotamos medidas técnicas e organizacionais para proteger suas informações contra acesso
não autorizado, perda ou uso indevido:</p>
<ul>
  <li>Conexão criptografada via <strong>HTTPS/SSL</strong> em todo o site</li>
  <li>Acesso administrativo protegido com autenticação forte</li>
  <li>Bloqueio de tentativas de acesso indevido via <code>.htaccess</code></li>
  <li>Atualizações regulares do WordPress, plugins e temas</li>
</ul>
<p>Apesar das medidas adotadas, nenhum sistema é 100% seguro. Em caso de incidente de segurança
que afete seus dados, você será notificado conforme exigido pela LGPD.</p>

<!-- ─── 10 ─────────────────────────────────────────────────────── -->
<h2>10. Retenção de Dados</h2>
<ul>
  <li><strong>Dados de navegação (Analytics):</strong> até 26 meses, após o que são anonimizados ou excluídos pelo Google</li>
  <li><strong>Dados de formulário de contato:</strong> até 2 anos ou enquanto necessário para resposta e registro</li>
  <li><strong>Comentários:</strong> mantidos enquanto o post estiver publicado; excluídos sob solicitação</li>
  <li><strong>Cookies publicitários:</strong> conforme configuração do Google AdSense (geralmente até 13 meses)</li>
  <li><strong>Newsletter:</strong> mantido até descadastramento ou inatividade de 24 meses</li>
</ul>

<!-- ─── 11 ─────────────────────────────────────────────────────── -->
<h2>11. Menores de Idade</h2>
<p>Este site não coleta intencionalmente dados pessoais de crianças menores de 13 anos.
Se você é responsável por uma criança e acredita que ela forneceu dados pessoais ao site,
entre em contato pelo e-mail <a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a>
para que possamos excluí-los imediatamente.</p>

<!-- ─── 12 ─────────────────────────────────────────────────────── -->
<h2>12. Links para Sites Externos</h2>
<p>Nosso site pode conter links para sites de terceiros (MakerWorld, Printables, Amazon, YouTube,
etc.). Não somos responsáveis pelas práticas de privacidade desses sites. Recomendamos que você
leia a política de privacidade de cada site que visitar.</p>

<!-- ─── 13 ─────────────────────────────────────────────────────── -->
<h2>13. Alterações nesta Política</h2>
<p>Podemos atualizar esta Política de Privacidade periodicamente para refletir mudanças em
nossas práticas, na legislação ou nos serviços de terceiros. A data de "Última atualização"
no topo desta página indica quando a versão atual entrou em vigor.</p>
<p>Recomendamos que você revise esta página regularmente. O uso continuado do site após
alterações implica concordância com a política atualizada.</p>

<!-- ─── 14 ─────────────────────────────────────────────────────── -->
<h2>14. Contato — Encarregado de Dados (DPO)</h2>
<p>Para dúvidas, solicitações ou reclamações relacionadas ao tratamento de dados pessoais,
entre em contato com o responsável pelo site:</p>

<ul>
  <li><strong>E-mail:</strong> <a href="mailto:casalabacate@gmail.com">casalabacate@gmail.com</a></li>
  <li><strong>Assunto sugerido:</strong> "Privacidade — [sua solicitação]"</li>
  <li><strong>Prazo de resposta:</strong> até 5 dias úteis para dúvidas gerais; até 15 dias corridos para solicitações LGPD</li>
  <li><strong>Localização:</strong> Rio de Janeiro – RJ, Brasil</li>
</ul>

<p>Você também pode registrar reclamações junto à <strong>Autoridade Nacional de Proteção de
Dados (ANPD)</strong>: <a href="https://www.gov.br/anpd" target="_blank" rel="noopener noreferrer">www.gov.br/anpd</a>.</p>

<hr>
<p style="font-size:0.85em;color:#666;">
Esta política foi elaborada em conformidade com a Lei Geral de Proteção de Dados (LGPD —
Lei nº 13.709/2018), o Marco Civil da Internet (Lei nº 12.965/2014), e as diretrizes do
Google AdSense para publicadores. Clube 3D Brasil © 2026. Todos os direitos reservados.
</p>
"""


def carregar_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def main():
    print("\n" + "=" * 60)
    print("  POLÍTICA DE PRIVACIDADE — Reescrita Completa")
    print("=" * 60 + "\n")

    env = carregar_env()
    user  = env.get("WP_USER", "")
    senha = env.get("WP_PASS", "")
    if not user or not senha:
        print("❌ WP_USER/WP_PASS não encontrados no .env")
        return

    api   = f"{WP_URL}/wp-json/wp/v2"
    token = base64.b64encode(f"{user}:{senha}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Content-Type":  "application/json",
        "User-Agent":    "Clube3DBrasil-Bot/1.0",
    })

    r = session.get(f"{api}/users/me", timeout=10)
    if not r.ok:
        print(f"❌ Autenticação falhou: {r.status_code}")
        return
    print(f"✅ Conectado como: {r.json().get('name', '')}\n")

    # Localizar a página pela slug
    for slug in ("politica-de-privacidade", "politica-privacidade", "privacy-policy"):
        r = session.get(f"{api}/pages", params={"slug": slug, "per_page": 5}, timeout=15)
        paginas = r.json() if r.ok else []
        if paginas:
            break

    if not paginas:
        print("❌ Página de Política de Privacidade não encontrada por slug.")
        print("   Tentando busca por título...")
        r = session.get(f"{api}/pages", params={"per_page": 100, "search": "privacidade"}, timeout=15)
        paginas = r.json() if r.ok else []

    if not paginas:
        print("❌ Página não localizada. Crie manualmente e execute novamente.")
        return

    pid    = paginas[0]["id"]
    titulo = paginas[0].get("title", {}).get("rendered", "")
    print(f"✅ Página encontrada: ID {pid} — '{titulo}'")
    print("   Atualizando conteúdo...\n")

    r = session.post(f"{api}/pages/{pid}", json={
        "title":   POLITICA_TITULO,
        "content": POLITICA_HTML,
        "status":  "publish",
        "meta": {
            "_yoast_wpseo_title":       "Política de Privacidade — Clube 3D Brasil",
            "_yoast_wpseo_metadesc":    (
                "Saiba como o Clube 3D Brasil coleta e usa seus dados. "
                "Política em conformidade com a LGPD e Google AdSense."
            ),
        },
    }, timeout=30)

    if r.ok:
        link = r.json().get("link", f"{WP_URL}/politica-de-privacidade/")
        print(f"✅ Política de Privacidade atualizada com sucesso!")
        print(f"   URL: {link}")
        print(f"\n  O que foi incluído:")
        print("   ✔ Identificação completa do responsável (email, localização)")
        print("   ✔ Google AdSense + cookie DART + links de opt-out")
        print("   ✔ Google Analytics com link de desativação")
        print("   ✔ Amazon Associates / links de afiliados")
        print("   ✔ Tabela de cookies (essenciais, analíticos, publicitários, preferências)")
        print("   ✔ 7 direitos LGPD com prazo de atendimento")
        print("   ✔ Segurança dos dados (HTTPS, .htaccess)")
        print("   ✔ Retenção de dados por categoria")
        print("   ✔ DPO identificado com email e prazo de resposta")
        print("   ✔ Links para ANPD, Google Ads Settings, NAI opt-out")
        print("   ✔ Meta description e título Yoast configurados")
    else:
        print(f"❌ Erro {r.status_code}: {r.text[:200]}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
