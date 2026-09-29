import json
import os
from typing import List
from datetime import datetime
from app.domain.entities.historico import Historico
from app.domain.repositories.historico_repository import IHistoricoRepository
from config import JSON_DB_FILE


def _load() -> dict:
    if not os.path.exists(JSON_DB_FILE):
        return {"usuarios": [], "permissoes": [], "historico": []}
    with open(JSON_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(dados: dict) -> None:
    with open(JSON_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


class HistoricoJsonRepository(IHistoricoRepository):
    """Implementação JSON (arquivo db.json) do repositório de histórico."""

    def listar_todos(self) -> List[dict]:
        return _load().get("historico", [])

    def listar_por_usuario(self, user_id: int) -> List[dict]:
        return [h for h in _load().get("historico", []) if h.get("Idf_Usuario") == user_id]

    def criar(self, historico: Historico) -> dict:
        db = _load()
        novo_id = len(db.get("historico", [])) + 1
        u = next((u for u in db.get("usuarios", []) if u["id"] == historico.idf_usuario), None)
        nme_usuario = u["nome"] if u else "Sistema"

        novo = {
            "Idf_Historico": novo_id,
            "Dta_Auditoria": datetime.now().isoformat(),
            "Nme_Planilha":  historico.nme_planilha,
            "Cod_Erro":      historico.cod_erro,
            "Stu_Auditoria": historico.stu_auditoria,
            "Des_Json":      historico.des_json,
            "Idf_Usuario":   historico.idf_usuario,
            "Idf_Permissao": historico.idf_permissao,
            "Nme_Usuario":   nme_usuario,
        }
        db.setdefault("historico", []).insert(0, novo)
        _save(db)
        return novo

    def excluir(self, hist_id: int) -> bool:
        db = _load()
        idx = next(
            (i for i, h in enumerate(db.get("historico", [])) if h.get("Idf_Historico") == hist_id),
            None,
        )
        if idx is None:
            return False
        db["historico"].pop(idx)
        _save(db)
        return True
