<?php get_header(); ?>

<?php while ( have_posts() ) : the_post();
  $pid = get_the_ID();
?>

<?php if ( hb_is_editorial_post( $pid ) ) : ?>

<article class="article-wrap">
  <div class="hb-container article-container">
    <?php hb_breadcrumb(); ?>

    <header class="article-hero">
      <p class="section-label">Cultura Retro</p>
      <h1 class="article-title"><?php the_title(); ?></h1>
      <div class="article-meta">
        <span><?php echo esc_html( get_the_date() ); ?></span>
        <span><?php echo esc_html( get_the_author() ); ?></span>
        <?php $cats = get_the_category(); if ( $cats ) : ?>
          <span><?php echo esc_html( $cats[0]->name ); ?></span>
        <?php endif; ?>
      </div>
      <?php if ( has_excerpt() ) : ?>
        <p class="article-lead"><?php echo esc_html( get_the_excerpt() ); ?></p>
      <?php endif; ?>
    </header>

    <?php if ( has_post_thumbnail() ) : ?>
      <figure class="article-cover">
        <?php the_post_thumbnail( 'hb-hero', ['loading'=>'eager'] ); ?>
      </figure>
    <?php endif; ?>

    <div class="article-layout">
      <main class="article-content entry-content">
        <?php the_content(); ?>
      </main>

      <aside class="sidebar article-sidebar">
        <div class="cta-wa-box">
          <div class="cta-icon" aria-hidden="true">HB</div>
          <h3>Garimpo de raridades</h3>
          <p>Encontrou uma memoria boa por aqui? Veja tambem os itens reais do acervo.</p>
          <a href="<?php echo esc_url( home_url('/#colecao') ); ?>" class="btn-primary">Ver acervo</a>
        </div>

        <div class="widget">
          <h3 class="widget-title">Guias e nostalgia</h3>
          <ul class="widget-recent">
            <?php
              $editorial = new WP_Query([
                'posts_per_page' => 5,
                'post__not_in'   => [$pid],
                'category_name'  => 'cultura-retro,anos-70,anos-80,anos-90,anos-2000,guias-de-colecionador',
              ]);
              while ( $editorial->have_posts() ) : $editorial->the_post();
            ?>
              <li>
                <div class="wtitle"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></div>
              </li>
            <?php endwhile; wp_reset_postdata(); ?>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</article>

<?php else :
  $img      = get_the_post_thumbnail_url($pid,'hb-card') ?: get_the_post_thumbnail_url($pid,'full');
  $preco    = get_post_meta($pid,'hb_preco',       true);
  $rar      = get_post_meta($pid,'hb_raridade',    true);
  $conserv  = get_post_meta($pid,'hb_conservacao', true);
  $decada   = get_post_meta($pid,'hb_decada',      true);
  $marca    = get_post_meta($pid,'hb_marca',       true);
  $modelo   = get_post_meta($pid,'hb_modelo',      true);
  $tipo     = get_post_meta($pid,'hb_tipo',        true);
  $origem   = get_post_meta($pid,'hb_origem',      true);
  $acomp    = get_post_meta($pid,'hb_acompanha',   true);
  $historia = get_post_meta($pid,'hb_historia',    true);
  $wa_msg   = get_post_meta($pid,'hb_wa_msg',      true) ?: 'Ola! Tenho interesse no produto: ' . get_the_title() . ' - da HelioBrinquedos';
  $wa_url   = hb_wa_link($wa_msg);
?>

<div class="single-wrap">
  <div class="hb-container">
    <?php hb_breadcrumb(); ?>

    <div class="single-grid">
      <div class="single-image">
        <?php if ($img) : ?>
          <img src="<?php echo esc_url($img); ?>" alt="<?php the_title_attribute(); ?>" loading="eager">
        <?php else : ?>
          <?php echo hb_thumb($pid,'hb-card'); ?>
        <?php endif; ?>
      </div>

      <div>
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

        <?php if ($rar && in_array($rar,['Muito Raro','Peca Unica','Peça Única'], true)) : ?>
          <div class="urgency-bar">Item raro com disponibilidade limitada.</div>
        <?php endif; ?>

        <?php if ($historia) : ?>
          <div class="single-history"><?php echo nl2br(esc_html($historia)); ?></div>
        <?php endif; ?>

        <div class="single-details">
          <p class="single-details-title">Ficha Tecnica</p>
          <?php
            echo hb_spec_row('Tipo',         $tipo);
            echo hb_spec_row('Raridade',     $rar);
            echo hb_spec_row('Conservacao',  $conserv);
            echo hb_spec_row('Decada',       $decada);
            echo hb_spec_row('Marca',        $marca);
            echo hb_spec_row('Modelo',       $modelo);
            echo hb_spec_row('Origem',       $origem);
            echo hb_spec_row('Acompanha',    $acomp);
          ?>
        </div>

        <div class="single-price-box">
          <div>
            <p class="single-price-lbl">Preco</p>
            <p class="single-price"><?php echo $preco ? 'R$ ' . esc_html($preco) : 'Sob consulta'; ?></p>
          </div>
          <?php if ($decada) : ?><span class="card-tag card-tag--decade"><?php echo esc_html($decada); ?></span><?php endif; ?>
        </div>

        <div class="single-ctas">
          <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="btn-primary">
            <?php echo hb_wa_icon(); ?>
            <?php echo $preco ? 'Quero comprar - R$ ' . esc_html($preco) : 'Tenho interesse - WhatsApp'; ?>
          </a>
          <a href="<?php echo esc_url(hb_wa_link('Ola! Tenho uma duvida sobre o produto: ' . get_the_title())); ?>"
             target="_blank" rel="noopener" class="btn-ghost">
            <?php echo hb_wa_icon(); ?>
            Fazer pergunta
          </a>
        </div>
      </div>
    </div>

    <div class="single-layout">
      <main id="primary">
        <?php if ( get_the_content() ) : ?>
          <div class="single-content">
            <div class="entry-content"><?php the_content(); ?></div>
          </div>
        <?php endif; ?>
      </main>

      <aside class="sidebar">
        <div class="cta-wa-box">
          <div class="cta-icon" aria-hidden="true">WA</div>
          <h3>Quer garantir este item?</h3>
          <p>Fale pelo WhatsApp e confirme disponibilidade, fotos extras e forma de envio.</p>
          <a href="<?php echo esc_url($wa_url); ?>" target="_blank" rel="noopener" class="btn-wa-green">
            <?php echo hb_wa_icon(); ?>
            Falar no WhatsApp
          </a>
        </div>

        <div class="widget">
          <h3 class="widget-title">Mais raridades</h3>
          <ul class="widget-recent">
            <?php $rec = new WP_Query(['posts_per_page'=>5,'post__not_in'=>[$pid],'orderby'=>'rand']);
              while ($rec->have_posts()) : $rec->the_post();
                if ( ! hb_is_product_post( get_the_ID() ) ) continue;
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
      </aside>
    </div>
  </div>
</div>

<?php endif; ?>

<?php endwhile; ?>
<?php get_footer(); ?>
