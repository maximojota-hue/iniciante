<?php get_header(); ?>

<?php
$all_q = new WP_Query(['post_status'=>'publish','posts_per_page'=>-1,'fields'=>'ids']);
$total = $all_q->found_posts;
wp_reset_postdata();

$product_query = new WP_Query([
  'post_status'    => 'publish',
  'posts_per_page' => 12,
  'orderby'        => 'date',
  'order'          => 'DESC',
  'meta_query'     => [
    'relation' => 'OR',
    ['key'=>'hb_raridade', 'compare'=>'EXISTS'],
    ['key'=>'hb_preco', 'compare'=>'EXISTS'],
    ['key'=>'hb_marca', 'compare'=>'EXISTS'],
  ],
]);

$editorial_query = new WP_Query([
  'post_status'    => 'publish',
  'posts_per_page' => 6,
  'orderby'        => 'date',
  'order'          => 'DESC',
  'category_name'  => 'cultura-retro,anos-70,anos-80,anos-90,anos-2000,guias-de-colecionador,tokusatsu,filmes-e-series,desenhos-nostalgicos',
]);

$filter_cats = get_categories(['hide_empty'=>true,'exclude'=>get_option('default_category')]);
$decades = ['Anos 70','Anos 80','Anos 90','Anos 2000'];
?>

<?php if ( is_home() || is_front_page() ) : ?>
<section class="hero-section">
  <div class="hero-grid-bg" aria-hidden="true"></div>
  <div class="hero-glow" aria-hidden="true"></div>
  <div class="hero-glow-2" aria-hidden="true"></div>

  <div class="hb-container">
    <div class="hero-content">
      <p class="section-label animate-fade-in" style="margin-bottom:1.25rem">
        Acervo vintage & cultura retro
      </p>

      <h1 class="hero-title animate-slide-up">
        HELIO<br>
        <span class="accent">BRINQUEDOS</span>
      </h1>

      <p class="hero-subtitle animate-fade-in" style="animation-delay:150ms">
        Brinquedos antigos, relogios raros, games classicos e action figures com historia.
        Um acervo para comprar, pesquisar e reviver as decadas que marcaram geracoes.
      </p>

      <div class="hero-stats animate-fade-in" style="animation-delay:200ms">
        <div>
          <p class="hero-stat-val hero-stat-val--orange"><?php echo esc_html($total); ?></p>
          <p class="hero-stat-lbl">Publicacoes</p>
        </div>
        <div class="hero-divider" aria-hidden="true"></div>
        <div>
          <p class="hero-stat-val hero-stat-val--gold">70-00</p>
          <p class="hero-stat-lbl">Decadas</p>
        </div>
      </div>

      <div class="hero-ctas animate-fade-in" style="animation-delay:300ms">
        <a href="#acervo" class="btn-primary">Ver acervo</a>
        <a href="#cultura-retro" class="btn-ghost">Ler cultura retro</a>
      </div>
    </div>
  </div>
</section>
<?php endif; ?>

<section id="acervo" class="products-section">
  <div class="hb-container">
    <div class="products-header">
      <div>
        <p class="section-label" style="margin-bottom:.25rem">Acervo a venda</p>
        <p class="products-count" id="products-count">
          <?php echo esc_html($product_query->found_posts); ?> <?php echo $product_query->found_posts === 1 ? 'item encontrado' : 'itens encontrados'; ?>
        </p>
      </div>
      <p class="products-meta">Garimpos vintage, itens raros e consulta por WhatsApp</p>
    </div>

    <div class="filter-section">
      <div class="filter-row">
        <span class="filter-row-lbl">Categoria</span>
        <button class="filter-pill active" data-filter-type="category" data-filter-value="Todos">Todos</button>
        <?php foreach ( $filter_cats as $cat ) : ?>
          <button class="filter-pill" data-filter-type="category" data-filter-value="<?php echo esc_attr($cat->name); ?>">
            <?php echo esc_html($cat->name); ?>
          </button>
        <?php endforeach; ?>
      </div>

      <div class="filter-row">
        <span class="filter-row-lbl">Decada</span>
        <button class="filter-pill active" data-filter-type="decade" data-filter-value="Todas">Todas</button>
        <?php foreach ( $decades as $dec ) : ?>
          <button class="filter-pill" data-filter-type="decade" data-filter-value="<?php echo esc_attr($dec); ?>">
            <?php echo esc_html($dec); ?>
          </button>
        <?php endforeach; ?>
      </div>
    </div>

    <?php if ( $product_query->have_posts() ) : ?>
    <div class="hb-grid" id="products-grid">
      <?php while ( $product_query->have_posts() ) : $product_query->the_post();
        $pid      = get_the_ID();
        $preco    = get_post_meta($pid,'hb_preco',true);
        $decada   = get_post_meta($pid,'hb_decada',true);
        $marca    = get_post_meta($pid,'hb_marca',true);
        $origem   = get_post_meta($pid,'hb_origem',true);
        $acomp    = get_post_meta($pid,'hb_acompanha',true);
        $historia = get_post_meta($pid,'hb_historia',true);
        $wa_msg   = get_post_meta($pid,'hb_wa_msg',true) ?: 'Ola! Tenho interesse no produto: ' . get_the_title() . ' - da HelioBrinquedos';
        $cat_name = hb_primary_category($pid);
        $wa_url   = hb_wa_link($wa_msg);
      ?>
      <article class="product-card" data-category="<?php echo esc_attr($cat_name); ?>" data-decade="<?php echo esc_attr($decada); ?>">
        <a href="<?php the_permalink(); ?>" class="card-thumb" tabindex="-1" aria-hidden="true">
          <?php echo hb_thumb($pid,'hb-card'); ?>
          <?php if ($decada) : ?><span class="card-tag card-tag--decade"><?php echo esc_html($decada); ?></span><?php endif; ?>
          <?php if ($origem) : ?>
            <span class="card-tag card-tag--origin card-tag--<?php echo esc_attr(strtolower($origem)); ?>"><?php echo esc_html($origem); ?></span>
          <?php endif; ?>
        </a>

        <div class="card-body">
          <div class="card-meta-top">
            <?php echo hb_rarity_badge($pid); ?>
            <?php if ($cat_name) : ?><span class="card-category"><?php echo esc_html($cat_name); ?></span><?php endif; ?>
          </div>
          <h2 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
          <?php if ($historia) : ?><p class="card-history"><?php echo esc_html($historia); ?></p><?php endif; ?>
          <ul class="card-info">
            <?php if ($marca) : ?><li class="card-info-item"><span class="card-dot" aria-hidden="true">></span><?php echo esc_html($marca); ?></li><?php endif; ?>
            <?php if ($acomp) : ?><li class="card-info-item full"><span class="card-dot" aria-hidden="true">></span><?php echo esc_html($acomp); ?></li><?php endif; ?>
          </ul>
          <div class="card-footer">
            <div>
              <p class="card-price-lbl">Preco</p>
              <p class="card-price"><?php echo $preco ? 'R$ ' . esc_html($preco) : 'Consulte'; ?></p>
            </div>
            <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="card-cta">
              <?php echo hb_wa_icon(); ?>
              Negociar
            </a>
          </div>
        </div>
      </article>
      <?php endwhile; wp_reset_postdata(); ?>
    </div>

    <div class="empty-state" style="display:none" aria-live="polite">
      <p class="empty-state-icon">HB</p>
      <p class="empty-state-title">Nenhum item nesta selecao.</p>
      <p class="empty-state-sub">Tente outro filtro ou chame no WhatsApp.</p>
    </div>
    <?php else : ?>
    <div class="empty-state">
      <p class="empty-state-icon">HB</p>
      <p class="empty-state-title">Nenhum item cadastrado ainda.</p>
      <p class="empty-state-sub">Publique os primeiros rascunhos pelo app Helio.</p>
    </div>
    <?php endif; ?>
  </div>
</section>

<section id="cultura-retro" class="editorial-section">
  <div class="hb-container">
    <div class="products-header">
      <div>
        <p class="section-label" style="margin-bottom:.25rem">Cultura retro</p>
        <h2 class="related-title">Historias, guias e nostalgia</h2>
      </div>
      <p class="products-meta">Conteudo para SEO, AdSense e autoridade</p>
    </div>

    <?php if ( $editorial_query->have_posts() ) : ?>
      <div class="article-grid">
        <?php while ( $editorial_query->have_posts() ) : $editorial_query->the_post(); ?>
          <article class="article-card">
            <a href="<?php the_permalink(); ?>" class="article-card-thumb">
              <?php if ( has_post_thumbnail() ) : the_post_thumbnail('hb-card'); else : ?><span>Cultura Retro</span><?php endif; ?>
            </a>
            <div class="article-card-body">
              <p class="section-label"><?php echo esc_html( hb_primary_category( get_the_ID() ) ); ?></p>
              <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
              <p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 22, '...' ) ); ?></p>
            </div>
          </article>
        <?php endwhile; wp_reset_postdata(); ?>
      </div>
    <?php else : ?>
      <div class="retro-clusters">
        <a href="<?php echo esc_url( home_url('/category/anos-80/') ); ?>">Anos 80</a>
        <a href="<?php echo esc_url( home_url('/category/games-classicos/') ); ?>">Games classicos</a>
        <a href="<?php echo esc_url( home_url('/category/brinquedos-antigos/') ); ?>">Brinquedos antigos</a>
        <a href="<?php echo esc_url( home_url('/category/guias-de-colecionador/') ); ?>">Guias de colecionador</a>
      </div>
    <?php endif; ?>
  </div>
</section>

<?php get_footer(); ?>
