/* DocAI Pipeline — Frontend Application */

const API = '/api/v1';

// ── State ──
let activeJobs = new Map();

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initUpload();
    initQA();
    checkHealth();
    loadDocuments();
});

// ── Health ──
async function checkHealth() {
    const badge = document.getElementById('apiStatus');
    try {
        const res = await fetch(`${API}/health`);
        if (res.ok) {
            badge.textContent = '● Connected';
            badge.classList.add('connected');
        }
    } catch {
        badge.textContent = '● Offline';
    }
}

// ── Tabs ──
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`panel${capitalize(tab.dataset.tab)}`).classList.add('active');

            if (tab.dataset.tab === 'documents') loadDocuments();
        });
    });
}

function capitalize(s) {
    const map = { upload: 'Upload', documents: 'Documents', qa: 'QA' };
    return map[s] || s;
}

// ── Upload ──
function initUpload() {
    const zone = document.getElementById('dropZone');
    const input = document.getElementById('fileInput');

    zone.addEventListener('click', () => input.click());
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', () => {
        if (input.files.length) uploadFile(input.files[0]);
        input.value = '';
    });
}

async function uploadFile(file) {
    const form = new FormData();
    form.append('file', file);

    const jobCard = createJobCard(file.name, 'uploading');
    document.getElementById('jobsList').prepend(jobCard);

    try {
        const res = await fetch(`${API}/documents/upload`, { method: 'POST', body: form });
        if (!res.ok) {
            const err = await res.json();
            updateJobCard(jobCard, 'failed', err.detail || 'Upload failed');
            return;
        }
        const data = await res.json();
        updateJobCard(jobCard, 'pending', `Job: ${data.job_id.substring(0, 8)}...`);
        pollJob(data.job_id, jobCard);
    } catch (err) {
        updateJobCard(jobCard, 'failed', err.message);
    }
}

function createJobCard(name, status) {
    const card = document.createElement('div');
    card.className = 'job-card';
    card.innerHTML = `
        <div class="job-info">
            <div class="job-name">${escapeHtml(name)}</div>
            <div class="job-meta">Uploading...</div>
            <div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div>
        </div>
        <span class="job-status ${status}">${status}</span>
    `;
    return card;
}

function updateJobCard(card, status, meta, progress) {
    card.querySelector('.job-status').className = `job-status ${status}`;
    card.querySelector('.job-status').textContent = status;
    if (meta) card.querySelector('.job-meta').textContent = meta;
    if (progress !== undefined) {
        card.querySelector('.progress-fill').style.width = `${progress}%`;
    }
}

async function pollJob(jobId, card) {
    const poll = async () => {
        try {
            const res = await fetch(`${API}/jobs/${jobId}`);
            if (!res.ok) return;
            const job = await res.json();

            const stage = job.current_stage ? ` — ${job.current_stage}` : '';
            updateJobCard(card, job.status, `${job.status}${stage}`, job.progress_pct);

            if (job.status === 'completed' || job.status === 'failed') {
                if (job.status === 'failed') {
                    updateJobCard(card, 'failed', job.error_message || 'Pipeline failed');
                }
                return;
            }
            setTimeout(poll, 1500);
        } catch {
            setTimeout(poll, 3000);
        }
    };
    poll();
}

// ── Documents ──
async function loadDocuments() {
    const list = document.getElementById('docList');
    try {
        const res = await fetch(`${API}/documents`);
        if (!res.ok) return;
        const data = await res.json();

        if (!data.documents.length) {
            list.innerHTML = '<p class="empty-state">No documents yet. Upload a file to get started.</p>';
            return;
        }

        list.innerHTML = data.documents.map(doc => `
            <div class="doc-card" onclick="showDocument('${doc.id}')">
                <div>
                    <div class="job-name">${escapeHtml(doc.filename)}</div>
                    <div class="job-meta">${formatSize(doc.file_size)} · ${formatDate(doc.created_at)}</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                    ${doc.document_type ? `<span class="doc-type-badge">${doc.document_type}</span>` : ''}
                    <span class="job-status ${doc.status}">${doc.status}</span>
                </div>
            </div>
        `).join('');
    } catch {
        list.innerHTML = '<p class="empty-state">Could not load documents.</p>';
    }
}

