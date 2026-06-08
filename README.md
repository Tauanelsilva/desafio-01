<div align="center">

# 🤖 Transparência RPA API

**Automated RPA solution for Brazil's Transparency Portal**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

*API de automação RPA desenvolvida com Python, FastAPI e Playwright para busca automatizada no Portal da Transparência do Governo Federal.*

[Getting Started](#-como-executar) · [Architecture](#-arquitetura-do-projeto) · [API Docs](#-cenários-de-teste) · [Hyperautomation](#-parte-2-hiperautomação)

</div>

---

## 📋 About

This project automates beneficiary lookups on Brazil's [Portal da Transparência](https://portaldatransparencia.gov.br/) through a REST API. It uses **Playwright** for headless browser automation and **FastAPI** as the async web framework, returning structured JSON data including Base64-encoded page screenshots.

The solution also includes a **Hyperautomation** module designed for integration with low-code platforms like Make.com and n8n, enabling end-to-end workflows with Google Drive and Google Sheets.

### ✨ Key Features

- 🔍 **Automated Search** — CPF, NIS, or name-based lookups on the Transparency Portal
- ⚡ **Async & Concurrent** — Isolated browser contexts per request for parallel execution
- 📸 **Evidence Capture** — Base64-encoded screenshots for audit trails
- 🛡️ **Resilient** — Fallback selectors and extended timeouts for portal instability
- 🐳 **Docker Ready** — One-command deployment with Docker Compose
- 🔄 **Hyperautomation** — Ready-to-import Make.com blueprint for Google Drive/Sheets integration

---

## 🛠️ Tech Stack

| Category | Technology |
|:---------|:-----------|
| **Language** | Python 3.11+ |
| **Framework** | FastAPI (async) |
| **Automation** | Playwright (Chromium, headless) |
| **Validation** | Pydantic |
| **Integration** | Google Drive & Sheets API |
| **Deployment** | Docker & Docker Compose |
| **Documentation** | Swagger/OpenAPI (auto-generated) |

---

## 🏗️ Arquitetura do Projeto

```
├── main.py                  # FastAPI app & endpoints
├── scraper.py               # RPA bot with Playwright
├── models.py                # Pydantic request/response models
├── google_integration.py    # Google APIs integration module
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Service orchestration
├── make-blueprint.json      # Make.com workflow blueprint
└── README.md                # Documentation
```

---

## 🚀 Como Executar

### 🐳 Via Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Tauanelsilva/desafio-01.git
cd desafio-01

# 2. Configure environment
cp .env.example .env

# 3. Build and run
docker-compose up --build
```

The API will be available at: `http://localhost:8000/docs`

### 💻 Manual Installation

```bash
# 1. Clone and enter directory
git clone https://github.com/Tauanelsilva/desafio-01.git
cd desafio-01

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Start the API
uvicorn main:app --reload
```

---

## 🧪 Cenários de Teste

Test the API through the Swagger UI at `/docs`:

| Scenario | Input | Expected Result |
|:---------|:------|:----------------|
| ✅ **Success (CPF/NIS)** | Valid CPF or NIS | `success: true`, full JSON with benefits + screenshot |
| ❌ **Not Found** | Invalid CPF/NIS | `success: false`, "0 results found" message |
| ✅ **Success (Name)** | Full name | Fetches data from the first matching result |
| 🔍 **Filtered** | Surname + filter | Applies "Social Program Beneficiary" filter |

---

## ⚡ Parte 2: Hiperautomação

The `make-blueprint.json` file can be imported into **Make.com** for end-to-end automation:

```
Webhook → API RPA Call → Google Drive Upload → Google Sheets Log
```

1. **Webhook** triggers the workflow via HTTP request
2. **API Call** sends POST to the FastAPI endpoint
3. **Google Drive** saves the JSON response as `[UUID]_[DATETIME].json`
4. **Google Sheets** logs a new row with: `ID, Name/CPF, Date, Drive Link`

> 💡 The `google_integration.py` module also supports direct API calls without Make.com.

---

## 🔧 Technical Decisions

| Decision | Rationale |
|:---------|:----------|
| **FastAPI** | High performance, native async/await, auto-generated Swagger docs |
| **Playwright over Selenium** | Faster, better async support, automatic DOM wait handling |
| **Instance per Request** | Isolated browser contexts prevent state overlap in concurrent execution |
| **Fallback Selectors** | Multiple CSS selectors + text-based location for portal UI changes |
| **UUID Identifiers** | Unique execution IDs following `[UUID]_[DATETIME].json` format |

---

## 👩‍💻 Author

**Tauane Luísa Silva** — [LinkedIn](https://www.linkedin.com/in/tauane-silva-62ba85339/) · [GitHub](https://github.com/Tauanelsilva)
