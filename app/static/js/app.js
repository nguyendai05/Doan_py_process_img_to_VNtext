// State
const state = {
    mode: 'single', // single or multi
    user: null,
    selectedFiles: [],
    originalImages: [], // THÊM: Lưu ảnh gốc để gửi cho Gemini
    textBlocks: [],
    selectedText: '',
    works: []
};

// DOM Elements
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initUpload();
    initModeSwitch();
    initTools();
    loadWorks();
});

// Auth Functions
function initAuth() {
    checkAuth();
}

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
    const data = {
        email: form.email.value,
        password: form.password.value
    };

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
        } else {
            alert(result.error || 'Đăng nhập thất bại');
        }
    } catch (e) {
        alert('Lỗi kết nối');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
        email: form.email.value,
        password: form.password.value
    };

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
        } else {
            alert(result.error || 'Đăng ký thất bại');
        }
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

function closeModal() {
    elements.modalOverlay.classList.add('hidden');
}

// Upload Functions
function initUpload() {
    const uploadArea = elements.uploadArea;
    const fileInput = elements.fileInput;

    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

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
    state.originalImages = validFiles; // LƯU ẢNH GỐC
    renderPreview();
    elements.processBtn.disabled = false;
}

function renderPreview() {
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
    } else {
        renderPreview();
    }
}

// Mode Switch
function initModeSwitch() {
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.mode = btn.dataset.mode;
            elements.fileInput.multiple = state.mode === 'multi';
            // Clear current selection
            state.selectedFiles = [];
            elements.previewSection.classList.add('hidden');
            elements.processBtn.disabled = true;
        });
    });
}

// OCR Processing
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
            const res = await fetch('/api/ocr/single', {
                method: 'POST',
                body: formData
            });
            const result = await res.json();
            if (result.success) {
                addTextBlock(result.processed_text, state.selectedFiles[0].name, state.selectedFiles[0]); // TRUYỀN FILE
            } else {
                alert(result.error || 'OCR thất bại');
            }
        } catch (e) {
            alert('Lỗi kết nối');
        }
    } else {
        state.selectedFiles.forEach(f => formData.append('images', f));
        try {
            const res = await fetch('/api/ocr/multi', {
                method: 'POST',
                body: formData
            });
            const result = await res.json();
            if (result.success) {
                result.results.forEach((r, idx) => {
                    if (r.success) {
                        addTextBlock(r.processed_text, r.filename, state.selectedFiles[idx]); // TRUYỀN FILE
                    }
                });
            } else {
                alert(result.error || 'OCR thất bại');
            }
        } catch (e) {
            alert('Lỗi kết nối');
        }
    }

    elements.processBtn.disabled = false;
    elements.processBtn.textContent = '🚀 Xử lý OCR';
}


// Text Blocks
function addTextBlock(text, title, imageFile) {
    const id = Date.now();
    state.textBlocks.push({
        id,
        text,
        title,
        imageFile: imageFile || null  // Lưu file ảnh gốc
    });
    renderTextBlocks();
}


function renderTextBlocks() {
    elements.textBlocks.innerHTML = '';
    state.textBlocks.forEach(block => {
        const div = document.createElement('div');
        div.className = 'text-block';

        // Hiển thị nút summarize nếu có ảnh
        const summarizeBtn = block.imageFile
            ? `<button class="btn btn-secondary btn-sm" onclick="summarizeImage(${block.id})">🤖 Tóm tắt AI</button>` : '';

        div.innerHTML = `
            <div class="text-block-header">
                <span class="text-block-title">📄 ${block.title}</span>
                <div class="text-block-actions">
                    <button class="btn btn-secondary btn-sm" onclick="copyText(${block.id})">📋 Copy</button>
                    <button class="btn btn-secondary btn-sm" onclick="saveToWork(${block.id})">💾 Save</button>
                    <button class="btn btn-secondary btn-sm" onclick="downloadText(${block.id})">⬇️ Download</button>
                    ${summarizeBtn}
                    <button class="btn btn-secondary btn-sm" onclick="removeBlock(${block.id})">🗑️</button>
                    <button class="btn btn-primary btn-sm" onclick="showAdvancedTTS(${block.id})">🎤 Text to mp3</button>

                </div>
            </div>
            <div class="text-block-content" data-id="${block.id}" onmouseup="handleTextSelect()">${block.text}</div>
        `;
        elements.textBlocks.appendChild(div);
    });
}


function copyText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        navigator.clipboard.writeText(block.text);
        alert('Đã copy!');
    }
}

