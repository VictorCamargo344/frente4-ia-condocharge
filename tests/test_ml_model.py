"""Testes da Camada 3 (modelo de detecção de anomalias)."""

import pytest

from condocharge_ai import ml_model
from condocharge_ai.schemas import SessionDTO

from tests.test_schemas import dados_sessao_valida


def test_features_extraidas_na_ordem_esperada():
    """A sessão padrão (19h00 às 21h10) deve virar o vetor de features esperado."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    features = ml_model.extrair_features(sessao)

    assert len(features) == len(ml_model.NOMES_FEATURES)
    assert features[0] == pytest.approx(2.1667, abs=0.001)
    assert features[1] == 14.8
    assert features[2] == 6.8
    assert features[3] == 7.1
    assert features[4] == 19.0



