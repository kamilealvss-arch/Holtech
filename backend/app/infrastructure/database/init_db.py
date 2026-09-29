import json
import os
from config import TIPO_BANCO, JSON_DB_FILE


# ─────────────────────────────────────────────────
# Inicialização do banco de dados
# ─────────────────────────────────────────────────

def init_db() -> None:
    """Inicializa o banco de dados de acordo com o TIPO_BANCO configurado."""
    if TIPO_BANCO == 0:
        _init_json()
    else:
        _init_postgres()


# ─────────────────────────────────────────────────
# Modo JSON
# ─────────────────────────────────────────────────

def _init_json() -> None:
    print("[DB MODE] Operando no modo JSON (0 - db.json).")
    if not os.path.exists(JSON_DB_FILE):
        dados_iniciais = {
            "usuarios": [
                {"id": 1, "nome": "Administrador", "email": "admin@holtech.com", "senha": "123", "perfil": "admin"},
                {"id": 2, "nome": "João Silva",    "email": "user@holtech.com",  "senha": "123", "perfil": "user"},
            ],
            "permissoes": [
                {"id": 1, "tpo_acesso": True, "tpo_usuario_per": "ADMIN", "idf_usuario": 1}
            ],
            "historico": [],
        }
        with open(JSON_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dados_iniciais, f, indent=2, ensure_ascii=False)
        print("[DB MODE] Arquivo db.json criado com dados iniciais.")


# ─────────────────────────────────────────────────
# Modo PostgreSQL
# ─────────────────────────────────────────────────

def _init_postgres() -> None:
    print("[DB MODE] Operando no modo SQL (1 - PostgreSQL).")
    try:
        from app.infrastructure.database.connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. TAB_Cadastro
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TAB_Cadastro (
                Idf_usuario  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                Nme_Usuario  VARCHAR(255) NOT NULL,
                Tpo_Usuario  BOOLEAN NOT NULL DEFAULT FALSE,
                Sha_Usuario  VARCHAR(255) NOT NULL,
                Eml_Usuario  VARCHAR(255) NOT NULL UNIQUE
            );
        """)

        # 2. TAB_Permissao
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TAB_Permissao (
                Idf_Permissao   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                Tpo_Acesso      BOOLEAN NOT NULL DEFAULT FALSE,
                Tpo_Usuario_Per VARCHAR(50) NOT NULL,
                Idf_Usuario     BIGINT NOT NULL,
                CONSTRAINT FK_Usuario_Permissao FOREIGN KEY (Idf_Usuario)
                    REFERENCES TAB_Cadastro (Idf_usuario)
                    ON DELETE CASCADE
            );
        """)

        # 3. TAB_Historico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TAB_Historico (
                Idf_Historico BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                Dta_Auditoria TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                Nme_Planilha  VARCHAR(255) NOT NULL,
                Cod_Erro      INT,
                Stu_Auditoria VARCHAR(50) DEFAULT 'SUCESSO' NOT NULL,
                Des_Json      JSONB NOT NULL DEFAULT '{}'::jsonb,
                Idf_Usuario   BIGINT NOT NULL,
                Idf_Permissao BIGINT,
                CONSTRAINT FK_Historico_Usuario FOREIGN KEY (Idf_Usuario)
                    REFERENCES TAB_Cadastro (Idf_usuario)
                    ON DELETE CASCADE
            );
        """)
        conn.commit()

        # Migrações de colunas legadas
        migracoes = [
            "ALTER TABLE TAB_Historico RENAME COLUMN Nome_Planilha TO Nme_Planilha;",
            "ALTER TABLE TAB_Historico RENAME COLUMN Status_Auditoria TO Stu_Auditoria;",
            "ALTER TABLE TAB_Historico RENAME COLUMN Detalhes_Json TO Des_Json;",
            "ALTER TABLE TAB_Historico DROP COLUMN IF EXISTS Tamanho_Arquivo_KB;",
            "ALTER TABLE TAB_Historico ADD COLUMN IF NOT EXISTS Cod_Erro INT;",
        ]
        for sql in migracoes:
            try:
                cursor.execute(sql)
                conn.commit()
            except Exception:
                conn.rollback()

        # Dados padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) AS total FROM TAB_Cadastro;")
        row = cursor.fetchone()
        total = row["total"] if row else 0
        if total == 0:
            cursor.execute("""
                INSERT INTO TAB_Cadastro (Nme_Usuario, Tpo_Usuario, Sha_Usuario, Eml_Usuario) VALUES
                ('Administrador', TRUE,  '123', 'admin@holtech.com'),
                ('João Silva',    FALSE, '123', 'user@holtech.com');
            """)
            print("[DB] Dados iniciais inseridos em TAB_Cadastro.")

        conn.commit()
        cursor.close()
        conn.close()
        print("[DB] PostgreSQL inicializado com sucesso!")
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar PostgreSQL: {e}")
