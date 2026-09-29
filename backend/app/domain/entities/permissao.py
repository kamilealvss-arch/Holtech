from dataclasses import dataclass
from typing import Optional


@dataclass
class Permissao:
    """Entidade de domínio: representa uma permissão de acesso."""
    tpo_acesso: bool
    tpo_usuario_per: str  # ex: "ADMIN"
    idf_usuario: int
    id: Optional[int] = None
