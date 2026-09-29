from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Historico:
    """Entidade de domínio: representa um registro de auditoria."""
    nme_planilha: str
    stu_auditoria: str
    des_json: dict
    idf_usuario: int
    id: Optional[int] = None
    dta_auditoria: Optional[datetime] = None
    cod_erro: Optional[int] = None
    idf_permissao: Optional[int] = None
    nme_usuario: Optional[str] = None
