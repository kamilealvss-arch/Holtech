# Holtech

Sistema de auditoria de holerites com landing page, login, painel administrativo, interface web de auditoria e API FastAPI.

## Estrutura

```text
backend/            API FastAPI (arquitetura DDD/MVC), validação de planilhas e banco de dados
frontend/auditoria/ Interface web de auditoria (/app)
frontend/login/     Tela de login HTML/CSS/JS (/login)
frontend/admin/     CRUD administrativo HTML/CSS/JS (/crud)
frontend/landing/   Landing page institucional e arquivos de deploy (/)
docs/               Documentação do projeto
```

## Rodar Localmente

Execute o servidor FastAPI (ele já serve a API e todos os módulos do frontend):

```powershell
cd C:\Users\caiolima\Desktop\HOLTECH
.\.venv\Scripts\python.exe backend\main.py
```

### Rodar com Docker Compose (Opcional)

```powershell
docker compose up --build
```

Acesse:

- Página inicial: http://localhost:8000/
- Login: http://localhost:8000/login/
- Painel de Auditoria: http://localhost:8000/app/
- Painel Administrativo: http://localhost:8000/crud/
- Documentação da API: http://localhost:8000/api/docs

Usuário de teste:

```text
admin@holtech.com
123
```
