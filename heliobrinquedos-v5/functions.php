<?php
/**
 * HelioBrinquedos — functions.php v4.0
 */
if ( ! defined( 'ABSPATH' ) ) exit;

define( 'HB_VER', '5.0.0' );
define( 'HB_URI', get_template_directory_uri() );
define( 'HB_DIR', get_template_directory() );

/* ── Setup ────────────────────────────────────────────────── */
function hb_setup() {
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'automatic-feed-links' );
    add_theme_support( 'html5', ['search-form','comment-form','comment-list','gallery','caption','style','script'] );
    add_theme_support( 'custom-logo', ['height'=>60,'width'=>220,'flex-width'=>true,'flex-height'=>true] );
    set_post_thumbnail_size( 800, 600, true );
    add_image_size( 'hb-hero',  1400, 700,  true );
    add_image_size( 'hb-card',  600,  450,  true );
    add_image_size( 'hb-thumb', 120,  90,   true );
    register_nav_menus(['primary'=>'Menu Principal','footer'=>'Menu Rodapé']);
    load_theme_textdomain( 'heliobrinquedos', HB_DIR . '/languages' );
}
add_action( 'after_setup_theme', 'hb_setup' );

function hb_content_width() { $GLOBALS['content_width'] = 1152; }
add_action( 'after_setup_theme', 'hb_content_width', 0 );

/* ── Enqueue ──────────────────────────────────────────────── */
function hb_enqueue() {
    // Google Fonts
    wp_enqueue_style( 'hb-fonts',
        'https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Nunito:wght@400;500;600;700&display=swap',
        [], null );

    wp_enqueue_style( 'hb-style', get_stylesheet_uri(), ['hb-fonts'], HB_VER );
    wp_enqueue_script( 'hb-main', HB_URI . '/assets/js/main.js', [], HB_VER, true );

    if ( is_singular() && comments_open() && get_option('thread_comments') ) {
        wp_enqueue_script( 'comment-reply' );
    }
}
add_action( 'wp_enqueue_scripts', 'hb_enqueue' );

/* ── Widgets ──────────────────────────────────────────────── */
function hb_widgets_init() {
    $a = [
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ];
    register_sidebar( array_merge( $a, ['name'=>'Sidebar Principal','id'=>'sidebar-1'] ) );
}
add_action( 'widgets_init', 'hb_widgets_init' );

/* ── Customizer ───────────────────────────────────────────── */
function hb_customizer( $wp_customize ) {
    $wp_customize->add_section('hb_contato', ['title'=>'📲 Contato e WhatsApp','priority'=>25]);
    $contato = [
        'hb_whatsapp'  => ['label'=>'Número WhatsApp (somente dígitos, ex: 5521981536073)', 'default'=>'5521981536073'],
        'hb_instagram' => ['label'=>'Link Instagram',  'default'=>'#'],
        'hb_facebook'  => ['label'=>'Link Facebook',   'default'=>'#'],
        'hb_youtube'   => ['label'=>'Link YouTube',    'default'=>'#'],
    ];
    foreach ( $contato as $id => $cfg ) {
        $wp_customize->add_setting( $id, ['default'=>$cfg['default'],'sanitize_callback'=>'sanitize_text_field','transport'=>'refresh'] );
        $wp_customize->add_control( $id, ['label'=>$cfg['label'],'section'=>'hb_contato','type'=>'text'] );
    }

    $wp_customize->add_section('hb_feira', ['title'=>'🏪 Atendimento Presencial','priority'=>26]);
    $feira = [
        'hb_feira_local'    => ['label'=>'Local da Feira (endereço completo)', 'default'=>'Feira de Antiguidades da Praça XV — Rio de Janeiro/RJ'],
        'hb_feira_horario'  => ['label'=>'Horário',                            'default'=>'Sábados das 8h às 15h'],
        'hb_feira_descricao'=> ['label'=>'Descrição adicional',                'default'=>'Venha ver de perto, testar e negociar diretamente!'],
    ];
    foreach ( $feira as $id => $cfg ) {
        $wp_customize->add_setting( $id, ['default'=>$cfg['default'],'sanitize_callback'=>'sanitize_text_field','transport'=>'refresh'] );
        $wp_customize->add_control( $id, ['label'=>$cfg['label'],'section'=>'hb_feira','type'=>'text'] );
    }
}
add_action( 'customize_register', 'hb_customizer' );

/* ── Helpers ──────────────────────────────────────────────── */
function hb_wa_link( $msg = '' ) {
    $num = preg_replace( '/\D/', '', get_theme_mod( 'hb_whatsapp', '5521981536073' ) );
    if ( ! $msg ) $msg = 'Olá! Vim pelo site HelioBrinquedos e tenho interesse em um produto.';
    return 'https://wa.me/' . $num . '?text=' . rawurlencode( $msg );
}

