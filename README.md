# Desafio Full Stack Developer - RPA e Hiperautomação

## Sobre o projeto

Este projeto é uma solução de automação RPA desenvolvida em Python para consultar informações no Portal da Transparência de forma automatizada.

A aplicação expõe uma API REST com FastAPI, executa a navegação automatizada com Playwright em modo headless e retorna os dados em formato JSON, incluindo uma captura da página convertida em Base64. Além da automação principal, o projeto possui uma estrutura desenhada e documentada para **Hiperautomação (Parte 2 do Desafio)**, pronta para integração em plataformas low-code como Make.com e n8n, utilizando APIs externas como Google Drive e Google Sheets.

---

## 🛠️ Decisões Técnicas

1. **Uso de FastAPI:** Escolhido pela alta performance, suporte nativo a `async/await` e autogeração de documentação Swagger/OpenAPI.
2. **Playwright:** Preferido sobre o Selenium por ser mais rápido, possuir melhor suporte assíncrono e abstrair automaticamente esperas dinâmicas do DOM.
3. **Instanciação por Requisição (Concorrência):** O `PortalTransparenciaScraper` é instanciado a cada requisição. O Playwright gerencia múltiplos browser contexts separadamente, permitindo *execuções simultâneas* sem sobreposição de estado, o que foi um requisito central.
4. **Resiliência e Fallbacks:** Foram implementados fallbacks nos seletores (ex: tentar localizar botões por nome, e se falhar, acessar via URL direta) para evitar que atualizações simples na interface do Governo quebrem o robô.
5. **UUID como Identificador:** Adição de `uuid4` como identificador único para cada execução, formatando o nome do arquivo exatamente como exigido: `[IDENTIFICADOR_UNICO]_[DATA_HORA].json`.
6. **Docker:** Configuração do ambiente via Dockerfile para garantir consistência entre ambientes e facilitar o deploy da API online.

---

## ⚠️ Desafios Enfrentados

- **Concorrência do Playwright no FastAPI:** Garantir que múltiplas chamadas simultâneas à API não causassem bloqueios. Foi resolvido utilizando `async with async_playwright()` dentro do escopo da requisição, criando browsers e contexts isolados.
- **Instabilidade e Lentidão do Portal:** O Portal da Transparência pode ser intermitente ou lento. Isso foi contornado com *timeouts* extensivos (60s) e tratamento de erros explícito retornando mensagens claras em JSON em vez de travar o servidor.
- **Identificação de Elementos Variáveis:** Diversas classes e seletores no Portal não são fixos (mudam com base na navegação). A solução foi usar múltiplos seletores CSS `.card, .box-resumo, section` e localização baseada em texto para máxima flexibilidade.

---

## Objetivo

Automatizar a busca de beneficiários no Portal da Transparência, estruturando os dados retornados por meio de uma API que pode ser consumida por outros sistemas, workflows low-code ou ferramentas de automação.

---

## Tecnologias utilizadas

* **Python 3.11+**
* **FastAPI** (Servidor Web Assíncrono)
* **Playwright** (Navegação Automatizada)
* **Pydantic** (Validação de Modelos)
* **Google API Client** (Drive e Sheets - via código ou via Hyperautomação)
* **Docker & Docker Compose**

---

## Arquitetura do projeto

```text
.
├── main.py                  # Aplicação FastAPI e endpoints
├── scraper.py               # Robô RPA com Playwright
├── models.py                # Modelos Pydantic de requisição e resposta
├── google_integration.py    # Módulo complementar de integração com Google APIs
├── requirements.txt         # Dependências do projeto
├── Dockerfile               # Configuração do container Docker
├── docker-compose.yml       # Orquestração do serviço
├── make-blueprint.json      # Exemplo de Workflow (Parte 2 - Make.com)
└── README.md                # Documentação
```

---

## Como executar localmente

### 🐳 Via Docker (Recomendado)

O uso de Docker garante que todas as dependências de sistema do Playwright (Chromium) funcionem corretamente.

1. Clone o repositório.
2. Crie seu arquivo `.env` baseado no `.env.example`.
3. Execute o comando:
   ```bash
   docker-compose up --build
   ```
4. A API estará disponível em: `http://localhost:8000/docs`

### 💻 Via Instalação Manual

1. Clone o repositório.
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Instale o navegador do Playwright:
   ```bash
   playwright install chromium
   ```
5. Rode a API:
   ```bash
   uvicorn main:app --reload
   ```

---

## ⚡ Parte 2: Hiperautomação (Workflow)

Para a Parte 2, foi disponibilizado um *Blueprint* pronto (arquivo `make-blueprint.json`) que pode ser importado na plataforma **Make.com**.

### Fluxo do Workflow:
1. **Webhook (Início):** O workflow é engatilhado via requisição HTTP externa.
2. **Action API RPA:** O Make faz uma requisição POST na nossa API FastAPI desenvolvida na Parte 1.
3. **Upload Google Drive:** O Make recebe o JSON da nossa API, o salva com o nome `[IDENTIFICADOR_UNICO]_[DATA_HORA].json` e sobe para o Google Drive.
4. **Insert Google Sheets:** O Make pega o link direto gerado pelo passo anterior e adiciona uma nova linha no Google Sheets com as colunas: `ID, Nome/CPF, Data, Link do Drive`.

> **Nota:** Caso o avaliador prefira testar o fluxo diretamente pelo código (sem o Make.com), a própria API possui as chamadas do módulo `google_integration.py` integradas internamente. Basta adicionar o arquivo `credentials.json` na raiz do projeto e configurar as variáveis no `.env`.

---

## 🧪 Cenários de Teste e Validação

Você pode testar a API através do Swagger na rota `/docs`.

| Cenário | Entrada | Resultado Esperado e Implementado |
| :--- | :--- | :--- |
| **Sucesso (CPF/NIS)** | CPF ou NIS válido | `sucesso: true`, JSON completo com todos os benefícios detalhados e evidência da tela (Base64). |
| **Erro (Inexistente)** | CPF ou NIS falso/inexistente | `sucesso: false`, mensagem "Foram encontrados 0 resultados...". |
| **Sucesso (Nome)** | Nome completo | Acessa e coleta os dados do **primeiro resultado** equivalente exibido pelo portal. |
| **Filtrado** | Sobrenome + Filtro Marcado | Aplica o checklist "Beneficiário de Programa Social", e coleta os dados. |

---

## Boas Práticas Implementadas

* **Separação de Responsabilidades:** API isolada da lógica de Scraping e Integrações.
* **Logging Estruturado:** Uso de `logging` no lugar de `print()` para rastreabilidade de requisições.
* **Middlewares de Segurança:** Implementação de Validação de Token Bearer e CORS.
* **Concorrência:** Scraping encapsulado garantindo execuções simultâneas eficientes.
* **Documentação:** API totalmente documentada via Swagger/OpenAPI nativo do FastAPI.
