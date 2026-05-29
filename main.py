import datetime
import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.concurrency import run_in_threadpool

from google_integration import atualizar_planilha, salvar_no_drive
from models import SearchRequest, SearchResponse
from scraper import PortalTransparenciaScraper

load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
SHEETS_RANGE = os.getenv("GOOGLE_SHEETS_RANGE", "Pagina1!A:E")

app = FastAPI(
    title="API Robô RPA - Portal da Transparência",
    description="API que realiza busca automatizada de beneficiários de programas sociais no Portal da Transparência.",
    version="1.0.0"
)

# Adiciona CORS para permitir consumo por workflows low-code
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

def validar_token(credentials: HTTPAuthorizationCredentials | None):
    """
    Valida o token Bearer caso API_TOKEN esteja configurado no ambiente.
    """
    if not API_TOKEN:
        return

    if not credentials or credentials.credentials != API_TOKEN:
        logger.warning("Tentativa de acesso com token inválido ou ausente.")
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido ou ausente."
        )

@app.post("/api/v1/buscar", response_model=SearchResponse, tags=["Scraper"])
async def buscar_beneficiario(
    request: SearchRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    """
    Busca um beneficiário no Portal da Transparência por Nome, CPF ou NIS.
    """
    validar_token(credentials)
    identificador_unico = str(uuid.uuid4())
    logger.info(f"[{identificador_unico}] Recebida requisição de busca para o termo: {request.termo}")

    # Instanciamos o bot por requisição para garantir segurança em execuções simultâneas
    scraper_bot = PortalTransparenciaScraper()

    try:
        resultado = await scraper_bot.scrape(
            termo=request.termo,
            filtro=request.filtro
        )

        if not resultado.get("sucesso"):
            logger.info(f"[{identificador_unico}] Busca falhou: {resultado.get('mensagem')}")
            return SearchResponse(**resultado)

        # Prepara a gravação do JSON
        json_data = SearchResponse(**resultado).model_dump_json()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # O desafio exige: [IDENTIFICADOR_UNICO]_[DATA_HORA].json
        filename = f"{identificador_unico}_{timestamp}.json"

        # Hiperautomação interna: Salva no Google Drive e Planilhas em threadpool (não-bloqueante)
        file_id = await run_in_threadpool(salvar_no_drive, json_data, filename)
        drive_link = ""

        if file_id and SPREADSHEET_ID:
            drive_link = f"https://drive.google.com/file/d/{file_id}/view"
            # O desafio pede: Identificador único, Nome, CPF, data/hora, link do Drive
            dados_planilha = [identificador_unico, request.termo, timestamp, drive_link]
            await run_in_threadpool(
                atualizar_planilha,
                SPREADSHEET_ID,
                SHEETS_RANGE,
                dados_planilha
            )

        logger.info(f"[{identificador_unico}] Requisição processada com sucesso.")
        return SearchResponse(**resultado)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"[{identificador_unico}] Erro interno na API")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na automação: {str(e)}"
        )


@app.get("/health", tags=["Status"])
async def health_check():
    """
    Retorna o status da API.
    """
    return {
        "status": "API online",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }
