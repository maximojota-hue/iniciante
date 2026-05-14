<?php get_header(); ?>

<?php while ( have_posts() ) : the_post();
  $pid     = get_the_ID();
  $img     = get_the_post_thumbnail_url($pid,'hb-card') ?: get_the_post_thumbnail_url($pid,'full');
  $preco   = get_post_meta($pid,'hb_preco',      true);
  $rar     = get_post_meta($pid,'hb_raridade',   true);
  $conserv = get_post_meta($pid,'hb_conservacao',true);
  $decada  = get_post_meta($pid,'hb_decada',     true);
  $marca   = get_post_meta($pid,'hb_marca',      true);
  $origem  = get_post_meta($pid,'hb_origem',     true);
  $acomp   = get_post_meta($pid,'hb_acompanha',  true);
  $historia= get_post_meta($pid,'hb_historia',   true);
  $wa_msg  = get_post_meta($pid,'hb_wa_msg',     true) ?: 'Olá! Tenho interesse no produto: ' . get_the_title() . ' — da HelioBrinquedos';
  $wa_url  = hb_wa_link($wa_msg);
?>

<div class="single-wrap">
  <div class="hb-container">

    <?php hb_breadcrumb(); ?>

    <!-- Grid principal: imagem + info -->
    <div class="single-grid">

      <!-- Imagem -->
      <div class="single-image">
        <?php if ($img) : ?>
          <img src="<?php echo esc_url($img); ?>" alt="<?php the_title_attribute(); ?>" loading="eager">
        <?php else : ?>
          <?php echo hb_thumb($pid,'hb-card'); ?>
        <?php endif; ?>
      </div>

      <!-- Informações -->
      <div>
        <!-- Badges -->
        <div class="single-badges">
          <?php
            $terms = get_the_terms($pid,'category');
            if ($terms) foreach ($terms as $t) :
          ?>
            <a href="<?php echo esc_url(get_term_link($t)); ?>" class="single-cat-pill">
              <?php echo esc_html($t->name); ?>
            </a>
          <?php endforeach; ?>
          <?php echo hb_rarity_badge($pid); ?>
        </div>

        <h1 class="single-title"><?php the_title(); ?></h1>

        <!-- Urgência para raros -->
        <?php if ($rar && in_array($rar,['Muito Raro','Peça Única'])) : ?>
          <div class="urgency-bar">
            ⚠️
            <?php echo $rar === 'Peça Única'
              ? 'Peça única — quando acabar, não tem mais!'
              : 'Item raro — disponibilidade limitada!'; ?>
          </div>
        <?php endif; ?>

        <!-- História -->
        <?php if ($historia) : ?>
          <div class="single-history">
            <?php echo nl2br(esc_html($historia)); ?>
          </div>
        <?php endif; ?>

        <!-- Ficha técnica -->
        <div class="single-details">
          <p class="single-details-title">Ficha Técnica</p>
          <?php
            echo hb_spec_row('Raridade',     $rar);
            echo hb_spec_row('Conservação',  $conserv);
            echo hb_spec_row('Década',       $decada);
            echo hb_spec_row('Marca',        $marca);
            echo hb_spec_row('Origem',       $origem);
            echo hb_spec_row('Acompanha',    $acomp);
          ?>
        </div>

        <!-- Preço -->
        <div class="single-price-box">
          <div>
            <p class="single-price-lbl">Preço</p>
            <p class="single-price">
              <?php echo $preco ? 'R$ ' . esc_html($preco) : 'Sob Consulta'; ?>
            </p>
          </div>
          <?php if ($decada) : ?>
            <span class="card-tag card-tag--decade"><?php echo esc_html($decada); ?></span>
          <?php endif; ?>
        </div>

        <!-- CTAs -->
        <div class="single-ctas">
          <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="btn-primary">
            <?php echo hb_wa_icon(); ?>
            <?php echo $preco
              ? 'Quero comprar — R$ ' . esc_html($preco)
              : 'Tenho interesse — falar no WhatsApp'; ?>
          </a>
          <a href="<?php echo esc_url(hb_wa_link('Olá! Tenho uma dúvida sobre o produto: ' . get_the_title())); ?>"
             target="_blank" rel="noopener" class="btn-ghost">
            <?php echo hb_wa_icon(); ?>
            Fazer uma pergunta
          </a>
        </div>
      </div><!-- /info -->
    </div><!-- /.single-grid -->

    <!-- Conteúdo do post + sidebar -->
    <div class="single-layout">

      <main id="primary">
        <?php if ( get_the_content() ) : ?>
          <div class="single-content">
            <div class="entry-content">
              <?php the_content(); ?>
            </div>
          </div>
        <?php endif; ?>
      </main>

      <aside class="sidebar">
        <!-- CTA WhatsApp sidebar -->
        <div class="cta-wa-box">
          <div class="cta-icon" aria-hidden="true">💬</div>
          <h3>Quer garantir este item?</h3>
          <p>Fale com o Hélio agora e garanta antes que acabe!</p>
          <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="btn-wa-green">
            <?php echo hb_wa_icon(); ?>
            Falar no WhatsApp
          </a>
        </div>

        <!-- Mais raridades -->
        <div class="widget">
          <h3 class="widget-title">⭐ Mais Raridades</h3>
          <ul class="widget-recent">
            <?php $rec = new WP_Query(['posts_per_page'=>5,'post__not_in'=>[$pid],'orderby'=>'rand']);
              while ($rec->have_posts()) : $rec->the_post();
                $rprice = get_post_meta(get_the_ID(),'hb_preco',true);
            ?>
              <li>
                <div class="wthumb">
                  <a href="<?php the_permalink(); ?>"><?php echo hb_thumb(get_the_ID(),'hb-thumb'); ?></a>
                </div>
                <div>
                  <div class="wtitle"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></div>
                  <div class="wprice"><?php echo $rprice ? 'R$ ' . esc_html($rprice) : 'Consulte'; ?></div>
                </div>
              </li>
            <?php endwhile; wp_reset_postdata(); ?>
          </ul>
        </div>

        <!-- Categorias -->
        <div class="widget">
          <h3 class="widget-title">📦 Categorias</h3>
          <ul class="widget-cats">
            <?php wp_list_categories(['title_li'=>'','orderby'=>'count','order'=>'DESC','number'=>8]); ?>
          </ul>
        </div>

        <!-- Feira -->
        <div class="widget">
          <h3 class="widget-title">🏪 Feira Presencial</h3>
          <ul class="footer-info-list">
            <li class="footer-info-item">
              <span class="footer-info-icon">📍</span>
              <?php echo esc_html(get_theme_mod('hb_feira_local','Feira de Antiguidades da Praça XV')); ?>
            </li>
            <li class="footer-info-item">
              <span class="footer-info-icon">🕐</span>
              <?php echo esc_html(get_theme_mod('hb_feira_horario','Sábados das 8h às 15h')); ?>
            </li>
          </ul>
        </div>
      </aside>

    </div><!-- /.single-layout -->

  </div><!-- /.hb-container -->
