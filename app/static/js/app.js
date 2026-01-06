// State
const state = {
    user: null,
    selectedFiles: [],
    textBlocks: [],
    selectedText: '',
    lastTranslation: '',  // Lưu bản dịch gần nhất
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
    initTools();
    loadWorks();

    // Xóa selection khi click ra ngoài vùng text
    document.addEventListener('click', (e) => {
        // Nếu click không phải vào textarea hoặc tools panel
        if (!e.target.closest('.text-block-content') &&
            !e.target.closest('.tools-panel') &&
            !e.target.closest('.modal-content')) {
            clearTextSelection();
        }
    });
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
    clearTextSelection();  // Xóa selection khi đóng modal
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
    const validFiles = Array.from(files)
        .filter(f => ['image/jpeg', 'image/png', 'image/jpg'].includes(f.type))
        .slice(0, 1);

    if (validFiles.length === 0) {
        alert('Vui lòng chọn file ảnh hợp lệ (JPG, PNG)');
        return;
    }

    state.selectedFiles = validFiles;
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
    formData.append('image', state.selectedFiles[0]);
    
    try {
        const res = await fetch('/api/ocr/single', {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        if (result.success) {
            addTextBlock(result.bart_output, state.selectedFiles[0].name);
        } else {
            alert(result.error || 'OCR thất bại');
        }
    } catch (e) {
        alert('Lỗi kết nối');
    }

    elements.processBtn.disabled = false;
    elements.processBtn.textContent = '🚀 Xử lý OCR';
}

// Text Blocks
function addTextBlock(text, title = 'Untitled') {
    const id = Date.now();
    state.textBlocks.push({ id, text, title });
    renderTextBlocks();
}

function renderTextBlocks() {
    elements.textBlocks.innerHTML = '';
    state.textBlocks.forEach(block => {
        const div = document.createElement('div');
        div.className = 'text-block';

        // HTML cho khung text gốc
        let html = `
            <div class="text-block-header">
                <span class="text-block-title">📄 ${block.title}</span>
                <div class="text-block-actions">
                    <button class="btn btn-secondary btn-sm" onclick="copyText(${block.id})">📋 Copy</button>
                    <button class="btn btn-secondary btn-sm" onclick="saveToWork(${block.id})">💾 Save</button>
                    <button class="btn btn-secondary btn-sm" onclick="downloadText(${block.id})">⬇️ Download</button>
                    <button class="btn btn-secondary btn-sm" onclick="removeBlock(${block.id})">🗑️</button>
                    <button class="btn btn-secondary btn-sm" onclick="translateBlock(${block.id}, this)">🌐 Translate All</button>
                </div>
            </div>
            <div class="text-block-label">🇻🇳 Tiếng Việt (Gốc):</div>
            <textarea
                class="text-block-content editable" 
                data-id="${block.id}" 
                onmouseup="handleTextSelect()"
                oninput="updateBlockText(${block.id}, this.value)"
            >${block.text}</textarea>
        `;

        // Nếu có bản dịch, hiển thị thêm khung bản dịch
        if (block.translated) {
            html += `
                <div class="text-block-label" style="margin-top: 15px;">🇬🇧 Tiếng Anh (Bản dịch):</div>
                <textarea
                    class="text-block-content translated editable"
                    data-id="${block.id}"
                    oninput="updateTranslatedText(${block.id}, this.value)"
                >${block.translated}</textarea>
                <div class="text-block-actions" style="margin-top: 10px;">
                    <button class="btn btn-secondary btn-sm" onclick="copyTranslatedText(${block.id})">📋 Copy bản dịch</button>
                </div>
            `;
        }

        div.innerHTML = html;
        elements.textBlocks.appendChild(div);
    });
}

function updateBlockText(id, newText) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        block.text = newText;
    }
}

// Cập nhật bản dịch khi user chỉnh sửa
function updateTranslatedText(id, newText) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        block.translated = newText;
    }
}

// Copy bản dịch
function copyTranslatedText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block && block.translated) {
        navigator.clipboard.writeText(block.translated).then(() => {
            showNotification('✓ Đã copy bản dịch', 'success');
        }).catch(() => {
            showNotification('Lỗi khi copy', 'error');
        });
    }
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
        clearTextSelection();  // Xóa selection nếu không hợp lệ
    }
}

