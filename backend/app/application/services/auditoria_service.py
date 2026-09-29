import os
import io
import re
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import pandas as pd
from validador import validar_planilhas, colorir_excel_holerite
from config import BASE_DIR
from app.infrastructure.factory import get_historico_repository
from app.application.services.historico_service import HistoricoService

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RETENCAO_DIAS = 60


class AuditoriaService:
    """Serviço de Auditoria de Folhas e Planilhas Holtech."""

    def __init__(self):
        self.historico_service = HistoricoService(get_historico_repository())

    @staticmethod
    def _limpar_arquivos_antigos():
        agora = time.time()
        for root, dirs, files in os.walk(UPLOAD_DIR, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                if os.path.isfile(filepath):
                    try:
                        idade = agora - os.path.getctime(filepath)
                        if idade > RETENCAO_DIAS * 86400:
                            os.remove(filepath)
                    except Exception:
                        pass
            for name in dirs:
                dirpath = os.path.join(root, name)
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                except Exception:
                    pass

    @staticmethod
    def _salvar_arquivo(conteudo: bytes, nome_arquivo: str, user_id: int, timestamp_str: str, prefixo: str = "") -> str:
        user_dir = os.path.join(UPLOAD_DIR, str(user_id or "default"), timestamp_str)
        os.makedirs(user_dir, exist_ok=True)
        nome_seguro = re.sub(r'[^A-Za-z0-9_.-]', '', nome_arquivo)
        if prefixo:
            nome_seguro = f"{prefixo}_{nome_seguro}"
        file_path = os.path.join(user_dir, nome_seguro)
        with open(file_path, "wb") as f:
            f.write(conteudo)
        return file_path

    def executar_auditoria(
        self,
        content_holerite: bytes,
        nome_holerite: str,
        content_depara: bytes,
        nome_depara: str,
        content_func: bytes,
        nome_func: str,
        user_id: int = 1,
    ) -> Dict[str, Any]:
        self._limpar_arquivos_antigos()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Salva arquivos originais
        path_holerite = self._salvar_arquivo(content_holerite, nome_holerite, user_id, timestamp_str, "holerite")
        path_depara = self._salvar_arquivo(content_depara, nome_depara, user_id, timestamp_str, "depara")
        path_func = self._salvar_arquivo(content_func, nome_func, user_id, timestamp_str, "func")

        # 2. Executa motor de validação
        file_h_io = io.BytesIO(content_holerite)
        file_h_io.name = nome_holerite
        file_d_io = io.BytesIO(content_depara)
        file_d_io.name = nome_depara
        file_f_io = io.BytesIO(content_func)
        file_f_io.name = nome_func

        df_erros, df_avisos, msg_erro_critico = validar_planilhas(file_h_io, file_d_io, file_f_io)

        detalhes_json = {
            "arquivos": {
                "holerite": path_holerite,
                "depara": path_depara,
                "funcionarios": path_func,
                "auditado": None,
            },
            "avisos": len(df_avisos) if df_avisos is not None and not df_avisos.empty else 0,
            "total_erros": 0,
        }

        # 3. Caso de Erro Crítico
        if msg_erro_critico:
            detalhes_json["erro_critico"] = msg_erro_critico
            hist = self.historico_service.criar(
                idf_usuario=user_id,
                nme_planilha=nome_holerite,
                stu_auditoria="ERRO",
                des_json=detalhes_json,
                cod_erro=500,
            )
            return {
                "sucesso": False,
                "status": "ERRO",
                "mensagem": msg_erro_critico,
                "total_erros": 0,
                "total_avisos": 0,
                "erros": [],
                "avisos": [],
                "erros_por_tipo": {},
                "historico_id": hist.get("idf_historico") or hist.get("Idf_Historico"),
            }

        # 4. Caso de Sucesso sem inconsistências
        if df_erros is None or df_erros.empty:
            avisos_list = df_avisos.to_dict(orient="records") if df_avisos is not None and not df_avisos.empty else []
            hist = self.historico_service.criar(
                idf_usuario=user_id,
                nme_planilha=nome_holerite,
                stu_auditoria="SUCESSO",
                des_json=detalhes_json,
            )
            return {
                "sucesso": True,
                "status": "SUCESSO",
                "mensagem": "Sucesso! Nenhuma inconsistência crítica detectada.",
                "total_erros": 0,
                "total_avisos": len(avisos_list),
                "erros": [],
                "avisos": avisos_list,
                "erros_por_tipo": {},
                "historico_id": hist.get("idf_historico") or hist.get("Idf_Historico"),
                "download_disponivel": False,
            }

        # 5. Caso com Inconsistências / Alertas
        total_erros = len(df_erros)
        detalhes_json["total_erros"] = total_erros
        coluna_tipo = "Tipo de Erro" if "Tipo de Erro" in df_erros.columns else df_erros.columns[0]
        erros_por_tipo = df_erros[coluna_tipo].value_counts().to_dict()

        # Gera e salva planilha colorida
        path_auditado = None
        celulas_pintadas = 0
        try:
            file_h_io.seek(0)
            b_auditado, celulas_pintadas = colorir_excel_holerite(file_h_io, df_erros, df_avisos)
            path_auditado = self._salvar_arquivo(b_auditado, f"AUDITADO_{nome_holerite}", user_id, timestamp_str)
            detalhes_json["arquivos"]["auditado"] = path_auditado
        except Exception as e:
            detalhes_json["aviso_coloracao"] = str(e)

        hist = self.historico_service.criar(
            idf_usuario=user_id,
            nme_planilha=nome_holerite,
            stu_auditoria="ALERTA",
            des_json=detalhes_json,
        )

        erros_list = df_erros.fillna("").to_dict(orient="records")
        avisos_list = df_avisos.fillna("").to_dict(orient="records") if df_avisos is not None and not df_avisos.empty else []

        hist_id = hist.get("idf_historico") or hist.get("Idf_Historico")

        return {
            "sucesso": True,
            "status": "ALERTA",
            "mensagem": f"Auditoria concluída com {total_erros} inconsistências detectadas.",
            "total_erros": total_erros,
            "total_avisos": len(avisos_list),
            "celulas_marcadas": celulas_pintadas,
            "erros_por_tipo": erros_por_tipo,
            "erros": erros_list,
            "avisos": avisos_list,
            "historico_id": hist_id,
            "download_disponivel": path_auditado is not None and os.path.exists(path_auditado),
        }

    def obter_caminho_download(self, historico_id: int) -> Optional[Tuple[str, str]]:
        """Retorna (caminho_absoluto, nome_arquivo) para download do Excel auditado."""
        todos = self.historico_service.listar_todos()
        registro = next(
            (r for r in todos if (r.get("idf_historico") or r.get("Idf_Historico")) == historico_id),
            None
        )
        if not registro:
            return None

        des_json = registro.get("des_json") or registro.get("Des_Json") or {}
        arquivos = des_json.get("arquivos", {})
        path_auditado = arquivos.get("auditado")

        if path_auditado and os.path.isfile(path_auditado):
            return path_auditado, os.path.basename(path_auditado)

        # Fallback para o arquivo original se auditado não existir
        path_orig = arquivos.get("holerite")
        if path_orig and os.path.isfile(path_orig):
            return path_orig, os.path.basename(path_orig)

        return None
