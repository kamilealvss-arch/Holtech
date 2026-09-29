import json
import os
from typing import Optional, List
from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import IUsuarioRepository
from config import JSON_DB_FILE


# ─────────────────────────────────────────────────
# Helpers internos de leitura/escrita do JSON
# ─────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(JSON_DB_FILE):
        dados = {
            "usuarios": [
                {"id": 1, "nome": "Administrador", "email": "admin@holtech.com", "senha": "123", "perfil": "admin"},
                {"id": 2, "nome": "João Silva",    "email": "user@holtech.com",  "senha": "123", "perfil": "user"},
            ],
            "permissoes": [
                {"id": 1, "tpo_acesso": True, "tpo_usuario_per": "ADMIN", "idf_usuario": 1}
            ],
            "historico": [],
        }
        _save(dados)
        return dados
    with open(JSON_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(dados: dict) -> None:
    with open(JSON_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────
# Implementação JSON
# ─────────────────────────────────────────────────

class UsuarioJsonRepository(IUsuarioRepository):
    """Implementação JSON (arquivo db.json) do repositório de usuários."""

    def listar(self) -> List[dict]:
        return _load().get("usuarios", [])

    def buscar_por_id(self, user_id: int) -> Optional[dict]:
        return next((u for u in _load().get("usuarios", []) if u["id"] == user_id), None)

    def buscar_por_email_senha(self, email: str, senha: str) -> Optional[dict]:
        return next(
            (u for u in _load().get("usuarios", []) if u["email"] == email and u["senha"] == senha),
            None,
        )

    def criar(self, usuario: Usuario) -> dict:
        db = _load()
        novo_id = max((u["id"] for u in db.get("usuarios", [])), default=0) + 1
        novo = {
            "id":     novo_id,
            "nome":   usuario.nome,
            "email":  usuario.email,
            "senha":  usuario.senha,
            "perfil": usuario.perfil,
        }
        db.setdefault("usuarios", []).append(novo)
        _save(db)
        return novo

    def atualizar(self, user_id: int, usuario: Usuario) -> Optional[dict]:
        db = _load()
        idx = next((i for i, u in enumerate(db.get("usuarios", [])) if u["id"] == user_id), None)
        if idx is None:
            return None
        db["usuarios"][idx].update({
            "nome":   usuario.nome,
            "email":  usuario.email,
            "senha":  usuario.senha,
            "perfil": usuario.perfil,
        })
        _save(db)
        return db["usuarios"][idx]

    def excluir(self, user_id: int) -> Optional[str]:
        db = _load()
        idx = next((i for i, u in enumerate(db.get("usuarios", [])) if u["id"] == user_id), None)
        if idx is None:
            return None
        email = db["usuarios"][idx]["email"]
        db["usuarios"].pop(idx)
        db["permissoes"] = [p for p in db.get("permissoes", []) if p.get("idf_usuario") != user_id]
        _save(db)
        return email

    def verificar_admin(self, user_id: int) -> bool:
        u = self.buscar_por_id(user_id)
        return u is not None and u.get("perfil") == "admin"

    def criar_permissao_admin(self, user_id: int) -> None:
        db = _load()
        if not any(p.get("idf_usuario") == user_id for p in db.get("permissoes", [])):
            perm_id = max((p.get("id", 0) for p in db.get("permissoes", [])), default=0) + 1
            db.setdefault("permissoes", []).append({
                "id":               perm_id,
                "tpo_acesso":       True,
                "tpo_usuario_per":  "ADMIN",
                "idf_usuario":      user_id,
            })
            _save(db)
