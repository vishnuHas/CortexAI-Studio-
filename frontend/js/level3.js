// ==========================================================================
// Level 3: Production-Style Agentic RAG Assistant Functions
// ==========================================================================

async function handleExecuteProductionRag() {
  const query = document.getElementById('l3-query-input').value.trim();
  const optRewrite = document.getElementById('l3-opt-rewrite').checked;
  const optRerank = document.getElementById('l3-opt-rerank').checked;
  const optGuard = document.getElementById('l3-opt-guard').checked;

  const btn = document.getElementById('l3-exec-btn');
  const answerBox = document.getElementById('l3-answer-box');
  const timelineBox = document.getElementById('l3-timeline-box');
  const matrixBox = document.getElementById('l3-chunks-matrix');
  const citationsList = document.getElementById('l3-citations-list');
  const scoresBar = document.getElementById('l3-scores-bar');
  const totalTimeBadge = document.getElementById('l3-total-time-badge');

  if (query.length < 2) {
    showToast('Please enter an enterprise or student query.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Executing LangGraph Agentic Pipeline...';
  answerBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 50px;">Traversing agentic pipeline stages: Query Rewriter &rarr; Vector Index &rarr; Reranker &rarr; Grounded LLM &rarr; Guardrails...</p>';
  citationsList.innerHTML = '';
  scoresBar.innerHTML = '';
  matrixBox.innerHTML = '';
  totalTimeBadge.textContent = 'Processing...';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level3/query-rag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        top_k: 4,
        enable_query_rewriting: optRewrite,
        enable_reranking: optRerank,
        enable_guardrails: optGuard,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Pipeline execution failed');

    // 1. Render Answer
    answerBox.innerHTML = marked.parse(data.answer);

    // 2. Score Badges
    const faithPct = Math.round(data.faithfulness_score * 100);
    const confPct = Math.round(data.confidence_score * 100);
    scoresBar.innerHTML = `
      <span class="badge-pill badge-green"><i data-lucide="shield-check"></i> Faithfulness: ${faithPct}%</span>
      <span class="badge-pill badge-blue"><i data-lucide="award"></i> Confidence: ${confPct}%</span>
    `;

    totalTimeBadge.textContent = `Total: ${data.total_latency_ms}ms`;
    totalTimeBadge.className = 'badge-pill badge-green';

    // 3. Render Observability Timeline
    if (data.execution_timeline && data.execution_timeline.length > 0) {
      let timelineHtml = '';
      data.execution_timeline.forEach((step, idx) => {
        timelineHtml += `
          <div class="timeline-step">
            <div class="step-num">${idx + 1}</div>
            <div class="step-info">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="step-title">${step.step_name}</span>
                <span class="step-latency">${step.latency_ms} ms</span>
              </div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
                ${Object.entries(step.details).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(' &bull; ')}
              </div>
            </div>
          </div>
        `;
      });
      timelineBox.innerHTML = timelineHtml;
    }

    // 4. Render Citations
    if (data.citations && data.citations.length > 0) {
      let citHtml = '<h5 style="font-size: 0.85rem; color: var(--key-navy); margin-bottom: 8px;">📚 Source Citations & References:</h5>';
      data.citations.forEach(c => {
        citHtml += `
          <div style="background: var(--key-blue-light); border-left: 3px solid var(--key-blue); padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; margin-bottom: 6px;">
            <strong>[Chunk #${c.chunk_id}] ${c.doc_name}</strong> (Relevance: ${Math.round(c.score * 100)}%)<br>
            <span style="color: var(--text-muted);">${c.snippet}</span>
          </div>
        `;
      });
      citationsList.innerHTML = citHtml;
    }

    // 5. Render Reranked Chunk Score Matrix
    if (data.reranked_chunks && data.reranked_chunks.length > 0) {
      let matrixHtml = `
        <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem;">
          <thead>
            <tr style="border-bottom: 1px solid var(--card-border); text-align: left;">
              <th style="padding: 6px;">Rank</th>
              <th style="padding: 6px;">Chunk ID</th>
              <th style="padding: 6px;">Document</th>
              <th style="padding: 6px;">Score</th>
            </tr>
          </thead>
          <tbody>
            ${data.reranked_chunks.map((c, i) => `
              <tr style="border-bottom: 1px solid var(--card-border-subtle);">
                <td style="padding: 6px; font-weight: 700;">#${i + 1}</td>
                <td style="padding: 6px;">Chunk ${c.chunk_id}</td>
                <td style="padding: 6px; color: var(--text-muted);">${c.doc_name}</td>
                <td style="padding: 6px; font-weight: 600; color: var(--key-blue);">${Math.round(c.score * 100)}%</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
      matrixBox.innerHTML = matrixHtml;
    }

    showToast(`RAG Pipeline completed in ${data.total_latency_ms}ms`, 'success');
  } catch (err) {
    answerBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="play-circle"></i> Execute Production RAG Pipeline';
    if (window.lucide) lucide.createIcons();
  }
}
