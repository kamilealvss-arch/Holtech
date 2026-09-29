// ─────────────────────────────────────────────────────────────────────────────
// app.js — Interface de Auditoria de Holerites (Holtech)
// ─────────────────────────────────────────────────────────────────────────────

const API_HOSTS_POR_FRONT = {
  'holtech.employer.com.br': 'api.holtech.employer.com.br',
  'testing-holtech.employer.com.br': 'testing-api.holtech.employer.com.br'
};

function getApiBaseUrl() {
  const apiHost = API_HOSTS_POR_FRONT[window.location.hostname];
  return apiHost ? `https://${apiHost}` : '';
}

// ── Armazenamento Seguro (com fallback contra SecurityError) ─────────────────
const memoryStorage = {};
const safeStorage = {
  getItem(key) {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return memoryStorage[key] || null;
    }
  },
  setItem(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      memoryStorage[key] = String(value);
    }
  },
  removeItem(key) {
    try {
      window.localStorage.removeItem(key);
    } catch {
      delete memoryStorage[key];
    }
  }
};

// ── Estado da Aplicação ──────────────────────────────────────────────────────
const state = {
  user: { id: 1, nome: 'Usuário', perfil: 'user' },
  files: {
    holerite: null,
    depara: null,
    func: null
  },
  currentResult: null,
  activeFilter: null
};

// ── Inicialização e Autenticação ─────────────────────────────────────────────
function initAuth() {
  const params = new URLSearchParams(window.location.search);
  const uidParam = params.get('user_id');
  const nomeParam = params.get('nome');
  const perfilParam = params.get('perfil');

  if (uidParam) {
    const userFromUrl = {
      id: parseInt(uidParam, 10),
      nome: nomeParam ? decodeURIComponent(nomeParam) : 'Usuário',
      perfil: perfilParam || 'user'
    };
    safeStorage.setItem('user', JSON.stringify(userFromUrl));
    state.user = userFromUrl;
  } else {
    try {
      const storedUser = safeStorage.getItem('user');
      if (storedUser) {
        state.user = JSON.parse(storedUser);
      }
    } catch {
      state.user = { id: 1, nome: 'Usuário', perfil: 'user' };
    }
  }

  if (!state.user) {
    state.user = { id: 1, nome: 'Usuário', perfil: 'user' };
  }

  const elName = document.getElementById('userName');
  if (elName) elName.textContent = state.user.nome || 'Usuário';

  const elBadge = document.getElementById('userBadge');
  if (elBadge) elBadge.textContent = state.user.perfil || 'user';

  if (state.user.perfil === 'admin') {
    const btnAdmin = document.getElementById('btnAdmin');
    if (btnAdmin) btnAdmin.style.display = 'inline-flex';
  }
}

const btnLogout = document.getElementById('btnLogout');
if (btnLogout) {
  btnLogout.addEventListener('click', () => {
    safeStorage.removeItem('user');
    window.location.href = '/login/';
  });
}

// ── Navegação por Abas ───────────────────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    btn.classList.add('active');
    const tabId = btn.getAttribute('data-tab');
    document.getElementById(tabId).classList.add('active');

    if (tabId === 'tab-historico') {
      carregarHistorico();
    }
  });
});

// ── Upload de Arquivos e Drag & Drop ─────────────────────────────────────────
function setupUploadCard(cardId, inputId, statusId, key) {
  const card = document.getElementById(cardId);
  const input = document.getElementById(inputId);
  const statusContainer = document.getElementById(statusId);

  card.addEventListener('click', (e) => {
    if (e.target.closest('.btn-remove-file')) return;
    input.click();
  });

  input.addEventListener('change', () => {
    if (input.files.length > 0) {
      setFile(key, input.files[0], card, statusContainer);
    }
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    card.addEventListener(eventName, (e) => {
      e.preventDefault();
      card.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    card.addEventListener(eventName, (e) => {
      e.preventDefault();
      card.classList.remove('drag-over');
    });
  });

  card.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length > 0) {
      input.files = e.dataTransfer.files;
      setFile(key, e.dataTransfer.files[0], card, statusContainer);
    }
  });
}

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function setFile(key, file, card, statusContainer) {
  state.files[key] = file;
  card.classList.add('has-file');

  statusContainer.innerHTML = `
    <div class="file-info-badge">
      <span class="file-name-truncate" title="${file.name}">📄 ${file.name} (${formatBytes(file.size)})</span>
      <button type="button" class="btn-remove-file" title="Remover arquivo" onclick="removeFile('${key}', event)">
        <i class='bx bx-x'></i>
      </button>
    </div>
  `;

  checkAllFilesSelected();
}

window.removeFile = function(key, event) {
  if (event) event.stopPropagation();
  state.files[key] = null;

  const cardMap = {
    holerite: { card: 'drop-holerite', status: 'status-holerite', input: 'file-holerite' },
    depara:   { card: 'drop-depara',   status: 'status-depara',   input: 'file-depara' },
    func:     { card: 'drop-func',     status: 'status-func',     input: 'file-func' }
  };

  const conf = cardMap[key];
  const card = document.getElementById(conf.card);
  const statusContainer = document.getElementById(conf.status);
  const input = document.getElementById(conf.input);

  card.classList.remove('has-file');
  input.value = '';
  statusContainer.innerHTML = '<span class="btn-select">Selecionar Arquivo</span>';

  checkAllFilesSelected();
};

function checkAllFilesSelected() {
  const btn = document.getElementById('btnExecutarAuditoria');
  const allSelected = state.files.holerite && state.files.depara && state.files.func;
  btn.disabled = !allSelected;
}

setupUploadCard('drop-holerite', 'file-holerite', 'status-holerite', 'holerite');
setupUploadCard('drop-depara',   'file-depara',   'status-depara',   'depara');
setupUploadCard('drop-func',     'file-func',     'status-func',     'func');

// ── Execução da Auditoria ────────────────────────────────────────────────────
document.getElementById('btnExecutarAuditoria').addEventListener('click', async () => {
  if (!state.files.holerite || !state.files.depara || !state.files.func) {
    alert('Por favor, selecione os três arquivos antes de executar a auditoria.');
    return;
  }

  const loadingState = document.getElementById('loadingState');
  const resultsContainer = document.getElementById('resultsContainer');
  const btnAudit = document.getElementById('btnExecutarAuditoria');

  loadingState.style.display = 'block';
  resultsContainer.style.display = 'none';
  btnAudit.disabled = true;

  try {
    const userId = (state.user && state.user.id) ? state.user.id : 1;
    const formData = new FormData();
    formData.append('holerite', state.files.holerite);
    formData.append('depara', state.files.depara);
    formData.append('funcionarios', state.files.func);
    formData.append('user_id', String(userId));

    const response = await fetch(`${getApiBaseUrl()}/api/auditoria/validar`, {
      method: 'POST',
      headers: {
        'X-User-Id': String(userId)
      },
      body: formData
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Falha na resposta do servidor' }));
      throw new Error(err.detail || 'Erro ao processar auditoria.');
    }

    const data = await response.json();
    state.currentResult = data;
    renderResults(data);

  } catch (error) {
    console.error('Erro na auditoria:', error);
    alert('Erro ao executar a auditoria: ' + error.message);
  } finally {
    loadingState.style.display = 'none';
    btnAudit.disabled = false;
  }
});

// ── Renderização dos Resultados ──────────────────────────────────────────────
function renderResults(data) {
  const container = document.getElementById('resultsContainer');
  const banner = document.getElementById('statusBanner');
  const bannerTitle = document.getElementById('bannerTitle');
  const bannerDesc = document.getElementById('bannerDesc');
  const bannerAction = document.getElementById('bannerAction');
  const btnDl = document.getElementById('btnDownloadAuditado');

  const kpiSection = document.getElementById('kpiSection');
  const kpiGrid = document.getElementById('kpiGrid');
  const tableSection = document.getElementById('tableSection');

  banner.className = 'status-banner';

  if (data.status === 'SUCESSO') {
    banner.classList.add('banner-success');
    bannerTitle.textContent = 'Sucesso! Planilhas em Conformidade';
    bannerDesc.textContent = 'Nenhuma inconsistência crítica foi detectada. A folha está pronta para importação.';
    bannerAction.style.display = 'none';
    kpiSection.style.display = 'none';
    tableSection.style.display = 'none';
  } else if (data.status === 'ALERTA') {
    banner.classList.add('banner-alert');
    bannerTitle.textContent = `Auditoria Concluída: ${data.total_erros} Inconsistências`;
    bannerDesc.textContent = `Foram identificados ${data.total_erros} desvios na folha (${data.celulas_marcadas || 0} células demarcadas no Excel).`;

    if (data.download_disponivel && data.historico_id) {
      bannerAction.style.display = 'block';
      btnDl.onclick = () => {
        window.location.href = `${getApiBaseUrl()}/api/auditoria/download/${data.historico_id}`;
      };
    } else {
      bannerAction.style.display = 'none';
    }

    // Renderizar KPIs
    renderKpis(data.erros_por_tipo || {});
    kpiSection.style.display = 'block';

    // Renderizar Tabela
    renderTable(data.erros || []);
    tableSection.style.display = 'block';

  } else {
    banner.classList.add('banner-danger');
    bannerTitle.textContent = 'Falha no Processamento da Auditoria';
    bannerDesc.textContent = data.mensagem || 'Ocorreu um erro durante a validação dos dados.';
    bannerAction.style.display = 'none';
    kpiSection.style.display = 'none';
    tableSection.style.display = 'none';
  }

  container.style.display = 'block';
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderKpis(errosPorTipo) {
  const grid = document.getElementById('kpiGrid');
  grid.innerHTML = '';

  const entries = Object.entries(errosPorTipo);
  if (entries.length === 0) return;

  // Card "Todos"
  const allCard = document.createElement('div');
  allCard.className = 'kpi-card active';
  allCard.innerHTML = `
    <p class="kpi-title">Todos os Desvios</p>
    <p class="kpi-value">${state.currentResult.total_erros}</p>
  `;
  allCard.onclick = () => {
    document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('active'));
    allCard.classList.add('active');
    state.activeFilter = null;
    renderTable(state.currentResult.erros || []);
  };
  grid.appendChild(allCard);

  entries.forEach(([tipo, qtd]) => {
    const card = document.createElement('div');
    card.className = 'kpi-card';
    card.innerHTML = `
      <p class="kpi-title">${tipo}</p>
      <p class="kpi-value">${qtd}</p>
    `;
    card.onclick = () => {
      document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      state.activeFilter = tipo;
      const filtrados = (state.currentResult.erros || []).filter(e => {
        const t = e['Tipo de Erro'] || e['tipo_erro'] || '';
        return t === tipo;
      });
      renderTable(filtrados);
    };
    grid.appendChild(card);
  });
}

function renderTable(erros) {
  const tbody = document.getElementById('corpoTabelaErros');
  tbody.innerHTML = '';

  if (!erros || erros.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 24px; color: #64748b;">Nenhuma inconsistência encontrada para este filtro.</td></tr>`;
    return;
  }

  erros.forEach(erro => {
    const tr = document.createElement('tr');
    const planilha = erro['Planilha'] || erro['planilha'] || 'HOLERITE';
    const linha = erro['Linha Excel'] || erro['linha_excel'] || '—';
    const ident = erro['Identificador'] || erro['identificador'] || '—';
    const tipo = erro['Tipo de Erro'] || erro['tipo_erro'] || 'Inconsistência';
    const desc = erro['Descrição'] || erro['descricao'] || '—';

    tr.innerHTML = `
      <td><strong>${planilha}</strong></td>
      <td>Linha ${linha}</td>
      <td>${ident}</td>
      <td><span class="badge-tipo">${tipo}</span></td>
      <td>${desc}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Filtro de texto na tabela
document.getElementById('filtroTabela').addEventListener('input', (e) => {
  const termo = e.target.value.toLowerCase().trim();
  if (!state.currentResult || !state.currentResult.erros) return;

  let base = state.currentResult.erros;
  if (state.activeFilter) {
    base = base.filter(item => (item['Tipo de Erro'] || item['tipo_erro'] || '') === state.activeFilter);
  }

  if (!termo) {
    renderTable(base);
    return;
  }

  const filtrados = base.filter(item => {
    const textoCompleto = JSON.stringify(Object.values(item)).toLowerCase();
    return textoCompleto.includes(termo);
  });

  renderTable(filtrados);
});

// Exportar CSV
document.getElementById('btnExportarCsv').addEventListener('click', () => {
  if (!state.currentResult || !state.currentResult.erros || state.currentResult.erros.length === 0) {
    alert('Não há erros para exportar.');
    return;
  }

  const headers = ['Planilha', 'Linha Excel', 'Identificador', 'Tipo de Erro', 'Descricao'];
  const csvRows = [headers.join(';')];

  state.currentResult.erros.forEach(e => {
    const row = [
      `"${e['Planilha'] || ''}"`,
      `"${e['Linha Excel'] || ''}"`,
      `"${e['Identificador'] || ''}"`,
      `"${e['Tipo de Erro'] || ''}"`,
      `"${(e['Descrição'] || '').replace(/"/g, '""')}"`
    ];
    csvRows.push(row.join(';'));
  });

  const blob = new Blob(["\ufeff" + csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `erros_auditoria_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
});

// ── Aba de Histórico ─────────────────────────────────────────────────────────
async function carregarHistorico() {
  const listContainer = document.getElementById('historicoList');
  listContainer.innerHTML = '<div class="empty-state">Carregando histórico...</div>';

  try {
    const userId = (state.user && state.user.id) ? state.user.id : 1;
    const isUserAdmin = (state.user && state.user.perfil === 'admin');
    const url = isUserAdmin
      ? `${getApiBaseUrl()}/api/historico/admin`
      : `${getApiBaseUrl()}/api/historico/usuario/${userId}`;

    const res = await fetch(url);
    if (!res.ok) throw new Error('Falha ao obter histórico');
    const dados = await res.json();

    if (!dados || dados.length === 0) {
      listContainer.innerHTML = '<div class="empty-state">Nenhum registro de auditoria encontrado.</div>';
      return;
    }

    listContainer.innerHTML = '';
    dados.forEach(row => {
      const status   = row.stu_auditoria || row.Stu_Auditoria || '—';
      const planilha = row.nme_planilha  || row.Nme_Planilha  || 'Auditoria';
      const usuario  = row.nme_usuario   || row.Nme_Usuario   || 'Usuário';
      const dataRaw  = row.dta_auditoria || row.Dta_Auditoria || '';
      const detalhes = row.des_json      || row.Des_Json      || {};
      const histId   = row.idf_historico || row.Idf_Historico;

      let dataFmt = dataRaw;
      try {
        const dt = new Date(dataRaw);
        dataFmt = dt.toLocaleDateString('pt-BR') + ' ' + dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
      } catch {}

      const arquivos = detalhes.arquivos || {};
      const totalErros = detalhes.total_erros !== undefined ? detalhes.total_erros : (detalhes.erros ? detalhes.erros.length : 0);

      const item = document.createElement('div');
      item.className = 'hist-item';
      item.innerHTML = `
        <div class="hist-info">
          <span class="hist-status ${status}">${status}</span>
          <div class="hist-meta">
            <h4>${planilha}</h4>
            <p><strong>${usuario}</strong> &bull; ${dataFmt} &bull; <strong>${totalErros}</strong> inconsistências</p>
          </div>
        </div>
        <div class="hist-actions">
          ${arquivos.auditado ? `
            <a href="${getApiBaseUrl()}/api/auditoria/download/${histId}" class="btn-file-dl primary" title="Baixar Planilha com Células Coloridas">
              <i class='bx bx-download'></i> Planilha Auditada
            </a>
          ` : ''}
        </div>
      `;
      listContainer.appendChild(item);
    });

  } catch (err) {
    console.error(err);
    listContainer.innerHTML = `<div class="empty-state">Erro ao carregar histórico: ${err.message}</div>`;
  }
}

document.getElementById('btnRecarregarHistorico').addEventListener('click', carregarHistorico);

// Iniciar autenticação
initAuth();
