"""
Atualiza o snippet 10 da home para escolher o STL em destaque por estrategia.

Regra aplicada no WordPress:
- buscar posts publicados de categorias geek/personagens/modelos;
- pontuar por imagem destacada, download/STL/3MF/modelo, origem MakerWorld,
  afiliado no conteudo e recencia;
- exibir o melhor post no hero da home, com fallback fixo caso a consulta falhe.

Uso:
  python atualizar_snippet10_destaque_estrategico.py
"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

import requests


SNIPPET_ID = 10


def carregar_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def conectar() -> tuple[requests.Session, str]:
    carregar_env()
    config = json.loads(Path("config.json").read_text(encoding="utf-8"))
    wp_url = config.get("wp_url", "https://clube3dbrasil.com").rstrip("/")
    user = os.environ.get("WP_USER", "")
    password = os.environ.get("WP_PASS", "")
    if not user or not password:
        raise SystemExit("WP_USER/WP_PASS nao encontrados no .env.")

    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 Clube3DStrategicHero/1.0",
    })
    return session, wp_url


PHP_FEATURED_LOGIC = r"""
    $c3d_featured_stl = array(
        'label' => '🔥 STL em destaque da semana',
        'title' => 'Porta-Pipoca do Bowser Jr impresso em 3D',
        'excerpt' => 'Um modelo geek funcional para imprimir, pintar e usar na mesa gamer, no setup ou na próxima sessão de filme.',
        'url' => 'https://clube3dbrasil.com/porta-pipoca-bowser-jr-impressa-3d/',
        'image' => 'https://clube3dbrasil.com/wp-content/uploads/2026/03/Bowser-jr-palomera-caramelera.jpg',
        'alt' => 'Porta pipoca do Bowser Jr impresso em 3D com recipiente frontal',
        'badge' => 'curadoria estrategica',
        'categoryUrl' => 'https://clube3dbrasil.com/category/games-personagens/',
    );

    $c3d_featured_query = new WP_Query( array(
        'post_type' => 'post',
        'post_status' => 'publish',
        'posts_per_page' => 30,
        'ignore_sticky_posts' => true,
        'tax_query' => array(
            array(
                'taxonomy' => 'category',
                'field' => 'slug',
                'terms' => array(
                    'games-personagens',
                    'stl-geek',
                    'modelos-stl',
                    'clash-royale-personagens',
                ),
                'operator' => 'IN',
            ),
        ),
    ) );

    if ( $c3d_featured_query->have_posts() ) {
        $c3d_best_score = -9999;
        while ( $c3d_featured_query->have_posts() ) {
            $c3d_featured_query->the_post();
            $c3d_post_id = get_the_ID();
            $c3d_title = wp_strip_all_tags( get_the_title( $c3d_post_id ) );
            $c3d_content = (string) get_post_field( 'post_content', $c3d_post_id );
            $c3d_text = mb_strtolower( $c3d_title . ' ' . wp_strip_all_tags( $c3d_content ) );
            $c3d_cats = wp_get_post_categories( $c3d_post_id, array( 'fields' => 'slugs' ) );
            $c3d_is_makerworld = false !== stripos( $c3d_content, 'makerworld.com' );
            $c3d_score = 0;

            if ( has_post_thumbnail( $c3d_post_id ) ) { $c3d_score += 18; }
            if ( preg_match( '/\b(stl|3mf|modelo|download|baixar|arquivo)\b/u', $c3d_text ) ) { $c3d_score += 20; }
            if ( $c3d_is_makerworld && preg_match( '/\b(gratis|gratuito|free)\b/u', $c3d_text ) ) { $c3d_score += 18; }
            if ( preg_match( '/\b(pokemon|pikachu|mario|sonic|goku|dragonite|mewtwo|clash|pekka|bowser|personagem|fan art)\b/u', $c3d_text ) ) { $c3d_score += 16; }
            if ( preg_match( '/(meli\.la|amzn\.to|sponsored|produto recomendado)/i', $c3d_content ) ) { $c3d_score += 12; }
            if ( in_array( 'games-personagens', $c3d_cats, true ) ) { $c3d_score += 14; }
            if ( in_array( 'clash-royale-personagens', $c3d_cats, true ) ) { $c3d_score += 10; }
            if ( in_array( 'stl-geek', $c3d_cats, true ) ) { $c3d_score += 8; }

            $c3d_age_days = max( 0, floor( ( current_time( 'timestamp' ) - get_post_time( 'U', true, $c3d_post_id ) ) / DAY_IN_SECONDS ) );
            if ( $c3d_age_days <= 7 ) {
                $c3d_score += 18;
            } elseif ( $c3d_age_days <= 30 ) {
                $c3d_score += 10;
            } elseif ( $c3d_age_days <= 90 ) {
                $c3d_score += 4;
            }

            if ( $c3d_score > $c3d_best_score ) {
                $c3d_best_score = $c3d_score;
                $c3d_excerpt = get_the_excerpt( $c3d_post_id );
                if ( ! $c3d_excerpt ) {
                    $c3d_excerpt = wp_trim_words( wp_strip_all_tags( $c3d_content ), 26, '...' );
                }
                $c3d_display_title = $c3d_title;
                $c3d_display_excerpt = wp_trim_words( wp_strip_all_tags( $c3d_excerpt ), 28, '...' );
                if ( ! $c3d_is_makerworld ) {
                    $c3d_free_terms = array(
                        'STL Grátis' => 'STL',
                        'STL Gratis' => 'STL',
                        'STLs gratuitos' => 'STLs',
                        'STLs gratis' => 'STLs',
                        'modelo gratuito' => 'modelo 3D',
                        'modelo gratis' => 'modelo 3D',
                        'Download STL Grátis' => 'Download STL',
                        'Download STL Gratis' => 'Download STL',
                        'gratuitos' => '',
                        'gratuito' => '',
                        'grátis' => '',
                        'gratis' => '',
                        'free' => '',
                    );
                    $c3d_display_title = str_ireplace( array_keys( $c3d_free_terms ), array_values( $c3d_free_terms ), $c3d_display_title );
                    $c3d_display_excerpt = str_ireplace( array_keys( $c3d_free_terms ), array_values( $c3d_free_terms ), $c3d_display_excerpt );
                    $c3d_display_title = trim( preg_replace( '/\s+/', ' ', $c3d_display_title ) );
                    $c3d_display_excerpt = trim( preg_replace( '/\s+/', ' ', $c3d_display_excerpt ) );
                }
                $c3d_image = get_the_post_thumbnail_url( $c3d_post_id, 'large' );
                if ( ! $c3d_image && preg_match( '/<img[^>]+src=["\']([^"\']+)["\']/i', $c3d_content, $c3d_match ) ) {
                    $c3d_image = esc_url_raw( $c3d_match[1] );
                }
                if ( ! $c3d_image ) {
                    $c3d_image = $c3d_featured_stl['image'];
                }
                $c3d_featured_stl = array(
                    'label' => '🔥 STL em destaque da semana',
                    'title' => $c3d_display_title,
                    'excerpt' => $c3d_display_excerpt,
                    'url' => get_permalink( $c3d_post_id ),
                    'image' => $c3d_image,
                    'alt' => $c3d_title . ' STL para impressão 3D',
                    'badge' => 'escolha estrategica',
                    'categoryUrl' => in_array( 'stl-geek', $c3d_cats, true ) ? 'https://clube3dbrasil.com/category/stl-geek/' : 'https://clube3dbrasil.com/category/games-personagens/',
                );
            }
        }
        wp_reset_postdata();
    }
