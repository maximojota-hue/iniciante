<?php get_header(); ?>

<?php
/* ── Stats para o hero ──────────────────────────────────────── */
$all_q = new WP_Query(['post_status'=>'publish','posts_per_page'=>-1,'fields'=>'ids']);
$total = $all_q->found_posts;
wp_reset_postdata();

$pu_q = new WP_Query(['post_status'=>'publish','posts_per_page'=>-1,'fields'=>'ids','meta_query'=>[['key'=>'hb_raridade','value'=>'Peça Única']]]);
$pecas_unicas = $pu_q->found_posts;
wp_reset_postdata();

$mr_q = new WP_Query(['post_status'=>'publish','posts_per_page'=>-1,'fields'=>'ids','meta_query'=>[['key'=>'hb_raridade','value'=>'Muito Raro']]]);
$muito_raros = $mr_q->found_posts;
wp_reset_postdata();

/* ── Categorias para filtro ─────────────────────────────────── */
$filter_cats = get_categories(['hide_empty'=>true,'exclude'=>get_option('default_category')]);
$decades = ['Anos 70','Anos 80','Anos 90','Anos 2000'];
?>

<!-- ═══ HERO (só na home) ════════════════════════════════════ -->
<?php if ( is_home() || is_front_page() ) : ?>
<section class="hero-section">
  <div class="hero-grid-bg" aria-hidden="true"></div>
  <div class="hero-glow"   aria-hidden="true"></div>
  <div class="hero-glow-2" aria-hidden="true"></div>
  <div class="hero-corner hero-corner--tl" aria-hidden="true"></div>
  <div class="hero-corner hero-corner--tr" aria-hidden="true"></div>
  <div class="hero-corner hero-corner--bl" aria-hidden="true"></div>
  <div class="hero-corner hero-corner--br" aria-hidden="true"></div>

  <div class="hb-container">
    <div class="hero-content">
      <p class="section-label animate-fade-in" style="margin-bottom:1.25rem">
        Raridades &amp; Colecionáveis · Rio de Janeiro
      </p>

      <h1 class="hero-title animate-slide-up">
        OBJETOS QUE<br>
        <span class="accent">O TEMPO</span><br>
        NÃO APAGOU
      </h1>

      <p class="hero-subtitle animate-fade-in" style="animation-delay:150ms">
        Brinquedos antigos, games clássicos e peças únicas dos anos 70 ao 2000.
        Cada item selecionado com cuidado e história garantida.
      </p>

      <div class="hero-stats animate-fade-in" style="animation-delay:200ms">
        <div>
          <p class="hero-stat-val hero-stat-val--orange"><?php echo esc_html($total); ?></p>
          <p class="hero-stat-lbl">Itens</p>
        </div>
        <?php if ($pecas_unicas) : ?>
        <div class="hero-divider" aria-hidden="true"></div>
        <div>
          <p class="hero-stat-val hero-stat-val--gold"><?php echo esc_html($pecas_unicas); ?></p>
          <p class="hero-stat-lbl">Peças Únicas</p>
        </div>
        <?php endif; ?>
        <?php if ($muito_raros) : ?>
        <div class="hero-divider" aria-hidden="true"></div>
        <div>
          <p class="hero-stat-val hero-stat-val--purple"><?php echo esc_html($muito_raros); ?></p>
          <p class="hero-stat-lbl">Muito Raros</p>
        </div>
        <?php endif; ?>
      </div>

      <div class="hero-ctas animate-fade-in" style="animation-delay:300ms">
        <a href="#colecao" class="btn-primary">
          Ver Coleção
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </a>
        <a href="<?php echo esc_url( hb_wa_link() ); ?>" target="_blank" rel="noopener" class="btn-ghost">
          <?php echo hb_wa_icon(); ?>
          Falar no WhatsApp
        </a>
      </div>
    </div>
  </div>
</section>
<?php endif; ?>

