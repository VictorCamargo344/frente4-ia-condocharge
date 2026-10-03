"""Geração de sessões sintéticas calibradas com as sessões reais do HCA G2 (SEMS+)."""

import numpy as np
from datetime import datetime, timedelta

# Energia por sessão (kWh), calibrada com as sessões reais da SEMS+
ENERGIA_MEDIA_KWH = 8.7
ENERGIA_DESVIO_KWH = 3.7

# Potência média estável do carregador do lab, calibrada com as sessões reais da SEMS+
POTENCIA_MEDIA_KW = 3.0
POTENCIA_DESVIO_KW = 0.25

# ~2/3 das sessões reais começam entre 17h e 22h
HORA_INICIO_MEDIA = 20.0
HORA_INICIO_DESVIO = 2.5


def gerar_sessao_normal(rng, indice):
    """Gera uma sessão de recarga normal, no formato do SessionDTO."""
    energia_kwh = max(rng.normal(ENERGIA_MEDIA_KWH, ENERGIA_DESVIO_KWH), 1.0)
    hora_inicio = min(max(rng.normal(HORA_INICIO_MEDIA, HORA_INICIO_DESVIO), 0.0), 23.5)
    potencia_media_kw = max(rng.normal(POTENCIA_MEDIA_KW, POTENCIA_DESVIO_KW), 1.5)

    data_base = datetime(2026, 9, 1)
    dia = int(rng.integers(0, 30))
    inicio = data_base + timedelta(days=dia, hours=hora_inicio)
    duracao_horas = energia_kwh / potencia_media_kw
    fim = inicio + timedelta(hours=duracao_horas)

    potencia_maxima_kw = potencia_media_kw * rng.uniform(1.05, 1.15)
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