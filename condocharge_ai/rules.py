"""Regras determinísticas da Camada 2: plausibilidade física das sessões."""

from condocharge_ai.schemas import SessionDTO

# Potência nominal (kW) de cada carregador cadastrado no condomínio.
POTENCIA_NOMINAL_KW = {
    "HCA01": 7.0,
}

# Duração mínima (s) para uma sessão com energia registrada ser plausível.
DURACAO_MINIMA_SEGUNDOS = 60

# Margem para variações normais de medição (5%).
TOLERANCIA_POTENCIA = 0.05
TOLERANCIA_ATRIBUICAO = 0.05


# Piso da tolerância (kWh): a SEMS mostra o green com uma casa decimal
TOLERANCIA_ATRIBUICAO_MIN_KWH = 0.1


def verificar_timestamp(sessao: SessionDTO):
    """Detecta sessão que termina antes ou no mesmo instante em que começou."""
    if sessao.ended_at <= sessao.started_at:
        return "INVALID_TIMESTAMP"
    return None


def verificar_kwh_negativo(sessao: SessionDTO):
    """Detecta qualquer energia (total, solar ou rede) negativa."""
    if sessao.total_kwh < 0 or sessao.grid_kwh < 0 or sessao.green_kwh < 0:
        return "NEGATIVE_KWH"
    return None


def verificar_duracao_curta(sessao: SessionDTO):
    """Detecta sessão com menos de 1 minuto que mesmo assim registrou energia."""
    duracao = (sessao.ended_at - sessao.started_at).total_seconds()
    if duracao < DURACAO_MINIMA_SEGUNDOS and sessao.total_kwh > 0:
        return "DURATION_TOO_SHORT"
    return None


def verificar_carregador_conhecido(sessao: SessionDTO):
    """Detecta sessão de um carregador que não está cadastrado."""
    if sessao.charger_id not in POTENCIA_NOMINAL_KW:
        return "UNKNOWN_CHARGER"
    return None


def verificar_potencia(sessao: SessionDTO):
    """Detecta potência máxima acima da nominal do carregador (com tolerância)."""
    if sessao.charger_id not in POTENCIA_NOMINAL_KW:
        return None  # caso já tratado pela regra UNKNOWN_CHARGER

    nominal = POTENCIA_NOMINAL_KW[sessao.charger_id]
    limite = nominal * (1 + TOLERANCIA_POTENCIA)

    if sessao.max_power_kw > limite:
        return "POWER_EXCEEDS_NOMINAL"
    return None


def verificar_capacidade(sessao: SessionDTO):
    """Detecta energia acima do máximo que o carregador entrega no tempo da sessão."""
    if sessao.charger_id not in POTENCIA_NOMINAL_KW:
        return None  # caso já tratado pela regra UNKNOWN_CHARGER

    duracao_horas = (sessao.ended_at - sessao.started_at).total_seconds() / 3600
    if duracao_horas <= 0:
        return None  # caso já tratado pela regra INVALID_TIMESTAMP

    nominal = POTENCIA_NOMINAL_KW[sessao.charger_id]
    capacidade_kwh = nominal * duracao_horas * (1 + TOLERANCIA_POTENCIA)

    if sessao.total_kwh > capacidade_kwh:
        return "KWH_EXCEEDS_CAPACITY"
    return None


def verificar_atribuicao_energia(sessao: SessionDTO):
    """Detecta quando solar (green) + rede (grid) não explica o total consumido."""
    soma_origens = sessao.green_kwh + sessao.grid_kwh
    diferenca = abs(soma_origens - sessao.total_kwh)

    tolerancia = max(sessao.total_kwh * TOLERANCIA_ATRIBUICAO, TOLERANCIA_ATRIBUICAO_MIN_KWH)
    if diferenca > tolerancia:
        return "ENERGY_SOURCE_ATTRIBUTION_MISMATCH"
    return None


# Ordem em que as regras são aplicadas. Para criar uma regra nova, basta escrever a função acima e acrescentá-la nesta lista.
REGRAS = [
    verificar_timestamp,
    verificar_kwh_negativo,
    verificar_duracao_curta,
    verificar_carregador_conhecido,
    verificar_potencia,
    verificar_capacidade,
    verificar_atribuicao_energia,
]


def verificar_regras(sessao: SessionDTO):
    """Aplica todas as regras e devolve a lista de códigos violados (vazia se a sessão é plausível)."""
    violacoes = []
    for regra in REGRAS:
        codigo = regra(sessao)
        if codigo is not None:
            violacoes.append(codigo)
    return violacoes