function downloadText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        const blob = new Blob([block.text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${block.title}.txt`;
        a.click();
    }
}

function removeBlock(id) {
    state.textBlocks = state.textBlocks.filter(b => b.id !== id);
    renderTextBlocks();
}

async function saveToWork(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (!block) return;

    try {
        const res = await fetch('/api/works', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: block.title,
                content: block.text,
                source_type: 'ocr'
            })
        });
        if (res.ok) {
            alert('Đã lưu vào Work!');
            loadWorks();
        }
    } catch (e) {
        alert('Lỗi lưu');
    }
}

// Text Selection & Tools
function handleTextSelect() {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0 && text.length <= 2000) {
        state.selectedText = text;
        elements.selectedCharCount.textContent = text.length;
        elements.toolsPanel.classList.remove('hidden');
    } else {
        elements.toolsPanel.classList.add('hidden');
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
            showResultModal('Text-to-Speech', `<audio controls src="${result.audio_url}"></audio>`);
        } else {
            alert(result.error);
        }
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
                <option value="zh-cn">中文</option>
            </select>
        </div>
        <button class="btn btn-primary" onclick="runTranslate()">Dịch</button>
        <div id="translate-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function runTranslate() {
    const destLang = document.getElementById('dest-lang').value;
    try {
        const res = await fetch('/api/tools/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: state.selectedText, dest_lang: destLang })
        });
        const result = await res.json();
        document.getElementById('translate-result').innerHTML = result.success
            ? `<p><strong>Kết quả:</strong></p><p>${result.translated_text}</p>`
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
        } else {
            html = `<p>${result.result}</p>`;
        }
        document.getElementById('research-result').innerHTML = html;
    } catch (e) {
        alert('Lỗi phân tích');
    }
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

// Work History
async function loadWorks() {
    if (!state.user) {
        elements.workList.innerHTML = '<p style="color:rgba(255,255,255,0.5);font-size:0.875rem">Đăng nhập để xem lịch sử</p>';
        return;
    }

    try {
        const res = await fetch('/api/works');
        const data = await res.json();
        state.works = data.works || [];
        renderWorkList();
    } catch (e) {
        console.error('Load works error', e);
    }
}

function renderWorkList() {
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
                title: b.title || `Block ${b.id}`
            }));
            renderTextBlocks();
        }
    } catch (e) {
        alert('Lỗi tải work');
    }
}

// Close modal on overlay click
elements.modalOverlay.addEventListener('click', (e) => {
    if (e.target === elements.modalOverlay) closeModal();
});

async function summarizeImage(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);

    if (!block || !block.imageFile) {
        alert('Không tìm thấy ảnh để tóm tắt');
        return;
    }

    // Hiển thị loading modal
    showLoadingModal('Đang phân tích ảnh bằng Gemini AI...');

    try {
        const formData = new FormData();
        formData.append('image', block.imageFile);

        const res = await fetch('/api/tools/summarize-image', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();

        if (result.success) {
            showSummaryModal(block.title, result.summary, block.imageFile);
        } else {
            alert(result.error || 'Lỗi khi tóm tắt ảnh');
        }
    } catch (e) {
        alert('Lỗi kết nối: ' + e.message);
    }
}

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

function showSummaryModal(title, summary, imageFile) {
    const imageUrl = URL.createObjectURL(imageFile);

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
                <button class="btn btn-primary" onclick="copySummary(\`${summary.replace(/`/g, '\\`')}\`)">📋 Copy tóm tắt</button>
                <button class="btn btn-secondary" onclick="downloadSummary('${title}', \`${summary.replace(/`/g, '\\`')}\`)">⬇️ Tải xuống</button>
            </div>
        </div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

function copySummary(text) {
    navigator.clipboard.writeText(text);
    alert('Đã copy tóm tắt!');
}

function downloadSummary(title, text) {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${title}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// ============ ADVANCED TTS ============

async function showAdvancedTTS(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    // Load danh sách giọng nói
    const voicesRes = await fetch('/api/tools/tts/voices');
    const voicesData = await voicesRes.json();

    if (!voicesData.success) {
        alert('Không thể tải danh sách giọng nói');
        return;
    }

    const voices = voicesData.voices;
    const styles = voicesData.styles;

    // Hiển thị modal
    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🎤 Text to Speech (Natural Reader)</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="tts-config">
            <div class="form-group">
                <label>🌍 Ngôn ngữ đích</label>
                <select id="tts-lang" onchange="updateVoiceOptions()">
                    ${Object.keys(voices).map(lang => `
                        <option value="${lang}">${getLanguageName(lang)}</option>
                    `).join('')}
                </select>
            </div>

            <div class="form-group">
                <label>👤 Giới tính giọng nói</label>
                <select id="tts-gender" onchange="updateVoiceList()">
                    <option value="female">Nữ</option>
                    <option value="male">Nam</option>
                </select>
            </div>

            <div class="form-group">
                <label>🎙️ Chọn giọng nói</label>
                <select id="tts-voice"></select>
            </div>

            <div class="form-group">
                <label>🎭 Phong cách (Style)</label>
                <select id="tts-style">
                    ${styles.map(s => `<option value="${s}">${getStyleName(s)}</option>`).join('')}
                </select>
            </div>

            <div class="form-group">
                <label>⚡ Tốc độ đọc: <span id="rate-value">+0%</span></label>
                <input type="range" id="tts-rate" min="-50" max="100" value="0"
                       oninput="document.getElementById('rate-value').textContent = (this.value >= 0 ? '+' : '') + this.value + '%'">
            </div>

            <div class="form-group">
                <label>🎵 Cao độ: <span id="pitch-value">+0Hz</span></label>
                <input type="range" id="tts-pitch" min="-50" max="50" value="0"
                       oninput="document.getElementById('pitch-value').textContent = (this.value >= 0 ? '+' : '') + this.value + 'Hz'">
            </div>

            <button class="btn btn-primary" style="width:100%; margin-top: 1rem;"
                    onclick="generateAdvancedTTS(${blockId})">
                🎤 Tạo giọng nói
            </button>

            <div id="tts-result" class="tts-result" style="margin-top: 1.5rem;"></div>
        </div>
    `;

    elements.modalOverlay.classList.remove('hidden');

    // Lưu voices data vào state tạm
    window.ttsVoicesData = voices;

    // Init voice list
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

    const voices = window.ttsVoicesData[lang]?.[gender] || [];

    const voiceSelect = document.getElementById('tts-voice');
    voiceSelect.innerHTML = voices.map((v, idx) => `
        <option value="${idx}">${v}</option>
    `).join('');
}

