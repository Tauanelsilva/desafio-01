# Desafio Full Stack Developer - RPA e Hiperautomação

## Sobre o projeto

Este projeto é uma solução de automação RPA desenvolvida em Python para consultar informações no Portal da Transparência de forma automatizada.

A aplicação expõe uma API REST com FastAPI, executa a navegação automatizada com Playwright em modo headless e retorna os dados em formato JSON, incluindo uma captura da página convertida em Base64.

Além da automação principal, o projeto possui uma estrutura preparada para hiperautomação, permitindo integração com Google Drive e Google Sheets por meio de APIs externas.

---

# Objetivo

Automatizar a busca de beneficiários no Portal da Transparência, estruturando os dados retornados por meio de uma API que pode ser consumida por outros sistemas, workflows low-code ou ferramentas de automação.

---

# Tecnologias utilizadas

* Python
* FastAPI
* Playwright
* Pydantic
* Uvicorn
* Google Drive API
* Google Sheets API
* Git e GitHub

---

# Arquitetura do projeto

```text
.
├── main.py                  # Aplicação FastAPI e definição dos endpoints
├── scraper.py               # Robô RPA com Playwright
├── models.py                # Modelos Pydantic de entrada e saída
├── google_integration.py    # Integração opcional com Google Drive e Sheets
├── requirements.txt         # Dependências do projeto
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Documentação do projeto
```

---

# Fluxo da automação

1. O usuário envia uma requisição para a API.
2. A API recebe o termo de busca e o filtro desejado.
3. O Playwright abre o navegador em modo headless.
4. O robô acessa o Portal da Transparência.
5. A automação realiza a busca e tenta aplicar o filtro informado.
6. O sistema captura os dados disponíveis na página.
7. A página consultada é salva como screenshot em Base64.
8. A API retorna uma resposta estruturada em JSON.
9. Opcionalmente, os dados podem ser enviados ao Google Drive e Google Sheets.

---

# Endpoints

## Health check

```http
GET /health
```

Retorna o status da API.

---

## Buscar beneficiário

```http
POST /api/v1/buscar
```

Executa a automação de busca no Portal da Transparência.

### Exemplo de requisição

```json
{
  "termo": "12345678900",
  "filtro": "BENEFICIÁRIO DE PROGRAMA SOCIAL"
}
```

### Exemplo de resposta

```json
{
  "sucesso": true,
  "dados": {
    "panorama": {
      "resumos": []
    },
    "beneficios": []
  },
  "imagem_base64": "string_base64_da_imagem",
  "mensagem": "Busca realizada com sucesso."
}
```

---

# Como executar localmente

## 1. Pré-requisitos

* Python 3.9 ou superior
* Git instalado

---

## 2. Clonar o repositório

```bash
git clone https://github.com/Tauanelsilva/desafio-01.git
cd desafio-01
```

---

## 3. Criar ambiente virtual

```bash
python -m venv venv
```

### No Windows

```bash
.\venv\Scripts\activate
```

### No Linux/Mac

```bash
source venv/bin/activate
```

---

## 4. Instalar dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 5. Executar a API

```bash
uvicorn main:app --reload
```

Acesse a documentação interativa em:

```text
http://localhost:8000/docs
```

---

# Integração com Google Drive e Google Sheets

O projeto possui integração opcional com Google Drive e Google Sheets.

Quando existe um arquivo `credentials.json` válido na raiz do projeto, a aplicação pode:

* salvar o resultado da consulta em formato JSON no Google Drive;
* registrar informações da execução em uma planilha Google Sheets.

Por segurança, o arquivo `credentials.json` não deve ser enviado ao GitHub.

---

# Variáveis e arquivos sensíveis

Os seguintes arquivos devem permanecer fora do versionamento:

```text
.env
credentials.json
venv/
__pycache__/
```

Esses arquivos estão configurados no `.gitignore`.

---

# Possível integração com workflows low-code

A API foi estruturada para ser consumida por ferramentas de automação como:

* n8n
* Make
* Windmill
* Zapier

## Exemplo de fluxo

1. Um webhook recebe uma solicitação.
2. O workflow envia uma requisição HTTP para `POST /api/v1/buscar`.
3. A resposta JSON é tratada dentro do fluxo.
4. O resultado pode ser salvo em banco de dados, planilha ou enviado para outro sistema.
5. Uma notificação pode ser disparada para o usuário final.

---

# Boas práticas aplicadas

* Separação entre API, modelos, scraper e integrações externas.
* Uso de modelos Pydantic para validação dos dados.
* Uso de Playwright assíncrono.
* Retorno padronizado em JSON.
* Documentação via Swagger/OpenAPI.
* Arquivos sensíveis ignorados pelo Git.
* Versionamento com Git e GitHub.

---

# Melhorias futuras

* Persistência em banco de dados PostgreSQL ou MongoDB.
* Criação de workflow real no n8n.
* Implementação de autenticação por token na API.
* Adição de testes automatizados.
* Deploy em ambiente cloud ou serverless.
* Monitoramento de execuções e logs estruturados.

1. Implemente o módulo `google_integration.py` contendo funções de `salvar_no_drive` e `atualizar_planilha`.
2. Habilite a chamada no fluxo do endpoint FastAPI.
