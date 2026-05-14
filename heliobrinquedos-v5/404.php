<?php get_header(); ?>

<div class="not-found">
  <div class="hb-container" style="text-align:center">
    <p class="not-found-code" aria-hidden="true">404</p>
    <h1 class="not-found-title">Página não encontrada</h1>
    <p class="not-found-sub">O item que você procura pode ter saído da coleção.</p>
    <div style="display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap;margin-top:2rem">
      <a href="<?php echo esc_url(home_url('/')); ?>" class="btn-primary">Ver Coleção</a>
      <a href="<?php echo esc_url(hb_wa_link()); ?>" target="_blank" rel="noopener" class="btn-ghost">
        <?php echo hb_wa_icon(); ?> Falar no WhatsApp
      </a>
    </div>
  </div>
</div>

<?php get_footer(); ?>
