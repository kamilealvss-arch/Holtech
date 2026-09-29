from pydantic import BaseModel
from typing import Optional


class HistoricoSchema(BaseModel):
    Idf_Usuario:   int
    Idf_Permissao: Optional[int] = None
    Nme_Planilha:  str
    Cod_Erro:      Optional[int] = None
    Stu_Auditoria: str
    Des_Json:      dict
