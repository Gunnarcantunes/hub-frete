"""
Transportadora A — simula integração com API REST JSON.
Especialidade: cargas expressas, regiões Sul/Sudeste.
"""
import asyncio
import random
from schemas.request import CotacaoRequest
from schemas.response import OpcaoFrete

NOME = "TransportadoraA"

# Tabela interna de multiplicadores por distância de CEP
_FAIXAS = [
    (20, 1.0, 2),
    (40, 1.3, 3),
    (60, 1.6, 4),
    (80, 2.0, 5),
    (100, 2.5, 6),
]


def _calcular_distancia_cep(cep_a: str, cep_b: str) -> int:
    """Estimativa grosseira de distância pelo prefixo do CEP."""
    return abs(int(cep_a[:2]) - int(cep_b[:2]))


async def cotar(req: CotacaoRequest) -> OpcaoFrete:
    await asyncio.sleep(random.uniform(0.3, 0.8))

    peso_efetivo = max(req.peso_kg, req.peso_cubado_kg)
    distancia = _calcular_distancia_cep(req.cep_origem, req.cep_destino)

    multiplicador, prazo = 2.5, 6
    for limite, mult, dias in _FAIXAS:
        if distancia <= limite:
            multiplicador, prazo = mult, dias
            break

    preco_base = 12.00 + (peso_efetivo * 3.20 * multiplicador)

    # Seguro automático: 0.3% do valor declarado
    seguro = req.valor_declarado * 0.003
    preco_final = round(preco_base + seguro, 2)

    return OpcaoFrete(
        transportadora=NOME,
        servico="Expresso",
        preco=preco_final,
        prazo_dias=prazo,
        peso_considerado_kg=round(peso_efetivo, 3),
        observacao="Inclui seguro automático de 0,3%",
    )
