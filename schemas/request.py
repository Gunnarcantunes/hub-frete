from pydantic import BaseModel, Field, field_validator


class CotacaoRequest(BaseModel):
    cep_origem: str = Field(..., examples=["01310100"], description="CEP de origem (8 dígitos)")
    cep_destino: str = Field(..., examples=["20040020"], description="CEP de destino (8 dígitos)")
    peso_kg: float = Field(..., gt=0, le=500, examples=[2.5], description="Peso da encomenda em kg")
    altura_cm: float = Field(..., gt=0, le=200, examples=[15.0], description="Altura em cm")
    largura_cm: float = Field(..., gt=0, le=200, examples=[20.0], description="Largura em cm")
    comprimento_cm: float = Field(..., gt=0, le=200, examples=[30.0], description="Comprimento em cm")
    valor_declarado: float = Field(..., ge=0, examples=[150.00], description="Valor declarado da mercadoria em R$")

    @field_validator("cep_origem", "cep_destino")
    @classmethod
    def validar_cep(cls, v: str) -> str:
        digits = v.replace("-", "").replace(".", "").strip()
        if not digits.isdigit() or len(digits) != 8:
            raise ValueError("CEP deve conter exatamente 8 dígitos numéricos")
        return digits

    @property
    def volume_cm3(self) -> float:
        return self.altura_cm * self.largura_cm * self.comprimento_cm

    @property
    def peso_cubado_kg(self) -> float:
        """Peso cubado usando fator padrão de 6000 cm³/kg."""
        return self.volume_cm3 / 6000.0
