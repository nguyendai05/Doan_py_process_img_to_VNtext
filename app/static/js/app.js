// =======================
// State
// =======================
const state = {
    mode: 'single',
    user: null,
    selectedFiles: [],
    originalImages: [],
    textBlocks: [],
    selectedText: '',
    works: []
};

// =======================
// DOM Elements
// =======================
const elements = {
    authSection: document.getElementById('auth-section'),
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    processBtn: document.getElementById('process-btn'),
    previewSection: document.getElementById('preview-section'),
    imagePreview: document.getElementById('image-preview'),
    textBlocks: document.getElementById('text-blocks'),
    toolsPanel: document.getElementById('tools-panel'),
    selectedCharCount: document.getElementById('selected-char-count'),
    workList: document.getElementById('work-list'),
    modalOverlay: document.getElementById('modal-overlay'),
    modalContent: document.getElementById('modal-content')
};

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initUpload();
    initModeSwitch();
    initTools();
    loadWorks();
});

// =======================
// Helpers
// =======================
function closeModal() {
    elements.modalOverlay.classList.add('hidden');
}
elements.modalOverlay?.addEventListener('click', (e) => {
    if (e.target === elements.modalOverlay) closeModal();
});

function showLoadingModal(message) {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>⏳ Đang xử lý...</h3>
        </div>
        <div style="padding: 2rem; text-align: center;">
            <p>${message}</p>
            <div class="loading-spinner"></div>
        </div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

function showResultModal(title, content) {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>${title}</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="result-panel">${content}</div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

function downloadTextAs(filename, text) {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function getLanguageName(code) {
    const names = {
        'vi': '🇻🇳 Tiếng Việt',
        'en': '🇬🇧 English',
        'ja': '🇯🇵 日本語',
        'ko': '🇰🇷 한국어',
        'zh-CN': '🇨🇳 中文',
        'fr': '🇫🇷 Français',
        'de': '🇩🇪 Deutsch',
        'es': '🇪🇸 Español'
    };
    return names[code] || code;
}

function getStyleName(style) {
    const names = {
        'general': 'Bình thường',
        'cheerful': 'Vui vẻ',
        'sad': 'Buồn',
        'angry': 'Giận dữ',
        'terrified': 'Sợ hãi',
        'shouting': 'Hét',
        'whispering': 'Thì thầm',
        'newscast': 'Đọc tin',
        'customer-service': 'Chăm sóc khách hàng',
        'assistant': 'Trợ lý'
    };
    return names[style] || style;
}

function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, (c) => ({
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
}

// =======================
// Auth
// =======================
function initAuth() { checkAuth(); }

async function checkAuth() {
    try {
        const res = await fetch('/api/auth/me');
        if (res.ok) {
            const data = await res.json();
            state.user = data.user;
            renderAuthSection();
            loadWorks();
        } else {
            state.user = null;
            renderAuthSection();
        }
    } catch (e) {
        state.user = null;
        renderAuthSection();
    }
}

function renderAuthSection() {
    if (!elements.authSection) return;
    if (state.user) {
        elements.authSection.innerHTML = `
            <div class="user-info">
                <span class="user-email">${state.user.email}</span>
                <button class="btn btn-secondary btn-sm" onclick="logout()">Đăng xuất</button>
            </div>
        `;
    } else {
        elements.authSection.innerHTML = `
            <div class="auth-buttons">
                <button class="btn btn-secondary btn-sm" onclick="showLoginModal()">Đăng nhập</button>
                <button class="btn btn-primary btn-sm" onclick="showRegisterModal()">Đăng ký</button>
            </div>
        `;
    }
}

function showLoginModal() {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>Đăng nhập</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleLogin(event)">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Mật khẩu</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%">Đăng nhập</button>
        </form>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

function showRegisterModal() {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>Đăng ký</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleRegister(event)">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Mật khẩu</label>
                <input type="password" name="password" minlength="6" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%">Đăng ký</button>
        </form>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const data = { email: form.email.value, password: form.password.value };

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            state.user = result.user;
            renderAuthSection();
            loadWorks();
            closeModal();
        } else alert(result.error || 'Đăng nhập thất bại');
    } catch (e) {
        alert('Lỗi kết nối');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const data = { email: form.email.value, password: form.password.value };

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            alert('Đăng ký thành công! Vui lòng đăng nhập.');
            showLoginModal();
        } else alert(result.error || 'Đăng ký thất bại');
    } catch (e) {
        alert('Lỗi kết nối');
    }
}

async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    state.user = null;
    state.works = [];
    renderAuthSection();
    renderWorkList();
}

// =======================
// Upload
// =======================
function initUpload() {
    if (!elements.uploadArea || !elements.fileInput || !elements.processBtn) return;

    const uploadArea = elements.uploadArea;
    const fileInput = elements.fileInput;

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    elements.processBtn.addEventListener('click', processOCR);
}

function handleFiles(files) {
    const maxFiles = state.mode === 'single' ? 1 : 5;
    const validFiles = Array.from(files)
        .filter(f => ['image/jpeg', 'image/png', 'image/jpg'].includes(f.type))
        .slice(0, maxFiles);

    if (validFiles.length === 0) {
        alert('Vui lòng chọn file ảnh hợp lệ (JPG, PNG)');
        return;
    }

    state.selectedFiles = validFiles;
    state.originalImages = validFiles;
    renderPreview();
    elements.processBtn.disabled = false;
}

function renderPreview() {
    if (!elements.imagePreview || !elements.previewSection) return;

    elements.imagePreview.innerHTML = '';
    state.selectedFiles.forEach((file, idx) => {
        const div = document.createElement('div');
        div.className = 'preview-item';
        div.innerHTML = `
            <img src="${URL.createObjectURL(file)}" alt="Preview">
            <button class="remove-btn" onclick="removeFile(${idx})">&times;</button>
        `;
        elements.imagePreview.appendChild(div);
    });
    elements.previewSection.classList.remove('hidden');
}

function removeFile(idx) {
    state.selectedFiles.splice(idx, 1);
    if (state.selectedFiles.length === 0) {
        elements.previewSection.classList.add('hidden');
        elements.processBtn.disabled = true;
    } else renderPreview();
}

// =======================
// Mode
// =======================
function initModeSwitch() {
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.mode = btn.dataset.mode;
            if (elements.fileInput) elements.fileInput.multiple = state.mode === 'multi';
            state.selectedFiles = [];
            if (elements.previewSection) elements.previewSection.classList.add('hidden');
            if (elements.processBtn) elements.processBtn.disabled = true;
        });
    });
}

