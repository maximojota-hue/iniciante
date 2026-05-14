<?php
/**
 * Plugin Name: Helio Brinquedos - Permalink Emergency Fix
 * Description: Corrige URLs publicas quando o rewrite do subdominio esta quebrado. Forca permalinks com /index.php/ e limpa regras de rewrite.
 * Version: 1.2.0
 * Author: Clube 3D Brasil
 */

if (!defined('ABSPATH')) {
    exit;
}

function helio_permalink_emergency_apply() {
    global $wp_rewrite;

    update_option('permalink_structure', '/index.php/%postname%/');
    update_option('category_base', 'categoria');
    update_option('tag_base', 'tag');

    if ($wp_rewrite) {
        $wp_rewrite->set_permalink_structure('/index.php/%postname%/');
        $wp_rewrite->flush_rules(true);
    } else {
        flush_rewrite_rules(true);
    }
}

register_activation_hook(__FILE__, 'helio_permalink_emergency_apply');

add_action('admin_init', function () {
    if (!current_user_can('manage_options')) {
        return;
    }

    if (get_option('helio_permalink_emergency_applied') !== '1') {
        helio_permalink_emergency_apply();
        update_option('helio_permalink_emergency_applied', '1');
    }
});

add_action('admin_notices', function () {
    if (!current_user_can('manage_options')) {
        return;
    }
    echo '<div class="notice notice-warning"><p><strong>Helio Permalink Emergency Fix ativo:</strong> URLs de posts foram configuradas para <code>/index.php/%postname%/</code>. Depois que o rewrite do servidor for corrigido, desative este plugin e salve os links permanentes novamente.</p></div>';
});

function helio_permalink_with_index($url) {
    $home = home_url('/');
    if (strpos($url, $home . 'index.php/') === 0) {
        return $url;
    }
    if (strpos($url, $home) === 0) {
        return $home . 'index.php/' . ltrim(substr($url, strlen($home)), '/');
    }
    return $url;
}

add_filter('post_link', 'helio_permalink_with_index', 99);
add_filter('post_type_link', 'helio_permalink_with_index', 99);
add_filter('page_link', 'helio_permalink_with_index', 99);

function helio_redirect_plain_slug_to_index() {
    if (is_admin() || (defined('REST_REQUEST') && REST_REQUEST)) {
        return;
    }

    $path = parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH);
    $path = trim((string) $path, '/');

    if ($path === ''
        || strpos($path, 'index.php/') === 0
        || strpos($path, 'wp-') === 0
        || strpos($path, 'feed') === 0
        || strpos($path, 'author/') === 0
        || strpos($path, 'category/') === 0
        || strpos($path, 'tag/') === 0
        || preg_match('/\\.(css|js|png|jpe?g|webp|gif|svg|ico|xml|txt|map)$/i', $path)
    ) {
        return;
    }

    $slug = basename($path);
    $matches = get_posts([
        'name'           => $slug,
        'post_type'      => ['post', 'page'],
        'post_status'    => 'publish',
        'posts_per_page' => 1,
        'fields'         => 'ids',
        'no_found_rows'  => true,
    ]);

    if (empty($matches)) {
        return;
    }

    $target = home_url('/index.php/' . get_post_field('post_name', $matches[0]) . '/');
    if (untrailingslashit(home_url('/' . $path)) === untrailingslashit($target)) {
        return;
    }

    wp_redirect($target, 301);
    exit;
}

add_action('init', 'helio_redirect_plain_slug_to_index', 1);
add_action('template_redirect', 'helio_redirect_plain_slug_to_index', 1);
