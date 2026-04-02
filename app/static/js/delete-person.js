/**
 * Shared delete-person handler.
 * Requires data attributes on the invoking page:
 *   #delete-person-data[data-person-id]
 *   #delete-person-data[data-person-name]
 *   #delete-person-data[data-confirm-msg]
 *   #delete-person-data[data-error-msg]
 */
async function deletePerson() {
  var el = document.getElementById('delete-person-data');
  if (!el) return;
  var name = el.dataset.personName;
  var confirmMsg = el.dataset.confirmMsg.replace('{name}', name);
  if (!confirm(confirmMsg)) return;
  try {
    var resp = await fetch('/api/persons/' + el.dataset.personId, { method: 'DELETE' });
    if (resp.ok || resp.status === 204) {
      window.location.href = '/wiki';
    } else {
      var err = await resp.json();
      alert(err.detail || el.dataset.errorMsg);
    }
  } catch(e) {
    alert(el.dataset.errorMsg);
  }
}
