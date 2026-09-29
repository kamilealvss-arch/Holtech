from typing import Optional, List
from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.database.connection import get_db_connection


class UsuarioPgRepository(IUsuarioRepository):
    """Implementação PostgreSQL do repositório de usuários."""

    def listar(self) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                Idf_usuario AS id,
                Nme_Usuario AS nome,
                Eml_Usuario AS email,
                Sha_Usuario AS senha,
                CASE WHEN Tpo_Usuario THEN 'admin' ELSE 'user' END AS perfil
            FROM TAB_Cadastro
            ORDER BY Idf_usuario ASC
        """)
        result = [dict(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result

    def buscar_por_id(self, user_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                Idf_usuario AS id,
                Nme_Usuario AS nome,
                Eml_Usuario AS email,
                Sha_Usuario AS senha,
                CASE WHEN Tpo_Usuario THEN 'admin' ELSE 'user' END AS perfil
            FROM TAB_Cadastro
            WHERE Idf_usuario = %s
        """, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(row) if row else None

    def buscar_por_email_senha(self, email: str, senha: str) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                Idf_usuario AS id,
                Nme_Usuario AS nome,
                Eml_Usuario AS email,
                Tpo_Usuario
            FROM TAB_Cadastro
            WHERE Eml_Usuario = %s AND Sha_Usuario = %s
        """, (email, senha))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            d = dict(row)
            return {
                "id":     d["id"],
                "nome":   d["nome"],
                "email":  d["email"],
                "perfil": "admin" if d["tpo_usuario"] else "user",
            }
        return None

    def criar(self, usuario: Usuario) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TAB_Cadastro (Nme_Usuario, Tpo_Usuario, Sha_Usuario, Eml_Usuario)
            VALUES (%s, %s, %s, %s)
            RETURNING
                Idf_usuario AS id,
                Nme_Usuario AS nome,
                Eml_Usuario AS email,
                Sha_Usuario AS senha,
                CASE WHEN Tpo_Usuario THEN 'admin' ELSE 'user' END AS perfil
        """, (usuario.nome, usuario.perfil == "admin", usuario.senha, usuario.email))
        novo = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        conn.close()
        return novo

    def atualizar(self, user_id: int, usuario: Usuario) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE TAB_Cadastro
            SET Nme_Usuario = %s,
                Tpo_Usuario = %s,
                Sha_Usuario = %s,
                Eml_Usuario = %s
            WHERE Idf_usuario = %s
            RETURNING
                Idf_usuario AS id,
                Nme_Usuario AS nome,
                Eml_Usuario AS email,
                Sha_Usuario AS senha,
                CASE WHEN Tpo_Usuario THEN 'admin' ELSE 'user' END AS perfil
        """, (usuario.nome, usuario.perfil == "admin", usuario.senha, usuario.email, user_id))
        row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return dict(row) if row else None

    def excluir(self, user_id: int) -> Optional[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Eml_Usuario FROM TAB_Cadastro WHERE Idf_usuario = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return None
        email = dict(row)["eml_usuario"]
        cursor.execute("DELETE FROM TAB_Cadastro WHERE Idf_usuario = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return email

    def verificar_admin(self, user_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Tpo_Usuario FROM TAB_Cadastro WHERE Idf_usuario = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return bool(dict(row)["tpo_usuario"]) if row else False

    def criar_permissao_admin(self, user_id: int) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TAB_Permissao (Tpo_Acesso, Tpo_Usuario_Per, Idf_usuario)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM TAB_Permissao WHERE Idf_usuario = %s
            )
        """, (True, "ADMIN", user_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
