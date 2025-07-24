// Global variables
let currentAnalysis = null;
let analysisInProgress = false;

// DOM Elements
const sections = {
    home: document.getElementById('home'),
    analyzer: document.getElementById('analyzer'),
    dashboard: document.getElementById('dashboard')
};

const navLinks = document.querySelectorAll('.neo-nav-link');
const analyzerForm = document.getElementById('analyzerForm');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('resultsContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const loadingText = document.getElementById('loadingText');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeForm();
    initializeHeader();
    initializeSearch();
});

// Navigation functionality
function initializeNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            showSection(targetId);
            updateActiveNav(this);
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    Object.values(sections).forEach(section => {
        if (section) section.style.display = 'none';
    });
    
    // Show target section
    if (sections[sectionId]) {
        sections[sectionId].style.display = 'block';
    }
}

function updateActiveNav(activeLink) {
    navLinks.forEach(link => link.classList.remove('active'));
    activeLink.classList.add('active');
}

function showAnalyzer() {
    showSection('analyzer');
    updateActiveNav(document.querySelector('a[href="#analyzer"]'));
}

// Header scroll effect
function initializeHeader() {
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Form functionality
function initializeForm() {
    if (analyzerForm) {
        analyzerForm.addEventListener('submit', handleFormSubmit);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (analysisInProgress) return;
    
    const formData = new FormData(analyzerForm);
    const data = Object.fromEntries(formData.entries());
    
    // Validate required fields
    if (!data.segmento.trim()) {
        showNotification('Por favor, informe o segmento de atuação.', 'error');
        return;
    }
    
    analysisInProgress = true;
    showDashboard();
    showLoading();
    
    try {
        await performAnalysis(data);
    } catch (error) {
        console.error('Erro na análise:', error);
        showNotification('Erro ao realizar análise. Tente novamente.', 'error');
        analysisInProgress = false;
        hideLoading();
    }
}

function showDashboard() {
    showSection('dashboard');
    updateActiveNav(document.querySelector('a[href="#dashboard"]'));
}

function showLoading() {
    loadingState.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Simulate progress with more detailed steps
    simulateProgress();
}

function simulateProgress() {
    const steps = [
        { progress: 5, text: 'Conectando com Gemini Pro 2.5...' },
        { progress: 15, text: 'Pesquisando dados atualizados na internet...' },
        { progress: 25, text: 'Analisando tendências do segmento...' },
        { progress: 35, text: 'Mapeando avatar ultra-detalhado...' },
        { progress: 45, text: 'Identificando concorrência e gaps...' },
        { progress: 55, text: 'Calculando métricas de performance...' },
        { progress: 65, text: 'Analisando comportamento digital...' },
        { progress: 75, text: 'Gerando estratégias de palavras-chave...' },
        { progress: 85, text: 'Criando projeções de cenários...' },
        { progress: 95, text: 'Finalizando análise ultra-detalhada...' },
        { progress: 100, text: 'Análise concluída com sucesso!' }
    ];
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            updateProgress(step.progress, step.text);
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 2000); // 2 seconds per step for more realistic timing
}

function updateProgress(percentage, text) {
    progressBar.style.width = percentage + '%';
    progressText.textContent = percentage + '%';
    loadingText.textContent = text;
}

async function performAnalysis(data) {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentAnalysis = result;
        
        // Wait for progress simulation to complete
        setTimeout(() => {
            hideLoading();
            displayResults(result);
            analysisInProgress = false;
        }, 22000); // 22 seconds total for progress simulation
        
    } catch (error) {
        console.error('Erro na análise:', error);
        hideLoading();
        showNotification('Erro ao realizar análise: ' + error.message, 'error');
        analysisInProgress = false;
    }
}

function hideLoading() {
    loadingState.style.display = 'none';
    resultsContainer.style.display = 'block';
}

function displayResults(analysis) {
    resultsContainer.innerHTML = generateResultsHTML(analysis);
    
    // Initialize interactive elements
    initializeResultsInteractions();
}

