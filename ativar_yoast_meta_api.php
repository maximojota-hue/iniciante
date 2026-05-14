<?php
/**
 * Plugin Name: Clube3D — Yoast Meta via REST API
 * Description: Registra os campos do Yoast SEO (focuskw, metadesc, title) para leitura e escrita via REST API.
 * Version: 1.0
 * Author: Clube 3D Brasil
 */

add_action('init', function () {
    $campos = [
        '_yoast_wpseo_focuskw',
        '_yoast_wpseo_metadesc',
        '_yoast_wpseo_title',
    ];
    foreach ($campos as $campo) {
        register_post_meta('post', $campo, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () {
                return current_user_can('edit_posts');
            },
        ]);
    }
});
