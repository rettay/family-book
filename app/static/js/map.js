(function() {
  'use strict';

  var svg = document.getElementById('map-svg');
  var emptyState = document.getElementById('map-empty');

  function isSafePersonId(value) {
    return typeof value === 'string' && /^[A-Za-z0-9-]{1,64}$/.test(value);
  }

  function safeText(value, fallback) {
    if (typeof value !== 'string' || value.length === 0) {
      return fallback || '';
    }
    return value.slice(0, 120);
  }

  function safeNumber(value) {
    return typeof value === 'number' && Number.isFinite(value) ? value : null;
  }

  function project(latitude, longitude) {
    var x = ((longitude + 180) / 360) * 1000;
    var y = ((90 - latitude) / 180) * 520;
    return {x: x, y: y};
  }

  function filtersFromForm() {
    return {
      living: document.getElementById('map-filter-living').value,
      branch: document.getElementById('map-filter-branch').value.trim(),
      residence_country: document.getElementById('map-filter-residence-country').value.trim().toUpperCase(),
      birth_country: document.getElementById('map-filter-birth-country').value.trim().toUpperCase()
    };
  }

  function queryString(filters) {
    var params = new URLSearchParams();
    Object.keys(filters).forEach(function(key) {
      if (filters[key] && filters[key] !== 'all') {
        params.set(key, filters[key]);
      }
    });
    var query = params.toString();
    return query ? '?' + query : '';
  }

  function drawBackdrop() {
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    var namespace = 'http://www.w3.org/2000/svg';
    var backdrop = document.createElementNS(namespace, 'rect');
    backdrop.setAttribute('x', '0');
    backdrop.setAttribute('y', '0');
    backdrop.setAttribute('width', '1000');
    backdrop.setAttribute('height', '520');
    backdrop.setAttribute('fill', 'transparent');
    svg.appendChild(backdrop);

    [130, 260, 390].forEach(function(y) {
      var line = document.createElementNS(namespace, 'line');
      line.setAttribute('x1', '0');
      line.setAttribute('x2', '1000');
      line.setAttribute('y1', String(y));
      line.setAttribute('y2', String(y));
      line.setAttribute('stroke', 'rgba(64, 86, 61, 0.18)');
      line.setAttribute('stroke-dasharray', '5 8');
      svg.appendChild(line);
    });

    [167, 333, 500, 667, 833].forEach(function(x) {
      var line = document.createElementNS(namespace, 'line');
      line.setAttribute('x1', String(x));
      line.setAttribute('x2', String(x));
      line.setAttribute('y1', '0');
      line.setAttribute('y2', '520');
      line.setAttribute('stroke', 'rgba(64, 86, 61, 0.12)');
      line.setAttribute('stroke-dasharray', '5 8');
      svg.appendChild(line);
    });
  }

  function drawMarkers(markers) {
    drawBackdrop();
    emptyState.hidden = markers.length > 0;

    markers.forEach(function(marker) {
      var latitude = safeNumber(marker.latitude);
      var longitude = safeNumber(marker.longitude);
      if (latitude === null || longitude === null || !isSafePersonId(marker.person && marker.person.id)) {
        return;
      }

      var point = project(latitude, longitude);
      var group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      var labelText = safeText(marker.person.display_name, 'Family member');
      var sublabelText = safeText(marker.place, safeText(marker.country_code, ''));
      group.setAttribute('transform', 'translate(' + point.x + ',' + point.y + ')');
      group.setAttribute('class', 'map-marker');
      group.setAttribute('tabindex', '0');
      group.setAttribute('role', 'link');
      group.setAttribute('aria-label', labelText + (sublabelText ? ', ' + sublabelText : ''));
      group.style.cursor = 'pointer';
      group.addEventListener('click', function() {
        window.location.assign('/people/' + encodeURIComponent(marker.person.id));
      });
      group.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          window.location.assign('/people/' + encodeURIComponent(marker.person.id));
        }
      });

      var halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      halo.setAttribute('r', '18');
      halo.setAttribute('fill', marker.kind === 'burial' ? 'rgba(180, 133, 28, 0.15)' : 'rgba(32, 92, 156, 0.15)');
      group.appendChild(halo);

      var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('r', '8');
      dot.setAttribute('fill', marker.kind === 'burial' ? '#b4851c' : '#205c9c');
      dot.setAttribute('stroke', '#fff');
      dot.setAttribute('stroke-width', '3');
      group.appendChild(dot);

      var label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', '14');
      label.setAttribute('y', '-10');
      label.setAttribute('fill', '#29403a');
      label.setAttribute('font-size', '13');
      label.setAttribute('font-weight', '600');
      label.textContent = labelText;
      group.appendChild(label);

      var sublabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      sublabel.setAttribute('x', '14');
      sublabel.setAttribute('y', '8');
      sublabel.setAttribute('fill', '#54665c');
      sublabel.setAttribute('font-size', '11');
      sublabel.textContent = sublabelText;
      group.appendChild(sublabel);

      svg.appendChild(group);
    });
  }

  async function loadMap() {
    var response = await fetch('/api/map' + queryString(filtersFromForm()));
    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }
    var data = await response.json();
    drawMarkers(data.markers || []);
  }

  document.getElementById('apply-map-filters').addEventListener('click', loadMap);
  document.getElementById('reset-map-filters').addEventListener('click', function() {
    document.getElementById('map-filter-living').value = 'all';
    document.getElementById('map-filter-branch').value = '';
    document.getElementById('map-filter-residence-country').value = '';
    document.getElementById('map-filter-birth-country').value = '';
    loadMap();
  });
  drawBackdrop();
  loadMap();
})();
