from pydantic import BaseModel
from typing import Optional


class OpcaoFrete(BaseModel):
    transportadora: str
    servico: str
    preco: float
    prazo_dias: int
    peso_considerado_kg: float
    observacao: Optional[str] = None


class ResultadoCotacao(BaseModel):
    cep_origem: str
    cep_destino: str
    peso_kg: float
    melhor_preco: Optional[OpcaoFrete] = None
    melhor_prazo: Optional[OpcaoFrete] = None
    todas_opcoes: list[OpcaoFrete] = []
    transportadoras_com_erro: list[str] = []
    tempo_total_ms: float
