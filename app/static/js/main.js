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

function openAccessibleOverlay(overlay, options) {
  if (!overlay) return;
  var opts = options || {};
  var state = rememberOverlayState(overlay);
  state.returnFocusTo = document.activeElement;
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

// Reaction picker toggle
function toggleReactionPicker(momentId, trigger) {
  var el = document.getElementById('reaction-picker-' + momentId);
  if (!el) return;
  var shouldOpen = el.classList.contains('hidden');
  el.classList.toggle('hidden', !shouldOpen);
  el.hidden = !shouldOpen;
  if (trigger) {
    trigger.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
  }
}

// Comments toggle
function toggleComments(momentId, trigger) {
  var el = document.getElementById('comments-' + momentId);
  if (el) {
    var shouldOpen = el.classList.contains('hidden');
    el.classList.toggle('hidden', !shouldOpen);
    el.hidden = !shouldOpen;
    if (trigger) {
      trigger.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
    }
    if (shouldOpen && !el.dataset.loaded) {
      el.dataset.loaded = '1';
      el.setAttribute('aria-busy', 'true');
      htmx.trigger(el, 'toggle-comments-' + momentId);
    }
  }
}

// Post comment
async function postComment(e, momentId) {
  e.preventDefault();
  var input = e.target.querySelector('input[name="body"]');
  var statusNode = document.getElementById('comment-status-' + momentId);
  var body = input.value.trim();
  if (!body) return;
  if (statusNode) {
    statusNode.textContent = '';
    statusNode.classList.add('hidden');
  }
  input.disabled = true;
  try {
    var resp = await fetch('/api/moments/' + momentId + '/comments', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({body: body})
    });
    if (resp.ok) {
      input.value = '';
      // Reload comments
      htmx.ajax('GET', '/partials/comments/' + momentId, '#comments-' + momentId);
    } else if (statusNode) {
      var data = await resp.json().catch(function() { return {}; });
      statusNode.textContent = data.detail || 'Could not add comment';
      statusNode.classList.remove('hidden');
    }
  } finally {
    input.disabled = false;
  }
}

// Lightbox
function openLightbox(url, altText) {
  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.hidden = true;
  lb.setAttribute('aria-hidden', 'true');
  lb.onclick = function(e) {
    if (e.target === lb) {
      closeAccessibleOverlay(lb);
      lb.remove();
    }
  };
  var closeBtn = document.createElement('button');
  closeBtn.className = 'lightbox__close';
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Close media viewer');
  closeBtn.textContent = '\u00D7';
  closeBtn.onclick = function(e) {
    e.stopPropagation();
    closeAccessibleOverlay(lb);
    lb.remove();
  };
  var dialog = document.createElement('div');
  dialog.className = 'lightbox__dialog';
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-label', altText || 'Expanded media');
  dialog.tabIndex = -1;
  var img = document.createElement('img');
  img.src = url;
  img.alt = altText || 'Expanded media';
  dialog.appendChild(closeBtn);
  dialog.appendChild(img);
  lb.appendChild(dialog);
  document.body.appendChild(lb);
  openAccessibleOverlay(lb, {initialFocus: '.lightbox__close'});
}

// Media upload (person profile page)
async function uploadMedia() {
  var fileInput = document.getElementById('media-upload-file');
  if (!fileInput || !fileInput.files[0]) return showToast('Select a file');
  var fd = new FormData();
  fd.append('file', fileInput.files[0]);
  // Get person_id from URL
  var match = window.location.pathname.match(/\/people\/([^/]+)/);
  if (match) fd.append('person_id', match[1]);
  var resp = await fetch('/api/media', {method: 'POST', body: fd});
  if (resp.ok) {
    showToast('Uploaded');
    if (match) {
      var gallery = document.getElementById('person-media');
      if (gallery) {
        gallery.setAttribute('aria-busy', 'true');
        try {
          var partialResp = await fetch('/partials/media-gallery?person_id=' + encodeURIComponent(match[1]));
          if (partialResp.ok) {
            gallery.innerHTML = await partialResp.text();
          }
        } finally {
          gallery.setAttribute('aria-busy', 'false');
        }
      }
    }
  } else {
    showToast('Upload failed');
  }
}

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
