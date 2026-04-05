/* Family Book — main.js */

var overlayStack = [];

function getFocusableElements(container) {
  if (!container) return [];
  return Array.prototype.slice.call(
    container.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  ).filter(function(el) {
    return !el.hidden && !el.closest('[hidden]') && el.getClientRects().length > 0;
  });
}

function rememberOverlayState(overlay) {
  if (!overlay.__fbOverlayState) {
    overlay.__fbOverlayState = {};
  }
  return overlay.__fbOverlayState;
}

function replaceNodeChildrenFromHTML(target, html) {
  if (!target) return;
  var parser = new DOMParser();
  var doc = parser.parseFromString(html, 'text/html');
  var nodes = Array.prototype.slice.call(doc.body.childNodes).map(function(node) {
    return document.importNode(node, true);
  });
  target.replaceChildren.apply(target, nodes);
}

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function openAccessibleOverlay(overlay, options) {
  if (!overlay) return;
  var opts = options || {};
  var state = rememberOverlayState(overlay);
  state.returnFocusTo = opts.returnFocus || document.activeElement;
  state.options = opts;
  overlay.hidden = false;
  overlay.classList.remove('hidden');
  overlay.setAttribute('aria-hidden', 'false');
  overlayStack = overlayStack.filter(function(item) { return item !== overlay; });
  overlayStack.push(overlay);
  document.body.classList.add('has-overlay');

  var focusTarget = null;
  if (opts.initialFocus) {
    focusTarget = overlay.querySelector(opts.initialFocus);
  }
  if (!focusTarget) {
    focusTarget = getFocusableElements(overlay)[0] || overlay;
  }
  if (focusTarget && typeof focusTarget.focus === 'function') {
    focusTarget.focus();
    window.setTimeout(function() {
      focusTarget.focus();
    }, 0);
  }
}

function closeAccessibleOverlay(overlay) {
  if (!overlay) return;
  var state = rememberOverlayState(overlay);
  overlay.classList.add('hidden');
  overlay.hidden = true;
  overlay.setAttribute('aria-hidden', 'true');
  overlayStack = overlayStack.filter(function(item) { return item !== overlay; });
  if (overlayStack.length === 0) {
    document.body.classList.remove('has-overlay');
  }
  if (state.returnFocusTo && typeof state.returnFocusTo.focus === 'function') {
    state.returnFocusTo.focus();
  }
}

window.openAccessibleOverlay = openAccessibleOverlay;
window.closeAccessibleOverlay = closeAccessibleOverlay;
window.replaceNodeChildrenFromHTML = replaceNodeChildrenFromHTML;

document.addEventListener('keydown', function(e) {
  var activeOverlay = overlayStack[overlayStack.length - 1];
  if (activeOverlay) {
    if (e.key === 'Escape') {
      e.preventDefault();
      if (activeOverlay.id === 'compose-modal' && typeof window.closeComposeModal === 'function') {
        window.closeComposeModal();
        return;
      }
      if (activeOverlay.id === 'person-sidebar' && typeof window.closeSidebar === 'function') {
        window.closeSidebar();
        return;
      }
      closeAccessibleOverlay(activeOverlay);
      return;
    }
    if (e.key === 'Tab') {
      var focusable = getFocusableElements(activeOverlay);
      if (focusable.length === 0) {
        e.preventDefault();
        activeOverlay.focus();
        return;
      }
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
      return;
    }
  }

  if (e.key === 'Escape') {
    toggleNav(false);
  }
});

// Nav toggle (mobile)
function toggleNav(forceOpen) {
  var links = document.getElementById('nav-links');
  var button = document.querySelector('.nav__hamburger');
  if (!links) return;
  var mobileMode = window.innerWidth <= 640;
  var shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !links.classList.contains('nav__links--open');
  if (mobileMode) {
    links.classList.toggle('nav__links--open', shouldOpen);
    links.setAttribute('aria-hidden', shouldOpen ? 'false' : 'true');
  } else {
    links.classList.remove('nav__links--open');
    links.removeAttribute('aria-hidden');
  }
  if (button) {
    button.setAttribute('aria-expanded', mobileMode && shouldOpen ? 'true' : 'false');
  }
}
// Close nav on link click (mobile)
document.addEventListener('click', function(e) {
  var links = document.getElementById('nav-links');
  if (links && !e.target.closest('.nav__hamburger') && !e.target.closest('#nav-links')) {
    toggleNav(false);
  }
});

// Logout
async function logout() {
  await fetch('/auth/logout', {method: 'POST'});
  if ('caches' in window) {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((key) => caches.delete(key)));
    } catch (err) {}
  }
  if (window.google && google.accounts && google.accounts.id) {
    google.accounts.id.disableAutoSelect();
  }
  window.location.href = '/login';
}