function hb_wa_icon() {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>';
}

function hb_rarity_badge( $pid ) {
    $rar  = get_post_meta( $pid, 'hb_raridade', true );
    if ( ! $rar ) return '';
    $map  = [
        'Comum'      => ['cls'=>'comum',      'icon'=>'●'],
        'Raro'       => ['cls'=>'raro',        'icon'=>'◆'],
        'Muito Raro' => ['cls'=>'muito-raro',  'icon'=>'★'],
        'Peça Única' => ['cls'=>'peca-unica',  'icon'=>'♛'],
    ];
    $cfg = $map[ $rar ] ?? ['cls'=>'comum','icon'=>'●'];
    return sprintf(
        '<span class="badge-rarity badge-rarity--%s"><span class="badge-icon">%s</span>%s</span>',
        esc_attr( $cfg['cls'] ), $cfg['icon'], esc_html( $rar )
    );
}

function hb_thumb( $pid, $size = 'hb-card' ) {
    if ( has_post_thumbnail( $pid ) ) {
        return get_the_post_thumbnail( $pid, $size, ['loading'=>'lazy'] );
    }
    $map = ['🎮'=>'games','🧸'=>'brinquedos','⭐'=>'raridades','🚗'=>'miniaturas'];
    $cats = wp_get_post_categories( $pid, ['fields'=>'slugs'] );
    $emoji = '🧸';
    foreach ( $map as $e => $slug ) {
        if ( in_array( $slug, $cats ) ) { $emoji = $e; break; }
    }
    return '<span class="card-thumb-emoji" aria-hidden="true">' . $emoji . '</span>';
}

function hb_primary_category( $pid ) {
    $cats = wp_get_post_categories( $pid, ['fields'=>'all'] );
    if ( ! $cats ) return '';
    $priority = ['brinquedos','games','raridades','miniaturas','destaques'];
    foreach ( $priority as $slug ) {
        foreach ( $cats as $cat ) {
            if ( $cat->slug === $slug ) return $cat->name;
        }
    }
    return $cats[0]->name;
}

function hb_spec_row( $label, $value ) {
    if ( ! $value ) return '';
    return sprintf(
        '<div class="detail-row"><span class="detail-label">%s</span><span class="detail-value">%s</span></div>',
        esc_html( $label ), esc_html( $value )
    );
}

function hb_post_has_category_slug( $pid, array $slugs ) {
    $cats = wp_get_post_categories( $pid, ['fields'=>'slugs'] );
    return (bool) array_intersect( $slugs, $cats );
}

function hb_is_product_post( $pid = null ) {
    $pid = $pid ?: get_the_ID();
    if ( ! $pid ) return false;

    $product_slugs = [
        'acervo',
        'brinquedos-antigos',
        'relogios-vintage',
        'games-classicos',
        'action-figures',
        'raridades',
        'brinquedos',
        'games',
        'miniaturas',
        'destaques',
    ];

    if ( hb_post_has_category_slug( $pid, $product_slugs ) ) {
        return true;
    }

    foreach ( ['hb_preco','hb_raridade','hb_conservacao','hb_decada','hb_marca','hb_acompanha'] as $key ) {
        if ( get_post_meta( $pid, $key, true ) ) return true;
    }

    return false;
}

function hb_is_editorial_post( $pid = null ) {
    return ! hb_is_product_post( $pid );
}

function hb_yoast_active() {
    return defined( 'WPSEO_VERSION' ) || class_exists( 'WPSEO_Frontend' );
}

function hb_breadcrumb() {
    echo '<nav class="breadcrumb" aria-label="Breadcrumb">';
    echo '<a href="' . esc_url( home_url('/') ) . '">Início</a>';
    echo '<span class="breadcrumb-sep">›</span>';
    if ( is_singular() ) {
        $cats = get_the_terms( get_the_ID(), 'category' );
        if ( $cats && ! is_wp_error( $cats ) ) {
            echo '<a href="' . esc_url( get_term_link( $cats[0] ) ) . '">' . esc_html( $cats[0]->name ) . '</a>';
            echo '<span class="breadcrumb-sep">›</span>';
        }
        echo '<span>' . get_the_title() . '</span>';
    } elseif ( is_category() ) {
        echo '<span>' . single_cat_title( '', false ) . '</span>';
    }
    echo '</nav>';
}

