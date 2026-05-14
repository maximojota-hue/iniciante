<?php get_header(); ?>

<section class="products-section">
  <div class="hb-container">
    <div class="products-header" style="margin-bottom:1.5rem">
      <div>
        <p class="section-label" style="margin-bottom:.25rem">Resultado da Busca</p>
        <p class="products-count">
          <?php
            $n = $GLOBALS['wp_query']->found_posts;
            echo esc_html($n) . ' ' . ($n === 1 ? 'item encontrado' : 'itens encontrados') . ' para "' . esc_html(get_search_query()) . '"';
          ?>
        </p>
      </div>
    </div>

    <?php if ( have_posts() ) : ?>
    <div class="hb-grid">
      <?php while ( have_posts() ) : the_post();
        $pid    = get_the_ID();
        $preco  = get_post_meta($pid,'hb_preco',true);
        $decada = get_post_meta($pid,'hb_decada',true);
        $origem = get_post_meta($pid,'hb_origem',true);
        $hist   = get_post_meta($pid,'hb_historia',true);
        $cat    = hb_primary_category($pid);
        $wa_msg = get_post_meta($pid,'hb_wa_msg',true) ?: 'Olá! Tenho interesse em: ' . get_the_title();
        $wa_url = hb_wa_link($wa_msg);
      ?>
      <article class="product-card"
        data-category="<?php echo esc_attr($cat); ?>"
        data-decade="<?php echo esc_attr($decada); ?>">
        <a href="<?php the_permalink(); ?>" class="card-thumb" tabindex="-1">
          <?php echo hb_thumb($pid,'hb-card'); ?>
          <?php if ($decada) : ?><span class="card-tag card-tag--decade"><?php echo esc_html($decada); ?></span><?php endif; ?>
        </a>
        <div class="card-body">
          <div class="card-meta-top"><?php echo hb_rarity_badge($pid); ?></div>
          <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
          <?php if ($hist) : ?><p class="card-history"><?php echo esc_html($hist); ?></p><?php endif; ?>
          <div class="card-footer">
            <div>
              <p class="card-price-lbl">Preço</p>
              <p class="card-price"><?php echo $preco ? 'R$ ' . esc_html($preco) : 'Consulte'; ?></p>
            </div>
            <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="card-cta">
              <?php echo hb_wa_icon(); ?> Negociar
            </a>
          </div>
        </div>
      </article>
      <?php endwhile; ?>
    </div>
    <?php else : ?>
    <div class="empty-state">
      <p class="empty-state-icon">🔍</p>
      <p class="empty-state-title">Nenhum resultado encontrado.</p>
      <p class="empty-state-sub">Tente termos diferentes ou <a href="<?php echo esc_url(home_url('/')); ?>" style="color:var(--hb-orange)">veja toda a coleção</a>.</p>
    </div>
    <?php endif; ?>

  </div>
</section>

<?php get_footer(); ?>
