/* Applies the saved language before first paint so RTL never flashes.
   Loaded as a classic, render-blocking script — kept external so the
   Content-Security-Policy never needs 'unsafe-inline' for scripts. */
(function () {
  try {
    var l = localStorage.getItem('gawahi-lang');
    if (l === 'ur' || l === 'sd') {
      var r = document.documentElement;
      r.lang = l; r.dir = 'rtl';
      r.setAttribute('data-font', l === 'ur' ? 'nastaliq' : 'naskh');
    }
    var th = localStorage.getItem('gawahi-theme');
    if (th === 'light' || th === 'dark') document.documentElement.setAttribute('data-theme', th);
  } catch (e) {}
})();
