(function () {
  'use strict';

  var filterState = { category: 'Todos', decade: 'Todas' };

  function applyFilters() {
    var cards   = document.querySelectorAll('.product-card[data-category]');
    var visible = 0;

    cards.forEach(function (card) {
      var catOk = filterState.category === 'Todos'  || card.dataset.category === filterState.category;
      var decOk = filterState.decade   === 'Todas'  || card.dataset.decade   === filterState.decade;

      if (catOk && decOk) {
        card.classList.remove('hidden');
        visible++;
      } else {
        card.classList.add('hidden');
      }
    });

    var countEl = document.querySelector('.products-count');
    if (countEl) {
      countEl.textContent = visible + (visible === 1 ? ' item encontrado' : ' itens encontrados');
    }

    var emptyEl = document.querySelector('.empty-state');
    if (emptyEl) {
      emptyEl.style.display = visible === 0 ? 'block' : 'none';
    }
  }

  function bindFilters(type, selector) {
    document.querySelectorAll(selector).forEach(function (pill) {
      pill.addEventListener('click', function () {
        document.querySelectorAll(selector).forEach(function (p) { p.classList.remove('active'); });
        pill.classList.add('active');
        filterState[type] = pill.dataset.filterValue;
        applyFilters();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindFilters('category', '.filter-pill[data-filter-type="category"]');
    bindFilters('decade',   '.filter-pill[data-filter-type="decade"]');

    // Stagger entrance animation for cards
    document.querySelectorAll('.product-card').forEach(function (card, i) {
      card.style.animationDelay = (i * 55) + 'ms';
      card.classList.add('animate-slide-up');
    });

    // Header border on scroll
    var header = document.querySelector('.site-header');
    if (header) {
      window.addEventListener('scroll', function () {
        header.style.borderBottomColor = window.scrollY > 10
          ? 'rgba(44,44,56,0.9)'
          : '';
      }, { passive: true });
    }
  });
})();
