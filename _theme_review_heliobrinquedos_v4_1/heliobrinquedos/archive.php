<?php get_header(); ?>

<section class="archive-header">
  <div class="hb-container">
    <?php hb_breadcrumb(); ?>
    <h1 class="archive-title" style="margin-top:1rem"><?php single_cat_title(); ?></h1>
    <?php if ( category_description() ) : ?>
      <p class="archive-desc"><?php echo category_description(); ?></p>
    <?php endif; ?>
  </div>
</section>

<section class="products-section" style="padding-top:1rem">
  <div class="hb-container">
    <div class="products-header">
      <p class="products-count" id="products-count">
        <?php
          global $wp_query;
          $n = $wp_query->found_posts;
          echo esc_html($n) . ' ' . ( $n === 1 ? 'item encontrado' : 'itens encontrados' );
        ?>
      </p>
    </div>

    <?php if ( have_posts() ) : ?>
    <div class="hb-grid">
      <?php while ( have_posts() ) : the_post();
        $pid     = get_the_ID();
        $preco   = get_post_meta($pid,'hb_preco',true);
        $decada  = get_post_meta($pid,'hb_decada',true);
        $origem  = get_post_meta($pid,'hb_origem',true);
        $acomp   = get_post_meta($pid,'hb_acompanha',true);
        $historia= get_post_meta($pid,'hb_historia',true);
        $cat_name= hb_primary_category($pid);
        $wa_msg  = get_post_meta($pid,'hb_wa_msg',true) ?: 'Olá! Tenho interesse em: ' . get_the_title() . ' — da HelioBrinquedos';
        $wa_url  = hb_wa_link($wa_msg);
      ?>
      <article class="product-card"
        data-category="<?php echo esc_attr($cat_name); ?>"
        data-decade="<?php echo esc_attr($decada); ?>">
        <a href="<?php the_permalink(); ?>" class="card-thumb" tabindex="-1">
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
        <div class="card-body">
          <div class="card-meta-top">
            <?php echo hb_rarity_badge($pid); ?>
            <?php if ($cat_name) : ?><span class="card-category"><?php echo esc_html($cat_name); ?></span><?php endif; ?>
          </div>
          <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
          <?php if ($historia) : ?><p class="card-history"><?php echo esc_html($historia); ?></p><?php endif; ?>
          <?php if ($acomp) : ?>
            <ul class="card-info">
              <li class="card-info-item full">
                <span class="card-dot" aria-hidden="true">▶</span><?php echo esc_html($acomp); ?>
              </li>
            </ul>
          <?php endif; ?>
          <div class="card-footer">
            <div>
              <p class="card-price-lbl">Preço</p>
              <p class="card-price"><?php echo $preco ? 'R$ ' . esc_html($preco) : 'Consulte'; ?></p>
            </div>
            <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="card-cta">
              <?php echo hb_wa_icon(); ?>
              Negociar
            </a>
          </div>
        </div>
      </article>
      <?php endwhile; ?>
    </div>
    <?php else : ?>
    <div class="empty-state">
      <p class="empty-state-icon">📦</p>
      <p class="empty-state-title">Nenhum produto nesta categoria.</p>
      <p class="empty-state-sub"><a href="<?php echo esc_url(home_url('/')); ?>" style="color:var(--hb-orange)">Ver todos os itens</a></p>
    </div>
    <?php endif; ?>

    <div style="text-align:center;margin-top:2.5rem">
      <?php
        the_posts_pagination([
          'mid_size'           => 2,
          'prev_text'          => '← Anterior',
          'next_text'          => 'Próxima →',
          'before_page_number' => '<span>',
          'after_page_number'  => '</span>',
        ]);
      ?>
    </div>

  </div>
</section>

<?php get_footer(); ?>
