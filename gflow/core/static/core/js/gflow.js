// G-Flow client JS
(function(){
  // Theme toggle (cookie-only fallback for anonymous, server-saved when logged-in)
  const root = document.documentElement;
  const saved = getCookie('gflow_theme') || 'light';
  root.setAttribute('data-theme', saved);

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }
  function setCookie(name, value, days) {
    const d = new Date(); d.setTime(d.getTime() + days*24*60*60*1000);
    document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax';
  }

  document.addEventListener('click', function(e){
    const t = e.target.closest('[data-theme-toggle]');
    if (!t) return;
    e.preventDefault();
    const cur = root.getAttribute('data-theme') || 'light';
    const next = cur === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', next);
    setCookie('gflow_theme', next, 365);
    // If logged-in, also persist server-side
    const url = t.getAttribute('href');
    if (url) { fetch(url, {method:'GET', credentials:'same-origin'}).catch(()=>{}); }
    updateThemeIcon(next);
  });

  function updateThemeIcon(theme) {
    document.querySelectorAll('[data-theme-icon]').forEach(el=>{
      el.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    });
  }
  updateThemeIcon(saved);

  // Top loader bar
  const bar = document.createElement('div');
  bar.className = 'gf-loader-bar';
  document.body.appendChild(bar);

  document.addEventListener('click', function(e){
    const a = e.target.closest('a');
    if (!a || a.target === '_blank' || a.hasAttribute('download') || a.hasAttribute('data-no-loader')) return;
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:')) return;
    bar.classList.add('loading');
  });
  document.addEventListener('submit', function(e){
    if (e.target.hasAttribute('data-no-loader')) return;
    bar.classList.add('loading');
    showOverlay('Traitement en cours...');
  });
  window.addEventListener('pageshow', function(){ bar.classList.remove('loading'); hideOverlay(); });

  // Full-page overlay loader (for forms)
  let overlay;
  function ensureOverlay() {
    if (overlay) return overlay;
    overlay = document.createElement('div');
    overlay.className = 'gf-loader-overlay';
    overlay.innerHTML = '<div class="text-center"><div class="gf-spinner mx-auto"></div><div class="gf-loader-text" id="gf-loader-text">Chargement...</div></div>';
    document.body.appendChild(overlay);
    return overlay;
  }
  function showOverlay(text) {
    const o = ensureOverlay();
    o.querySelector('#gf-loader-text').textContent = text || 'Chargement...';
    o.classList.add('show');
  }
  function hideOverlay() { if (overlay) overlay.classList.remove('show'); }
  window.GFlow = { showOverlay, hideOverlay };
})();