// Toast
function showToast(msg) {
  var container = document.getElementById('toast-container');
  if (!container) return;
  var toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'status');
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(function() { toast.remove(); }, 3000);
}

// Check URL for toast param
(function() {
  var params = new URLSearchParams(window.location.search);
  if (params.get('toast')) {
    showToast(params.get('toast'));
    params.delete('toast');
    var newUrl = window.location.pathname;
    if (params.toString()) newUrl += '?' + params.toString();
    history.replaceState(null, '', newUrl);
  }
})();

// Lightbox — supports image, video, and audio
function _guessMediaType(url) {
  if (!url) return 'image';
  var lower = url.toLowerCase();
  if (lower.match(/\.(mp4|webm|mov|quicktime)(\?|$)/)) return 'video';
  if (lower.match(/\.(mp3|m4a|ogg|opus|wav)(\?|$)/)) return 'audio';
  if (lower.match(/\.pdf(\?|$)/)) return 'document';
  return 'image';
}

function openLightbox(url, altText, mediaType) {
  if (!mediaType) mediaType = _guessMediaType(url);
  if (mediaType === 'document') {
    window.open(url, '_blank');
    return;
  }
  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.hidden = true;
  lb.setAttribute('aria-hidden', 'true');
  lb.onclick = function(e) {
    if (e.target === lb) {
      _closeLightbox(lb);
    }
  };
  var closeBtn = document.createElement('button');
  closeBtn.className = 'lightbox__close';
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Close media viewer');
  closeBtn.textContent = '\u00D7';
  closeBtn.onclick = function(e) {
    e.stopPropagation();
    _closeLightbox(lb);
  };
  var dialog = document.createElement('div');
  dialog.className = 'lightbox__dialog';
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-label', altText || 'Expanded media');
  dialog.tabIndex = -1;
  dialog.appendChild(closeBtn);

  if (mediaType === 'video') {
    var video = document.createElement('video');
    video.controls = true;
    video.autoplay = true;
    video.src = url;
    video.style.maxWidth = '90vw';
    video.style.maxHeight = '80vh';
    dialog.appendChild(video);
  } else if (mediaType === 'audio') {
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.autoplay = true;
    audio.src = url;
    audio.style.width = '400px';
    audio.style.maxWidth = '90vw';
    dialog.appendChild(audio);
  } else {
    var img = document.createElement('img');
    img.src = url;
    img.alt = altText || 'Expanded media';
    dialog.appendChild(img);
  }

  lb.appendChild(dialog);
  document.body.appendChild(lb);
  openAccessibleOverlay(lb, {initialFocus: '.lightbox__close'});
}

function _closeLightbox(lb) {
  // Pause any playing media before removing
  var video = lb.querySelector('video');
  var audio = lb.querySelector('audio');
  if (video) video.pause();
  if (audio) audio.pause();
  closeAccessibleOverlay(lb);
  lb.remove();
}

// Media upload (person profile page)
var ALLOWED_UPLOAD_TYPES = [
  'image/jpeg', 'image/png', 'image/webp', 'image/gif',
  'video/mp4', 'video/quicktime', 'video/webm',
  'audio/opus', 'audio/mp3', 'audio/m4a', 'audio/ogg', 'audio/mpeg',
  'application/pdf'
];

function familyBookLabel(key, fallback) {
  var labels = window.familyBookLabels || {};
  return labels[key] || fallback;
}

function _resolveMediaUploadContext(source) {
  var origin = source && source.closest ? source.closest('form') : document.getElementById('media-upload-form');
  var fileInput = origin ? origin.querySelector('#media-upload-file, input[type="file"]') : document.getElementById('media-upload-file');
  var personField = origin ? origin.querySelector('input[name="person_id"]') : null;
  var personId = origin && origin.dataset ? origin.dataset.personId : '';
  if (!personId && personField) {
    personId = personField.value;
  }
  if (!personId) {
    var personMatch = window.location.pathname.match(/\/people\/([^/]+)/);
    personId = personMatch ? personMatch[1] : '';
  }
  return {
    form: origin,
    fileInput: fileInput,
    personId: personId
  };
}

function _getMediaUploadState() {
  if (!window.__familyBookMediaUploadState) {
    window.__familyBookMediaUploadState = {
      options: null,
      shared: {title: '', description: '', takenAt: '', taggedPeople: []},
      items: [],
      uploading: false,
      activeXhr: null,
      suggestionTimer: null,
      suggestions: [],
      searchQuery: ''
    };
  }
  return window.__familyBookMediaUploadState;
}

