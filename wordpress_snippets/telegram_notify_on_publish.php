<?php
/**
 * Clube 3D Brasil - Telegram ao publicar post.
 *
 * Use no plugin Code Snippets ou no functions.php do tema filho.
 * Configure as constantes no wp-config.php:
 *
 * define('CLUBE3D_TELEGRAM_BOT_TOKEN', '123456:ABC...');
 * define('CLUBE3D_TELEGRAM_CHAT_ID', '-1001234567890');
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('transition_post_status', 'clube3d_telegram_notify_on_publish', 10, 3);

function clube3d_telegram_notify_on_publish($new_status, $old_status, $post) {
    if ($new_status !== 'publish' || $old_status === 'publish') {
        return;
    }

    if (!$post || $post->post_type !== 'post') {
        return;
    }

    if (!defined('CLUBE3D_TELEGRAM_BOT_TOKEN') || !defined('CLUBE3D_TELEGRAM_CHAT_ID')) {
        return;
    }

    $token = CLUBE3D_TELEGRAM_BOT_TOKEN;
    $chat_id = CLUBE3D_TELEGRAM_CHAT_ID;
    if (!$token || !$chat_id) {
        return;
    }

    $title = html_entity_decode(get_the_title($post), ENT_QUOTES, 'UTF-8');
    $link = get_permalink($post);
    $excerpt = wp_strip_all_tags(get_the_excerpt($post));
    $excerpt = mb_substr(preg_replace('/\s+/', ' ', $excerpt), 0, 220);

    $message = "<b>Novo post no Clube 3D Brasil</b>\n\n";
    $message .= '<b>' . esc_html($title) . "</b>\n";
    if ($excerpt) {
        $message .= "\n" . esc_html($excerpt) . "\n";
    }
    $message .= "\n<a href=\"" . esc_url($link) . "\">Abrir post</a>";

    wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", array(
        'timeout' => 12,
        'headers' => array('Content-Type' => 'application/json; charset=utf-8'),
        'body' => wp_json_encode(array(
            'chat_id' => $chat_id,
            'text' => $message,
            'parse_mode' => 'HTML',
            'disable_web_page_preview' => false,
        )),
    ));
}
