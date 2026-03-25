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
    momentFilter: 'all',
    relationshipGroup: '',
    peopleOptions: [],
    highlightMomentId: '',
    highlightMediaId: ''
  };
  var preferences = {
    show_names: true,
    show_birth_dates: false,
    show_country_flags: true,
    show_photos: true
  };
  var NODE_RADIUS = 30;
  var NODE_SPACING_X = 100;
  var NODE_SPACING_Y = 150;

  var root = document.getElementById('tree-root');
  var statusNode = document.getElementById('tree-status');
  var sidebar = document.getElementById('person-sidebar');
  var sidebarContent = document.getElementById('sidebar-content');

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
    document.getElementById('pref-show-birth-dates').checked = !!preferences.show_birth_dates;
    document.getElementById('pref-show-country-flags').checked = !!preferences.show_country_flags;
    document.getElementById('pref-show-photos').checked = !!preferences.show_photos;
  }

  function readPreferenceInputs() {
    preferences = {
      show_names: document.getElementById('pref-show-names').checked,
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

  function chooseDefaultSidebarTab() {
    var card = getSidebarCard();
    if (!card) {
      return 'overview';
    }
    if (sidebarState.activeTab && sidebarContent.querySelector('[data-tree-sidebar-panel="' + sidebarState.activeTab + '"]')) {
      return sidebarState.activeTab;
    }
    var canManage = card.dataset.treeSidebarCanManage === 'true';
    var storyCount = Number(card.dataset.treeSidebarStoryCount || 0);
    var mediaCount = Number(card.dataset.treeSidebarMediaCount || 0);
    var relationCount = Number(card.dataset.treeSidebarParentCount || 0) +
      Number(card.dataset.treeSidebarChildCount || 0) +
      Number(card.dataset.treeSidebarPartnerCount || 0);
    if (canManage && storyCount === 0) {
      sidebarState.momentFilter = 'story';
      return 'moments';
    }
    if (canManage && mediaCount === 0) {
      return 'media';
    }
    if (canManage && relationCount === 0) {
      sidebarState.relationshipGroup = 'parent';
      return 'relationships';
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

  function createMomentNode(moment) {
    var article = document.createElement('article');
    article.className = 'tree-sidebar-moment';
    if (sidebarState.highlightMomentId && sidebarState.highlightMomentId === moment.id) {
      article.classList.add('tree-sidebar-moment--highlight');
    }

    var isSharedEvent = !!(moment.tagged_people && moment.tagged_people.length);

    var meta = document.createElement('div');
    meta.className = 'tree-sidebar-moment__meta';
    meta.textContent = moment.kind === 'story'
      ? root.dataset.treeStoryLabel
      : root.dataset.treeMomentLabel;
    if (isSharedEvent) {
      meta.textContent = root.dataset.treeSharedEventLabel + ' · ' + meta.textContent;
    }
    if (moment.occurred_at) {
      meta.textContent += ' · ' + formatDateLabel(moment.occurred_at);
    }
    article.appendChild(meta);

    if (moment.about && moment.about.display_name) {
      var about = document.createElement('p');
      about.className = 'tree-sidebar-moment__about';
      about.textContent = root.dataset.aboutLabel + ' ' + moment.about.display_name;
      article.appendChild(about);
    }

    if (moment.title) {
      var title = document.createElement('h4');
      title.className = 'tree-sidebar-moment__title';
      title.textContent = moment.title;
      article.appendChild(title);
    }

    if (moment.body) {
      var body = document.createElement('p');
      body.className = 'tree-sidebar-moment__body';
      body.textContent = moment.body;
      article.appendChild(body);
    }

    if (moment.media && moment.media.length) {
      if (moment.media.length > 1) {
        var bundle = document.createElement('div');
        bundle.className = 'tree-sidebar-bundle';
        var bundleLabel = document.createElement('strong');
        bundleLabel.className = 'tree-sidebar-bundle__title';
        bundleLabel.textContent = root.dataset.treeBundleLabel;
        bundle.appendChild(bundleLabel);
        var bundleMeta = document.createElement('span');
        bundleMeta.className = 'tree-sidebar-bundle__meta';
        bundleMeta.textContent = root.dataset.treeBundleItemsLabel.replace('{count}', String(moment.media.length));
        bundle.appendChild(bundleMeta);
        article.appendChild(bundle);
      }
      var mediaStrip = document.createElement('div');
      mediaStrip.className = 'tree-sidebar-moment__media-strip';
      moment.media.slice(0, 3).forEach(function(media) {
        var thumb = document.createElement('button');
        thumb.type = 'button';
        thumb.className = 'tree-sidebar-moment__media-thumb';
        thumb.addEventListener('click', function() {
          if (typeof window.openLightbox === 'function') {
            window.openLightbox('/api/media/' + media.id + '/file', media.caption || root.dataset.openMediaLabel);
          } else {
            window.location.href = '/api/media/' + media.id + '/file';
          }
        });
        var img = document.createElement('img');
        img.src = '/api/media/' + media.id + '/thumbnail';
        img.alt = media.caption || root.dataset.openMediaLabel;
        img.loading = 'lazy';
        thumb.appendChild(img);
        mediaStrip.appendChild(thumb);
      });
      article.appendChild(mediaStrip);
    }

    var metaRow = document.createElement('div');
    metaRow.className = 'tree-sidebar-meta-row';
    if (moment.comment_count) {
      var commentsChip = document.createElement('span');
      commentsChip.className = 'tree-sidebar-pill';
      commentsChip.textContent = moment.comment_count + ' ' + root.dataset.commentCountLabel;
      metaRow.appendChild(commentsChip);
    }
    if (moment.tagged_people && moment.tagged_people.length) {
      var taggedChip = document.createElement('span');
      taggedChip.className = 'tree-sidebar-pill';
      taggedChip.textContent = root.dataset.taggedPeopleLabel + ': ' + buildTaggedPeopleSummary(moment.tagged_people);
      metaRow.appendChild(taggedChip);
    }
    if (metaRow.childElementCount) {
      article.appendChild(metaRow);
    }

    var actions = document.createElement('div');
    actions.className = 'tree-sidebar-item-actions';
    if (moment.about && moment.about.id) {
      actions.appendChild(createMiniAction(root.dataset.viewProfileLabel, function() {
        window.location.href = '/people/' + moment.about.id;
      }));
    }
    actions.appendChild(createMiniAction(root.dataset.openMomentsLabel, function() {
      var targetId = moment.about && moment.about.id ? moment.about.id : getSidebarPersonId();
      window.location.href = '/moments?person=' + encodeURIComponent(targetId);
    }));
    article.appendChild(actions);
    return article;
  }

  function renderTreeMoments(moments) {
    var container = document.getElementById('tree-sidebar-moments');
    if (!container) {
      return;
    }
    container.setAttribute('aria-busy', 'false');
    if (sidebarState.momentFilter === 'shared') {
      moments = moments.filter(function(moment) {
        return moment.tagged_people && moment.tagged_people.length;
      });
    }
    if (!moments.length) {
      renderEmptyTreeStream(
        container,
        sidebarState.momentFilter === 'story'
          ? root.dataset.emptyStoryMoments
          : (sidebarState.momentFilter === 'shared' ? root.dataset.emptySharedEvents : root.dataset.emptyMoments),
        getSidebarCanManage() ? (
          sidebarState.momentFilter === 'story'
            ? root.dataset.addFirstStory
            : (sidebarState.momentFilter === 'shared' ? root.dataset.addEventLabel : null)
        ) : null,
        function() {
          var form = document.getElementById('tree-moment-form');
          if (!form) {
            return;
          }
          if (sidebarState.momentFilter === 'shared') {
            var scopeSelect = form.querySelector('select[name="authoring_scope"]');
            if (scopeSelect) {
              scopeSelect.value = 'shared';
              toggleTreeMomentFields(form.querySelector('select[name="kind"]').value, 'shared');
            }
          }
          var bodyInput = form.querySelector('textarea[name="body"]');
          if (bodyInput) {
            bodyInput.focus();
          }
        }
      );
      return;
    }
    clearNode(container);
    moments.forEach(function(moment) {
      container.appendChild(createMomentNode(moment));
    });
    sidebarState.highlightMomentId = '';
  }

  function createMediaNode(media) {
    var item = document.createElement('div');
    item.className = 'tree-sidebar-media-item';
    if (sidebarState.highlightMediaId && sidebarState.highlightMediaId === media.id) {
      item.classList.add('tree-sidebar-media-item--highlight');
    }
    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.addEventListener('click', function() {
      if (typeof window.openLightbox === 'function') {
        window.openLightbox('/api/media/' + media.id + '/file', media.caption || root.dataset.openMediaLabel);
      } else {
        window.location.href = '/api/media/' + media.id + '/file';
      }
    });
    var img = document.createElement('img');
    img.src = '/api/media/' + media.id + '/thumbnail';
    img.alt = media.caption || 'Family media';
    img.loading = 'lazy';
    img.onerror = function() {
      img.src = '/api/media/' + media.id + '/file';
    };
    trigger.appendChild(img);
    item.appendChild(trigger);
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

  async function loadTreeSidebarMoments(personId) {
    var container = document.getElementById('tree-sidebar-moments');
    if (!container) {
      return;
    }
    container.setAttribute('aria-busy', 'true');
    try {
      var limit = sidebarState.momentFilter === 'shared' ? 20 : 8;
      var url = '/api/moments?person=' + encodeURIComponent(personId) + '&limit=' + limit;
      if (sidebarState.momentFilter === 'story') {
        url += '&kind=story';
      } else if (sidebarState.momentFilter === 'shared') {
        url += '&shared=true';
      }
      var resp = await fetch(url);
      if (!resp.ok) {
        throw new Error(root.dataset.momentsError);
      }
      var data = await resp.json();
      renderTreeMoments(data);
    } catch (err) {
      renderEmptyTreeStream(container, err.message || root.dataset.momentsError);
    }
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

  function setTreeMomentFilter(filterName) {
    sidebarState.momentFilter = filterName || 'all';
    var chips = sidebarContent.querySelectorAll('[data-tree-moment-filter]');
    Array.prototype.forEach.call(chips, function(chip) {
      var active = chip.dataset.treeMomentFilter === sidebarState.momentFilter;
      chip.classList.toggle('tree-sidebar-chip--active', active);
    });
    var personId = getSidebarPersonId();
    if (personId) {
      loadTreeSidebarMoments(personId);
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

  function initializeTreeMomentComposer() {
    var form = document.getElementById('tree-moment-form');
    if (!form) {
      return;
    }
    if (form.dataset.treeComposerBound === 'true') {
      if (typeof form._syncTreeMomentComposer === 'function') {
        form._syncTreeMomentComposer();
      }
      return;
    }
    var kindSelect = form.querySelector('select[name="kind"]');
    var scopeSelect = form.querySelector('select[name="authoring_scope"]');
    var titleInput = form.querySelector('[data-tree-moment-title-input]');
    var bodyLabel = form.querySelector('[data-tree-moment-body-label]');
    var bodyInput = form.querySelector('[data-tree-moment-body-input]');
    var submitButton = form.querySelector('[data-tree-moment-submit]');
    var fileInput = form.querySelector('[data-tree-story-files]');
    var fileSummary = document.getElementById('tree-story-files-summary');
    var fileList = document.getElementById('tree-story-files-list');
    var modeHint = form.querySelector('[data-tree-story-mode-hint]');
    if (!kindSelect || !scopeSelect || !titleInput || !bodyLabel || !bodyInput || !submitButton) {
      return;
    }

    function syncMomentComposer(kind, scope) {
      var isStory = kind === 'story';
      var isShared = scope === 'shared';
      bodyLabel.textContent = isStory ? root.dataset.storyPromptLabel : root.dataset.notePromptLabel;
      bodyInput.placeholder = isStory ? root.dataset.storyPromptLabel : root.dataset.notePromptLabel;
      titleInput.placeholder = isStory ? root.dataset.storyTitlePlaceholder : root.dataset.noteTitlePlaceholder;
      submitButton.textContent = isShared
        ? root.dataset.addEventLabel
        : (isStory ? root.dataset.addStoryLabel : root.dataset.addNoteLabel);
      if (modeHint) {
        modeHint.textContent = isShared
          ? root.dataset.treeStoryFocusSharedHint
          : root.dataset.treeStoryFocusPersonHint;
      }
    }
    form._syncTreeMomentComposer = function() {
      syncMomentComposer(kindSelect.value, scopeSelect.value);
    };

    kindSelect.addEventListener('change', function() {
      syncMomentComposer(kindSelect.value, scopeSelect.value);
    });
    scopeSelect.addEventListener('change', function() {
      syncMomentComposer(kindSelect.value, scopeSelect.value);
    });
    if (fileInput) {
      fileInput.addEventListener('change', function() {
        renderComposerFiles(fileInput, fileSummary, fileList);
      });
      renderComposerFiles(fileInput, fileSummary, fileList);
    }
    form.dataset.treeComposerBound = 'true';
    syncMomentComposer(kindSelect.value, scopeSelect.value);
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
    initializeTreeMomentComposer();
    initializeTreeMediaComposer();
    switchTreeSidebarTab(chooseDefaultSidebarTab(), sidebarState.relationshipGroup || sidebarState.momentFilter);
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

  function relationshipPayload(personId, relatedId, mode) {
    if (mode === 'parent') {
      return {
        endpoint: '/api/relationships/parent-child',
        body: {parent_id: relatedId, child_id: personId, kind: 'biological'}
      };
    }
    if (mode === 'child') {
      return {
        endpoint: '/api/relationships/parent-child',
        body: {parent_id: personId, child_id: relatedId, kind: 'biological'}
      };
    }
    return {
      endpoint: '/api/relationships/partnership',
      body: {person_a_id: personId, person_b_id: relatedId, kind: 'married'}
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

  async function loadTree() {
    setStatus(document.body.dataset.loadingText || 'Loading...');
    var resp = await fetch('/api/tree' + queryString(currentFilters()));
    if (resp.status === 401) {
      window.location.href = '/login';
      return;
    }
    treeData = await resp.json();
    render();
  }

  async function renderSidebar(personId) {
    currentSidebarPersonId = personId;
    sidebarContent.setAttribute('aria-busy', 'true');
    var resp = await fetch('/people/' + personId + '/card');
    var html = await resp.text();
    window.replaceNodeChildrenFromHTML(sidebarContent, html);
    sidebarContent.setAttribute('aria-busy', 'false');
    initializeTreeSidebar(personId);
  }

  async function init() {
    try {
      var loaded = await loadPreferences();
      if (!loaded) {
        return;
      }
      await loadTree();
    } catch (err) {
      document.getElementById('tree-page').textContent = root.dataset.loadError;
    }
  }

  function drawEmptyState(w, h) {
    g.append('text')
      .attr('x', w / 2)
      .attr('y', h / 2)
      .attr('text-anchor', 'middle')
      .attr('fill', '#6b6054')
      .text(root.dataset.emptyText);
    setStatus(root.dataset.statusTemplate.replace('{count}', '0'));
  }

  function buildTreeStructures() {
    var personsById = {};
    treeData.persons.forEach(function(person) {
      personsById[person.id] = person;
    });

    var childToParents = {};
    var parentToChildren = {};
    treeData.parent_child.forEach(function(parentChild) {
      if (!childToParents[parentChild.child_id]) {
        childToParents[parentChild.child_id] = [];
      }
      childToParents[parentChild.child_id].push(parentChild.parent_id);
      if (!parentToChildren[parentChild.parent_id]) {
        parentToChildren[parentChild.parent_id] = [];
      }
      parentToChildren[parentChild.parent_id].push(parentChild.child_id);
    });

    return {
      personsById: personsById,
      childToParents: childToParents,
      parentToChildren: parentToChildren
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

  function layoutTree(rootId, parentToChildren) {
    var visited = new Set();
    var nodePositions = {};

    function buildHierarchy(rootNodeId) {
      var rootNode = {id: rootNodeId, children: [], depth: 0, x: 0, y: 0};
      var queue = [rootNode];
      visited.add(rootNodeId);

      while (queue.length > 0) {
        var node = queue.shift();
        var children = parentToChildren[node.id] || [];
        children.forEach(function(childId) {
          if (visited.has(childId)) {
            return;
          }
          visited.add(childId);
          var childNode = {id: childId, children: [], depth: node.depth + 1, parent: node};
          node.children.push(childNode);
          queue.push(childNode);
        });
      }

      return rootNode;
    }

    function applyLayout(node, xStart, y, maxDepth) {
      node.y = y;
      if (node.depth > maxDepth.value) {
        maxDepth.value = node.depth;
      }

      if (node.children.length === 0) {
        node.x = xStart + NODE_SPACING_X / 2;
        return xStart + NODE_SPACING_X;
      }

      var nextX = xStart;
      node.children.forEach(function(child) {
        nextX = applyLayout(child, nextX, y + NODE_SPACING_Y, maxDepth);
      });

      var first = node.children[0];
      var last = node.children[node.children.length - 1];
      node.x = (first.x + last.x) / 2;
      return nextX;
    }

    var rootNode = buildHierarchy(rootId);
    var maxDepth = {value: 0};
    applyLayout(rootNode, 0, 60, maxDepth);

    var allNodes = [];
    function collectNodes(node) {
      allNodes.push(node);
      nodePositions[node.id] = {x: node.x, y: node.y};
      node.children.forEach(collectNodes);
    }
    collectNodes(rootNode);

    var unvisited = treeData.persons.filter(function(person) {
      return !visited.has(person.id);
    });
    var ux = 0;
    unvisited.forEach(function(person) {
      var detachedNode = {
        id: person.id,
        children: [],
        depth: maxDepth.value + 1,
        x: ux,
        y: (maxDepth.value + 1) * NODE_SPACING_Y + 60
      };
      allNodes.push(detachedNode);
      nodePositions[person.id] = {x: detachedNode.x, y: detachedNode.y};
      ux += NODE_SPACING_X;
    });

    return {allNodes: allNodes, nodePositions: nodePositions};
  }

  function addMetricPill(nodeGroup, person, baseY) {
    var metrics = [];
    if (person.moment_count) metrics.push('M ' + person.moment_count);
    if (person.story_count) metrics.push('S ' + person.story_count);
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

  function renderNode(node, person) {
    var nodeGroup = g.append('g')
      .attr('class', 'person-node' + (person.branch ? ' person-node--branch-' + person.branch : ''))
      .attr('data-id', person.id)
      .attr('transform', 'translate(' + node.x + ',' + node.y + ')')
      .attr('tabindex', '0')
      .attr('role', 'button')
      .attr('aria-label', 'Open details for ' + person.display_name)
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
          .text(person.display_name.substring(0, 2));
      }
    }

    nodeGroup.append('circle')
      .attr('class', 'tap-target')
      .attr('r', NODE_RADIUS + 10);

    var nextTextY = NODE_RADIUS + 16;
    if (preferences.show_names) {
      nodeGroup.append('text')
        .attr('class', 'name-label')
        .attr('dy', nextTextY)
        .text(person.display_name);
      nextTextY += 15;
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
      openPersonSidebar(person.id, this);
    });

    nodeGroup.on('dblclick', function() {
      window.location.href = '/people/' + person.id;
    });

    nodeGroup.on('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
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
    var layout = layoutTree(rootId, structures.parentToChildren);

    var lineGen = d3.line().curve(d3.curveBumpY);
    layout.allNodes.forEach(function(node) {
      if (node.children) {
        node.children.forEach(function(child) {
          g.append('path')
            .attr('class', 'parent-child-line')
            .attr('d', lineGen([[node.x, node.y + NODE_RADIUS], [child.x, child.y - NODE_RADIUS]]));
        });
      }
    });

    treeData.partnerships.forEach(function(partnership) {
      var posA = layout.nodePositions[partnership.person_a_id];
      var posB = layout.nodePositions[partnership.person_b_id];
      if (!posA || !posB) {
        return;
      }
      var dissolved = partnership.status === 'dissolved' || partnership.status === 'separated';
      g.append('line')
        .attr('class', 'partnership-line' + (dissolved ? ' partnership-line--dissolved' : ''))
        .attr('x1', posA.x)
        .attr('y1', posA.y)
        .attr('x2', posB.x)
        .attr('y2', posB.y);
    });

    layout.allNodes.forEach(function(node) {
      var person = structures.personsById[node.id];
      if (person) {
        renderNode(node, person);
      }
    });

    var bounds = g.node().getBBox();
    var dx = w / 2 - (bounds.x + bounds.width / 2);
    var dy = h / 2 - (bounds.y + bounds.height / 2);
    var scale = Math.min(w / (bounds.width + 100), h / (bounds.height + 100), 1);
    svg.call(zoom.transform, d3.zoomIdentity.translate(dx, dy).scale(scale));

    setStatus(root.dataset.statusTemplate.replace('{count}', String(treeData.persons.length)));
  }

  async function openPersonSidebar(personId, triggerNode) {
    if (currentSidebarPersonId && currentSidebarPersonId !== personId) {
      sidebarState.activeTab = '';
      sidebarState.relationshipGroup = '';
      sidebarState.momentFilter = 'all';
      sidebarState.highlightMomentId = '';
      sidebarState.highlightMediaId = '';
    }
    sidebarTrigger = triggerNode || document.activeElement;
    sidebar.classList.add('person-sidebar--open');
    window.openAccessibleOverlay(sidebar, {initialFocus: '.person-sidebar__close'});
    await renderSidebar(personId);
  }

  function switchTreeSidebarTab(tabName, context) {
    sidebarState.activeTab = tabName || 'overview';
    if (tabName === 'moments') {
      if (context === 'story' || context === 'all') {
        sidebarState.momentFilter = context;
      } else if (!context) {
        sidebarState.momentFilter = 'all';
      }
    }
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
    if (sidebarState.activeTab === 'moments') {
      setTreeMomentFilter(sidebarState.momentFilter || 'all');
    }
    if (sidebarState.activeTab === 'media') {
      var personId = getSidebarPersonId();
      if (personId) {
        loadTreeSidebarMedia(personId);
      }
    }
  }

  function countryFlag(code) {
    if (!code || code.length !== 2) {
      return '';
    }
    var offset = 127397;
    return String.fromCodePoint(code.charCodeAt(0) + offset, code.charCodeAt(1) + offset);
  }

  async function refreshTreeWorkspace(personId) {
    await loadTree();
    if (personId) {
      await renderSidebar(personId);
    }
  }

  function toggleTreeMomentFields(kind, scope) {
    if (scope === 'shared') {
      sidebarState.momentFilter = 'shared';
    } else {
      sidebarState.momentFilter = kind === 'story' ? 'story' : 'all';
    }
    var form = document.getElementById('tree-moment-form');
    if (form && typeof form._syncTreeMomentComposer === 'function') {
      form._syncTreeMomentComposer();
    }
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

  async function submitTreeMoment(event, personId) {
    event.preventDefault();
    setError('tree-moment-error', '');
    var form = event.target;
    var button = form.querySelector('button[type="submit"]');
    var originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = root.dataset.savingLabel;
    var uploadedFiles = [];

    try {
      var payload = formDataToJson(form);
      var authoringScope = payload.authoring_scope || 'person';
      delete payload.authoring_scope;
      payload.person_id = personId;
      payload.occurred_at = normalizeOccurredAt(payload.occurred_at);
      var taggedPersonIds = parseJsonArray(payload.tagged_person_ids);
      payload.tagged_person_ids = taggedPersonIds;
      if (authoringScope === 'shared' && !taggedPersonIds.length) {
        throw new Error(root.dataset.treeSharedEventRequiresPeople);
      }
      var fileInput = form.querySelector('[data-tree-story-files]');
      if (fileInput && fileInput.files && fileInput.files.length) {
        uploadedFiles = await uploadTreeFiles(fileInput.files, personId, {
          caption: payload.title || '',
          taggedPersonIds: taggedPersonIds
        });
        payload.media_ids = uploadedFiles.map(function(item) { return item.id; });
      }
      var resp = await fetch('/api/moments', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      var data = await resp.json().catch(function() { return {}; });
      if (!resp.ok) {
        throw new Error(data.detail || root.dataset.updateError);
      }
      form.reset();
      sidebarState.activeTab = 'moments';
      sidebarState.momentFilter = authoringScope === 'shared'
        ? 'shared'
        : (payload.kind === 'story' ? 'story' : 'all');
      sidebarState.highlightMomentId = data.id || '';
      await refreshTreeWorkspace(personId);
      showToastMessage(
        authoringScope === 'shared'
          ? root.dataset.treeEventCreated
          : (payload.kind === 'story' ? root.dataset.treeStoryCreated : root.dataset.treeNoteCreated)
      );
    } catch (err) {
      await cleanupUploadedTreeMedia(uploadedFiles);
      setError('tree-moment-error', err.message || root.dataset.updateError);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
    return false;
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
      uploads = await uploadTreeFiles(fileInput.files, personId, {
        caption: captionInput && captionInput.value.trim() ? captionInput.value.trim() : ''
      });
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
      var resp = await fetch('/api/persons/' + personId, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formDataToJson(form, {
          nullableFields: [
            'nickname',
            'birth_date_raw',
            'birth_place',
            'residence_place',
            'residence_country_code',
            'branch',
            'bio'
          ]
        }))
      });
      var data = await resp.json().catch(function() { return {}; });
      if (!resp.ok) {
        throw new Error(data.detail || root.dataset.updateError);
      }
      sidebarState.activeTab = 'details';
      await refreshTreeWorkspace(personId);
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
      var request = relationshipPayload(personId, relatedId, mode);
      var resp = await fetch(request.endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(request.body)
      });
      var data = await resp.json().catch(function() { return {}; });
      if (!resp.ok) {
        throw new Error(data.detail || root.dataset.relationshipError);
      }
      form.reset();
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = mode;
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
        body: JSON.stringify(formDataToJson(form))
      });
      var created = await createResp.json().catch(function() { return {}; });
      if (!createResp.ok) {
        throw new Error(created.detail || root.dataset.updateError);
      }

      var request = relationshipPayload(personId, created.id, mode);
      var linkResp = await fetch(request.endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(request.body)
      });
      var linkData = await linkResp.json().catch(function() { return {}; });
      if (!linkResp.ok) {
        throw new Error(linkData.detail || root.dataset.relationshipError);
      }

      form.reset();
      sidebarState.activeTab = 'overview';
      sidebarState.relationshipGroup = '';
      await loadTree();
      await openPersonSidebar(created.id, sidebarTrigger);
      showToastMessage(root.dataset.createdMessage);
    } catch (err) {
      setError('tree-relationship-error', err.message || root.dataset.relationshipError);
    } finally {
      button.disabled = false;
      button.textContent = originalLabel;
    }
    return false;
  }

  async function removeTreeRelationship(relId, relationshipType, personId, groupName) {
    setError('tree-relationship-error', '');
    try {
      var endpoint = relationshipType === 'partnership'
        ? '/api/relationships/partnership/' + relId
        : '/api/relationships/parent-child/' + relId;
      var resp = await fetch(endpoint, {method: 'DELETE'});
      if (!resp.ok) {
        var data = await resp.json().catch(function() { return {}; });
        throw new Error(data.detail || root.dataset.relationshipError);
      }
      sidebarState.activeTab = 'relationships';
      sidebarState.relationshipGroup = groupName || '';
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

  window.treeReset = function() {
    if (treeData) {
      render();
    }
  };

  window.closeSidebar = function() {
    sidebar.classList.remove('person-sidebar--open');
    currentSidebarPersonId = null;
    window.closeAccessibleOverlay(sidebar);
    if (sidebarTrigger && typeof sidebarTrigger.focus === 'function') {
      sidebarTrigger.focus();
    }
  };

  window.saveTreePerson = saveTreePerson;
  window.linkTreeRelationship = linkTreeRelationship;
  window.createTreeRelative = createTreeRelative;
  window.removeTreeRelationship = removeTreeRelationship;
  window.openTreeSidebarPerson = openTreeSidebarPerson;
  window.switchTreeSidebarTab = switchTreeSidebarTab;
  window.setTreeMomentFilter = setTreeMomentFilter;
  window.submitTreeMoment = submitTreeMoment;
  window.uploadTreeMedia = uploadTreeMedia;
  window.toggleTreeMomentFields = toggleTreeMomentFields;

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
