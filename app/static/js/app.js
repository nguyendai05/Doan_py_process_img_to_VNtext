// State
const state = {
    user: null,
    selectedFiles: [],
    textBlocks: [],
    selectedText: '',
    works: []
};

// TTS State
const ttsState = {
    selectedLanguage: localStorage.getItem('tts_language') || 'vi',
    isGenerating: false,
    lastUsedLanguage: localStorage.getItem('tts_language') || 'vi',
    currentAudio: null
};

// Supported TTS Languages
const TTS_LANGUAGES = [
    { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' },
    { code: 'zh-CN', name: '中文', flag: '🇨🇳' }
];

// Translate State - Requirements: 1.2, 1.4
const translateState = {
    sourceLang: localStorage.getItem('translate_source_lang') || 'auto',
    destLang: localStorage.getItem('translate_dest_lang') || 'en',
    isTranslating: false,
    lastResult: null
};

// Supported Translate Languages - Requirements: 1.2
const TRANSLATE_LANGUAGES = [
    { code: 'auto', name: 'Tự động phát hiện', flag: '🔍' },
    { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' },
    { code: 'zh-cn', name: '中文 (简体)', flag: '🇨🇳' },
    { code: 'zh-tw', name: '中文 (繁體)', flag: '🇹🇼' },
    { code: 'th', name: 'ไทย', flag: '🇹🇭' },
    { code: 'ru', name: 'Русский', flag: '🇷🇺' }
];

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
    initModal();
});

/**
 * Initialize modal behavior - prevent closing on outside click
 */
function initModal() {
    // Prevent modal from closing when clicking on overlay (outside modal content)
    // Modal can only be closed by clicking the close button
    if (elements.modalOverlay) {
        elements.modalOverlay.addEventListener('click', (e) => {
            // Do nothing - modal stays open
            e.stopPropagation();
        });
    }

    // Prevent clicks inside modal content from bubbling
    if (elements.modalContent) {
        elements.modalContent.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
}

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

/**
 * Close the modal and stop any playing TTS audio
 * Requirements: 4.4 - Stop audio playback when modal is closed
 */
function closeModal() {
    // Stop TTS audio playback if playing
    if (ttsState.currentAudio) {
        ttsState.currentAudio.pause();
        ttsState.currentAudio.currentTime = 0;
        ttsState.currentAudio = null;
    }
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

    // Paste image from clipboard (Ctrl+V)
    document.addEventListener('paste', handlePaste);
}

/**
 * Handle paste event for images from clipboard
 */
function handlePaste(e) {
    const clipboardData = e.clipboardData || window.clipboardData;
    if (!clipboardData) return;

    const items = clipboardData.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
        const item = items[i];

        // Check if item is an image
        if (item.type.indexOf('image') !== -1) {
            e.preventDefault();

            const file = item.getAsFile();
            if (file) {
                // Validate file type
                if (['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
                    // Create a proper file name
                    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                    const extension = file.type.split('/')[1];
                    const renamedFile = new File([file], `pasted_image_${timestamp}.${extension}`, { type: file.type });

                    state.selectedFiles = [renamedFile];
                    renderPreview();
                    elements.processBtn.disabled = false;
                    showToast('✅ Đã paste ảnh từ clipboard!', 'success');
                } else {
                    showToast('⚠️ Chỉ hỗ trợ ảnh JPG, PNG', 'warning');
                }
            }
            return;
        }
    }
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
            // Reload works list to show new work
            loadWorks();
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
    if (state.textBlocks.length === 0) {
        elements.textBlocks.innerHTML = `
            <div class="empty-state" id="empty-results">
                <div class="empty-state-icon">📝</div>
                <h4>Kết quả OCR sẽ hiển thị ở đây</h4>
                <p>Tải ảnh lên và nhấn "Xử lý OCR" để bắt đầu</p>
            </div>
        `;
        return;
    }

    state.textBlocks.forEach(block => {
        const shortTitle = block.title.length > 25 ? block.title.substring(0, 25) + '...' : block.title;
        const div = document.createElement('div');
        div.className = 'text-block';
        div.innerHTML = `
            <div class="text-block-header">
                <span class="text-block-title">
                    <span class="icon">📄</span>
                    <span class="title-text" title="${block.title}">${shortTitle}</span>
                </span>
                <div class="text-block-actions">
                    <button class="btn-action" onclick="copyText(${block.id})" title="Copy">📋</button>
                    <button class="btn-action" onclick="downloadText(${block.id})" title="Tải xuống">⬇️</button>
                    <button class="btn-action" onclick="translateAllByModel()" title="Dịch tất cả (Model Vi→En)">🌐</button>
                    <button class="btn-action" onclick="runBartCorrection(${block.id})" title="Sửa lỗi bằng AI">🤖</button>
                    <button class="btn-action btn-delete" onclick="removeBlock(${block.id})" title="Xóa">🗑️</button>
                </div>
            </div>
            <textarea
                class="text-block-content editable"
                data-id="${block.id}"
                onmouseup="handleTextSelect()"
                oninput="updateBlockText(${block.id}, this.value)"
                placeholder="Nội dung văn bản..."
            >${block.text}</textarea>
        `;
        elements.textBlocks.appendChild(div);
    });
}

function updateBlockText(id, newText) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        block.text = newText;
    }
}