// =======================
// OCR
// =======================
async function processOCR() {
    if (!state.user) {
        alert('Vui lòng đăng nhập để sử dụng OCR');
        showLoginModal();
        return;
    }
    if (state.selectedFiles.length === 0) return;

    elements.processBtn.disabled = true;
    elements.processBtn.textContent = '⏳ Đang xử lý...';

    const formData = new FormData();

    if (state.mode === 'single') {
        formData.append('image', state.selectedFiles[0]);
        try {
            const res = await fetch('/api/ocr/single', { method: 'POST', body: formData });
            const result = await res.json();
            if (result.success) addTextBlock(result.processed_text, state.selectedFiles[0].name, state.selectedFiles[0]);
            else alert(result.error || 'OCR thất bại');
        } catch (e) { alert('Lỗi kết nối'); }
    } else {
        state.selectedFiles.forEach(f => formData.append('images', f));
        try {
            const res = await fetch('/api/ocr/multi', { method: 'POST', body: formData });
            const result = await res.json();
            if (result.success) {
                result.results.forEach((r, idx) => {
                    if (r.success) addTextBlock(r.processed_text, r.filename, state.selectedFiles[idx]);
                });
            } else alert(result.error || 'OCR thất bại');
        } catch (e) { alert('Lỗi kết nối'); }
    }

    elements.processBtn.disabled = false;
    elements.processBtn.textContent = '🚀 Xử lý OCR';
}

// =======================
// Blocks
// =======================
function addTextBlock(text, title, imageFile) {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    state.textBlocks.push({ id, text, title, imageFile: imageFile || null });
    renderTextBlocks();
}