function generateResultsHTML(analysis) {
    return `
        <div class="results-header">
            <div class="neo-enhanced-card">
                <div class="neo-card-header">
                    <div class="neo-card-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <h3 class="neo-card-title">Análise Ultra-Detalhada Concluída</h3>
                </div>
                <div class="neo-card-content">
                    <p>Sua análise de avatar foi processada pelo Gemini Pro 2.5 com pesquisa em tempo real na internet. Explore os insights ultra-detalhados abaixo.</p>
                    <div class="results-actions">
                        <button class="neo-cta-button" onclick="downloadReport()">
                            <i class="fas fa-download"></i>
                            <span>Baixar Relatório Completo</span>
                        </button>
                        <button class="neo-cta-button" onclick="shareResults()" style="background: var(--neo-bg); color: var(--text-primary); box-shadow: var(--neo-shadow-1);">
                            <i class="fas fa-share"></i>
                            <span>Compartilhar</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="results-grid">
            ${generateEscopoSection(analysis.escopo)}
            ${generateAvatarUltraDetalhadoSection(analysis.avatar_ultra_detalhado)}
            ${generateDoresUltraDetalhadasSection(analysis.mapeamento_dores_ultra_detalhado)}
            ${generateConcorrenciaDetalhadaSection(analysis.analise_concorrencia_detalhada)}
            ${generateInteligenciaMercadoSection(analysis.inteligencia_mercado)}
            ${generatePalavrasChaveSection(analysis.estrategia_palavras_chave)}
            ${generateMetricasDetalhadasSection(analysis.metricas_performance_detalhadas)}
            ${generateVozMercadoSection(analysis.voz_mercado_linguagem)}
            ${generateProjecoesCenariosSection(analysis.projecoes_cenarios)}
            ${generatePlanoAcaoDetalhadoSection(analysis.plano_acao_detalhado)}
            ${generateInsightsExclusivosSection(analysis.insights_exclusivos)}
        </div>
    `;
}

