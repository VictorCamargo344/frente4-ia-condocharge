"""Testes da Camada 2 (regras determinísticas)."""

from condocharge_ai import rules
from condocharge_ai.schemas import SessionDTO

from tests.test_schemas import dados_sessao_valida


def test_timestamp_valido_passa():
    """Uma sessão que termina depois de começar não deve violar a regra de timestamp."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_timestamp(sessao)
    assert resultado is None


def test_timestamp_invalido():
    """Uma sessão que termina antes de começar deve violar a regra de timestamp."""
    dados = dados_sessao_valida()
    dados["ended_at"] = "2026-09-22T18:00:00"

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_timestamp(sessao)
    assert resultado == "INVALID_TIMESTAMP"

def test_verificar_kwh_valido():
    """Uma sessão em que o kWh é positivo não viola a regra."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_kwh_negativo(sessao)
    assert resultado is None
    

def test_verificar_kwh_negativo():
    """Não é para existir kwh negativo."""
    dados = dados_sessao_valida()
    dados["grid_kwh"] = -900

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_kwh_negativo(sessao)
    assert resultado == "NEGATIVE_KWH"


