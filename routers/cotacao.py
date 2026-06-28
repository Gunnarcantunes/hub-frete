import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter
from schemas.request import CotacaoRequest
from schemas.response import OpcaoFrete, ResultadoCotacao
from services import transportadora_a, transportadora_b, transportadora_c

router = APIRouter()

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "cotacoes.json"


async def _cotar_seguro(nome: str, coro) -> tuple[OpcaoFrete | None, str | None]:
    """Executa cotação capturando exceções para não derrubar as demais."""
    try:
        resultado = await coro
        return resultado, None
    except Exception as exc:
        return None, f"{nome}: {exc}"


def _registrar(req: CotacaoRequest, resultado: ResultadoCotacao) -> None:
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": req.model_dump(),
        "melhor_preco": resultado.melhor_preco.model_dump() if resultado.melhor_preco else None,
        "melhor_prazo": resultado.melhor_prazo.model_dump() if resultado.melhor_prazo else None,
        "todas_opcoes": [o.model_dump() for o in resultado.todas_opcoes],
        "erros": resultado.transportadoras_com_erro,
        "tempo_ms": resultado.tempo_total_ms,
    }

    registros: list[dict] = []
    if _LOG_FILE.exists():
        try:
            registros = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            registros = []

    registros.append(registro)
    _LOG_FILE.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")


@router.post("/cotar", response_model=ResultadoCotacao, summary="Cotar frete em 3 transportadoras")
async def cotar_frete(req: CotacaoRequest) -> ResultadoCotacao:
    inicio = time.perf_counter()

    resultados = await asyncio.gather(
        _cotar_seguro("TransportadoraA", transportadora_a.cotar(req)),
        _cotar_seguro("TransportadoraB", transportadora_b.cotar(req)),
        _cotar_seguro("TransportadoraC", transportadora_c.cotar(req)),
    )

    opcoes: list[OpcaoFrete] = []
    erros: list[str] = []

    for opcao, erro in resultados:
        if opcao is not None:
            opcoes.append(opcao)
        if erro is not None:
            erros.append(erro)

    melhor_preco = min(opcoes, key=lambda o: o.preco) if opcoes else None
    melhor_prazo = min(opcoes, key=lambda o: o.prazo_dias) if opcoes else None

    tempo_ms = round((time.perf_counter() - inicio) * 1000, 2)

    resultado = ResultadoCotacao(
        cep_origem=req.cep_origem,
        cep_destino=req.cep_destino,
        peso_kg=req.peso_kg,
        melhor_preco=melhor_preco,
        melhor_prazo=melhor_prazo,
        todas_opcoes=sorted(opcoes, key=lambda o: o.preco),
        transportadoras_com_erro=erros,
        tempo_total_ms=tempo_ms,
    )

    _registrar(req, resultado)
    return resultado