function _ensureMediaUploadModal() {
  var modal = document.getElementById('media-upload-modal');
  if (modal) {
    return modal;
  }
  modal = document.createElement('div');
  modal.id = 'media-upload-modal';
  modal.className = 'media-upload-modal hidden';
  modal.hidden = true;
  modal.setAttribute('aria-hidden', 'true');
  modal.innerHTML = '<div class="media-upload-modal__panel" role="dialog" aria-modal="true" aria-labelledby="media-upload-modal-title">' +
    '<div class="media-upload-modal__header">' +
      '<div>' +
        '<h2 id="media-upload-modal-title" class="media-upload-modal__title"></h2>' +
        '<p class="media-upload-modal__subtitle"></p>' +
      '</div>' +
      '<button type="button" class="media-upload-modal__close" data-media-upload-close aria-label="' + familyBookLabel('upload.close', 'Close') + '">&times;</button>' +
    '</div>' +
    '<div class="media-upload-modal__body"></div>' +
    '<div class="media-upload-modal__footer">' +
      '<button type="button" class="btn btn--ghost" data-media-upload-cancel></button>' +
      '<button type="button" class="btn btn--primary" data-media-upload-submit></button>' +
    '</div>' +
  '</div>';
  document.body.appendChild(modal);
  return modal;
}