/* ── Meta Box ─────────────────────────────────────────────── */
function hb_register_metabox() {
    add_meta_box( 'hb_produto_meta', '🧸 Informações do Produto', 'hb_metabox_callback', 'post', 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'hb_register_metabox' );

function hb_metabox_callback( $post ) {
    wp_nonce_field( 'hb_save_meta', 'hb_nonce' );
    $fields = [
        '-- Produto'         => null,
        'hb_preco'           => 'Preço (ex: 250,00 ou deixe vazio para "Sob Consulta")',
        'hb_raridade'        => 'Raridade (Comum / Raro / Muito Raro / Peça Única)',
        'hb_conservacao'     => 'Estado de Conservação (Excelente / Muito Bom / Bom / Regular)',
        'hb_decada'          => 'Década (Anos 70 / Anos 80 / Anos 90 / Anos 2000)',
        'hb_marca'           => 'Marca / Fabricante',
        'hb_modelo'          => 'Modelo / Referencia',
        'hb_tipo'            => 'Tipo de item (brinquedo, relogio, game, action figure)',
        'hb_origem'          => 'Origem (Nacional / Importado)',
        'hb_acompanha'       => 'Acompanha (ex: caixa original, manual, acessórios)',
        '-- WhatsApp'        => null,
        'hb_wa_msg'          => 'Mensagem automática WhatsApp (deixe vazio para padrão)',
        '-- SEO'             => null,
        'hb_seo_desc'        => 'Meta descrição (máx. 155 caracteres)',
        'hb_palavras'        => 'Palavras-chave',
        '-- História'        => null,
        'hb_historia'        => 'Conte a história / contexto do produto',
    ];
    ?>
    <style>
    .hb-meta-table{width:100%;border-collapse:collapse}
    .hb-meta-table td{padding:6px 8px;vertical-align:top}
    .hb-meta-table .hb-label{width:230px;font-weight:600;font-size:13px;padding-top:9px}
    .hb-meta-table input,.hb-meta-table textarea{width:100%;padding:6px 10px;border:1px solid #ddd;border-radius:4px;font-size:13px}
    .hb-meta-table textarea{height:70px;resize:vertical}
    .hb-section-head td{background:#fff8ee;font-weight:700;font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:8px 10px;color:#8a5a00;border-top:2px solid #e0aa38}
    </style>
    <table class="hb-meta-table">
    <?php foreach ( $fields as $key => $label ) :
        if ( $label === null ) : ?>
          <tr class="hb-section-head"><td colspan="2"><?php echo esc_html( ltrim( $key, '-' ) ); ?></td></tr>
        <?php else :
            $val     = esc_attr( get_post_meta( $post->ID, $key, true ) );
            $is_long = in_array( $key, ['hb_historia','hb_seo_desc','hb_palavras','hb_acompanha'] );
        ?>
          <tr>
            <td class="hb-label"><label for="<?php echo $key; ?>"><?php echo esc_html( $label ); ?></label></td>
            <td>
              <?php if ( $is_long ) : ?>
                <textarea id="<?php echo $key; ?>" name="<?php echo $key; ?>"><?php echo $val; ?></textarea>
              <?php else : ?>
                <input type="text" id="<?php echo $key; ?>" name="<?php echo $key; ?>" value="<?php echo $val; ?>">
              <?php endif; ?>
            </td>
          </tr>
        <?php endif; endforeach; ?>
    </table>
    <?php
}

function hb_save_meta( $pid ) {
    if ( ! isset( $_POST['hb_nonce'] ) || ! wp_verify_nonce( $_POST['hb_nonce'], 'hb_save_meta' ) ) return;
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) return;
    if ( ! current_user_can( 'edit_post', $pid ) ) return;
    $keys = ['hb_preco','hb_raridade','hb_conservacao','hb_decada','hb_marca','hb_modelo','hb_tipo','hb_origem','hb_acompanha','hb_wa_msg','hb_seo_desc','hb_palavras','hb_historia'];
    foreach ( $keys as $k ) {
        if ( isset( $_POST[$k] ) ) update_post_meta( $pid, $k, sanitize_textarea_field( $_POST[$k] ) );
    }
}
add_action( 'save_post', 'hb_save_meta' );

/* ── REST API — expõe meta fields para scripts externos ──────── */
function hb_register_meta_rest() {
    $meta_keys = [
        'hb_preco', 'hb_raridade', 'hb_conservacao', 'hb_decada',
        'hb_marca', 'hb_modelo', 'hb_tipo', 'hb_origem', 'hb_acompanha', 'hb_wa_msg',
        'hb_seo_desc', 'hb_palavras', 'hb_historia',
    ];
    foreach ( $meta_keys as $key ) {
        register_post_meta( 'post', $key, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function() { return current_user_can( 'edit_posts' ); },
        ]);
    }
}
add_action( 'init', 'hb_register_meta_rest' );

/* ── SEO + Open Graph ─────────────────────────────────────── */
function hb_seo_meta() {
    if ( hb_yoast_active() ) return;

    if ( is_singular() ) {
        echo '<link rel="canonical" href="' . esc_url( get_permalink() ) . '">' . "\n";
        global $post;
        $desc = get_post_meta( $post->ID, 'hb_seo_desc', true ) ?: wp_trim_words( get_the_excerpt(), 25, '' );
        $keys = get_post_meta( $post->ID, 'hb_palavras', true );
        if ( $desc ) echo '<meta name="description" content="' . esc_attr($desc) . '">' . "\n";
        echo '<meta property="og:locale" content="pt_BR">' . "\n";
        echo '<meta property="og:title" content="' . esc_attr( get_the_title() ) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($desc) . '">' . "\n";
        echo '<meta property="og:type" content="' . ( hb_is_product_post( $post->ID ) ? 'product' : 'article' ) . '">' . "\n";
        echo '<meta property="og:url" content="' . esc_url( get_permalink() ) . '">' . "\n";
        if ( has_post_thumbnail() ) {
            echo '<meta property="og:image" content="' . esc_url( get_the_post_thumbnail_url($post->ID,'hb-hero') ) . '">' . "\n";
        }
    } elseif ( is_front_page() || is_home() ) {
        echo '<link rel="canonical" href="' . esc_url( home_url('/') ) . '">' . "\n";
    }
}
add_action( 'wp_head', 'hb_seo_meta', 1 );

/* ── Schema JSON-LD ───────────────────────────────────────── */
function hb_schema() {
    if ( ! ( is_front_page() || is_home() || is_singular() ) ) return;
    $flags = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;
    $num   = preg_replace('/\D/', '', get_theme_mod('hb_whatsapp','5521981536073'));

    if ( is_front_page() || is_home() ) {
        $data = [
            '@context' => 'https://schema.org',
            '@type'    => 'Store',
            'name'     => 'HelioBrinquedos',
            'url'      => home_url('/'),
            'telephone'=> '+' . $num,
            'openingHours' => 'Sa 08:00-15:00',
            'address'  => ['@type'=>'PostalAddress','addressCountry'=>'BR','addressLocality'=>get_theme_mod('hb_feira_local','')],
        ];
        echo '<script type="application/ld+json">' . json_encode($data,$flags) . '</script>' . "\n";
    }

    if ( is_singular() && hb_is_product_post( get_the_ID() ) ) {
        global $post;
        $preco = get_post_meta( $post->ID, 'hb_preco',      true );
        $rar   = get_post_meta( $post->ID, 'hb_raridade',   true );
        $cond  = get_post_meta( $post->ID, 'hb_conservacao',true );
        $data  = [
            '@context'    => 'https://schema.org',
            '@type'       => 'Product',
            'name'        => get_the_title(),
            'url'         => get_permalink(),
            'description' => get_post_meta( $post->ID, 'hb_seo_desc', true ) ?: wp_trim_words( get_the_excerpt(), 25, '' ),
            'brand'       => ['@type'=>'Brand','name'=>get_post_meta($post->ID,'hb_marca',true) ?: 'HelioBrinquedos'],
        ];
        if ( has_post_thumbnail() ) $data['image'] = get_the_post_thumbnail_url($post->ID,'hb-hero');
        if ( $preco ) {
            $data['offers'] = [
                '@type'         => 'Offer',
                'priceCurrency' => 'BRL',
                'price'         => str_replace(',','.', preg_replace('/[^\d,]/','',$preco)),
                'availability'  => 'https://schema.org/InStock',
                'seller'        => ['@type'=>'Organization','name'=>'HelioBrinquedos'],
            ];
        }
        if ( $cond ) {
            $cond_map = ['Excelente'=>'NewCondition','Muito Bom'=>'UsedCondition','Bom'=>'UsedCondition','Regular'=>'DamagedCondition'];
            $data['itemCondition'] = 'https://schema.org/' . ( $cond_map[$cond] ?? 'UsedCondition' );
        }
        echo '<script type="application/ld+json">' . json_encode($data,$flags) . '</script>' . "\n";
    }

    if ( is_singular() && hb_is_editorial_post( get_the_ID() ) && ! hb_yoast_active() ) {
        global $post;
        $data = [
            '@context'         => 'https://schema.org',
            '@type'            => 'Article',
            'headline'         => get_the_title(),
            'url'              => get_permalink(),
            'datePublished'    => get_the_date( DATE_W3C ),
            'dateModified'     => get_the_modified_date( DATE_W3C ),
            'author'           => ['@type'=>'Person','name'=>get_the_author()],
            'publisher'        => ['@type'=>'Organization','name'=>'HelioBrinquedos'],
            'description'      => wp_trim_words( get_the_excerpt(), 28, '' ),
        ];
        if ( has_post_thumbnail() ) $data['image'] = get_the_post_thumbnail_url($post->ID,'hb-hero');
        echo '<script type="application/ld+json">' . json_encode($data,$flags) . '</script>' . "\n";
    }
}
add_action( 'wp_head', 'hb_schema' );
