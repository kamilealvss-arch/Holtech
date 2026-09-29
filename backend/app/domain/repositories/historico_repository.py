from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.historico import Historico


class IHistoricoRepository(ABC):
    """Interface (contrato) para o repositório de histórico de auditoria."""

    @abstractmethod
    def listar_todos(self) -> List[dict]:
        """Lista todo o histórico de auditoria."""
        pass

    @abstractmethod
    def listar_por_usuario(self, user_id: int) -> List[dict]:
        """Lista o histórico filtrado por usuário."""
        pass

    @abstractmethod
    def criar(self, historico: Historico) -> dict:
        """Persiste um novo registro de auditoria."""
        pass

    @abstractmethod
    def excluir(self, hist_id: int) -> bool:
        """Remove um registro de auditoria. Retorna True se removido."""
        pass
