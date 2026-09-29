const API_HOSTS_POR_FRONT = {
  'holtech.employer.com.br': 'api.holtech.employer.com.br',
  'testing-holtech.employer.com.br': 'testing-api.holtech.employer.com.br'
};

function getApiBaseUrl() {
  const apiHost = API_HOSTS_POR_FRONT[window.location.hostname];
  return apiHost ? `https://${apiHost}` : '';
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch(`${getApiBaseUrl()}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email, senha: password })
    });
    
    if (!response.ok) {
      const errData = await response.json();
      alert(errData.detail || 'E-mail ou senha incorretos.');
      return;
    }
    
    const user = await response.json();
    
    // Armazena a sessão no localStorage com fallback seguro
    try {
      localStorage.setItem('user', JSON.stringify(user));
    } catch (e) {
      console.warn('Não foi possível salvar no localStorage:', e);
    }
    
    const queryParams = `?user_id=${user.id}&nome=${encodeURIComponent(user.nome || '')}&perfil=${user.perfil || 'user'}`;
    if (user.perfil === 'admin') {
      window.location.href = `/crud/${queryParams}`;
    } else {
      window.location.href = `/app/${queryParams}`;
    }
  } catch (error) {
    console.error('Erro ao fazer login:', error);
    alert('Erro ao conectar com o servidor da API: ' + (error.message || ''));
  }
});
