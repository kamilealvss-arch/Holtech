from fastapi import APIRouter
from app.application.schemas.auth_schemas import LoginSchema
from app.application.services.auth_service import AuthService
from app.infrastructure.factory import get_usuario_repository

router = APIRouter(prefix="/api", tags=["Autenticação"])


def _auth_service() -> AuthService:
    return AuthService(get_usuario_repository())


@router.post("/login", summary="Autenticar usuário")
def login(dados: LoginSchema):
    """Valida e-mail e senha. Retorna dados do usuário e perfil (admin/user)."""
    return _auth_service().login(dados.email, dados.senha)
