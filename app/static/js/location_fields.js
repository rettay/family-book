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

  function hasCoordinates(group) {
    var latitudeInput = group.querySelector('[data-place-latitude]');
    var longitudeInput = group.querySelector('[data-place-longitude]');
    return Boolean(latitudeInput && latitudeInput.value && longitudeInput && longitudeInput.value);
  }

  function loadGooglePlaces(apiKey) {
    if (window.google && window.google.maps && window.google.maps.importLibrary) {
      return window.google.maps.importLibrary('places');
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
        '&loading=async&auth_referrer_policy=origin';
      script.async = true;
      script.defer = true;
      script.onload = function() {
        if (!(window.google && window.google.maps && window.google.maps.importLibrary)) {
          reject(new Error('places-unavailable'));
          return;
        }
        window.google.maps.importLibrary('places').then(resolve).catch(reject);
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
    var components = (place && (place.addressComponents || place.address_components)) || [];
    for (var i = 0; i < components.length; i += 1) {
      var component = components[i];
      if ((component.types || []).indexOf('country') !== -1) {
        return safeText(
          component.shortText ||
          component.short_name ||
          component.longText ||
          component.long_name
        ).toUpperCase();
      }
    }
    return '';
  }

  function extractLatitude(location) {
    if (!location) {
      return '';
    }
    if (typeof location.lat === 'function') {
      return String(location.lat());
    }
    if (typeof location.lat === 'number') {
      return String(location.lat);
    }
    return '';
  }

  function extractLongitude(location) {
    if (!location) {
      return '';
    }
    if (typeof location.lng === 'function') {
      return String(location.lng());
    }
    if (typeof location.lng === 'number') {
      return String(location.lng);
    }
    return '';
  }

  function predictionText(prediction) {
    if (!prediction) {
      return '';
    }
    if (prediction.text && typeof prediction.text.toString === 'function') {
      return safeText(prediction.text.toString());
    }
    return safeText(prediction.mainText || prediction.description || '');
  }

  function createSuggestionBox(placeInput) {
    var box = document.createElement('div');
    box.className = 'place-autocomplete-suggestions';
    box.hidden = true;
    box.setAttribute('role', 'listbox');
    placeInput.insertAdjacentElement('afterend', box);
    return box;
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

    var suggestionBox = createSuggestionBox(placeInput);
    var manualHint = config.manualHint || '';
    var configuredHint = config.configuredHint || manualHint;
    var verifiedHint = config.verifiedHint || configuredHint;
    var failedHint = config.failedHint || manualHint;
    var suggestionsLabel = config.suggestionsLabel || manualHint || 'Place suggestions';
    suggestionBox.setAttribute('aria-label', suggestionsLabel);
    var activePredictions = [];
    var activeIndex = -1;
    var requestNonce = 0;
    var debounceHandle = null;
    var sessionToken = null;

    function hideSuggestions() {
      activePredictions = [];
      activeIndex = -1;
      suggestionBox.hidden = true;
      suggestionBox.innerHTML = '';
    }

    function resetManualState() {
      clearCoordinates(group);
      hideSuggestions();
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
    }

    function resetSessionToken() {
      sessionToken = null;
    }

    function renderSuggestions(predictions) {
      activePredictions = predictions.slice();
      activeIndex = -1;
      suggestionBox.innerHTML = '';
      if (!activePredictions.length) {
        suggestionBox.hidden = true;
        return;
      }

      activePredictions.forEach(function(prediction, index) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'place-autocomplete-suggestion';
        button.setAttribute('role', 'option');
        button.dataset.index = String(index);
        button.textContent = predictionText(prediction);
        button.addEventListener('mousedown', function(event) {
          event.preventDefault();
        });
        button.addEventListener('click', function() {
          choosePrediction(prediction);
        });
        suggestionBox.appendChild(button);
      });

      suggestionBox.hidden = false;
    }

    function focusSuggestion(nextIndex) {
      var buttons = suggestionBox.querySelectorAll('.place-autocomplete-suggestion');
      if (!buttons.length) {
        activeIndex = -1;
        return;
      }
      activeIndex = (nextIndex + buttons.length) % buttons.length;
      buttons.forEach(function(button, index) {
        button.classList.toggle('place-autocomplete-suggestion--active', index === activeIndex);
      });
    }

    async function choosePrediction(prediction) {
      try {
        var places = await loadGooglePlaces(config.apiKey);
        var place = prediction.toPlace();
        await place.fetchFields({
          fields: ['formattedAddress', 'location', 'addressComponents']
        });

        var resolvedPlace = safeText(place.formattedAddress) || predictionText(prediction);
        if (resolvedPlace) {
          placeInput.value = resolvedPlace;
        }

        var resolvedCountry = extractCountryCode(place);
        if (resolvedCountry) {
          countryInput.value = resolvedCountry;
        }

        var lat = extractLatitude(place.location);
        var lng = extractLongitude(place.location);
        latitudeInput.value = lat;
        longitudeInput.value = lng;
        if (!lat || !lng) {
          clearCoordinates(group);
        }

        resetSessionToken();
        hideSuggestions();
        setStatus(group, verifiedHint, 'verified');
      } catch (_error) {
        hideSuggestions();
        setStatus(group, failedHint, 'warning');
      }
    }

    async function fetchSuggestions(query, nonce) {
      try {
        var places = await loadGooglePlaces(config.apiKey);
        if (!sessionToken && places.AutocompleteSessionToken) {
          sessionToken = new places.AutocompleteSessionToken();
        }
        var request = { input: query };
        var country = countryInput.value.trim();
        if (/^[a-z]{2}$/i.test(country)) {
          request.includedRegionCodes = [country.toLowerCase()];
        }
        if (sessionToken) {
          request.sessionToken = sessionToken;
        }

        var response = await places.AutocompleteSuggestion.fetchAutocompleteSuggestions(request);
        if (nonce !== requestNonce) {
          return;
        }
        var suggestions = (response && response.suggestions) || [];
        renderSuggestions(
          suggestions
            .map(function(entry) { return entry && entry.placePrediction; })
            .filter(Boolean)
        );
      } catch (_error) {
        if (nonce !== requestNonce) {
          return;
        }
        hideSuggestions();
        setStatus(group, failedHint, 'warning');
      }
    }

    placeInput.addEventListener('input', function() {
      clearCoordinates(group);
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
      if (debounceHandle) {
        window.clearTimeout(debounceHandle);
      }
      if (!config.hasGoogle || !config.apiKey) {
        hideSuggestions();
        return;
      }
      var query = safeText(placeInput.value);
      requestNonce += 1;
      if (query.length < 3) {
        hideSuggestions();
        resetSessionToken();
        return;
      }
      var nonce = requestNonce;
      debounceHandle = window.setTimeout(function() {
        fetchSuggestions(query, nonce);
      }, 220);
    });

    placeInput.addEventListener('keydown', function(event) {
      if (suggestionBox.hidden) {
        return;
      }
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        focusSuggestion(activeIndex + 1);
        return;
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        focusSuggestion(activeIndex - 1);
        return;
      }
      if (event.key === 'Escape') {
        hideSuggestions();
        return;
      }
      if (event.key === 'Enter' && activeIndex >= 0 && activePredictions[activeIndex]) {
        event.preventDefault();
        choosePrediction(activePredictions[activeIndex]);
      }
    });

    placeInput.addEventListener('blur', function() {
      window.setTimeout(hideSuggestions, 150);
    });

    countryInput.addEventListener('input', function() {
      clearCoordinates(group);
      hideSuggestions();
      resetSessionToken();
      if (/^[a-z]{2}$/i.test(countryInput.value.trim())) {
        countryInput.value = countryInput.value.trim().toUpperCase();
      }
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
    });

    if (hasCoordinates(group)) {
      setStatus(group, verifiedHint, 'verified');
    } else {
      setStatus(group, config.hasGoogle ? configuredHint : manualHint, 'neutral');
    }
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
    if (suggestionsLabel) {
      suggestionBox.setAttribute('aria-label', suggestionsLabel);
    }
