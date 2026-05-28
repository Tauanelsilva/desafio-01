import datetime
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

from google_integration import atualizar_planilha, salvar_no_drive
from models import SearchRequest, SearchResponse
from scraper import PortalTransparenciaScraper

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
SHEETS_RANGE = os.getenv("GOOGLE_SHEETS_RANGE", "Pagina1!A:C")

app = FastAPI(
    title="API Robô RPA - Portal da Transparência",
    description="API que realiza busca automatizada de beneficiários de programas sociais no Portal da Transparência.",
    version="1.0.0"
)

scraper_bot = PortalTransparenciaScraper()


def validar_token(authorization: str | None):
    """
    Valida o token Bearer caso API_TOKEN esteja configurado no ambiente.
    """
    if not API_TOKEN:
        return

    expected_token = f"Bearer {API_TOKEN}"

    if authorization != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido ou ausente."
        )


@app.post("/api/v1/buscar", response_model=SearchResponse, tags=["Scraper"])
async def buscar_beneficiario(
    request: SearchRequest,
    authorization: str | None = Header(default=None)
):
    """
    Busca um beneficiário no Portal da Transparência por Nome, CPF ou NIS.
    """

    validar_token(authorization)

    try:
        resultado = await scraper_bot.scrape(
            termo=request.termo,
            filtro=request.filtro
        )

        response = SearchResponse(
            sucesso=resultado.get("sucesso", False),
            dados=resultado.get("dados"),
            imagem_base64=resultado.get("imagem_base64"),
            mensagem=resultado.get("mensagem")
        )

        if response.sucesso:
            json_data = response.model_dump_json()

            filename = (
                f"{request.termo.replace(' ', '_')}_"
                f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            drive_file_id = salvar_no_drive(json_data, filename)

            if SPREADSHEET_ID:
                row_data = [
                    request.termo,
                    datetime.datetime.now().isoformat(),
                    "Sucesso",
                    drive_file_id or "Não enviado ao Drive"
                ]

                atualizar_planilha(
                    SPREADSHEET_ID,
                    SHEETS_RANGE,
                    row_data
                )

        return response

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na API: {repr(e)}"
        )


@app.get("/health", tags=["Health"])
def health_check():
    """
    Verifica se a API está ativa.
    """

    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat()
    }