function renderTextBlocks() {
    if (!elements.textBlocks) return;

    elements.textBlocks.innerHTML = '';
    state.textBlocks.forEach(block => {
        const div = document.createElement('div');
        div.className = 'text-block';

        const summarizeBtn = block.imageFile
            ? `<button class="btn btn-secondary btn-sm" onclick="summarizeImage(${block.id})">🤖 Tóm tắt AI</button>` : '';

        div.innerHTML = `
            <div class="text-block-header">
                <span class="text-block-title">📄 ${block.title}</span>
                <div class="text-block-actions">
                    <button class="btn btn-secondary btn-sm" onclick="copyText(${block.id})">📋 Copy</button>
                    <button class="btn btn-secondary btn-sm" onclick="saveToWork(${block.id}, 'ocr')">💾 Save</button>
                    <button class="btn btn-secondary btn-sm" onclick="downloadBlockText(${block.id})">⬇️ Download</button>
                    ${summarizeBtn}
                    <button class="btn btn-secondary btn-sm" onclick="removeBlock(${block.id})">🗑️</button>
                    <button class="btn btn-primary btn-sm" onclick="openSpeakMenu(${block.id})">🎤translate or convert</button>
                </div>
            </div>
            <div class="text-block-content" data-id="${block.id}" onmouseup="handleTextSelect()">${block.text}</div>
        `;
        elements.textBlocks.appendChild(div);
    });
}

function copyText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (!block) return;
    navigator.clipboard.writeText(block.text);
    alert('Đã copy!');
}

function downloadBlockText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (!block) return;
    downloadTextAs(`${block.title}.txt`, block.text);
}

function removeBlock(id) {
    state.textBlocks = state.textBlocks.filter(b => b.id !== id);
    renderTextBlocks();
}


async function saveToWork(id, source_type = 'ocr', overrideTitle = null, overrideContent = null) {
    const block = state.textBlocks.find(b => b.id === id);
    if (!block) return;

    const title = overrideTitle || block.title;
    const content = overrideContent != null ? overrideContent : block.text;

    try {
        const res = await fetch('/api/works', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, source_type })
        });
        if (res.ok) {
            alert('Đã lưu!');
            loadWorks();
        } else {
            const r = await res.json().catch(() => ({}));
            alert(r.error || 'Lỗi lưu');
        }
    } catch (e) {
        alert('Lỗi lưu');
    }
}

function handleTextSelect() {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    if (text.length > 0 && text.length <= 2000) {
        state.selectedText = text;
        if (elements.selectedCharCount) elements.selectedCharCount.textContent = text.length;
        if (elements.toolsPanel) elements.toolsPanel.classList.remove('hidden');
    } else {
        if (elements.toolsPanel) elements.toolsPanel.classList.add('hidden');
    }
}

function initTools() {
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tool = btn.dataset.tool;
            if (tool === 'tts') runTTS();
            else if (tool === 'translate') showTranslateModal();
            else if (tool === 'research') showResearchModal();
        });
    });
}

async function runTTS() {
    if (!state.selectedText) return;
    try {
        const res = await fetch('/api/tools/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: state.selectedText, language: 'vi' })
        });
        const result = await res.json();
        if (result.success) {
            showResultModal('Text-to-Speech', `<audio controls src="${result.audio_url}" style="width:100%"></audio>`);
        } else alert(result.error);
    } catch (e) {
        alert('Lỗi TTS');
    }
}

function showTranslateModal() {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🌐 Dịch văn bản</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="form-group">
            <label>Ngôn ngữ đích</label>
            <select id="dest-lang">
                <option value="en">English</option>
                <option value="vi">Tiếng Việt</option>
                <option value="ja">日本語</option>
                <option value="ko">한국어</option>
                <option value="zh-CN">中文</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
                <option value="es">Español</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="runTranslateSelected()">Dịch</button>
        <div id="translate-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function runTranslateSelected() {
    const destLang = document.getElementById('dest-lang').value;
    try {
        const res = await fetch('/api/tools/translate-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: state.selectedText, dest_lang: destLang })
        });
        const result = await res.json();
        document.getElementById('translate-result').innerHTML = result.success
            ? `<p><strong>Kết quả:</strong></p><div style="white-space:pre-wrap">${result.translated_text}</div>`
            : `<p style="color:red">${result.error}</p>`;
    } catch (e) {
        alert('Lỗi dịch');
    }
}

