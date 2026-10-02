"""Regras determinísticas da Camada 2: plausibilidade física das sessões"""

from condocharge_ai.schemas import SessionDTO

POTENCIA_NOMINAL_KW = {
    "HCA01": 7.0,
}

def verificar_timestamp(sessao: SessionDTO):
    if sessao.ended_at <= sessao.started_at:
        return "INVALID_TIMESTAMP"
    return None


def verificar_kwh_negativo(sessao: SessionDTO):
    if sessao.total_kwh < 0 or sessao.grid_kwh < 0 or sessao.green_kwh < 0:
        return "NEGATIVE_KWH"
    return None