function copyText(id) {
    const block = state.textBlocks.find(b => b.id === id);
    if (block) {
        navigator.clipboard.writeText(block.text);
        showToast('Đã copy vào clipboard!', 'success');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
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

// Character count thresholds for TTS
const CHAR_LIMITS = {
    GREEN_MAX: 1500,      // 0-1500: green (safe)
    YELLOW_MAX: 1900,     // 1501-1900: yellow (warning)
    RED_MAX: 2000,        // 1901-2000: red (approaching limit)
    ABSOLUTE_MAX: 2000    // >2000: disabled
};

// Text Selection & Tools
function handleTextSelect() {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0) {
        state.selectedText = text;
        updateCharacterCountDisplay(text.length);
        elements.toolsPanel.classList.remove('hidden');
        updateModelTranslateButtonState();
    } else {
        elements.toolsPanel.classList.add('hidden');
    }

}

/**
 * Close the tools panel
 */
function closeToolsPanel() {
    elements.toolsPanel.classList.add('hidden');
    state.selectedText = '';
    window.getSelection().removeAllRanges();
}

/**
 * Update character count display with color indicators and warning messages
 * Requirements: 5.1, 5.4
 * @param {number} count - Number of characters selected
 */
function updateCharacterCountDisplay(count) {
    const charCountEl = elements.selectedCharCount;
    const ttsBtn = document.querySelector('.tool-btn[data-tool="tts"]');

    // Update character count text
    charCountEl.textContent = count;

    // Remove all existing color classes
    charCountEl.classList.remove('char-count-green', 'char-count-yellow', 'char-count-red');

    // Get or create warning message element
    let warningEl = document.getElementById('char-limit-warning');
    if (!warningEl) {
        warningEl = document.createElement('p');
        warningEl.id = 'char-limit-warning';
        warningEl.className = 'char-limit-warning';
        // Insert after selected-text-info
        const selectedTextInfo = document.querySelector('.selected-text-info');
        if (selectedTextInfo) {
            selectedTextInfo.parentNode.insertBefore(warningEl, selectedTextInfo.nextSibling);
        }
    }

    // Determine color class and warning message based on count
    if (count <= CHAR_LIMITS.GREEN_MAX) {
        // Green: 0-1500 chars - safe zone
        charCountEl.classList.add('char-count-green');
        warningEl.textContent = '';
        warningEl.classList.add('hidden');

        // Enable TTS button
        if (ttsBtn) {
            ttsBtn.disabled = false;
            ttsBtn.classList.remove('disabled');
        }
    } else if (count <= CHAR_LIMITS.YELLOW_MAX) {
        // Yellow: 1501-1900 chars - warning zone
        charCountEl.classList.add('char-count-yellow');
        warningEl.textContent = `⚠️ Đang tiến gần giới hạn (${CHAR_LIMITS.ABSOLUTE_MAX} ký tự)`;
        warningEl.classList.remove('hidden');
        warningEl.classList.remove('warning-red');
        warningEl.classList.add('warning-yellow');

        // Enable TTS button
        if (ttsBtn) {
            ttsBtn.disabled = false;
            ttsBtn.classList.remove('disabled');
        }
    } else if (count <= CHAR_LIMITS.RED_MAX) {
        // Red: 1901-2000 chars - danger zone
        charCountEl.classList.add('char-count-red');
        warningEl.textContent = `⚠️ Gần đạt giới hạn tối đa (${count}/${CHAR_LIMITS.ABSOLUTE_MAX})`;
        warningEl.classList.remove('hidden');
        warningEl.classList.remove('warning-yellow');
        warningEl.classList.add('warning-red');

        // Enable TTS button (still within limit)
        if (ttsBtn) {
            ttsBtn.disabled = false;
            ttsBtn.classList.remove('disabled');
        }
    } else {
        // Over limit: >2000 chars - disabled
        charCountEl.classList.add('char-count-red');
        warningEl.textContent = `❌ Vượt quá giới hạn ${CHAR_LIMITS.ABSOLUTE_MAX} ký tự. TTS bị vô hiệu hóa.`;
        warningEl.classList.remove('hidden');
        warningEl.classList.remove('warning-yellow');
        warningEl.classList.add('warning-red');

        // Disable TTS button
        if (ttsBtn) {
            ttsBtn.disabled = true;
            ttsBtn.classList.add('disabled');
        }
    }
}

function initTools() {
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tool = btn.dataset.tool;
            if (tool === 'tts') showTTSModal();
            else if (tool === 'translate') showTranslateModal();
            else if (tool === 'research') showResearchModal();
        });
    });
}