async function showDocument(docId) {
    const list = document.getElementById('docList');
    const detail = document.getElementById('docDetail');
    const content = document.getElementById('docDetailContent');

    list.classList.add('hidden');
    detail.classList.remove('hidden');

    content.innerHTML = '<div class="spinner"></div> Loading...';

    try {
        const [docRes, extRes] = await Promise.all([
            fetch(`${API}/documents/${docId}`),
            fetch(`${API}/extraction/${docId}`),
        ]);

        const doc = await docRes.json();
        const ext = await extRes.json();

        let html = `
            <div class="detail-section">
                <h3>Document Info</h3>
                <div class="field-grid">
                    <div class="field-item"><div class="field-label">Filename</div><div class="field-value">${escapeHtml(doc.filename)}</div></div>
                    <div class="field-item"><div class="field-label">Type</div><div class="field-value">${doc.document_type || '—'}</div></div>
                    <div class="field-item"><div class="field-label">Pages</div><div class="field-value">${doc.page_count || '—'}</div></div>
                    <div class="field-item"><div class="field-label">Status</div><div class="field-value">${doc.status}</div></div>
                    <div class="field-item"><div class="field-label">Size</div><div class="field-value">${formatSize(doc.file_size)}</div></div>
                    <div class="field-item"><div class="field-label">Uploaded</div><div class="field-value">${formatDate(doc.created_at)}</div></div>
                </div>
            </div>
        `;

        if (ext.fields && ext.fields.length) {
            html += `
                <div class="detail-section">
                    <h3>Extracted Fields</h3>
                    <div class="field-grid">
                        ${ext.fields.map(f => `
                            <div class="field-item">
                                <div class="field-label">${escapeHtml(f.field_name)}</div>
                                <div class="field-value">${escapeHtml(f.field_value || '—')}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        if (doc.pages && doc.pages.length) {
            html += `
                <div class="detail-section">
                    <h3>Extracted Text</h3>
                    ${doc.pages.map(p => `
                        <div class="page-label">Page ${p.page_number} · ${p.extraction_method}${p.ocr_confidence ? ` · ${(p.ocr_confidence * 100).toFixed(0)}% confidence` : ''}</div>
                        <div class="page-text">${escapeHtml(p.text_content || '(no text)')}</div>
                    `).join('')}
                </div>
            `;
        }

        html += `
            <div class="export-btns">
                <button class="btn-outline" onclick="exportDoc('${docId}', 'json')">Export JSON</button>
                <button class="btn-outline" onclick="exportDoc('${docId}', 'csv')">Export CSV</button>
            </div>
        `;

        content.innerHTML = html;
    } catch {
        content.innerHTML = '<p class="empty-state">Failed to load document details.</p>';
    }

    document.getElementById('backToList').onclick = () => {
        detail.classList.add('hidden');
        list.classList.remove('hidden');
    };
}

function exportDoc(docId, format) {
    window.open(`${API}/export/${docId}/${format}`, '_blank');
}

// ── Q&A ──
function initQA() {
    const btn = document.getElementById('qaSubmit');
    const input = document.getElementById('qaInput');

    btn.addEventListener('click', () => submitQuestion());
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitQuestion(); }
    });
}

async function submitQuestion() {
    const input = document.getElementById('qaInput');
    const results = document.getElementById('qaResults');
    const btn = document.getElementById('qaSubmit');
    const question = input.value.trim();

    if (!question) return;

    btn.disabled = true;
    btn.textContent = 'Thinking...';

    results.innerHTML = `<div class="qa-answer"><div class="spinner"></div> Searching documents and generating answer...</div>`;

    try {
        const res = await fetch(`${API}/rag/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, top_k: 5 }),
        });

        if (!res.ok) {
            const err = await res.json();
            results.innerHTML = `<div class="qa-answer"><p style="color:var(--danger)">${escapeHtml(err.detail || 'Query failed')}</p></div>`;
            return;
        }

        const data = await res.json();
        let html = `
            <div class="qa-answer">
                <div class="qa-answer-text">${escapeHtml(data.answer)}</div>
        `;

        if (data.sources && data.sources.length) {
            html += `<div class="qa-sources-title">Sources (${data.sources.length})</div>`;
            html += data.sources.map(s => `
                <div class="source-chip">
                    <div class="source-meta">${escapeHtml(s.document_name)}${s.page_numbers ? ` · Pages: ${s.page_numbers}` : ''} · Score: ${s.score.toFixed(3)}</div>
                    <div class="source-text">${escapeHtml(s.chunk_text.substring(0, 200))}...</div>
                </div>
            `).join('');
        }

        html += '</div>';
        results.innerHTML = html;
    } catch (err) {
        results.innerHTML = `<div class="qa-answer"><p style="color:var(--danger)">Error: ${escapeHtml(err.message)}</p></div>`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Ask';
    }
}

// ── Helpers ──
function escapeHtml(s) {
    if (!s) return '';
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function formatDate(iso) {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
