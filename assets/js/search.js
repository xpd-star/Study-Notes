(function () {
  var input = document.querySelector('[data-search="input"]');
  var items = document.querySelectorAll('[data-search="item"]');
  if (!input || !items || !items.length) return;

  function normalize(s) {
    return (s || '').toString().toLowerCase();
  }

  input.addEventListener('input', function () {
    var q = normalize(input.value).trim();
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      var hay = normalize(el.getAttribute('data-search-text'));
      el.style.display = q === '' || hay.indexOf(q) !== -1 ? '' : 'none';
    }
  });
})();

