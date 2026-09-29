from typing import List, Optional
from app.domain.entities.historico import Historico
from app.domain.repositories.historico_repository import IHistoricoRepository


class HistoricoService:
    """Serviço de histórico — gerencia registros de auditoria."""

    def __init__(self, historico_repo: IHistoricoRepository):
        self.historico_repo = historico_repo

    def listar_todos(self) -> List[dict]:
        return self.historico_repo.listar_todos()

    def listar_por_usuario(self, user_id: int) -> List[dict]:
        return self.historico_repo.listar_por_usuario(user_id)

    def criar(
        self,
        idf_usuario: int,
        nme_planilha: str,
        stu_auditoria: str,
        des_json: dict,
        cod_erro: Optional[int] = None,
        idf_permissao: Optional[int] = None,
    ) -> dict:
        historico = Historico(
            nme_planilha=nme_planilha,
            stu_auditoria=stu_auditoria,
            des_json=des_json,
            idf_usuario=idf_usuario,
            cod_erro=cod_erro,
            idf_permissao=idf_permissao,
        )
        return self.historico_repo.criar(historico)

    def excluir(self, hist_id: int) -> bool:
        return self.historico_repo.excluir(hist_id)

    def registrar_auditoria(
        self,
        admin_id: int,
        acao: str,
        status: str,
        detalhes: dict,
        cod_erro: Optional[int] = None,
    ) -> None:
        """Registra um log de auditoria de forma silenciosa (nunca levanta exceção)."""
        try:
            self.criar(
                idf_usuario=admin_id,
                nme_planilha="GESTAO_USUARIOS",
                stu_auditoria=status,
                des_json={"acao": acao, **detalhes},
                cod_erro=cod_erro,
            )
        except Exception as e:
            print(f"[AVISO] Falha ao registrar auditoria '{acao}': {e}")
