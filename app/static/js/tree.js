/* Family Book — D3 Tree Visualization */

(function() {
  'use strict';

  var svg;
  var g;
  var zoom;
  var treeData;
  var sidebarTrigger = null;
  var currentSidebarPersonId = null;
  var sidebarState = {
    activeTab: 'overview',
    relationshipGroup: '',
    peopleOptions: [],
    highlightMediaId: '',
    highlightRelatedPersonId: '',
    graphMode: null
  };
  var preferences = {
    show_names: true,
    show_nicknames: false,
    show_birth_dates: false,
    show_country_flags: true,
    show_photos: true
  };
  var NODE_RADIUS = 30;
  var NODE_SPACING_X = 100;
  var NODE_SPACING_Y = 150;
  var PARTNER_GAP_X = 120;
  var FAMILY_UNIT_GAP_X = 190;
  var COMPONENT_PADDING_X = 88;
  var COMPONENT_PADDING_Y = 72;
  var DETACHED_COMPONENT_GAP_X = 72;
  var DETACHED_COMPONENT_GAP_Y = 110;
  var lastFitTransform = null;
  var currentRootPersonId = '';
  var currentFocusPersonId = '';
  var initialUrlFocusPersonId = '';
  var initialUrlFocusApplied = false;

  var root = document.getElementById('tree-root');
  var statusNode = document.getElementById('tree-status');
  var sidebar = document.getElementById('person-sidebar');
  var sidebarContent = document.getElementById('sidebar-content');
  var treeLayout = document.getElementById('tree-root');

  function readFocusParamFromUrl() {
    try {
      var url = new URL(window.location.href);
      return url.searchParams.get('focus') || '';
    } catch (err) {
      return '';
    }
  }

  function updateFocusParam(personId) {
    try {
      var url = new URL(window.location.href);
      if (personId) {
        url.searchParams.set('focus', personId);
      } else {
        url.searchParams.delete('focus');
      }
      window.history.replaceState({}, '', url.pathname + url.search + url.hash);
    } catch (err) {
      return;
    }
  }

  function lookupPerson(personId) {
    if (!treeData || !treeData.persons) {
      return null;
    }
    return treeData.persons.find(function(person) {
      return person.id === personId;
    }) || null;
  }

  function personDisplayName(personId) {
    var person = lookupPerson(personId);
    return person ? person.display_name : '';
  }

  function treeNodeLabel(person) {
    if (!person) {
      return '';
    }
    if (preferences.show_nicknames && person.nickname) {
      var nickname = String(person.nickname || '').trim();
      if (!nickname) {
        return person.display_name;
      }
      if (!person.last_name) {
        return nickname;
      }
      if (person.name_display_order === 'eastern') {
        return [person.last_name, nickname].filter(Boolean).join(' ');
      }
      if (person.name_display_order === 'patronymic' && person.patronymic) {
        return [person.last_name, nickname, person.patronymic].filter(Boolean).join(' ');
      }
      return [nickname, person.last_name].filter(Boolean).join(' ');
    }
    return person.display_name;
  }

  function setCurrentFocusPerson(personId, options) {
    var opts = options || {};
    currentFocusPersonId = personId || '';
    if (opts.updateUrl !== false) {
      updateFocusParam(currentFocusPersonId);
    }
    syncNavigationContext();
    syncSidebarOrientation();
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

  function choosePrimaryParentPair(parentIds, partnershipByPair) {
    var ids = Array.from(new Set((parentIds || []).filter(Boolean))).sort();
    if (ids.length < 2) {
      return null;
    }
    if (ids.length === 2) {
      return ids;
    }
    for (var index = 0; index < ids.length; index += 1) {
      for (var otherIndex = index + 1; otherIndex < ids.length; otherIndex += 1) {
        var pair = [ids[index], ids[otherIndex]];
        if (partnershipByPair[pair.join('|')]) {
          return pair;
        }
      }
    }
    return null;
  }

  function pushUnique(map, key, value) {
    if (!map[key]) {
      map[key] = [];
    }
    if (map[key].indexOf(value) === -1) {
      map[key].push(value);
    }
  }

  function averageValues(values) {
    var filtered = (values || []).filter(function(value) {
      return value !== null && value !== undefined;
    });
    if (!filtered.length) {
      return null;
    }
    return filtered.reduce(function(total, value) {
      return total + value;
    }, 0) / filtered.length;
  }

  function currentFilters() {
    return {
      living: document.getElementById('tree-filter-living').value,
      branch: document.getElementById('tree-filter-branch').value.trim(),
      residence_country: document.getElementById('tree-filter-residence-country').value.trim().toUpperCase(),
      birth_country: document.getElementById('tree-filter-birth-country').value.trim().toUpperCase()
    };
  }

  function syncPreferenceInputs() {
    document.getElementById('pref-show-names').checked = !!preferences.show_names;
    document.getElementById('pref-show-nicknames').checked = !!preferences.show_nicknames;
    document.getElementById('pref-show-birth-dates').checked = !!preferences.show_birth_dates;
    document.getElementById('pref-show-country-flags').checked = !!preferences.show_country_flags;
    document.getElementById('pref-show-photos').checked = !!preferences.show_photos;
  }

  function readPreferenceInputs() {
    preferences = {
      show_names: document.getElementById('pref-show-names').checked,
      show_nicknames: document.getElementById('pref-show-nicknames').checked,
      show_birth_dates: document.getElementById('pref-show-birth-dates').checked,
      show_country_flags: document.getElementById('pref-show-country-flags').checked,
      show_photos: document.getElementById('pref-show-photos').checked
    };
  }

  function setStatus(text) {
    statusNode.textContent = text;
  }

  function escapeHTML(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatTemplate(template, values) {
    return String(template || '').replace(/\{([^}]+)\}/g, function(_, key) {
      return Object.prototype.hasOwnProperty.call(values, key) ? String(values[key]) : '';
    });
  }

  function clearNode(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function showToastMessage(message) {
    if (typeof window.showToast === 'function') {
      window.showToast(message);
    }
  }

  function parseJsonArray(rawValue) {
    if (!rawValue) {
      return [];
    }
    try {
      var parsed = JSON.parse(rawValue);
      if (Array.isArray(parsed)) {
        return parsed.filter(Boolean);
      }
    } catch (err) {
      return [];
    }
    return [];
  }

  function formatDateLabel(value) {
    if (!value) {
      return '';
    }
    var date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value).slice(0, 10);
    }
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  function createMiniAction(label, handler, className) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = className || 'btn btn--ghost btn--sm';
    button.textContent = label;
    button.addEventListener('click', handler);
    return button;
  }

  function getSidebarCard() {
    return sidebarContent.querySelector('[data-tree-sidebar-person-id]');
  }

  function getSidebarPersonId() {
    var card = getSidebarCard();
    return card ? card.dataset.treeSidebarPersonId : currentSidebarPersonId;
  }

  function getSidebarCanManage() {
    var card = getSidebarCard();
    return !!(card && card.dataset.treeSidebarCanManage === 'true');
  }

  function getSidebarPersonName() {
    var titleNode = sidebarContent.querySelector('.tree-sidebar-card__title');
    return titleNode ? titleNode.textContent.trim() : '';
  }

  function parseSidebarPeopleOptions() {
    var scriptNode = sidebarContent.querySelector('#tree-sidebar-people-options');
    if (!scriptNode) {
      sidebarState.peopleOptions = [];
      return;
    }
    try {
      sidebarState.peopleOptions = JSON.parse(scriptNode.textContent || '[]');
    } catch (err) {
      sidebarState.peopleOptions = [];
    }
  }

  function openRelationshipDisclosure(groupName) {
    if (!groupName) {
      return;
    }
    var disclosures = sidebarContent.querySelectorAll('[data-tree-relationship-group]');
    Array.prototype.forEach.call(disclosures, function(disclosure) {
      disclosure.open = disclosure.dataset.treeRelationshipGroup === groupName;
    });
  }

  function relationshipSingularLabel(mode) {
    if (mode === 'parent') {
      return root.dataset.treeParentSingular;
    }
    if (mode === 'child') {
      return root.dataset.treeChildSingular;
    }
    return root.dataset.treePartnerSingular;
  }

  function graphModeSummary(modeState) {
    if (!modeState) {
      return {title: '', description: ''};
    }
    var values = {
      name: modeState.sourcePersonName || getSidebarPersonName(),
      relationship: relationshipSingularLabel(modeState.mode),
      current: modeState.currentRelatedName || ''
    };
    return {
      title: modeState.action === 'replace'
        ? root.dataset.treeReplaceOnTree
        : root.dataset.treeGraphPickOnTree,
      description: formatTemplate(
        modeState.action === 'replace'
          ? root.dataset.treeGraphPromptReplace
          : root.dataset.treeGraphPromptLink,
        values
      )
    };
  }

  function syncNavigationContext() {
    var focusStatus = document.getElementById('tree-focus-status');
    var rootStatus = document.getElementById('tree-root-status');
    var returnFocusButton = document.getElementById('tree-return-focus');
    var centerRootButton = document.getElementById('tree-center-root');
    var hasFocus = !!(currentFocusPersonId && lookupPerson(currentFocusPersonId));
    var rootName = personDisplayName(currentRootPersonId);

    if (focusStatus) {
      focusStatus.textContent = hasFocus
        ? formatTemplate(root.dataset.treeFocusCurrentTemplate, {name: personDisplayName(currentFocusPersonId)})
        : root.dataset.treeFocusNone;
    }
    if (rootStatus) {
      rootStatus.textContent = rootName
        ? root.dataset.treeRootLabel + ': ' + rootName
        : root.dataset.treeRootLabel;
    }
    if (returnFocusButton) {
      returnFocusButton.disabled = !hasFocus;
    }
    if (centerRootButton) {
      centerRootButton.disabled = !currentRootPersonId;
    }
  }

  function syncSidebarOrientation() {
    var card = getSidebarCard();
    if (!card) {
      return;
    }

    var personId = card.dataset.treeSidebarPersonId || '';
    var isRoot = card.dataset.treeSidebarIsRoot === 'true';
    var focusBadge = document.getElementById('tree-sidebar-focus-badge');
    var setFocusButton = document.getElementById('tree-sidebar-set-focus');
    var returnFocusButton = document.getElementById('tree-sidebar-return-focus');
    var centerRootButton = document.getElementById('tree-sidebar-center-root');
    var focusExists = !!(currentFocusPersonId && lookupPerson(currentFocusPersonId));
    var isCurrentFocus = !!(focusExists && currentFocusPersonId === personId);

    if (focusBadge) {
      focusBadge.hidden = !isCurrentFocus;
    }
    if (setFocusButton) {
      setFocusButton.hidden = isCurrentFocus;
    }
    if (returnFocusButton) {
      returnFocusButton.hidden = !focusExists || isCurrentFocus;
    }
    if (centerRootButton) {
      centerRootButton.hidden = !currentRootPersonId || isRoot;
    }
  }

  function syncRelationshipCalcControls() {
    var startButton = document.getElementById('tree-relcalc-start');
    var cancelButton = document.getElementById('tree-relcalc-cancel');
    if (startButton) {
      startButton.disabled = _relCalcMode;
    }
    if (cancelButton) {
      cancelButton.hidden = !_relCalcMode;
    }
  }

  function syncInteractionModeClasses() {
    if (!treeLayout) {
      return;
    }
    treeLayout.classList.toggle('tree-layout--graph-mode', !!sidebarState.graphMode);
    treeLayout.classList.toggle('tree-layout--relcalc-mode', !!_relCalcMode);
  }

  function updateGraphModeBanner() {
    var banner = document.getElementById('tree-graph-mode-banner');
    var canvasPrompt = document.getElementById('tree-graph-prompt');
    var canvasPromptText = document.getElementById('tree-graph-prompt-text');
    if (!banner) {
      return;
    }
    var titleNode = document.getElementById('tree-graph-mode-title');
    var descriptionNode = document.getElementById('tree-graph-mode-description');
    if (!sidebarState.graphMode) {
      banner.classList.add('hidden');
      if (titleNode) titleNode.textContent = '';
      if (descriptionNode) descriptionNode.textContent = '';
      if (canvasPrompt) canvasPrompt.hidden = true;
      syncInteractionModeClasses();
      return;
    }
    var summary = graphModeSummary(sidebarState.graphMode);
    banner.classList.remove('hidden');
    if (titleNode) titleNode.textContent = summary.title;
    if (descriptionNode) descriptionNode.textContent = summary.description;
    setStatus(summary.description);
    if (canvasPrompt && canvasPromptText) {
      canvasPromptText.textContent = summary.description;
      canvasPrompt.hidden = false;
    }
    syncInteractionModeClasses();
  }

  function applyRelationshipHighlights() {
    var cards = sidebarContent.querySelectorAll('[data-tree-related-person]');
    Array.prototype.forEach.call(cards, function(card) {
      var active = !!(sidebarState.highlightRelatedPersonId && card.dataset.treeRelatedPerson === sidebarState.highlightRelatedPersonId);
      card.classList.toggle('tree-related-card--highlight', active);
    });
  }

  function restoreDefaultStatus() {
    if (treeData && treeData.persons) {
      setStatus(root.dataset.statusTemplate.replace('{count}', String(treeData.persons.length)));
    }
  }

  function chooseDefaultSidebarTab() {
    var card = getSidebarCard();
    if (!card) {
      return 'overview';
    }
    if (sidebarState.activeTab && sidebarContent.querySelector('[data-tree-sidebar-panel="' + sidebarState.activeTab + '"]')) {
      return sidebarState.activeTab;
    }
    return card.dataset.treeSidebarDefaultTab || 'overview';
  }

  function renderEmptyTreeStream(container, text, actionLabel, actionHandler) {
    clearNode(container);
    var wrapper = document.createElement('div');
    wrapper.className = 'tree-sidebar-stream-empty';
    var copy = document.createElement('p');
    copy.textContent = text;
    wrapper.appendChild(copy);
    if (actionLabel && typeof actionHandler === 'function') {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn--secondary btn--sm';
      button.textContent = actionLabel;
      button.addEventListener('click', actionHandler);
      wrapper.appendChild(button);
    }
    container.appendChild(wrapper);
  }

  function buildTaggedPeopleSummary(taggedPeople) {
    if (!taggedPeople || !taggedPeople.length) {
      return '';
    }
    return taggedPeople
      .map(function(person) {
        return person && person.display_name ? person.display_name : '';
      })
      .filter(Boolean)
      .join(', ');
  }

  function formatAttachmentSummary(count) {
    if (!count) {
      return root.dataset.treeStoryAttachmentsPending;
    }
    return root.dataset.treeStoryAttachmentsCount.replace('{count}', String(count));
  }

  function renderComposerFiles(fileInput, summaryNode, listNode) {
    var files = fileInput && fileInput.files ? Array.prototype.slice.call(fileInput.files) : [];
    if (summaryNode) {
      summaryNode.textContent = formatAttachmentSummary(files.length);
    }
    if (!listNode) {
      return;
    }
    clearNode(listNode);
    files.forEach(function(file) {
      var chip = document.createElement('span');
      chip.className = 'tree-composer-token';
      chip.textContent = file.name;
      listNode.appendChild(chip);
    });
  }

  function createMediaNode(media) {
    var item = document.createElement('div');
    item.className = 'tree-sidebar-media-item';
    if (sidebarState.highlightMediaId && sidebarState.highlightMediaId === media.id) {
      item.classList.add('tree-sidebar-media-item--highlight');
    }
    var mediaUrl = '/api/media/' + media.id + '/file';
    var mType = media.media_type || 'image';

    if (mType === 'audio') {
      var audioEl = document.createElement('audio');
      audioEl.controls = true;
      audioEl.preload = 'metadata';
      audioEl.style.width = '100%';
      audioEl.src = mediaUrl;
      var audioLabel = document.createElement('div');
      audioLabel.className = 'tree-sidebar-media-item__audio-label';
      audioLabel.textContent = media.caption || media.original_filename || 'Audio';
      item.appendChild(audioLabel);
      item.appendChild(audioEl);
    } else if (mType === 'document') {
      var docLink = document.createElement('a');
      docLink.href = mediaUrl;
      docLink.target = '_blank';
      docLink.rel = 'noopener';
      docLink.className = 'tree-sidebar-media-item__doc-link';
      docLink.innerHTML = '&#128196; ' + (media.caption || media.original_filename || 'Document');
      item.appendChild(docLink);
    } else {
      var trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.addEventListener('click', function() {
        if (typeof window.openLightbox === 'function') {
          window.openLightbox(mediaUrl, media.caption || root.dataset.openMediaLabel, mType === 'video' ? 'video' : 'image');
        } else {
          window.location.href = mediaUrl;
        }
      });
      if (mType === 'video') {
        var videoThumb = document.createElement('div');
        videoThumb.className = 'tree-sidebar-media-item__video-thumb';
        var thumbImg = document.createElement('img');
        thumbImg.src = '/api/media/' + media.id + '/thumbnail';
        thumbImg.alt = media.caption || 'Video';
        thumbImg.loading = 'lazy';
        thumbImg.onerror = function() { thumbImg.style.display = 'none'; };
        var playIcon = document.createElement('span');
        playIcon.className = 'tree-sidebar-media-item__play-icon';
        playIcon.textContent = '\u25B6';
        videoThumb.appendChild(thumbImg);
        videoThumb.appendChild(playIcon);
        trigger.appendChild(videoThumb);
      } else {
        var img = document.createElement('img');
        img.src = '/api/media/' + media.id + '/thumbnail';
        img.alt = media.caption || 'Family media';
        img.loading = 'lazy';
        img.onerror = function() {
          img.src = mediaUrl;
        };
        trigger.appendChild(img);
      }
      item.appendChild(trigger);
    }
    var meta = document.createElement('div');
    meta.className = 'tree-sidebar-media-item__meta';
    if (media.caption) {
      var caption = document.createElement('p');
      caption.textContent = media.caption;
      meta.appendChild(caption);
    }
    var created = document.createElement('span');
    created.className = 'tree-sidebar-media-item__date';
    created.textContent = formatDateLabel(media.created_at);
    meta.appendChild(created);
    item.appendChild(meta);

    var actions = document.createElement('div');
    actions.className = 'tree-sidebar-item-actions tree-sidebar-item-actions--compact';
    actions.appendChild(createMiniAction(root.dataset.openMediaLabel, function() {
      window.location.href = '/api/media/' + media.id + '/file';
    }));
    item.appendChild(actions);
    return item;
  }

  function renderTreeMedia(mediaItems) {
    var container = document.getElementById('tree-sidebar-media');
    if (!container) {
      return;
    }
    container.setAttribute('aria-busy', 'false');
    if (!mediaItems.length) {
      renderEmptyTreeStream(
        container,
        root.dataset.emptyMedia,
        getSidebarCanManage() ? root.dataset.addFirstPhoto : null,
        function() {
          var input = document.querySelector('#tree-media-form input[type="file"]');
          if (input) {
            input.click();
          }
        }
      );
      return;
    }
    clearNode(container);
    var grid = document.createElement('div');
    grid.className = 'tree-sidebar-media-grid';
    mediaItems.forEach(function(media) {
      grid.appendChild(createMediaNode(media));
    });
    container.appendChild(grid);
    sidebarState.highlightMediaId = '';
  }

  async function loadTreeSidebarMedia(personId) {
    var container = document.getElementById('tree-sidebar-media');
    if (!container) {
      return;
    }
    container.setAttribute('aria-busy', 'true');
    try {
      var resp = await fetch('/api/media?person_id=' + encodeURIComponent(personId));
      if (!resp.ok) {
        throw new Error(root.dataset.mediaError);
      }
      var data = await resp.json();
      renderTreeMedia(data);
    } catch (err) {
      renderEmptyTreeStream(container, err.message || root.dataset.mediaError);
    }
  }

  function initializeTreePickers() {
    var pickers = sidebarContent.querySelectorAll('[data-tree-picker]');
    Array.prototype.forEach.call(pickers, function(picker) {
      var input = picker.querySelector('[data-tree-picker-input]');
      var valueNode = picker.querySelector('[data-tree-picker-value]');
      var resultsNode = picker.querySelector('[data-tree-picker-results]');
      if (!input || !valueNode || !resultsNode) {
        return;
      }

      function closeResults() {
        resultsNode.classList.add('hidden');
        clearNode(resultsNode);
      }

      function renderResults(matches) {
        clearNode(resultsNode);
        if (!matches.length) {
          var empty = document.createElement('div');
          empty.className = 'tree-picker__empty';
          empty.textContent = root.dataset.pickerEmpty;
          resultsNode.appendChild(empty);
          resultsNode.classList.remove('hidden');
          return;
        }
        matches.slice(0, 8).forEach(function(option) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'tree-picker__result';
          button.setAttribute('role', 'option');
          button.textContent = option.display_name;
          button.addEventListener('click', function() {
            input.value = option.display_name;
            valueNode.value = option.id;
            closeResults();
          });
          resultsNode.appendChild(button);
        });
        resultsNode.classList.remove('hidden');
      }

      input.addEventListener('input', function() {
        var query = input.value.trim().toLowerCase();
        valueNode.value = '';
        if (!query) {
          closeResults();
          return;
        }
        var matches = sidebarState.peopleOptions.filter(function(option) {
          return String(option.display_name || '').toLowerCase().indexOf(query) !== -1;
        });
        renderResults(matches);
      });

      input.addEventListener('blur', function() {
        setTimeout(closeResults, 120);
      });

      input.form.addEventListener('reset', function() {
        closeResults();
      });
    });
  }

  function initializeTreeMultiPickers() {
    var pickers = sidebarContent.querySelectorAll('[data-tree-multi-picker]');
    Array.prototype.forEach.call(pickers, function(picker) {
      var input = picker.querySelector('[data-tree-multi-picker-input]');
      var valueNode = picker.querySelector('[data-tree-multi-picker-value]');
      var selectedNode = picker.querySelector('[data-tree-multi-picker-selected]');
      var resultsNode = picker.querySelector('[data-tree-multi-picker-results]');
      if (!input || !valueNode || !selectedNode || !resultsNode) {
        return;
      }

      function readSelectedIds() {
        return parseJsonArray(valueNode.value);
      }

      function writeSelectedIds(ids) {
        valueNode.value = JSON.stringify(ids);
        renderSelected(ids);
      }

      function closeResults() {
        resultsNode.classList.add('hidden');
        clearNode(resultsNode);
      }

      function renderSelected(ids) {
        clearNode(selectedNode);
        ids.forEach(function(id) {
          var option = sidebarState.peopleOptions.find(function(candidate) {
            return candidate.id === id;
          });
          if (!option) {
            return;
          }
          var token = document.createElement('span');
          token.className = 'tree-composer-token';
          var label = document.createElement('span');
          label.textContent = option.display_name;
          token.appendChild(label);
          var remove = document.createElement('button');
          remove.type = 'button';
          remove.className = 'tree-composer-token__remove';
          remove.setAttribute('aria-label', root.dataset.treeMultiPickerRemove + ' ' + option.display_name);
          remove.textContent = '×';
          remove.addEventListener('click', function() {
            writeSelectedIds(readSelectedIds().filter(function(selectedId) {
              return selectedId !== id;
            }));
          });
          token.appendChild(remove);
          selectedNode.appendChild(token);
        });
      }

      function renderResults(matches) {
        clearNode(resultsNode);
        if (!matches.length) {
          var empty = document.createElement('div');
          empty.className = 'tree-picker__empty';
          empty.textContent = root.dataset.pickerEmpty;
          resultsNode.appendChild(empty);
          resultsNode.classList.remove('hidden');
          return;
        }
        matches.slice(0, 8).forEach(function(option) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'tree-picker__result';
          button.setAttribute('role', 'option');
          button.textContent = option.display_name;
          button.addEventListener('click', function() {
            var ids = readSelectedIds();
            if (ids.indexOf(option.id) === -1) {
              ids.push(option.id);
              writeSelectedIds(ids);
            }
            input.value = '';
            closeResults();
            input.focus();
          });
          resultsNode.appendChild(button);
        });
        resultsNode.classList.remove('hidden');
      }

      input.addEventListener('input', function() {
        var query = input.value.trim().toLowerCase();
        if (!query) {
          closeResults();
          return;
        }
        var selectedIds = readSelectedIds();
        var matches = sidebarState.peopleOptions.filter(function(option) {
          return selectedIds.indexOf(option.id) === -1 &&
            String(option.display_name || '').toLowerCase().indexOf(query) !== -1;
        });
        renderResults(matches);
      });

      input.addEventListener('blur', function() {
        setTimeout(closeResults, 120);
      });

      input.form.addEventListener('reset', function() {
        setTimeout(function() {
          writeSelectedIds([]);
          closeResults();
        }, 0);
      });

      writeSelectedIds(readSelectedIds());
    });
  }

  function initializeTreeMediaComposer() {
    var form = document.getElementById('tree-media-form');
    if (!form) {
      return;
    }
    var fileInput = form.querySelector('input[type="file"]');
    var nameNode = document.getElementById('tree-media-file-name');
    if (!fileInput || !nameNode) {
      return;
    }

    function syncMediaFileName() {
      var listNode = document.getElementById('tree-media-file-list');
      renderComposerFiles(fileInput, nameNode, listNode);
    }

    fileInput.addEventListener('change', syncMediaFileName);
    syncMediaFileName();
  }

  function initializeTreeSidebar(personId) {
    parseSidebarPeopleOptions();
    initializeTreePickers();
    initializeTreeMultiPickers();
    initializeTreeMediaComposer();
    switchTreeSidebarTab(chooseDefaultSidebarTab(), sidebarState.relationshipGroup);
    applyRelationshipHighlights();
    updateGraphModeBanner();
  }

  function resolvePhotoHref(photoUrl) {
    if (!photoUrl) {
      return '';
    }
    if (photoUrl.indexOf('http') === 0 || photoUrl.indexOf('/') === 0) {
      return photoUrl;
    }
    return '/api/media/' + photoUrl + '/file';
  }

  function relationshipPayload(personId, relatedId, mode, relationshipMeta) {
    var meta = relationshipMeta || {};
    if (mode === 'parent') {
      return {
        endpoint: '/api/relationships/parent-child',
        body: {
          parent_id: relatedId,
          child_id: personId,
          kind: meta.kind || 'biological',
          confidence: meta.confidence,
          source: meta.source,
          source_detail: meta.source_detail,
          notes: meta.notes,
          start_date: meta.start_date,
          end_date: meta.end_date
        }
      };
    }
    if (mode === 'child') {
      return {
        endpoint: '/api/relationships/parent-child',
        body: {
          parent_id: personId,
          child_id: relatedId,
          kind: meta.kind || 'biological',
          confidence: meta.confidence,
          source: meta.source,
          source_detail: meta.source_detail,
          notes: meta.notes,
          start_date: meta.start_date,
          end_date: meta.end_date
        }
      };
    }
    return {
      endpoint: '/api/relationships/partnership',
      body: {
        person_a_id: personId,
        person_b_id: relatedId,
        kind: meta.kind || 'married',
        status: meta.status || 'active',
        start_date: meta.start_date,
        start_date_precision: meta.start_date_precision,
        end_date: meta.end_date,
        end_date_precision: meta.end_date_precision,
        source: meta.source,
        notes: meta.notes
      }
    };
  }

  function setError(nodeId, message) {
    var node = document.getElementById(nodeId);
    if (!node) return;
    node.textContent = message || '';
    node.classList.toggle('hidden', !message);
  }

  function clearErrors() {
    setError('tree-person-edit-error', '');
    setError('tree-relationship-error', '');
  }

  function formDataToJson(form, options) {
    var opts = options || {};
    var nullableFields = opts.nullableFields || [];
    var formData = new FormData(form);
    var payload = {};
    formData.forEach(function(value, key) {
      if (typeof value === 'string') {
        var trimmed = value.trim();
        if (trimmed !== '') {
          payload[key] = trimmed;
        } else if (nullableFields.indexOf(key) !== -1) {
          payload[key] = null;
        }
      }
    });
    return payload;
  }

  function relationshipMetaFromForm(form, mode) {
    var raw = formDataToJson(form, {
      nullableFields: ['confidence', 'source_detail', 'notes', 'start_date', 'end_date']
    });
    if (mode === 'partner') {
      return {
        kind: raw.kind || 'married',
        status: raw.status || 'active',
        start_date: raw.start_date,
        start_date_precision: raw.start_date_precision,
        end_date: raw.end_date,
        end_date_precision: raw.end_date_precision,
        source: raw.source,
        notes: raw.notes
      };
    }
    return {
      kind: raw.kind || 'biological',
      confidence: raw.confidence || 'confirmed',
      source: raw.source,
      source_detail: raw.source_detail,
      notes: raw.notes,
      start_date: raw.start_date,
      end_date: raw.end_date
    };
  }

  function treeRelativeCreatePayload(form) {
    var payload = {};
    ['first_name', 'last_name', 'branch'].forEach(function(field) {
      var input = form.querySelector('[name="' + field + '"]');
      if (!input) {
        return;
      }
      var value = String(input.value || '').trim();
      if (value) {
        payload[field] = value;
      }
    });
    return payload;
  }

  async function loadPreferences() {
    var resp = await fetch('/api/tree/preferences');
    if (resp.status === 401) {
      window.location.href = '/login';
      return false;
    }
    preferences = await resp.json();
    syncPreferenceInputs();
    return true;
  }

  async function savePreferences() {
    readPreferenceInputs();
    var resp = await fetch('/api/tree/preferences', {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(preferences)
    });
    if (resp.status === 401) {
      window.location.href = '/login';
      return;
    }
    preferences = await resp.json();
    syncPreferenceInputs();
    render();
  }

  async function fetchTreeData() {
    var resp = await fetch('/api/tree' + queryString(currentFilters()));
    if (resp.status === 401) {
      window.location.href = '/login';
      return null;
    }
    return await resp.json();
  }

  async function loadTree() {
    setStatus(document.body.dataset.loadingText || 'Loading...');
    treeData = await fetchTreeData();
    if (!treeData) {
      return;
    }
    render();
  }

  async function renderSidebar(personId) {
    currentSidebarPersonId = personId;
    var clearedGraphMode = false;
    if (sidebarState.graphMode && sidebarState.graphMode.sourcePersonId !== personId) {
      sidebarState.graphMode = null;
      clearedGraphMode = true;
    }
    sidebarContent.setAttribute('aria-busy', 'true');
    var resp = await fetch('/people/' + personId + '/card');
    var html = await resp.text();
    window.replaceNodeChildrenFromHTML(sidebarContent, html);
    sidebarContent.setAttribute('aria-busy', 'false');
    initializeTreeSidebar(personId);
    if (clearedGraphMode && treeData) {
      render();
    }
  }

  async function init() {
    try {
      initialUrlFocusPersonId = readFocusParamFromUrl();
      setStatus(document.body.dataset.loadingText || 'Loading...');
      var initialState = await Promise.all([
        loadPreferences(),
        fetchTreeData()
      ]);
      if (!initialState[0] || !initialState[1]) {
        return;
      }
      treeData = initialState[1];
      render();
    } catch (err) {
      document.getElementById('tree-page').textContent = root.dataset.loadError;
    }
  }

  function drawEmptyState(w, h) {
    g.append('text')
      .attr('x', w / 2)
      .attr('y', h / 2 - 30)
      .attr('text-anchor', 'middle')
      .attr('fill', '#6b6054')
      .text(root.dataset.emptyText);

    // Add first person CTA
    var ctaLabel = root.dataset.treeAddFirstPerson || 'Add your first family member';
    var ctaGroup = g.append('g')
      .attr('transform', 'translate(' + (w / 2) + ',' + (h / 2 + 10) + ')')
      .style('cursor', 'pointer');
    ctaGroup.append('circle')
      .attr('r', 20)
      .attr('fill', 'var(--green-pale, #d9eac9)')
      .attr('stroke', 'var(--green-mid, #7da362)')
      .attr('stroke-width', 2);
    ctaGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('fill', 'var(--green-deep, #2d5016)')
      .attr('font-size', '22px')
      .attr('font-weight', '700')
      .attr('pointer-events', 'none')
      .text('+');
    ctaGroup.append('text')
      .attr('y', 34)
      .attr('text-anchor', 'middle')
      .attr('fill', '#6b6054')
      .attr('font-size', '13px')
      .text(ctaLabel);
    ctaGroup.on('click', function() {
      window.openAddPersonPanel();
    });

    setStatus(root.dataset.statusTemplate.replace('{count}', '0'));
  }

  function buildTreeStructures() {
    var personsById = {};
    treeData.persons.forEach(function(person) {
      personsById[person.id] = person;
    });

    var childToParents = {};
    var parentToChildren = {};
    var partnerMap = {};
    var partnershipByPair = {};
    var partnershipsByPair = {};
    var parentChildByEdge = {};

    function pushUnique(map, key, value) {
      if (!map[key]) {
        map[key] = [];
      }
      if (map[key].indexOf(value) === -1) {
        map[key].push(value);
      }
    }

    function partnershipPriority(partnership) {
      if (!partnership) {
        return -1;
      }
      var statusScore = partnership.status === 'active'
        ? 4
        : partnership.status === 'widowed'
          ? 3
          : partnership.status === 'separated'
            ? 2
            : partnership.status === 'dissolved'
              ? 1
              : 0;
      var dateScore = Number(String(partnership.start_date || '').replace(/-/g, '')) || 0;
      return statusScore * 100000000 + dateScore;
    }

    treeData.parent_child.forEach(function(parentChild) {
      if (!childToParents[parentChild.child_id]) {
        childToParents[parentChild.child_id] = [];
      }
      childToParents[parentChild.child_id].push(parentChild.parent_id);
      if (!parentToChildren[parentChild.parent_id]) {
        parentToChildren[parentChild.parent_id] = [];
      }
      parentToChildren[parentChild.parent_id].push(parentChild.child_id);
      parentChildByEdge[parentChild.parent_id + '|' + parentChild.child_id] = parentChild;
    });

    treeData.partnerships.forEach(function(partnership) {
      var pair = [partnership.person_a_id, partnership.person_b_id].sort();
      var key = pair.join('|');
      if (!partnershipsByPair[key]) {
        partnershipsByPair[key] = [];
      }
      partnershipsByPair[key].push(partnership);
      if (!partnershipByPair[key] || partnershipPriority(partnership) >= partnershipPriority(partnershipByPair[key])) {
        partnershipByPair[key] = partnership;
      }
      pushUnique(partnerMap, pair[0], pair[1]);
      pushUnique(partnerMap, pair[1], pair[0]);
    });

    var familyUnitsByKey = {};
    var familyUnitsByPair = {};

    function ensureFamilyUnit(key, payload) {
      if (!familyUnitsByKey[key]) {
        familyUnitsByKey[key] = {
          id: 'family-unit:' + key,
          key: key,
          renderKey: payload.renderKey || key,
          parentIds: (payload.parentIds || []).slice(),
          childIds: [],
          explicitPartnership: !!payload.explicitPartnership,
          partnership: payload.partnership || null,
          partnershipKind: payload.partnershipKind || null,
          partnershipStatus: payload.partnershipStatus || null,
          unitType: payload.unitType || 'family'
        };
      } else if (payload.partnership && !familyUnitsByKey[key].partnership) {
        familyUnitsByKey[key].partnership = payload.partnership;
        familyUnitsByKey[key].partnershipKind = payload.partnershipKind || familyUnitsByKey[key].partnershipKind;
        familyUnitsByKey[key].partnershipStatus = payload.partnershipStatus || familyUnitsByKey[key].partnershipStatus;
        familyUnitsByKey[key].explicitPartnership = familyUnitsByKey[key].explicitPartnership || !!payload.explicitPartnership;
      }
      return familyUnitsByKey[key];
    }

    Object.keys(partnershipByPair).forEach(function(pairKey) {
      var primaryPartnership = partnershipByPair[pairKey];
      ensureFamilyUnit('pair:' + pairKey, {
        renderKey: pairKey,
        parentIds: pairKey.split('|'),
        explicitPartnership: true,
        partnership: primaryPartnership,
        partnershipKind: primaryPartnership.kind || 'married',
        partnershipStatus: primaryPartnership.status || 'active',
        unitType: 'pair'
      });
    });

    Object.keys(childToParents).forEach(function(childId) {
      var parentIds = Array.from(new Set((childToParents[childId] || []).filter(Boolean))).sort();
      if (!parentIds.length) {
        return;
      }
      var selectedParents = null;
      if (parentIds.length === 1) {
        selectedParents = [parentIds[0]];
      } else if (parentIds.length === 2) {
        selectedParents = parentIds.slice();
      } else {
        selectedParents = choosePrimaryParentPair(parentIds, partnershipByPair) || parentIds.slice(0, 2);
      }
      if (!selectedParents || !selectedParents.length) {
        return;
      }
      var unitKey = selectedParents.length === 1
        ? 'single:' + selectedParents[0]
        : 'pair:' + selectedParents.slice().sort().join('|');
      var pairKey = selectedParents.length === 2 ? selectedParents.slice().sort().join('|') : '';
      var primaryPartnership = pairKey ? (partnershipByPair[pairKey] || null) : null;
      var unit = ensureFamilyUnit(unitKey, {
        renderKey: pairKey || unitKey,
        parentIds: selectedParents,
        explicitPartnership: !!primaryPartnership,
        partnership: primaryPartnership,
        partnershipKind: primaryPartnership ? primaryPartnership.kind : null,
        partnershipStatus: primaryPartnership ? primaryPartnership.status : null,
        unitType: selectedParents.length === 1 ? 'single-parent' : 'pair'
      });
      if (unit.childIds.indexOf(childId) === -1) {
        unit.childIds.push(childId);
      }
      if (selectedParents.length === 2) {
        if (!familyUnitsByPair[pairKey]) {
          familyUnitsByPair[pairKey] = [];
        }
        if (familyUnitsByPair[pairKey].indexOf(childId) === -1) {
          familyUnitsByPair[pairKey].push(childId);
        }
        pushUnique(partnerMap, selectedParents[0], selectedParents[1]);
        pushUnique(partnerMap, selectedParents[1], selectedParents[0]);
      }
    });

    var familyUnits = Object.keys(familyUnitsByKey).map(function(key) {
      return familyUnitsByKey[key];
    });
    var familyUnitsByPerson = {};
    var incomingFamilyUnitByChild = {};
    familyUnits.forEach(function(unit) {
      unit.parentIds.forEach(function(parentId) {
        pushUnique(familyUnitsByPerson, parentId, unit.key);
      });
      unit.childIds.forEach(function(childId) {
        pushUnique(familyUnitsByPerson, childId, unit.key);
        if (!incomingFamilyUnitByChild[childId] || unit.parentIds.length > familyUnitsByKey[incomingFamilyUnitByChild[childId]].parentIds.length) {
          incomingFamilyUnitByChild[childId] = unit.key;
        }
      });
    });

    return {
      personsById: personsById,
      childToParents: childToParents,
      parentToChildren: parentToChildren,
      partnerMap: partnerMap,
      partnershipByPair: partnershipByPair,
      partnershipsByPair: partnershipsByPair,
      familyUnitsByPair: familyUnitsByPair,
      familyUnits: familyUnits,
      familyUnitsByPerson: familyUnitsByPerson,
      incomingFamilyUnitByChild: incomingFamilyUnitByChild,
      parentChildByEdge: parentChildByEdge
    };
  }

  function determineRootId(personsById, childToParents) {
    var rootId = treeData.root_id;
    if (!rootId || !personsById[rootId]) {
      var allChildIds = new Set(Object.keys(childToParents));
      var rootCandidates = treeData.persons.filter(function(person) {
        return !allChildIds.has(person.id);
      });
      rootId = rootCandidates.length > 0 ? rootCandidates[0].id : treeData.persons[0].id;
    }
    return rootId;
  }

  function layoutTree(rootId, parentToChildren, childToParents, partnerMap, familyUnitsByPair, partnershipByPair, familyUnits, familyUnitsByPerson, incomingFamilyUnitByChild, viewportWidth) {
    var visited = new Set();
    var nodePositions = {};
    var nodeLookup = {};
    var components = [];

    function buildHierarchy(rootNodeId) {
      // Phase 1: Direction-aware BFS to assign generation depths.
      // Children go deeper (+1), parents go shallower (-1), partners stay level (0).
      var depthOf = {};
      depthOf[rootNodeId] = 0;
      visited.add(rootNodeId);
      var bfsQueue = [rootNodeId];
      var componentIds = [rootNodeId];

      while (bfsQueue.length > 0) {
        var nid = bfsQueue.shift();
        var d = depthOf[nid];
        (parentToChildren[nid] || []).forEach(function(cid) {
          if (!visited.has(cid)) {
            visited.add(cid);
            depthOf[cid] = d + 1;
            bfsQueue.push(cid);
            componentIds.push(cid);
          }
        });
        (childToParents[nid] || []).forEach(function(pid) {
          if (!visited.has(pid)) {
            visited.add(pid);
            depthOf[pid] = d - 1;
            bfsQueue.push(pid);
            componentIds.push(pid);
          }
        });
        (partnerMap[nid] || []).forEach(function(partnerId) {
          if (!visited.has(partnerId)) {
            visited.add(partnerId);
            depthOf[partnerId] = d;
            bfsQueue.push(partnerId);
            componentIds.push(partnerId);
          }
        });
      }

      // Normalize so minimum depth = 0
      var minD = 0;
      componentIds.forEach(function(id) { if (depthOf[id] < minD) minD = depthOf[id]; });
      if (minD < 0) {
        componentIds.forEach(function(id) { depthOf[id] -= minD; });
      }

      // Phase 2: Build layout tree from depth assignments.
      // Each node's layout-children are connected people at exactly depth+1.
      var placed = {};
      function buildNode(id) {
        placed[id] = true;
        var nd = depthOf[id];
        var node = {id: id, children: [], depth: nd, x: 0, y: 0};
        var partners = [];
        (partnerMap[id] || []).forEach(function(partnerId) {
          if (!placed[partnerId] && depthOf[partnerId] === nd) {
            partners.push(partnerId);
          }
        });
        partners.sort(function(a, b) {
          var aHasFamily = ((familyUnitsByPair[[a, id].sort().join('|')] || []).length) > 0;
          var bHasFamily = ((familyUnitsByPair[[b, id].sort().join('|')] || []).length) > 0;
          if (aHasFamily !== bHasFamily) {
            return aHasFamily ? -1 : 1;
          }
          return a.localeCompare(b);
        });
        partners.forEach(function(partnerId) {
          if (!placed[partnerId]) {
            var partnerNode = buildNode(partnerId);
            partnerNode.parent = node;
            node.children.push(partnerNode);
          }
        });
        var deeper = [];
        (parentToChildren[id] || []).forEach(function(cid) {
          if (!placed[cid] && depthOf[cid] === nd + 1) deeper.push(cid);
        });
        (childToParents[id] || []).forEach(function(pid) {
          if (!placed[pid] && depthOf[pid] === nd + 1) deeper.push(pid);
        });
        deeper.forEach(function(childId) {
          if (!placed[childId]) {
            var childNode = buildNode(childId);
            childNode.parent = node;
            node.children.push(childNode);
          }
        });
        return node;
      }

      // Start from the shallowest node (prefer designated root if tied)
      var topId = componentIds[0];
      componentIds.forEach(function(id) {
        if (depthOf[id] < depthOf[topId]) topId = id;
      });
      if (depthOf[rootNodeId] === depthOf[topId]) topId = rootNodeId;

      var root = buildNode(topId);

      // Attach any unplaced component members (shouldn't happen, but safety net)
      componentIds.forEach(function(id) {
        if (!placed[id]) {
          var orphan = buildNode(id);
          orphan.parent = root;
          root.children.push(orphan);
        }
      });

      return root;
    }

    function applyLayout(node, xStart, yOffset, maxDepth) {
      node.y = yOffset + (node.depth * NODE_SPACING_Y);
      if (node.depth > maxDepth.value) {
        maxDepth.value = node.depth;
      }

      if (node.children.length === 0) {
        node.x = xStart + NODE_SPACING_X / 2;
        return xStart + NODE_SPACING_X;
      }

      var nextX = xStart;
      node.children.forEach(function(child) {
        nextX = applyLayout(child, nextX, yOffset, maxDepth);
      });

      var first = node.children[0];
      var last = node.children[node.children.length - 1];
      node.x = (first.x + last.x) / 2;
      return nextX;
    }

    function collectComponentNodes(rootNode) {
      var nodes = [];
      function walk(node) {
        nodes.push(node);
        nodeLookup[node.id] = node;
        nodePositions[node.id] = {x: node.x, y: node.y};
        node.children.forEach(walk);
      }
      walk(rootNode);
      return nodes;
    }

    function componentBounds(nodes) {
      var minX = Infinity;
      var maxX = -Infinity;
      var minY = Infinity;
      var maxY = -Infinity;
      nodes.forEach(function(node) {
        minX = Math.min(minX, node.x);
        maxX = Math.max(maxX, node.x);
        minY = Math.min(minY, node.y);
        maxY = Math.max(maxY, node.y);
      });
      return {
        minX: minX,
        maxX: maxX,
        minY: minY,
        maxY: maxY,
        width: Math.max(maxX - minX, 0),
        height: Math.max(maxY - minY, 0)
      };
    }

    function shiftComponent(component, dx, dy) {
      component.nodes.forEach(function(node) {
        node.x += dx;
        node.y += dy;
        nodePositions[node.id].x = node.x;
        nodePositions[node.id].y = node.y;
      });
      component.bounds = componentBounds(component.nodes);
    }

    function average(values) {
      if (!values.length) {
        return null;
      }
      return values.reduce(function(total, value) {
        return total + value;
      }, 0) / values.length;
    }

    function ancestryAnchorX(personId, depth) {
      return average((childToParents[personId] || []).map(function(parentId) {
        var parentNode = nodeLookup[parentId];
        if (!parentNode || parentNode.depth >= depth || !nodePositions[parentId]) {
          return null;
        }
        return nodePositions[parentId].x;
      }).filter(function(value) {
        return value !== null;
      }));
    }

    function packComponentRows(component) {
      var rowsByDepth = {};
      component.nodes.forEach(function(node) {
        if (!rowsByDepth[node.depth]) {
          rowsByDepth[node.depth] = [];
        }
        rowsByDepth[node.depth].push(node);
      });

      function familyUnitCenter(unit) {
        var values = [];
        unit.parentIds.forEach(function(parentId) {
          if (nodePositions[parentId]) {
            values.push(nodePositions[parentId].x);
          }
        });
        unit.childIds.forEach(function(childId) {
          if (nodePositions[childId]) {
            values.push(nodePositions[childId].x);
          }
        });
        return average(values) || 0;
      }

      function nodeDesiredCenter(node, unitCenters) {
        var anchors = [node.x];
        var ancestryAnchor = ancestryAnchorX(node.id, node.depth);
        if (ancestryAnchor !== null && ancestryAnchor !== undefined) {
          anchors.push(ancestryAnchor);
        }
        var childAverage = average((parentToChildren[node.id] || []).map(function(childId) {
          return nodePositions[childId] ? nodePositions[childId].x : null;
        }).filter(function(value) {
          return value !== null && value !== undefined;
        }));
        if (childAverage !== null && childAverage !== undefined) {
          anchors.push(childAverage);
        }
        var incomingUnitKey = incomingFamilyUnitByChild[node.id];
        if (incomingUnitKey && unitCenters[incomingUnitKey] !== undefined) {
          anchors.push(unitCenters[incomingUnitKey]);
        }
        (familyUnitsByPerson[node.id] || []).forEach(function(unitKey) {
          if (unitCenters[unitKey] !== undefined) {
            anchors.push(unitCenters[unitKey]);
          }
        });
        return average(anchors.filter(function(value) {
          return value !== null && value !== undefined;
        })) || node.x;
      }

      for (var pass = 0; pass < 4; pass += 1) {
        var unitCenters = {};
        (familyUnits || []).forEach(function(unit) {
          unitCenters[unit.key] = familyUnitCenter(unit);
        });

        Object.keys(rowsByDepth).forEach(function(depthKey) {
          var rowNodes = rowsByDepth[depthKey].slice().sort(function(a, b) {
            return a.x - b.x;
          });
          var nodeById = {};
          rowNodes.forEach(function(node) {
            nodeById[node.id] = node;
          });

          var rowPeerGraph = {};
          rowNodes.forEach(function(node) {
            rowPeerGraph[node.id] = [];
          });

          (familyUnits || []).forEach(function(unit) {
            var unitParentIds = unit.parentIds.filter(function(parentId) {
              var parentNode = nodeById[parentId];
              return !!parentNode;
            });
            if (unitParentIds.length < 2) {
              return;
            }
            for (var index = 0; index < unitParentIds.length; index += 1) {
              for (var otherIndex = index + 1; otherIndex < unitParentIds.length; otherIndex += 1) {
                pushUnique(rowPeerGraph, unitParentIds[index], unitParentIds[otherIndex]);
                pushUnique(rowPeerGraph, unitParentIds[otherIndex], unitParentIds[index]);
              }
            }
          });

          var claimed = {};
          var items = [];
          rowNodes.forEach(function(node) {
            if (claimed[node.id]) {
              return;
            }
            var queue = [node.id];
            var componentIds = [];
            while (queue.length) {
              var currentId = queue.shift();
              if (claimed[currentId]) {
                continue;
              }
              claimed[currentId] = true;
              componentIds.push(currentId);
              (rowPeerGraph[currentId] || []).forEach(function(peerId) {
                if (!claimed[peerId]) {
                  queue.push(peerId);
                }
              });
            }
            if (componentIds.length === 1) {
              items.push({
                type: 'single',
                ids: componentIds,
                desiredCenter: nodeDesiredCenter(nodeById[componentIds[0]], unitCenters),
                width: Math.max(NODE_SPACING_X * 0.92, (treeNodeLabel(lookupPerson(componentIds[0])).length * 7))
              });
              return;
            }
            var orderedIds = componentIds.slice().sort(function(aId, bId) {
              var aNode = nodeById[aId];
              var bNode = nodeById[bId];
              var aDesired = nodeDesiredCenter(aNode, unitCenters);
              var bDesired = nodeDesiredCenter(bNode, unitCenters);
              if (aDesired !== bDesired) {
                return aDesired - bDesired;
              }
              return aNode.x - bNode.x;
            });
            var componentDegrees = {};
            componentIds.forEach(function(personId) {
              componentDegrees[personId] = (rowPeerGraph[personId] || []).filter(function(peerId) {
                return componentIds.indexOf(peerId) !== -1;
              }).length;
            });
            var pathEndpoints = componentIds.filter(function(personId) {
              return componentDegrees[personId] <= 1;
            }).sort(function(aId, bId) {
              return nodeDesiredCenter(nodeById[aId], unitCenters) - nodeDesiredCenter(nodeById[bId], unitCenters);
            });
            if (pathEndpoints.length) {
              var walkedIds = [];
              var seenIds = {};
              var currentId = pathEndpoints[0];
              var previousId = '';
              while (currentId && !seenIds[currentId]) {
                walkedIds.push(currentId);
                seenIds[currentId] = true;
                var nextIds = (rowPeerGraph[currentId] || []).filter(function(peerId) {
                  return componentIds.indexOf(peerId) !== -1 && peerId !== previousId && !seenIds[peerId];
                });
                previousId = currentId;
                currentId = nextIds.length ? nextIds.sort(function(aId, bId) {
                  return nodeDesiredCenter(nodeById[aId], unitCenters) - nodeDesiredCenter(nodeById[bId], unitCenters);
                })[0] : '';
              }
              if (walkedIds.length === componentIds.length) {
                orderedIds = walkedIds;
              }
            }
            var desiredCenter = average(orderedIds.map(function(personId) {
              return nodeDesiredCenter(nodeById[personId], unitCenters);
            }));
            items.push({
              type: 'cluster',
              ids: orderedIds,
              desiredCenter: desiredCenter,
              width: Math.max((orderedIds.length - 1) * PARTNER_GAP_X + NODE_SPACING_X * 0.9, orderedIds.length * 84)
            });
          });

          items.sort(function(a, b) {
            return a.desiredCenter - b.desiredCenter;
          });

          var previousRight = null;
          items.forEach(function(item) {
            var halfWidth = item.width / 2;
            var center = item.desiredCenter;
            if (previousRight !== null) {
              center = Math.max(center, previousRight + FAMILY_UNIT_GAP_X / 2 + halfWidth);
            }
            item.center = center;
            previousRight = center + halfWidth;
          });

          items.forEach(function(item) {
            if (item.type === 'single') {
              var singleId = item.ids[0];
              if (nodeLookup[singleId]) {
                nodeLookup[singleId].x = item.center;
                nodePositions[singleId].x = item.center;
              }
              return;
            }
            var spanStart = item.center - ((item.ids.length - 1) * PARTNER_GAP_X) / 2;
            item.ids.forEach(function(personId, memberIndex) {
              var memberX = spanStart + memberIndex * PARTNER_GAP_X;
              if (nodeLookup[personId]) {
                nodeLookup[personId].x = memberX;
                nodePositions[personId].x = memberX;
              }
            });
          });
        });
      }
    }

    var rootNode = buildHierarchy(rootId);
    var maxDepth = {value: 0};
    applyLayout(rootNode, 0, 0, maxDepth);
    components.push({
      id: rootNode.id,
      isPrimary: true,
      nodes: collectComponentNodes(rootNode),
      bounds: null
    });

    var unvisited = treeData.persons.filter(function(person) {
      return !visited.has(person.id);
    });
    while (unvisited.length > 0) {
      var componentRoot = buildHierarchy(unvisited[0].id);
      var componentMaxDepth = {value: 0};
      applyLayout(componentRoot, 0, 0, componentMaxDepth);
      components.push({
        id: componentRoot.id,
        isPrimary: false,
        nodes: collectComponentNodes(componentRoot),
        bounds: null
      });
      unvisited = treeData.persons.filter(function(person) {
        return !visited.has(person.id);
      });
    }

    components.forEach(function(component) {
      packComponentRows(component);
      component.bounds = componentBounds(component.nodes);
    });

    var primaryComponent = components[0];
    shiftComponent(primaryComponent, COMPONENT_PADDING_X - primaryComponent.bounds.minX, 60 - primaryComponent.bounds.minY);

    var availableWidth = Math.max((viewportWidth || 1400) - 120, 520);
    var detachedTop = primaryComponent.bounds.maxY + NODE_SPACING_Y;
    var cursorX = 40;
    var cursorY = detachedTop;
    var rowMaxHeight = 0;
    components.slice(1).forEach(function(component) {
      var neededWidth = component.bounds.width + COMPONENT_PADDING_X * 2;
      var neededHeight = component.bounds.height + COMPONENT_PADDING_Y * 2;
      if (cursorX > 40 && cursorX + neededWidth > availableWidth) {
        cursorX = 40;
        cursorY += rowMaxHeight + DETACHED_COMPONENT_GAP_Y;
        rowMaxHeight = 0;
      }
      shiftComponent(
        component,
        cursorX + COMPONENT_PADDING_X - component.bounds.minX,
        cursorY + COMPONENT_PADDING_Y - component.bounds.minY
      );
      cursorX += neededWidth + DETACHED_COMPONENT_GAP_X;
      rowMaxHeight = Math.max(rowMaxHeight, neededHeight);
    });

    var allNodes = [];
    components.forEach(function(component) {
      component.bounds = componentBounds(component.nodes);
      component.nodes.forEach(function(node) {
        allNodes.push(node);
      });
    });

    function orderedPairIds(aId, bId, desiredCenter) {
      var aNode = nodeLookup[aId];
      var bNode = nodeLookup[bId];
      var aAnchor = ancestryAnchorX(aId, aNode ? aNode.depth : 0);
      var bAnchor = ancestryAnchorX(bId, bNode ? bNode.depth : 0);

      if (aAnchor !== null && bAnchor !== null && aAnchor !== bAnchor) {
        return aAnchor < bAnchor ? [aId, bId] : [bId, aId];
      }
      if (aAnchor !== null && bAnchor === null) {
        return aAnchor <= desiredCenter ? [aId, bId] : [bId, aId];
      }
      if (bAnchor !== null && aAnchor === null) {
        return bAnchor <= desiredCenter ? [bId, aId] : [aId, bId];
      }
      if (aNode && bNode && aNode.x !== bNode.x) {
        return aNode.x < bNode.x ? [aId, bId] : [bId, aId];
      }
      return [aId, bId];
    }

    return {
      allNodes: allNodes,
      nodePositions: nodePositions,
      components: components,
      primaryComponent: primaryComponent
    };
  }

  function addMetricPill(nodeGroup, person, baseY) {
    var metrics = [];
    if (person.media_count) metrics.push('Md ' + person.media_count);
    if (!metrics.length) {
      return;
    }

    var label = metrics.join(' · ');
    var width = Math.max(52, label.length * 5.9 + 14);
    nodeGroup.append('rect')
      .attr('class', 'metric-pill')
      .attr('x', -(width / 2))
      .attr('y', baseY - 10)
      .attr('width', width)
      .attr('height', 16);
    nodeGroup.append('text')
      .attr('class', 'metric-label')
      .attr('y', baseY + 1)
      .text(label);
  }

  function collectFamilyUnits(structures, layout, pcKindLookup) {
    var familyUnits = [];
    var coveredEdges = {};
    (structures.familyUnits || []).forEach(function(structuralUnit) {
      var parentIds = (structuralUnit.parentIds || []).filter(function(parentId) {
        return !!layout.nodePositions[parentId];
      });
      if (!parentIds.length) {
        return;
      }
      var childIds = (structuralUnit.childIds || []).filter(function(childId) {
        return !!layout.nodePositions[childId];
      });
      if (!childIds.length) {
        return;
      }
      var renderChildIds = [];
      var childKinds = {};
      childIds.forEach(function(childId) {
        var edgeKinds = parentIds.map(function(parentId) {
          return pcKindLookup[parentId + '|' + childId] || null;
        }).filter(Boolean);
        if (!edgeKinds.length) {
          return;
        }
        var firstKind = edgeKinds[0];
        var allSameKind = edgeKinds.every(function(kind) {
          return kind === firstKind;
        });
        if (!allSameKind) {
          return;
        }
        renderChildIds.push(childId);
        childKinds[childId] = firstKind;
        parentIds.forEach(function(parentId) {
          coveredEdges[parentId + '|' + childId] = true;
        });
      });
      var renderByKind = {};
      renderChildIds.forEach(function(childId) {
        var renderKind = childKinds[childId] || 'biological';
        if (!renderByKind[renderKind]) {
          renderByKind[renderKind] = [];
        }
        renderByKind[renderKind].push(childId);
      });
      Object.keys(renderByKind).forEach(function(renderKind) {
        familyUnits.push({
          key: structuralUnit.key + '|kind:' + renderKind,
          renderKey: structuralUnit.renderKey,
          parentIds: parentIds.slice(),
          childIds: childIds.slice(),
          renderChildIds: renderByKind[renderKind].slice(),
          childKinds: childKinds,
          partnershipKind: structuralUnit.partnershipKind || null,
          partnershipStatus: structuralUnit.partnershipStatus || null,
          unitType: structuralUnit.unitType || 'family'
        });
      });
    });

    familyUnits.forEach(function(unit) {
      unit.childIds.sort(function(a, b) {
        return layout.nodePositions[a].x - layout.nodePositions[b].x;
      });
      unit.renderChildIds.sort(function(a, b) {
        return layout.nodePositions[a].x - layout.nodePositions[b].x;
      });
    });

    return {
      familyUnits: familyUnits,
      coveredEdges: coveredEdges
    };
  }

  function drawGenerationBands(layout) {
    var targetNodes = layout && layout.primaryComponent ? layout.primaryComponent.nodes : layout.allNodes;
    var levels = {};
    targetNodes.forEach(function(node) {
      levels[node.depth] = node.y;
    });
    var depths = Object.keys(levels).map(function(depth) {
      return Number(depth);
    }).sort(function(a, b) {
      return a - b;
    });
    if (!depths.length) {
      return;
    }

    var minX = Infinity;
    var maxX = -Infinity;
    targetNodes.forEach(function(node) {
      minX = Math.min(minX, node.x);
      maxX = Math.max(maxX, node.x);
    });

    var bandGroup = g.append('g').attr('class', 'generation-bands');
    depths.forEach(function(depth, index) {
      var y = levels[depth];
      var top = y - (NODE_SPACING_Y / 2) + 18;
      bandGroup.append('rect')
        .attr('class', 'generation-band' + (index % 2 === 0 ? ' generation-band--even' : ' generation-band--odd'))
        .attr('x', minX - 180)
        .attr('y', top)
        .attr('width', (maxX - minX) + 360)
        .attr('height', NODE_SPACING_Y - 36)
        .attr('rx', 24)
        .attr('ry', 24);
      bandGroup.append('text')
        .attr('class', 'generation-band__label')
        .attr('x', minX - 150)
        .attr('y', top + 28)
        .text(formatTemplate(root.dataset.treeGenerationTemplate, {index: index + 1}));
    });
  }

  function drawComponentFrames(layout) {
    if (!layout || !layout.components || layout.components.length < 2) {
      return;
    }
    var frameGroup = g.append('g').attr('class', 'tree-component-frames');
    var detachedIndex = 0;
    layout.components.forEach(function(component) {
      if (component.isPrimary || !component.bounds) {
        return;
      }
      detachedIndex += 1;
      var frameX = component.bounds.minX - COMPONENT_PADDING_X * 0.55;
      var frameY = component.bounds.minY - COMPONENT_PADDING_Y * 0.7;
      var frameWidth = component.bounds.width + COMPONENT_PADDING_X * 1.1;
      var frameHeight = component.bounds.height + COMPONENT_PADDING_Y * 1.35;
      frameGroup.append('rect')
        .attr('class', 'tree-component-frame')
        .attr('x', frameX)
        .attr('y', frameY)
        .attr('width', frameWidth)
        .attr('height', frameHeight)
        .attr('rx', 24)
        .attr('ry', 24)
        .attr('data-component-root', component.id);
      frameGroup.append('text')
        .attr('class', 'tree-component-label')
        .attr('x', frameX + 20)
        .attr('y', frameY + 28)
        .text(formatTemplate(root.dataset.treeDetachedComponentTemplate, {index: detachedIndex}));
    });
  }

  function appendTreeDefs() {
    var defs = svg.append('defs');
    defs.append('marker')
      .attr('id', 'tree-parent-arrow')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 8)
      .attr('refY', 5)
      .attr('markerWidth', 7)
      .attr('markerHeight', 7)
      .attr('orient', 'auto-start-reverse')
      .append('path')
      .attr('d', 'M 0 0 L 10 5 L 0 10 z')
      .attr('class', 'tree-parent-arrow');
  }

  function applyContextHighlight(personId, structures) {
    if (!personId || !structures) {
      return;
    }
    var relatedIds = new Set([personId]);
    (structures.parentToChildren[personId] || []).forEach(function(id) { relatedIds.add(id); });
    (structures.childToParents[personId] || []).forEach(function(id) { relatedIds.add(id); });
    (structures.partnerMap[personId] || []).forEach(function(id) { relatedIds.add(id); });

    d3.selectAll('.tree-node').classed('tree-node--context', function() {
      return relatedIds.has(d3.select(this).attr('data-person-id'));
    });
    d3.selectAll('.parent-child-line, .partnership-line, .family-unit-stem, .family-unit-rail, .family-unit-drop')
      .classed('edge--context', function() {
        var el = d3.select(this);
        var from = el.attr('data-from');
        var to = el.attr('data-to');
        if (from === personId || to === personId) {
          return true;
        }
        if (el.attr('data-family-unit')) {
          return el.attr('data-family-unit').indexOf(personId) !== -1;
        }
        return false;
      });
  }

  function applyZoomTransform(transform, duration) {
    if (!svg || !zoom || !transform) {
      return;
    }
    var transition = svg;
    if (duration && duration > 0) {
      transition = svg.transition().duration(duration);
    }
    transition.call(zoom.transform, transform);
  }

  function fitTreeToBounds(bounds, viewportWidth, viewportHeight) {
    var safeWidth = Math.max(bounds.width + 140, 1);
    var safeHeight = Math.max(bounds.height + 140, 1);
    var scale = Math.min(viewportWidth / safeWidth, viewportHeight / safeHeight, 1);
    return d3.zoomIdentity
      .translate(
        viewportWidth / 2 - (bounds.x + bounds.width / 2) * scale,
        viewportHeight / 2 - (bounds.y + bounds.height / 2) * scale
      )
      .scale(scale);
  }

  function renderNode(node, person) {
    var isGraphSource = !!(sidebarState.graphMode && sidebarState.graphMode.sourcePersonId === person.id);
    var isGraphCandidate = !!(sidebarState.graphMode && sidebarState.graphMode.sourcePersonId !== person.id);
    var isFocusPerson = !!(currentFocusPersonId && currentFocusPersonId === person.id);
    var isRootPerson = !!(currentRootPersonId && currentRootPersonId === person.id);
    var nodeLabel = treeNodeLabel(person);
    var nodeGroup = g.append('g')
      .attr('class', 'tree-node person-node' +
        (person.branch ? ' person-node--branch-' + person.branch : '') +
        (isGraphSource ? ' person-node--graph-source' : '') +
        (isGraphCandidate ? ' person-node--graph-candidate' : '') +
        (isFocusPerson ? ' person-node--focus' : '') +
        (isRootPerson ? ' person-node--root' : ''))
      .attr('data-id', person.id)
      .attr('data-render-label', nodeLabel)
      .attr('data-person-id', person.id)
      .attr('transform', 'translate(' + node.x + ',' + node.y + ')')
      .attr('tabindex', '0')
      .attr('role', 'button')
      .attr('aria-label', sidebarState.graphMode
        ? 'Select ' + person.display_name + ' as ' + relationshipSingularLabel(sidebarState.graphMode.mode)
        : 'Open details for ' + person.display_name)
      .style('cursor', 'pointer');

    var showPhoto = preferences.show_photos && person.photo_url;
    if (showPhoto) {
      var clipId = 'clip-' + person.id.replace(/[^a-zA-Z0-9]/g, '');
      var defs = nodeGroup.append('defs');
      defs.append('clipPath')
        .attr('id', clipId)
        .append('circle')
        .attr('r', NODE_RADIUS);
      nodeGroup.append('image')
        .attr('href', resolvePhotoHref(person.photo_url))
        .attr('x', -NODE_RADIUS)
        .attr('y', -NODE_RADIUS)
        .attr('width', NODE_RADIUS * 2)
        .attr('height', NODE_RADIUS * 2)
        .attr('clip-path', 'url(#' + clipId + ')')
        .attr('preserveAspectRatio', 'xMidYMid slice');
      nodeGroup.append('circle')
        .attr('class', 'photo-clip')
        .attr('r', NODE_RADIUS)
        .attr('fill', 'none')
        .attr('stroke', 'white')
        .attr('stroke-width', 2);
    } else {
      nodeGroup.append('circle')
        .attr('class', 'photo-clip')
        .attr('r', NODE_RADIUS);
      if (preferences.show_names) {
        nodeGroup.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', '0.35em')
          .attr('fill', '#2d5016')
          .attr('font-size', '14px')
          .attr('font-weight', '700')
          .attr('pointer-events', 'none')
          .text(nodeLabel.substring(0, 2));
      }
      // Camera icon overlay for photo-less nodes
      if (preferences.show_photos) {
        var iconGroup = nodeGroup.append('g')
          .attr('class', 'tree-node__add-photo')
          .attr('pointer-events', 'all')
          .style('cursor', 'pointer');
        iconGroup.append('circle')
          .attr('r', 12)
          .attr('cx', NODE_RADIUS - 8)
          .attr('cy', NODE_RADIUS - 8)
          .attr('fill', 'var(--bg-warm, #faf8f5)')
          .attr('stroke', 'var(--border, #e0d6c8)')
          .attr('stroke-width', 1);
        // Camera body path
        iconGroup.append('path')
          .attr('d', 'M' + (NODE_RADIUS - 13) + ',' + (NODE_RADIUS - 11) +
            ' l2,-3 h6 l2,3 h2 a1,1 0 0,1 1,1 v6 a1,1 0 0,1 -1,1 h-14 a1,1 0 0,1 -1,-1 v-6 a1,1 0 0,1 1,-1 z')
          .attr('fill', 'none')
          .attr('stroke', 'var(--green-deep, #2d5016)')
          .attr('stroke-width', 1.2)
          .attr('stroke-linecap', 'round')
          .attr('stroke-linejoin', 'round');
        // Camera lens circle
        iconGroup.append('circle')
          .attr('cx', NODE_RADIUS - 8)
          .attr('cy', NODE_RADIUS - 6)
          .attr('r', 2.5)
          .attr('fill', 'none')
          .attr('stroke', 'var(--green-deep, #2d5016)')
          .attr('stroke-width', 1.2);
        iconGroup.on('click', function(event) {
          event.stopPropagation();
          triggerTreePhotoUpload(person.id);
        });
      }
    }

    nodeGroup.append('circle')
      .attr('class', 'tap-target')
      .attr('r', NODE_RADIUS + 10);

    // Add-relative plus button (hover-revealed, hidden during graph mode)
    if (!sidebarState.graphMode && !_relCalcMode) {
      var addRelGroup = nodeGroup.append('g')
        .attr('class', 'tree-node__add-relative')
        .attr('pointer-events', 'all')
        .style('cursor', 'pointer');
      addRelGroup.append('circle')
        .attr('r', 10)
        .attr('cx', 0)
        .attr('cy', -(NODE_RADIUS + 4))
        .attr('fill', 'var(--green-pale, #d9eac9)')
        .attr('stroke', 'var(--green-mid, #7da362)')
        .attr('stroke-width', 1.5);
      addRelGroup.append('text')
        .attr('x', 0)
        .attr('y', -(NODE_RADIUS + 4))
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', 'var(--green-deep, #2d5016)')
        .attr('font-size', '14px')
        .attr('font-weight', '700')
        .attr('pointer-events', 'none')
        .text('+');
      addRelGroup.on('click', function(event) {
        event.stopPropagation();
        openPersonSidebar(person.id).then(function() {
          switchTreeSidebarTab('relationships');
        });
      });
    }

    var nextTextY = NODE_RADIUS + 16;
    if (preferences.show_names) {
      var lineBreakIndex = nodeLabel.length > 14 ? nodeLabel.lastIndexOf(' ') : -1;
      if (lineBreakIndex > 2 && lineBreakIndex < nodeLabel.length - 2) {
        var nameText = nodeGroup.append('text')
          .attr('class', 'name-label')
          .attr('text-anchor', 'middle')
          .attr('dy', nextTextY - 4);
        nameText.append('tspan')
          .attr('x', 0)
          .text(nodeLabel.slice(0, lineBreakIndex));
        nameText.append('tspan')
          .attr('x', 0)
          .attr('dy', '1.1em')
          .text(nodeLabel.slice(lineBreakIndex + 1));
        nextTextY += 27;
      } else {
        nodeGroup.append('text')
          .attr('class', 'name-label')
          .attr('dy', nextTextY)
          .text(nodeLabel);
        nextTextY += 15;
      }
    }

    if (preferences.show_birth_dates && person.birth_date_raw) {
      nodeGroup.append('text')
        .attr('class', 'rel-label')
        .attr('dy', nextTextY)
        .text(person.birth_date_raw);
      nextTextY += 14;
    }

    if (preferences.show_country_flags && person.residence_country_code) {
      nodeGroup.append('text')
        .attr('class', 'rel-label')
        .attr('dy', nextTextY)
        .text(countryFlag(person.residence_country_code));
      nextTextY += 14;
    }

    addMetricPill(nodeGroup, person, nextTextY);

    nodeGroup.on('click', function() {
      if (_relCalcMode) {
        _handleRelCalcClick(person.id);
        return;
      }
      if (sidebarState.graphMode) {
        handleGraphNodeSelection(person.id);
        return;
      }
      openPersonSidebar(person.id, this);
    });

    nodeGroup.on('dblclick', function(event) {
      if (sidebarState.graphMode) {
        event.preventDefault();
        return;
      }
      window.location.href = '/people/' + person.id + '/edit';
    });

    nodeGroup.on('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        if (sidebarState.graphMode) {
          handleGraphNodeSelection(person.id);
          return;
        }
        openPersonSidebar(person.id, this);
      }
    });
  }

  function render() {
    var container = document.getElementById('tree-page');
    var w = container.clientWidth;
    var h = container.clientHeight;

    svg = d3.select('#tree-svg')
      .attr('width', w)
      .attr('height', h);
    svg.selectAll('*').remove();
    appendTreeDefs();

    g = svg.append('g');

    zoom = d3.zoom()
      .scaleExtent([0.2, 3])
      .on('zoom', function(event) {
        g.attr('transform', event.transform);
      });
    svg.call(zoom);

    if (!treeData || !treeData.persons || treeData.persons.length === 0) {
      drawEmptyState(w, h);
      return;
    }

    var structures = buildTreeStructures();
    var rootId = determineRootId(structures.personsById, structures.childToParents);
    var layout = layoutTree(
      rootId,
      structures.parentToChildren,
      structures.childToParents,
      structures.partnerMap,
      structures.familyUnitsByPair,
      structures.partnershipByPair,
      structures.familyUnits,
      structures.familyUnitsByPerson,
      structures.incomingFamilyUnitByChild,
      w
    );
    currentRootPersonId = rootId;
    if (currentFocusPersonId && !structures.personsById[currentFocusPersonId]) {
      currentFocusPersonId = '';
    }

    // Build parent-child kind lookup: "parentId|childId" → kind
    var pcKindLookup = {};
    treeData.parent_child.forEach(function(pc) {
      pcKindLookup[pc.parent_id + '|' + pc.child_id] = pc.kind || 'biological';
    });

    drawGenerationBands(layout);
    drawComponentFrames(layout);

    var families = collectFamilyUnits(structures, layout, pcKindLookup);
    var lineGen = d3.line().curve(d3.curveBumpY);
    treeData.parent_child.forEach(function(parentChild) {
      var fromKey = parentChild.parent_id + '|' + parentChild.child_id;
      if (families.coveredEdges[fromKey]) {
        return;
      }
      var parentPos = layout.nodePositions[parentChild.parent_id];
      var childPos = layout.nodePositions[parentChild.child_id];
      if (!parentPos || !childPos) {
        return;
      }
      var kind = parentChild.kind || 'biological';
      g.append('path')
        .attr('class', 'parent-child-line parent-child-line--' + kind)
        .attr('data-from', parentChild.parent_id)
        .attr('data-to', parentChild.child_id)
        .attr('marker-end', 'url(#tree-parent-arrow)')
        .attr('d', lineGen([[parentPos.x, parentPos.y + NODE_RADIUS], [childPos.x, childPos.y - NODE_RADIUS]]));
    });

    Object.keys(structures.partnershipByPair || {}).forEach(function(pairKey) {
      var partnership = structures.partnershipByPair[pairKey];
      var posA = layout.nodePositions[partnership.person_a_id];
      var posB = layout.nodePositions[partnership.person_b_id];
      if (!posA || !posB) {
        return;
      }
      var former = partnership.status && partnership.status !== 'active';
      var pKind = partnership.kind || 'married';
      g.append('line')
        .attr('class', 'partnership-line partnership-line--' + pKind +
          (former ? ' partnership-line--former partnership-line--status-' + partnership.status : ''))
        .attr('data-from', partnership.person_a_id)
        .attr('data-to', partnership.person_b_id)
        .attr('x1', posA.x)
        .attr('y1', posA.y)
        .attr('x2', posB.x)
        .attr('y2', posB.y);
      g.append('circle')
        .attr('class', 'partnership-knot partnership-knot--' + pKind)
        .attr('cx', (posA.x + posB.x) / 2)
        .attr('cy', (posA.y + posB.y) / 2)
        .attr('r', 5)
        .attr('data-from', partnership.person_a_id)
        .attr('data-to', partnership.person_b_id);
    });

    families.familyUnits.forEach(function(unit) {
      if (!unit.renderChildIds.length) {
        return;
      }
      var visibleParents = unit.parentIds.map(function(parentId) {
        return layout.nodePositions[parentId] ? {
          id: parentId,
          pos: layout.nodePositions[parentId]
        } : null;
      }).filter(Boolean);
      if (!visibleParents.length) {
        return;
      }
      var familyCenterX = averageValues(visibleParents.map(function(parent) {
        return parent.pos.x;
      }));
      var familyTopY = Math.max.apply(Math, visibleParents.map(function(parent) {
        return parent.pos.y;
      })) + NODE_RADIUS;
      var familyRailY = familyTopY + 34;
      var childXs = unit.renderChildIds.map(function(childId) {
        return layout.nodePositions[childId].x;
      });
      var kind = unit.childKinds[unit.renderChildIds[0]] || 'biological';

      g.append('line')
        .attr('class', 'family-unit-stem parent-child-line parent-child-line--' + kind)
        .attr('x1', familyCenterX)
        .attr('y1', familyTopY - 4)
        .attr('x2', familyCenterX)
        .attr('y2', familyRailY)
        .attr('data-family-unit', unit.renderKey || unit.key);
      g.append('circle')
        .attr('class', 'family-unit-anchor')
        .attr('cx', familyCenterX)
        .attr('cy', familyTopY - 6)
        .attr('r', 5);
      if (childXs.length > 1) {
        g.append('line')
          .attr('class', 'family-unit-rail parent-child-line parent-child-line--' + kind)
          .attr('x1', Math.min.apply(Math, childXs))
          .attr('y1', familyRailY)
          .attr('x2', Math.max.apply(Math, childXs))
          .attr('y2', familyRailY)
          .attr('data-family-unit', unit.renderKey || unit.key);
      }
      unit.renderChildIds.forEach(function(childId) {
        var childPos = layout.nodePositions[childId];
        if (!childPos) {
          return;
        }
        g.append('line')
          .attr('class', 'family-unit-drop parent-child-line parent-child-line--' + kind)
          .attr('x1', childPos.x)
          .attr('y1', childXs.length > 1 ? familyRailY : familyTopY + 8)
          .attr('x2', childPos.x)
          .attr('y2', childPos.y - NODE_RADIUS)
          .attr('data-from', unit.renderKey || unit.key)
          .attr('marker-end', 'url(#tree-parent-arrow)')
          .attr('data-to', childId);
      });
    });

    layout.allNodes.forEach(function(node) {
      var person = structures.personsById[node.id];
      if (person) {
        renderNode(node, person);
      }
    });

    var bounds = g.node().getBBox();
    lastFitTransform = fitTreeToBounds(bounds, w, h);
    applyZoomTransform(lastFitTransform, 0);

    setStatus(root.dataset.statusTemplate.replace('{count}', String(treeData.persons.length)));
    syncNavigationContext();
    syncSidebarOrientation();
    syncRelationshipCalcControls();
    updateGraphModeBanner();
    applyContextHighlight(currentSidebarPersonId, structures);

    if (!initialUrlFocusApplied) {
      initialUrlFocusApplied = true;
      if (initialUrlFocusPersonId && structures.personsById[initialUrlFocusPersonId]) {
        setCurrentFocusPerson(initialUrlFocusPersonId, {updateUrl: false});
        window.setTimeout(function() {
          zoomToNode(initialUrlFocusPersonId, {scale: 1.1});
          openPersonSidebar(initialUrlFocusPersonId, document.querySelector('#tree-svg [data-id="' + initialUrlFocusPersonId + '"]'));
        }, 80);
      }
    }
  }

  async function openPersonSidebar(personId, triggerNode) {
    sidebarState.activeTab = '';
    sidebarState.relationshipGroup = '';
    sidebarState.highlightMediaId = '';
    sidebarTrigger = triggerNode || document.activeElement;
    sidebar.classList.add('person-sidebar--open');
    window.openAccessibleOverlay(sidebar, {initialFocus: '.person-sidebar__close'});
    await renderSidebar(personId);
  }

  function switchTreeSidebarTab(tabName, context) {
    sidebarState.activeTab = tabName || 'overview';
    if (tabName === 'relationships' && (context === 'parent' || context === 'child' || context === 'partner')) {
      sidebarState.relationshipGroup = context;
    }

    var tabs = sidebarContent.querySelectorAll('[data-tree-sidebar-tab]');
    Array.prototype.forEach.call(tabs, function(tab) {
      var active = tab.dataset.treeSidebarTab === sidebarState.activeTab;
      tab.classList.toggle('tree-sidebar-tab--active', active);
      tab.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    var panels = sidebarContent.querySelectorAll('[data-tree-sidebar-panel]');
    Array.prototype.forEach.call(panels, function(panel) {
      var active = panel.dataset.treeSidebarPanel === sidebarState.activeTab;
      panel.hidden = !active;
    });

    if (sidebarState.activeTab === 'relationships') {
      openRelationshipDisclosure(sidebarState.relationshipGroup || context);
    }
    if (sidebarState.activeTab === 'media') {
      var personId = getSidebarPersonId();
      if (personId) {
        loadTreeSidebarMedia(personId);
      }
    }
    if (sidebarState.activeTab === 'records') {
      var personId = getSidebarPersonId();
      if (personId) {
        loadSavedRecords(personId);
      }
    }
    updateGraphModeBanner();
    applyRelationshipHighlights();
  }

  function openSidebarDetailsSection(sectionName) {
    switchTreeSidebarTab('details');
    setTimeout(function() {
      var section = sidebarContent.querySelector('[data-tree-details-section="' + sectionName + '"]');
      if (section) {
        section.open = true;
        var firstInput = section.querySelector('input, select, textarea');
        if (firstInput) firstInput.focus();
      }
    }, 50);
  }

  function relationshipDeleteEndpoint(relId, relationshipType) {
    return relationshipType === 'partnership'
      ? '/api/relationships/partnership/' + relId
      : '/api/relationships/parent-child/' + relId;
  }

  async function deleteRelationshipByType(relId, relationshipType) {
    return fetch(relationshipDeleteEndpoint(relId, relationshipType), {method: 'DELETE'});
  }

  function startTreeGraphMode(personId, mode, options) {
    var opts = options || {};
    if (_relCalcMode) {
      cancelRelationshipCalc(true);
    }
    setError('tree-relationship-error', '');
    sidebarState.activeTab = 'relationships';
    sidebarState.relationshipGroup = mode;
    sidebarState.highlightRelatedPersonId = opts.currentRelatedId || '';
    sidebarState.graphMode = {
      sourcePersonId: personId,
      sourcePersonName: getSidebarPersonName(),
      mode: mode,
      action: opts.action || 'link',
      relationshipId: opts.relationshipId || '',
      relationshipType: opts.relationshipType || (mode === 'partner' ? 'partnership' : 'parent-child'),
      currentRelatedId: opts.currentRelatedId || '',
      currentRelatedName: opts.currentRelatedName || '',
      relationshipMeta: opts.relationshipMeta || {}
    };
    switchTreeSidebarTab('relationships', mode);
    if (treeData) {
      render();
    }
  }

  function cancelTreeGraphMode(silent) {
    sidebarState.graphMode = null;
    sidebarState.highlightRelatedPersonId = '';
    updateGraphModeBanner();
    syncInteractionModeClasses();
    if (treeData) {
      render();
    } else {
      restoreDefaultStatus();
    }
    if (!silent) {
      showToastMessage(root.dataset.treeGraphCancelled);
    }
  }

  function openTreeRelationshipSearch(groupName) {
    if (sidebarState.graphMode) {
      cancelTreeGraphMode(true);
    }
    if (_relCalcMode) {
      cancelRelationshipCalc(true);
    }
    sidebarState.activeTab = 'relationships';
    sidebarState.relationshipGroup = groupName;
    switchTreeSidebarTab('relationships', groupName);
    openRelationshipDisclosure(groupName);
    var input = sidebarContent.querySelector('[data-tree-link-form="' + groupName + '"] [data-tree-picker-input]');
    if (input) {
      input.focus();
    }
  }

  function openTreeRelationshipCreate(groupName) {
    if (sidebarState.graphMode) {
      cancelTreeGraphMode(true);
    }
    if (_relCalcMode) {
      cancelRelationshipCalc(true);
    }
    sidebarState.activeTab = 'relationships';
    sidebarState.relationshipGroup = groupName;
    switchTreeSidebarTab('relationships', groupName);
    openRelationshipDisclosure(groupName);
    var input = sidebarContent.querySelector('[data-tree-create-form="' + groupName + '"] input[name="first_name"]');
    if (input) {
      input.focus();
    }
  }

  async function executeRelationshipRequest(request) {
    var resp = await fetch(request.endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(request.body)
    });
    var data = await resp.json().catch(function() { return {}; });
    if (!resp.ok) {
      throw new Error(data.detail || root.dataset.relationshipError);
    }
    return data;
  }

  async function handleGraphNodeSelection(targetPersonId) {
    if (!sidebarState.graphMode) {
      return;
    }
    var modeState = sidebarState.graphMode;
    if (targetPersonId === modeState.sourcePersonId || targetPersonId === modeState.currentRelatedId) {
      setError('tree-relationship-error', root.dataset.treeGraphSelectOther);
      return;
    }

    var targetPerson = (treeData && treeData.persons || []).find(function(person) {
      return person.id === targetPersonId;
    });
    if (!targetPerson) {
      setError('tree-relationship-error', root.dataset.relationshipError);
      return;
    }

    var confirmMessage = formatTemplate(
      modeState.action === 'replace'
        ? root.dataset.treeGraphConfirmReplace
        : root.dataset.treeGraphConfirmLink,
      {
        target: targetPerson.display_name,
        name: modeState.sourcePersonName || getSidebarPersonName(),
        relationship: relationshipSingularLabel(modeState.mode),
        current: modeState.currentRelatedName || ''
      }
    );
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setError('tree-relationship-error', '');
    try {
      var createdRelationship = await executeRelationshipRequest(
        relationshipPayload(
          modeState.sourcePersonId,
          targetPersonId,
          modeState.mode,
          modeState.relationshipMeta
        )
      );

      if (modeState.action === 'replace' && modeState.relationshipId) {
        var deleteResp = await deleteRelationshipByType(modeState.relationshipId, modeState.relationshipType);
        if (!deleteResp.ok) {
          await deleteRelationshipByType(createdRelationship.id, modeState.relationshipType).catch(function() {
            return null;
          });
          var deleteData = await deleteResp.json().catch(function() { return {}; });
          throw new Error(deleteData.detail || root.dataset.relationshipError);
        }
      }

      sidebarState.graphMode = null;
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = modeState.mode;
      sidebarState.highlightRelatedPersonId = targetPersonId;
      await refreshTreeWorkspace(modeState.sourcePersonId);
      showToastMessage(
        modeState.action === 'replace'
          ? root.dataset.treeRelationshipReplaced
          : root.dataset.relationshipMessage
      );
    } catch (err) {
      setError('tree-relationship-error', err.message || root.dataset.relationshipError);
    }
  }

  function countryFlag(code) {
    if (!code || code.length !== 2) {
      return '';
    }
    var offset = 127397;
    return String.fromCodePoint(code.charCodeAt(0) + offset, code.charCodeAt(1) + offset);
  }

  function triggerTreePhotoUpload(personId) {
    openPersonSidebar(personId).then(function() {
      switchTreeSidebarTab('media');
      setTimeout(function() {
        var fileInput = sidebarContent.querySelector('[data-tree-sidebar-panel="media"] input[type="file"]');
        if (fileInput) { fileInput.click(); }
      }, 200);
    });
  }

  async function refreshTreeWorkspace(personId) {
    await loadTree();
    if (personId) {
      await renderSidebar(personId);
    }
  }

  function syncPersonIntoTreeData(personId, detail) {
    if (!treeData || !treeData.persons || !detail || !personId) {
      return;
    }
    treeData.persons = treeData.persons.map(function(person) {
      if (person.id !== personId) {
        return person;
      }
      return Object.assign({}, person, detail);
    });
  }

  function normalizeOccurredAt(rawValue) {
    if (!rawValue) {
      return null;
    }
    if (rawValue.indexOf('T') !== -1) {
      return rawValue;
    }
    return rawValue + 'T12:00:00Z';
  }

  async function uploadTreeFiles(files, personId, options) {
    var opts = options || {};
    var uploaded = [];
    try {
      for (var index = 0; index < files.length; index += 1) {
        var fd = new FormData();
        fd.append('file', files[index]);
        fd.append('person_id', personId);
        if (opts.caption) {
          fd.append('caption', opts.caption);
        }
        if (opts.purpose && opts.purpose !== 'memory') {
          fd.append('purpose', opts.purpose);
        }
        if (opts.taggedPersonIds && opts.taggedPersonIds.length) {
          fd.append('tagged_person_ids', JSON.stringify(opts.taggedPersonIds));
        }
        var resp = await fetch('/api/media', {method: 'POST', body: fd});
        var data = await resp.json().catch(function() { return {}; });
        if (!resp.ok) {
          throw new Error(data.detail || root.dataset.mediaError);
        }
        uploaded.push(data);
      }
    } catch (err) {
      await cleanupUploadedTreeMedia(uploaded);
      throw err;
    }
    return uploaded;
  }

  async function cleanupUploadedTreeMedia(uploadedItems) {
    if (!uploadedItems || !uploadedItems.length) {
      return;
    }
    var createdItems = uploadedItems.filter(function(item) {
      return item && item.id && !item.is_duplicate;
    });
    await Promise.all(createdItems.map(function(item) {
      return fetch('/api/media/' + item.id, {method: 'DELETE'}).catch(function() {
        return null;
      });
    }));
  }

  async function uploadTreeMedia(event, personId) {
    event.preventDefault();
    setError('tree-media-error', '');
    var form = event.target;
    var fileInput = form.querySelector('input[type="file"]');
    var button = form.querySelector('button[type="submit"]');
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
      setError('tree-media-error', root.dataset.mediaError);
      return false;
    }

    var originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = root.dataset.uploadLabel;
    var uploads = [];

    try {
      var captionInput = form.querySelector('input[name="caption"]');
      var purposeSelect = form.querySelector('select[name="purpose"]');
      uploads = await uploadTreeFiles(fileInput.files, personId, {
        caption: captionInput && captionInput.value.trim() ? captionInput.value.trim() : '',
        purpose: purposeSelect && purposeSelect.value ? purposeSelect.value : 'memory'
      });
      // Auto-set profile photo if person has none and upload is an image
      var treePerson = (treeData && treeData.persons || []).find(function(p) { return p.id === personId; });
      if (treePerson && !treePerson.photo_url && uploads.length > 0 && uploads[0].mime_type && uploads[0].mime_type.indexOf('image') === 0) {
        await fetch('/api/persons/' + personId, {
          method: 'PUT',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ photo_url: uploads[0].id })
        }).catch(function() { /* best-effort */ });
      }
      form.reset();
      sidebarState.activeTab = 'media';
      sidebarState.highlightMediaId = uploads.length ? uploads[uploads.length - 1].id : '';
      await refreshTreeWorkspace(personId);
      showToastMessage(root.dataset.treeMediaUploaded);
    } catch (err) {
      await cleanupUploadedTreeMedia(uploads);
      setError('tree-media-error', err.message || root.dataset.mediaError);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
    return false;
  }

  async function saveTreePerson(event, personId) {
    event.preventDefault();
    clearErrors();
    var form = event.target;
    var button = form.querySelector('button[type="submit"]');
    var originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = root.dataset.savingLabel;

    try {
      var payload = formDataToJson(form, {
          nullableFields: [
            'nickname',
            'birth_date_raw',
            'birth_date_precision',
            'death_date_raw',
            'death_date_precision',
            'birth_place',
            'birth_country_code',
            'residence_place',
            'residence_country_code',
            'burial_place',
            'burial_country_code',
            'burial_cemetery_name',
            'burial_plot_number',
            'branch',
            'bio',
            'research_notes',
            'patronymic',
            'birth_last_name',
            'gender',
            'contact_whatsapp',
            'contact_telegram',
            'contact_signal',
            'contact_email',
            'obituary',
            'obituary_source',
            'height',
            'weight',
            'eye_color',
            'hair_color',
            'blood_type',
            'maternal_haplogroup',
            'paternal_haplogroup',
            'dna_test_provider',
            'source_detail',
            'confidence'
          ]
        });
      // Only send advanced collection fields when the compact tree form exposes them.
      [
        'education',
        'career',
        'organizations',
        'admixture',
        'medical_conditions'
      ].forEach(function(fieldName) {
        if (form.querySelector('[data-json-field="' + fieldName + '"]') || form.querySelector('#tree-' + fieldName + '-entries')) {
          payload[fieldName] = collectJsonArrayEntries(fieldName);
        }
      });
      // Handle is_living checkbox (unchecked = not in FormData)
      var livingCheckbox = form.querySelector('[name="is_living"]');
      if (livingCheckbox) {
        payload.is_living = livingCheckbox.checked;
      }
      // Handle languages as array
      var langInput = form.querySelector('[name="languages"]');
      if (langInput) {
        var langVal = langInput.value.trim();
        payload.languages = langVal ? langVal.split(',').map(function(s) { return s.trim(); }).filter(Boolean) : [];
      }
      var resp = await fetch('/api/persons/' + personId, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      var data = await resp.json().catch(function() { return {}; });
      if (!resp.ok) {
        throw new Error(data.detail || root.dataset.updateError);
      }
      sidebarState.activeTab = 'details';
      syncPersonIntoTreeData(personId, data);
      render();
      await renderSidebar(personId);
      showToastMessage(root.dataset.savedMessage);
    } catch (err) {
      setError('tree-person-edit-error', err.message || root.dataset.updateError);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
    return false;
  }

  async function linkTreeRelationship(event, personId, mode) {
    event.preventDefault();
    setError('tree-relationship-error', '');
    var form = event.target;
    var relatedId = form.querySelector('[name="related_person_id"]').value;
    if (!relatedId) {
      setError('tree-relationship-error', root.dataset.relationshipError);
      return false;
    }

    try {
      await executeRelationshipRequest(relationshipPayload(
        personId,
        relatedId,
        mode,
        relationshipMetaFromForm(form, mode)
      ));
      form.reset();
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = mode;
      sidebarState.highlightRelatedPersonId = relatedId;
      await refreshTreeWorkspace(personId);
      showToastMessage(root.dataset.relationshipMessage);
    } catch (err) {
      setError('tree-relationship-error', err.message || root.dataset.relationshipError);
    }
    return false;
  }

  async function createTreeRelative(event, personId, mode) {
    event.preventDefault();
    setError('tree-relationship-error', '');
    var form = event.target;
    var button = form.querySelector('button[type="submit"]');
    var originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = root.dataset.savingLabel;

    try {
      var createResp = await fetch('/api/persons', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(treeRelativeCreatePayload(form))
      });
      var created = await createResp.json().catch(function() { return {}; });
      if (!createResp.ok) {
        throw new Error(created.detail || root.dataset.updateError);
      }

      await executeRelationshipRequest(relationshipPayload(
        personId,
        created.id,
        mode,
        relationshipMetaFromForm(form, mode)
      ));

      form.reset();
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = mode;
      sidebarState.highlightRelatedPersonId = created.id;
      await refreshTreeWorkspace(personId);
      showToastMessage(root.dataset.createdMessage);
    } catch (err) {
      setError('tree-relationship-error', err.message || root.dataset.relationshipError);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
    return false;
  }

  async function replaceTreeRelationship(relId, relationshipType, personId, groupName, relatedId, relatedName, relationshipMeta) {
    setError('tree-relationship-error', '');
    startTreeGraphMode(personId, groupName, {
      action: 'replace',
      relationshipId: relId,
      relationshipType: relationshipType,
      currentRelatedId: relatedId,
      currentRelatedName: relatedName,
      relationshipMeta: relationshipMeta || {}
    });
    return false;
  }

  async function removeTreeRelationship(relId, relationshipType, personId, groupName, relatedName) {
    setError('tree-relationship-error', '');
    var confirmed = window.confirm(formatTemplate(root.dataset.treeRemoveConfirm, {
      name: relatedName || '',
      relationship: relationshipSingularLabel(groupName || 'partner')
    }));
    if (!confirmed) {
      return false;
    }
    try {
      var resp = await deleteRelationshipByType(relId, relationshipType);
      if (!resp.ok) {
        var data = await resp.json().catch(function() { return {}; });
        throw new Error(data.detail || root.dataset.relationshipError);
      }
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = groupName || '';
      sidebarState.highlightRelatedPersonId = '';
      await refreshTreeWorkspace(personId);
      showToastMessage(root.dataset.treeRelationshipRemoved);
    } catch (err) {
      setError('tree-relationship-error', err.message || root.dataset.relationshipError);
    }
    return false;
  }

  function openTreeSidebarPerson(personId) {
    var node = document.querySelector('#tree-svg [data-id="' + personId + '"]');
    if (node) {
      openPersonSidebar(personId, node);
      return;
    }
    openPersonSidebar(personId, sidebarTrigger || document.activeElement);
  }

  // --- Tree Search ---

  var searchInput = document.getElementById('tree-search-input');
  var searchResults = document.getElementById('tree-search-results');
  var searchSelectedIndex = -1;
  var searchMatches = [];

  function searchTree(query) {
    if (!treeData || !treeData.persons || !query || query.length < 1) {
      return [];
    }
    var lower = query.toLowerCase();
    return treeData.persons.filter(function(person) {
      var name = (person.display_name || '').toLowerCase();
      var nick = (person.nickname || '').toLowerCase();
      var branch = (person.branch || '').toLowerCase();
      return name.indexOf(lower) !== -1 || nick.indexOf(lower) !== -1 || branch.indexOf(lower) !== -1;
    }).slice(0, 20);
  }

  function renderSearchResults(matches) {
    searchMatches = matches;
    searchSelectedIndex = -1;
    clearNode(searchResults);

    if (matches.length === 0) {
      var empty = document.createElement('div');
      empty.className = 'tree-search-empty';
      empty.textContent = root.dataset.treeSearchNoResults || 'No matching people found';
      searchResults.appendChild(empty);
      searchResults.hidden = false;
      searchInput.setAttribute('aria-expanded', 'true');
      return;
    }

    matches.forEach(function(person, idx) {
      var item = document.createElement('div');
      item.className = 'tree-search-result';
      item.setAttribute('role', 'option');
      item.setAttribute('id', 'tree-search-result-' + idx);
      item.setAttribute('aria-selected', 'false');
      item.dataset.personId = person.id;

      var nameSpan = document.createElement('span');
      nameSpan.className = 'tree-search-result__name';
      nameSpan.textContent = person.display_name;
      item.appendChild(nameSpan);

      var meta = [];
      if (person.nickname) meta.push('"' + person.nickname + '"');
      if (person.branch) meta.push(person.branch);
      if (person.birth_date_raw) meta.push(person.birth_date_raw);
      if (meta.length) {
        var metaSpan = document.createElement('span');
        metaSpan.className = 'tree-search-result__meta';
        metaSpan.textContent = meta.join(' · ');
        item.appendChild(metaSpan);
      }

      item.addEventListener('click', function() {
        selectSearchResult(person.id);
      });
      searchResults.appendChild(item);
    });

    searchResults.hidden = false;
    searchInput.setAttribute('aria-expanded', 'true');
  }

  function hideSearchResults() {
    searchResults.hidden = true;
    searchInput.setAttribute('aria-expanded', 'false');
    searchInput.removeAttribute('aria-activedescendant');
    searchSelectedIndex = -1;
    searchMatches = [];
  }

  function selectSearchResult(personId) {
    searchInput.value = '';
    hideSearchResults();
    setCurrentFocusPerson(personId);
    zoomToNode(personId, {scale: 1.15});
    openPersonSidebar(personId, document.querySelector('#tree-svg [data-id="' + personId + '"]'));
  }

  function updateSearchSelection(newIndex) {
    var items = searchResults.querySelectorAll('[role="option"]');
    if (items.length === 0) return;

    if (newIndex < 0) newIndex = items.length - 1;
    if (newIndex >= items.length) newIndex = 0;

    Array.prototype.forEach.call(items, function(item, i) {
      item.setAttribute('aria-selected', i === newIndex ? 'true' : 'false');
    });

    searchSelectedIndex = newIndex;
    searchInput.setAttribute('aria-activedescendant', 'tree-search-result-' + newIndex);
    items[newIndex].scrollIntoView({block: 'nearest'});
  }

  function zoomToNode(personId, options) {
    if (!svg || !zoom || !treeData) return;
    var opts = options || {};

    var nodeEl = g.select('[data-id="' + personId + '"]');
    if (nodeEl.empty()) return;

    var transform = nodeEl.attr('transform');
    var match = transform && transform.match(/translate\(\s*([\d.-]+)\s*,\s*([\d.-]+)\s*\)/);
    if (!match) return;

    var nx = parseFloat(match[1]);
    var ny = parseFloat(match[2]);
    var container = document.getElementById('tree-page');
    var w = container.clientWidth;
    var h = container.clientHeight;
    var scale = opts.scale || 1.2;
    var tx = w / 2 - nx * scale;
    var ty = h / 2 - ny * scale;

    applyZoomTransform(d3.zoomIdentity.translate(tx, ty).scale(scale), opts.duration == null ? 600 : opts.duration);

    // Flash highlight
    var circle = nodeEl.select('.photo-clip');
    if (!circle.empty() && opts.flash !== false) {
      var origStroke = circle.attr('stroke');
      var origWidth = circle.attr('stroke-width');
      circle
        .attr('stroke', '#e67e22')
        .attr('stroke-width', 4);
      setTimeout(function() {
        circle.attr('stroke', origStroke || null).attr('stroke-width', origWidth || null);
      }, 1500);
    }
  }

  if (searchInput) {
    var searchDebounce;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchDebounce);
      var query = searchInput.value.trim();
      if (!query) {
        hideSearchResults();
        return;
      }
      searchDebounce = setTimeout(function() {
        var matches = searchTree(query);
        renderSearchResults(matches);
      }, 150);
    });

    searchInput.addEventListener('keydown', function(event) {
      if (searchResults.hidden) return;

      if (event.key === 'ArrowDown') {
        event.preventDefault();
        updateSearchSelection(searchSelectedIndex + 1);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        updateSearchSelection(searchSelectedIndex - 1);
      } else if (event.key === 'Enter') {
        event.preventDefault();
        if (searchSelectedIndex >= 0 && searchMatches[searchSelectedIndex]) {
          selectSearchResult(searchMatches[searchSelectedIndex].id);
        }
      } else if (event.key === 'Escape') {
        hideSearchResults();
        searchInput.blur();
      }
    });

    searchInput.addEventListener('focus', function() {
      var query = searchInput.value.trim();
      if (query && treeData) {
        renderSearchResults(searchTree(query));
      }
    });

    document.addEventListener('click', function(event) {
      if (!event.target.closest('#tree-search')) {
        hideSearchResults();
      }
    });
  }

  window.treeZoomIn = function() {
    if (svg && zoom) {
      svg.transition().call(zoom.scaleBy, 1.3);
    }
  };

  window.treeZoomOut = function() {
    if (svg && zoom) {
      svg.transition().call(zoom.scaleBy, 0.7);
    }
  };

  window.treeFitView = function() {
    if (lastFitTransform) {
      applyZoomTransform(lastFitTransform, 350);
    } else if (treeData) {
      render();
    }
  };

  window.treeCenterRoot = function() {
    if (!currentRootPersonId) {
      return;
    }
    zoomToNode(currentRootPersonId, {scale: 1.05});
  };

  window.treeReturnToFocus = function() {
    if (!currentFocusPersonId) {
      return;
    }
    zoomToNode(currentFocusPersonId, {scale: 1.1});
  };

  window.setTreeFocus = function(personId) {
    if (!personId) {
      return;
    }
    setCurrentFocusPerson(personId);
    zoomToNode(personId, {scale: 1.1, flash: false});
  };

  window.treeReset = function() {
    hideSearchResults();
    if (sidebarState.graphMode) {
      cancelTreeGraphMode(true);
      return;
    }
    if (_relCalcMode) {
      cancelRelationshipCalc(true);
      return;
    }
    _clearPathHighlight();
    var relResult = document.getElementById('tree-relcalc-result');
    if (relResult) {
      relResult.hidden = true;
    }
    if (currentFocusPersonId) {
      window.treeReturnToFocus();
      return;
    }
    if (currentRootPersonId) {
      window.treeCenterRoot();
      return;
    }
    if (lastFitTransform) {
      applyZoomTransform(lastFitTransform, 350);
    } else if (treeData) {
      render();
    }
  };

  window.closeSidebar = function() {
    if (_relCalcMode) {
      _relCalcMode = false;
      _relCalcFirst = null;
    }
    sidebar.classList.remove('person-sidebar--open');
    currentSidebarPersonId = null;
    sidebarState.graphMode = null;
    sidebarState.highlightRelatedPersonId = '';
    window.closeAccessibleOverlay(sidebar);
    var expandTab = document.getElementById('sidebar-expand-tab');
    if (expandTab) expandTab.hidden = true;
    var relcalcBanner = document.getElementById('tree-relcalc-banner');
    if (relcalcBanner) relcalcBanner.hidden = true;
    var relcalcResult = document.getElementById('tree-relcalc-result');
    if (relcalcResult) relcalcResult.hidden = true;
    _clearPathHighlight();
    syncRelationshipCalcControls();
    syncInteractionModeClasses();
    if (treeData) {
      render();
    }
    if (sidebarTrigger && typeof sidebarTrigger.focus === 'function') {
      sidebarTrigger.focus();
    }
  };

  window.collapseSidebar = function() {
    sidebar.classList.remove('person-sidebar--open');
    window.closeAccessibleOverlay(sidebar);
    var expandTab = document.getElementById('sidebar-expand-tab');
    if (expandTab) expandTab.hidden = false;
  };

  window.expandSidebar = function() {
    var expandTab = document.getElementById('sidebar-expand-tab');
    if (expandTab) expandTab.hidden = true;
    if (currentSidebarPersonId) {
      sidebar.classList.add('person-sidebar--open');
      window.openAccessibleOverlay(sidebar, {initialFocus: '.person-sidebar__close'});
    }
  };

  // ── Left Panel Collapse / Expand ────────────────────────────────────

  var PANEL_COLLAPSED_KEY = 'treePanelCollapsed';

  function _updatePanelToggleUI(collapsed) {
    var expandTab = document.getElementById('tree-panel-expand-tab');
    if (expandTab) expandTab.hidden = !collapsed;
  }

  function _rerenderAfterPanelTransition() {
    setTimeout(function() {
      if (treeData) render();
    }, 350);
  }

  function collapseTreePanelSilent() {
    if (!treeLayout) return;
    treeLayout.classList.add('tree-layout--panel-collapsed');
    _updatePanelToggleUI(true);
  }

  function restoreTreePanelState() {
    try {
      if (localStorage.getItem(PANEL_COLLAPSED_KEY) === '1') {
        collapseTreePanelSilent();
      }
    } catch (e) { /* localStorage unavailable */ }
  }

  window.toggleTreePanel = function() {
    if (!treeLayout) return;
    var isCollapsed = treeLayout.classList.contains('tree-layout--panel-collapsed');
    if (isCollapsed) {
      treeLayout.classList.remove('tree-layout--panel-collapsed');
      _updatePanelToggleUI(false);
      try { localStorage.setItem(PANEL_COLLAPSED_KEY, '0'); } catch (e) {}
    } else {
      treeLayout.classList.add('tree-layout--panel-collapsed');
      _updatePanelToggleUI(true);
      try { localStorage.setItem(PANEL_COLLAPSED_KEY, '1'); } catch (e) {}
    }
    _rerenderAfterPanelTransition();
  };

  // Keep old names as aliases for backwards compatibility
  window.collapseTreePanel = function() {
    if (!treeLayout) return;
    treeLayout.classList.add('tree-layout--panel-collapsed');
    _updatePanelToggleUI(true);
    try { localStorage.setItem(PANEL_COLLAPSED_KEY, '1'); } catch (e) {}
    _rerenderAfterPanelTransition();
  };

  window.expandTreePanel = function() {
    if (!treeLayout) return;
    treeLayout.classList.remove('tree-layout--panel-collapsed');
    _updatePanelToggleUI(false);
    try { localStorage.setItem(PANEL_COLLAPSED_KEY, '0'); } catch (e) {}
    _rerenderAfterPanelTransition();
  };

  restoreTreePanelState();

  // ── External Records Search ─────────────────────────────────────────

  var SOURCE_LABELS = {
    chronicling_america: 'Chronicling America (USA Newspapers)',
    nara: 'NARA Catalog (USA Archives)',
    trove: 'Trove (Australian Newspapers)',
    dpla: 'DPLA (US Libraries & Archives)',
    familysearch: 'FamilySearch',
    antenati: 'Antenati (Italian Civil Records)'
  };

  async function searchAllExternalRecords(personId) {
    var status = document.getElementById('tree-external-records-status');
    var container = document.getElementById('tree-external-records-results');
    if (!status || !container) return;

    status.textContent = 'Searching all sources…';
    clearNode(container);

    try {
      var resp = await fetch('/api/external-records/search?person_id=' + encodeURIComponent(personId));
      if (!resp.ok) {
        var err = await resp.json().catch(function() { return {detail: 'Search failed'}; });
        status.textContent = err.detail || 'Search failed';
        return;
      }
      var data = await resp.json();
      status.textContent = '';
      renderExternalRecordResults(container, data.sources || []);
    } catch (e) {
      status.textContent = 'Search failed: ' + e.message;
    }
  }

  async function searchExternalSource(personId, source) {
    var status = document.getElementById('tree-external-records-status');
    var container = document.getElementById('tree-external-records-results');
    if (!status || !container) return;

    status.textContent = 'Searching ' + (SOURCE_LABELS[source] || source) + '…';
    clearNode(container);

    try {
      var resp = await fetch('/api/external-records/search?person_id=' + encodeURIComponent(personId) + '&source=' + encodeURIComponent(source));
      if (!resp.ok) {
        var err = await resp.json().catch(function() { return {detail: 'Search failed'}; });
        status.textContent = err.detail || 'Search failed';
        return;
      }
      var data = await resp.json();
      status.textContent = '';
      renderExternalRecordResults(container, data.sources || []);
    } catch (e) {
      status.textContent = 'Search failed: ' + e.message;
    }
  }

  function renderExternalRecordResults(container, sources) {
    clearNode(container);
    if (!sources || sources.length === 0) {
      container.textContent = 'No sources returned.';
      return;
    }

    sources.forEach(function(src) {
      var section = document.createElement('details');
      section.className = 'tree-external-source-group';
      section.open = src.results && src.results.length > 0;

      var summary = document.createElement('summary');
      var label = SOURCE_LABELS[src.source] || src.source;
      var count = src.total_count || (src.results ? src.results.length : 0);
      summary.textContent = label + ' (' + count + ')';
      if (src.error) {
        summary.textContent += ' — ' + src.error;
      }
      if (!src.available) {
        summary.textContent += ' [not configured]';
      }
      section.appendChild(summary);

      if (src.results && src.results.length > 0) {
        var list = document.createElement('div');
        list.className = 'tree-external-results-list';
        src.results.forEach(function(result) {
          var item = document.createElement('div');
          item.className = 'tree-external-result-item';

          var titleEl = document.createElement('div');
          titleEl.className = 'tree-external-result-item__title';
          if (result.url) {
            var link = document.createElement('a');
            link.href = result.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = result.title || 'View record';
            titleEl.appendChild(link);
          } else {
            titleEl.textContent = result.title || 'Record';
          }
          item.appendChild(titleEl);

          var meta = [];
          if (result.date) meta.push(result.date);
          if (result.location) meta.push(result.location);
          if (result.record_type && result.record_type !== 'link') meta.push(result.record_type);
          if (meta.length) {
            var metaEl = document.createElement('div');
            metaEl.className = 'tree-external-result-item__meta';
            metaEl.textContent = meta.join(' · ');
            item.appendChild(metaEl);
          }

          if (result.snippet) {
            var snippetEl = document.createElement('div');
            snippetEl.className = 'tree-external-result-item__snippet';
            snippetEl.textContent = result.snippet;
            item.appendChild(snippetEl);
          }

          // Save button
          var savedRecordsEl = document.getElementById('tree-saved-records');
          var personId = savedRecordsEl ? savedRecordsEl.dataset.personId : '';
          if (personId && result.title) {
            var saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn--ghost btn--xs';
            saveBtn.textContent = 'Save';
            saveBtn.onclick = (function(r, btn) {
              return function() { saveExternalRecord(personId, r, btn); };
            })(result, saveBtn);
            item.appendChild(saveBtn);
          }

          list.appendChild(item);
        });
        section.appendChild(list);
      }

      container.appendChild(section);
    });
  }

  // ── Saved Records ──────────────────────────────────────────────────

  async function saveExternalRecord(personId, result, btn) {
    try {
      btn.disabled = true;
      btn.textContent = 'Saving…';
      var resp = await fetch('/api/research/saved-records', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          person_id: personId,
          title: result.title || 'Untitled',
          url: result.url || null,
          source: result.source || 'unknown',
          snippet: result.snippet || null
        })
      });
      if (resp.ok) {
        btn.textContent = 'Saved';
        loadSavedRecords(personId);
      } else {
        btn.textContent = 'Error';
        setTimeout(function() { btn.textContent = 'Save'; btn.disabled = false; }, 2000);
      }
    } catch (e) {
      btn.textContent = 'Error';
      setTimeout(function() { btn.textContent = 'Save'; btn.disabled = false; }, 2000);
    }
  }

  async function loadSavedRecords(personId) {
    var container = document.getElementById('tree-saved-records');
    if (!container) return;

    try {
      var resp = await fetch('/api/research/saved-records/' + encodeURIComponent(personId));
      if (!resp.ok) return;
      var data = await resp.json();
      clearNode(container);

      if (!data.records || data.records.length === 0) return;

      var heading = document.createElement('h4');
      heading.className = 'tree-sidebar-card__section-title';
      heading.style.marginTop = '1rem';
      heading.textContent = 'Saved Records (' + data.records.length + ')';
      container.appendChild(heading);

      data.records.forEach(function(record) {
        var item = document.createElement('div');
        item.className = 'tree-external-result-item tree-saved-record-item';

        var titleEl = document.createElement('div');
        titleEl.className = 'tree-external-result-item__title';
        if (record.url) {
          var link = document.createElement('a');
          link.href = record.url;
          link.target = '_blank';
          link.rel = 'noopener noreferrer';
          link.textContent = record.title;
          titleEl.appendChild(link);
        } else {
          titleEl.textContent = record.title;
        }
        item.appendChild(titleEl);

        var metaEl = document.createElement('div');
        metaEl.className = 'tree-external-result-item__meta';
        metaEl.textContent = (SOURCE_LABELS[record.source] || record.source);
        item.appendChild(metaEl);

        if (record.snippet) {
          var snippetEl = document.createElement('div');
          snippetEl.className = 'tree-external-result-item__snippet';
          snippetEl.textContent = record.snippet;
          item.appendChild(snippetEl);
        }

        var delBtn = document.createElement('button');
        delBtn.type = 'button';
        delBtn.className = 'btn btn--ghost btn--xs btn--danger';
        delBtn.textContent = 'Remove';
        delBtn.onclick = (function(rid) {
          return function() { deleteSavedRecord(rid, personId); };
        })(record.id);
        item.appendChild(delBtn);

        container.appendChild(item);
      });
    } catch (e) {
      // Silently fail
    }
  }

  async function deleteSavedRecord(recordId, personId) {
    try {
      var resp = await fetch('/api/research/saved-records/' + encodeURIComponent(recordId), {
        method: 'DELETE'
      });
      if (resp.ok) {
        loadSavedRecords(personId);
      }
    } catch (e) {
      // Silently fail
    }
  }

  // ── CEMLA Search ──────────────────────────────────────────────────

  async function searchCemla(event) {
    event.preventDefault();
    var form = event.target;
    var container = document.getElementById('tree-cemla-results');
    if (!container) return;

    var surname = form.querySelector('[name="cemla_surname"]').value.trim();
    var givenName = form.querySelector('[name="cemla_given_name"]').value.trim();
    var yearFrom = form.querySelector('[name="cemla_year_from"]').value.trim();
    var yearTo = form.querySelector('[name="cemla_year_to"]').value.trim();

    if (!surname) {
      container.textContent = 'Surname is required.';
      return;
    }

    container.textContent = 'Searching CEMLA…';

    try {
      var url = '/api/external-records/cemla?surname=' + encodeURIComponent(surname);
      if (givenName) url += '&given_name=' + encodeURIComponent(givenName);
      if (yearFrom) url += '&year_from=' + encodeURIComponent(yearFrom);
      if (yearTo) url += '&year_to=' + encodeURIComponent(yearTo);

      var resp = await fetch(url);
      if (!resp.ok) {
        var err = await resp.json().catch(function() { return {detail: 'Search failed'}; });
        container.textContent = err.detail || 'Search failed';
        return;
      }
      var data = await resp.json();
      renderCemlaResults(container, data);
    } catch (e) {
      container.textContent = 'Search failed: ' + e.message;
    }
  }

  function renderCemlaResults(container, data) {
    clearNode(container);

    if (data.error) {
      var msg = document.createElement('p');
      msg.className = 'tree-sidebar-card__muted';
      msg.textContent = data.error;
      container.appendChild(msg);
    }

    if (data.results && data.results.length > 0) {
      var list = document.createElement('div');
      list.className = 'tree-external-results-list';
      data.results.forEach(function(r) {
        var item = document.createElement('div');
        item.className = 'tree-external-result-item';

        var titleEl = document.createElement('div');
        titleEl.className = 'tree-external-result-item__title';
        titleEl.textContent = r.passenger_name || 'Unknown';
        item.appendChild(titleEl);

        var meta = [];
        if (r.ship_name) meta.push('Ship: ' + r.ship_name);
        if (r.arrival_date) meta.push(r.arrival_date);
        if (r.nationality) meta.push(r.nationality);
        if (meta.length) {
          var metaEl = document.createElement('div');
          metaEl.className = 'tree-external-result-item__meta';
          metaEl.textContent = meta.join(' · ');
          item.appendChild(metaEl);
        }

        var ports = [];
        if (r.departure_port) ports.push('From: ' + r.departure_port);
        if (r.arrival_port) ports.push('To: ' + r.arrival_port);
        if (ports.length) {
          var portsEl = document.createElement('div');
          portsEl.className = 'tree-external-result-item__snippet';
          portsEl.textContent = ports.join(' · ');
          item.appendChild(portsEl);
        }

        list.appendChild(item);
      });
      container.appendChild(list);
    }

    if (data.fallback_url) {
      var linkWrap = document.createElement('p');
      linkWrap.className = 'tree-sidebar-card__muted';
      linkWrap.style.marginTop = '0.5rem';
      var link = document.createElement('a');
      link.href = data.fallback_url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Search CEMLA directly →';
      linkWrap.appendChild(link);
      container.appendChild(linkWrap);
    }
  }

  // ── GEDCOM Upload ─────────────────────────────────────────────────

  function _buildProgressBar(container) {
    clearNode(container);
    var wrap = document.createElement('div');
    wrap.className = 'tree-gedcom-progress';
    var bar = document.createElement('div');
    bar.className = 'tree-gedcom-progress__bar';
    var fill = document.createElement('div');
    fill.className = 'tree-gedcom-progress__fill';
    fill.style.width = '0%';
    bar.appendChild(fill);
    var label = document.createElement('div');
    label.className = 'tree-gedcom-progress__label';
    label.textContent = 'Uploading…';
    wrap.appendChild(bar);
    wrap.appendChild(label);
    container.appendChild(wrap);
    return { fill: fill, label: label };
  }

  async function uploadGedcom(event) {
    event.preventDefault();
    var form = event.target;
    var errorEl = document.getElementById('tree-gedcom-error');
    var resultsEl = document.getElementById('tree-gedcom-results');

    if (errorEl) { errorEl.textContent = ''; errorEl.classList.add('hidden'); }
    if (resultsEl) clearNode(resultsEl);

    var fileInput = form.querySelector('[name="gedcom_file"]');
    if (!fileInput || !fileInput.files || !fileInput.files.length) {
      if (errorEl) { errorEl.textContent = 'Please select a GEDCOM file.'; errorEl.classList.remove('hidden'); }
      return;
    }

    var file = fileInput.files[0];
    if (file.size > 10 * 1024 * 1024) {
      if (errorEl) { errorEl.textContent = 'File exceeds 10MB limit.'; errorEl.classList.remove('hidden'); }
      return;
    }

    var formData = new FormData();
    formData.append('file', file);

    // Build progress bar
    var progress = resultsEl ? _buildProgressBar(resultsEl) : null;

    // Use XHR for upload progress events
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/import/gedcom');

    if (progress) {
      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
          var pct = Math.round((e.loaded / e.total) * 100);
          progress.fill.style.width = pct + '%';
          progress.label.textContent = 'Uploading… ' + pct + '%';
        }
      });
      xhr.upload.addEventListener('load', function() {
        progress.fill.style.width = '100%';
        progress.label.textContent = 'Processing GEDCOM…';
        progress.fill.classList.add('tree-gedcom-progress__fill--processing');
      });
    }

    xhr.onload = function() {
      var data;
      try { data = JSON.parse(xhr.responseText); } catch (_e) { data = null; }

      if (xhr.status !== 200 || !data) {
        if (errorEl) {
          errorEl.textContent = (data && data.detail) || 'Import failed';
          errorEl.classList.remove('hidden');
        }
        if (resultsEl) clearNode(resultsEl);
        return;
      }

      if (resultsEl) {
        clearNode(resultsEl);
        var summary = document.createElement('div');
        summary.className = 'tree-gedcom-summary';
        summary.innerHTML =
          '<p><strong>' + escapeHTML(data.persons_created) + '</strong> persons created</p>' +
          '<p><strong>' + escapeHTML(data.relationships_created) + '</strong> relationships created</p>' +
          (data.duplicates_skipped ? '<p><strong>' + escapeHTML(data.duplicates_skipped) + '</strong> duplicates skipped</p>' : '');

        if (data.duplicate_candidates && data.duplicate_candidates.length) {
          var dupeList = '<details class="tree-sidebar-disclosure"><summary>' +
            escapeHTML(data.duplicate_candidates.length) + ' potential duplicates detected</summary><ul class="tree-gedcom-duplicates">';
          data.duplicate_candidates.forEach(function(d) {
            dupeList += '<li><strong>' + escapeHTML(d.gedcom_name) + '</strong> matches <em>' +
              escapeHTML(d.existing_name) + '</em> (' + escapeHTML(d.match_reason) + ')</li>';
          });
          dupeList += '</ul></details>';
          summary.innerHTML += dupeList;
        }

        if (data.errors && data.errors.length) {
          summary.innerHTML += '<p class="form-error">' + escapeHTML(data.errors.join('; ')) + '</p>';
        }
        resultsEl.appendChild(summary);
      }

      // Reload the tree to show new persons
      if (typeof loadTree === 'function') loadTree();
      showToastMessage('GEDCOM import complete: ' + data.persons_created + ' persons, ' + data.relationships_created + ' relationships');
    };

    xhr.onerror = function() {
      if (errorEl) { errorEl.textContent = 'Import failed: network error'; errorEl.classList.remove('hidden'); }
      if (resultsEl) clearNode(resultsEl);
    };

    xhr.send(formData);
  }

  // ── GEDCOM Preview (two-phase import) ──────────────────────────────

  // Store the selected file between preview and confirm
  var _gedcomPendingFile = null;

  async function previewGedcom(event) {
    event.preventDefault();
    var form = event.target;
    var errorEl = document.getElementById('tree-gedcom-error');
    var previewEl = document.getElementById('tree-gedcom-preview');
    var resultsEl = document.getElementById('tree-gedcom-results');

    if (errorEl) { errorEl.textContent = ''; errorEl.classList.add('hidden'); }
    if (previewEl) clearNode(previewEl);
    if (resultsEl) clearNode(resultsEl);

    var fileInput = form.querySelector('[name="gedcom_file"]');
    if (!fileInput || !fileInput.files || !fileInput.files.length) {
      if (errorEl) { errorEl.textContent = 'Please select a GEDCOM file.'; errorEl.classList.remove('hidden'); }
      return;
    }

    var file = fileInput.files[0];
    if (file.size > 10 * 1024 * 1024) {
      if (errorEl) { errorEl.textContent = 'File exceeds 10MB limit.'; errorEl.classList.remove('hidden'); }
      return;
    }

    _gedcomPendingFile = file;
    if (previewEl) previewEl.textContent = 'Analyzing file…';

    try {
      var formData = new FormData();
      formData.append('file', file);
      var resp = await fetch('/api/import/gedcom/preview', { method: 'POST', body: formData });
      var data = await resp.json();

      if (!resp.ok) {
        if (errorEl) { errorEl.textContent = data.detail || 'Preview failed'; errorEl.classList.remove('hidden'); }
        if (previewEl) clearNode(previewEl);
        return;
      }

      renderGedcomPreview(previewEl, data);
    } catch (e) {
      if (errorEl) { errorEl.textContent = 'Preview failed: ' + e.message; errorEl.classList.remove('hidden'); }
      if (previewEl) clearNode(previewEl);
    }
  }

  function renderGedcomPreview(container, data) {
    clearNode(container);
    var wrap = document.createElement('div');
    wrap.className = 'tree-gedcom-preview';

    // Summary line
    var summary = document.createElement('p');
    summary.innerHTML = 'Found <strong>' + escapeHTML(data.individuals_count) +
      '</strong> individuals and <strong>' + escapeHTML(data.families_count) + '</strong> families.';
    wrap.appendChild(summary);

    // Duplicate candidates section
    var dupes = (data.individuals || []).filter(function(i) { return i.is_duplicate; });
    if (dupes.length > 0) {
      var dupeSection = document.createElement('div');
      dupeSection.className = 'tree-gedcom-preview__dupes';
      var heading = document.createElement('p');
      heading.innerHTML = '<strong>' + escapeHTML(dupes.length) +
        '</strong> potential duplicate(s) detected — these will be skipped:';
      dupeSection.appendChild(heading);

      var dupeList = document.createElement('ul');
      dupeList.className = 'tree-gedcom-duplicates';
      dupes.forEach(function(d) {
        var li = document.createElement('li');
        li.innerHTML = '<strong>' + escapeHTML(d.name) + '</strong>';
        if (d.duplicate_match) {
          li.innerHTML += ' matches <em>' + escapeHTML(d.duplicate_match.existing_name) +
            '</em> (' + escapeHTML(d.duplicate_match.match_reason) + ')';
        }
        dupeList.appendChild(li);
      });
      dupeSection.appendChild(dupeList);
      wrap.appendChild(dupeSection);
    }

    // New individuals to be created
    var newIndividuals = (data.individuals || []).filter(function(i) { return !i.is_duplicate; });
    if (newIndividuals.length > 0) {
      var newSection = document.createElement('details');
      newSection.className = 'tree-sidebar-disclosure';
      var newSummary = document.createElement('summary');
      newSummary.textContent = newIndividuals.length + ' new person(s) to create';
      newSection.appendChild(newSummary);
      var newList = document.createElement('ul');
      newList.className = 'tree-gedcom-duplicates';
      newIndividuals.forEach(function(n) {
        var li = document.createElement('li');
        var text = escapeHTML(n.name);
        if (n.birth_date) text += ' (b. ' + escapeHTML(n.birth_date) + ')';
        li.innerHTML = text;
        newList.appendChild(li);
      });
      newSection.appendChild(newList);
      wrap.appendChild(newSection);
    }

    // Confirm / Cancel buttons
    var actions = document.createElement('div');
    actions.className = 'tree-gedcom-preview__actions';
    actions.style.marginTop = '10px';
    actions.style.display = 'flex';
    actions.style.gap = '8px';

    var confirmBtn = document.createElement('button');
    confirmBtn.type = 'button';
    confirmBtn.className = 'btn btn--primary';
    confirmBtn.textContent = 'Confirm Import';
    confirmBtn.addEventListener('click', function() { confirmGedcomImport(); });
    actions.appendChild(confirmBtn);

    var cancelBtn = document.createElement('button');
    cancelBtn.type = 'button';
    cancelBtn.className = 'btn btn--ghost';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.addEventListener('click', function() {
      clearNode(container);
      _gedcomPendingFile = null;
    });
    actions.appendChild(cancelBtn);

    wrap.appendChild(actions);
    container.appendChild(wrap);
  }

  function confirmGedcomImport() {
    if (!_gedcomPendingFile) return;
    // Simulate a form submit event for uploadGedcom
    var errorEl = document.getElementById('tree-gedcom-error');
    var previewEl = document.getElementById('tree-gedcom-preview');
    var resultsEl = document.getElementById('tree-gedcom-results');

    if (previewEl) clearNode(previewEl);

    var formData = new FormData();
    formData.append('file', _gedcomPendingFile);
    _gedcomPendingFile = null;

    // Build progress bar
    var progress = resultsEl ? _buildProgressBar(resultsEl) : null;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/import/gedcom');

    if (progress) {
      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
          var pct = Math.round((e.loaded / e.total) * 100);
          progress.fill.style.width = pct + '%';
          progress.label.textContent = 'Uploading… ' + pct + '%';
        }
      });
      xhr.upload.addEventListener('load', function() {
        progress.fill.style.width = '100%';
        progress.label.textContent = 'Processing GEDCOM…';
        progress.fill.classList.add('tree-gedcom-progress__fill--processing');
      });
    }

    xhr.onload = function() {
      var data;
      try { data = JSON.parse(xhr.responseText); } catch (_e) { data = null; }

      if (xhr.status !== 200 || !data) {
        if (errorEl) { errorEl.textContent = (data && data.detail) || 'Import failed'; errorEl.classList.remove('hidden'); }
        if (resultsEl) clearNode(resultsEl);
        return;
      }

      if (resultsEl) {
        clearNode(resultsEl);
        var summary = document.createElement('div');
        summary.className = 'tree-gedcom-summary';
        summary.innerHTML =
          '<p><strong>' + escapeHTML(data.persons_created) + '</strong> persons created</p>' +
          '<p><strong>' + escapeHTML(data.relationships_created) + '</strong> relationships created</p>' +
          (data.duplicates_skipped ? '<p><strong>' + escapeHTML(data.duplicates_skipped) + '</strong> duplicates skipped</p>' : '');
        resultsEl.appendChild(summary);
      }

      if (typeof loadTree === 'function') loadTree();
      showToastMessage('GEDCOM import complete: ' + data.persons_created + ' persons, ' + data.relationships_created + ' relationships');
    };

    xhr.onerror = function() {
      if (errorEl) { errorEl.textContent = 'Import failed: network error'; errorEl.classList.remove('hidden'); }
      if (resultsEl) clearNode(resultsEl);
    };

    xhr.send(formData);
  }

  function collectJsonArrayEntries(fieldName) {
    var container = document.getElementById('tree-' + fieldName + '-entries');
    if (!container) return [];
    var entries = container.querySelectorAll('.tree-json-entry[data-json-field="' + fieldName + '"]');
    var result = [];
    entries.forEach(function(entry) {
      var obj = {};
      var inputs = entry.querySelectorAll('[data-key]');
      var hasValue = false;
      inputs.forEach(function(input) {
        var val = input.value.trim();
        if (val) {
          obj[input.getAttribute('data-key')] = val;
          hasValue = true;
        }
      });
      if (hasValue) result.push(obj);
    });
    return result;
  }

  function addJsonArrayEntry(fieldName) {
    var container = document.getElementById('tree-' + fieldName + '-entries');
    if (!container) return;
    var templates = {
      education: '<div class="tree-json-entry" data-json-field="education"><div class="tree-inline-form__row"><label>Institution<input class="form-input" type="text" data-key="institution"></label><label>Degree<input class="form-input" type="text" data-key="degree"></label></div><div class="tree-inline-form__row"><label>Field<input class="form-input" type="text" data-key="field_of_study"></label><label>Start Year<input class="form-input" type="text" data-key="year_start"></label></div><div class="tree-inline-form__row"><label>End Year<input class="form-input" type="text" data-key="year_end"></label><label>Notes<input class="form-input" type="text" data-key="notes"></label></div><button type="button" class="btn btn--ghost btn--sm" onclick="this.closest(\'.tree-json-entry\').remove()">Remove</button></div>',
      career: '<div class="tree-json-entry" data-json-field="career"><div class="tree-inline-form__row"><label>Employer<input class="form-input" type="text" data-key="employer"></label><label>Title<input class="form-input" type="text" data-key="title"></label></div><div class="tree-inline-form__row"><label>Start Year<input class="form-input" type="text" data-key="year_start"></label><label>End Year<input class="form-input" type="text" data-key="year_end"></label></div><div class="tree-inline-form__row"><label>Location<input class="form-input" type="text" data-key="location"></label><label>Notes<input class="form-input" type="text" data-key="notes"></label></div><button type="button" class="btn btn--ghost btn--sm" onclick="this.closest(\'.tree-json-entry\').remove()">Remove</button></div>',
      organizations: '<div class="tree-json-entry" data-json-field="organizations"><div class="tree-inline-form__row"><label>Organization<input class="form-input" type="text" data-key="name"></label><label>Role<input class="form-input" type="text" data-key="role"></label></div><div class="tree-inline-form__row"><label>Year Joined<input class="form-input" type="text" data-key="year_joined"></label><label>Year Left<input class="form-input" type="text" data-key="year_left"></label></div><label>Notes<input class="form-input" type="text" data-key="notes"></label><button type="button" class="btn btn--ghost btn--sm" onclick="this.closest(\'.tree-json-entry\').remove()">Remove</button></div>',
      admixture: '<div class="tree-json-entry" data-json-field="admixture"><div class="tree-inline-form__row"><label>Ethnicity<input class="form-input" type="text" data-key="ethnicity"></label><label>Percentage<input class="form-input" type="text" data-key="percentage"></label></div><label>Source<input class="form-input" type="text" data-key="source"></label><button type="button" class="btn btn--ghost btn--sm" onclick="this.closest(\'.tree-json-entry\').remove()">Remove</button></div>',
      medical_conditions: '<div class="tree-json-entry" data-json-field="medical_conditions"><div class="tree-inline-form__row"><label>Condition<input class="form-input" type="text" data-key="condition"></label><label>Onset Age<input class="form-input" type="text" data-key="onset_age"></label></div><div class="tree-inline-form__row"><label>Status<select class="form-input" data-key="status"><option value="">—</option><option value="active">Active</option><option value="resolved">Resolved</option><option value="managed">Managed</option><option value="unknown">Unknown</option></select></label><label>Severity<input class="form-input" type="text" data-key="severity"></label></div><label>Treatment<input class="form-input" type="text" data-key="treatment"></label><div class="tree-inline-form__row"><label>Hereditary Line<select class="form-input" data-key="hereditary_line"><option value="">—</option><option value="maternal">Maternal</option><option value="paternal">Paternal</option><option value="both">Both</option><option value="unknown">Unknown</option></select></label><label>Notes<input class="form-input" type="text" data-key="notes"></label></div><button type="button" class="btn btn--ghost btn--sm" onclick="this.closest(\'.tree-json-entry\').remove()">Remove</button></div>'
    };
    if (templates[fieldName]) {
      container.insertAdjacentHTML('beforeend', templates[fieldName]);
    }
  }

  // ── Add Person Panel (inline sidebar form) ────────────────────────
  window.openAddPersonPanel = function() {
    var addLabel = root.dataset.treeAddNewPerson || 'Add New Person';
    var createLabel = root.dataset.treeCreatePerson || 'Create';
    var firstNameLabel = root.dataset.treeFirstNameLabel || 'First Name';
    var lastNameLabel = root.dataset.treeLastNameLabel || 'Last Name';
    var branchLabel = root.dataset.treeBranchLabel || 'Branch';

    sidebar.classList.add('person-sidebar--open');
    window.openAccessibleOverlay(sidebar, {initialFocus: '#add-person-first-name'});

    var html = '<div class="tree-sidebar-card" style="padding-top: 56px;">' +
      '<button class="person-sidebar__close" type="button" aria-label="Close" onclick="closeSidebar()" style="position:absolute;top:12px;right:12px;">&times;</button>' +
      '<h2 class="tree-sidebar-card__title" style="margin-bottom:16px;">' + escapeHTML(addLabel) + '</h2>' +
      '<form id="add-person-inline-form" onsubmit="return false;">' +
      '<div class="form-group" style="margin-bottom:12px;"><label for="add-person-first-name">' + escapeHTML(firstNameLabel) + '</label>' +
      '<input type="text" class="form-input" id="add-person-first-name" required></div>' +
      '<div class="form-group" style="margin-bottom:12px;"><label for="add-person-last-name">' + escapeHTML(lastNameLabel) + '</label>' +
      '<input type="text" class="form-input" id="add-person-last-name"></div>' +
      '<div class="form-group" style="margin-bottom:16px;"><label for="add-person-branch">' + escapeHTML(branchLabel) + '</label>' +
      '<input type="text" class="form-input" id="add-person-branch" placeholder="optional"></div>' +
      '<button type="submit" class="btn btn--primary" id="add-person-submit" style="width:100%;">' + escapeHTML(createLabel) + '</button>' +
      '</form></div>';

    window.replaceNodeChildrenFromHTML(sidebarContent, html);

    var form = document.getElementById('add-person-inline-form');
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      var btn = document.getElementById('add-person-submit');
      btn.disabled = true;
      btn.textContent = '...';
      var firstName = document.getElementById('add-person-first-name').value.trim();
      var lastName = document.getElementById('add-person-last-name').value.trim();
      var branch = document.getElementById('add-person-branch').value.trim();
      if (!firstName) { btn.disabled = false; btn.textContent = createLabel; return; }
      var body = { first_name: firstName, source: 'manual' };
      if (lastName) body.last_name = lastName;
      if (branch) body.branch = branch;
      try {
        var resp = await fetch('/api/persons', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(body)
        });
        if (resp.ok) {
          var newPerson = await resp.json();
          await loadTree();
          closeSidebar();
          if (newPerson && newPerson.id) {
            openPersonSidebar(newPerson.id);
          }
          showToastMessage(root.dataset.createdMessage || 'Person created');
        } else {
          var err = await resp.json().catch(function() { return {detail: 'Failed'}; });
          btn.textContent = err.detail || 'Failed';
          btn.disabled = false;
        }
      } catch(ex) {
        btn.textContent = 'Error';
        btn.disabled = false;
      }
    });
  };

  window.collectJsonArrayEntries = collectJsonArrayEntries;
  window.addJsonArrayEntry = addJsonArrayEntry;
  window.saveTreePerson = saveTreePerson;
  window.linkTreeRelationship = linkTreeRelationship;
  window.createTreeRelative = createTreeRelative;
  window.removeTreeRelationship = removeTreeRelationship;
  window.replaceTreeRelationship = replaceTreeRelationship;
  window.openTreeSidebarPerson = openTreeSidebarPerson;
  window.switchTreeSidebarTab = switchTreeSidebarTab;
  window.openSidebarDetailsSection = openSidebarDetailsSection;
  window.uploadTreeMedia = uploadTreeMedia;
  window.startTreeGraphMode = startTreeGraphMode;
  window.cancelTreeGraphMode = cancelTreeGraphMode;
  window.openTreeRelationshipSearch = openTreeRelationshipSearch;
  window.openTreeRelationshipCreate = openTreeRelationshipCreate;
  window.searchAllExternalRecords = searchAllExternalRecords;
  window.searchExternalSource = searchExternalSource;
  window.searchCemla = searchCemla;
  window.uploadGedcom = uploadGedcom;
  window.previewGedcom = previewGedcom;
  window.confirmGedcomImport = confirmGedcomImport;

  // ── Relationship Calculator ─────────────────────────────────────
  var _relCalcMode = false;
  var _relCalcFirst = null;

  function startRelationshipCalc() {
    if (sidebarState.graphMode) {
      cancelTreeGraphMode(true);
    }
    _relCalcMode = true;
    _relCalcFirst = null;
    var banner = document.getElementById('tree-relcalc-banner');
    if (banner) {
      banner.textContent = root.dataset.treeRelcalcStepOne;
      banner.hidden = false;
    }
    syncRelationshipCalcControls();
    syncInteractionModeClasses();
    if (treeData) {
      render();
    }
  }

  function cancelRelationshipCalc(silent) {
    _relCalcMode = false;
    _relCalcFirst = null;
    var banner = document.getElementById('tree-relcalc-banner');
    if (banner) banner.hidden = true;
    _clearPathHighlight();
    var resultPanel = document.getElementById('tree-relcalc-result');
    if (resultPanel) resultPanel.hidden = true;
    syncRelationshipCalcControls();
    syncInteractionModeClasses();
    if (!silent) {
      restoreDefaultStatus();
    }
    if (treeData) {
      render();
    }
  }

  function _handleRelCalcClick(personId) {
    if (!_relCalcFirst) {
      _relCalcFirst = personId;
      var banner = document.getElementById('tree-relcalc-banner');
      if (banner) banner.textContent = root.dataset.treeRelcalcStepTwo;
      // Highlight first node
      d3.selectAll('.tree-node').classed('tree-node--relcalc-selected', function() {
        return d3.select(this).attr('data-person-id') === personId;
      });
      return true;
    }
    if (personId === _relCalcFirst) return true;
    // Second person selected — compute path
    _computeRelationship(_relCalcFirst, personId);
    return true;
  }

  async function _computeRelationship(fromId, toId) {
    var banner = document.getElementById('tree-relcalc-banner');
    if (banner) banner.textContent = root.dataset.treeRelcalcComputing;
    try {
      var resp = await fetch('/api/relationships/path?from=' + encodeURIComponent(fromId) + '&to=' + encodeURIComponent(toId));
      if (!resp.ok) throw new Error('API error');
      var data = await resp.json();
      _showRelationshipResult(data);
      if (data.found && data.path.length > 0) {
        _highlightPath(data.path);
      }
    } catch (err) {
      if (banner) banner.textContent = root.dataset.treeRelcalcError;
    }
    _relCalcMode = false;
    _relCalcFirst = null;
    if (banner) banner.hidden = true;
    syncRelationshipCalcControls();
    syncInteractionModeClasses();
  }

  function _showRelationshipResult(data) {
    var panel = document.getElementById('tree-relcalc-result');
    if (!panel) return;
    panel.hidden = false;
    var label = panel.querySelector('.tree-relcalc-result__label');
    var details = panel.querySelector('.tree-relcalc-result__details');
    if (label) {
      label.textContent = data.found ? data.relationship_label : 'No relationship path found';
    }
    if (details && data.path_details) {
      details.innerHTML = '';
      data.path_details.forEach(function(edge) {
        var div = document.createElement('div');
        div.className = 'tree-relcalc-result__step';
        div.textContent = edge.from_name + ' \u2192 ' + edge.to_name + ' (' + edge.edge_kind + ')';
        details.appendChild(div);
      });
    }
  }

  function _highlightPath(pathIds) {
    _clearPathHighlight();
    var pathSet = new Set(pathIds);
    d3.selectAll('.tree-node').classed('tree-node--path-highlight', function() {
      return pathSet.has(d3.select(this).attr('data-person-id'));
    });
    // Highlight edges
    var pathPairs = new Set();
    for (var i = 0; i < pathIds.length - 1; i++) {
      pathPairs.add(pathIds[i] + '|' + pathIds[i + 1]);
      pathPairs.add(pathIds[i + 1] + '|' + pathIds[i]);
    }
    d3.selectAll('.parent-child-line, .partnership-line').classed('edge--path-highlight', function() {
      var el = d3.select(this);
      var from = el.attr('data-from');
      var to = el.attr('data-to');
      return from && to && pathPairs.has(from + '|' + to);
    });
  }

  function _clearPathHighlight() {
    d3.selectAll('.tree-node--path-highlight').classed('tree-node--path-highlight', false);
    d3.selectAll('.tree-node--relcalc-selected').classed('tree-node--relcalc-selected', false);
    d3.selectAll('.edge--path-highlight').classed('edge--path-highlight', false);
  }

  window.startRelationshipCalc = startRelationshipCalc;
  window.cancelRelationshipCalc = cancelRelationshipCalc;

  document.getElementById('save-tree-preferences').addEventListener('click', savePreferences);
  document.getElementById('apply-tree-filters').addEventListener('click', function() {
    window.closeSidebar();
    loadTree();
  });
  document.getElementById('reset-tree-filters').addEventListener('click', function() {
    document.getElementById('tree-filter-living').value = 'all';
    document.getElementById('tree-filter-branch').value = '';
    document.getElementById('tree-filter-residence-country').value = '';
    document.getElementById('tree-filter-birth-country').value = '';
    window.closeSidebar();
    loadTree();
  });

  document.addEventListener('keydown', function(event) {
    if (event.key !== 'Escape') {
      return;
    }
    if (searchResults && !searchResults.hidden) {
      event.preventDefault();
      event.stopPropagation();
      hideSearchResults();
      return;
    }
    if (sidebarState.graphMode) {
      event.preventDefault();
      event.stopPropagation();
      cancelTreeGraphMode(true);
      return;
    }
    if (_relCalcMode) {
      event.preventDefault();
      event.stopPropagation();
      cancelRelationshipCalc(true);
      return;
    }
  }, true);

  var resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      if (treeData) {
        render();
      }
    }, 250);
  });

  init();
})();
