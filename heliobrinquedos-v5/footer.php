<footer class="site-footer">
  <div class="hb-container">
    <div class="footer-inner">
      <div class="footer-grid">

        <!-- Brand -->
        <div>
          <div class="footer-brand-row">
            <span class="footer-brand-icon" aria-hidden="true">🧸</span>
            <p class="footer-brand-name">HELIO<span class="accent">BRINQUEDOS</span></p>
          </div>
          <p class="footer-brand-desc">
            Raridades e colecionáveis dos anos 70 ao 2000.
            Cada peça selecionada com cuidado e história garantida.
          </p>
        </div>

        <!-- Feira -->
        <div id="feira">
          <h4 class="footer-col-title">Feira Presencial</h4>
          <ul class="footer-info-list">
            <li class="footer-info-item">
              <span class="footer-info-icon" aria-hidden="true">📍</span>
              <?php echo esc_html( get_theme_mod('hb_feira_local','Feira de Antiguidades da Praça XV — Rio de Janeiro/RJ') ); ?>
            </li>
            <li class="footer-info-item">
              <span class="footer-info-icon" aria-hidden="true">🗓️</span>
              <?php echo esc_html( get_theme_mod('hb_feira_horario','Sábados das 8h às 15h') ); ?>
            </li>
            <li class="footer-info-item">
              <span class="footer-info-icon" aria-hidden="true">📲</span>
              <?php
                $num = get_theme_mod('hb_whatsapp','5521981536073');
                $fmt = preg_replace('/^55(\d{2})(\d{5})(\d{4})$/', '($1) $2-$3', preg_replace('/\D/','',$num));
                echo esc_html($fmt);
              ?>
            </li>
          </ul>
        </div>

        <!-- Contato -->
        <div id="sobre">
          <h4 class="footer-col-title">Contato</h4>
          <p class="footer-contact-desc">
            Atendimento via WhatsApp. Negociamos envio para todo o Brasil.
          </p>
          <a href="<?php echo esc_url( hb_wa_link() ); ?>" target="_blank" rel="noopener"
             class="btn-wa-green">
            <?php echo hb_wa_icon(); ?>
            Enviar Mensagem
          </a>
        </div>

      </div><!-- /.footer-grid -->

      <div class="footer-bottom">
        <p>© <?php echo date('Y'); ?> HelioBrinquedos · <?php bloginfo('url'); ?></p>
        <p>Raridades dos anos 70 ao 2000 · Rio de Janeiro</p>
      </div>
    </div>
  </div>
</footer>

<!-- WhatsApp float -->
<a href="<?php echo esc_url( hb_wa_link() ); ?>" target="_blank" rel="noopener"
   class="whatsapp-float" title="Falar no WhatsApp" aria-label="Abrir WhatsApp">
  <?php echo hb_wa_icon(); ?>
</a>

<?php wp_footer(); ?>
</body>
</html>
