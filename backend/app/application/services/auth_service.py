from fastapi import HTTPException
from app.domain.repositories.usuario_repository import IUsuarioRepository


class AuthService:
    """Serviço de autenticação — responsável pelo login de usuários."""

    def __init__(self, usuario_repo: IUsuarioRepository):
        self.usuario_repo = usuario_repo

    def login(self, email: str, senha: str) -> dict:
        usuario = self.usuario_repo.buscar_por_email_senha(email, senha)
        if not usuario:
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
        return {
            "sucesso": True,
            "id":      usuario["id"],
            "nome":    usuario["nome"],
            "perfil":  usuario["perfil"],
        }
