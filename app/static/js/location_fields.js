(function() {
  'use strict';

  var loaderPromise = null;

  function safeText(value) {
    return typeof value === 'string' ? value.trim() : '';
  }

  function setStatus(group, text, tone) {
    var status = group.querySelector('[data-place-status]');
    if (!status) {
      return;
    }
    status.textContent = text || '';
    status.dataset.tone = tone || 'neutral';
  }

  function loadGooglePlaces(apiKey) {
    if (window.google && window.google.maps && window.google.maps.places) {
      return Promise.resolve(window.google.maps.places);
    }
    if (loaderPromise) {
      return loaderPromise;
    }
    if (!apiKey) {
      return Promise.reject(new Error('places-not-configured'));
    }

    loaderPromise = new Promise(function(resolve, reject) {
      var script = document.createElement('script');
      script.src =
        'https://maps.googleapis.com/maps/api/js?key=' +
        encodeURIComponent(apiKey) +
        '&libraries=places&auth_referrer_policy=origin';
      script.async = true;
      script.defer = true;
      script.onload = function() {
        if (window.google && window.google.maps && window.google.maps.places) {
          resolve(window.google.maps.places);
          return;
        }
        reject(new Error('places-unavailable'));
      };
      script.onerror = function() {
        loaderPromise = null;
        reject(new Error('places-load-failed'));
      };
      document.head.appendChild(script);
    });

    loaderPromise.catch(function() {
      loaderPromise = null;
    });

    return loaderPromise;
  }

  function extractCountryCode(place) {
    var components = (place && place.address_components) || [];
    for (var i = 0; i < components.length; i += 1) {
      var component = components[i];
      if ((component.types || []).indexOf('country') !== -1) {
        return safeText(component.short_name).toUpperCase();
      }
    }
    return '';
  }

  function clearCoordinates(group) {
    var latitudeInput = group.querySelector('[data-place-latitude]');
    var longitudeInput = group.querySelector('[data-place-longitude]');
    if (latitudeInput) {
      latitudeInput.value = '';
    }
    if (longitudeInput) {
      longitudeInput.value = '';
    }
  }

  function bindPlaceGroup(group, config) {
    if (!group || group.dataset.locationBound === 'true') {
      return;
    }
    group.dataset.locationBound = 'true';

    var placeInput = group.querySelector('[data-place-input]');
    var countryInput = group.querySelector('[data-country-input]');
    var latitudeInput = group.querySelector('[data-place-latitude]');
    var longitudeInput = group.querySelector('[data-place-longitude]');
    if (!placeInput || !countryInput || !latitudeInput || !longitudeInput) {
      return;
    }

    var manualHint = config.manualHint || '';
    var configuredHint = config.configuredHint || manualHint;
    var verifiedHint = config.verifiedHint || configuredHint;
    var failedHint = config.failedHint || manualHint;

    function resetManualState() {
      clearCoordinates(group);
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
    }

    placeInput.addEventListener('input', resetManualState);
    countryInput.addEventListener('input', function() {
      clearCoordinates(group);
      if (/^[a-z]{2}$/i.test(countryInput.value.trim())) {
        countryInput.value = countryInput.value.trim().toUpperCase();
      }
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
    });

    setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');

    if (!config.hasGoogle || !config.apiKey) {
      return;
    }

    loadGooglePlaces(config.apiKey)
      .then(function() {
        var autocomplete = new window.google.maps.places.Autocomplete(placeInput, {
          fields: ['address_components', 'formatted_address', 'geometry', 'name'],
          types: ['geocode'],
        });
        autocomplete.addListener('place_changed', function() {
          var place = autocomplete.getPlace();
          if (!place) {
            return;
          }
          var resolvedPlace = safeText(place.formatted_address) || safeText(place.name);
          if (resolvedPlace) {
            placeInput.value = resolvedPlace;
          }
          var resolvedCountry = extractCountryCode(place);
          if (resolvedCountry) {
            countryInput.value = resolvedCountry;
          }
          var geometry = place.geometry && place.geometry.location;
          if (geometry) {
            latitudeInput.value = String(geometry.lat());
            longitudeInput.value = String(geometry.lng());
          } else {
            clearCoordinates(group);
          }
          setStatus(group, verifiedHint, 'verified');
        });
      })
      .catch(function() {
        setStatus(group, failedHint, 'warning');
      });
  }

  function init(root, options) {
    var scope = root || document;
    var config = options || {};
    var groups = scope.querySelectorAll('[data-place-field]');
    groups.forEach(function(group) {
      bindPlaceGroup(group, config);
    });
  }

  window.familyBookLocations = {
    init: init,
  };
})();
