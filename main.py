from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models import SearchRequest, SearchResponse
from scraper import PortalTransparenciaScraper
import datetime
import os

# Integração com Google (Parte 2)
from google_integration import salvar_no_drive, atualizar_planilha

app = FastAPI(
    title="API Robô RPA - Portal da Transparência",
    description="API que realiza busca automatizada de beneficiários de programas sociais no Portal da Transparência.",
    version="1.0.0"
)

scraper_bot = PortalTransparenciaScraper()

@app.post("/api/v1/buscar", response_model=SearchResponse, tags=["Scraper"])
async def buscar_beneficiario(request: SearchRequest):
    """
    Endpoint para buscar um beneficiário no Portal da Transparência pelo Nome, CPF ou NIS.
    O robô opera em background utilizando Playwright (headless).
    """
    try:
        resultado = await scraper_bot.scrape(termo=request.termo, filtro=request.filtro)
        
        # Estrutura a resposta
        response = SearchResponse(
            sucesso=resultado.get("sucesso", False),
            dados=resultado.get("dados"),
            imagem_base64=resultado.get("imagem_base64"),
            mensagem=resultado.get("mensagem")
        )

        # PARTE 2: Bônus Hiperautomação (Google Drive / Sheets)
        if response.sucesso:
            json_data = response.model_dump_json()
            filename = f"{request.termo.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Salva o arquivo no drive e atualiza a planilha (silencioso se não houver credentials.json)
            salvar_no_drive(json_data, filename)
            
            # ATENÇÃO: Substitua os valores abaixo pela sua ID de planilha real e nome da aba
            SPREADSHEET_ID = 'SUA_SPREADSHEET_ID_AQUI'
            RANGE_NAME = 'Página1!A:C'
            
            row_data = [request.termo, datetime.datetime.now().isoformat(), "Sucesso"]
            atualizar_planilha(SPREADSHEET_ID, RANGE_NAME, row_data)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint para verificação de saúde da API.
    """
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}
