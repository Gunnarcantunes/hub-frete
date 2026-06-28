"""
Transportadora C — lê tabela de preços de arquivo CSV local.
Especialidade: frete fracionado com tabela regional fechada.
"""
import asyncio
import csv
import random
from pathlib import Path
from schemas.request import CotacaoRequest
from schemas.response import OpcaoFrete

NOME = "TransportadoraC"
_CSV_PATH = Path(__file__).parent.parent / "tabelas" / "transportadora_c.csv"


def _carregar_tabela() -> list[dict]:
    with open(_CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _buscar_linha(tabela: list[dict], req: CotacaoRequest) -> dict | None:
    """
    Busca a linha mais específica da tabela para o par de CEPs e peso.
    Tenta prefixo de 2 dígitos, cai para a linha fallback '00'/'00' se não encontrar.
    """
    origem_pref = req.cep_origem[:2]
    destino_pref = req.cep_destino[:2]
    peso = req.peso_kg

    candidatas = [
        row for row in tabela
        if row["cep_origem_prefixo"] == origem_pref
        and row["cep_destino_prefixo"] == destino_pref
        and float(row["peso_max_kg"]) >= peso
    ]

    if not candidatas:
        # fallback: linha genérica
        candidatas = [
            row for row in tabela
            if row["cep_origem_prefixo"] == "00"
            and row["cep_destino_prefixo"] == "00"
            and float(row["peso_max_kg"]) >= peso
        ]

    if not candidatas:
        return None

    # Menor faixa de peso_max que ainda cobre o peso solicitado
    return min(candidatas, key=lambda r: float(r["peso_max_kg"]))


async def cotar(req: CotacaoRequest) -> OpcaoFrete:
    await asyncio.sleep(random.uniform(0.3, 0.8))

    tabela = _carregar_tabela()
    linha = _buscar_linha(tabela, req)

    if linha is None:
        raise ValueError(f"Rota {req.cep_origem[:2]} → {req.cep_destino[:2]} não atendida pela {NOME}")

    peso_efetivo = max(req.peso_kg, req.peso_cubado_kg)
    preco = float(linha["preco_base"]) + (peso_efetivo * float(linha["preco_por_kg"]))
    preco = round(preco, 2)
    prazo = int(linha["prazo_dias"])

    return OpcaoFrete(
        transportadora=NOME,
        servico="Fracionado",
        preco=preco,
        prazo_dias=prazo,
        peso_considerado_kg=round(peso_efetivo, 3),
        observacao="Tabela regional — fracionado",
    )
