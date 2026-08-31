// ==========================================================================
// Level 1: Student Utility Studio Functions
// ==========================================================================

function loadSampleSummarizeText() {
  const sample = `Attention Is All You Need (Transformer Architecture Notes):
The Transformer model relies entirely on self-attention mechanisms to compute representations of its input and output without using sequence-aligned RNNs or convolution. The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. 

The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder. Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions. Positional encodings are added to the input embeddings at the bottoms of the encoder and decoder stacks to inject information about the relative or absolute position of the tokens in the sequence.`;
  document.getElementById('l1-sum-input').value = sample;
  showToast('Sample lecture notes loaded.', 'info');
}

function loadSampleQuizText() {
  const sample = `Vector Embeddings and Semantic Search in AI Engineering:
Dense vector embeddings map words, phrases, or entire documents into a continuous high-dimensional geometric vector space. Unlike traditional keyword search (such as BM25 or TF-IDF) which relies strictly on exact lexical matches, vector search calculates mathematical proximity using Cosine Similarity or Euclidean Distance.

In a modern Retrieval-Augmented Generation (RAG) system, long documents are chunked hierarchically with sliding window overlap. When a user submits a query, it is embedded into the same vector space, and the top-K nearest document chunks are retrieved to ground the generative large language model's answer. Cross-encoder rerankers and faithfulness guardrails are frequently added to verify source accuracy and eliminate hallucinations.`;
  document.getElementById('l1-quiz-input').value = sample;
  showToast('Sample study material loaded.', 'info');
}

