from fastapi import HTTPException
from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.application.services.historico_service import HistoricoService


class UsuarioService:
    """Serviço de usuários — orquestra regras de negócio de CRUD."""

    def __init__(self, usuario_repo: IUsuarioRepository, historico_service: HistoricoService):
        self.usuario_repo = usuario_repo
        self.historico_service = historico_service

    # ─────────────────────────────────────────────────
    # Verificação de permissão
    # ─────────────────────────────────────────────────

    def verificar_admin(self, admin_id: int) -> None:
        """Lança HTTPException se o usuário não for administrador."""
        usuario = self.usuario_repo.buscar_por_id(admin_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário solicitante não encontrado")
        if usuario.get("perfil") != "admin":
            raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")

    # ─────────────────────────────────────────────────
    # Operações CRUD
    # ─────────────────────────────────────────────────

    def listar(self) -> list:
        return self.usuario_repo.listar()

    def criar(self, admin_id: int, nome: str, email: str, senha: str, perfil: str) -> dict:
        try:
            self.verificar_admin(admin_id)
            usuario = Usuario(nome=nome, email=email, senha=senha, perfil=perfil)
            novo = self.usuario_repo.criar(usuario)
            if perfil == "admin":
                self.usuario_repo.criar_permissao_admin(novo["id"])
            self.historico_service.registrar_auditoria(
                admin_id, "CRIAR_USUARIO", "SUCESSO",
                {"usuario_id": novo["id"], "usuario_email": email},
            )
            return novo
        except HTTPException as he:
            self.historico_service.registrar_auditoria(
                admin_id, "CRIAR_USUARIO", "ERRO",
                {"usuario_email": email, "erro": he.detail}, he.status_code,
            )
            raise
        except Exception as e:
            self.historico_service.registrar_auditoria(
                admin_id, "CRIAR_USUARIO", "ERRO",
                {"usuario_email": email, "erro": str(e)}, 500,
            )
            raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

    def atualizar(self, admin_id: int, user_id: int, nome: str, email: str, senha: str, perfil: str) -> dict:
        try:
            self.verificar_admin(admin_id)
            usuario = Usuario(nome=nome, email=email, senha=senha, perfil=perfil)
            atualizado = self.usuario_repo.atualizar(user_id, usuario)
            if not atualizado:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            if perfil == "admin":
                self.usuario_repo.criar_permissao_admin(user_id)
            self.historico_service.registrar_auditoria(
                admin_id, "EDITAR_USUARIO", "SUCESSO",
                {"usuario_id": user_id, "usuario_email": email},
            )
            return atualizado
        except HTTPException as he:
            self.historico_service.registrar_auditoria(
                admin_id, "EDITAR_USUARIO", "ERRO",
                {"usuario_id": user_id, "erro": he.detail}, he.status_code,
            )
            raise
        except Exception as e:
            self.historico_service.registrar_auditoria(
                admin_id, "EDITAR_USUARIO", "ERRO",
                {"usuario_id": user_id, "erro": str(e)}, 500,
            )
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

    def excluir(self, admin_id: int, user_id: int) -> dict:
        try:
            self.verificar_admin(admin_id)
            email = self.usuario_repo.excluir(user_id)
            if email is None:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            self.historico_service.registrar_auditoria(
                admin_id, "EXCLUIR_USUARIO", "SUCESSO",
                {"usuario_id": user_id, "usuario_email": email},
            )
            return {"sucesso": True, "mensagem": "Usuário removido com sucesso"}
        except HTTPException as he:
            self.historico_service.registrar_auditoria(
                admin_id, "EXCLUIR_USUARIO", "ERRO",
                {"usuario_id": user_id, "erro": he.detail}, he.status_code,
            )
            raise
        except Exception as e:
            self.historico_service.registrar_auditoria(
                admin_id, "EXCLUIR_USUARIO", "ERRO",
                {"usuario_id": user_id, "erro": str(e)}, 500,
            )
            raise HTTPException(status_code=500, detail=f"Erro ao excluir usuário: {str(e)}")