// Hàm xóa selection và ẩn tools panel
function clearTextSelection() {
    const selection = window.getSelection();
    if (selection) {
        selection.removeAllRanges();  // Xóa vùng chọn
    }
    state.selectedText = '';
    elements.toolsPanel.classList.add('hidden');  // Ẩn panel công cụ
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
            <h3>🌐 Dịch văn bản (Việt → Anh)</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="form-group">
            <label>Model: VinAI (Vietnamese → English)</label>
        </div>
        <button class="btn btn-primary" onclick="runTranslate()">Dịch</button>
        <div id="translate-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function runTranslate() {
    // VinAI model chỉ hỗ trợ Việt → Anh
    try {
        const res = await fetch('/api/tools/translate', {  // Fix: Đúng route
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: state.selectedText,
                src_lang: 'vi',
                dest_lang: 'en'
            })
        });
        const result = await res.json();
        document.getElementById('translate-result').innerHTML = result.success
            ? `<p><strong>Kết quả:</strong></p><p>${result.translated_text}</p>`
            : `<p style="color:red">${result.error}</p>`;

        // Xóa selection sau khi dịch xong
        clearTextSelection();
    } catch (e) {
        document.getElementById('translate-result').innerHTML = `<p style="color:red">Lỗi: ${e.message}</p>`;
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

// Hàm dịch toàn bộ text block từ Việt sang Anh
async function translateBlock(blockId, buttonElement) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block || !block.text || !block.text.trim()) {
        showNotification('Không có văn bản để dịch', 'warning');
        return;
    }

    // Disable button và hiển thị loading
    buttonElement.disabled = true;
    buttonElement.innerHTML = '⏳ Đang dịch...';

    try {
        const response = await fetch('/api/tools/translate', {  // Fix: Đúng route với tools blueprint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: block.text,  // VinAI model dịch Việt→Anh
                src_lang: 'vi',
                dest_lang: 'en'
            })
        });

        // Parse JSON response
        const data = await response.json();

        console.log('Translation response:', data);  // Debug log

        // Kiểm tra response
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Dịch thất bại');
        }

        // Kiểm tra có kết quả dịch không
        if (!data.translated_text) {
            throw new Error('Không nhận được kết quả dịch');
        }

        // LƯU bản dịch vào block (không thay thế text gốc)
        block.translated = data.translated_text;

        // Render lại để hiển thị cả 2 khung
        renderTextBlocks();

        showNotification('✓ Dịch hoàn tất!', 'success');

        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = '✓ Đã dịch';
        buttonElement.classList.add('btn-success');

    } catch (error) {
        console.error('Lỗi dịch:', error);
        showNotification(error.message || 'Dịch thất bại', 'error');

        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = '🌐 Translate All';
    }
}

// Hàm dịch text được chọn từ Việt sang Anh
async function translateSelectedText() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (!selectedText) {
        showNotification('Vui lòng chọn văn bản để dịch', 'warning');
        return;
    }

    try {
        // Hiển thị modal loading
        showTranslationModal();

        const response = await fetch('/api/tools/translate', {  // Fix: Đúng route với tools blueprint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: selectedText,  // VinAI model dịch Việt→Anh
                src_lang: 'vi',
                dest_lang: 'en'
            })
        });

        // Parse JSON response
        const data = await response.json();

        console.log('Translation response:', data);  // Debug log

        // Kiểm tra response
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Dịch thất bại');
        }

        // Kiểm tra có kết quả dịch không
        if (!data.translated_text) {
            throw new Error('Không nhận được kết quả dịch');
        }

        // Hiển thị kết quả dịch
        showTranslationResult(selectedText, data.translated_text);

    } catch (error) {
        console.error('Lỗi dịch:', error);
        hideTranslationModal();
        showNotification(error.message || 'Dịch thất bại', 'error');
    }
}

// Hiển thị modal loading khi đang dịch
function showTranslationModal() {
    const modal = document.createElement('div');
    modal.id = 'translation-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>🌐 Đang dịch...</h3>
            </div>
            <div class="modal-body">
                <div class="spinner"></div>
                <p>Vui lòng đợi trong khi hệ thống dịch văn bản của bạn</p>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Hiển thị kết quả dịch
function showTranslationResult(original, translated) {
    const modal = document.getElementById('translation-modal');
    if (!modal) return;

    // Escape HTML để tránh lỗi XSS
    const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    const originalEscaped = escapeHtml(original);
    const translatedEscaped = escapeHtml(translated);

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>🌐 Kết Quả Dịch</h3>
                <button class="close-btn" onclick="hideTranslationModal()">×</button>
            </div>
            <div class="modal-body">
                <div class="translation-box">
                    <label>Bản gốc (Tiếng Việt):</label>
                    <div class="text-box">${originalEscaped}</div>
                </div>
                <div class="translation-box">
                    <label>Bản dịch (Tiếng Anh):</label>
                    <div class="text-box">${translatedEscaped}</div>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="copyTranslationText()">
                        📋 Sao chép bản dịch
                    </button>
                    <button class="btn btn-secondary" onclick="hideTranslationModal()">
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    `;

    // Lưu translated text vào data attribute để copy
    modal.setAttribute('data-translated', translated);
}

// Ẩn modal
function hideTranslationModal() {
    const modal = document.getElementById('translation-modal');
    if (modal) {
        modal.remove();
    }
}

// Copy bản dịch
function copyTranslation(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Đã sao chép bản dịch!', 'success');
    }).catch(() => {
        showNotification('Lỗi khi sao chép', 'error');
    });
}

// Copy bản dịch từ modal
function copyTranslationText() {
    const modal = document.getElementById('translation-modal');
    if (modal) {
        const text = modal.getAttribute('data-translated');
        if (text) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('✓ Đã sao chép bản dịch!', 'success');
            }).catch(() => {
                showNotification('Lỗi khi sao chép', 'error');
            });
        }
    }
}

// Hiển thị thông báo
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