function showTTSModal() {
    if (!state.selectedText) return;

    // Build language options grid
    const languageOptions = TTS_LANGUAGES.map(lang => {
        const isSelected = lang.code === ttsState.lastUsedLanguage;
        return `
            <div class="tts-language-option ${isSelected ? 'selected' : ''}"
                 data-lang="${lang.code}"
                 onclick="selectTTSLanguage('${lang.code}')">
                <span class="lang-flag">${lang.flag}</span>
                <span class="lang-name">${lang.name}</span>
            </div>
        `;
    }).join('');

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🔊 Text-to-Speech</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="tts-modal-body">
            <p class="tts-instruction">Chọn ngôn ngữ đọc:</p>
            <div class="tts-language-grid" id="tts-language-grid">
                ${languageOptions}
            </div>
            <div class="tts-selected-text-preview">
                <label>Văn bản đã chọn (${state.selectedText.length} ký tự):</label>
                <div class="text-preview">${state.selectedText.substring(0, 100)}${state.selectedText.length > 100 ? '...' : ''}</div>
            </div>
            <button class="btn btn-primary tts-generate-btn" id="tts-generate-btn" onclick="runTTS()">
                <span class="btn-text">🔊 Tạo Audio</span>
            </button>
        </div>
        <div id="tts-result" class="result-panel mt-2"></div>
    `;

    // Set initial selected language
    ttsState.selectedLanguage = ttsState.lastUsedLanguage;
    elements.modalOverlay.classList.remove('hidden');
}

function selectTTSLanguage(langCode) {
    ttsState.selectedLanguage = langCode;

    // Update UI to show selected language
    document.querySelectorAll('.tts-language-option').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.lang === langCode) {
            el.classList.add('selected');
        }
    });
}

async function runTTS() {
    if (!state.selectedText) return;
    if (ttsState.isGenerating) return;

    // Set generating state
    ttsState.isGenerating = true;

    // Update UI to show loading state
    const generateBtn = document.getElementById('tts-generate-btn');
    const ttsToolBtn = document.querySelector('.tool-btn[data-tool="tts"]');

    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="btn-text">⏳ Đang tạo audio...</span>';
    }

    // Disable TTS button in tools panel
    if (ttsToolBtn) {
        ttsToolBtn.disabled = true;
        ttsToolBtn.classList.add('disabled');
    }

    try {
        const res = await fetch('/api/tools/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: state.selectedText,
                language: ttsState.selectedLanguage
            })
        });
        const result = await res.json();

        if (result.success) {
            // Save selected language to localStorage for next time
            localStorage.setItem('tts_language', ttsState.selectedLanguage);
            ttsState.lastUsedLanguage = ttsState.selectedLanguage;

            // Show result in the TTS modal using renderAudioPlayer
            const ttsResultDiv = document.getElementById('tts-result');
            if (ttsResultDiv) {
                ttsResultDiv.innerHTML = renderAudioPlayer(result.audio_url, result.from_cache);

                // Store audio reference for cleanup on modal close
                const audioElement = document.getElementById('tts-audio-element');
                if (audioElement) {
                    ttsState.currentAudio = audioElement;
                }
            }
        } else {
            // Show error in the TTS modal
            const ttsResultDiv = document.getElementById('tts-result');
            if (ttsResultDiv) {
                ttsResultDiv.innerHTML = `
                    <div class="tts-error">
                        <span class="error-icon">❌</span>
                        <span class="error-message">${result.error || 'Lỗi tạo audio'}</span>
                    </div>
                `;
            } else {
                showToast(result.error || 'Lỗi tạo audio', 'error');
            }
        }
    } catch (e) {
        const ttsResultDiv = document.getElementById('tts-result');
        if (ttsResultDiv) {
            ttsResultDiv.innerHTML = `
                <div class="tts-error">
                    <span class="error-icon">❌</span>
                    <span class="error-message">Lỗi kết nối</span>
                </div>
            `;
        } else {
            showToast('Lỗi kết nối', 'error');
        }
    } finally {
        // Reset generating state
        ttsState.isGenerating = false;

        // Re-enable buttons
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<span class="btn-text">🔊 Tạo Audio</span>';
        }

        if (ttsToolBtn) {
            ttsToolBtn.disabled = false;
            ttsToolBtn.classList.remove('disabled');
        }
    }
}

/**
 * Show translate modal with language selector grids
 * Requirements: 1.1, 1.3, 1.5, 6.1, 6.3
 */
function showTranslateModal() {
    if (!state.selectedText) return;

    // Build source language options grid (includes auto-detect)
    const sourceLanguageOptions = TRANSLATE_LANGUAGES.map(lang => {
        const isSelected = lang.code === translateState.sourceLang;
        return `
            <div class="translate-lang-option ${isSelected ? 'selected' : ''}"
                 data-lang="${lang.code}"
                 data-type="source"
                 onclick="selectSourceLang('${lang.code}')">
                <span class="lang-flag">${lang.flag}</span>
                <span class="lang-name">${lang.name}</span>
            </div>
        `;
    }).join('');

    // Build destination language options grid (excludes auto-detect)
    const destLanguageOptions = TRANSLATE_LANGUAGES
        .filter(lang => lang.code !== 'auto')
        .map(lang => {
            const isSelected = lang.code === translateState.destLang;
            return `
                <div class="translate-lang-option ${isSelected ? 'selected' : ''}"
                     data-lang="${lang.code}"
                     data-type="dest"
                     onclick="selectDestLang('${lang.code}')">
                    <span class="lang-flag">${lang.flag}</span>
                    <span class="lang-name">${lang.name}</span>
                </div>
            `;
        }).join('');

    // Check if swap should be disabled (source is 'auto')
    const swapDisabled = translateState.sourceLang === 'auto';
    const swapTooltip = swapDisabled ? 'title="Không thể hoán đổi khi nguồn là Tự động phát hiện"' : '';

    // Check if same language warning should be shown
    const showSameLangWarning = translateState.sourceLang !== 'auto' &&
        translateState.sourceLang === translateState.destLang;

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🌐 Dịch văn bản</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="translate-modal-body">
            <div class="translate-language-selector">
                <div class="translate-lang-section">
                    <label class="translate-lang-label">Ngôn ngữ nguồn:</label>
                    <div class="translate-language-grid" id="source-lang-grid">
                        ${sourceLanguageOptions}
                    </div>
                </div>

                <div class="translate-swap-section">
                    <button class="swap-lang-btn ${swapDisabled ? 'disabled' : ''}"
                            onclick="swapLanguages()"
                            ${swapDisabled ? 'disabled' : ''}
                            ${swapTooltip}>
                        ⇄
                    </button>
                </div>

                <div class="translate-lang-section">
                    <label class="translate-lang-label">Ngôn ngữ đích:</label>
                    <div class="translate-language-grid" id="dest-lang-grid">
                        ${destLanguageOptions}
                    </div>
                </div>
            </div>

            <div id="same-lang-warning" class="same-lang-warning ${showSameLangWarning ? '' : 'hidden'}">
                ⚠️ Ngôn ngữ nguồn và đích giống nhau. Vui lòng chọn ngôn ngữ khác.
            </div>

            <div class="translate-selected-text-preview">
                <label>Văn bản đã chọn (${state.selectedText.length} ký tự):</label>
                <div class="text-preview">${state.selectedText.substring(0, 150)}${state.selectedText.length > 150 ? '...' : ''}</div>
            </div>

            <button class="btn btn-primary translate-btn" id="translate-btn" onclick="runTranslate()" ${showSameLangWarning ? 'disabled' : ''}>
                <span class="btn-text">🌐 Dịch</span>
            </button>
            <button class="btn btn-secondary translate-btn" id="translate-model-btn" onclick="runTranslate('model')" disabled>
                <span class="btn-text">🤖 Dịch bằng Model (Vi→En)</span>
            </button>

        </div>
        <div id="translate-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
    updateModelTranslateButtonState();
}

/**
 * Select source language for translation
 * Requirements: 6.2
 * @param {string} langCode - Language code to select
 */
function selectSourceLang(langCode) {
    translateState.sourceLang = langCode;

    // Update UI to show selected source language
    document.querySelectorAll('#source-lang-grid .translate-lang-option').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.lang === langCode) {
            el.classList.add('selected');
        }
    });

    // Update swap button state (disabled if source is 'auto')
    const swapBtn = document.querySelector('.swap-lang-btn');
    if (swapBtn) {
        if (langCode === 'auto') {
            swapBtn.disabled = true;
            swapBtn.classList.add('disabled');
            swapBtn.title = 'Không thể hoán đổi khi nguồn là Tự động phát hiện';
        } else {
            swapBtn.disabled = false;
            swapBtn.classList.remove('disabled');
            swapBtn.title = '';
        }
    }

    // Update same language warning
    updateSameLangWarning();
    updateModelTranslateButtonState();
}

/**
 * Select destination language for translation
 * Requirements: 6.2
 * @param {string} langCode - Language code to select
 */
function selectDestLang(langCode) {
    translateState.destLang = langCode;

    // Update UI to show selected destination language
    document.querySelectorAll('#dest-lang-grid .translate-lang-option').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.lang === langCode) {
            el.classList.add('selected');
        }
    });

    // Update same language warning
    updateSameLangWarning();
    updateModelTranslateButtonState();
}

/**
 * Swap source and destination languages
 * Requirements: 6.2
 * Only works if source is not 'auto'
 */
function swapLanguages() {
    // Don't swap if source is 'auto'
    if (translateState.sourceLang === 'auto') {
        return;
    }

    // Swap the languages
    const tempLang = translateState.sourceLang;
    translateState.sourceLang = translateState.destLang;
    translateState.destLang = tempLang;

    // Update source language UI
    document.querySelectorAll('#source-lang-grid .translate-lang-option').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.lang === translateState.sourceLang) {
            el.classList.add('selected');
        }
    });

    // Update destination language UI
    document.querySelectorAll('#dest-lang-grid .translate-lang-option').forEach(el => {
        el.classList.remove('selected');
        if (el.dataset.lang === translateState.destLang) {
            el.classList.add('selected');
        }
    });

    // Update same language warning (should be same after swap)
    updateSameLangWarning();
    updateModelTranslateButtonState();
}

/**
 * Update same language warning visibility and translate button state
 * Requirements: 1.5
 */
function updateSameLangWarning() {
    const warningEl = document.getElementById('same-lang-warning');
    const translateBtn = document.getElementById('translate-btn');

    // Show warning if source (not auto) equals destination
    const showWarning = translateState.sourceLang !== 'auto' &&
        translateState.sourceLang === translateState.destLang;

    if (warningEl) {
        if (showWarning) {
            warningEl.classList.remove('hidden');
        } else {
            warningEl.classList.add('hidden');
        }
    }

    // Disable translate button if same language
    if (translateBtn) {
        translateBtn.disabled = showWarning;
    }
}

/**
 * Run translation with loading state and caching support
 * Requirements: 2.1, 2.2, 1.4
 */
async function runTranslate(mode = 'google') {
    if (!state.selectedText) return;
    if (translateState.isTranslating) return;

    // Chặn chắc ở client cho mode model
    if (mode === 'model') {
        const ok = (translateState.destLang === 'en') &&
            (translateState.sourceLang === 'vi' ||
                (translateState.sourceLang === 'auto' && isLikelyVietnamese(state.selectedText)));

        if (!ok) {
            showToast('Model chỉ hỗ trợ dịch Tiếng Việt → English (Vi→En)', 'warning');
            updateModelTranslateButtonState();
            return;
        }
    }

    const sourceLang = translateState.sourceLang;
    const destLang = translateState.destLang;

    translateState.isTranslating = true;

    const translateBtn = document.getElementById('translate-btn');
    const modelBtn = document.getElementById('translate-model-btn');
    const translateToolBtn = document.querySelector('.tool-btn[data-tool="translate"]');
    const translateResultDiv = document.getElementById('translate-result');

    // Loading state
    if (translateBtn) {
        translateBtn.disabled = true;
        translateBtn.innerHTML = '<span class="btn-text">⏳ Đang dịch...</span>';
    }
    if (modelBtn) {
        modelBtn.disabled = true;
    }
    if (translateToolBtn) {
        translateToolBtn.disabled = true;
        translateToolBtn.classList.add('disabled');
    }
    if (translateResultDiv) {
        translateResultDiv.innerHTML = `
            <div class="translate-loading">
                <span class="loading-spinner">⏳</span>
                <span class="loading-text">${mode === 'model' ? 'Đang dịch bằng model (Vi→En)...' : 'Đang dịch văn bản...'}</span>
            </div>
        `;
    }

    try {
        let res, result;

        if (mode === 'model') {
            // MODEL Vi->En
            res = await fetch('/api/tools/translate-model-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: state.selectedText })
            });

            result = await res.json();

            if (res.ok && result.success) {
                // Chuẩn hoá để dùng lại UI hiện tại
                const normalized = {
                    translated_text: result.translated_text || '',
                    source_lang: 'vi',
                    dest_lang: 'en',
                    from_cache: false
                };

                translateState.lastResult = normalized;
                if (translateResultDiv) {
                    translateResultDiv.innerHTML = renderTranslationResult(normalized);
                }
            } else {
                if (translateResultDiv) {
                    translateResultDiv.innerHTML = renderTranslationError({
                        error: result.error || 'Dịch bằng model thất bại',
                        error_code: result.error_code || 'TRANSLATION_FAILED'
                    });
                }
            }
        } else {
            // GOOGLE translate như cũ
            res = await fetch('/api/tools/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: state.selectedText,
                    dest_lang: destLang,
                    src_lang: sourceLang
                })
            });

            result = await res.json();

            if (result.success) {
                localStorage.setItem('translate_source_lang', sourceLang);
                localStorage.setItem('translate_dest_lang', destLang);

                translateState.lastResult = result;
                if (translateResultDiv) {
                    translateResultDiv.innerHTML = renderTranslationResult(result);
                }
            } else {
                if (translateResultDiv) {
                    translateResultDiv.innerHTML = renderTranslationError(result);
                }
            }
        }
    } catch (e) {
        if (translateResultDiv) {
            translateResultDiv.innerHTML = renderTranslationError({
                error: 'Lỗi kết nối. Vui lòng thử lại.',
                error_code: 'NETWORK_ERROR'
            });
        }
    } finally {
        translateState.isTranslating = false;

        // Restore nút Dịch thường (same language rule vẫn giữ)
        if (translateBtn) {
            const sameLang = translateState.sourceLang !== 'auto' &&
                translateState.sourceLang === translateState.destLang;

            translateBtn.disabled = sameLang;
            translateBtn.innerHTML = '<span class="btn-text">🌐 Dịch</span>';
        }

        // Restore tool button
        if (translateToolBtn) {
            translateToolBtn.disabled = false;
            translateToolBtn.classList.remove('disabled');
        }

        // Update lại trạng thái nút model theo rule vi->en/auto-viet
        updateModelTranslateButtonState();
    }
}

function isLikelyVietnamese(text) {
    const s = (text || '').trim();
    if (!s) return false;

    // Có dấu tiếng Việt hoặc ký tự đặc trưng
    const vietChars = /[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]/i;
    if (vietChars.test(s)) return true;

    // Fallback đoán bằng vài từ common (không dấu)
    const commonWords = /\b(tôi|toi|ban|bạn|chung|chúng|khong|không|va|và|la|là|cua|của|cho|mot|một|nhung|những|duoc|được|vui|long|lòng|xin|kinh|kính|gui|gửi)\b/i;
    return commonWords.test(s);
}

function updateModelTranslateButtonState() {
    const btn = document.getElementById('translate-model-btn');
    if (!btn) return;

    const src = translateState.sourceLang; // 'auto' | 'vi' | ...
    const dst = translateState.destLang;   // 'en' | ...

    let enabled = false;

    // Model cố định Vi -> En
    if (dst === 'en') {
        if (src === 'vi') enabled = true;
        else if (src === 'auto') enabled = isLikelyVietnamese(state.selectedText);
        else enabled = false;
    }

    btn.disabled = !enabled;

    // Tooltip rõ ràng
    if (!enabled) {
        if (dst !== 'en') btn.title = 'Model chỉ hỗ trợ đích là English (en)';
        else if (src !== 'vi' && src !== 'auto') btn.title = 'Model chỉ hỗ trợ nguồn là Tiếng Việt (vi)';
        else btn.title = 'Model chỉ bật khi phát hiện văn bản có vẻ là Tiếng Việt';
    } else {
        btn.title = 'Dịch bằng Model (Vi→En)';
    }
}

/**
 * Render translation result with enhanced display
 * Requirements: 4.1, 4.2, 4.3, 4.4
 * @param {object} result - Translation result object
 * @returns {string} HTML string for the translation result
 */
function renderTranslationResult(result) {
    // Get language names for badges
    const sourceLangInfo = TRANSLATE_LANGUAGES.find(l => l.code === result.source_lang) ||
        { name: result.source_lang, flag: '🌐' };
    const destLangInfo = TRANSLATE_LANGUAGES.find(l => l.code === result.dest_lang) ||
        { name: result.dest_lang, flag: '🌐' };

    // Determine if source was auto-detected
    const sourceLabel = translateState.sourceLang === 'auto'
        ? `${sourceLangInfo.flag} ${sourceLangInfo.name} (phát hiện tự động)`
        : `${sourceLangInfo.flag} ${sourceLangInfo.name}`;

    // Cache indicator badge - Requirements: 4.4
    const cacheIndicator = result.from_cache
        ? '<span class="cache-badge cached">📦 Từ cache</span>'
        : '<span class="cache-badge new">✨ Mới dịch</span>';

    return `
        <div class="translation-result-container">
            <div class="translation-result-header">
                <div class="translation-lang-badges">
                    <span class="lang-badge source-lang">${sourceLabel}</span>
                    <span class="lang-arrow">→</span>
                    <span class="lang-badge dest-lang">${destLangInfo.flag} ${destLangInfo.name}</span>
                </div>
                ${cacheIndicator}
            </div>
            <div class="translation-result-text">
                ${escapeHtml(result.translated_text)}
            </div>
            <div class="translation-result-actions">
                <button class="btn btn-secondary btn-sm copy-result-btn" onclick="copyTranslationResult()">
                    <span class="copy-icon">📋</span>
                    <span>Sao chép</span>
                </button>
            </div>
        </div>
    `;
}

/**
 * Render translation error message
 * Requirements: 2.4
 * @param {object} result - Error result object with error and error_code
 * @returns {string} HTML string for the error display
 */
function renderTranslationError(result) {
    // Map error codes to user-friendly messages
    const errorMessages = {
        'EMPTY_TEXT': '❌ Văn bản trống hoặc chỉ chứa khoảng trắng.',
        'TEXT_TOO_LONG': '❌ Văn bản vượt quá giới hạn 2000 ký tự.',
        'SAME_LANGUAGE': '❌ Ngôn ngữ nguồn và đích giống nhau.',
        'UNSUPPORTED_LANGUAGE': '❌ Ngôn ngữ không được hỗ trợ.',
        'TRANSLATION_FAILED': '❌ Dịch thất bại. Vui lòng thử lại.',
        'NETWORK_ERROR': '❌ Lỗi kết nối. Vui lòng kiểm tra mạng và thử lại.',
        'CACHE_ERROR': '❌ Lỗi hệ thống cache.'
    };

    const errorMessage = errorMessages[result.error_code] || result.error || 'Đã xảy ra lỗi không xác định.';

    return `
        <div class="translate-error">
            <span class="error-icon">⚠️</span>
            <span class="error-message">${errorMessage}</span>
        </div>
    `;
}

/**
 * Copy translation result to clipboard
 * Requirements: 4.3
 */
function copyTranslationResult() {
    if (translateState.lastResult && translateState.lastResult.translated_text) {
        navigator.clipboard.writeText(translateState.lastResult.translated_text)
            .then(() => {
                showToast('Đã sao chép kết quả dịch!', 'success');
            })
            .catch(() => {
                showToast('Không thể sao chép. Vui lòng thử lại.', 'error');
            });
    }
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showResearchModal() {
    if (!state.selectedText) {
        showToast('Vui lòng chọn văn bản trước', 'warning');
        return;
    }

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>📚 Research</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="research-modal-body">
            <div class="research-selected-text">
                <label>Văn bản đã chọn (${state.selectedText.length} ký tự):</label>
                <div class="text-preview">${state.selectedText.substring(0, 150)}${state.selectedText.length > 150 ? '...' : ''}</div>
            </div>
            <div class="form-group">
                <label>Loại phân tích</label>
                <select id="research-type" class="research-type-select">
                    <option value="keywords">🔑 Từ khóa</option>
                    <option value="summary">📝 Tóm tắt</option>
                </select>
            </div>
            <button class="btn btn-primary" id="research-btn" onclick="runResearch()">
                <span class="btn-text">🔍 Phân tích</span>
            </button>
        </div>
        <div id="research-result" class="result-panel mt-2"></div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

async function runResearch() {
    const type = document.getElementById('research-type').value;
    const researchBtn = document.getElementById('research-btn');
    const resultDiv = document.getElementById('research-result');

    // Show loading state
    if (researchBtn) {
        researchBtn.disabled = true;
        researchBtn.innerHTML = '<span class="btn-text">⏳ Đang phân tích...</span>';
    }
    if (resultDiv) {
        resultDiv.innerHTML = '<div class="research-loading"><span>⏳</span> Đang xử lý...</div>';
    }

    try {
        let res, result;

        if (type === 'summary') {
            // ✅ TÓM TẮT: dùng model summarize service
            res = await fetch('/api/tools/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: state.selectedText,
                    debug: false
                })
            });
            result = await res.json();

            if (res.ok && result.success) {
                // render giống summary text
                resultDiv.innerHTML = `<div class="research-text">${escapeHtml(result.result || '')}</div>`;
            } else {
                resultDiv.innerHTML = `<div class="research-error">❌ ${escapeHtml(result.error || 'Tóm tắt thất bại')}</div>`;
            }

        } else {
            // ✅ TỪ KHÓA: vẫn dùng research như cũ
            res = await fetch('/api/tools/research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: state.selectedText, type })
            });
            result = await res.json();

            let html = '';

            if (type === 'keywords' && result.success) {
                const keywords = result.result || [];
                const processingTime = result.processing_time_ms || 0;
                const method = result.method || 'unknown';

                if (keywords.length > 0) {
                    html = `
                        <div class="keywords-result">
                            <div class="keywords-header">
                                <span class="keywords-count">🔑 ${keywords.length} từ khóa</span>
                                <span class="keywords-time">⚡ ${processingTime}ms</span>
                            </div>
                            <div class="keywords-grid">
                                ${keywords.map((k, i) => {
                        const keyword = typeof k === 'object' ? k.keyword : k;
                        const score = typeof k === 'object' ? k.score : null;
                        const count = typeof k === 'object' ? k.count : null;
                        const pos = typeof k === 'object' ? k.pos : null;

                        const colorClass = i < 3 ? 'keyword-top' : (i < 6 ? 'keyword-mid' : 'keyword-low');

                        return `
                                        <div class="keyword-item ${colorClass}" title="POS: ${pos || 'N/A'}, Điểm: ${score || 'N/A'}">
                                            <span class="keyword-rank">#${i + 1}</span>
                                            <span class="keyword-text">${escapeHtml(keyword)}</span>
                                            ${count ? `<span class="keyword-count">×${count}</span>` : ''}
                                            <button class="keyword-search-btn" onclick="searchKeyword('${escapeHtml(keyword).replace(/'/g, "\\'")}')">🔍</button>
                                        </div>
                                    `;
                    }).join('')}
                            </div>
                            <div class="keywords-footer">
                                <span class="keywords-method">Phương pháp: ${method === 'hybrid_vietnamese' ? 'Hybrid (POS + TF)' : 'Fallback'}</span>
                            </div>
                        </div>
                    `;
                } else {
                    html = '<div class="research-empty">Không tìm thấy từ khóa nào.</div>';
                }
            } else if (Array.isArray(result.result)) {
                html = '<ul class="research-list">' +
                    result.result.map(r => `<li>${escapeHtml(typeof r === 'object' ? r.keyword || JSON.stringify(r) : r)}</li>`).join('') +
                    '</ul>';
            } else if (result.result) {
                html = `<div class="research-text">${escapeHtml(result.result)}</div>`;
            } else if (result.error) {
                html = `<div class="research-error">❌ ${escapeHtml(result.error)}</div>`;
            }

            resultDiv.innerHTML = html;
        }

    } catch (e) {
        resultDiv.innerHTML = '<div class="research-error">❌ Lỗi kết nối. Vui lòng thử lại.</div>';
    } finally {
        if (researchBtn) {
            researchBtn.disabled = false;
            researchBtn.innerHTML = '<span class="btn-text">🔍 Phân tích</span>';
        }
    }
}

/**
 * Open Google search with keyword in new tab
 * @param {string} keyword - Keyword to search
 */
function searchKeyword(keyword) {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(keyword)}`;
    window.open(searchUrl, '_blank');
}

