<?php if ( post_password_required() ) return; ?>
<?php if ( have_comments() ) : ?>
  <h3 style="font-family:var(--font-display);margin-bottom:1rem;font-size:1rem">
    <?php comments_number('Nenhum comentário','Um comentário','% comentários'); ?>
  </h3>
  <ol class="comment-list" style="list-style:none;display:flex;flex-direction:column;gap:1rem">
    <?php wp_list_comments(['style'=>'ol','short_ping'=>true]); ?>
  </ol>
<?php endif; ?>
<?php comment_form(['label_submit'=>'Enviar','title_reply'=>'Deixe um comentário']); ?>
