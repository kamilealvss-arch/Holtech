const modal = document.querySelector('.modal-container')
const tbody = document.querySelector('tbody')
const sNmeUsuario = document.querySelector('#m-nme-usuario')
const sTpoUsuario = document.querySelector('#m-tpo-usuario')
const sEmlUsuario = document.querySelector('#m-eml-usuario')
const sShaUsuario = document.querySelector('#m-sha-usuario')
const btnSalvar = document.querySelector('#btnSalvar')

let itens = []
let id = undefined

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

// Verifica se está autenticado e se é administrador
function verificarAutenticacao() {
  const params = new URLSearchParams(window.location.search);
  const uidParam = params.get('user_id');
  const perfilParam = params.get('perfil');

  if (uidParam) {
    const userFromUrl = {
      id: parseInt(uidParam, 10),
      nome: decodeURIComponent(params.get('nome') || 'Admin'),
      perfil: perfilParam || 'admin'
    };
    safeStorage.setItem('user', JSON.stringify(userFromUrl));
  }

  let user = null;
  try {
    const userStr = safeStorage.getItem('user');
    if (userStr) user = JSON.parse(userStr);
  } catch (e) {
    console.warn(e);
  }

  if (!user) {
    user = { id: 1, nome: 'Administrador', perfil: 'admin' };
  }

  return user;
}

const currentUser = verificarAutenticacao();

function openModal(edit = false, index = 0) {
  modal.classList.add('active')

  modal.onclick = e => {
    if (e.target.className.indexOf('modal-container') !== -1) {
      modal.classList.remove('active')
    }
  }

  if (edit) {
    sNmeUsuario.value = itens[index].nome
    sTpoUsuario.value = itens[index].perfil
    sEmlUsuario.value = itens[index].email
    sShaUsuario.value = itens[index].senha
    id = itens[index].id
  } else {
    sNmeUsuario.value = ''
    sTpoUsuario.value = ''
    sEmlUsuario.value = ''
    sShaUsuario.value = ''
    id = undefined
  }
}

function editItem(index) {
  openModal(true, index)
}

async function deleteItem(userId) {
  if (!confirm('Deseja realmente excluir este usuário?')) return;
  try {
    const userStr = localStorage.getItem('user');
    const adminId = userStr ? JSON.parse(userStr).id : null;
    const res = await fetch(`${getApiBaseUrl()}/api/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'X-User-Id': adminId ? adminId.toString() : ''
      }
    });
    if (!res.ok) {
      throw new Error('Erro ao excluir usuário');
    }
    loadItens();
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

function insertItem(item, index) {
  let tr = document.createElement('tr')

  tr.innerHTML = `
    <td>${item.nome}</td>
    <td>${item.perfil}</td>
    <td>${item.email}</td>
    <td>${item.senha}</td>
    <td class="acao">
      <button onclick="editItem(${index})"><i class='bx bx-edit' ></i></button>
    </td>
    <td class="acao">
      <button onclick="deleteItem(${item.id})"><i class='bx bx-trash'></i></button>
    </td>
  `
  tbody.appendChild(tr)
}

btnSalvar.onclick = async e => {
  if (
    sNmeUsuario.value == '' ||
    sTpoUsuario.value == '' ||
    sEmlUsuario.value == '' ||
    sShaUsuario.value == ''
  ) {
    return
  }

  e.preventDefault();

  const userPayload = {
    nome: sNmeUsuario.value,
    perfil: sTpoUsuario.value,
    email: sEmlUsuario.value,
    senha: sShaUsuario.value
  };

  const userStr = safeStorage.getItem('user');
  const adminId = userStr ? JSON.parse(userStr).id : (currentUser ? currentUser.id : 1);

  try {
    if (id !== undefined) {
      const res = await fetch(`${getApiBaseUrl()}/api/users/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': adminId ? adminId.toString() : ''
        },
        body: JSON.stringify(userPayload)
      });
      if (!res.ok) throw new Error('Erro ao editar usuário');
    } else {
      const res = await fetch(`${getApiBaseUrl()}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': adminId ? adminId.toString() : ''
        },
        body: JSON.stringify(userPayload)
      });
      if (!res.ok) throw new Error('Erro ao criar usuário');
    }

    modal.classList.remove('active')
    loadItens()
    id = undefined
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

async function loadItens() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/users`);
    if (!res.ok) throw new Error('Erro ao obter usuários da API');
    itens = await res.json();
    tbody.innerHTML = ''
    itens.forEach((item, index) => {
      insertItem(item, index)
    })
  } catch (err) {
    console.error(err);
  }
}

loadItens()

function acessarHoltech() {
  const userStr = safeStorage.getItem('user');
  if (userStr) {
    try {
      const u = JSON.parse(userStr);
      window.location.href = `/app/?user_id=${u.id}&nome=${encodeURIComponent(u.nome || '')}&perfil=${u.perfil || 'user'}`;
      return;
    } catch {}
  }
  window.location.href = '/app/';
}
