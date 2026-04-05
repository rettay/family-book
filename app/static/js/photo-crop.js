/* Family Book — photo-crop.js
   Wraps Cropper.js for pre-upload editing and gallery image editing.

   Public API:
     window.openPhotoCrop(options)
       options.src        — image URL or blob URL to load
       options.onConfirm  — function(blob, mimeType) called when user confirms
       options.onCancel   — function() called when user cancels (optional)

     window.openGalleryPhotoCrop(mediaId, imgEl)
       Opens crop modal for an existing gallery image; POSTs result to
       /api/media/{mediaId}/edit-image and refreshes the thumbnail.
*/
(function () {
  'use strict';

  var _cropInstance = null;
  var _onConfirmCallback = null;
  var _onCancelCallback = null;
  var _sourceMime = 'image/jpeg';

  function _modal() { return document.getElementById('photo-crop-modal'); }
  function _img()   { return document.getElementById('photo-crop-img'); }

  function _destroyCropper() {
    if (_cropInstance) {
      _cropInstance.destroy();
      _cropInstance = null;
    }
  }

  function _open(src, mime, onConfirm, onCancel) {
    var modal = _modal();
    var img   = _img();
    if (!modal || !img) return;

    _destroyCropper();
    _sourceMime = mime || 'image/jpeg';
    _onConfirmCallback = onConfirm || null;
    _onCancelCallback  = onCancel  || null;

    img.src = src;
    img.onload = function () {
      if (typeof Cropper === 'undefined') {
        console.warn('Cropper.js not loaded');
        return;
      }
      _cropInstance = new Cropper(img, {
        viewMode: 1,
        autoCropArea: 1,
        responsive: true,
        checkOrientation: false,
      });
    };

    if (typeof window.openAccessibleOverlay === 'function') {
      window.openAccessibleOverlay(modal, { initialFocus: '#photo-crop-confirm' });
    } else {
      modal.hidden = false;
      modal.classList.remove('hidden');
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function _close() {
    var modal = _modal();
    if (!modal) return;
    _destroyCropper();
    if (typeof window.closeAccessibleOverlay === 'function') {
      window.closeAccessibleOverlay(modal);
    } else {
      modal.hidden = true;
      modal.classList.add('hidden');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  function _confirm() {
    if (!_cropInstance) {
      _close();
      return;
    }
    var mime = _sourceMime;
    if (mime !== 'image/png' && mime !== 'image/webp') mime = 'image/jpeg';
    _cropInstance.getCroppedCanvas().toBlob(function (blob) {
      var cb = _onConfirmCallback;
      _close();
      if (cb) cb(blob, mime);
    }, mime, 0.92);
  }

  // ── Wire up static modal buttons ─────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var modal       = _modal();
    var closeBtn    = document.getElementById('photo-crop-close');
    var cancelBtn   = document.getElementById('photo-crop-cancel');
    var confirmBtn  = document.getElementById('photo-crop-confirm');
    var rotateLeft  = document.getElementById('photo-crop-rotate-left');
    var rotateRight = document.getElementById('photo-crop-rotate-right');

    if (closeBtn)    closeBtn.onclick   = function () { if (_onCancelCallback) _onCancelCallback(); _close(); };
    if (cancelBtn)   cancelBtn.onclick  = function () { if (_onCancelCallback) _onCancelCallback(); _close(); };
    if (confirmBtn)  confirmBtn.onclick = _confirm;
    if (rotateLeft)  rotateLeft.onclick  = function () { if (_cropInstance) _cropInstance.rotate(-90); };
    if (rotateRight) rotateRight.onclick = function () { if (_cropInstance) _cropInstance.rotate(90); };

    if (modal) {
      modal.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { if (_onCancelCallback) _onCancelCallback(); _close(); }
      });
    }
  });

  // ── Public: generic open ──────────────────────────────────────────────
  window.openPhotoCrop = function (opts) {
    var options = opts || {};
    _open(options.src || '', options.mime || 'image/jpeg', options.onConfirm, options.onCancel);
  };

  // ── Public: open for an existing gallery media item ───────────────────
  window.openGalleryPhotoCrop = function (mediaId, triggerEl) {
    var src  = '/api/media/' + mediaId + '/file';
    var mime = 'image/jpeg'; // best-effort; server preserves format
    _open(src, mime, function (blob, blobMime) {
      var fd = new FormData();
      fd.append('file', blob, 'edit.' + (blobMime === 'image/png' ? 'png' : 'jpg'));
      fetch('/api/media/' + mediaId + '/edit-image', { method: 'POST', body: fd })
        .then(function (resp) {
          if (!resp.ok) throw new Error('edit-image failed');
          return resp.json();
        })
        .then(function () {
          // Bust thumb cache by reloading the img element
          var galleryItem = triggerEl ? triggerEl.closest('.media-gallery__item, article') : null;
          if (galleryItem) {
            var thumbImg = galleryItem.querySelector('img');
            if (thumbImg) {
              var base = thumbImg.src.split('?')[0];
              thumbImg.src = base + '?t=' + Date.now();
            }
          }
          if (typeof showToast === 'function') {
            showToast(familyBookLabel('media.edit_photo_saved', 'Photo updated'));
          }
        })
        .catch(function () {
          if (typeof showToast === 'function') {
            showToast(familyBookLabel('common.error', 'Error'));
          }
        });
    });
  };

  // ── Public: open for a pre-upload item in the upload modal ───────────
  // Called with the item index in the upload state and the file's data URL
  window.openUploadPhotoCrop = function (itemIndex, previewUrl, mime) {
    _open(previewUrl, mime || 'image/jpeg', function (blob, blobMime) {
      // Replace the file in the upload state
      if (!window.__familyBookMediaUploadState) return;
      var state = window.__familyBookMediaUploadState;
      var item  = state.items[itemIndex];
      if (!item) return;

      // Revoke old blob URL
      if (item.previewUrl && item.previewUrl.indexOf('blob:') === 0) {
        URL.revokeObjectURL(item.previewUrl);
      }

      // Build a new File from the cropped blob
      var ext  = blobMime === 'image/png' ? '.png' : '.jpg';
      var name = item.file.name.replace(/\.[^.]+$/, '') + '_edited' + ext;
      var newFile = new File([blob], name, { type: blobMime });
      item.file       = newFile;
      item.previewUrl = URL.createObjectURL(newFile);

      // Re-render the upload modal so the new preview is shown
      if (typeof _renderMediaUploadModal === 'function') {
        _renderMediaUploadModal();
      }
    });
  };

})();