function generateEscopoSection(escopo) {
    if (!escopo) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-bullseye"></i>
                </div>
                <h3 class="neo-card-title">Escopo Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="escopo-content">
                    <div class="detail-item">
                        <strong>Segmento Principal:</strong>
                        <p>${escopo.segmento_principal}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Subsegmentos Identificados:</strong>
                        <ul>
                            ${escopo.subsegmentos?.map(sub => `<li>${sub}</li>`).join('') || ''}
                        </ul>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Produto Ideal:</strong>
                        <p>${escopo.produto_ideal}</p>
                    </div>
                    
                    <div class="detail-item">
                        <strong>Proposta de Valor:</strong>
                        <blockquote>${escopo.proposta_valor}</blockquote>
                    </div>
                    
                    ${escopo.tamanho_mercado ? `
                    <div class="detail-item">
                        <strong>Tamanho do Mercado:</strong>
                        <div class="market-size-grid">
                            <div class="market-metric">
                                <span class="metric-label">TAM</span>
                                <span class="metric-value">${escopo.tamanho_mercado.tam}</span>
                            </div>
                            <div class="market-metric">
                                <span class="metric-label">SAM</span>
                                <span class="metric-value">${escopo.tamanho_mercado.sam}</span>
                            </div>
                            <div class="market-metric">
                                <span class="metric-label">SOM</span>
                                <span class="metric-value">${escopo.tamanho_mercado.som}</span>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateAvatarUltraDetalhadoSection(avatar) {
    if (!avatar) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-user-circle"></i>
                </div>
                <h3 class="neo-card-title">Avatar Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="avatar-profile">
                    ${avatar.persona_principal ? `
                    <div class="avatar-section">
                        <h4>Persona Principal</h4>
                        <div class="persona-card">
                            <div class="persona-info">
                                <h5>${avatar.persona_principal.nome}</h5>
                                <p><strong>Idade:</strong> ${avatar.persona_principal.idade}</p>
                                <p><strong>Profissão:</strong> ${avatar.persona_principal.profissao}</p>
                                <p><strong>Renda:</strong> ${avatar.persona_principal.renda_mensal}</p>
                                <p><strong>Localização:</strong> ${avatar.persona_principal.localizacao}</p>
                                <p><strong>Estado Civil:</strong> ${avatar.persona_principal.estado_civil}</p>
                                <p><strong>Escolaridade:</strong> ${avatar.persona_principal.escolaridade}</p>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.demografia_detalhada ? `
                    <div class="avatar-section">
                        <h4>Demografia Detalhada</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <strong>Faixa Etária Primária:</strong>
                                <p>${avatar.demografia_detalhada.faixa_etaria_primaria}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Faixa Etária Secundária:</strong>
                                <p>${avatar.demografia_detalhada.faixa_etaria_secundaria}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Distribuição por Gênero:</strong>
                                <p>${avatar.demografia_detalhada.distribuicao_genero}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Distribuição Geográfica:</strong>
                                <p>${avatar.demografia_detalhada.distribuicao_geografica}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Classes Sociais:</strong>
                                <p>${avatar.demografia_detalhada.classes_sociais}</p>
                            </div>
                            <div class="detail-item">
                                <strong>Nível Educacional:</strong>
                                <p>${avatar.demografia_detalhada.nivel_educacional}</p>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.psicografia_profunda ? `
                    <div class="avatar-section">
                        <h4>Psicografia Profunda</h4>
                        <div class="detail-item">
                            <strong>Valores Fundamentais:</strong>
                            <ul>
                                ${avatar.psicografia_profunda.valores_fundamentais?.map(valor => `<li>${valor}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Estilo de Vida:</strong>
                            <p>${avatar.psicografia_profunda.estilo_vida_detalhado}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Personalidade Dominante:</strong>
                            <p>${avatar.psicografia_profunda.personalidade_dominante}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Aspirações Profissionais:</strong>
                            <ul>
                                ${avatar.psicografia_profunda.aspiracoes_profissionais?.map(asp => `<li>${asp}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Aspirações Pessoais:</strong>
                            <ul>
                                ${avatar.psicografia_profunda.aspiracoes_pessoais?.map(asp => `<li>${asp}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Medos Profundos:</strong>
                            <ul>
                                ${avatar.psicografia_profunda.medos_profundos?.map(medo => `<li>${medo}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Motivadores Principais:</strong>
                            <ul>
                                ${avatar.psicografia_profunda.motivadores_principais?.map(mot => `<li>${mot}</li>`).join('') || ''}
                            </ul>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${avatar.comportamento_digital_avancado ? `
                    <div class="avatar-section">
                        <h4>Comportamento Digital Avançado</h4>
                        <div class="detail-item">
                            <strong>Plataformas Primárias:</strong>
                            <ul>
                                ${avatar.comportamento_digital_avancado.plataformas_primarias?.map(plat => `<li>${plat}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Horários de Pico:</strong>
                            <p><strong>Segunda a Sexta:</strong> ${avatar.comportamento_digital_avancado.horarios_pico_detalhados?.segunda_sexta || ''}</p>
                            <p><strong>Fins de Semana:</strong> ${avatar.comportamento_digital_avancado.horarios_pico_detalhados?.fins_semana || ''}</p>
                        </div>
                        <div class="detail-item">
                            <strong>Conteúdo Preferido:</strong>
                            <ul>
                                ${avatar.comportamento_digital_avancado.conteudo_consumido?.formatos_preferidos?.map(cont => `<li>${cont}</li>`).join('') || ''}
                            </ul>
                        </div>
                        <div class="detail-item">
                            <strong>Comportamento de Compra:</strong>
                            <p><strong>Frequência:</strong> ${avatar.comportamento_digital_avancado.comportamento_compra_online?.frequencia_compras || ''}</p>
                            <p><strong>Ticket Médio:</strong> ${avatar.comportamento_digital_avancado.comportamento_compra_online?.ticket_medio || ''}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateDoresUltraDetalhadasSection(dores) {
    if (!dores) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-heart-broken"></i>
                </div>
                <h3 class="neo-card-title">Mapeamento de Dores Ultra-Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="dores-content">
                    ${dores.dores_nivel_1_criticas ? `
                    <div class="detail-item">
                        <strong>Dores Nível 1 - Críticas:</strong>
                        <div class="dores-list">
                            ${dores.dores_nivel_1_criticas.map((dor, index) => `
                                <div class="dor-item nivel-1">
                                    <h5>Dor Crítica ${index + 1} - Intensidade: ${dor.intensidade}</h5>
                                    <p><strong>Descrição:</strong> ${dor.dor}</p>
                                    <p><strong>Frequência:</strong> ${dor.frequencia}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida}</p>
                                    <p><strong>Nível de Consciência:</strong> ${dor.nivel_consciencia}</p>
                                    <p><strong>Tentativas de Solução:</strong> ${dor.tentativas_solucao?.join(', ') || ''}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${dores.dores_nivel_2_importantes ? `
                    <div class="detail-item">
                        <strong>Dores Nível 2 - Importantes:</strong>
                        <div class="dores-list">
                            ${dores.dores_nivel_2_importantes.map((dor, index) => `
                                <div class="dor-item nivel-2">
                                    <h5>Dor Importante ${index + 1} - Intensidade: ${dor.intensidade}</h5>
                                    <p><strong>Descrição:</strong> ${dor.dor}</p>
                                    <p><strong>Frequência:</strong> ${dor.frequencia}</p>
                                    <p><strong>Impacto:</strong> ${dor.impacto_vida}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${dores.jornada_dor ? `
                    <div class="detail-item">
                        <strong>Jornada da Dor:</strong>
                        <div class="jornada-dor">
                            <p><strong>Gatilho Inicial:</strong> ${dores.jornada_dor.gatilho_inicial}</p>
                            <p><strong>Evolução:</strong> ${dores.jornada_dor.evolucao_dor}</p>
                            <p><strong>Ponto Insuportável:</strong> ${dores.jornada_dor.ponto_insuportavel}</p>
                            <p><strong>Busca por Solução:</strong> ${dores.jornada_dor.busca_solucao}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateConcorrenciaDetalhadaSection(concorrencia) {
    if (!concorrencia) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chess"></i>
                </div>
                <h3 class="neo-card-title">Análise da Concorrência Detalhada</h3>
            </div>
            <div class="neo-card-content">
                <div class="concorrencia-content">
                    ${concorrencia.concorrentes_diretos ? `
                    <div class="detail-item">
                        <strong>Concorrentes Diretos:</strong>
                        ${concorrencia.concorrentes_diretos.map(conc => `
                            <div class="competitor-item">
                                <h5>${conc.nome} - ${conc.preco_range}</h5>
                                <p><strong>Proposta de Valor:</strong> ${conc.proposta_valor}</p>
                                <p><strong>Posicionamento:</strong> ${conc.posicionamento}</p>
                                <p><strong>Público-Alvo:</strong> ${conc.publico_alvo}</p>
                                <p><strong>Share de Mercado:</strong> ${conc.share_mercado_estimado}</p>
                                <p><strong>Pontos Fortes:</strong> ${conc.pontos_fortes?.join(', ') || ''}</p>
                                <p><strong>Pontos Fracos:</strong> ${conc.pontos_fracos?.join(', ') || ''}</p>
                                <p><strong>Canais de Marketing:</strong> ${conc.canais_marketing?.join(', ') || ''}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${concorrencia.gaps_oportunidades ? `
                    <div class="detail-item">
                        <strong>Gaps e Oportunidades:</strong>
                        <ul>
                            ${concorrencia.gaps_oportunidades.map(gap => `<li>${gap}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    ${concorrencia.fatores_diferenciacao ? `
                    <div class="detail-item">
                        <strong>Fatores de Diferenciação:</strong>
                        <ul>
                            ${concorrencia.fatores_diferenciacao.map(fator => `<li>${fator}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateInteligenciaMercadoSection(mercado) {
    if (!mercado) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-pie"></i>
                </div>
                <h3 class="neo-card-title">Inteligência de Mercado</h3>
            </div>
            <div class="neo-card-content">
                <div class="mercado-content">
                    ${mercado.tendencias_crescimento ? `
                    <div class="detail-item">
                        <strong>Tendências em Crescimento:</strong>
                        ${mercado.tendencias_crescimento.map(tend => `
                            <div class="tendencia-item crescimento">
                                <h5>${tend.tendencia}</h5>
                                <p><strong>Impacto:</strong> ${tend.impacto}</p>
                                <p><strong>Timeline:</strong> ${tend.timeline}</p>
                                <p><strong>Oportunidade:</strong> ${tend.oportunidade}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${mercado.sazonalidade_detalhada ? `
                    <div class="detail-item">
                        <strong>Sazonalidade Detalhada:</strong>
                        <div class="sazonalidade-grid">
                            <div class="sazonalidade-item">
                                <h6>Picos de Demanda</h6>
                                <p>${mercado.sazonalidade_detalhada.picos_demanda?.join(', ') || ''}</p>
                            </div>
                            <div class="sazonalidade-item">
                                <h6>Baixas de Demanda</h6>
                                <p>${mercado.sazonalidade_detalhada.baixas_demanda?.join(', ') || ''}</p>
                            </div>
                        </div>
                        <p><strong>Fatores Sazonais:</strong> ${mercado.sazonalidade_detalhada.fatores_sazonais?.join(', ') || ''}</p>
                    </div>
                    ` : ''}
                    
                    ${mercado.tecnologias_emergentes ? `
                    <div class="detail-item">
                        <strong>Tecnologias Emergentes:</strong>
                        <ul>
                            ${mercado.tecnologias_emergentes.map(tech => `<li>${tech}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generatePalavrasChaveSection(palavras) {
    if (!palavras) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h3 class="neo-card-title">Estratégia de Palavras-Chave</h3>
            </div>
            <div class="neo-card-content">
                <div class="palavras-content">
                    ${palavras.palavras_primarias ? `
                    <div class="detail-item">
                        <strong>Palavras-Chave Primárias:</strong>
                        <div class="keywords-table">
                            ${palavras.palavras_primarias.map(kw => `
                                <div class="keyword-row">
                                    <span class="keyword">${kw.termo}</span>
                                    <span class="volume">${kw.volume_mensal}/mês</span>
                                    <span class="cpc">${kw.cpc_estimado}</span>
                                    <span class="difficulty ${kw.dificuldade?.toLowerCase()}">${kw.dificuldade}</span>
                                    <span class="intent">${kw.intencao_busca}</span>
                                    <span class="opportunity ${kw.oportunidade?.toLowerCase()}">${kw.oportunidade}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${palavras.palavras_long_tail ? `
                    <div class="detail-item">
                        <strong>Palavras Long Tail:</strong>
                        <ul>
                            ${palavras.palavras_long_tail.map(kw => `<li>${kw}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    ${palavras.custos_aquisicao_canal ? `
                    <div class="detail-item">
                        <strong>Custos por Canal:</strong>
                        <div class="platform-costs">
                            ${Object.entries(palavras.custos_aquisicao_canal).map(([platform, costs]) => `
                                <div class="platform-item">
                                    <h5>${platform.charAt(0).toUpperCase() + platform.slice(1)}</h5>
                                    <div class="platform-metrics">
                                        <span>CPC: ${costs.cpc_medio}</span>
                                        <span>CPM: ${costs.cpm_medio}</span>
                                        <span>CTR: ${costs.ctr_esperado}</span>
                                        <span>Conv: ${costs.conversao_esperada}</span>
                                        <span>CPA: ${costs.cpa_estimado}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateMetricasDetalhadasSection(metricas) {
    if (!metricas) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 class="neo-card-title">Métricas de Performance Detalhadas</h3>
            </div>
            <div class="neo-card-content">
                <div class="metricas-content">
                    ${metricas.benchmarks_segmento ? `
                    <div class="detail-item">
                        <strong>Benchmarks do Segmento:</strong>
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="metric-value">${metricas.benchmarks_segmento.cac_medio_segmento}</div>
                                <div class="metric-label">CAC Médio</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${metricas.benchmarks_segmento.ltv_medio_segmento}</div>
                                <div class="metric-label">LTV Médio</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${metricas.benchmarks_segmento.churn_rate_medio}</div>
                                <div class="metric-label">Churn Rate</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${metricas.benchmarks_segmento.ticket_medio_segmento}</div>
                                <div class="metric-label">Ticket Médio</div>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${metricas.funil_conversao_otimizado ? `
                    <div class="detail-item">
                        <strong>Funil de Conversão Otimizado:</strong>
                        <div class="funnel-steps">
                            <div class="funnel-step">Visitantes → Leads: ${metricas.funil_conversao_otimizado.visitantes_leads}</div>
                            <div class="funnel-step">Leads → Oportunidades: ${metricas.funil_conversao_otimizado.leads_oportunidades}</div>
                            <div class="funnel-step">Oportunidades → Vendas: ${metricas.funil_conversao_otimizado.oportunidades_vendas}</div>
                            <div class="funnel-step">Vendas → Clientes: ${metricas.funil_conversao_otimizado.vendas_clientes}</div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${metricas.kpis_criticos ? `
                    <div class="detail-item">
                        <strong>KPIs Críticos:</strong>
                        ${metricas.kpis_criticos.map(kpi => `
                            <div class="kpi-item">
                                <h5>${kpi.metrica}</h5>
                                <p><strong>Valor Ideal:</strong> ${kpi.valor_ideal}</p>
                                <p><strong>Como Medir:</strong> ${kpi.como_medir}</p>
                                <p><strong>Frequência:</strong> ${kpi.frequencia}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateVozMercadoSection(voz) {
    if (!voz) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-comments"></i>
                </div>
                <h3 class="neo-card-title">Voz do Mercado e Linguagem</h3>
            </div>
            <div class="neo-card-content">
                <div class="voz-content">
                    ${voz.objecoes_principais ? `
                    <div class="detail-item">
                        <strong>Principais Objeções:</strong>
                        ${voz.objecoes_principais.map(obj => `
                            <div class="objecao-item">
                                <h5>Objeção: "${obj.objecao}"</h5>
                                <p><strong>Frequência:</strong> ${obj.frequencia}</p>
                                <p><strong>Momento:</strong> ${obj.momento_surgimento}</p>
                                <p><strong>Estratégia de Contorno:</strong> ${obj.estrategia_contorno}</p>
                                <p><strong>Prova Social Necessária:</strong> ${obj.prova_social_necessaria}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${voz.linguagem_avatar ? `
                    <div class="detail-item">
                        <strong>Linguagem do Avatar:</strong>
                        <p><strong>Termos Técnicos:</strong> ${voz.linguagem_avatar.termos_tecnicos?.join(', ') || ''}</p>
                        <p><strong>Gírias e Expressões:</strong> ${voz.linguagem_avatar.girias_expressoes?.join(', ') || ''}</p>
                        <p><strong>Palavras de Poder:</strong> ${voz.linguagem_avatar.palavras_poder?.join(', ') || ''}</p>
                        <p><strong>Palavras a Evitar:</strong> ${voz.linguagem_avatar.palavras_evitar?.join(', ') || ''}</p>
                    </div>
                    ` : ''}
                    
                    ${voz.gatilhos_mentais_efetivos ? `
                    <div class="detail-item">
                        <strong>Gatilhos Mentais Efetivos:</strong>
                        ${voz.gatilhos_mentais_efetivos.map(gatilho => `
                            <div class="gatilho-item">
                                <h5>${gatilho.gatilho}</h5>
                                <p><strong>Aplicação:</strong> ${gatilho.aplicacao}</p>
                                <p><strong>Efetividade:</strong> ${gatilho.efetividade}</p>
                                <p><strong>Exemplos:</strong> ${gatilho.exemplos?.join(', ') || ''}</p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${voz.tom_comunicacao ? `
                    <div class="detail-item">
                        <strong>Tom de Comunicação:</strong>
                        <p><strong>Personalidade da Marca:</strong> ${voz.tom_comunicacao.personalidade_marca}</p>
                        <p><strong>Nível de Formalidade:</strong> ${voz.tom_comunicacao.nivel_formalidade}</p>
                        <p><strong>Emoções a Despertar:</strong> ${voz.tom_comunicacao.emocoes_despertar?.join(', ') || ''}</p>
                        <p><strong>Temas de Storytelling:</strong> ${voz.tom_comunicacao.storytelling_temas?.join(', ') || ''}</p>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateProjecoesCenariosSection(projecoes) {
    if (!projecoes) return '';
    
    return `
        <div class="neo-enhanced-card result-card">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h3 class="neo-card-title">Projeções de Cenários</h3>
            </div>
            <div class="neo-card-content">
                <div class="projecoes-content">
                    <div class="scenarios-grid">
                        ${projecoes.cenario_conservador ? `
                        <div class="scenario-item conservador">
                            <h4>Cenário Conservador</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${projecoes.cenario_conservador.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${projecoes.cenario_conservador.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${projecoes.cenario_conservador.cac}</p>
                                <p><strong>LTV:</strong> ${projecoes.cenario_conservador.ltv}</p>
                                <p><strong>Faturamento:</strong> ${projecoes.cenario_conservador.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${projecoes.cenario_conservador.roi}</p>
                                <p><strong>Break-even:</strong> ${projecoes.cenario_conservador.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${projecoes.cenario_conservador.premissas?.map(premissa => `<li>${premissa}</li>`).join('') || ''}
                                </ul>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${projecoes.cenario_realista ? `
                        <div class="scenario-item realista">
                            <h4>Cenário Realista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${projecoes.cenario_realista.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${projecoes.cenario_realista.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${projecoes.cenario_realista.cac}</p>
                                <p><strong>LTV:</strong> ${projecoes.cenario_realista.ltv}</p>
                                <p><strong>Faturamento:</strong> ${projecoes.cenario_realista.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${projecoes.cenario_realista.roi}</p>
                                <p><strong>Break-even:</strong> ${projecoes.cenario_realista.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${projecoes.cenario_realista.premissas?.map(premissa => `<li>${premissa}</li>`).join('') || ''}
                                </ul>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${projecoes.cenario_otimista ? `
                        <div class="scenario-item otimista">
                            <h4>Cenário Otimista</h4>
                            <div class="scenario-metrics">
                                <p><strong>Conversão:</strong> ${projecoes.cenario_otimista.taxa_conversao}</p>
                                <p><strong>Ticket Médio:</strong> ${projecoes.cenario_otimista.ticket_medio}</p>
                                <p><strong>CAC:</strong> ${projecoes.cenario_otimista.cac}</p>
                                <p><strong>LTV:</strong> ${projecoes.cenario_otimista.ltv}</p>
                                <p><strong>Faturamento:</strong> ${projecoes.cenario_otimista.faturamento_mensal}</p>
                                <p><strong>ROI:</strong> ${projecoes.cenario_otimista.roi}</p>
                                <p><strong>Break-even:</strong> ${projecoes.cenario_otimista.break_even}</p>
                            </div>
                            <div class="scenario-assumptions">
                                <strong>Premissas:</strong>
                                <ul>
                                    ${projecoes.cenario_otimista.premissas?.map(premissa => `<li>${premissa}</li>`).join('') || ''}
                                </ul>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generatePlanoAcaoDetalhadoSection(plano) {
    if (!plano || !Array.isArray(plano)) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-tasks"></i>
                </div>
                <h3 class="neo-card-title">Plano de Ação Detalhado</h3>
            </div>
            <div class="neo-card-content">
                <div class="plano-content">
                    <div class="action-timeline">
                        ${plano.map((fase, index) => `
                            <div class="action-phase">
                                <div class="phase-header">
                                    <div class="phase-number">${index + 1}</div>
                                    <div class="phase-info">
                                        <h4>${fase.fase}</h4>
                                        <p><strong>Duração:</strong> ${fase.duracao}</p>
                                    </div>
                                </div>
                                <div class="phase-actions">
                                    ${fase.acoes?.map(acao => `
                                        <div class="action-item-detailed">
                                            <h5>${acao.acao}</h5>
                                            <div class="action-details">
                                                <p><strong>Responsável:</strong> ${acao.responsavel}</p>
                                                <p><strong>Prazo:</strong> ${acao.prazo}</p>
                                                <p><strong>Recursos:</strong> ${acao.recursos_necessarios?.join(', ') || ''}</p>
                                                <p><strong>Entregáveis:</strong> ${acao.entregaveis?.join(', ') || ''}</p>
                                                <p><strong>Métricas de Sucesso:</strong> ${acao.metricas_sucesso?.join(', ') || ''}</p>
                                            </div>
                                        </div>
                                    `).join('') || ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateInsightsExclusivosSection(insights) {
    if (!insights || !Array.isArray(insights)) return '';
    
    return `
        <div class="neo-enhanced-card result-card full-width">
            <div class="neo-card-header">
                <div class="neo-card-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <h3 class="neo-card-title">Insights Exclusivos</h3>
            </div>
            <div class="neo-card-content">
                <div class="insights-content">
                    <div class="insights-list">
                        ${insights.map((insight, index) => `
                            <div class="insight-item">
                                <div class="insight-number">${index + 1}</div>
                                <div class="insight-text">
                                    <p>${insight}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function initializeResultsInteractions() {
    // Add any interactive functionality for results
    console.log('Results interactions initialized');
}

function downloadReport() {
    if (!currentAnalysis) {
        showNotification('Nenhuma análise disponível para download.', 'error');
        return;
    }
    
    // Create and download report
    const reportData = generateReportData(currentAnalysis);
    const blob = new Blob([reportData], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `analise-avatar-gemini-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Relatório baixado com sucesso!', 'success');
}

function generateReportData(analysis) {
    return `
RELATÓRIO DE ANÁLISE DE AVATAR - GEMINI PRO 2.5
===============================================

ESCOPO ULTRA-DETALHADO
----------------------
Segmento Principal: ${analysis.escopo?.segmento_principal || 'N/A'}
Produto Ideal: ${analysis.escopo?.produto_ideal || 'N/A'}
Proposta de Valor: ${analysis.escopo?.proposta_valor || 'N/A'}

AVATAR ULTRA-DETALHADO
----------------------
Persona Principal: ${analysis.avatar_ultra_detalhado?.persona_principal?.nome || 'N/A'}
Idade: ${analysis.avatar_ultra_detalhado?.persona_principal?.idade || 'N/A'}
Profissão: ${analysis.avatar_ultra_detalhado?.persona_principal?.profissao || 'N/A'}
Renda: ${analysis.avatar_ultra_detalhado?.persona_principal?.renda_mensal || 'N/A'}

Demografia:
- Faixa Etária Primária: ${analysis.avatar_ultra_detalhado?.demografia_detalhada?.faixa_etaria_primaria || 'N/A'}
- Distribuição por Gênero: ${analysis.avatar_ultra_detalhado?.demografia_detalhada?.distribuicao_genero || 'N/A'}
- Distribuição Geográfica: ${analysis.avatar_ultra_detalhado?.demografia_detalhada?.distribuicao_geografica || 'N/A'}

Psicografia:
- Valores: ${analysis.avatar_ultra_detalhado?.psicografia_profunda?.valores_fundamentais?.join(', ') || 'N/A'}
- Estilo de Vida: ${analysis.avatar_ultra_detalhado?.psicografia_profunda?.estilo_vida_detalhado || 'N/A'}

INTELIGÊNCIA DE MERCADO
-----------------------
Tendências em Crescimento: ${analysis.inteligencia_mercado?.tendencias_crescimento?.map(t => t.tendencia).join(', ') || 'N/A'}
Tecnologias Emergentes: ${analysis.inteligencia_mercado?.tecnologias_emergentes?.join(', ') || 'N/A'}

PROJEÇÕES
---------
Cenário Realista:
- Conversão: ${analysis.projecoes_cenarios?.cenario_realista?.taxa_conversao || 'N/A'}
- Faturamento: ${analysis.projecoes_cenarios?.cenario_realista?.faturamento_mensal || 'N/A'}
- ROI: ${analysis.projecoes_cenarios?.cenario_realista?.roi || 'N/A'}

INSIGHTS EXCLUSIVOS
-------------------
${analysis.insights_exclusivos?.map((insight, index) => `${index + 1}. ${insight}`).join('\n') || 'N/A'}

Gerado em: ${new Date().toLocaleString()}
Powered by Gemini Pro 2.5 com Pesquisa na Internet
    `;
}

function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'Análise de Avatar com Gemini Pro 2.5 - UP Lançamentos',
            text: 'Confira minha análise ultra-detalhada de avatar!',
            url: window.location.href
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Link copiado para a área de transferência!', 'success');
        });
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: var(--neo-border-radius);
        color: var(--text-light);
        font-weight: 600;
        z-index: 10000;
        box-shadow: var(--neo-shadow-2);
        transition: var(--neo-transition);
        transform: translateX(100%);
        max-width: 400px;
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            break;
        default:
            notification.style.background = 'var(--brand-gradient)';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('.neo-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            if (query.length > 2) {
                searchSegmentos(query);
            }
        });
    }
}

async function searchSegmentos(query) {
    try {
        const response = await fetch(`/api/segmentos?search=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        // Display search suggestions
        displaySearchSuggestions(data.segmentos);
        
    } catch (error) {
        console.error('Erro na busca:', error);
    }
}

function displaySearchSuggestions(segmentos) {
    // Implementation for search suggestions dropdown
    console.log('Segmentos encontrados:', segmentos);
}