/**
 * Show a result modal with optional TTS audio player support
 * @param {string} title - Modal title
 * @param {string|object} content - Content string or object with audioUrl and fromCache for TTS
 * Requirements: 2.3, 2.4, 4.4
 */
function showResultModal(title, content) {
    let bodyContent;

    // Check if content is a TTS result object
    if (content && typeof content === 'object' && content.audioUrl) {
        // Render enhanced audio player for TTS results
        bodyContent = renderAudioPlayer(content.audioUrl, content.fromCache);

        // Schedule audio element reference storage after DOM update
        setTimeout(() => {
            const audioElement = document.getElementById('tts-audio-element');
            if (audioElement) {
                ttsState.currentAudio = audioElement;
            }
        }, 0);
    } else if (content && typeof content === 'object' && content.error) {
        // Render error message for failed TTS generation
        bodyContent = `
            <div class="tts-error">
                <span class="error-icon">❌</span>
                <span class="error-message">${content.error}</span>
            </div>
        `;
    } else {
        // Regular content (string)
        bodyContent = content;
    }

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>${title}</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="result-panel">${bodyContent}</div>
    `;
    elements.modalOverlay.classList.remove('hidden');
}

/**
 * Render enhanced audio player with native controls, cache indicator, and download button
 * @param {string} audioUrl - URL of the audio file
 * @param {boolean} fromCache - Whether the audio was served from cache
 * @returns {string} HTML string for the audio player
 * Requirements: 4.1, 4.2, 4.3
 */
function renderAudioPlayer(audioUrl, fromCache) {
    const cacheIndicator = fromCache
        ? '<span class="cache-badge cached">📦 Từ cache</span>'
        : '<span class="cache-badge new">✨ Mới tạo</span>';

    // Extract filename from URL for download
    const filename = audioUrl.split('/').pop() || 'audio.mp3';

    return `
        <div class="audio-player-container">
            <div class="audio-player-header">
                ${cacheIndicator}
            </div>
            <div class="audio-player-main">
                <audio
                    controls
                    src="${audioUrl}"
                    class="tts-audio-player"
                    preload="metadata"
                    id="tts-audio-element"
                >
                    Trình duyệt của bạn không hỗ trợ phát audio.
                </audio>
            </div>
            <div class="audio-player-actions">
                <a href="${audioUrl}" download="${filename}" class="btn btn-secondary btn-sm download-audio-btn">
                    <span class="download-icon">⬇️</span>
                    <span>Tải xuống</span>
                </a>
            </div>
        </div>
    `;
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
            <button class="work-item-delete" onclick="event.stopPropagation(); deleteWork(${w.id})" title="Xóa">✕</button>
            <div class="work-item-title" ondblclick="event.stopPropagation(); editWorkTitle(${w.id}, this)" title="Double-click để sửa tên">${w.title}</div>
            <div class="work-item-meta">${w.block_count} blocks • ${new Date(w.created_at).toLocaleDateString('vi')}</div>
        </div>
    `).join('');
}

