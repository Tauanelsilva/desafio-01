import asyncio
import base64
from typing import Dict, Any
from playwright.async_api import async_playwright
from models import PersonData, BenefitDetail

class PortalTransparenciaScraper:
    def __init__(self):
        self.base_url = "https://portaldatransparencia.gov.br"

    async def scrape(self, termo: str, filtro: str = "BENEFICIÁRIO DE PROGRAMA SOCIAL") -> Dict[str, Any]:
        async with async_playwright() as p:
            # Lança o browser em modo headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Acessa a página principal de busca
                # Na prática, o Portal da Transparência redireciona as buscas, 
                # vamos simular a navegação da forma mais estável: acessando a URL de busca diretamente
                # O parâmetro 'termo' é passado na querystring.
                search_url = f"{self.base_url}/busca?termo={termo}"
                await page.goto(search_url, wait_until="networkidle")

                # Espera carregar os resultados. Se houver filtro, precisamos clicar nele.
                # O filtro "Beneficiário de Programa Social" costuma aparecer na lateral
                # Vamos tentar aplicar o filtro se ele existir na página
                if filtro:
                    try:
                        # Busca por um botão/link que contenha o texto do filtro e clica
                        filter_element = page.locator(f"text='{filtro}'").first
                        if await filter_element.is_visible():
                            await filter_element.click()
                            await page.wait_for_load_state("networkidle")
                    except Exception as e:
                        print(f"Não foi possível aplicar o filtro: {e}")

                # Clica no primeiro resultado correspondente a uma pessoa física/jurídica
                # Normalmente, os links têm uma classe específica ou estão dentro de h3/a
                # Vamos tentar pegar o primeiro link relevante
                first_result = page.locator("css=.resultados-busca a").first
                if await first_result.is_visible():
                    # Pega a URL do perfil
                    profile_url = await first_result.get_attribute('href')
                    if profile_url and not profile_url.startswith('http'):
                        profile_url = self.base_url + profile_url
                    
                    # Vai para a página de perfil da pessoa
                    await page.goto(profile_url, wait_until="networkidle")
                else:
                    # Se não achou de forma convencional, a busca pode não ter resultados
                    pass

                # Tira o screenshot da página "Panorama da relação..."
                screenshot_bytes = await page.screenshot(full_page=True)
                base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')

                # Extrai dados básicos do panorama
                panorama_data = {}
                # Aqui buscaríamos os elementos de panorama (ex: .box-resumo)
                box_resumos = await page.locator("css=.box-resumo").all_text_contents()
                panorama_data['resumos'] = [b.strip() for b in box_resumos]

                # Extrai os benefícios (Auxílio Brasil, Auxílio Emergencial, Bolsa Família)
                beneficios_extraidos = []
                # Exemplo: Procura acordions ou abas de benefícios
                # (Lógica genérica pois o layout exato exigiria inspeção do DOM vivo)
                secoes_beneficios = await page.locator("css=.secao-beneficio").all()
                for secao in secoes_beneficios:
                    nome = await secao.locator("css=h3").inner_text()
                    detalhes = await secao.locator("css=.detalhes").inner_text()
                    beneficios_extraidos.append(BenefitDetail(
                        nome_beneficio=nome.strip(),
                        detalhes={"info": detalhes.strip()}
                    ))

                # Se a lista estiver vazia por falta da classe correta, a API retornará o que conseguiu

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

            except Exception as e:
                # Tira um screenshot do erro para debug, se possível
                error_screenshot = ""
                try:
                    screenshot_bytes = await page.screenshot()
                    error_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                except:
                    pass

                return {
                    "sucesso": False,
                    "dados": None,
                    "imagem_base64": error_screenshot or None,
                    "mensagem": f"Erro durante a execução do scraper: {str(e)}"
                }
            finally:
                await context.close()
                await browser.close()
