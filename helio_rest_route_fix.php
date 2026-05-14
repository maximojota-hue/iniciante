<?php
/**
 * Plugin Name: Helio Brinquedos - REST Route Fix + Yoast Meta
 * Description: Forca URLs da REST API em ?rest_route= quando /wp-json/ esta quebrado e libera campos Yoast/meta do tema para edicao via REST.
 * Version: 1.0.0
 * Author: Clube 3D Brasil
 */

if (!defined('ABSPATH')) {
    exit;
}

add_filter('rest_url', function ($url, $path, $blog_id, $scheme) {
    $home = home_url('/');
    $path = '/' . ltrim((string) $path, '/');

    return add_query_arg('rest_route', $path, $home);
}, 10, 4);

add_filter('rest_pre_serve_request', function ($served, $result, $request, $server) {
    header('Content-Type: application/json; charset=' . get_option('blog_charset'));
    return $served;
}, 10, 4);

add_action('init', function () {
    $yoast_fields = [
        '_yoast_wpseo_focuskw',
        '_yoast_wpseo_metadesc',
        '_yoast_wpseo_title',
    ];

    foreach ($yoast_fields as $field) {
        register_post_meta('post', $field, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () {
                return current_user_can('edit_posts');
            },
        ]);
    }

    $helio_fields = [
        'hb_seo_desc',
        'hb_marca',
        'hb_modelo',
        'hb_tipo',
        'hb_decada',
        'hb_raridade',
        'hb_preco',
        'hb_conservacao',
        'hb_acompanha',
        'hb_historia',
        'hb_origem',
        'hb_palavras',
        'hb_wa_msg',
    ];

    foreach ($helio_fields as $field) {
        register_post_meta('post', $field, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () {
                return current_user_can('edit_posts');
            },
        ]);
    }
});
