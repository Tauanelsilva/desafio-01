import base64
from typing import Any, Dict

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from models import BenefitDetail, PersonData


class PortalTransparenciaScraper:
    def __init__(self):
        self.base_url = "https://portaldatransparencia.gov.br"

    async def scrape(
        self,
        termo: str,
        filtro: str = "BENEFICIÁRIO DE PROGRAMA SOCIAL"
    ) -> Dict[str, Any]:

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(
                    f"{self.base_url}/pessoa/visao-geral",
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                await page.wait_for_timeout(2000)

                # Acessa a opção de Busca de Pessoa Física
                botao_busca = page.get_by_role("link", name="Acessar busca").first
                await botao_busca.click()
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(2000)

                # Preenche o campo de busca
                campo_busca = page.locator("input").first
                await campo_busca.fill(termo)

                # Aplica filtro social, quando informado
                if filtro:
                    try:
                        filtro_social = page.get_by_label("Beneficiário de Programa Social")
                        await filtro_social.check()
                    except Exception:
                        pass

                # Clica em consultar
                await page.get_by_role("button", name="Consultar").click()
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)

                texto_pagina = await page.text_content("body") or ""

                # Tratamento de erro: nome inexistente
                if "Foram encontrados 0 resultados" in texto_pagina:
                    return {
                        "sucesso": False,
                        "dados": None,
                        "imagem_base64": None,
                        "mensagem": f"Foram encontrados 0 resultados para o termo {termo}."
                    }

                # Tratamento de erro: tempo de resposta
                if "Não foi possível retornar os dados" in texto_pagina:
                    return {
                        "sucesso": False,
                        "dados": None,
                        "imagem_base64": None,
                        "mensagem": "Não foi possível retornar os dados no tempo de resposta solicitado."
                    }

                # Tenta abrir o primeiro resultado clicável
                links = page.locator("a")
                total_links = await links.count()

                abriu_resultado = False

                for i in range(total_links):
                    link_texto = await links.nth(i).inner_text()
                    href = await links.nth(i).get_attribute("href")

                    if href and (
                        "/pessoa-fisica/" in href
                        or "pessoa-fisica" in href
                        or termo.lower() in link_texto.lower()
                    ):
                        await links.nth(i).click()
                        abriu_resultado = True
                        break

                if not abriu_resultado:
                    screenshot_bytes = await page.screenshot(full_page=True)
                    base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")

                    return {
                        "sucesso": False,
                        "dados": None,
                        "imagem_base64": base64_image,
                        "mensagem": "Resultado encontrado, mas não foi possível abrir o primeiro registro automaticamente."
                    }

                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)

                # Screenshot da tela de panorama
                screenshot_bytes = await page.screenshot(full_page=True)
                base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")

                texto_pessoa = await page.text_content("body") or ""

                panorama_data = {
                    "conteudo_pagina": texto_pessoa
                }

                beneficios_extraidos = []

                beneficios_mapeados = [
                    "Auxílio Brasil",
                    "Auxílio Emergencial",
                    "Bolsa Família"
                ]

                for beneficio in beneficios_mapeados:
                    if beneficio.lower() in texto_pessoa.lower():
                        beneficios_extraidos.append(
                            BenefitDetail(
                                nome_beneficio=beneficio,
                                detalhes={
                                    "encontrado_no_panorama": True
                                }
                            )
                        )

                # Tenta acessar botões/link de detalhamento
                botoes_detalhar = page.get_by_role("link", name="Detalhar")
                total_detalhar = await botoes_detalhar.count()

                for i in range(total_detalhar):
                    try:
                        await botoes_detalhar.nth(i).click()
                        await page.wait_for_load_state("domcontentloaded")
                        await page.wait_for_timeout(2000)

                        texto_detalhe = await page.text_content("body") or ""

                        beneficios_extraidos.append(
                            BenefitDetail(
                                nome_beneficio=f"Benefício detalhado {i + 1}",
                                detalhes={
                                    "conteudo_detalhado": texto_detalhe
                                }
                            )
                        )

                        await page.go_back()
                        await page.wait_for_load_state("domcontentloaded")
                        await page.wait_for_timeout(2000)

                        botoes_detalhar = page.get_by_role("link", name="Detalhar")

                    except Exception:
                        continue

                person_data = PersonData(
                    panorama=panorama_data,
                    beneficios=beneficios_extraidos
                )

                return {
                    "sucesso": True,
                    "dados": person_data.model_dump(),
                    "imagem_base64": base64_image,
                    "mensagem": "Busca realizada com sucesso."
                }

            except PlaywrightTimeoutError:
                return {
                    "sucesso": False,
                    "dados": None,
                    "imagem_base64": None,
                    "mensagem": "Não foi possível retornar os dados no tempo de resposta solicitado."
                }

            except Exception as e:
                error_screenshot = None

                try:
                    screenshot_bytes = await page.screenshot(full_page=True)
                    error_screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
                except Exception:
                    pass

                return {
                    "sucesso": False,
                    "dados": None,
                    "imagem_base64": error_screenshot,
                    "mensagem": f"Erro durante a execução do scraper: {repr(e)}"
                }

            finally:
                await context.close()
                await browser.close()