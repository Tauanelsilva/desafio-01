from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    termo: str = Field(
        ...,
        description="Nome, CPF ou NIS do beneficiário para busca"
    )

    filtro: Optional[str] = Field(
        default="BENEFICIÁRIO DE PROGRAMA SOCIAL",
        description="Filtro de busca aplicado na consulta"
    )


class BenefitDetail(BaseModel):
    nome_beneficio: str = Field(
        ...,
        description="Nome do benefício encontrado"
    )

    detalhes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detalhes coletados do benefício"
    )


class PersonData(BaseModel):
    panorama: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dados do panorama geral do beneficiário"
    )

    beneficios: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de benefícios associados"
    )


class SearchResponse(BaseModel):
    sucesso: bool = Field(
        ...,
        description="Indica se a busca foi realizada com sucesso"
    )
    dados: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dados do beneficiário e benefícios"
    )
    imagem_base64: Optional[str] = Field(
        default=None,
        description="Screenshot da tela em base64"
    )
    mensagem: str = Field(
        ...,
        description="Mensagem descritiva do resultado da busca"
    )
