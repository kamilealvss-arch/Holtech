from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    """Interface (contrato) para o repositório de usuários."""

    @abstractmethod
    def listar(self) -> List[dict]:
        """Lista todos os usuários cadastrados."""
        pass

    @abstractmethod
    def buscar_por_id(self, user_id: int) -> Optional[dict]:
        """Busca um usuário pelo ID."""
        pass

    @abstractmethod
    def buscar_por_email_senha(self, email: str, senha: str) -> Optional[dict]:
        """Busca usuário por e-mail e senha — usado na autenticação."""
        pass

    @abstractmethod
    def criar(self, usuario: Usuario) -> dict:
        """Persiste um novo usuário e retorna o registro criado."""
        pass

    @abstractmethod
    def atualizar(self, user_id: int, usuario: Usuario) -> Optional[dict]:
        """Atualiza os dados de um usuário existente."""
        pass

    @abstractmethod
    def excluir(self, user_id: int) -> Optional[str]:
        """Remove um usuário e retorna o e-mail do registro excluído (ou None se não encontrado)."""
        pass

    @abstractmethod
    def verificar_admin(self, user_id: int) -> bool:
        """Retorna True se o usuário for administrador."""
        pass

    @abstractmethod
    def criar_permissao_admin(self, user_id: int) -> None:
        """Registra permissão de administrador para o usuário (idempotente)."""
        pass