/**
 * Edit work title inline
 */
function editWorkTitle(workId, titleElement) {
    const currentTitle = titleElement.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentTitle;
    input.className = 'work-title-input';
    input.onclick = (e) => e.stopPropagation();

    // Save on blur or Enter
    const saveTitle = async () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== currentTitle) {
            try {
                const res = await fetch(`/api/works/${workId}/rename`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: newTitle })
                });
                const data = await res.json();
                if (data.success) {
                    // Update state
                    const work = state.works.find(w => w.id === workId);
                    if (work) work.title = newTitle;
                    showToast('✅ Đã đổi tên thành công!', 'success');
                } else {
                    showToast('⚠️ Lỗi đổi tên: ' + (data.error || 'Unknown'), 'error');
                }
            } catch (e) {
                showToast('⚠️ Lỗi kết nối', 'error');
            }
        }
        // Replace input with title
        titleElement.textContent = input.value.trim() || currentTitle;
        titleElement.style.display = '';
        input.remove();
    };

    input.onblur = saveTitle;
    input.onkeydown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            input.blur();
        } else if (e.key === 'Escape') {
            titleElement.textContent = currentTitle;
            titleElement.style.display = '';
            input.remove();
        }
    };

    // Hide original title and show input
    titleElement.style.display = 'none';
    titleElement.parentNode.insertBefore(input, titleElement);
    input.focus();
    input.select();
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
            // Mark active work
            document.querySelectorAll('.work-item').forEach(el => el.classList.remove('active'));
            const activeItem = document.querySelector(`.work-item[onclick*="loadWork(${id})"]`);
            if (activeItem) activeItem.classList.add('active');
        }
    } catch (e) {
        alert('Lỗi tải work');
    }
}

