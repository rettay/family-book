(function() {
  'use strict';

  var root = document.getElementById('map-root');
  var svg = document.getElementById('map-svg');
  var googleMapEl = document.getElementById('google-map');
  var emptyState = document.getElementById('map-empty');
  var providerStatus = document.getElementById('map-provider-status');
  var selectedCard = document.getElementById('map-selected-marker');
  var selectedTitle = document.getElementById('map-selected-title');
  var selectedDetails = document.getElementById('map-selected-details');
  var selectedLink = document.getElementById('map-selected-link');
  var googleMap = null;
  var googleLoader = null;
  var googleOverlay = null;
  var googleOverlayContainer = null;
  var googleOverlayMarkers = [];
  var selectedMarkerId = '';
  var lastMarkers = [];

  function isSafePersonId(value) {
    return typeof value === 'string' && /^[A-Za-z0-9-]{1,64}$/.test(value);
  }

  function safeText(value, fallback) {
    if (typeof value !== 'string' || value.length === 0) {
      return fallback || '';
    }
    return value.slice(0, 160);
  }

  function safeNumber(value) {
    return typeof value === 'number' && Number.isFinite(value) ? value : null;
  }

  function project(latitude, longitude) {
    var x = ((longitude + 180) / 360) * 1000;
    var y = ((90 - latitude) / 180) * 520;
    return { x: x, y: y };
  }

  function navigateToPerson(personId) {
    window.location.assign('/people/' + encodeURIComponent(personId) + '/edit');
  }

  function relationLabel(scope) {
    if (scope === 'self') return root.dataset.relationSelfLabel;
    if (scope === 'one_step') return root.dataset.relationOneStepLabel;
    if (scope === 'two_steps') return root.dataset.relationTwoStepsLabel;
    if (scope === 'extended') return root.dataset.relationExtendedLabel;
    return root.dataset.relationUnlinkedLabel;
  }

  function sourceLabel(source) {
    if (source === 'coordinates') return root.dataset.sourceCoordinatesLabel;
    if (source === 'place_lookup') return root.dataset.sourcePlaceLookupLabel;
    return root.dataset.sourceCountryCentroidLabel;
  }

  function relationRingColor(scope) {
    if (scope === 'self') return '#238061';
    if (scope === 'one_step') return '#367e42';
    if (scope === 'two_steps') return '#205c9c';
    if (scope === 'extended') return '#6c7885';
    return '#9a886e';
  }

  function markerFill(kind) {
    return kind === 'burial' ? '#b4851c' : '#205c9c';
  }

  function currentProvider() {
    return root && root.dataset.mapProvider === 'google' ? 'google' : 'svg';
  }

  function setProviderStatus(text) {
    if (providerStatus && typeof text === 'string' && text) {
      providerStatus.textContent = text;
    }
  }

  function setBoardMode(mode) {
    var useGoogle = mode === 'google';
    if (googleMapEl) googleMapEl.hidden = !useGoogle;
    if (svg) svg.hidden = useGoogle;
  }

  function selectedMarker() {
    for (var i = 0; i < lastMarkers.length; i += 1) {
      var marker = lastMarkers[i];
      if (marker.person && marker.person.id + ':' + marker.kind === selectedMarkerId) {
        return marker;
      }
    }
    return lastMarkers[0] || null;
  }

  function renderSelectedMarker(marker) {
    if (!selectedCard || !selectedTitle || !selectedDetails || !selectedLink) {
      return;
    }
    if (!marker || !marker.person || !isSafePersonId(marker.person.id)) {
      selectedCard.hidden = true;
      return;
    }
    selectedCard.hidden = false;
    selectedTitle.textContent = safeText(marker.person.display_name, 'Family member');
    selectedLink.href = '/people/' + encodeURIComponent(marker.person.id) + '/edit';
    selectedDetails.innerHTML = '';

    [
      marker.kind === 'burial' ? root.dataset.kindBurialLabel : root.dataset.kindResidenceLabel,
      safeText(marker.place, marker.country_code || ''),
      relationLabel(marker.relation_scope),
      sourceLabel(marker.location_source)
    ].filter(Boolean).forEach(function(line) {
      var detail = document.createElement('div');
      detail.textContent = line;
      selectedDetails.appendChild(detail);
    });
  }

  function focusMarker(marker) {
    if (!marker || !marker.person || !isSafePersonId(marker.person.id)) {
      return;
    }
    selectedMarkerId = marker.person.id + ':' + marker.kind;
    renderSelectedMarker(marker);
  }

  function filtersFromForm() {
    return {
      living: document.getElementById('map-filter-living').value,
      branch: document.getElementById('map-filter-branch').value.trim(),
      residence_country: document.getElementById('map-filter-residence-country').value.trim().toUpperCase(),
      birth_country: document.getElementById('map-filter-birth-country').value.trim().toUpperCase(),
      relationship_scope: document.getElementById('map-filter-relationship-scope').value
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

  function drawSvgMarkers(markers) {
    setBoardMode('svg');
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
      group.setAttribute('data-location-source', marker.location_source);
      group.setAttribute('data-relation-scope', marker.relation_scope);
      group.setAttribute('aria-label', labelText + (sublabelText ? ', ' + sublabelText : ''));
      group.style.cursor = 'pointer';
      group.addEventListener('mouseenter', function() { focusMarker(marker); });
      group.addEventListener('focus', function() { focusMarker(marker); });
      group.addEventListener('click', function() { navigateToPerson(marker.person.id); });
      group.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          navigateToPerson(marker.person.id);
        }
      });

      var relationRing = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      relationRing.setAttribute('r', '18');
      relationRing.setAttribute('fill', 'transparent');
      relationRing.setAttribute('stroke', relationRingColor(marker.relation_scope));
      relationRing.setAttribute('stroke-width', '3');
      if (marker.location_source === 'country_centroid') {
        relationRing.setAttribute('stroke-dasharray', '4 4');
      }
      group.appendChild(relationRing);

      var halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      halo.setAttribute('r', '12');
      halo.setAttribute('fill', marker.kind === 'burial' ? 'rgba(180, 133, 28, 0.16)' : 'rgba(32, 92, 156, 0.16)');
      group.appendChild(halo);

      var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('r', '7');
      dot.setAttribute('fill', markerFill(marker.kind));
      dot.setAttribute('stroke', '#fff');
      dot.setAttribute('stroke-width', '3');
      group.appendChild(dot);

      var label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', '15');
      label.setAttribute('y', '-10');
      label.setAttribute('fill', '#29403a');
      label.setAttribute('font-size', '13');
      label.setAttribute('font-weight', '600');
      label.textContent = labelText;
      group.appendChild(label);

      var sublabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      sublabel.setAttribute('x', '15');
      sublabel.setAttribute('y', '8');
      sublabel.setAttribute('fill', '#54665c');
      sublabel.setAttribute('font-size', '11');
      sublabel.textContent = sublabelText;
      group.appendChild(sublabel);

      svg.appendChild(group);
    });

    renderSelectedMarker(selectedMarker());
  }

  function clearGoogleOverlayMarkers() {
    googleOverlayMarkers = [];
    if (googleOverlayContainer) {
      googleOverlayContainer.textContent = '';
    }
  }

  function ensureGoogleOverlay() {
    if (googleOverlay) {
      return googleOverlay;
    }

    googleOverlay = new window.google.maps.OverlayView();
    googleOverlay.onAdd = function() {
      googleOverlayContainer = document.createElement('div');
      googleOverlayContainer.className = 'map-google-overlay';
      this.getPanes().overlayMouseTarget.appendChild(googleOverlayContainer);
    };
    googleOverlay.draw = function() {
      renderGoogleOverlayMarkers();
    };
    googleOverlay.onRemove = function() {
      if (googleOverlayContainer) {
        googleOverlayContainer.remove();
        googleOverlayContainer = null;
      }
    };
    googleOverlay.setMap(googleMap);
    return googleOverlay;
  }

  function renderGoogleOverlayMarkers() {
    if (!googleOverlay || !googleOverlayContainer) {
      return;
    }

    var projection = googleOverlay.getProjection();
    if (!projection) {
      return;
    }

    googleOverlayContainer.textContent = '';

    googleOverlayMarkers.forEach(function(marker) {
      var latitude = safeNumber(marker.latitude);
      var longitude = safeNumber(marker.longitude);
      if (latitude === null || longitude === null || !isSafePersonId(marker.person && marker.person.id)) {
        return;
      }

      var position = projection.fromLatLngToDivPixel(
        new window.google.maps.LatLng(latitude, longitude)
      );
      if (!position) {
        return;
      }

      var labelText = safeText(marker.person.display_name, 'Family member');
      var sublabelText = safeText(marker.place, safeText(marker.country_code, ''));
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'map-google-marker-button';
      button.dataset.relationScope = marker.relation_scope;
      button.dataset.locationSource = marker.location_source;
      button.style.left = position.x + 'px';
      button.style.top = position.y + 'px';
      button.setAttribute('aria-label', labelText + (sublabelText ? ', ' + sublabelText : ''));
      button.addEventListener('mouseenter', function() { focusMarker(marker); });
      button.addEventListener('focus', function() { focusMarker(marker); });
      button.addEventListener('click', function() { navigateToPerson(marker.person.id); });
      button.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          navigateToPerson(marker.person.id);
        }
      });

      var dot = document.createElement('span');
      dot.className = 'map-google-marker-dot map-google-marker-dot--' + (marker.kind === 'burial' ? 'burial' : 'residence');
      dot.setAttribute('aria-hidden', 'true');
      button.appendChild(dot);

      var label = document.createElement('span');
      label.className = 'map-google-marker-label';
      label.textContent = labelText;
      button.appendChild(label);

      googleOverlayContainer.appendChild(button);
    });

    renderSelectedMarker(selectedMarker());
  }

  function renderGoogleMap(markers) {
    if (!window.google || !window.google.maps) {
      throw new Error('google-maps-unavailable');
    }

    setBoardMode('google');
    emptyState.hidden = markers.length > 0;

    if (!googleMap) {
      var options = {
        center: { lat: 20, lng: 0 },
        zoom: 2,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
        gestureHandling: 'cooperative'
      };
      if (root.dataset.googleMapsMapId) {
        options.mapId = root.dataset.googleMapsMapId;
      }
      googleMap = new window.google.maps.Map(googleMapEl, options);
    }

    clearGoogleOverlayMarkers();

    if (!markers.length) {
      googleMap.setCenter({ lat: 20, lng: 0 });
      googleMap.setZoom(2);
      ensureGoogleOverlay();
      renderGoogleOverlayMarkers();
      return;
    }

    var bounds = new window.google.maps.LatLngBounds();
    var validMarkers = [];

    markers.forEach(function(marker) {
      var latitude = safeNumber(marker.latitude);
      var longitude = safeNumber(marker.longitude);
      if (latitude === null || longitude === null || !isSafePersonId(marker.person && marker.person.id)) {
        return;
      }
      validMarkers.push(marker);
      bounds.extend({ lat: latitude, lng: longitude });
    });

    googleOverlayMarkers = validMarkers;
    ensureGoogleOverlay();

    if (googleOverlayMarkers.length === 1) {
      googleMap.setCenter(bounds.getCenter());
      googleMap.setZoom(4);
      renderGoogleOverlayMarkers();
      return;
    }
    googleMap.fitBounds(bounds, 64);
    renderGoogleOverlayMarkers();
  }

  function loadGoogleMapsLibrary() {
    if (window.google && window.google.maps) {
      return Promise.resolve(window.google.maps);
    }
    if (googleLoader) {
      return googleLoader;
    }
    var apiKey = root.dataset.googleMapsApiKey;
    if (!apiKey) {
      return Promise.reject(new Error('google-maps-not-configured'));
    }

    googleLoader = new Promise(function(resolve, reject) {
      var script = document.createElement('script');
      script.src =
        'https://maps.googleapis.com/maps/api/js?key=' +
        encodeURIComponent(apiKey) +
        '&auth_referrer_policy=origin';
      script.async = true;
      script.defer = true;
      script.onload = function() {
        if (window.google && window.google.maps) {
          resolve(window.google.maps);
          return;
        }
        reject(new Error('google-maps-unavailable'));
      };
      script.onerror = function() {
        googleLoader = null;
        reject(new Error('google-maps-load-failed'));
      };
      document.head.appendChild(script);
    });
    googleLoader.catch(function() {
      googleLoader = null;
    });
    return googleLoader;
  }

  async function fetchMarkers() {
    var response = await fetch('/api/map' + queryString(filtersFromForm()));
    if (response.status === 401) {
      window.location.href = '/login';
      return null;
    }
    var data = await response.json();
    return data.markers || [];
  }

  async function loadMap() {
    var markers = await fetchMarkers();
    if (markers === null) {
      return;
    }

    lastMarkers = markers;
    if (!markers.length) {
      selectedMarkerId = '';
    } else if (!selectedMarker()) {
      selectedMarkerId = markers[0].person.id + ':' + markers[0].kind;
    }

    if (currentProvider() === 'google') {
      try {
        await loadGoogleMapsLibrary();
        setProviderStatus(root.dataset.providerGoogleLabel);
        renderGoogleMap(markers);
        return;
      } catch (error) {
        setProviderStatus(root.dataset.providerErrorLabel);
      }
    }

    setProviderStatus(root.dataset.providerFallbackLabel);
    drawSvgMarkers(markers);
  }

  document.getElementById('apply-map-filters').addEventListener('click', loadMap);
  document.getElementById('reset-map-filters').addEventListener('click', function() {
    document.getElementById('map-filter-living').value = 'all';
    document.getElementById('map-filter-branch').value = '';
    document.getElementById('map-filter-residence-country').value = '';
    document.getElementById('map-filter-birth-country').value = '';
    document.getElementById('map-filter-relationship-scope').value = 'all';
    loadMap();
  });

  drawBackdrop();
  loadMap();
  window.familyBookMap = {
    reload: loadMap
  };
})();
