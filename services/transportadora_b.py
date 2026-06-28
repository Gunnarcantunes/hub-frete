"""
Transportadora B — simula integração com API que retorna XML (SOAP/legacy).
Especialidade: cargas econômicas, cobertura nacional completa.
"""
import asyncio
import random
import xml.etree.ElementTree as ET
from schemas.request import CotacaoRequest
from schemas.response import OpcaoFrete

NOME = "TransportadoraB"


def _montar_xml_request(req: CotacaoRequest) -> str:
    """Constrói o XML que seria enviado à transportadora real."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CotacaoRequest>
  <CepOrigem>{req.cep_origem}</CepOrigem>
  <CepDestino>{req.cep_destino}</CepDestino>
  <PesoKg>{req.peso_kg}</PesoKg>
  <Dimensoes>
    <Altura>{req.altura_cm}</Altura>
    <Largura>{req.largura_cm}</Largura>
    <Comprimento>{req.comprimento_cm}</Comprimento>
  </Dimensoes>
  <ValorDeclarado>{req.valor_declarado}</ValorDeclarado>
</CotacaoRequest>"""


def _parsear_xml_response(xml_str: str) -> dict:
    """Parseia o XML que a transportadora retornaria."""
    root = ET.fromstring(xml_str)
    return {
        "preco": float(root.findtext("Preco", "0")),
        "prazo": int(root.findtext("PrazoDias", "0")),
        "servico": root.findtext("Servico", "Econômico"),
        "peso_cobrado": float(root.findtext("PesoCobrado", "0")),
    }


def _gerar_xml_resposta_simulada(req: CotacaoRequest) -> str:
    """Simula a resposta XML que viria da transportadora."""
    peso_efetivo = max(req.peso_kg, req.peso_cubado_kg)
    distancia = abs(int(req.cep_origem[:2]) - int(req.cep_destino[:2]))

    preco = 8.50 + (peso_efetivo * 2.10) + (distancia * 0.35)
    prazo = max(2, min(15, 2 + distancia // 8))
    preco = round(preco, 2)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CotacaoResponse>
  <Preco>{preco}</Preco>
  <PrazoDias>{prazo}</PrazoDias>
  <Servico>Econômico</Servico>
  <PesoCobrado>{round(peso_efetivo, 3)}</PesoCobrado>
</CotacaoResponse>"""


async def cotar(req: CotacaoRequest) -> OpcaoFrete:
    await asyncio.sleep(random.uniform(0.3, 0.8))

    # Simula o ciclo request/response XML
    _xml_req = _montar_xml_request(req)
    xml_resp = _gerar_xml_resposta_simulada(req)
    dados = _parsear_xml_response(xml_resp)

    return OpcaoFrete(
        transportadora=NOME,
        servico=dados["servico"],
        preco=dados["preco"],
        prazo_dias=dados["prazo"],
        peso_considerado_kg=dados["peso_cobrado"],
        observacao="Tarifa econômica, cobertura nacional",
    )
