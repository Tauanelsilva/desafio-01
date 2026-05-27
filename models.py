from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    termo: str = Field(..., description="Nome, CPF ou NIS do beneficiário para busca")
    filtro: Optional[str] = Field(default="BENEFICIÁRIO DE PROGRAMA SOCIAL", description="Filtro de busca a ser aplicado")

class BenefitDetail(BaseModel):
    nome_beneficio: str
    detalhes: Dict[str, Any] = Field(default_factory=dict)

class PersonData(BaseModel):
    panorama: Dict[str, Any] = Field(default_factory=dict)
    beneficios: List[BenefitDetail] = Field(default_factory=list)

class SearchResponse(BaseModel):
    sucesso: bool
    dados: Optional[PersonData] = None
    imagem_base64: Optional[str] = Field(None, description="Screenshot da página em Base64")
    mensagem: Optional[str] = None