function _mediaPreviewMarkup(item) {
  if (item.previewUrl && item.file.type.indexOf('image/') === 0) {
    return '<img src="' + item.previewUrl + '" alt="' + item.file.name.replace(/"/g, '&quot;') + '">';
  }
  if (item.file.type.indexOf('video/') === 0) {
    return '<span class="media-upload-item__icon" aria-hidden="true">&#127909;</span>';
  }
  if (item.file.type.indexOf('audio/') === 0) {
    return '<span class="media-upload-item__icon" aria-hidden="true">&#9835;</span>';
  }
  return '<span class="media-upload-item__icon" aria-hidden="true">&#128196;</span>';
}

function _renderMediaUploadModal() {
  var state = _getMediaUploadState();
  var modal = _ensureMediaUploadModal();
  var titleNode = modal.querySelector('.media-upload-modal__title');
  var subtitleNode = modal.querySelector('.media-upload-modal__subtitle');
  var body = modal.querySelector('.media-upload-modal__body');
  var cancelBtn = modal.querySelector('[data-media-upload-cancel]');
  var submitBtn = modal.querySelector('[data-media-upload-submit]');

  titleNode.textContent = state.options && state.options.title ? state.options.title : familyBookLabel('upload.title', 'Review upload');
  subtitleNode.textContent = familyBookLabel('upload.subtitle', 'Add shared details now, then upload with progress for each file.');
  cancelBtn.textContent = state.uploading ? familyBookLabel('upload.cancel_upload', 'Cancel upload') : familyBookLabel('common.cancel', 'Cancel');
  submitBtn.textContent = state.uploading ? familyBookLabel('upload.uploading', 'Uploading...') : familyBookLabel('upload.submit', 'Start upload');
  submitBtn.disabled = state.uploading;

  var chipMarkup = state.shared.taggedPeople.map(function(person, index) {
    return '<button type="button" class="media-upload-chip" data-chip-index="' + index + '">' +
      '<span>' + escapeHtml(person.display_name || '') + '</span>' +
      '<span aria-hidden="true">&times;</span>' +
    '</button>';
  }).join('');

  var suggestionMarkup = state.suggestions.map(function(person) {
    return '<button type="button" class="media-upload-suggestion" data-person-id="' + person.id + '">' +
      escapeHtml(person.display_name || '') +
    '</button>';
  }).join('');

  body.innerHTML =
    '<section class="media-upload-shared">' +
      '<h3>' + familyBookLabel('upload.shared_metadata', 'Shared metadata') + '</h3>' +
      '<div class="media-upload-grid">' +
        '<label><span>' + familyBookLabel('upload.shared_title', 'Shared title') + '</span><input class="form-input" type="text" data-shared-field="title" value="' + escapeHtml(state.shared.title) + '" maxlength="300"></label>' +
        '<label><span>' + familyBookLabel('upload.taken_at', 'Date taken') + '</span><input class="form-input" type="date" data-shared-field="takenAt" value="' + escapeHtml(state.shared.takenAt) + '"></label>' +
      '</div>' +
      '<label><span>' + familyBookLabel('upload.shared_description', 'Shared description') + '</span><textarea class="form-input" rows="3" data-shared-field="description">' + escapeHtml(state.shared.description) + '</textarea></label>' +
      '<label><span>' + familyBookLabel('upload.tag_people', 'Tag family members') + '</span><input class="form-input" type="search" data-tag-search placeholder="' + familyBookLabel('upload.tag_search_placeholder', 'Search family members') + '" value="' + escapeHtml(state.searchQuery) + '"></label>' +
      '<div class="media-upload-chip-list">' + chipMarkup + '</div>' +
      '<div class="media-upload-suggestions">' + suggestionMarkup + '</div>' +
    '</section>' +
    '<section class="media-upload-items">' +
      state.items.map(function(item, index) {
        var isImage = item.file.type.indexOf('image/') === 0;
        var editBtn = isImage
          ? '<button type="button" class="btn btn--ghost btn--sm media-upload-item__edit-btn" data-upload-edit-index="' + index + '">' +
              familyBookLabel('media.edit_before_upload', 'Edit before upload') +
            '</button>'
          : '';
        return '<article class="media-upload-item" data-upload-item-index="' + index + '">' +
          '<div class="media-upload-item__preview">' + _mediaPreviewMarkup(item) + editBtn + '</div>' +
          '<div class="media-upload-item__content">' +
            '<div class="media-upload-item__header">' +
              '<strong>' + escapeHtml(item.file.name) + '</strong>' +
              '<span>' + Math.max(1, Math.round(item.file.size / 1024)) + ' KB</span>' +
            '</div>' +
            '<div class="media-upload-grid">' +
              '<label><span>' + familyBookLabel('upload.file_title', 'Title') + '</span><input class="form-input" type="text" data-item-field="title" data-item-index="' + index + '" value="' + escapeHtml(item.title) + '" maxlength="300"></label>' +
              '<label><span>' + familyBookLabel('upload.taken_at', 'Date taken') + '</span><input class="form-input" type="date" data-item-field="takenAt" data-item-index="' + index + '" value="' + escapeHtml(item.takenAt) + '"></label>' +
            '</div>' +
            '<label><span>' + familyBookLabel('upload.file_description', 'Description') + '</span><textarea class="form-input" rows="3" data-item-field="description" data-item-index="' + index + '">' + escapeHtml(item.description) + '</textarea></label>' +
            '<div class="media-upload-progress" data-progress-wrap="' + index + '"' + (item.progressVisible ? '' : ' hidden') + '>' +
              '<div class="media-upload-progress__bar"><div class="media-upload-progress__fill" style="width:' + item.progress + '%"></div></div>' +
              '<div class="media-upload-progress__label">' + escapeHtml(item.progressLabel || familyBookLabel('upload.waiting', 'Waiting to upload')) + '</div>' +
            '</div>' +
          '</div>' +
        '</article>';
      }).join('') +
    '</section>';

  Array.prototype.forEach.call(body.querySelectorAll('[data-upload-edit-index]'), function(button) {
    button.addEventListener('click', function() {
      var itemIndex = Number(button.getAttribute('data-upload-edit-index'));
      var item = state.items[itemIndex];
      if (!item || !item.previewUrl) return;
      if (typeof window.openUploadPhotoCrop === 'function') {
        window.openUploadPhotoCrop(itemIndex, item.previewUrl, item.file.type);
      }
    });
  });
  Array.prototype.forEach.call(body.querySelectorAll('[data-shared-field]'), function(input) {
    input.addEventListener('input', function() {
      state.shared[input.getAttribute('data-shared-field')] = input.value;
    });
  });
  Array.prototype.forEach.call(body.querySelectorAll('[data-item-field]'), function(input) {
    input.addEventListener('input', function() {
      var itemIndex = Number(input.getAttribute('data-item-index'));
      var field = input.getAttribute('data-item-field');
      if (!state.items[itemIndex]) {
        return;
      }
      state.items[itemIndex][field] = input.value;
    });
  });
  Array.prototype.forEach.call(body.querySelectorAll('[data-chip-index]'), function(button) {
    button.addEventListener('click', function() {
      state.shared.taggedPeople.splice(Number(button.getAttribute('data-chip-index')), 1);
      _renderMediaUploadModal();
    });
  });
  Array.prototype.forEach.call(body.querySelectorAll('.media-upload-suggestion'), function(button) {
    button.addEventListener('click', function() {
      var personId = button.getAttribute('data-person-id');
      var person = state.suggestions.find(function(entry) { return entry.id === personId; });
      if (!person) {
        return;
      }
      if (!state.shared.taggedPeople.some(function(entry) { return entry.id === person.id; })) {
        state.shared.taggedPeople.push(person);
      }
      state.suggestions = [];
      state.searchQuery = '';
      _renderMediaUploadModal();
    });
  });
  var searchInput = body.querySelector('[data-tag-search]');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      state.searchQuery = searchInput.value;
      window.clearTimeout(state.suggestionTimer);
      state.suggestionTimer = window.setTimeout(function() {
        _loadMediaUploadSuggestions();
      }, 250);
    });
  }

  modal.querySelector('[data-media-upload-close]').onclick = function() { _cancelMediaUploadWorkflow(); };
  cancelBtn.onclick = function() { _cancelMediaUploadWorkflow(); };
  submitBtn.onclick = function() { _submitMediaUploadWorkflow(); };
}