let lastTTSRequest = 0;
const TTS_COOLDOWN = 5000; //

async function generateAdvancedTTS(blockId) {
    const now = Date.now();
    if (now - lastTTSRequest < TTS_COOLDOWN) {
        alert(`⏳ Vui lòng đợi ${Math.ceil((TTS_COOLDOWN - (now - lastTTSRequest)) / 1000)}s`);
        return;
    }
    lastTTSRequest = now;

    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    const rateValue = parseInt(document.getElementById('tts-rate').value, 10);
    const pitchValue = parseInt(document.getElementById('tts-pitch').value, 10);

    const rate = (rateValue >= 0 ? `+${rateValue}%` : `${rateValue}%`);
    const pitch = (pitchValue >= 0 ? `+${pitchValue}Hz` : `${pitchValue}Hz`);

    const config = {
        text: block.text,
        target_lang: document.getElementById('tts-lang').value,
        voice_gender: document.getElementById('tts-gender').value,
        voice_index: parseInt(document.getElementById('tts-voice').value, 10),
        rate,
        pitch,
        style: document.getElementById('tts-style').value
    };


    // Show loading
    document.getElementById('tts-result').innerHTML = `
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
            document.getElementById('tts-result').innerHTML = `
                <div class="tts-success">
                    <h4 style="color: #10b981; margin-bottom: 1rem;">✅ Tạo thành công!</h4>
                    <audio controls style="width: 100%; margin-bottom: 1rem;">
                        <source src="${result.audio_url}" type="audio/mpeg">
                    </audio>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-primary" onclick="downloadAudio('${result.audio_url}', '${result.filename}')">
                            ⬇️ Tải xuống MP3
                        </button>
                        <button class="btn btn-secondary" onclick="copyAudioLink('${window.location.origin}${result.audio_url}')">
                            🔗 Copy link
                        </button>
                    </div>
                </div>
            `;
        } else {
            document.getElementById('tts-result').innerHTML = `
                <div style="color: #ef4444; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                    ❌ ${result.error}
                </div>
            `;
        }
    } catch (e) {
        document.getElementById('tts-result').innerHTML = `
            <div style="color: #ef4444;">❌ Lỗi: ${e.message}</div>
        `;
    }
}

function downloadAudio(url, filename) {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

function copyAudioLink(url) {
    navigator.clipboard.writeText(url);
    alert('Đã copy link audio!');
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
