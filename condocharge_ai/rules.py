"""Regras determinísticas da Camada 2: plausibilidade física das sessões"""

from condocharge_ai.schemas import SessionDTO

POTENCIA_NOMINAL_KW = {
    "HCA01": 7.0,
}

DURACAO_MINIMA_SEGUNDOS = 60


def verificar_timestamp(sessao: SessionDTO):
    """Detecta sessão que termina antes ou no mesmo instante em que começou."""
    if sessao.ended_at <= sessao.started_at:
        return "INVALID_TIMESTAMP"
    return None


def verificar_kwh_negativo(sessao: SessionDTO):
    """Detecta sessão a sessão teve kwh em algum momento."""
    if sessao.total_kwh < 0 or sessao.grid_kwh < 0 or sessao.green_kwh < 0:
        return "NEGATIVE_KWH"
    return None


def verificar_duracao_curta(sessao: SessionDTO):
    """Detecta sessão a sessão teve uma duração muito curta."""
    duracao = (sessao.ended_at - sessao.started_at).total_seconds()
    if duracao < DURACAO_MINIMA_SEGUNDOS and sessao.total_kwh > 0:
        return "DURATION_TOO_SHORT"
    return None


def verificar_carregador_conhecido(sessao: SessionDTO):
    """Detecta se o carregador utilizado na sessão é conhecido"""
    if sessao.charger_id not in POTENCIA_NOMINAL_KW:
        return "UNKNOWN_CHARGER"
    return None