<!-- ═══ COLEÇÃO ═══════════════════════════════════════════════ -->
<section id="colecao" class="products-section">
  <div class="hb-container">

    <!-- Header -->
    <div class="products-header">
      <div>
        <p class="section-label" style="margin-bottom:.25rem">Coleção Disponível</p>
        <p class="products-count" id="products-count">
          <?php echo esc_html($total); ?> <?php echo $total === 1 ? 'item encontrado' : 'itens encontrados'; ?>
        </p>
      </div>
      <p class="products-meta">
        Atualizado em <?php echo date_i18n('F/Y'); ?> · Feira Praça XV
      </p>
    </div>

    <!-- Filtros -->
    <div class="filter-section">
      <!-- Categorias -->
      <div class="filter-row">
        <span class="filter-row-lbl">Categoria</span>
        <button class="filter-pill active"
          data-filter-type="category"
          data-filter-value="Todos">Todos</button>
        <?php foreach ( $filter_cats as $cat ) : ?>
          <button class="filter-pill"
            data-filter-type="category"
            data-filter-value="<?php echo esc_attr($cat->name); ?>">
            <?php echo esc_html($cat->name); ?>
          </button>
        <?php endforeach; ?>
      </div>

      <!-- Décadas -->
      <div class="filter-row">
        <span class="filter-row-lbl">Década</span>
        <button class="filter-pill active"
          data-filter-type="decade"
          data-filter-value="Todas">Todas</button>
        <?php foreach ( $decades as $dec ) : ?>
          <button class="filter-pill"
            data-filter-type="decade"
            data-filter-value="<?php echo esc_attr($dec); ?>">
            <?php echo esc_html($dec); ?>
          </button>
        <?php endforeach; ?>
      </div>
    </div>

    <!-- Grid de produtos -->
    <?php
    $products = new WP_Query([
      'post_status'    => 'publish',
      'posts_per_page' => -1,
      'orderby'        => 'date',
      'order'          => 'DESC',
    ]);
    ?>

    <?php if ( $products->have_posts() ) : ?>
    <div class="hb-grid" id="products-grid">
      <?php while ( $products->have_posts() ) : $products->the_post();
        $pid     = get_the_ID();
        $preco   = get_post_meta($pid,'hb_preco',      true);
        $rar     = get_post_meta($pid,'hb_raridade',   true);
        $decada  = get_post_meta($pid,'hb_decada',     true);
        $marca   = get_post_meta($pid,'hb_marca',      true);
        $origem  = get_post_meta($pid,'hb_origem',     true);
        $acomp   = get_post_meta($pid,'hb_acompanha',  true);
        $historia= get_post_meta($pid,'hb_historia',   true);
        $wa_msg  = get_post_meta($pid,'hb_wa_msg',     true) ?: 'Olá! Tenho interesse no produto: ' . get_the_title() . ' — da HelioBrinquedos';
        $cat_name= hb_primary_category($pid);
        $wa_url  = hb_wa_link($wa_msg);
      ?>
      <article class="product-card"
        data-category="<?php echo esc_attr($cat_name); ?>"
        data-decade="<?php echo esc_attr($decada); ?>">

        <!-- Thumbnail -->
        <a href="<?php the_permalink(); ?>" class="card-thumb" tabindex="-1" aria-hidden="true">
          <?php echo hb_thumb($pid,'hb-card'); ?>
          <?php if ($decada) : ?>
            <span class="card-tag card-tag--decade"><?php echo esc_html($decada); ?></span>
          <?php endif; ?>
          <?php if ($origem) : ?>
            <span class="card-tag card-tag--origin card-tag--<?php echo esc_attr(strtolower($origem)); ?>">
              <?php echo esc_html($origem); ?>
            </span>
          <?php endif; ?>
        </a>

        <!-- Body -->
        <div class="card-body">
          <div class="card-meta-top">
            <?php echo hb_rarity_badge($pid); ?>
            <?php if ($cat_name) : ?>
              <span class="card-category"><?php echo esc_html($cat_name); ?></span>
            <?php endif; ?>
          </div>

          <h2 class="card-title">
            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
          </h2>

          <?php if ($historia) : ?>
            <p class="card-history"><?php echo esc_html($historia); ?></p>
          <?php endif; ?>

          <ul class="card-info">
            <?php if ($marca) : ?>
              <li class="card-info-item">
                <span class="card-dot" aria-hidden="true">▶</span>
                <?php echo esc_html($marca); ?>
              </li>
            <?php endif; ?>
            <?php if ($acomp) : ?>
              <li class="card-info-item full">
                <span class="card-dot" aria-hidden="true">▶</span>
                <?php echo esc_html($acomp); ?>
              </li>
            <?php endif; ?>
          </ul>

          <!-- Footer: preço + CTA -->
          <div class="card-footer">
            <div>
              <p class="card-price-lbl">Preço</p>
              <p class="card-price">
                <?php echo $preco ? 'R$ ' . esc_html($preco) : 'Consulte'; ?>
              </p>
            </div>
            <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="card-cta">
              <?php echo hb_wa_icon(); ?>
              Negociar
            </a>
          </div>
        </div><!-- /.card-body -->
      </article>
      <?php endwhile; wp_reset_postdata(); ?>
    </div><!-- /.hb-grid -->

    <div class="empty-state" style="display:none" aria-live="polite">
      <p class="empty-state-icon">📦</p>
      <p class="empty-state-title">Nenhum item nesta categoria.</p>
      <p class="empty-state-sub">Tente outro filtro ou entre em contato.</p>
    </div>

    <?php else : ?>
    <div class="empty-state">
      <p class="empty-state-icon">📦</p>
      <p class="empty-state-title">Nenhum produto cadastrado ainda.</p>
      <p class="empty-state-sub">Volte em breve ou fale no WhatsApp.</p>
    </div>
    <?php endif; ?>

  </div>
</section>

<?php get_footer(); ?>
