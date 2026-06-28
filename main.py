from fastapi import FastAPI
from routers.cotacao import router as cotacao_router

app = FastAPI(
    title="Hub de Frete",
    description="Microsserviço de cotação de frete — consulta 3 transportadoras em paralelo e retorna a melhor opção.",
    version="1.0.0",
)

app.include_router(cotacao_router, tags=["Cotação"])


@app.get("/health", tags=["Infra"], summary="Health check")
async def health() -> dict:
    return {"status": "ok", "service": "hub-de-frete"}
