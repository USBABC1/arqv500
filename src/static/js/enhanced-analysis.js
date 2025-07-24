/**
 * ARQV30 Enhanced - JavaScript Principal
 * Funcionalidades avançadas para análise de mercado
 */

// Estado global da aplicação
const AppState = {
    sessionId: generateSessionId(),
    attachments: [],
    currentAnalysis: null,
    isAnalyzing: false
};

// Configurações
const CONFIG = {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedExtensions: ['pdf', 'doc', 'docx', 'txt', 'json', 'csv', 'xlsx', 'xls'],
    apiBaseUrl: '/api'
};

/**
 * Inicialização da aplicação
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 Inicializando ARQV30 Enhanced v2.0');
    
    // Verificar status do sistema
    checkSystemStatus();
    
    // Inicializar componentes
    initializeFileUpload();
    initializeForm();
    initializeTooltips();
    
    // Auto-save do formulário
    initializeAutoSave();
    
    console.log('✅ Aplicação inicializada com sucesso');
}

/**
 * Verificação de status do sistema
 */
function checkSystemStatus() {
    fetch(`${CONFIG.apiBaseUrl}/app_status`)
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data);
            logSystemInfo(data);
        })
        .catch(error => {
            console.error('❌ Erro ao verificar status do sistema:', error);
            updateStatusIndicator({ status: 'error', message: 'Erro de conexão' });
        });
}

function updateStatusIndicator(data) {
    const statusText = document.getElementById('status-text');
    const statusDot = document.querySelector('.status-dot');
    const versionInfo = document.getElementById('version-info');
    
    if (data.status === 'running') {
        statusText.textContent = 'Sistema Online';
        statusText.style.color = '#10b981';
        statusDot.style.background = '#10b981';
    } else {
        statusText.textContent = data.message || 'Sistema com Problemas';
        statusText.style.color = '#ef4444';
        statusDot.style.background = '#ef4444';
    }
    
    if (versionInfo) {
        versionInfo.textContent = `v${data.version || '2.0.0'}`;
    }
}

function logSystemInfo(data) {
    console.log('📊 Status do Sistema:', data);
    
    if (data.services) {
        console.log('🤖 Gemini:', data.services.gemini?.available ? '✅' : '❌');
        console.log('🚢 WebSailor:', data.services.websailor?.available ? '✅' : '❌');
        console.log('🔍 Deep Search:', data.services.deep_search?.available ? '✅' : '❌');
        console.log('📎 Attachments:', data.services.attachments?.available ? '✅' : '❌');
    }
}

/**
 * Sistema de upload de arquivos
 */
function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // Click para selecionar arquivos
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Seleção de arquivos
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
}

function handleFiles(files) {
    console.log(`📁 Processando ${files.length} arquivo(s)`);
    
    Array.from(files).forEach(file => {
        if (validateFile(file)) {
            uploadFile(file);
        }
    });
}

