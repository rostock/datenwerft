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

  let isEditMode = false;
  let draggedItem = null;

  /**
   * Toggle between edit and normal mode
   */
  editLayoutBtn.addEventListener('click', function() {
    isEditMode = !isEditMode;
    editLayoutBtn.classList.toggle('active', isEditMode);
    gridContainer.classList.toggle('edit-mode', isEditMode);

    if (isEditMode) {
      editLayoutBtn.title = 'Layout-Bearbeitung beenden';
      editLayoutText.textContent = 'Speichern & Beenden';
      editLayoutIcon.className = 'fa-solid fa-check me-2';
      editLayoutBtn.classList.remove('btn-outline-secondary');
      editLayoutBtn.classList.add('btn-primary');
      enableDragDrop();
    } else {
      editLayoutBtn.title = 'Layout bearbeiten';
      editLayoutText.textContent = 'Layout anpassen';
      editLayoutIcon.className = 'fa-solid fa-pen-to-square me-2';
      editLayoutBtn.classList.add('btn-outline-secondary');
      editLayoutBtn.classList.remove('btn-primary');
      disableDragDrop();
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
    setTimeout(() => {
      draggedItem.classList.remove('just-dropped');
    }, 600);

    targetItem.classList.remove('drag-over');
  });

  /**
   * Save grid layout order to server
   */
  function saveGridLayout() {
    const order = Array.from(gridContainer.children)
      .filter(child => child.classList.contains('grid-item'))
      .map(item => item.id);

    fetch(saveLayoutUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        layout: order
      })
    }).catch(error => console.error('Fehler beim Speichern des Layouts:', error));
  }

  /**
   * Load grid layout order from server data
   */
  function loadGridLayout() {
    const layoutDataElement = document.getElementById('dashboard-layout-data');
    if (!layoutDataElement) return;

    try {
      const order = JSON.parse(layoutDataElement.textContent);
      if (!order || order.length === 0) return;

      const itemMap = {};

      gridItems.forEach(item => {
        itemMap[item.id] = item;
      });

      // Reorder items based on saved layout
      order.forEach(id => {
        if (itemMap[id]) {
          gridContainer.appendChild(itemMap[id]);
        }
      });
    } catch (e) {
      console.error('Fehler beim Laden des Grid-Layouts:', e);
    }
  }

  // Initialize: Load saved layout on page load
  loadGridLayout();
});