async function _loadMediaUploadSuggestions() {
  var state = _getMediaUploadState();
  if (!state.searchQuery || state.searchQuery.trim().length < 2) {
    state.suggestions = [];
    _renderMediaUploadModal();
    return;
  }
  try {
    var resp = await fetch('/api/persons?search=' + encodeURIComponent(state.searchQuery.trim()));
    if (!resp.ok) {
      throw new Error('suggestions failed');
    }
    var people = await resp.json();
    state.suggestions = people.filter(function(person) {
      return !state.shared.taggedPeople.some(function(tagged) { return tagged.id === person.id; });
    }).slice(0, 6);
  } catch (err) {
    state.suggestions = [];
  }
  _renderMediaUploadModal();
}

function _resetMediaUploadState() {
  var state = _getMediaUploadState();
  if (state.activeXhr) {
    state.activeXhr.abort();
  }
  state.items.forEach(function(item) {
    if (item.previewUrl && item.previewUrl.indexOf('blob:') === 0) {
      URL.revokeObjectURL(item.previewUrl);
    }
  });
  window.__familyBookMediaUploadState = {
    options: null,
    shared: {title: '', description: '', takenAt: '', taggedPeople: []},
    items: [],
    uploading: false,
    activeXhr: null,
    suggestionTimer: null,
    suggestions: [],
    searchQuery: ''
  };
}

function _cancelMediaUploadWorkflow() {
  var modal = _ensureMediaUploadModal();
  _resetMediaUploadState();
  closeAccessibleOverlay(modal);
}

function startMediaUploadWorkflow(options) {
  var opts = options || {};
  var files = (opts.files || []).slice();
  if (!files.length) {
    showToast(familyBookLabel('upload.select_file', 'Select a file'));
    return false;
  }
  for (var index = 0; index < files.length; index += 1) {
    if (files[index].type && ALLOWED_UPLOAD_TYPES.indexOf(files[index].type) === -1) {
      showToast(familyBookLabel('upload.unsupported_file', 'Unsupported file type') + ': ' + files[index].name);
      return false;
    }
  }

  var state = _getMediaUploadState();
  state.options = opts;
  state.items = files.map(function(file) {
    return {
      file: file,
      previewUrl: file.type.indexOf('image/') === 0 ? URL.createObjectURL(file) : '',
      title: '',
      description: '',
      takenAt: '',
      progress: 0,
      progressLabel: familyBookLabel('upload.waiting', 'Waiting to upload'),
      progressVisible: false
    };
  });
  state.uploading = false;
  state.activeXhr = null;
  state.shared = {title: '', description: '', takenAt: '', taggedPeople: []};
  state.suggestions = [];
  state.searchQuery = '';
  _renderMediaUploadModal();
  openAccessibleOverlay(_ensureMediaUploadModal(), {initialFocus: '[data-shared-field="title"]'});
  return false;
}

window.startMediaUploadWorkflow = startMediaUploadWorkflow;

function _uploadSingleFile(file, personId, payload, progressCallback, xhrRefCallback) {
  return new Promise(function(resolve, reject) {
    var fd = new FormData();
    fd.append('file', file);
    if (personId) fd.append('person_id', personId);
    if (payload.caption) fd.append('caption', payload.caption);
    if (payload.title) fd.append('title', payload.title);
    if (payload.description) fd.append('description', payload.description);
    if (payload.takenAt) fd.append('taken_at', payload.takenAt);
    if (payload.purpose) fd.append('purpose', payload.purpose);
    if (payload.taggedPersonIds && payload.taggedPersonIds.length) {
      fd.append('tagged_person_ids', JSON.stringify(payload.taggedPersonIds));
    }

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/media');
    xhr.responseType = 'json';
    xhr.upload.onprogress = function(event) {
      if (!progressCallback || !event.lengthComputable) {
        return;
      }
      progressCallback(Math.min(99, Math.round((event.loaded / event.total) * 100)));
    };
    xhr.onload = function() {
      if (xhr.status < 400) {
        resolve(xhr.response);
        return;
      }
      var detail = xhr.response && xhr.response.detail ? xhr.response.detail : xhr.statusText;
      reject(new Error(detail || 'Upload failed'));
    };
    xhr.onerror = function() { reject(new Error('Network error')); };
    xhr.onabort = function() { reject(new Error('Upload cancelled')); };
    if (xhrRefCallback) {
      xhrRefCallback(xhr);
    }
    xhr.send(fd);
  });
}

async function _maybeSetHeadshot(personId, uploadedItems, strategy, currentPhotoUrl) {
  if (!personId || !uploadedItems || !uploadedItems.length || !strategy) {
    return;
  }
  var imageUpload = uploadedItems.find(function(item) {
    return item && item.mime_type && item.mime_type.indexOf('image') === 0;
  });
  if (!imageUpload) {
    return;
  }
  if (strategy === 'if-empty') {
    if (typeof currentPhotoUrl !== 'undefined' && currentPhotoUrl !== null) {
      if (currentPhotoUrl) {
        return;
      }
    } else {
      var personResp = await fetch('/api/persons/' + personId);
      if (!personResp.ok) {
        return;
      }
      var person = await personResp.json();
      if (person.photo_url) {
        return;
      }
    }
  }
  await fetch('/api/persons/' + personId, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ photo_url: imageUpload.id })
  });
}

