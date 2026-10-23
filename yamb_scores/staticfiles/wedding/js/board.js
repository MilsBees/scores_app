(() => {
  const text = JSON.parse(document.getElementById('wedding-texts').textContent);
  const body = document.body;
  const boardElement = document.getElementById('board');
  const filtersElement = document.getElementById('filters');
  const form = document.getElementById('card-form');
  const backdrop = document.getElementById('dialog-backdrop');
  const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
  const state = { columns: [], filter: 'all', editing: null, draggedCardId: null, draggedColumnId: null };

  const elements = {
    overall: document.getElementById('overall-progress'),
    syncStatus: document.getElementById('sync-status'),
    heading: document.getElementById('board-heading'),
    logout: document.getElementById('logout-button'),
    title: document.getElementById('card-title'),
    owner: document.getElementById('card-owner'),
    notes: document.getElementById('card-notes'),
    dueDate: document.getElementById('card-due-date'),
    subtaskList: document.getElementById('subtask-list'),
    dialogTitle: document.getElementById('dialog-title'),
    error: document.getElementById('dialog-error'),
  };

  elements.heading.textContent = text.board_heading;
  elements.logout.textContent = text.logout;
  filtersElement.setAttribute('aria-label', text.filters_label);
  document.getElementById('title-label').textContent = text.card_title;
  document.getElementById('owner-label').textContent = text.owner;
  document.getElementById('notes-label').textContent = text.notes;
  document.getElementById('due-date-label').textContent = text.due_date;
  document.getElementById('subtasks-label').textContent = text.subtasks;
  document.getElementById('add-subtask').textContent = text.add_subtask;
  document.getElementById('save-button').textContent = text.save;
  document.getElementById('cancel-button').textContent = text.cancel;
  document.getElementById('delete-button').textContent = text.delete;
  for (const [value, label] of Object.entries(text.owners)) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    elements.owner.append(option);
  }

  function endpoint(template, id) {
    return template.replace('/0/', `/${id}/`);
  }

  async function api(url, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body) {
      headers.set('Content-Type', 'application/json');
      headers.set('X-CSRFToken', csrfToken);
    } else if (options.method && options.method !== 'GET') {
      headers.set('X-CSRFToken', csrfToken);
    }
    const response = await fetch(url, { ...options, headers, credentials: 'same-origin' });
    if (response.status === 401) {
      window.location.assign(`${body.dataset.boardUrl.replace('api/board/', 'login/')}`);
      throw new Error('Authentication required');
    }
    const payload = response.status === 204 ? null : await response.json();
    if (!response.ok) throw new Error(payload?.error || text.api_error);
    return payload;
  }

  function makeButton(label, onClick, className = '') {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `button subtle ${className}`.trim();
    button.textContent = label;
    button.addEventListener('click', onClick);
    return button;
  }

  function isVisible(card) {
    return state.filter === 'all' || card.owner === state.filter || (card.owner === 'S' && ['M', 'E'].includes(state.filter));
  }

  function renderFilters() {
    filtersElement.replaceChildren();
    for (const [value, label] of Object.entries(text.filters)) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'filter-button';
      button.textContent = label;
      button.setAttribute('aria-pressed', String(state.filter === value));
      button.addEventListener('click', () => {
        state.filter = value;
        render();
      });
      filtersElement.append(button);
    }
  }

  function createSubtaskToggle(card, subtask) {
    const item = document.createElement('li');
    const label = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = subtask.done;
    checkbox.addEventListener('change', async () => {
      const updated = card.subtasks.map((task) => ({
        id: task.id,
        title: task.title,
        done: task.id === subtask.id ? checkbox.checked : task.done,
      }));
      try {
        await api(endpoint(body.dataset.cardUrlTemplate, card.id), {
          method: 'PATCH',
          body: JSON.stringify({ subtasks: updated }),
        });
        await loadBoard();
      } catch {
        checkbox.checked = subtask.done;
        window.alert(text.api_error);
      }
    });
    const title = document.createElement('span');
    title.textContent = subtask.title;
    if (subtask.done) title.className = 'subtask-done';
    label.append(checkbox, title);
    item.append(label);
    return item;
  }

  function createCard(card, column, index) {
    const article = document.createElement('article');
    article.className = 'task-card';
    article.draggable = true;
    article.dataset.cardId = card.id;
    article.addEventListener('dragstart', (event) => {
      state.draggedCardId = card.id;
      state.draggedColumnId = column.id;
      article.classList.add('dragging');
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', String(card.id));
    });
    article.addEventListener('dragend', () => {
      state.draggedCardId = null;
      state.draggedColumnId = null;
      article.classList.remove('dragging');
      document.querySelectorAll('.drop-target').forEach((node) => node.classList.remove('drop-target'));
    });

    const titleRow = document.createElement('div');
    titleRow.className = 'task-title-row';
    const title = document.createElement('h3');
    title.textContent = card.title;
    const badge = document.createElement('span');
    badge.className = `owner-badge owner-${card.owner}`;
    badge.textContent = card.owner;
    badge.title = text.filters[card.owner];
    titleRow.append(title, badge);
    article.append(titleRow);

    if (card.notes) {
      const notes = document.createElement('p');
      notes.className = 'task-notes';
      notes.textContent = card.notes;
      article.append(notes);
    }
    if (card.due_date) {
      const dueDate = document.createElement('time');
      dueDate.className = 'task-date';
      dueDate.dateTime = card.due_date;
      dueDate.textContent = `${text.due_date}: ${card.due_date}`;
      article.append(dueDate);
    }
    if (card.subtasks.length) {
      const list = document.createElement('ul');
      list.className = 'checklist';
      card.subtasks.forEach((subtask) => list.append(createSubtaskToggle(card, subtask)));
      article.append(list);
    }

    const actions = document.createElement('div');
    actions.className = 'card-actions';
    actions.append(makeButton(text.edit, () => openDialog(card, column.id)));
    const destination = document.createElement('select');
    destination.setAttribute('aria-label', text.move_to);
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = text.move_to;
    destination.append(placeholder);
    state.columns.forEach((target) => {
      const option = document.createElement('option');
      option.value = target.id;
      option.textContent = target.name;
      destination.append(option);
    });
    destination.addEventListener('change', async () => {
      if (!destination.value) return;
      try {
        await moveCard(card.id, Number(destination.value), Number.MAX_SAFE_INTEGER);
      } catch {
        window.alert(text.api_error);
      }
    });
    actions.append(destination);
    actions.append(makeButton(text.move_up, () => moveCardSafely(card.id, column.id, Math.max(0, index - 1))));
    actions.append(makeButton(text.move_down, () => moveCardSafely(card.id, column.id, index + 1)));
    article.append(actions);
    return article;
  }

  function render() {
    renderFilters();
    boardElement.replaceChildren();
    const doneColumn = state.columns.find((column) => column.name === text.column_names[2]);
    const totalCards = state.columns.reduce((count, column) => count + column.cards.length, 0);
    elements.overall.textContent = `${doneColumn?.cards.length || 0} / ${totalCards} ${text.done_count}`;
    state.columns.forEach((column) => {
      const section = document.createElement('section');
      section.className = 'board-column';
      section.dataset.columnId = column.id;
      section.addEventListener('dragover', (event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
      });
      section.addEventListener('drop', async (event) => {
        event.preventDefault();
        const cardId = Number(event.dataTransfer.getData('text/plain') || state.draggedCardId);
        if (!cardId) return;
        const cardElements = [...section.querySelectorAll('.task-card')];
        const relativeY = event.clientY;
        let position = cardElements.findIndex((element) => {
          const bounds = element.getBoundingClientRect();
          return relativeY < bounds.top + bounds.height / 2;
        });
        if (position < 0) position = cardElements.length;
        if (state.draggedColumnId === column.id) {
          const sourceIndex = cardElements.findIndex((element) => Number(element.dataset.cardId) === cardId);
          if (sourceIndex >= 0 && sourceIndex < position) position -= 1;
        }
        try {
          await moveCard(cardId, column.id, position);
        } catch {
          window.alert(text.api_error);
        }
      });

      const heading = document.createElement('header');
      heading.className = 'column-heading';
      const title = document.createElement('h2');
      title.textContent = column.name;
      const count = document.createElement('span');
      count.className = 'column-count';
      count.textContent = `${column.cards.length} ${text.cards_count}`;
      heading.append(title, count);
      const cardsContainer = document.createElement('div');
      cardsContainer.className = 'column-cards';
      const visibleCards = column.cards.filter(isVisible);
      if (!visibleCards.length) {
        const empty = document.createElement('p');
        empty.className = 'empty-column';
        empty.textContent = text.empty_column;
        cardsContainer.append(empty);
      } else {
        visibleCards.forEach((card, index) => {
          cardsContainer.append(createCard(card, column, column.cards.indexOf(card)));
        });
      }
      const addButton = makeButton(text.add_card, () => openDialog(null, column.id), 'column-add');
      section.append(heading, cardsContainer, addButton);
      boardElement.append(section);
    });
  }

  async function loadBoard() {
    const data = await api(body.dataset.boardUrl);
    state.columns = data.columns;
    elements.syncStatus.hidden = true;
    render();
  }

  function reportRefreshError() {
    elements.syncStatus.textContent = text.refresh_error;
    elements.syncStatus.hidden = false;
  }

  async function moveCard(cardId, columnId, position) {
    await api(endpoint(body.dataset.moveUrlTemplate, cardId), {
      method: 'POST',
      body: JSON.stringify({ column_id: columnId, position }),
    });
    await loadBoard();
  }

  async function moveCardSafely(cardId, columnId, position) {
    try {
      await moveCard(cardId, columnId, position);
    } catch {
      window.alert(text.api_error);
    }
  }

  function addSubtaskRow(item = { title: '', done: false }) {
    const row = document.createElement('div');
    row.className = 'subtask-row';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = Boolean(item.done);
    checkbox.setAttribute('aria-label', text.subtasks);
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 200;
    input.placeholder = text.new_subtask;
    input.value = item.title || '';
    if (item.id) input.dataset.subtaskId = item.id;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.textContent = '×';
    remove.setAttribute('aria-label', text.delete);
    remove.addEventListener('click', () => row.remove());
    row.append(checkbox, input, remove);
    elements.subtaskList.append(row);
  }

  function openDialog(card, columnId) {
    state.editing = card;
    elements.dialogTitle.textContent = card ? text.edit : text.add_card;
    elements.title.value = card?.title || '';
    elements.owner.value = card?.owner || 'M';
    elements.notes.value = card?.notes || '';
    elements.dueDate.value = card?.due_date || '';
    elements.subtaskList.replaceChildren();
    (card?.subtasks || []).forEach(addSubtaskRow);
    document.getElementById('delete-button').hidden = !card;
    document.getElementById('dialog-error').hidden = true;
    backdrop.dataset.columnId = columnId;
    backdrop.hidden = false;
    elements.title.focus();
  }

  function closeDialog() {
    backdrop.hidden = true;
    state.editing = null;
    form.reset();
  }

  document.getElementById('add-subtask').addEventListener('click', () => addSubtaskRow());
  document.getElementById('cancel-button').addEventListener('click', closeDialog);
  backdrop.addEventListener('click', (event) => {
    if (event.target === backdrop) closeDialog();
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const title = elements.title.value.trim();
    if (!title) {
      elements.error.textContent = text.title_required;
      elements.error.hidden = false;
      return;
    }
    const subtasks = [...elements.subtaskList.querySelectorAll('.subtask-row')].map((row) => {
      const input = row.querySelector('input[type="text"]');
      return {
        ...(input.dataset.subtaskId ? { id: Number(input.dataset.subtaskId) } : {}),
        title: input.value.trim(),
        done: row.querySelector('input[type="checkbox"]').checked,
      };
    }).filter((item) => item.title);
    const values = {
      title,
      owner: elements.owner.value,
      notes: elements.notes.value,
      due_date: elements.dueDate.value || null,
      subtasks,
    };
    const editing = state.editing;
    try {
      await api(editing ? endpoint(body.dataset.cardUrlTemplate, editing.id) : body.dataset.cardsUrl, {
        method: editing ? 'PUT' : 'POST',
        body: JSON.stringify(editing ? values : { ...values, column_id: Number(backdrop.dataset.columnId) }),
      });
      closeDialog();
      await loadBoard();
    } catch {
      elements.error.textContent = text.api_error;
      elements.error.hidden = false;
    }
  });

  document.getElementById('delete-button').addEventListener('click', async () => {
    if (!state.editing || !window.confirm(text.delete_confirm)) return;
    try {
      await api(endpoint(body.dataset.cardUrlTemplate, state.editing.id), { method: 'DELETE' });
      closeDialog();
      await loadBoard();
    } catch {
      elements.error.textContent = text.api_error;
      elements.error.hidden = false;
    }
  });

  render();
  loadBoard().catch(reportRefreshError);
  window.setInterval(() => {
    if (document.visibilityState === 'visible') loadBoard().catch(reportRefreshError);
  }, 30000);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') loadBoard().catch(reportRefreshError);
  });
})();
