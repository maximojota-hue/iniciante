<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
  <div class="hb-container">
    <div class="header-inner">

      <a href="<?php echo esc_url( home_url('/') ); ?>" class="site-logo" aria-label="HelioBrinquedos - inicio">
        <span class="site-logo-icon" aria-hidden="true">HB</span>
        <div class="site-logo-text">
          <p class="site-logo-name">HELIO<span class="accent">BRINQUEDOS</span></p>
          <p class="site-logo-tag">Acervo vintage & cultura retro</p>
        </div>
      </a>

      <nav class="header-nav" aria-label="Menu principal">
        <a href="<?php echo esc_url( home_url('/#acervo') ); ?>">Acervo</a>
        <a href="<?php echo esc_url( home_url('/#cultura-retro') ); ?>">Cultura Retro</a>
        <a href="<?php echo esc_url( home_url('/category/guias-de-colecionador/') ); ?>">Guias</a>
        <a href="<?php echo esc_url( home_url('/#sobre') ); ?>">Contato</a>
      </nav>

      <a href="<?php echo esc_url( hb_wa_link() ); ?>" target="_blank" rel="noopener" class="btn-primary header-wa">
        <?php echo hb_wa_icon(); ?>
        <span class="txt-sm">(21) 98153-6073</span>
        <span class="txt-lg">WhatsApp</span>
      </a>

    </div>
  </div>
</header>