function showResearchModal() {
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>📚 Research</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="form-group">
            <label>Loại phân tích</label>
            <select id="research-type">
                <option value="summary">Tóm tắt</option>
                <option value="keywords">Từ khóa</option>
                <option value="questions">Câu hỏi ôn tập</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="runResearch()">Phân tích</button>
        <div id="research-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function runResearch() {
    const type = document.getElementById('research-type').value;
    try {
        const res = await fetch('/api/tools/research', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: state.selectedText, type })
        });
        const result = await res.json();
        let html = '';
        if (Array.isArray(result.result)) {
            html = '<ul>' + result.result.map(r => `<li>${r}</li>`).join('') + '</ul>';
        } else html = `<p>${result.result}</p>`;
        document.getElementById('research-result').innerHTML = html;
    } catch (e) {
        alert('Lỗi phân tích');
    }
}

async function loadWorks() {
    if (!elements.workList) return;

    if (!state.user) {
        elements.workList.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.875rem">Đăng nhập để xem lịch sử</p>';
        return;
    }

    try {
        const res = await fetch('/api/works');
        const data = await res.json();
        state.works = data.works || [];
        renderWorkList();
    } catch (e) {}
}

function renderWorkList() {
    if (!elements.workList) return;
    if (state.works.length === 0) {
        elements.workList.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.875rem">Chưa có work nào</p>';
        return;
    }

    elements.workList.innerHTML = state.works.map(w => `
        <div class="work-item" onclick="loadWork(${w.id})">
            <div class="work-item-title">${w.title}</div>
            <div class="work-item-meta">${w.block_count} blocks • ${new Date(w.created_at).toLocaleDateString('vi')}</div>
        </div>
    `).join('');
}

async function loadWork(id) {
    try {
        const res = await fetch(`/api/works/${id}`);
        const data = await res.json();
        if (data.work) {
            state.textBlocks = data.work.text_blocks.map(b => ({
                id: b.id,
                text: b.content,
                title: b.title || `Block ${b.id}`,
                imageFile: null
            }));
            renderTextBlocks();
        }
    } catch (e) {
        alert('Lỗi tải work');
    }
}


async function summarizeImage(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    showLoadingModal('Đang phân tích ảnh bằng Gemini AI...');
    try {
        const formData = new FormData();
        formData.append('image', block.imageFile);

        const res = await fetch('/api/tools/summarize-image', { method: 'POST', body: formData });
        const result = await res.json();

        if (result.success) {
            showSummaryModal(block.title, result.summary, block.imageFile);
        } else {
            alert(result.error || 'Lỗi khi tóm tắt ảnh');
            closeModal();
        }
    } catch (e) {
        alert('Lỗi kết nối: ' + e.message);
        closeModal();
    }
}