async function _submitMediaUploadWorkflow() {
  var state = _getMediaUploadState();
  if (!state.options || state.uploading) {
    return;
  }
  state.uploading = true;
  _renderMediaUploadModal();
  var uploadedItems = [];
  try {
    for (var index = 0; index < state.items.length; index += 1) {
      var item = state.items[index];
      item.progressVisible = true;
      item.progress = 0;
      item.progressLabel = familyBookLabel('upload.progress_starting', 'Starting upload...');
      _renderMediaUploadProgress(index, 0, item.progressLabel);
      var response = await _uploadSingleFile(
        item.file,
        state.options.personId,
        {
          caption: item.caption || state.options.caption || '',
          title: item.title || state.shared.title,
          description: item.description || state.shared.description,
          takenAt: item.takenAt || state.shared.takenAt,
          purpose: state.options.purpose || 'memory',
          taggedPersonIds: state.shared.taggedPeople.map(function(person) { return person.id; })
        },
        function(progress) {
          item.progress = progress;
          item.progressLabel = familyBookLabel('upload.progress_percent', 'Uploading') + ' ' + progress + '%';
          _renderMediaUploadProgress(index, progress, item.progressLabel);
        },
        function(xhr) {
          state.activeXhr = xhr;
        }
      );
      item.progress = 100;
      item.progressLabel = familyBookLabel('upload.progress_done', 'Upload complete');
      _renderMediaUploadProgress(index, 100, item.progressLabel);
      uploadedItems.push(response);
      state.activeXhr = null;
    }

    await _maybeSetHeadshot(state.options.personId, uploadedItems, state.options.autoSetHeadshot, state.options.currentPhotoUrl);
    if (typeof state.options.onComplete === 'function') {
      await state.options.onComplete(uploadedItems);
    }
    showToast(state.options.successMessage || familyBookLabel('upload.upload_complete', 'Upload complete'));
    _cancelMediaUploadWorkflow();
  } catch (err) {
    state.uploading = false;
    state.activeXhr = null;
    _renderMediaUploadModal();
    showToast(err.message || familyBookLabel('common.error', 'Something went wrong'));
  }
}

function _renderMediaUploadProgress(index, progress, label) {
  var modal = document.getElementById('media-upload-modal');
  if (!modal) {
    return;
  }
  var wrap = modal.querySelector('[data-progress-wrap="' + index + '"]');
  if (!wrap) {
    return;
  }
  wrap.hidden = false;
  var fill = wrap.querySelector('.media-upload-progress__fill');
  var text = wrap.querySelector('.media-upload-progress__label');
  if (fill) {
    fill.style.width = Math.max(0, Math.min(100, progress)) + '%';
  }
  if (text) {
    text.textContent = label || '';
  }
}

async function uploadMedia(source) {
  var ctx = _resolveMediaUploadContext(source);
  if (!ctx.fileInput || !ctx.fileInput.files || !ctx.fileInput.files.length) {
    showToast(familyBookLabel('upload.select_file', 'Select a file'));
    return false;
  }

  return startMediaUploadWorkflow({
    files: Array.from(ctx.fileInput.files),
    personId: ctx.personId,
    purpose: 'memory',
    title: familyBookLabel('upload.title', 'Review upload'),
    onComplete: async function() {
      ctx.fileInput.value = '';
      if (ctx.personId) {
        var gallery = document.getElementById('person-media');
        if (gallery) {
          gallery.setAttribute('aria-busy', 'true');
          try {
            var partialResp = await fetch('/partials/media-gallery?person_id=' + encodeURIComponent(ctx.personId));
            if (partialResp.ok) {
              replaceNodeChildrenFromHTML(gallery, await partialResp.text());
            }
          } finally {
            gallery.setAttribute('aria-busy', 'false');
          }
        }
      }
    }
  });
}

// Media delete
async function deleteMedia(mediaId, options) {
  var opts = options || {};
  var label = familyBookLabel('media.confirm_delete', 'Remove this media? This cannot be undone.');
  if (!confirm(label)) {
    return false;
  }
  var resp = await fetch('/api/media/' + mediaId, {method: 'DELETE'});
  if (!resp.ok) {
    var detail = '';
    try { detail = (await resp.json()).detail || ''; } catch (e) { /* ignore */ }
    showToast(detail || familyBookLabel('common.error', 'Something went wrong'));
    return false;
  }
  showToast(familyBookLabel('media.deleted', 'Media removed'));
  if (typeof opts.onDelete === 'function') {
    opts.onDelete();
  }
  return true;
}
window.deleteMedia = deleteMedia;

