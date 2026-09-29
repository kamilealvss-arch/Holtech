from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    """Entidade de domínio: representa um usuário do sistema."""
    nome: str
    email: str
    senha: str
    perfil: str          # "admin" | "user"
    id: Optional[int] = None
