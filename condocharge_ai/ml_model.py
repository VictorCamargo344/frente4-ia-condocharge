"""Camada 3: detecção de anomalias estatísticas com Isolation Forest e LOF."""

from condocharge_ai.schemas import SessionDTO


NOMES_FEATURES = [
    "duracao_horas", 
    "total_kwh", 
    "average_power_kw", 
    "max_power_kw", 
    "hora_inicio",
]


def extrair_features(sessao: SessionDTO):
    """Transforma uma sessão no vetor numérico usado pelo modelo."""
    duracao_horas = (sessao.ended_at - sessao.started_at).total_seconds() / 3600
    hora_inicio = sessao.started_at.hour + (sessao.started_at.minute / 60)
    return [
        duracao_horas,
        sessao.total_kwh,
        sessao.average_power_kw,
        sessao.max_power_kw,
        hora_inicio,
    ]

