// ==========================================================================
// Level 2: Document-Based Q&A Assistant Functions
// ==========================================================================

// Drag & drop dropzone listeners
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('l2-dropzone');
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      uploadL2File(files[0]);
    }
  }, false);
});

function handleL2FileUpload(event) {
  const file = event.target.files[0];
  if (file) {
    uploadL2File(file);
  }
}

async function uploadL2File(file) {
  const formData = new FormData();
  formData.append('file', file);

  const statusBadge = document.getElementById('l2-doc-status-badge');
  statusBadge.className = 'badge-pill badge-blue';
  statusBadge.innerHTML = '<span class="spinner"></span> Indexing...';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level2/upload`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');

    APP_STATE.l2ActiveDocId = data.doc_id;
    APP_STATE.l2ActiveDocName = data.filename;

    document.getElementById('l2-active-doc-name').textContent = data.filename;
    statusBadge.className = 'badge-pill badge-green';
    statusBadge.textContent = 'Active & Indexed';

    document.getElementById('l2-chunk-count-badge').textContent = `Chunks: ${data.total_chunks}`;
    renderL2Chunks(data.chunk_sample);

    showToast(`Indexed ${data.filename} (${data.total_chunks} chunks)`, 'success');
  } catch (err) {
    statusBadge.className = 'badge-pill badge-amber';
    statusBadge.textContent = 'Upload Error';
    showToast(`Error: ${err.message}`, 'error');
  }
}

function renderL2Chunks(chunks) {
  const container = document.getElementById('l2-chunk-inspector');
  if (!chunks || chunks.length === 0) {
    container.innerHTML = '<p style="font-size: 0.85rem; color: var(--text-muted);">No chunks available to display.</p>';
    return;
  }

  let html = '';
  chunks.forEach(chunk => {
    html += `
      <div class="chunk-item">
        <div class="chunk-meta">
          <span>Chunk #${chunk.chunk_id}</span>
          <span>Chars ${chunk.start_char}-${chunk.end_char}</span>
        </div>
        <p style="color: var(--text-muted); font-size: 0.82rem; line-height: 1.5;">${chunk.text}</p>
      </div>
    `;
  });
  container.innerHTML = html;
}

function setL2Query(text) {
  document.getElementById('l2-query-input').value = text;
  handleL2Query();
}

async function handleL2Query() {
  const query = document.getElementById('l2-query-input').value.trim();
  const btn = document.getElementById('l2-query-btn');
  const answerBox = document.getElementById('l2-answer-box');
  const chunksBox = document.getElementById('l2-matched-chunks-box');
  const confBadge = document.getElementById('l2-confidence-badge');

  if (query.length < 3) {
    showToast('Please enter a question with at least 3 characters.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>';
  answerBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 40px;">Searching vector memory and extracting grounded context...</p>';
  chunksBox.innerHTML = '';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level2/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doc_id: APP_STATE.l2ActiveDocId,
        query: query,
        top_k: 3,
        strict_grounding: true,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Query failed');

    answerBox.innerHTML = marked.parse(data.answer);

    // Confidence badge
    confBadge.style.display = 'inline-flex';
    const confPct = Math.round(data.confidence_score * 100);
    confBadge.textContent = `Confidence: ${confPct}%`;
    confBadge.className = confPct > 80 ? 'badge-pill badge-green' : 'badge-pill badge-blue';

    // Render retrieved chunks
    if (data.retrieved_chunks && data.retrieved_chunks.length > 0) {
      let chunksHtml = '';
      data.retrieved_chunks.forEach(c => {
        const scorePct = Math.round(c.score * 100);
        chunksHtml += `
          <div class="chunk-item">
            <div class="chunk-meta">
              <span style="color: var(--key-blue);">Chunk #${c.chunk_id}</span>
              <span class="badge-pill badge-blue" style="font-size: 0.7rem;">Sim Score: ${scorePct}%</span>
            </div>
            <p style="color: var(--text-muted); font-size: 0.8rem;">${c.text}</p>
          </div>
        `;
      });
      chunksBox.innerHTML = chunksHtml;
    } else {
      chunksBox.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-muted);">No matching chunks retrieved.</p>';
    }

    showToast(`Query answered in ${data.execution_time_ms}ms`, 'success');
  } catch (err) {
    answerBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="send"></i> Ask';
    if (window.lucide) lucide.createIcons();
  }
}
