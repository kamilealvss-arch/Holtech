from typing import List
from psycopg2.extras import Json
from app.domain.entities.historico import Historico
from app.domain.repositories.historico_repository import IHistoricoRepository
from app.infrastructure.database.connection import get_db_connection


class HistoricoPgRepository(IHistoricoRepository):
    """Implementação PostgreSQL do repositório de histórico."""

    def listar_todos(self) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.Idf_Historico,
                h.Dta_Auditoria,
                h.Nme_Planilha,
                h.Cod_Erro,
                h.Stu_Auditoria,
                h.Des_Json,
                h.Idf_Usuario,
                c.Nme_Usuario
            FROM TAB_Historico h
            JOIN TAB_Cadastro  c ON h.Idf_Usuario = c.Idf_usuario
            ORDER BY h.Dta_Auditoria DESC
        """)
        result = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result

    def listar_por_usuario(self, user_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.Idf_Historico,
                h.Dta_Auditoria,
                h.Nme_Planilha,
                h.Cod_Erro,
                h.Stu_Auditoria,
                h.Des_Json,
                h.Idf_Usuario,
                c.Nme_Usuario
            FROM TAB_Historico h
            JOIN TAB_Cadastro  c ON h.Idf_Usuario = c.Idf_usuario
            WHERE h.Idf_Usuario = %s
            ORDER BY h.Dta_Auditoria DESC
        """, (user_id,))
        result = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result

    def criar(self, historico: Historico) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TAB_Historico
                (Nme_Planilha, Cod_Erro, Stu_Auditoria, Des_Json, Idf_Usuario, Idf_Permissao)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                Idf_Historico, Dta_Auditoria, Nme_Planilha,
                Cod_Erro, Stu_Auditoria, Des_Json, Idf_Usuario, Idf_Permissao
        """, (
            historico.nme_planilha,
            historico.cod_erro,
            historico.stu_auditoria,
            Json(historico.des_json),
            historico.idf_usuario,
            historico.idf_permissao,
        ))
        novo = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        conn.close()
        return novo

    def excluir(self, hist_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TAB_Historico WHERE Idf_Historico = %s", (hist_id,))
        linhas = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return linhas > 0