"""


JS_HERO_BLOCK = r"""
        var featuredStl = <?php echo wp_json_encode( $c3d_featured_stl, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ); ?> || {};
        function c3dText(value, fallback) {
          return String(value || fallback || '').replace(/[<>&]/g, function(ch) {
            return ({'<':'&lt;','>':'&gt;','&':'&amp;'}[ch]);
          });
        }
        function c3dAttr(value, fallback) {
          return c3dText(value, fallback).replace(/"/g, '&quot;');
        }
        var hero = document.querySelector('.hub-hero');
        if (hero) {
          hero.classList.add('c3d-featured-hero');
          hero.innerHTML = '<div class="c3d-featured-copy reveal visible">' +
            '<div class="c3d-featured-kicker">' + c3dText(featuredStl.label, '🔥 STL em destaque da semana') + '</div>' +
            '<h1>' + c3dText(featuredStl.title, 'STL geek em destaque no Clube 3D Brasil') + '</h1>' +
            '<p class="c3d-featured-sub">' + c3dText(featuredStl.excerpt, 'Modelo com bom potencial de clique, download e conversão para a comunidade maker brasileira.') + '</p>' +
            '<ul class="c3d-featured-checks"><li>Modelo com apelo visual</li><li>Potencial de download</li><li>Conteúdo para maker brasileiro</li><li>Chance de conversão com comunidade/afiliado</li></ul>' +
            '<div class="c3d-featured-actions"><a href="' + c3dAttr(featuredStl.url, 'https://clube3dbrasil.com/blog/') + '" class="btn-primary">Ver agora</a><a href="' + c3dAttr(featuredStl.categoryUrl, 'https://clube3dbrasil.com/category/games-personagens/') + '" class="btn-ghost">Explorar STL Geek</a></div>' +
          '</div>' +
          '<div class="c3d-featured-media"><img src="' + c3dAttr(featuredStl.image, 'https://clube3dbrasil.com/wp-content/uploads/2026/03/Bowser-jr-palomera-caramelera.jpg') + '" alt="' + c3dAttr(featuredStl.alt, featuredStl.title || 'STL em destaque') + '" loading="eager" decoding="async"><div class="c3d-featured-badge">' + c3dText(featuredStl.badge, 'curadoria estrategica') + '</div></div>';
        }
"""


def aplicar_alteracoes(code: str) -> str:
    marker = "    ?>\n    <style id=\"c3d-home-structure-overrides\">"
    if marker not in code:
        raise RuntimeError("Marcador PHP/CSS do snippet 10 nao encontrado.")
    php_pattern = re.compile(
        r"\n    \$c3d_featured_stl = array\(\n.*?(?=" + re.escape(marker) + r")",
        re.S,
    )
    if "$c3d_featured_stl = array(" in code:
        code, _ = php_pattern.subn(lambda _: "\n" + PHP_FEATURED_LOGIC + "\n", code, count=1)
    else:
        code = code.replace(marker, PHP_FEATURED_LOGIC + "\n" + marker, 1)

    hero_pattern = re.compile(
        r"        var hero = document\.querySelector\('\.hub-hero'\);\n"
        r"        if \(hero\) \{\n"
        r".*?"
        r"        \}\n"
        r"        var quick = document\.querySelector\('\.quick-nav'\);",
        re.S,
    )
    replacement = JS_HERO_BLOCK + "\n        var quick = document.querySelector('.quick-nav');"
    updated, count = hero_pattern.subn(replacement, code, count=1)
    if count != 1:
        featured_pattern = re.compile(
            r"        var featuredStl = <\?php echo wp_json_encode\(.*?"
            r"        var quick = document\.querySelector\('\.quick-nav'\);",
            re.S,
        )
        updated, count = featured_pattern.subn(replacement, code, count=1)
    if count != 1:
        raise RuntimeError("Bloco JS do hero nao encontrado para substituicao.")
    return updated


def main() -> None:
    session, wp_url = conectar()
    endpoint = f"{wp_url}/wp-json/code-snippets/v1/snippets/{SNIPPET_ID}"
    response = session.get(endpoint, timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"Falha ao ler snippet {SNIPPET_ID}: {response.status_code} {response.text[:200]}")

    snippet = response.json()
    original = snippet.get("code", "")
    updated = aplicar_alteracoes(original)
    if updated == original:
        print("Snippet 10 ja estava com destaque estrategico.")
        return

    payload = {
        "name": snippet.get("name"),
        "desc": snippet.get("desc", ""),
        "code": updated,
        "tags": snippet.get("tags", []),
        "scope": snippet.get("scope", "front-end"),
        "active": snippet.get("active", True),
        "priority": snippet.get("priority", 20),
    }
    save = session.post(endpoint, json=payload, timeout=30)
    if save.status_code not in (200, 201):
        raise SystemExit(f"Falha ao salvar snippet {SNIPPET_ID}: {save.status_code} {save.text[:300]}")
    print(f"Snippet {SNIPPET_ID} atualizado com destaque estrategico.")


if __name__ == "__main__":
    main()
