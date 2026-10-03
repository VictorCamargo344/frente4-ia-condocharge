"""Geração de sessões sintéticas calibradas com as sessões reais do HCA G2 (SEMS+)."""

from datetime import datetime, timedelta

import numpy as np

# Energia por sessão (kWh): 215 sessões reais da SEMS+ (out/2025 a out/2026)
ENERGIA_MEDIA_KWH = 8.0
ENERGIA_DESVIO_KWH = 3.4

# Potência média (kW): cresce com a energia da sessão (correlação 0,39 nas sessões reais)
POTENCIA_BASE_KW = 1.86
POTENCIA_POR_KWH = 0.05
POTENCIA_DESVIO_KW = 0.40

# Fração do tempo da sessão em que o carro efetivamente carrega
FRACAO_TEMPO_CARREGANDO = 0.9

# Potência máxima (kW): teto de operação do carregador do lab
POTENCIA_MAXIMA_MIN_KW = 3.3
POTENCIA_MAXIMA_MAX_KW = 3.5

# Horário de início: dois grupos observados nas sessões reais
PROPORCAO_SESSOES_NOITE = 0.88
HORA_NOITE_MEDIA = 20.8
HORA_NOITE_DESVIO = 1.3
HORA_DIA_MEDIA = 14.0
HORA_DIA_DESVIO = 3.0


def gerar_sessao_normal(rng, indice):
    """Gera uma sessão de recarga normal, no formato do SessionDTO."""
    energia_kwh = max(rng.normal(ENERGIA_MEDIA_KWH, ENERGIA_DESVIO_KWH), 1.0)
    if rng.uniform(0.0, 1.0) < PROPORCAO_SESSOES_NOITE:
        hora_sorteada = rng.normal(HORA_NOITE_MEDIA, HORA_NOITE_DESVIO)
    else:
        hora_sorteada = rng.normal(HORA_DIA_MEDIA, HORA_DIA_DESVIO)
    hora_inicio = min(max(hora_sorteada, 0.0), 23.5)
    potencia_sorteada = POTENCIA_BASE_KW + POTENCIA_POR_KWH * energia_kwh + rng.normal(0.0, POTENCIA_DESVIO_KW)
    potencia_media_kw = min(max(potencia_sorteada, 1.0), 3.3)

    data_base = datetime(2026, 9, 1)
    dia = int(rng.integers(0, 30))
    inicio = data_base + timedelta(days=dia, hours=hora_inicio)
    duracao_horas = energia_kwh / potencia_media_kw / FRACAO_TEMPO_CARREGANDO
    fim = inicio + timedelta(hours=duracao_horas)

    potencia_maxima_kw = rng.uniform(POTENCIA_MAXIMA_MIN_KW, POTENCIA_MAXIMA_MAX_KW)
    fracao_green = rng.uniform(0.0, 1.0)
    green_kwh = energia_kwh * fracao_green
    grid_kwh = energia_kwh - green_kwh

    return {
        "session_id": f"SIM-{indice:04d}",
        "charger_id": "HCA01",
        "card_id": "SIM-CARD",
        "started_at": inicio,
        "ended_at": fim,
        "total_kwh": round(energia_kwh, 2),
        "green_kwh": round(green_kwh, 2),
        "grid_kwh": round(grid_kwh, 2),
        "average_power_kw": round(potencia_media_kw, 2),
        "max_power_kw": round(potencia_maxima_kw, 2),
        "status": "completed",
    }


def gerar_sessoes_normais(quantidade, semente=42):
    """Gera múltiplas sessões de recarga normal, no formato do SessionDTO."""
    rng = np.random.default_rng(semente)
    sessoes = []
    for i in range(quantidade):
        sessoes.append(gerar_sessao_normal(rng, i))
    return sessoes
