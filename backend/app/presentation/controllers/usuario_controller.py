from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from app.application.schemas.usuario_schemas import UsuarioSchema
from app.application.services.usuario_service import UsuarioService
from app.application.services.historico_service import HistoricoService
from app.infrastructure.factory import get_usuario_repository, get_historico_repository

router = APIRouter(prefix="/api", tags=["Usuários"])


# ─────────────────────────────────────────────────
# Injeção de dependências
# ─────────────────────────────────────────────────

def _usuario_service() -> UsuarioService:
    historico_svc = HistoricoService(get_historico_repository())
    return UsuarioService(get_usuario_repository(), historico_svc)


def get_admin_id(x_user_id: Optional[str] = Header(None)) -> int:
    """Extrai e valida o ID do administrador do header X-User-Id."""
    if not x_user_id or not x_user_id.isdigit():
        raise HTTPException(status_code=401, detail="Header X-User-Id inválido ou ausente")
    return int(x_user_id)


# ─────────────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────────────

@router.get("/users", summary="Listar usuários")
def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados."""
    return _usuario_service().listar()


@router.post("/users", summary="Criar usuário")
def criar_usuario(user: UsuarioSchema, admin_id: int = Depends(get_admin_id)):
    """Cria um novo usuário. Requer header X-User-Id de um administrador."""
    return _usuario_service().criar(admin_id, user.nome, user.email, user.senha, user.perfil)


@router.put("/users/{user_id}", summary="Atualizar usuário")
def atualizar_usuario(user_id: int, user: UsuarioSchema, admin_id: int = Depends(get_admin_id)):
    """Atualiza os dados de um usuário. Requer header X-User-Id de um administrador."""
    return _usuario_service().atualizar(admin_id, user_id, user.nome, user.email, user.senha, user.perfil)


@router.delete("/users/{user_id}", summary="Excluir usuário")
def excluir_usuario(user_id: int, admin_id: int = Depends(get_admin_id)):
    """Remove um usuário e suas permissões. Requer header X-User-Id de um administrador."""
    return _usuario_service().excluir(admin_id, user_id)
