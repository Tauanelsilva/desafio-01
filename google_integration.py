import io
import json
import logging
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)

# SCOPES necessários para o Drive e Sheets
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']

# Nome do arquivo de credenciais (pode ser sobrescrito via ENV)
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")


def _get_credentials():
    """Obtém as credenciais da conta de serviço (se existir o arquivo)."""
    if os.path.exists(CREDENTIALS_FILE):
        return service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
    return None


def salvar_no_drive(json_data: str, filename: str) -> str | None:
    """Faz o upload do JSON para o Google Drive e retorna o ID do arquivo."""
    creds = _get_credentials()
    if not creds:
        logger.warning(f"Arquivo {CREDENTIALS_FILE} não encontrado. Upload para o Drive ignorado.")
        return None

    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': filename, 'mimeType': 'application/json'}
        media = MediaIoBaseUpload(io.BytesIO(json_data.encode('utf-8')), mimetype='application/json', resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"Arquivo salvo no Drive com sucesso. ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Erro ao salvar no Drive: {e}")
        return None


def atualizar_planilha(spreadsheet_id: str, range_name: str, row_data: list) -> bool:
    """Adiciona uma nova linha com os dados (row_data) no Google Sheets."""
    creds = _get_credentials()
    if not creds:
        logger.warning(f"Arquivo {CREDENTIALS_FILE} não encontrado. Atualização do Sheets ignorada.")
        return False

    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': [row_data]
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        updates = result.get('updates', {}).get('updatedCells', 0)
        logger.info(f"Planilha atualizada com sucesso: {updates} células modificadas.")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar planilha: {e}")
        return False
