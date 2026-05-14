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

      <!-- Logo -->
      <a href="<?php echo esc_url( home_url('/') ); ?>" class="site-logo" aria-label="HelioBrinquedos — início">
        <span class="site-logo-icon" aria-hidden="true">🧸</span>
        <div class="site-logo-text">
          <p class="site-logo-name">HELIO<span class="accent">BRINQUEDOS</span></p>
          <p class="site-logo-tag">Raridades &amp; Colecionáveis</p>
        </div>
      </a>

      <!-- Nav desktop -->
      <nav class="header-nav" aria-label="Menu principal">
        <a href="<?php echo esc_url( home_url('/#colecao') ); ?>">Coleção</a>
        <a href="<?php echo esc_url( home_url('/#feira') ); ?>">Feira Presencial</a>
        <a href="<?php echo esc_url( home_url('/#sobre') ); ?>">Sobre</a>
      </nav>

      <!-- WhatsApp CTA -->
      <a href="<?php echo esc_url( hb_wa_link() ); ?>" target="_blank" rel="noopener"
         class="btn-primary header-wa">
        <?php echo hb_wa_icon(); ?>
        <span class="txt-sm">(21) 98153-6073</span>
        <span class="txt-lg">WhatsApp</span>
      </a>

    </div>
  </div>
</header>