function validateFile(file) {
    // Verificar tamanho
    if (file.size > CONFIG.maxFileSize) {
        showNotification(`Arquivo "${file.name}" é muito grande. Máximo: 10MB`, 'error');
        return false;
    }
    
    // Verificar extensão
    const extension = file.name.split('.').pop().toLowerCase();
    if (!CONFIG.allowedExtensions.includes(extension)) {
        showNotification(`Tipo de arquivo "${extension}" não suportado`, 'error');
        return false;
    }
    
    return true;
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', AppState.sessionId);
    
    // Mostrar progresso
    const attachmentId = Date.now().toString();
    addAttachmentToList(file, attachmentId, 'uploading');
    
    fetch(`${CONFIG.apiBaseUrl}/upload_attachment`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateAttachmentStatus(attachmentId, 'success', data);
            AppState.attachments.push({
                id: data.attachment_id,
                filename: file.name,
                content_type: data.content_type,
                preview: data.content_preview
            });
            showNotification(`Anexo "${file.name}" processado com sucesso`, 'success');
        } else {
            updateAttachmentStatus(attachmentId, 'error', data);
            showNotification(`Erro ao processar "${file.name}": ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Erro no upload:', error);
        updateAttachmentStatus(attachmentId, 'error', { error: error.message });
        showNotification(`Erro no upload de "${file.name}"`, 'error');
    });
}

function addAttachmentToList(file, attachmentId, status) {
    const attachmentList = document.getElementById('attachmentList');
    
    const attachmentItem = document.createElement('div');
    attachmentItem.className = 'attachment-item';
    attachmentItem.id = `attachment-${attachmentId}`;
    
    const statusIcon = getStatusIcon(status);
    const fileIcon = getFileIcon(file.name);
    
    attachmentItem.innerHTML = `
        <div class="attachment-info">
            <i class="${fileIcon} attachment-icon"></i>
            <div>
                <div style="font-weight: 500;">${file.name}</div>
                <div style="font-size: 0.8rem; color: #6b7280;">
                    ${formatFileSize(file.size)} • ${status === 'uploading' ? 'Processando...' : 'Pronto'}
                </div>
            </div>
        </div>
        <div class="attachment-status">
            <i class="${statusIcon}" style="margin-right: 8px;"></i>
            <button class="remove-attachment" onclick="removeAttachment('${attachmentId}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    attachmentList.appendChild(attachmentItem);
}

function updateAttachmentStatus(attachmentId, status, data) {
    const attachmentItem = document.getElementById(`attachment-${attachmentId}`);
    if (!attachmentItem) return;
    
    const statusIcon = getStatusIcon(status);
    const statusElement = attachmentItem.querySelector('.attachment-status i');
    const infoElement = attachmentItem.querySelector('.attachment-info div div:last-child');
    
    if (statusElement) {
        statusElement.className = statusIcon;
    }
    
    if (infoElement) {
        if (status === 'success') {
            infoElement.innerHTML = `${infoElement.innerHTML.split(' • ')[0]} • ${data.content_type || 'Processado'}`;
        } else if (status === 'error') {
            infoElement.innerHTML = `${infoElement.innerHTML.split(' • ')[0]} • Erro: ${data.error || 'Falha no upload'}`;
        }
    }
}

function getStatusIcon(status) {
    switch (status) {
        case 'uploading': return 'fas fa-spinner fa-spin';
        case 'success': return 'fas fa-check-circle text-green-500';
        case 'error': return 'fas fa-exclamation-circle text-red-500';
        default: return 'fas fa-file';
    }
}

function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    switch (extension) {
        case 'pdf': return 'fas fa-file-pdf';
        case 'doc':
        case 'docx': return 'fas fa-file-word';
        case 'txt': return 'fas fa-file-alt';
        case 'json': return 'fas fa-file-code';
        case 'csv':
        case 'xlsx':
        case 'xls': return 'fas fa-file-excel';
        default: return 'fas fa-file';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeAttachment(attachmentId) {
    const attachmentItem = document.getElementById(`attachment-${attachmentId}`);
    if (attachmentItem) {
        attachmentItem.remove();
    }
    
    // Remover do estado
    AppState.attachments = AppState.attachments.filter(att => att.id !== attachmentId);
    
    showNotification('Anexo removido', 'info');
}

/**
 * Sistema de formulário
 */
function initializeForm() {
    const form = document.getElementById('analysisForm');
    form.addEventListener('submit', handleFormSubmit);
    
    // Validação em tempo real
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    if (AppState.isAnalyzing) {
        showNotification('Análise já em andamento', 'warning');
        return;
    }
    
    if (!validateForm()) {
        return;
    }
    
    startAnalysis();
}

function validateForm() {
    const form = document.getElementById('analysisForm');
    const formData = new FormData(form);
    
    // Verificar campos obrigatórios
    const segmento = formData.get('segmento');
    if (!segmento || segmento.trim().length < 3) {
        showNotification('Segmento de mercado é obrigatório (mín. 3 caracteres)', 'error');
        document.getElementById('segmento').focus();
        return false;
    }
    
    return true;
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'Este campo é obrigatório');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.style.borderColor = '#ef4444';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#ef4444';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '4px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Sistema de análise
 */
function startAnalysis() {
    console.log('🔍 Iniciando análise ultra-detalhada');
    
    AppState.isAnalyzing = true;
    
    // Coletar dados do formulário
    const formData = collectFormData();
    
    // Mostrar loading
    showLoadingScreen();
    
    // Enviar para análise
    performAnalysis(formData);
}

function collectFormData() {
    const form = document.getElementById('analysisForm');
    const formData = new FormData(form);
    
    const data = {
        segmento: formData.get('segmento'),
        produto: formData.get('produto'),
        publico: formData.get('publico'),
        preco: formData.get('preco'),
        concorrentes: formData.get('concorrentes'),
        objetivoReceita: formData.get('objetivoReceita'),
        orcamentoMarketing: formData.get('orcamentoMarketing'),
        prazoLancamento: formData.get('prazoLancamento'),
        query: formData.get('query'),
        dadosAdicionais: formData.get('dadosAdicionais'),
        session_id: AppState.sessionId
    };
    
    console.log('📋 Dados coletados:', data);
    return data;
}

function showLoadingScreen() {
    document.querySelector('.form-section').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';
    
    // Simular progresso
    simulateProgress();
}

function simulateProgress() {
    const steps = [
        'Processando dados do formulário...',
        'Analisando anexos enviados...',
        'Realizando busca profunda na internet...',
        'Executando WebSailor para navegação avançada...',
        'Processando com Gemini Pro 2.5...',
        'Consolidando insights e resultados...',
        'Finalizando análise ultra-detalhada...'
    ];
    
    const progressSteps = document.getElementById('progressSteps');
    const loadingStatus = document.getElementById('loadingStatus');
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepElement = document.createElement('div');
            stepElement.className = 'progress-step';
            stepElement.innerHTML = `✅ ${steps[currentStep]}`;
            progressSteps.appendChild(stepElement);
            
            if (currentStep + 1 < steps.length) {
                loadingStatus.textContent = steps[currentStep + 1];
            }
            
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 2000);
}

function performAnalysis(data) {
    fetch(`${CONFIG.apiBaseUrl}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log('✅ Análise concluída:', result);
        AppState.currentAnalysis = result;
        showResults(result);
    })
    .catch(error => {
        console.error('❌ Erro na análise:', error);
        showAnalysisError(error);
    })
    .finally(() => {
        AppState.isAnalyzing = false;
    });
}

function showResults(result) {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    const resultsContainer = document.getElementById('analysisResults');
    resultsContainer.innerHTML = formatAnalysisResults(result);
    
    // Scroll para os resultados
    document.getElementById('resultsSection').scrollIntoView({ 
        behavior: 'smooth' 
    });
    
    showNotification('Análise ultra-detalhada concluída com sucesso!', 'success');
}

function formatAnalysisResults(result) {
    let html = '';
    
    // Informações sobre contextos utilizados
    if (result.search_context_used || result.websailor_used || result.attachments_used) {
        html += `
            <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 10px; padding: 20px; margin-bottom: 30px;">
                <h3 style="color: #0369a1; margin-bottom: 15px;">
                    <i class="fas fa-info-circle"></i> Contextos Utilizados na Análise
                </h3>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    ${result.websailor_used ? '<div><i class="fas fa-ship" style="color: #10b981;"></i> WebSailor Navigation</div>' : ''}
                    ${result.search_context_used ? '<div><i class="fas fa-search" style="color: #10b981;"></i> Busca Profunda</div>' : ''}
                    ${result.attachments_used ? '<div><i class="fas fa-paperclip" style="color: #10b981;"></i> Análise de Anexos</div>' : ''}
                </div>
            </div>
        `;
    }
    
    // Resultados principais
    if (result.avatar_ultra_detalhado) {
        html += formatSection('Avatar Ultra-Detalhado', result.avatar_ultra_detalhado, 'fas fa-user-circle');
    }
    
    if (result.escopo) {
        html += formatSection('Escopo e Posicionamento', result.escopo, 'fas fa-bullseye');
    }
    
    if (result.analise_concorrencia_detalhada) {
        html += formatSection('Análise de Concorrência', result.analise_concorrencia_detalhada, 'fas fa-chess');
    }
    
    if (result.estrategia_palavras_chave) {
        html += formatSection('Estratégia de Marketing', result.estrategia_palavras_chave, 'fas fa-megaphone');
    }
    
    if (result.metricas_performance_detalhadas) {
        html += formatSection('Métricas de Performance', result.metricas_performance_detalhadas, 'fas fa-chart-bar');
    }
    
    if (result.projecoes_cenarios) {
        html += formatSection('Projeções e Cenários', result.projecoes_cenarios, 'fas fa-chart-line');
    }
    
    if (result.inteligencia_mercado) {
        html += formatSection('Inteligência de Mercado', result.inteligencia_mercado, 'fas fa-brain');
    }
    
    if (result.plano_acao_detalhado) {
        html += formatSection('Plano de Ação', result.plano_acao_detalhado, 'fas fa-tasks');
    }
    
    if (result.insights_exclusivos) {
        html += formatInsights(result.insights_exclusivos);
    }
    
    return html;
}

function formatSection(title, data, icon) {
    if (!data || typeof data !== 'object') {
        return '';
    }
    
    let content = '';
    
    for (const [key, value] of Object.entries(data)) {
        if (value && typeof value === 'object') {
            content += `<h4 style="color: #374151; margin: 20px 0 10px 0;">${formatKey(key)}</h4>`;
            content += formatObject(value);
        } else if (value) {
            content += `<p><strong>${formatKey(key)}:</strong> ${value}</p>`;
        }
    }
    
    return `
        <div style="background: white; border-radius: 15px; padding: 30px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: #1f2937; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <i class="${icon}"></i> ${title}
            </h3>
            ${content}
        </div>
    `;
}

function formatObject(obj, level = 0) {
    let html = '';
    const indent = level * 20;
    
    for (const [key, value] of Object.entries(obj)) {
        if (value && typeof value === 'object') {
            html += `<div style="margin-left: ${indent}px; margin-bottom: 15px;">`;
            html += `<h5 style="color: #4b5563; margin-bottom: 8px;">${formatKey(key)}</h5>`;
            html += formatObject(value, level + 1);
            html += `</div>`;
        } else if (Array.isArray(value)) {
            html += `<div style="margin-left: ${indent}px; margin-bottom: 15px;">`;
            html += `<strong>${formatKey(key)}:</strong>`;
            html += `<ul style="margin: 8px 0 0 20px;">`;
            value.forEach(item => {
                html += `<li>${item}</li>`;
            });
            html += `</ul></div>`;
        } else if (value) {
            html += `<p style="margin-left: ${indent}px;"><strong>${formatKey(key)}:</strong> ${value}</p>`;
        }
    }
    
    return html;
}

function formatInsights(insights) {
    if (!Array.isArray(insights)) return '';
    
    let html = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 30px; margin-bottom: 25px;">
            <h3 style="margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-lightbulb"></i> Insights Exclusivos
            </h3>
            <div style="display: grid; gap: 15px;">
    `;
    
    insights.forEach((insight, index) => {
        html += `
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px;">
                <div style="display: flex; align-items: flex-start; gap: 15px;">
                    <div style="background: rgba(255,255,255,0.2); border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                        ${index + 1}
                    </div>
                    <div style="flex: 1;">
                        ${insight}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div></div>`;
    return html;
}

function formatKey(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase());
}

function showAnalysisError(error) {
    document.getElementById('loadingSection').style.display = 'none';
    document.querySelector('.form-section').style.display = 'block';
    
    showNotification(`Erro na análise: ${error.message || 'Erro desconhecido'}`, 'error');
    
    AppState.isAnalyzing = false;
}

/**
 * Funcionalidades auxiliares
 */
function generatePDF() {
    if (!AppState.currentAnalysis) {
        showNotification('Nenhuma análise disponível para gerar PDF', 'warning');
        return;
    }
    
    showNotification('Gerando PDF...', 'info');
    
    fetch(`${CONFIG.apiBaseUrl}/generate_pdf`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            report_content: AppState.currentAnalysis
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erro ao gerar PDF');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analise_arqv30_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('PDF gerado com sucesso!', 'success');
    })
    .catch(error => {
        console.error('❌ Erro ao gerar PDF:', error);
        showNotification('Erro ao gerar PDF', 'error');
    });
}

function resetForm() {
    // Limpar estado
    AppState.attachments = [];
    AppState.currentAnalysis = null;
    AppState.sessionId = generateSessionId();
    
    // Resetar interface
    document.getElementById('resultsSection').style.display = 'none';
    document.querySelector('.form-section').style.display = 'block';
    document.getElementById('analysisForm').reset();
    document.getElementById('attachmentList').innerHTML = '';
    
    // Limpar erros
    document.querySelectorAll('.field-error').forEach(error => error.remove());
    document.querySelectorAll('.form-control').forEach(field => {
        field.style.borderColor = '';
    });
    
    showNotification('Formulário resetado', 'info');
}

/**
 * Sistema de notificações
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = getNotificationIcon(type);
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2rem;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Estilos da notificação
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '10px',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        minWidth: '300px',
        maxWidth: '500px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        animation: 'slideInRight 0.3s ease-out'
    });
    
    // Cores por tipo
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
    
    console.log(`📢 ${type.toUpperCase()}: ${message}`);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-bell';
    }
}

/**
 * Auto-save do formulário
 */
function initializeAutoSave() {
    const form = document.getElementById('analysisForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', debounce(saveFormData, 1000));
    });
    
    // Carregar dados salvos
    loadFormData();
}

function saveFormData() {
    const form = document.getElementById('analysisForm');
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem('arqv30_form_data', JSON.stringify(data));
    console.log('💾 Dados do formulário salvos automaticamente');
}

function loadFormData() {
    try {
        const savedData = localStorage.getItem('arqv30_form_data');
        if (savedData) {
            const data = JSON.parse(savedData);
            
            for (const [key, value] of Object.entries(data)) {
                const field = document.querySelector(`[name="${key}"]`);
                if (field && value) {
                    field.value = value;
                }
            }
            
            console.log('📂 Dados do formulário carregados');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar dados salvos:', error);
    }
}

/**
 * Tooltips e ajuda
 */
function initializeTooltips() {
    // Adicionar tooltips aos campos
    const tooltips = {
        'segmento': 'Defina o segmento de mercado principal do seu produto ou serviço',
        'query': 'Descreva o que você quer pesquisar na internet para enriquecer a análise',
        'uploadArea': 'Envie arquivos com drivers mentais, provas visuais, perfis psicológicos ou dados de pesquisa'
    };
    
    for (const [id, text] of Object.entries(tooltips)) {
        const element = document.getElementById(id);
        if (element) {
            element.title = text;
        }
    }
}

/**
 * Utilitários
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Adicionar estilos de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .progress-step {
        padding: 8px 0;
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    .progress-step:last-child {
        color: #10b981;
        font-weight: 500;
    }
`;
document.head.appendChild(style);

// Exportar funções globais
window.generatePDF = generatePDF;
window.resetForm = resetForm;
window.removeAttachment = removeAttachment;

