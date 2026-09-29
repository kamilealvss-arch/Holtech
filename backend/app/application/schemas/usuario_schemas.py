from pydantic import BaseModel


class UsuarioSchema(BaseModel):
    nome: str
    perfil: str   # "admin" | "user"
    email: str
    senha: str