// Delete work
async function deleteWork(id) {
    if (!confirm('Bạn có chắc muốn xóa mục này?')) return;

    try {
        const res = await fetch(`/api/works/${id}`, {
            method: 'DELETE'
        });
        if (res.ok) {
            state.works = state.works.filter(w => w.id !== id);
            renderWorkList();
            // Clear text blocks if deleted work was active
            state.textBlocks = [];
            renderTextBlocks();
        } else {
            const data = await res.json();
            alert(data.error || 'Xóa thất bại');
        }
    } catch (e) {
        alert('Lỗi kết nối');
    }
}

// Start new process - reset UI for new image
function startNewProcess() {
    // Clear current state
    state.selectedFiles = [];
    state.textBlocks = [];

    // Reset UI
    elements.previewSection.classList.add('hidden');
    elements.imagePreview.innerHTML = '';
    elements.processBtn.disabled = true;
    elements.fileInput.value = '';

    // Clear text blocks display
    elements.textBlocks.innerHTML = `
        <div class="empty-state" id="empty-results">
            <div class="empty-state-icon">📝</div>
            <h4>Kết quả OCR sẽ hiển thị ở đây</h4>
            <p>Tải ảnh lên và nhấn "Xử lý OCR" để bắt đầu</p>
        </div>
    `;

    // Remove active state from work items
    document.querySelectorAll('.work-item').forEach(el => el.classList.remove('active'));

    // Hide tools panel
    elements.toolsPanel.classList.add('hidden');
}

