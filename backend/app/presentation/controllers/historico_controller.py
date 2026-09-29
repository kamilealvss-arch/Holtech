from fastapi import APIRouter, HTTPException
from app.application.schemas.historico_schemas import HistoricoSchema
from app.application.services.historico_service import HistoricoService
from app.infrastructure.factory import get_historico_repository
from config import TIPO_BANCO

router = APIRouter(prefix="/api", tags=["Histórico"])


def _historico_service() -> HistoricoService:
    return HistoricoService(get_historico_repository())


# ─────────────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────────────

@router.get("/historico", summary="Listar histórico completo")
def listar_historico():
    """Retorna todo o histórico de auditoria."""
    return _historico_service().listar_todos()


@router.get("/historico/admin", summary="Listar histórico (admin)")
def listar_historico_admin():
    """Alias para /historico — mantém compatibilidade com o frontend."""
    return _historico_service().listar_todos()


@router.get("/historico/usuario/{user_id}", summary="Histórico por usuário")
def listar_historico_usuario(user_id: int):
    """Retorna o histórico de auditoria filtrado por usuário."""
    return _historico_service().listar_por_usuario(user_id)


@router.post("/historico", summary="Registrar auditoria")
def criar_historico(hist: HistoricoSchema):
    """Cria um novo registro de auditoria."""
    return _historico_service().criar(
        idf_usuario=hist.Idf_Usuario,
        nme_planilha=hist.Nme_Planilha,
        stu_auditoria=hist.Stu_Auditoria,
        des_json=hist.Des_Json,
        cod_erro=hist.Cod_Erro,
        idf_permissao=hist.Idf_Permissao,
    )


@router.delete("/historico/{hist_id}", summary="Excluir registro de auditoria")
def excluir_historico(hist_id: int):
    """Remove um registro do histórico de auditoria."""
    sucesso = _historico_service().excluir(hist_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return {"sucesso": True, "mensagem": "Histórico removido com sucesso"}


@router.get("/debug_db", summary="Status do banco de dados")
def debug_db():
    """Retorna o modo atual de banco de dados (JSON ou PostgreSQL)."""
    if TIPO_BANCO == 0:
        return {"modo": "JSON", "arquivo": "db.json"}
    try:
        from app.infrastructure.database.connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tab_historico';"
        )
        cols = [dict(c) for c in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"modo": "SQL", "colunas": cols}
    except Exception as e:
        return {"erro": str(e)}
