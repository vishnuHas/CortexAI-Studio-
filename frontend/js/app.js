// ==========================================================================
// CortexAI Studio - Main Application State & Utilities
// ==========================================================================

const APP_STATE = {
  activeTab: 'level1',
  activeL1SubTab: 'summarize',
  apiKey: localStorage.getItem('cortex_nvidia_key') || '',
  modelName: localStorage.getItem('cortex_model_name') || 'meta/llama-3.2-11b-vision-instruct',
  apiBase: window.location.origin.includes('8000') || window.location.origin.includes('localhost')
    ? `${window.location.origin}/api`
    : 'http://localhost:8000/api',
  l2ActiveDocId: 'sample_arch_guide',
  l2ActiveDocName: 'AI_Architecture_Handbook.pdf'
};

// Main Tab Navigation
function switchMainTab(tabId) {
  APP_STATE.activeTab = tabId;

  // Update navbar tab active classes
  document.querySelectorAll('.nav-tab-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) activeBtn.classList.add('active');

  // Show target section
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.style.display = 'none';
    pane.classList.remove('active');
  });

  const targetPane = document.getElementById(`section-${tabId}`);
  if (targetPane) {
    targetPane.style.display = 'block';
    targetPane.classList.add('active');
  }

  // Refresh icons
  if (window.lucide) lucide.createIcons();
}

// Level 1 Sub-Tab Navigation
function switchLevel1SubTab(subTabId) {
  APP_STATE.activeL1SubTab = subTabId;

  document.querySelectorAll('.sub-tab-btn').forEach(btn => btn.classList.remove('active'));
  const activeSubBtn = document.getElementById(`l1-tab-btn-${subTabId}`);
  if (activeSubBtn) activeSubBtn.classList.add('active');

  document.querySelectorAll('.l1-subpane').forEach(pane => pane.style.display = 'none');
  const targetSubpane = document.getElementById(`l1-pane-${subTabId}`);
  if (targetSubpane) targetSubpane.style.display = 'block';

  if (window.lucide) lucide.createIcons();
}

// API Key Modal Management
function openApiKeyModal() {
  document.getElementById('modal-api-key-input').value = APP_STATE.apiKey;
  document.getElementById('modal-model-select').value = APP_STATE.modelName;
  document.getElementById('apiKeyModal').classList.add('show');
}

function closeApiKeyModal() {
  document.getElementById('apiKeyModal').classList.remove('show');
}

async function saveApiKeyConfig() {
  const key = document.getElementById('modal-api-key-input').value.trim();
  const model = document.getElementById('modal-model-select').value;

  APP_STATE.apiKey = key;
  APP_STATE.modelName = model;
  localStorage.setItem('cortex_nvidia_key', key);
  localStorage.setItem('cortex_model_name', model);

  updateNavKeyStatus();

  // Send to backend
  try {
    await fetch(`${APP_STATE.apiBase}/config/api-key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key, model_name: model })
    });
    showToast(key ? 'NVIDIA NIM API key configured!' : 'Using Offline Mock Engine Mode', 'success');
  } catch (e) {
    showToast('Saved locally in browser session.', 'info');
  }

  closeApiKeyModal();
}

function updateNavKeyStatus() {
  const statusEl = document.getElementById('nav-key-status');
  if (statusEl) {
    if (APP_STATE.apiKey) {
      statusEl.innerHTML = '<span style="color: #10B981;">●</span> NVIDIA NIM Active';
    } else {
      statusEl.innerHTML = '<span style="color: #F59E0B;">●</span> Mock Engine (Click to set key)';
    }
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  
  let iconName = 'info';
  if (type === 'success') iconName = 'check-circle';
  if (type === 'error') iconName = 'alert-triangle';

  toast.innerHTML = `<i data-lucide="${iconName}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  if (window.lucide) lucide.createIcons();

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  updateNavKeyStatus();
  if (window.lucide) lucide.createIcons();
});