// Modal overlay click behavior - DISABLED to prevent accidental closing
// To close modal, user must click the X button
// elements.modalOverlay.addEventListener('click', (e) => {
//     if (e.target === elements.modalOverlay) closeModal();
// });

let modelTranslateLastText = "";

async function translateAllByModel() {
    if (!state.user) {
        alert('Vui lòng đăng nhập để dịch');
        showLoginModal();
        return;
    }

    if (!state.textBlocks || state.textBlocks.length === 0) return;

    const combinedText = state.textBlocks
        .map(b => (b.text || '').trim())
        .filter(t => t.length > 0)
        .join('\n\n');

    if (!combinedText.trim()) return;

    showResultModal('🌐 Dịch tất cả (Model Vi→En)', `
        <div class="translate-loading">
            <span class="loading-spinner">⏳</span>
            <span class="loading-text">Đang dịch bằng model...</span>
        </div>
    `);

    try {
        const res = await fetch('/api/tools/translate-model-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: combinedText })
        });

        const result = await res.json();

        modelTranslateLastText = result.translated_text || '';
        showResultModal('🌐 Kết quả dịch (Model Vi→En)', renderModelTranslationResult(modelTranslateLastText));
        showToast('✅ Dịch xong!', 'success');
    } catch (e) {
        // bỏ luôn lỗi: im lặng
    }
}

function renderModelTranslationResult(text) {
    return `
        <div class="translation-result-container">
            <div class="translation-result-header" style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div style="font-weight:600;">✅ Dịch xong</div>
                <div class="translation-result-actions" style="display:flex; gap:8px;">
                    <button class="btn-action" onclick="copyModelTranslationResult()" title="Copy">📋</button>
                    <button class="btn-action" onclick="downloadModelTranslationResult()" title="Tải xuống">⬇️</button>
                </div>
            </div>

            <div class="translation-result-text"
                 style="max-height:55vh; overflow:auto; white-space:pre-wrap; word-break:break-word; margin-top:10px;">
                ${escapeHtml(text || '')}
            </div>
        </div>
    `;
}

function copyModelTranslationResult() {
    const text = modelTranslateLastText || '';
    if (!text.trim()) return;

    navigator.clipboard.writeText(text);
}

function downloadModelTranslationResult() {
    const text = modelTranslateLastText || '';
    if (!text.trim()) return;

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_model_vi-en_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;

    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
}

// ===========================
// SUMMARY (Model) - NEW
// Modal giống "dịch model" (copy + download + save)
// ===========================

let modelSummaryLastText = "";
let modelSummaryLastTitle = "";
let modelSummaryLastInput = ""; // giữ input để copy/download đúng ngữ cảnh (nếu bạn cần sau này)

async function summarizeBlockByModel(blockId) {
    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block) return;

    if (!state.user) {
        alert('Vui lòng đăng nhập để tóm tắt');
        showLoginModal();
        return;
    }

    const text = (block.text || '').trim();
    if (!text) return;

    // giữ input để phục vụ debug tương lai (không dùng rerun nữa nhưng để lại biến)
    modelSummaryLastInput = text;

    // UI loading modal
    showResultModal('📝 Tóm tắt', `
        <div class="translate-loading">
            <span class="loading-spinner">⏳</span>
            <span class="loading-text">Đang tóm tắt...</span>
        </div>
    `);

    try {
        // Gọi API summarize theo 1 thuật toán ensemble bên server (không cần algo nữa)
        const res = await fetch('/api/tools/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text,
                debug: false
            })
        });

        const result = await res.json();

        if (!res.ok || !result.success) {
            showResultModal('📝 Tóm tắt', `
                <div class="translate-error">
                    <span class="error-icon">⚠️</span>
                    <span class="error-message">${escapeHtml(result.error || 'Tóm tắt thất bại')}</span>
                </div>
            `);
            return;
        }

        modelSummaryLastText = result.result || '';
        modelSummaryLastTitle = block.title || 'Untitled';

        showResultModal('📝 Kết quả tóm tắt', renderModelSummaryResult(modelSummaryLastText));
        showToast('✅ Tóm tắt xong!', 'success');

    } catch (e) {
        showResultModal('📝 Tóm tắt', `
            <div class="translate-error">
                <span class="error-icon">⚠️</span>
                <span class="error-message">Lỗi kết nối</span>
            </div>
        `);
    }
}

function renderModelSummaryResult(text) {
    return `
        <div class="translation-result-container">
            <div class="translation-result-header" style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div style="font-weight:600;">✅ Tóm tắt xong</div>

                <div class="translation-result-actions" style="display:flex; gap:8px;">
                    <button class="btn-action" onclick="copyModelSummaryResult()" title="Copy">📋</button>
                    <button class="btn-action" onclick="downloadModelSummaryResult()" title="Tải xuống">⬇️</button>
                </div>
            </div>

            <div class="translation-result-text"
                 style="max-height:55vh; overflow:auto; white-space:pre-wrap; word-break:break-word; margin-top:10px;">
                ${escapeHtml(text || '')}
            </div>
        </div>
    `;
}

function copyModelSummaryResult() {
    const text = modelSummaryLastText || '';
    if (!text.trim()) return;
    navigator.clipboard.writeText(text);
    showToast('Đã copy tóm tắt!', 'success');
}

function downloadModelSummaryResult() {
    const text = modelSummaryLastText || '';
    if (!text.trim()) return;

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
}