// 1. Summarizer
async function handleSummarizeNotes() {
  const content = document.getElementById('l1-sum-input').value.trim();
  const style = document.getElementById('l1-sum-style').value;
  const audience = document.getElementById('l1-sum-audience').value;
  const btn = document.getElementById('l1-sum-btn');
  const outputBox = document.getElementById('l1-sum-output');

  if (content.length < 10) {
    showToast('Please enter at least 10 characters of study notes.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Synthesizing Summary...';
  outputBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 60px;">Analyzing semantic hierarchy and formatting summary...</p>';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level1/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: content,
        style: style,
        target_audience: audience,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Summarization failed');

    outputBox.innerHTML = marked.parse(data.result);
    document.getElementById('l1-sum-metrics').innerHTML = `⏱️ ${data.processing_time_ms}ms &bull; ~${data.tokens_estimated} tokens`;
    
    // Show prompt template
    document.getElementById('l1-sum-prompt-collapse').style.display = 'block';
    document.getElementById('l1-sum-prompt-text').textContent = data.raw_prompt_used;

    showToast('Summary successfully generated!', 'success');
  } catch (err) {
    outputBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="play"></i> Generate Structured Summary';
    if (window.lucide) lucide.createIcons();
  }
}

// 2. Interactive Quiz & Flashcards Generator
let currentQuizData = null;
let userQuizScore = 0;
let answeredCount = 0;

async function handleGenerateQuiz() {
  const content = document.getElementById('l1-quiz-input').value.trim();
  const difficulty = document.getElementById('l1-quiz-diff').value;
  const numQuestions = parseInt(document.getElementById('l1-quiz-num').value);
  const btn = document.getElementById('l1-quiz-btn');
  const outputBox = document.getElementById('l1-quiz-output');

  if (content.length < 15) {
    showToast('Please provide at least 15 characters of study material.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating Interactive Assessment...';
  outputBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 60px;">Creating verified MCQs, options, and flashcards...</p>';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level1/generate-quiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: content,
        difficulty: difficulty,
        num_questions: numQuestions,
        include_flashcards: true,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Quiz generation failed');

    currentQuizData = data;
    userQuizScore = 0;
    answeredCount = 0;

    renderInteractiveQuiz(data);
    showToast('Assessment ready! Test your knowledge.', 'success');
  } catch (err) {
    outputBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles"></i> Generate Interactive Quiz & Flashcards';
    if (window.lucide) lucide.createIcons();
  }
}

function renderInteractiveQuiz(data) {
  const container = document.getElementById('l1-quiz-output');
  const scoreBadge = document.getElementById('l1-quiz-score-badge');
  scoreBadge.style.display = 'inline-flex';
  scoreBadge.textContent = `Score: 0 / ${data.questions.length}`;

  let html = `
    <div style="margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--card-border);">
      <h3 style="color: var(--key-navy); font-size: 1.1rem;">${data.title}</h3>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">${data.summary_of_material}</p>
    </div>
  `;

  // Render Questions
  data.questions.forEach((q, qIndex) => {
    html += `
      <div class="quiz-card" id="quiz-card-${qIndex}">
        <p style="font-weight: 700; font-size: 0.95rem; color: var(--key-navy);">
          Question ${qIndex + 1}: ${q.question}
        </p>
        <div style="margin-top: 10px;">
          ${q.options.map((opt, optIndex) => `
            <button class="quiz-option" id="q-${qIndex}-opt-${optIndex}" onclick="selectQuizAnswer(${qIndex}, ${optIndex}, ${q.correct_option})">
              <strong>${String.fromCharCode(65 + optIndex)}.</strong> ${opt}
            </button>
          `).join('')}
        </div>
        <div id="q-${qIndex}-explanation" style="display: none; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 0.85rem; background: var(--bg-cream);">
          <strong>💡 Explanation:</strong> ${q.explanation}
        </div>
      </div>
    `;
  });

  // Render Flashcards Carousel if present
  if (data.flashcards && data.flashcards.length > 0) {
    html += `
      <div style="margin-top: 24px;">
        <h4 style="color: var(--key-navy); margin-bottom: 12px;"><i data-lucide="layers"></i> High-Yield Study Flashcards</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
          ${data.flashcards.map(f => `
            <div class="flashcard-box">
              <div class="flashcard-term">${f.term}</div>
              <div class="flashcard-def">${f.definition}</div>
              ${f.mnemonic ? `<div style="margin-top: 8px; font-size: 0.75rem; color: var(--key-blue); font-weight: 600;">⚡ Mnemonic: ${f.mnemonic}</div>` : ''}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

function selectQuizAnswer(qIndex, selectedOpt, correctOpt) {
  const card = document.getElementById(`quiz-card-${qIndex}`);
  if (card.dataset.answered === 'true') return; // Prevent multiple clicks

  card.dataset.answered = 'true';
  answeredCount++;

  const selectedBtn = document.getElementById(`q-${qIndex}-opt-${selectedOpt}`);
  const correctBtn = document.getElementById(`q-${qIndex}-opt-${correctOpt}`);

  if (selectedOpt === correctOpt) {
    userQuizScore++;
    selectedBtn.classList.add('selected-correct');
  } else {
    selectedBtn.classList.add('selected-wrong');
    correctBtn.classList.add('selected-correct');
  }

  // Show explanation
  document.getElementById(`q-${qIndex}-explanation`).style.display = 'block';

  // Update Score badge
  const scoreBadge = document.getElementById('l1-quiz-score-badge');
  scoreBadge.textContent = `Score: ${userQuizScore} / ${currentQuizData.questions.length}`;
  if (userQuizScore === currentQuizData.questions.length) {
    scoreBadge.className = 'badge-pill badge-green';
  }
}

// 3. Concept Explainer
async function handleExplainConcept() {
  const concept = document.getElementById('l1-exp-concept').value.trim();
  const depth = document.getElementById('l1-exp-depth').value;
  const includeAnalogy = document.getElementById('l1-exp-analogy').checked;
  const includeCheck = document.getElementById('l1-exp-check').checked;
  const btn = document.getElementById('l1-exp-btn');
  const outputBox = document.getElementById('l1-exp-output');

  if (!concept) {
    showToast('Please enter a concept name to explain.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Deconstructing Concept...';
  outputBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 60px;">Synthesizing intuitive mental models and step-by-step breakdown...</p>';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level1/explain-concept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        concept: concept,
        depth_level: depth,
        include_analogy: includeAnalogy,
        include_practice_question: includeCheck,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Concept explanation failed');

    outputBox.innerHTML = marked.parse(data.result);
    showToast('Concept breakdown generated!', 'success');
  } catch (err) {
    outputBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="zap"></i> Generate Pedagogical Breakdown';
    if (window.lucide) lucide.createIcons();
  }
}

// 4. Answer Improver
async function handleImproveAnswer() {
  const question = document.getElementById('l1-imp-question').value.trim();
  const draft = document.getElementById('l1-imp-draft').value.trim();
  const rubric = document.getElementById('l1-imp-rubric').value;
  const btn = document.getElementById('l1-imp-btn');
  const outputBox = document.getElementById('l1-imp-output');

  if (!question || !draft) {
    showToast('Please fill in both the exam question and your draft answer.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Grading & Polishing...';
  outputBox.innerHTML = '<p style="color: var(--key-blue); text-align: center; margin-top: 60px;">Evaluating against academic rubric and generating enhanced draft...</p>';

  try {
    const res = await fetch(`${APP_STATE.apiBase}/level1/improve-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        student_draft: draft,
        rubric_focus: rubric,
        api_key: APP_STATE.apiKey || null
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Answer improvement failed');

    outputBox.innerHTML = marked.parse(data.result);
    showToast('Answer feedback & polished version ready!', 'success');
  } catch (err) {
    outputBox.innerHTML = `<p style="color: var(--accent-rose);">Error: ${err.message}</p>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="award"></i> Polish Answer & Generate Rubric Feedback';
    if (window.lucide) lucide.createIcons();
  }
}
