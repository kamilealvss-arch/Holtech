from config import TIPO_BANCO
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.domain.repositories.historico_repository import IHistoricoRepository


def get_usuario_repository() -> IUsuarioRepository:
    """Factory: retorna a implementação correta de IUsuarioRepository."""
    if TIPO_BANCO == 0:
        from app.infrastructure.repositories.json.usuario_json_repository import UsuarioJsonRepository
        return UsuarioJsonRepository()
    from app.infrastructure.repositories.postgres.usuario_pg_repository import UsuarioPgRepository
    return UsuarioPgRepository()


def get_historico_repository() -> IHistoricoRepository:
    """Factory: retorna a implementação correta de IHistoricoRepository."""
    if TIPO_BANCO == 0:
        from app.infrastructure.repositories.json.historico_json_repository import HistoricoJsonRepository
        return HistoricoJsonRepository()
    from app.infrastructure.repositories.postgres.historico_pg_repository import HistoricoPgRepository
    return HistoricoPgRepository()
