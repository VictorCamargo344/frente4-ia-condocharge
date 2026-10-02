"""Regras determinísticas da Camada 2: plausibilidade física das sessões"""

from condocharge_ai.schemas import SessionDTO

POTENCIA_NOMINAL_KW = {
    "HCA01": 7.0,
}

def verificar_timestamp(sessao: SessionDTO):
    if sessao.ended_at <= sessao.started_at:
        return "INVALID_TIMESTAMP"
    return None