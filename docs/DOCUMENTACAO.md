# Documentação do Sistema Holtech

Sistema completo de Gestão de Usuários (CRUD), Auditoria de Holerites e Histórico de Permissões com suporte a duplo modo de banco de dados (JSON e PostgreSQL).

---

## 📋 Sumário
1. [Visão Geral](#1-visão-geral)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Modos de Banco de Dados (`TIPO_BANCO`)](#3-modos-de-banco-de-dados-tipo_banco)
4. [Estrutura das Tabelas / Coleções](#4-estrutura-das-tabelas--coleções)
5. [Regras de Negócio e Permissões](#5-regras-de-negócio-e-permissões)
6. [Rotas e Endpoints da API](#6-rotas-e-endpoints-da-api)
7. [Como Executar o Projeto](#7-como-executar-o-projeto)

---

## 1. Visão Geral

O **Holtech** é um sistema web composto por:
- **API Backend (FastAPI)**: Gerencia a autenticação, controle de usuários, permissões, auditorias, validação de planilhas e alternância dinâmica entre banco de dados JSON e PostgreSQL.
- **Frontend de Login e CRUD (HTML/CSS/JS)**: Interface leve para autenticação de usuários e gerenciamento completo de cadastros (apenas administradores).
- **Interface Web de Auditoria (HTML/CSS/JS em `/app`)**: Painel moderno e responsivo para envio e validação de planilhas de holerites, geração de alertas e download de arquivos auditados.

---

## 2. Estrutura do Projeto

```
HOLTECH/
├── backend/
│   ├── main.py                   # API Backend FastAPI principal (entrypoint)
│   ├── app/                      # Arquitetura DDD/MVC (domain, application, infrastructure, presentation)
│   ├── config.py                 # Configurações globais e variáveis de ambiente
│   ├── db.json                   # Banco de dados local em JSON (modo TIPO_BANCO = 0)
│   ├── validador.py              # Regras e funções de validação de planilhas
│   ├── Dockerfile                # Dockerfile oficial da API
│   ├── deployment-aks.yaml       # Manifesto Kubernetes para release no AKS
│   ├── COMO_CONFIGURAR_POSTGRES.md
│   └── requirements.txt          # Dependências Python
├── frontend/
│   ├── admin/
│   │   ├── index.html            # Interface de Gestão de Usuários (CRUD)
│   │   ├── style.css             # Estilos da página de CRUD
│   │   └── style.js              # Lógica de consumo da API no CRUD
│   ├── login/
│       ├── index.html            # Tela de Login
│       ├── style.css             # Estilos do Login
│       └── login.js              # Lógica de autenticação do Login
│   └── landing/
│       └── public/               # Landing Page institucional
└── docs/
    └── DOCUMENTACAO.md
```

---

## 3. Modos de Banco de Dados (`TIPO_BANCO`)

A aplicação possui um seletor dinâmico de banco de dados configurável via variável de ambiente `TIPO_BANCO` ou no arquivo `backend/config.py`:

```python
TIPO_BANCO = int(os.getenv("TIPO_BANCO", "0"))  # 0: JSON (Padrão) | 1: SQL (PostgreSQL)
```

### Comportamento dos Modos:

| Configuração | Descrição | Armazenamento |
| :--- | :--- | :--- |
| **`TIPO_BANCO = 0`** *(Padrão)* | Opera através de um arquivo JSON local. Ideal para desenvolvimento, testes e execução sem necessidade de instalar/configurar o PostgreSQL. | `backend/db.json` |
| **`TIPO_BANCO = 1`** | Conecta-se diretamente a uma instância do PostgreSQL e executa comandos SQL nativos. | Banco PostgreSQL (`login_holtech`) |

> **Nota**: Ao alterar `TIPO_BANCO`, todas as rotas da API (Login, Usuários, Permissões e Histórico) passam automaticamente a utilizar o motor escolhido sem necessidade de refatoração no código.

---

## 4. Estrutura das Tabelas / Coleções

### 1. `TAB_Cadastro` / `usuarios`
Armazena os dados dos usuários do sistema.

| Coluna / Propriedade | Tipo SQL | Tipo JSON | Descrição |
| :--- | :--- | :--- | :--- |
| `Idf_usuario` / `id` | `BIGINT (PK)` | `number` | Identificador único do usuário |
| `Nme_Usuario` / `nome` | `VARCHAR(255)` | `string` | Nome completo |
| `Tpo_Usuario` / `perfil` | `BOOLEAN` | `string` | `true` / `'admin'` para Administrador, `false` / `'user'` para Usuário Comum |
| `Sha_Usuario` / `senha` | `VARCHAR(255)` | `string` | Senha |
| `Eml_Usuario` / `email` | `VARCHAR(255) UNIQUE` | `string` | E-mail do usuário |

---

### 2. `TAB_Permissao` / `permissoes`
Registra as permissões atribuídas aos administradores.

| Coluna / Propriedade | Tipo SQL | Tipo JSON | Descrição |
| :--- | :--- | :--- | :--- |
| `Idf_Permissao` / `id` | `BIGINT (PK)` | `number` | Identificador da permissão |
| `Tpo_Acesso` / `tpo_acesso` | `BOOLEAN` | `boolean` | Status do acesso (`true` para ativo) |
| `Tpo_Usuario_Per` / `tpo_usuario_per` | `VARCHAR(50)` | `string` | Tipo da permissão (ex: `'ADMIN'`) |
| `Idf_Usuario` / `idf_usuario` | `BIGINT (FK)` | `number` | ID do usuário associado em `TAB_Cadastro` |

---

### 3. `TAB_Historico` / `historico`
Registra os logs de auditoria de CRUD e de validações de planilhas.

| Coluna / Propriedade | Tipo SQL | Tipo JSON | Descrição |
| :--- | :--- | :--- | :--- |
| `Idf_Historico` / `Idf_Historico` | `BIGINT (PK)` | `number` | ID do histórico |
| `Dta_Auditoria` / `Dta_Auditoria` | `TIMESTAMP` | `string` | Data e hora do registro |
| `Nme_Planilha` / `Nme_Planilha` | `VARCHAR(255)` | `string` | Nome da planilha ou ação realizada |
| `Cod_Erro` / `Cod_Erro` | `INT` | `number` | Código de erro (se houver) |
| `Stu_Auditoria` / `Stu_Auditoria` | `VARCHAR(50)` | `string` | Status (`'SUCESSO'`, `'ERRO'`, `'ALERTA'`) |
| `Des_Json` / `Des_Json` | `JSONB` | `object` | Detalhes em formato JSON |
| `Idf_Usuario` / `Idf_Usuario` | `BIGINT (FK)` | `number` | ID do usuário realizador da ação |

---

## 5. Regras de Negócio e Permissões

1. **Auto-registro de Permissão Admin**:
   Sempre que um novo usuário for cadastrado como Administrador (ou um usuário existente for atualizado para o perfil `admin`), a aplicação insere automaticamente o registro de permissão na tabela `TAB_Permissao` (SQL) ou no array `permissoes` (JSON).

2. **Acesso Protegido ao CRUD**:
   A interface `/crud/` exige autenticação e restringe o acesso exclusivo para usuários com perfil `admin`.

3. **Navegação Integrada no Streamlit**:
   No painel Streamlit (`app.py`), a barra lateral inclui o botão **`👥 Voltar ao CRUD`** para usuários administradores, permitindo o retorno imediato ao painel de gestão de usuários.

---

## 6. Rotas e Endpoints da API

A API roda por padrão em `http://localhost:8000`.

### Autenticação
- `POST /api/login`: Valida e-mail e senha. Retorna os dados do usuário e perfil (`admin` ou `user`).

### Usuários (CRUD)
- `GET /api/users`: Lista todos os usuários cadastrados.
- `POST /api/users`: Cria um novo usuário. Requer o header `X-User-Id` de um admin. Registra permissão se for admin.
- `PUT /api/users/{id}`: Atualiza os dados de um usuário existente. Requer o header `X-User-Id` de um admin.
- `DELETE /api/users/{id}`: Remove um usuário e suas permissões associadas. Requer o header `X-User-Id` de um admin.

### Auditoria e Histórico
- `GET /api/historico`: Retorna o histórico de auditoria (Admin).
- `GET /api/historico/usuario/{id}`: Retorna o histórico específico de um usuário.
- `POST /api/historico`: Registra um novo log de auditoria.
- `DELETE /api/historico/{id}`: Exclui um registro do histórico.
- `GET /api/debug_db`: Retorna o status atual do modo de banco de dados.

---

## 7. Como Executar o Projeto

### Pré-requisitos
- Python 3.9+ instalado.
- (Opcional) PostgreSQL instalado se for utilizar `TIPO_BANCO = 1`.

### Passo 1: Instalar Dependências

Abra o terminal na pasta `backend` e execute:

```bash
pip install -r requirements.txt
```

---

### Passo 2: Definir o Modo do Banco de Dados

Configure no arquivo `backend/config.py` ou via variável de ambiente:

- Para usar o banco em arquivo **JSON** (padrão, recomendado para testes sem setup de DB):
  ```bash
  # Windows (PowerShell)
  $env:TIPO_BANCO = "0"
  ```

- Para usar o banco **PostgreSQL**:
  ```bash
  # Windows (PowerShell)
  $env:TIPO_BANCO = "1"
  ```
  *(Se utilizar o PostgreSQL, configure também `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` caso sejam diferentes do padrão `localhost:5432`).*

---

### Passo 3: Executar a API FastAPI

Na pasta `backend`, execute:

```bash
python main.py
```
A API ficará disponível em **`http://localhost:8000`**.

---

### Passo 4: Acessar no Navegador

- **Página Inicial (Landing Page)**: [http://localhost:8000/](http://localhost:8000/)
- **Tela de Login**: [http://localhost:8000/login/](http://localhost:8000/login/)
  - *Admin Padrão*: `admin@holtech.com` | Senha: `123`
  - *User Padrão*: `user@holtech.com` | Senha: `123`
- **Painel de Auditoria**: [http://localhost:8000/app/](http://localhost:8000/app/)
- **Gestão de Usuários (CRUD)**: [http://localhost:8000/crud/](http://localhost:8000/crud/)
- **Documentação OpenAPI (Swagger)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
