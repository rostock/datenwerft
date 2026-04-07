/**
 * Dashboard Grid Layout Manager
 * Handles drag-and-drop functionality and layout persistence
 */

document.addEventListener('DOMContentLoaded', function() {
  const gridContainer = document.getElementById('grid-container');
  const editLayoutBtn = document.getElementById('edit-layout-btn');
  const editLayoutText = document.getElementById('edit-layout-text');
  const editLayoutIcon = editLayoutBtn.querySelector('i');
  const gridItems = Array.from(document.querySelectorAll('.grid-item'));

  // Inject Resize Controls
  gridItems.forEach(item => {
    const controls = document.createElement('div');
    controls.className = 'resize-controls';
    controls.innerHTML = `
      <div class="resize-group">
        <button type="button" class="resize-btn" data-action="toggle-width" title="Breite ändern (1 Spalte / 2 Spalten)">
          <i class="fa-solid fa-arrows-left-right"></i>
        </button>
        <button type="button" class="resize-btn" data-action="toggle-height" title="Höhe ändern (1x / 2x / 3x)">
          <i class="fa-solid fa-arrows-up-down"></i>
        </button>
      </div>
    `;
    item.appendChild(controls);
    updateResizeButtonState(item);
  });

  /**
   * Update resize button states based on item classes
   */
  function updateResizeButtonState(item) {
    const widthBtn = item.querySelector('[data-action="toggle-width"]');
    const heightBtn = item.querySelector('[data-action="toggle-height"]');

    if (widthBtn) widthBtn.classList.toggle('active', item.classList.contains('use2columns'));

    if (heightBtn) {
      const is2 = item.classList.contains('use2rows');
      const is3 = item.classList.contains('use3rows');

      heightBtn.classList.toggle('active', is2 || is3);

      if (is3) {
        heightBtn.innerHTML = '<span style="font-weight:800">3</span>';
        heightBtn.title = "Höhe: 3-fach (Klicken zum Zurücksetzen)";
      } else if (is2) {
        heightBtn.innerHTML = '<span style="font-weight:800">2</span>';
        heightBtn.title = "Höhe: 2-fach (Klicken für 3-fach)";
      } else {
        heightBtn.innerHTML = '<i class="fa-solid fa-arrows-up-down"></i>';
        heightBtn.title = "Höhe ändern (1x / 2x / 3x)";
      }
    }
  }

  /**
   * Handle resize button clicks
   */
  gridContainer.addEventListener('click', function(e) {
    if (!isEditMode) return;
    const btn = e.target.closest('.resize-btn');
    if (!btn) return;

    e.stopPropagation();
    e.preventDefault();

    const item = btn.closest('.grid-item');
    const action = btn.dataset.action;

    if (action === 'toggle-width') {
      item.classList.toggle('use2columns');
    } else if (action === 'toggle-height') {
      // Cycle: Normal -> 2rows -> 3rows -> Normal
      if (item.classList.contains('use2rows')) {
        item.classList.remove('use2rows');
        item.classList.add('use3rows');
      } else if (item.classList.contains('use3rows')) {
        item.classList.remove('use3rows');
      } else {
        item.classList.add('use2rows');
      }
    }
    updateResizeButtonState(item);
  });

  // Initialize Bootstrap tooltip safely
  let editLayoutTooltip = null;
  try {
    editLayoutTooltip = new bootstrap.Tooltip(editLayoutBtn);
  } catch (e) {
    console.warn('Bootstrap Tooltip initialization failed:', e);
  }

  let isEditMode = false;
  let draggedItem = null;

  /**
   * Toggle between edit and normal mode
   */
  editLayoutBtn.addEventListener('click', function() {
    if (editLayoutTooltip) editLayoutTooltip.hide();
    isEditMode = !isEditMode;
    editLayoutBtn.classList.toggle('active', isEditMode);
    gridContainer.classList.toggle('edit-mode', isEditMode);

    if (isEditMode) {
      enableDragDrop();
      editLayoutBtn.setAttribute('data-bs-original-title', 'Dashboard-Bearbeitung beenden');
      if (editLayoutText) editLayoutText.textContent = 'Speichern & Beenden';
      editLayoutIcon.className = 'fa-solid fa-check me-2';
      editLayoutBtn.classList.remove('btn-outline-secondary');
      editLayoutBtn.classList.add('btn-primary');
    } else {
      disableDragDrop();
      editLayoutBtn.setAttribute('data-bs-original-title', 'Dashboard Layout bearbeiten');
      if (editLayoutText) editLayoutText.textContent = 'Layout anpassen';
      editLayoutIcon.className = 'fa-solid fa-pen-to-square me-2';
      editLayoutBtn.classList.add('btn-outline-secondary');
      editLayoutBtn.classList.remove('btn-primary');
      saveGridLayout();
    }
  });

  /**
   * Enable drag and drop functionality
   */
  function enableDragDrop() {
    gridItems.forEach(item => {
      item.classList.add('draggable');
      item.draggable = true;
    });
  }

  /**
   * Disable drag and drop functionality
   */
  function disableDragDrop() {
    gridItems.forEach(item => {
      item.classList.remove('draggable', 'dragging', 'drag-over', 'just-dropped');
      item.draggable = false;
    });
  }

  /**
   * Handle drag start event
   */
  gridContainer.addEventListener('dragstart', function(e) {
    if (!isEditMode) return;

    let gridItem = e.target.closest('.grid-item');
    if (!gridItem) return;

    draggedItem = gridItem;
    draggedItem.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  });

  /**
   * Handle drag end event
   */
  gridContainer.addEventListener('dragend', function(e) {
    if (!isEditMode || !draggedItem) return;
    draggedItem.classList.remove('dragging');
    gridItems.forEach(item => item.classList.remove('drag-over'));
    draggedItem = null;
  });

  /**
   * Handle drag over event
   */
  gridContainer.addEventListener('dragover', function(e) {
    if (!isEditMode || !draggedItem) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  });

  /**
   * Handle drag enter event
   */
  gridContainer.addEventListener('dragenter', function(e) {
    if (!isEditMode || !draggedItem) return;
    let gridItem = e.target.closest('.grid-item');
    if (!gridItem || gridItem === draggedItem) return;
    gridItem.classList.add('drag-over');
  });

  /**
   * Handle drag leave event
   */
  gridContainer.addEventListener('dragleave', function(e) {
    if (!isEditMode) return;
    let gridItem = e.target.closest('.grid-item');
    if (!gridItem) return;
    gridItem.classList.remove('drag-over');
  });

  /**
   * Handle drop event - reorder grid items
   */
  gridContainer.addEventListener('drop', function(e) {
    if (!isEditMode || !draggedItem) return;
    e.preventDefault();
    e.stopPropagation();

    let targetItem = e.target.closest('.grid-item');
    if (!targetItem || targetItem === draggedItem) return;

    const allItems = Array.from(gridContainer.children).filter(child => child.classList.contains('grid-item'));
    const draggedIndex = allItems.indexOf(draggedItem);
    const targetIndex = allItems.indexOf(targetItem);

    if (draggedIndex < targetIndex) {
      targetItem.parentNode.insertBefore(draggedItem, targetItem.nextSibling);
    } else {
      targetItem.parentNode.insertBefore(draggedItem, targetItem);
    }

    // Add drop animation
    draggedItem.classList.remove('dragging');
    draggedItem.classList.add('just-dropped');

    const droppedItem = draggedItem;
    setTimeout(() => {
      if (droppedItem) droppedItem.classList.remove('just-dropped');
    }, 600);

    targetItem.classList.remove('drag-over');
  });

  /**
   * Save grid layout order to server
   */
  function saveGridLayout() {
    const items = Array.from(gridContainer.children)
      .filter(child => child.classList.contains('grid-item'));

    const order = items.map(item => item.id);
    const sizes = {};

    items.forEach(item => {
      const itemSizes = [];
      if (item.classList.contains('use2columns')) itemSizes.push('use2columns');
      if (item.classList.contains('use2rows')) itemSizes.push('use2rows');
      if (item.classList.contains('use3rows')) itemSizes.push('use3rows');

      if (itemSizes.length > 0) {
        sizes[item.id] = itemSizes;
      }
    });

    console.log('Saving layout order:', order, 'sizes:', sizes);

    fetch(saveLayoutUrl, {
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        layout: order,
        sizes: sizes
      })
    })
    .then(response => {
      console.log('Save response status:', response.status);
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => console.log('Layout saved:', data))
    .catch(error => console.error('Fehler beim Speichern des Layouts:', error));
  }

  /**
   * Load grid layout order from server data
   */
  function loadGridLayout() {
    const layoutDataElement = document.getElementById('dashboard-layout-data');
    if (!layoutDataElement) return;

    console.log('Raw layout data from server:', layoutDataElement.textContent);

    try {
      const data = JSON.parse(layoutDataElement.textContent);
      console.log('Parsed layout data:', data);

      if (!data) return;

      let order = [];
      let sizes = {};

      // Handle both legacy format (array) and new format (object)
      if (Array.isArray(data)) {
        order = data;
      } else {
        order = data.layout || [];
        sizes = data.sizes || {};
      }

      if (order.length === 0 && Object.keys(sizes).length === 0) return;

      const itemMap = {};
      gridItems.forEach(item => {
        itemMap[item.id] = item;
      });

      // Apply saved sizes
      Object.keys(sizes).forEach(id => {
        if (itemMap[id]) {
          // Reset size classes first
          itemMap[id].classList.remove('use2columns', 'use2rows', 'use3rows');
          sizes[id].forEach(cls => itemMap[id].classList.add(cls));
          updateResizeButtonState(itemMap[id]);
        }
      });

      // Reorder items based on saved layout
      if (order.length > 0) {
        order.forEach(id => {
          if (itemMap[id]) {
            gridContainer.appendChild(itemMap[id]);
          } else {
            console.warn('Item ID from saved layout not found in DOM:', id);
          }
        });
      }
    } catch (e) {
      console.error('Fehler beim Laden des Grid-Layouts:', e);
    }
  }

  /**
   * Check content height and auto-assign use2rows if needed
   */
  function checkContentHeight() {
    gridItems.forEach(item => {
      // Only check items that are not already 3 rows
      if (item.classList.contains('use3rows')) return;

      const cardBody = item.querySelector('.card-body');
      if (!cardBody) return;

      // Calculate total height of children including margins
      let contentHeight = 0;
      Array.from(cardBody.children).forEach(child => {
        const style = window.getComputedStyle(child);
        contentHeight += child.offsetHeight + (parseInt(style.marginTop) || 0) + (parseInt(style.marginBottom) || 0);
      });

      // Add padding of card-body
      const bodyStyle = window.getComputedStyle(cardBody);
      const padding = (parseInt(bodyStyle.paddingTop) || 0) + (parseInt(bodyStyle.paddingBottom) || 0);
      const totalHeight = contentHeight + padding;

      // Threshold: Grid row min-height is 200px.
      // If content is significantly larger (e.g. > 225px), upgrade to 2 rows.
      if (totalHeight > 225) {
        if (!item.classList.contains('use2rows')) {
          item.classList.add('use2rows');
          updateResizeButtonState(item);
        }
      }
    });
  }

  // Run check on load and resize
  window.addEventListener('load', checkContentHeight);

  let resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(checkContentHeight, 200);
  });

  // Initialize: Load saved layout on page load
  loadGridLayout();

  // Run check after layout load to ensure content fits
  setTimeout(checkContentHeight, 100);
});
