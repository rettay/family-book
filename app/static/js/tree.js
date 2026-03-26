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
    highlightMediaId: '',
    highlightRelatedPersonId: '',
    graphMode: null
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

  function updateGraphModeBanner() {
    var banner = document.getElementById('tree-graph-mode-banner');
    if (!banner) {
      return;
    }
    var titleNode = document.getElementById('tree-graph-mode-title');
    var descriptionNode = document.getElementById('tree-graph-mode-description');
    if (!sidebarState.graphMode) {
      banner.classList.add('hidden');
      if (titleNode) titleNode.textContent = '';
      if (descriptionNode) descriptionNode.textContent = '';
      return;
    }
    var summary = graphModeSummary(sidebarState.graphMode);
    banner.classList.remove('hidden');
    if (titleNode) titleNode.textContent = summary.title;
    if (descriptionNode) descriptionNode.textContent = summary.description;
    setStatus(summary.description);
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
    var isGraphSource = !!(sidebarState.graphMode && sidebarState.graphMode.sourcePersonId === person.id);
    var isGraphCandidate = !!(sidebarState.graphMode && sidebarState.graphMode.sourcePersonId !== person.id);
    var nodeGroup = g.append('g')
      .attr('class', 'tree-node person-node' +
        (person.branch ? ' person-node--branch-' + person.branch : '') +
        (isGraphSource ? ' person-node--graph-source' : '') +
        (isGraphCandidate ? ' person-node--graph-candidate' : ''))
      .attr('data-id', person.id)
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
      window.location.href = '/people/' + person.id;
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

    // Build parent-child kind lookup: "parentId|childId" → kind
    var pcKindLookup = {};
    treeData.parent_child.forEach(function(pc) {
      pcKindLookup[pc.parent_id + '|' + pc.child_id] = pc.kind || 'biological';
    });

    var lineGen = d3.line().curve(d3.curveBumpY);
    layout.allNodes.forEach(function(node) {
      if (node.children) {
        node.children.forEach(function(child) {
          var kind = pcKindLookup[node.id + '|' + child.id] || 'biological';
          g.append('path')
            .attr('class', 'parent-child-line parent-child-line--' + kind)
            .attr('data-from', node.id)
            .attr('data-to', child.id)
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
      var pKind = partnership.kind || 'married';
      g.append('line')
        .attr('class', 'partnership-line partnership-line--' + pKind + (dissolved ? ' partnership-line--dissolved' : ''))
        .attr('data-from', partnership.person_a_id)
        .attr('data-to', partnership.person_b_id)
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
    updateGraphModeBanner();
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
      // Collect JSON array fields (education, career, organizations, admixture, medical_conditions)
      payload.education = collectJsonArrayEntries('education');
      payload.career = collectJsonArrayEntries('career');
      payload.organizations = collectJsonArrayEntries('organizations');
      payload.admixture = collectJsonArrayEntries('admixture');
      payload.medical_conditions = collectJsonArrayEntries('medical_conditions');
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
      await executeRelationshipRequest(relationshipPayload(personId, relatedId, mode));
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
        body: JSON.stringify(formDataToJson(form))
      });
      var created = await createResp.json().catch(function() { return {}; });
      if (!createResp.ok) {
        throw new Error(created.detail || root.dataset.updateError);
      }

      await executeRelationshipRequest(relationshipPayload(personId, created.id, mode));

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
    zoomToNode(personId);
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

  function zoomToNode(personId) {
    if (!svg || !zoom || !treeData) return;

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
    var scale = 1.2;
    var tx = w / 2 - nx * scale;
    var ty = h / 2 - ny * scale;

    svg.transition()
      .duration(600)
      .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));

    // Flash highlight
    var circle = nodeEl.select('.photo-clip');
    if (!circle.empty()) {
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

  window.treeReset = function() {
    if (treeData) {
      render();
    }
  };

  window.closeSidebar = function() {
    sidebar.classList.remove('person-sidebar--open');
    currentSidebarPersonId = null;
    sidebarState.graphMode = null;
    sidebarState.highlightRelatedPersonId = '';
    window.closeAccessibleOverlay(sidebar);
    var expandTab = document.getElementById('sidebar-expand-tab');
    if (expandTab) expandTab.hidden = true;
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

          list.appendChild(item);
        });
        section.appendChild(list);
      }

      container.appendChild(section);
    });
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
  window.setTreeMomentFilter = setTreeMomentFilter;
  window.submitTreeMoment = submitTreeMoment;
  window.uploadTreeMedia = uploadTreeMedia;
  window.toggleTreeMomentFields = toggleTreeMomentFields;
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
    _relCalcMode = true;
    _relCalcFirst = null;
    var banner = document.getElementById('tree-relcalc-banner');
    if (banner) {
      banner.textContent = 'Select the first person on the tree.';
      banner.hidden = false;
    }
  }

  function cancelRelationshipCalc() {
    _relCalcMode = false;
    _relCalcFirst = null;
    var banner = document.getElementById('tree-relcalc-banner');
    if (banner) banner.hidden = true;
    _clearPathHighlight();
    var resultPanel = document.getElementById('tree-relcalc-result');
    if (resultPanel) resultPanel.hidden = true;
  }

  function _handleRelCalcClick(personId) {
    if (!_relCalcFirst) {
      _relCalcFirst = personId;
      var banner = document.getElementById('tree-relcalc-banner');
      if (banner) banner.textContent = 'Now select the second person.';
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
    if (banner) banner.textContent = 'Computing relationship...';
    try {
      var resp = await fetch('/api/relationships/path?from=' + encodeURIComponent(fromId) + '&to=' + encodeURIComponent(toId));
      if (!resp.ok) throw new Error('API error');
      var data = await resp.json();
      _showRelationshipResult(data);
      if (data.found && data.path.length > 0) {
        _highlightPath(data.path);
      }
    } catch (err) {
      if (banner) banner.textContent = 'Could not compute relationship.';
    }
    _relCalcMode = false;
    _relCalcFirst = null;
    if (banner) banner.hidden = true;
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