// ── Language autocomplete (shared) ──
var _langCache = null;
function _fetchLanguages() {
  if (_langCache) return _langCache;
  _langCache = fetch('/static/data/languages.json')
    .then(function(r) { return r.json(); })
    .catch(function() { _langCache = null; return []; });
  return _langCache;
}

/**
 * Initialize a language autocomplete chip input.
 * @param {HTMLElement} container – element containing [data-lang-autocomplete]
 * @param {Object} opts – { placeholder: string }
 * Expects this HTML structure inside container:
 *   <div class="tag-input" data-lang-autocomplete>
 *     <div class="tag-input__chips" data-lang-chips>
 *       <input type="text" class="tag-input__text" data-lang-search ...>
 *     </div>
 *     <div class="tag-input__dropdown" data-lang-dropdown></div>
 *     <input type="hidden" name="languages" data-lang-hidden value="en,es">
 *   </div>
 */
function initLanguageAutocomplete(container, opts) {
  if (!container) return null;
  var wrapper = container.querySelector ? container.querySelector('[data-lang-autocomplete]') : null;
  if (!wrapper) return null;
  var chipsEl = wrapper.querySelector('[data-lang-chips]');
  var searchEl = wrapper.querySelector('[data-lang-search]');
  var dropdownEl = wrapper.querySelector('[data-lang-dropdown]');
  var hiddenEl = wrapper.querySelector('[data-lang-hidden]');
  if (!chipsEl || !searchEl || !dropdownEl || !hiddenEl) return null;

  var allLanguages = [];
  var selectedCodes = (hiddenEl.value || '').split(',').map(function(s) { return s.trim(); }).filter(Boolean);

  function renderChips() {
    chipsEl.querySelectorAll('.tag-input__chip').forEach(function(n) { n.remove(); });
    selectedCodes.forEach(function(code) {
      var lang = allLanguages.find(function(e) { return e.code === code; });
      var chip = document.createElement('span');
      chip.className = 'tag-input__chip';
      chip.textContent = lang ? lang.name + ' (' + code + ')' : code;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'tag-input__chip-remove';
      btn.innerHTML = '&times;';
      btn.onclick = function() { removeCode(code); };
      chip.appendChild(btn);
      chipsEl.insertBefore(chip, searchEl);
    });
    hiddenEl.value = selectedCodes.join(',');
  }

  function filterDropdown() {
    var query = searchEl.value.toLowerCase();
    if (!query) {
      dropdownEl.className = 'tag-input__dropdown';
      dropdownEl.innerHTML = '';
      return;
    }
    var matches = allLanguages.filter(function(e) {
      return (e.name.toLowerCase().indexOf(query) !== -1 || e.code.toLowerCase().indexOf(query) !== -1)
        && selectedCodes.indexOf(e.code) === -1;
    }).slice(0, 8);
    if (!matches.length) {
      dropdownEl.className = 'tag-input__dropdown';
      dropdownEl.innerHTML = '';
      return;
    }
    dropdownEl.innerHTML = matches.map(function(e) {
      return '<div class="tag-input__option" data-lang-code="' + escapeHtml(e.code) + '">' + escapeHtml(e.name) + ' (' + escapeHtml(e.code) + ')</div>';
    }).join('');
    dropdownEl.className = 'tag-input__dropdown tag-input__dropdown--open';
  }

  function addCode(code) {
    if (selectedCodes.indexOf(code) === -1) {
      selectedCodes.push(code);
      renderChips();
    }
    searchEl.value = '';
    closeDropdown();
  }

  function removeCode(code) {
    selectedCodes = selectedCodes.filter(function(c) { return c !== code; });
    renderChips();
  }

  function closeDropdown() {
    dropdownEl.className = 'tag-input__dropdown';
    dropdownEl.innerHTML = '';
  }

  // Event listeners
  searchEl.addEventListener('input', filterDropdown);
  searchEl.addEventListener('focus', filterDropdown);
  searchEl.addEventListener('blur', function() { setTimeout(closeDropdown, 200); });
  searchEl.addEventListener('keydown', function(event) {
    if (event.key === 'Backspace' && !searchEl.value && selectedCodes.length > 0) {
      selectedCodes.pop();
      renderChips();
    }
  });
  chipsEl.addEventListener('click', function() { searchEl.focus(); });

  // Delegate click on dropdown options
  dropdownEl.addEventListener('mousedown', function(event) {
    var opt = event.target.closest('[data-lang-code]');
    if (opt) {
      addCode(opt.getAttribute('data-lang-code'));
    }
  });

  // Load data and render
  _fetchLanguages().then(function(data) {
    allLanguages = data;
    renderChips();
  });

  return {
    getSelectedCodes: function() { return selectedCodes.slice(); }
  };
}
window.initLanguageAutocomplete = initLanguageAutocomplete;

