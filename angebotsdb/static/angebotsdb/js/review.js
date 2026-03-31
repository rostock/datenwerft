'use strict';

/**
 * review.js
 *
 * Steuert die interaktive Logik der Review-Ansicht:
 *  1. Kommentar-Textfelder per Klick auf den Toggle-Button ein-/ausklappen
 *  2. Zeilenfarbe der Tabelle aktualisieren wenn ein Kommentar vorhanden ist
 *  3. Freigabe- und Zurückweisen-Button dynamisch aktivieren/deaktivieren
 *  4. Hinweistext unterhalb der Buttons aktualisieren
 *  5. Formular-Submit über hidden input + nativen submit-Button
 */

document.addEventListener('DOMContentLoaded', function () {

  const reviewForm = document.getElementById('review-form');
  if (!reviewForm) return;

  const btnApprove    = document.getElementById('btn-approve');
  const btnReject     = document.getElementById('btn-reject');
  const actionHint    = document.getElementById('action-hint');
  const hiddenAction  = document.getElementById('hidden-action');

  const commentFields = Array.from(reviewForm.querySelectorAll('.comment-field'));
  const toggleButtons = Array.from(reviewForm.querySelectorAll('.toggle-comment'));

  // ── 1. Toggle-Buttons ─────────────────────────────────────────────────────

  toggleButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var fieldName = btn.dataset.field;
      var wrapper   = document.getElementById('comment-wrapper-' + fieldName);
      var textarea  = document.getElementById('comment-' + fieldName);

      if (!wrapper) return;

      var isHidden = wrapper.classList.contains('d-none');

      if (isHidden) {
        wrapper.classList.remove('d-none');
        btn.classList.remove('btn-outline-secondary');
        btn.classList.add('btn-warning');
        btn.innerHTML = '<i class="fa-solid fa-comment me-1"></i>Kommentar bearbeiten';
        if (textarea) textarea.focus();
      } else {
        var val = textarea ? textarea.value.trim() : '';
        if (val === '') {
          wrapper.classList.add('d-none');
          btn.classList.remove('btn-warning');
          btn.classList.add('btn-outline-secondary');
          btn.innerHTML = '<i class="fa-solid fa-comment me-1"></i>Kommentar';
        }
      }
    });
  });

  // ── 2. & 3. & 4. Button-States aktualisieren ──────────────────────────────

  function updateButtonStates() {
    var hasComments = false;

    commentFields.forEach(function (field) {
      var fieldName = field.id.replace('comment-', '');
      var row       = document.getElementById('row-' + fieldName);
      var toggleBtn = reviewForm.querySelector('.toggle-comment[data-field="' + fieldName + '"]');
      var wrapper   = document.getElementById('comment-wrapper-' + fieldName);
      var val       = field.value.trim();

      if (val !== '') {
        hasComments = true;

        if (row) row.classList.add('review-row-commented');

        if (toggleBtn) {
          toggleBtn.classList.remove('btn-outline-secondary');
          toggleBtn.classList.add('btn-warning');
          toggleBtn.innerHTML = '<i class="fa-solid fa-comment me-1"></i>Kommentar bearbeiten';
        }

        if (wrapper) wrapper.classList.remove('d-none');

      } else {
        if (row) row.classList.remove('review-row-commented');
      }
    });

    // Approve-Button: sichtbar disabled/enabled über aria + visuelle Klasse,
    // aber NICHT das HTML-disabled-Attribut setzen – das würde den value blocken.
    // Stattdessen blockieren wir den Klick im click-Handler.
    if (btnApprove) {
      if (hasComments) {
        btnApprove.setAttribute('aria-disabled', 'true');
        btnApprove.classList.add('opacity-50');
        btnApprove.style.pointerEvents = 'none';
      } else {
        btnApprove.removeAttribute('aria-disabled');
        btnApprove.classList.remove('opacity-50');
        btnApprove.style.pointerEvents = '';
      }
    }

    if (btnReject) {
      if (!hasComments) {
        btnReject.setAttribute('aria-disabled', 'true');
        btnReject.classList.add('opacity-50');
        btnReject.style.pointerEvents = 'none';
      } else {
        btnReject.removeAttribute('aria-disabled');
        btnReject.classList.remove('opacity-50');
        btnReject.style.pointerEvents = '';
      }
    }

    if (actionHint) {
      if (hasComments) {
        actionHint.innerHTML =
          '<i class="fa-solid fa-triangle-exclamation me-1 text-warning"></i>' +
          'Kommentare vorhanden \u2013 Freigabe nicht m\u00f6glich.';
      } else {
        actionHint.innerHTML =
          '<i class="fa-solid fa-circle-check me-1 text-success"></i>' +
          'Keine Kommentare \u2013 Freigabe m\u00f6glich.';
      }
    }
  }

  commentFields.forEach(function (field) {
    field.addEventListener('input', updateButtonStates);
  });

  // ── 5. Submit-Logik ───────────────────────────────────────────────────────
  //
  // Beide Buttons sind type="submit". Das hidden-input #hidden-action
  // hat keinen name – der value kommt direkt vom geklickten Button über
  // das name="action"-Attribut.
  // Wir fangen submit ab, lesen welcher Button geklickt wurde und
  // zeigen einen Spinner an. Der native Submit läuft dann normal weiter.

  var submitting = false;

  reviewForm.addEventListener('submit', function (e) {
    if (submitting) {
      e.preventDefault();
      return;
    }

    var actionValue = (hiddenAction && hiddenAction.value) ? hiddenAction.value : null;

    if (!actionValue) {
      // Kein action-Wert → Formular nicht abschicken
      e.preventDefault();
      return;
    }

    submitting = true;

    var activeBtn = document.getElementById('btn-' + actionValue);
    if (activeBtn) {
      activeBtn.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin me-1"></i>Wird verarbeitet\u2026';
    }
  });

  // Klick auf Approve
  if (btnApprove) {
    btnApprove.addEventListener('click', function (e) {
      // Doppelklick-Schutz
      if (submitting) { e.preventDefault(); return; }

      var hasComments = commentFields.some(function (f) {
        return f.value.trim() !== '';
      });
      if (hasComments) {
        e.preventDefault();
        return;
      }
      if (hiddenAction) hiddenAction.value = 'approve';
    });
  }

  // Klick auf Reject
  if (btnReject) {
    btnReject.addEventListener('click', function (e) {
      if (submitting) { e.preventDefault(); return; }

      var hasComments = commentFields.some(function (f) {
        return f.value.trim() !== '';
      });
      if (!hasComments) {
        e.preventDefault();
        return;
      }
      if (hiddenAction) hiddenAction.value = 'reject';
    });
  }

  // ── 6. Initialer Zustand ──────────────────────────────────────────────────
  updateButtonStates();

});