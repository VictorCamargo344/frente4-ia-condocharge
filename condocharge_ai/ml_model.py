"""Camada 3: detecção de anomalias estatísticas com Isolation Forest e LOF."""

from condocharge_ai.schemas import SessionDTO


NOMES_FEATURES = [
    "duracao_horas",
    "total_kwh",
    "average_power_kw",
    "max_power_kw",
    "fator_coerencia",
]

def extrair_features(sessao: SessionDTO):
    """Transforma uma sessão no vetor numérico usado pelo modelo."""
    duracao_horas = (sessao.ended_at - sessao.started_at).total_seconds() / 3600

    # Energia ÷ (potência × duração): ~0,90 em sessões reais; foge disso se a medição é incoerente
    denominador = sessao.average_power_kw * duracao_horas
    if denominador > 0:
        fator_coerencia = sessao.total_kwh / denominador
    else:
        fator_coerencia = 0.0

    return [
        duracao_horas,
        sessao.total_kwh,
        sessao.average_power_kw,
        sessao.max_power_kw,
        fator_coerencia,
    ]