// Person sidebar (tree page)
function closeSidebar() {
  var el = document.getElementById('person-sidebar');
  if (el) {
    el.classList.remove('person-sidebar--open');
    closeAccessibleOverlay(el);
  }
}

document.body.addEventListener('htmx:beforeRequest', function(event) {
  var target = event.detail && event.detail.target ? event.detail.target : event.target;
  if (target && target.setAttribute) {
    target.setAttribute('aria-busy', 'true');
  }
});

document.body.addEventListener('htmx:afterSwap', function(event) {
  var target = event.detail && event.detail.target ? event.detail.target : event.target;
  if (target && target.setAttribute) {
    target.setAttribute('aria-busy', 'false');
  }
});

document.body.addEventListener('htmx:responseError', function(event) {
  var target = event.detail && event.detail.target ? event.detail.target : event.target;
  if (target && target.setAttribute) {
    target.setAttribute('aria-busy', 'false');
  }
  showToast('Could not load content');
});

// ── Story audio inline upload ───────────────────────────────────────────
// Uploads a selected audio file and wires the result to the hidden story
// audio_media_id input so it gets submitted with the story form.
async function handleStoryAudioSelect(fileInput, storySlot) {
  var file = fileInput.files && fileInput.files[0];
  if (!file) return;
  var uploadRow = document.getElementById('story-audio-upload-' + storySlot);
  var personId = uploadRow ? uploadRow.getAttribute('data-person-id') : '';
  var hiddenInput = document.getElementById('story-audio-id-' + storySlot);
  if (!hiddenInput) return;

  // Disable the file input during upload
  fileInput.disabled = true;
  var label = uploadRow ? uploadRow.querySelector('span') : null;
  if (label) label.textContent = '…';

  try {
    var result = await new Promise(function (resolve, reject) {
      var fd = new FormData();
      fd.append('file', file);
      if (personId) fd.append('person_id', personId);
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/media');
      xhr.responseType = 'json';
      xhr.onload = function () {
        if (xhr.status < 400) resolve(xhr.response);
        else reject(new Error((xhr.response && xhr.response.detail) || 'Upload failed'));
      };
      xhr.onerror = function () { reject(new Error('Network error')); };
      xhr.send(fd);
    });
    hiddenInput.value = result.id || '';
    // Show a simple audio player as confirmation
    if (uploadRow) {
      var player = document.createElement('audio');
      player.controls = true;
      player.style.width = '100%';
      player.style.marginBottom = '4px';
      var src = document.createElement('source');
      src.src = '/api/media/' + result.id + '/file';
      player.appendChild(src);
      uploadRow.insertBefore(player, fileInput);
      fileInput.style.display = 'none';
      if (label) label.textContent = file.name;
    }
  } catch (err) {
    fileInput.disabled = false;
    if (label) label.textContent = err.message || 'Upload failed';
    if (typeof showToast === 'function') showToast(err.message || 'Upload failed');
  }
}
window.handleStoryAudioSelect = handleStoryAudioSelect;

// ── TTS for story cards ─────────────────────────────────────────────────
// Reads the story body text aloud using the Web Speech API.
// Gracefully no-ops in browsers that lack speechSynthesis.
var _ttsActiveBtn = null;

function toggleStoryTTS(btn) {
  if (!('speechSynthesis' in window)) return;
  // Stop any in-progress speech first
  if (_ttsActiveBtn && _ttsActiveBtn !== btn) {
    window.speechSynthesis.cancel();
    _ttsActiveBtn.textContent = _ttsActiveBtn.getAttribute('data-tts-listen') || 'Listen';
    _ttsActiveBtn = null;
  }
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    btn.textContent = btn.getAttribute('data-tts-listen') || 'Listen';
    _ttsActiveBtn = null;
    return;
  }
  var storyId = btn.getAttribute('data-story-id');
  var card = storyId ? document.getElementById('story-' + storyId) : btn.closest('.wiki-story-card');
  if (!card) return;
  var bodyEl = card.querySelector('.wiki-story-card__body');
  if (!bodyEl) return;
  var text = bodyEl.textContent || bodyEl.innerText || '';
  if (!text.trim()) return;
  var utter = new window.SpeechSynthesisUtterance(text.trim());
  utter.onend = function () {
    btn.textContent = btn.getAttribute('data-tts-listen') || 'Listen';
    _ttsActiveBtn = null;
  };
  utter.onerror = function () {
    btn.textContent = btn.getAttribute('data-tts-listen') || 'Listen';
    _ttsActiveBtn = null;
  };
  btn.textContent = btn.getAttribute('data-tts-stop') || 'Stop';
  _ttsActiveBtn = btn;
  window.speechSynthesis.speak(utter);
}