function showSummaryModal(title, summary, imageFile) {
    const imageUrl = URL.createObjectURL(imageFile);
    const safe = summary.replace(/`/g, '\\`');

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🤖 Tóm tắt nội dung ảnh</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="summary-content">
            <div class="summary-image">
                <img src="${imageUrl}" alt="${title}" style="max-width: 100%; border-radius: 8px; margin-bottom: 1rem;">
            </div>
            <div class="summary-text">
                <h4 style="margin-bottom: 1rem; color: #667eea;">📝 ${title}</h4>
                <div style="white-space: pre-wrap; line-height: 1.6;">${summary}</div>
            </div>
            <div class="summary-actions" style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
                <button class="btn btn-primary" onclick="navigator.clipboard.writeText(\`${safe}\`);alert('Đã copy!')">📋 Copy</button>
                <button class="btn btn-secondary" onclick="downloadTextAs('summary_${title}.txt', \`${safe}\`)">⬇️ Download</button>
            </div>
        </div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

function openSpeakMenu(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🛠️ Chọn chức năng</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>

        <div class="form-group">
            <label>🌍 Ngôn ngữ</label>
            <select id="menu-lang">
                <option value="en">English</option>
                <option value="vi">Tiếng Việt</option>
                <option value="ja">日本語</option>
                <option value="ko">한국어</option>
                <option value="zh-CN">中文</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
                <option value="es">Español</option>
            </select>
        </div>

        <div style="display:flex; gap:.5rem;">
            <button class="btn btn-primary" style="flex:1" onclick="openContextTranslate(${blockId})">🌐 Dịch (ngữ cảnh)</button>
            <button class="btn btn-secondary" style="flex:1" onclick="showAdvancedTTS(${blockId})">🎤 Text to mp3</button>
        </div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function openContextTranslate(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    const dest_lang = document.getElementById('menu-lang')?.value || 'en';

    showLoadingModal('Đang dịch theo ngữ cảnh...');
    try {
        const res = await fetch('/api/tools/translate-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: block.text, dest_lang })
        });
        const r = await res.json();
        if (!r.success) {
            alert(r.error || 'Dịch thất bại');
            closeModal();
            return;
        }

        const translated = r.translated_text || '';
        const safe = translated.replace(/`/g, '\\`');

        elements.modalContent.innerHTML = `
            <div class="modal-header">
                <h3>🌐 Dịch theo ngữ cảnh (${getLanguageName(dest_lang)})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>

            <div class="result-panel" style="white-space:pre-wrap; line-height:1.6;">${translated}</div>

            <div style="display:flex; gap:.5rem; margin-top:1rem;">
                <button class="btn btn-primary" onclick="saveToWork(${blockId}, 'translate', 'Translate - ${block.title}', \`${safe}\`)">💾 Save</button>
                <button class="btn btn-secondary" onclick="downloadTextAs('translate_${block.title}.txt', \`${safe}\`)">⬇️ Download</button>
            </div>
        `;
        elements.modalOverlay.classList.remove('hidden');

    } catch (e) {
        alert('Lỗi kết nối');
        closeModal();
    }
}

async function showAdvancedTTS(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    const chosenLang = document.getElementById('menu-lang')?.value || 'vi';

    const voicesRes = await fetch('/api/tools/tts/voices');
    const voicesData = await voicesRes.json();

    const voices = voicesData.voices;

    window.ttsVoicesData = voices;

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🎤 Text to Speech (MP3)</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>

        <div class="tts-config">
            <div class="form-group">
                <label>🌍 Ngôn ngữ</label>
                <select id="tts-lang" onchange="updateVoiceOptions()">
                    ${Object.keys(voices).map(lang => `
                        <option value="${lang}" ${lang === chosenLang ? 'selected' : ''}>${getLanguageName(lang)}</option>
                    `).join('')}
                </select>
            </div>

            <div class="form-group">
                <label>👤 Giới tính</label>
                <select id="tts-gender" onchange="updateVoiceList()">
                    <option value="female">Nữ</option>
                    <option value="male">Nam</option>
                </select>
            </div>

            <div class="form-group">
                <label>🎙️ Giọng</label>
                <select id="tts-voice"></select>
            </div>

            <div style="display:flex; gap:.5rem;">
                <button class="btn btn-primary" style="flex:1" onclick="generateAdvancedTTS(${blockId})">🎤 Tạo MP3</button>
                <button class="btn btn-secondary" style="flex:1; background:#10b981; border-color:#10b981; color:#fff;"
                        onclick="openHighlightSpeak(${blockId})">🖍️ Highlight</button>
            </div>

            <div id="tts-result" class="tts-result" style="margin-top: 1.5rem;"></div>
        </div>
    `;

    elements.modalOverlay.classList.remove('hidden');
    updateVoiceOptions();
}

function updateVoiceOptions() {
    const lang = document.getElementById('tts-lang').value;
    document.getElementById('tts-gender').value = 'female';
    updateVoiceList();
}

function updateVoiceList() {
    const lang = document.getElementById('tts-lang').value;
    const gender = document.getElementById('tts-gender').value;
    const voices = window.ttsVoicesData?.[lang]?.[gender] || [];
    const voiceSelect = document.getElementById('tts-voice');
    voiceSelect.innerHTML = voices.map((v, idx) => `<option value="${idx}">${v}</option>`).join('');
}

let lastTTSRequest = 0;
const TTS_COOLDOWN = 1200;

async function generateAdvancedTTS(blockId, overrideText = null) {
    const now = Date.now();
    if (now - lastTTSRequest < TTS_COOLDOWN) return null;
    lastTTSRequest = now;

    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return null;
    const text = overrideText != null ? overrideText : block.text;

    const config = {
        text,
        target_lang: document.getElementById('tts-lang').value,
        voice_gender: document.getElementById('tts-gender').value,
        voice_index: parseInt(document.getElementById('tts-voice').value, 10) || 0
    };

    const out = document.getElementById('tts-result');
    out.innerHTML = `
        <div style="text-align:center; padding: 2rem;">
            <div class="loading-spinner"></div>
            <p>Đang tạo giọng nói...</p>
        </div>
    `;

    try {
        const res = await fetch('/api/tools/advanced-tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const result = await res.json();

        if (result.success) {
            out.innerHTML = `
                <div class="tts-success">
                    <h4 style="color: #10b981; margin-bottom: 1rem;">✅ Thành công!</h4>
                    <audio controls style="width: 100%; margin-bottom: 1rem;">
                        <source src="${result.audio_url}" type="audio/mpeg">
                    </audio>
                    <div style="display:flex; gap:.5rem;">
                        <button class="btn btn-primary" onclick="downloadAudio('${result.audio_url}', '${result.filename}')">⬇️ Download MP3</button>
                        <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('${window.location.origin}${result.audio_url}');alert('Đã copy link!')">🔗 Copy link</button>
                    </div>
                </div>
            `;
            return result;
        } else {
            out.innerHTML = `<div style="color:#ef4444; padding:1rem; background:rgba(239,68,68,.1); border-radius:8px;">❌ ${result.error}</div>`;
            return null;
        }
    } catch (e) {
        out.innerHTML = `<div style="color:#ef4444;">❌ Lỗi: ${e.message}</div>`;
        return null;
    }
}

function downloadAudio(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

async function hsGenerateTTS(text, config) {
    const payload = {
        text,
        target_lang: config.target_lang || 'vi',
        voice_gender: config.voice_gender || 'female',
        voice_index: Number(config.voice_index || 0),
    };

    const res = await fetch('/api/tools/advanced-tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    return await res.json();
}

async function openHighlightSpeak(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    // snapshot config từ modal Advanced trước khi modal bị replace (NO rate/pitch/style)
    const ttsConfigSnapshot = {
        target_lang: document.getElementById('tts-lang')?.value || 'vi',
        voice_gender: document.getElementById('tts-gender')?.value || 'female',
        voice_index: parseInt(document.getElementById('tts-voice')?.value || '0', 10)
    };

    // dùng đúng ngôn ngữ đang chọn để dịch (highlight)
    const dest_lang = ttsConfigSnapshot.target_lang || 'en';

    showLoadingModal('Đang dịch theo ngữ cảnh để highlight...');
    try {
        const res = await fetch('/api/tools/translate-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: block.text, dest_lang })
        });

        const r = await res.json().catch(() => ({}));
        if (!r || !r.success) {
            closeModal();
            return;
        }

        const translated = (r.translated_text || '').trim();
        const lines = translated.split('\n').map(s => s.trim()).filter(Boolean);

        elements.modalContent.innerHTML = `
            <div class="modal-header">
                <h3>🖍️ Highlight Speak (${getLanguageName(dest_lang)})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>

            <div class="form-group">
                <div><strong>Dòng đang đọc:</strong> <span id="hs-current-line">-</span></div>
            </div>

            <div id="hs-lines" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; max-height:45vh; overflow:auto;">
                ${lines.map((l, i) => `<div class="hs-line" data-idx="${i}" style="padding:.35rem 0;">${escapeHtml(l)}</div>`).join('')}
            </div>

            <div style="display:flex; gap:.5rem; margin-top:1rem;">
                <button class="btn btn-primary" onclick="hsPlay()">▶️ Phát + Highlight</button>
                <button class="btn btn-secondary" onclick="hsDownloadVideo()">⬇️ Download video</button>
            </div>

            <div id="hs-audio-wrap" class="result-panel" style="margin-top:1rem;"></div>
        `;
        elements.modalOverlay.classList.remove('hidden');

        window.__hs = {
            blockId,
            dest_lang,
            translated,
            lines,
            ttsConfig: ttsConfigSnapshot, // chỉ còn target_lang/voice_gender/voice_index
            audioEl: null,
            lineTimes: [],
            recordedChunks: [],
            canvas: null,
            ctx: null,
            raf: null
        };

    } catch (e) {
        closeModal();
    }
}

async function hsPlay() {
    const hs = window.__hs;
    if (!hs) return;

    const ttsResult = await hsGenerateTTS(hs.translated, hs.ttsConfig);
    if (!ttsResult || !ttsResult.success || !ttsResult.audio_url) {
        alert(ttsResult?.error || 'TTS thất bại');
        return;
    }

    const audioWrap = document.getElementById('hs-audio-wrap');
    audioWrap.innerHTML = `
        <audio id="hs-audio" controls style="width:100%;">
            <source src="${ttsResult.audio_url}" type="audio/mpeg">
        </audio>
    `;

    const audio = document.getElementById('hs-audio');
    hs.audioEl = audio;

    audio.onloadedmetadata = () => {
        const total = audio.duration || 1;
        const weights = hs.lines.map(l => Math.max(10, l.length));
        const sum = weights.reduce((a,b)=>a+b,0) || 1;
        let acc = 0;
        hs.lineTimes = weights.map(w => {
            const start = acc;
            const dur = total * (w / sum);
            acc += dur;
            return { start, end: start + dur };
        });
    };

    audio.ontimeupdate = () => {
        const t = audio.currentTime || 0;
        const idx = hs.lineTimes.findIndex(x => t >= x.start && t < x.end);
        hsSetLine(idx);
    };

    audio.onended = () => hsSetLine(-1);
    audio.play();
}

function hsSetLine(idx) {
    const hs = window.__hs;
    const label = document.getElementById('hs-current-line');
    const linesEl = document.getElementById('hs-lines');
    if (!hs || !linesEl) return;

    const els = linesEl.querySelectorAll('.hs-line');
    els.forEach(el => {
        const i = parseInt(el.dataset.idx, 10);
        el.style.color = '#1e293b';
        el.style.fontWeight = '400';
        if (idx >= 0 && i < idx) {
            el.style.color = '#2563eb'; // done blue
        }
        if (i === idx) {
            el.style.color = '#ef4444'; // current red
            el.style.fontWeight = '700';
            el.scrollIntoView({ block: 'nearest' });
        }
    });

    if (idx >= 0) label.textContent = hs.lines[idx] || '-';
    else label.textContent = '-';
}

async function hsDownloadVideo() {
    const hs = window.__hs;
    if (!hs || !hs.audioEl) {
        alert('Bạn phải bấm phát trước để có audio.');
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = 900;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');
    hs.canvas = canvas;
    hs.ctx = ctx;

    const stream = canvas.captureStream(30);

    let audioStream = null;
    try {
        if (hs.audioEl.captureStream) audioStream = hs.audioEl.captureStream();
        else if (hs.audioEl.mozCaptureStream) audioStream = hs.audioEl.mozCaptureStream();
    } catch (e) {}

    if (!audioStream) {
        alert('Trình duyệt không hỗ trợ capture audio stream (Chrome thường OK).');
        return;
    }

    const combined = new MediaStream([
        ...stream.getVideoTracks(),
        ...audioStream.getAudioTracks()
    ]);

    const recorder = new MediaRecorder(combined, { mimeType: 'video/webm' });
    hs.recordedChunks = [];
    recorder.ondataavailable = (e) => { if (e.data.size > 0) hs.recordedChunks.push(e.data); };
    recorder.onstop = () => {
        const blob = new Blob(hs.recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'highlight_speak.webm';
        a.click();
        URL.revokeObjectURL(url);
    };

    const render = () => {
        const curIdx = (() => {
            const t = hs.audioEl.currentTime || 0;
            const idx = hs.lineTimes.findIndex(x => t >= x.start && t < x.end);
            return idx;
        })();

        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0f172a';
        ctx.font = '22px Segoe UI';
        ctx.fillText('Highlight Speak', 30, 40);

        ctx.font = '18px Segoe UI';
        let y = 90;
        const maxLinesOnScreen = 20;

        const start = Math.max(0, curIdx - 5);
        const end = Math.min(hs.lines.length, start + maxLinesOnScreen);

        for (let i = start; i < end; i++) {
            if (curIdx >= 0 && i < curIdx) ctx.fillStyle = '#2563eb';
            else if (i === curIdx) ctx.fillStyle = '#ef4444';
            else ctx.fillStyle = '#1e293b';

            ctx.fillText(hs.lines[i], 30, y);
            y += 26;
        }

        hs.raf = requestAnimationFrame(render);
    };

    recorder.start();
    render();

    const stopAll = () => {
        try { cancelAnimationFrame(hs.raf); } catch(e){}
        if (recorder.state !== 'inactive') recorder.stop();
        hs.audioEl.removeEventListener('ended', stopAll);
    };
    hs.audioEl.addEventListener('ended', stopAll);

    if (hs.audioEl.paused) hs.audioEl.play();
}
