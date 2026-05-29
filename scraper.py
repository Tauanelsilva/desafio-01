import base64
import logging
from typing import Any, Dict

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from models import BenefitDetail, PersonData

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class PortalTransparenciaScraper:
    def __init__(self):
        self.base_url = "https://portaldatransparencia.gov.br"

    async def scrape(
        self,
        termo: str,
        filtro: str = "BENEFICIÁRIO DE PROGRAMA SOCIAL"
    ) -> Dict[str, Any]:
        logger.info(f"Iniciando busca no portal da transparência para: {termo}")

        async with async_playwright() as p:
            # Recomenda-se modo headless para produção. Em caso de bloqueios, pode-se ajustar args.
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            # Definir viewport padrão para garantir screenshots consistentes
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            try:
                logger.info("Acessando página inicial de Pessoas Físicas...")
                await page.goto(
                    f"{self.base_url}/pessoa/visao-geral",
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(2000)

                # Acessa a opção de Busca de Pessoa Física com fallback
                logger.info("Navegando para o campo de busca...")
                try:
                    botao_busca = page.get_by_role("link", name="Acessar busca").first
                    await botao_busca.click(timeout=10000)
                except Exception:
                    # Fallback caso o botão mude
                    await page.goto(f"{self.base_url}/busca", wait_until="domcontentloaded")
                
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(2000)

                # Preenche o campo de busca
                logger.info("Preenchendo termo de busca...")
                campo_busca = page.locator("input[placeholder*='Buscar'], input.search-input, input").first
                await campo_busca.fill(termo)

                # Aplica filtro social, quando informado
                if filtro:
                    try:
                        logger.info(f"Aplicando filtro: {filtro}")
                        filtro_social = page.get_by_label("Beneficiário de Programa Social")
                        await filtro_social.check(timeout=5000)
                    except Exception as e:
                        logger.warning(f"Não foi possível aplicar o filtro social: {e}")

                # Clica em consultar
                logger.info("Consultando...")
                await page.get_by_role("button", name="Consultar").click()
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)

                texto_pagina = await page.text_content("body") or ""

                # Tratamento de erro: nome inexistente
                if "Foram encontrados 0 resultados" in texto_pagina or "Não encontramos resultados" in texto_pagina:
                    logger.info("Nenhum resultado encontrado.")
                    return {
                        "sucesso": False,
                        "dados": None,
                        "imagem_base64": None,
                        "mensagem": f"Foram encontrados 0 resultados para o termo {termo}."
                    }

                # Tratamento de erro: tempo de resposta
                if "Não foi possível retornar os dados" in texto_pagina:
                    logger.error("Erro no portal: Não foi possível retornar os dados no tempo de resposta solicitado.")
                    return {
                        "sucesso": False,
                        "dados": None,
                        "imagem_base64": None,
                        "mensagem": "Não foi possível retornar os dados no tempo de resposta solicitado."
                    }

                # Clica no primeiro resultado encontrado
                logger.info("Acessando o primeiro resultado da busca...")
                try:
                    primeiro_resultado = page.locator(".resultado-nome a, .box-resultado a").first
                    await primeiro_resultado.click(timeout=10000)
                except Exception as e:
                    logger.warning("Falha ao clicar no primeiro resultado. Tentando buscar link pelo texto...")
                    # Fallback para tentar clicar em qualquer link de pessoa física
                    links = page.get_by_role("link").filter(has_text=termo.upper())
                    if await links.count() > 0:
                        await links.first.click()
                    else:
                        raise e
                
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)

                # Captura de tela (em Base64)
                logger.info("Capturando evidência (screenshot)...")
                screenshot_bytes = await page.screenshot(full_page=True)
                imagem_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

                # Coletar dados do panorama
                logger.info("Coletando dados do panorama...")
                panorama = {}
                resumos = []
                cards = page.locator(".card, .box-resumo, section")
                cards_count = await cards.count()

                for i in range(cards_count):
                    card = cards.nth(i)
                    texto = await card.text_content()
                    if texto:
                        # Limpar excesso de espaços
                        texto_limpo = " ".join(texto.split())
                        if texto_limpo:
                            resumos.append(texto_limpo)

                panorama["resumos"] = list(set(resumos)) # Remover duplicatas se houver

                # Coletar detalhes dos benefícios
                logger.info("Inspecionando lista de benefícios...")
                beneficios = []
                links_beneficios = page.locator("a").filter(
                    has_text="Lista de pagamentos"
                )

                total_links = await links_beneficios.count()

                for i in range(total_links):
                    try:
                        # Recapturamos o link devido à navegação
                        links_atualizados = page.locator("a").filter(has_text="Lista de pagamentos")
                        link = links_atualizados.nth(i)
                        nome = await link.text_content()
                        logger.info(f"Coletando detalhes de: {nome.strip()}")
                        await link.click()
                        await page.wait_for_load_state("domcontentloaded")
                        await page.wait_for_timeout(2000)

                        detalhe = await page.text_content("body") or ""
                        # Limpa quebras de linha e excesso de espaços no detalhe
                        detalhe_limpo = " ".join(detalhe.split())
                        
                        beneficio_dict = {
                            "nome_beneficio": nome.strip(),
                            "detalhes": {"texto_pagina": detalhe_limpo[:2000]} # Limitamos o texto para não estourar o JSON
                        }
                        beneficios.append(beneficio_dict)

                        await page.go_back()
                        await page.wait_for_load_state("domcontentloaded")
                        await page.wait_for_timeout(2000)
                    except Exception as e:
                        logger.error(f"Erro ao coletar detalhe do benefício {i}: {e}")
                        continue

                dados = {
                    "panorama": panorama,
                    "beneficios": beneficios
                }

                logger.info(f"Automação concluída com sucesso para: {termo}")
                return {
                    "sucesso": True,
                    "dados": dados,
                    "imagem_base64": imagem_base64,
                    "mensagem": "Busca realizada com sucesso."
                }

            except PlaywrightTimeoutError:
                logger.error(f"Timeout ao buscar o termo: {termo}")
                return {
                    "sucesso": False,
                    "dados": None,
                    "imagem_base64": None,
                    "mensagem": "Timeout: o portal não respondeu a tempo."
                }

            except Exception as e:
                logger.exception(f"Erro inesperado durante a automação para {termo}")
                return {
                    "sucesso": False,
                    "dados": None,
                    "imagem_base64": None,
                    "mensagem": f"Erro durante a automação: {str(e)}"
                }

            finally:
                logger.info("Encerrando browser...")
                await browser.close()
