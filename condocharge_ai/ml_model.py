"""Camada 3: detecção de anomalias estatísticas com Isolation Forest e LOF."""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

from condocharge_ai.schemas import SessionDTO


NOMES_FEATURES = [
    "duracao_horas",
    "total_kwh",
    "average_power_kw",
    "max_power_kw",
    "fator_coerencia",
]

# Arquivo com o modelo treinado (gerado por training/train.py)
CAMINHO_MODELO = Path(__file__).parent / "artifacts" / "modelo_v1.joblib"

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


@lru_cache(maxsize=1)
def carregar_modelo():
    """Carrega o modelo treinado do disco uma única vez e reaproveita nas chamadas seguintes."""
    return joblib.load(CAMINHO_MODELO)


def avaliar_sessao(sessao: SessionDTO):
    """Aplica o Isolation Forest e o LOF a uma sessão e devolve o veredito da Camada 3."""
    modelo = carregar_modelo()

    features = np.array([extrair_features(sessao)])
    padronizadas = modelo["escalonador"].transform(features)

    suspeita_iforest = bool(modelo["iforest"].predict(padronizadas)[0])
    suspeita_lof = bool(modelo["lof"].predict(padronizadas)[0])

    # Score de 0 a 1: a opinião mais desconfiada entre os dois modelos
    score = max(
        modelo["iforest"].predict_proba(padronizadas)[0, 1],
        modelo["lof"].predict_proba(padronizadas)[0, 1],
    )

    motivos = []
    if suspeita_iforest:
        motivos.append("ISOLATION_FOREST_OUTLIER")
    if suspeita_lof:
        motivos.append("LOF_OUTLIER")

    return {
        "is_anomaly": suspeita_iforest or suspeita_lof,
        "score": round(float(score), 3),
        "reasons": motivos,
        "model_version": modelo["versao"],
    }