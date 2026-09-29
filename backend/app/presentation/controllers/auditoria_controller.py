import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import FileResponse

from app.application.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/api/auditoria", tags=["Auditoria"])
auditoria_service = AuditoriaService()


@router.post("/validar")
async def validar_auditoria(
    holerite: UploadFile = File(..., description="Arquivo Excel/CSV de Holerites"),
    depara: UploadFile = File(..., description="Arquivo Excel/CSV de De-Para de Verbas"),
    funcionarios: UploadFile = File(..., description="Arquivo Excel/CSV de Funcionários"),
    user_id: Optional[int] = Form(None),
    x_user_id: Optional[str] = Header(None),
):
    """
    Executa a auditoria completa de holerites, de-para e funcionários.
    Pinta as células inconsistentes em vermelho e registra no histórico.
    """
    uid = user_id
    if uid is None and x_user_id and x_user_id.isdigit():
        uid = int(x_user_id)
    if uid is None:
        uid = 1

    try:
        content_h = await holerite.read()
        content_d = await depara.read()
        content_f = await funcionarios.read()

        if not content_h or not content_d or not content_f:
            raise HTTPException(status_code=400, detail="Todos os 3 arquivos devem ser preenchidos e não podem estar vazios.")

        resultado = auditoria_service.executar_auditoria(
            content_holerite=content_h,
            nome_holerite=holerite.filename or "HOLERITE.xlsx",
            content_depara=content_d,
            nome_depara=depara.filename or "DEPARA.xlsx",
            content_func=content_f,
            nome_func=funcionarios.filename or "FUNCIONARIOS.xlsx",
            user_id=uid,
        )
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar auditoria: {str(e)}")


@router.get("/download/{historico_id}")
def download_planilha_auditada(historico_id: int):
    """
    Download do arquivo de holerites auditado (com as células coloridas em vermelho).
    """
    info = auditoria_service.obter_caminho_download(historico_id)
    if not info:
        raise HTTPException(status_code=404, detail="Arquivo auditado não encontrado ou período de retenção expirado.")

    filepath, filename = info
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado no servidor.")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