// ==================== BART CORRECTION ====================
let bartCorrectionState = {
    currentBlockId: null,
    originalText: '',
    correctedText: '',
    evaluation: null
};

/**
 * Run BART correction on a text block
 */
async function runBartCorrection(blockId) {
    if (!state.user) {
        alert('Vui lòng đăng nhập để sử dụng tính năng này');
        showLoginModal();
        return;
    }

    const block = state.textBlocks.find(b => b.id === blockId);
    if (!block || !block.text.trim()) {
        showToast('Không có văn bản để sửa lỗi', 'warning');
        return;
    }

    // Store current block ID
    bartCorrectionState.currentBlockId = blockId;
    bartCorrectionState.originalText = block.text;

    // Show loading modal
    showResultModal('🤖 Sửa lỗi bằng AI', `
        <div class="bart-loading">
            <span class="loading-spinner">⏳</span>
            <span class="loading-text">Đang phân tích và sửa lỗi bằng BARTpho...</span>
        </div>
    `);

    try {
        const res = await fetch('/api/tools/bart-correction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: block.text })
        });

        const result = await res.json();

        if (result.success) {
            bartCorrectionState.correctedText = result.corrected_text;
            bartCorrectionState.evaluation = result.evaluation;

            showBartComparisonModal(result);
        } else {
            showResultModal('🤖 Sửa lỗi bằng AI', `
                <div class="bart-error">
                    <span class="error-icon">❌</span>
                    <span class="error-message">${escapeHtml(result.error || 'Sửa lỗi thất bại')}</span>
                </div>
            `);
        }
    } catch (e) {
        showResultModal('🤖 Sửa lỗi bằng AI', `
            <div class="bart-error">
                <span class="error-icon">❌</span>
                <span class="error-message">Lỗi kết nối</span>
            </div>
        `);
    }
}

/**
 * Show BART comparison modal with original vs corrected text
 */
function showBartComparisonModal(result) {
    const eval_data = result.evaluation || {};

    // Determine quality color based on similarity
    const similarity = eval_data.similarity_score || 0;
    let qualityClass = 'quality-good';
    let qualityLabel = '✅ Tốt';
    if (similarity < 70) {
        qualityClass = 'quality-warning';
        qualityLabel = '⚠️ Thay đổi nhiều';
    } else if (similarity < 50) {
        qualityClass = 'quality-danger';
        qualityLabel = '⛔ Thay đổi rất nhiều';
    }

    // Character diff display
    const charDiff = eval_data.char_diff || 0;
    const charDiffDisplay = charDiff > 0 ? `+${charDiff}` : charDiff.toString();
    const charDiffClass = charDiff > 0 ? 'diff-increase' : (charDiff < 0 ? 'diff-decrease' : 'diff-neutral');

    elements.modalContent.innerHTML = `
        <div class="modal-header">
            <h3>🤖 Kết quả sửa lỗi AI</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="bart-comparison-body">
            <!-- Quality Badge -->
            <div class="bart-quality-badge ${qualityClass}">
                ${qualityLabel} • Độ tương đồng: ${similarity}%
            </div>
            
            <!-- Evaluation Stats Grid -->
            <div class="bart-evaluation-grid">
                <div class="eval-card">
                    <div class="eval-card-icon">📝</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Ký tự gốc</div>
                        <div class="eval-card-value">${eval_data.original_char_count || 0}</div>
                    </div>
                </div>
                <div class="eval-card">
                    <div class="eval-card-icon">✅</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Ký tự sau sửa</div>
                        <div class="eval-card-value">
                            ${eval_data.corrected_char_count || 0}
                            <span class="eval-card-diff ${charDiffClass}">(${charDiffDisplay})</span>
                        </div>
                    </div>
                </div>
                <div class="eval-card">
                    <div class="eval-card-icon">📊</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Từ gốc → Sau sửa</div>
                        <div class="eval-card-value">${eval_data.original_word_count || 0} → ${eval_data.corrected_word_count || 0}</div>
                    </div>
                </div>
                <div class="eval-card">
                    <div class="eval-card-icon">📑</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Số câu</div>
                        <div class="eval-card-value">${eval_data.original_sentence_count || 0} → ${eval_data.corrected_sentence_count || 0}</div>
                    </div>
                </div>
                <div class="eval-card highlight">
                    <div class="eval-card-icon">🔄</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Từ thay đổi</div>
                        <div class="eval-card-value">${eval_data.changes_count || 0} <span class="eval-card-percent">(${eval_data.change_rate || 0}%)</span></div>
                    </div>
                </div>
                <div class="eval-card">
                    <div class="eval-card-icon">🎯</div>
                    <div class="eval-card-content">
                        <div class="eval-card-label">Độ tương đồng</div>
                        <div class="eval-card-value similarity-bar">
                            <div class="similarity-fill" style="width: ${similarity}%"></div>
                            <span>${similarity}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Comparison View -->
            <div class="bart-comparison-grid">
                <div class="comparison-column">
                    <h4>📄 Văn bản gốc</h4>
                    <div class="comparison-text original">${escapeHtml(result.original_text || '')}</div>
                </div>
                <div class="comparison-column">
                    <h4>✨ Văn bản đã sửa</h4>
                    <div class="comparison-text corrected">${escapeHtml(result.corrected_text || '')}</div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="bart-actions">
                <button class="btn btn-secondary" onclick="useBartOriginal()">
                    📄 Giữ bản gốc
                </button>
                <button class="btn btn-primary" onclick="useBartCorrected()">
                    ✨ Dùng bản đã sửa
                </button>
            </div>
        </div>
    `;

    elements.modalOverlay.classList.remove('hidden');
}

/**
 * Use original text (close modal without changes)
 */
function useBartOriginal() {
    closeModal();
    showToast('✅ Đã giữ nguyên bản gốc', 'info');
    bartCorrectionState = { currentBlockId: null, originalText: '', correctedText: '', evaluation: null };
}

/**
 * Use corrected text (update text block)
 */
function useBartCorrected() {
    const blockId = bartCorrectionState.currentBlockId;
    const correctedText = bartCorrectionState.correctedText;

    if (blockId && correctedText) {
        // Update state
        const block = state.textBlocks.find(b => b.id === blockId);
        if (block) {
            block.text = correctedText;
        }

        // Update textarea in DOM
        const textarea = document.querySelector(`textarea[data-id="${blockId}"]`);
        if (textarea) {
            textarea.value = correctedText;
        }

        showToast('✅ Đã áp dụng bản sửa lỗi!', 'success');
    }

    closeModal();
    bartCorrectionState = { currentBlockId: null, originalText: '', correctedText: '', evaluation: null };
}

