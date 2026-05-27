# Desafio Full Stack Developer - RPA e Hiperautomação (Solução)

Esta é a solução para o desafio de automação robótica de processos utilizando Python, Playwright e FastAPI. 
O projeto contempla a **Parte 1 (Automação Web)**, realizando a extração de dados do Portal da Transparência de forma autônoma e os expondo através de uma API. Também deixamos a arquitetura pronta para a **Parte 2 (Hiperautomação)**.

## Arquitetura do Projeto

* `main.py`: Aplicação FastAPI, expondo a rota `/api/v1/buscar` para a execução do scraper. O Swagger UI / OpenAPI interativo pode ser acessado em `/docs`.
* `scraper.py`: A lógica do robô utilizando Playwright. Opera em modo *headless* podendo suportar múltiplas execuções através do contexto assíncrono do browser.
* `models.py`: Modelos Pydantic para a validação da entrada (request) e saída (response) da API.

## Como Executar Localmente

### 1. Pré-requisitos
Certifique-se de possuir o Python 3.9+ instalado em sua máquina.

### 2. Configurar o Ambiente Virtual

Abra um terminal (ex: PowerShell ou Command Prompt) na pasta do projeto e execute:

```powershell
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
# source venv/bin/activate
```

### 3. Instalar Dependências

Com o ambiente virtual ativado:

```powershell
pip install -r requirements.txt
playwright install chromium
```

### 4. Executar a API

Inicie o servidor com o uvicorn:

```powershell
uvicorn main:app --reload
```

### 5. Testando a Solução

Acesse a interface interativa da API (Swagger) no seu navegador:
**http://localhost:8000/docs**

Encontre a rota **`POST /api/v1/buscar`**, clique em "Try it out", e insira o JSON do corpo da requisição:

```json
{
  "termo": "12345678900", // Insira o CPF, NIS ou Nome do beneficiário
  "filtro": "BENEFICIÁRIO DE PROGRAMA SOCIAL"
}
```

A API retornará um JSON contendo o status de sucesso, os dados capturados e a imagem (Screenshot) convertida em **Base64**.

---

## Observações sobre a Parte 2 (Hiperautomação - Bônus)
O arquivo `main.py` possui placeholders comentados que podem ser ativados caso as credenciais da API do Google Cloud (`credentials.json`) sejam providenciadas. Para plugar a Parte 2:
1. Implemente o módulo `google_integration.py` contendo funções de `salvar_no_drive` e `atualizar_planilha`.
2. Habilite a chamada no fluxo do endpoint FastAPI.