</div><!-- /.single-wrap -->

<!-- Produtos relacionados -->
<?php
  $rcats = wp_get_post_categories($pid);
  if ($rcats) :
    $rel = new WP_Query(['category__in'=>$rcats,'posts_per_page'=>4,'post__not_in'=>[$pid],'orderby'=>'rand']);
    if ($rel->have_posts()) :
?>
<section class="related-section">
  <div class="hb-container">
    <h2 class="related-title">Você também pode <span class="accent">gostar</span></h2>
    <div class="hb-grid">
      <?php while ($rel->have_posts()) : $rel->the_post();
        $rpid   = get_the_ID();
        $rpreco = get_post_meta($rpid,'hb_preco',true);
        $rdec   = get_post_meta($rpid,'hb_decada',true);
        $rorig  = get_post_meta($rpid,'hb_origem',true);
        $rhist  = get_post_meta($rpid,'hb_historia',true);
        $rcat   = hb_primary_category($rpid);
        $rwa    = get_post_meta($rpid,'hb_wa_msg',true) ?: 'Olá! Tenho interesse em: ' . get_the_title() . ' — da HelioBrinquedos';
      ?>
      <article class="product-card"
        data-category="<?php echo esc_attr($rcat); ?>"
        data-decade="<?php echo esc_attr($rdec); ?>">
        <a href="<?php the_permalink(); ?>" class="card-thumb" tabindex="-1">
          <?php echo hb_thumb($rpid,'hb-card'); ?>
          <?php if ($rdec) : ?>
            <span class="card-tag card-tag--decade"><?php echo esc_html($rdec); ?></span>
          <?php endif; ?>
          <?php if ($rorig) : ?>
            <span class="card-tag card-tag--origin card-tag--<?php echo esc_attr(strtolower($rorig)); ?>">
              <?php echo esc_html($rorig); ?>
            </span>
          <?php endif; ?>
        </a>
        <div class="card-body">
          <div class="card-meta-top">
            <?php echo hb_rarity_badge($rpid); ?>
            <?php if ($rcat) : ?><span class="card-category"><?php echo esc_html($rcat); ?></span><?php endif; ?>
          </div>
          <h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
          <?php if ($rhist) : ?><p class="card-history"><?php echo esc_html($rhist); ?></p><?php endif; ?>
          <div class="card-footer">
            <div>
              <p class="card-price-lbl">Preço</p>
              <p class="card-price"><?php echo $rpreco ? 'R$ ' . esc_html($rpreco) : 'Consulte'; ?></p>
            </div>
            <a href="<?php echo esc_url(hb_wa_link($rwa)); ?>" target="_blank" rel="noopener" class="card-cta">
              <?php echo hb_wa_icon(); ?>
              Negociar
            </a>
          </div>
        </div>
      </article>
      <?php endwhile; wp_reset_postdata(); ?>
    </div>
  </div>
</section>
<?php endif; endif; ?>

<?php endwhile; ?>
<?php get_footer(); ?>
