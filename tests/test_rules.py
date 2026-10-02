"""Testes da Camada 2 (regras determinísticas de plausibilidade física)."""

from condocharge_ai import rules
from condocharge_ai.schemas import SessionDTO

from tests.test_schemas import dados_sessao_valida


def test_timestamp_valido_passa():
    """Uma sessão que termina depois de começar não deve violar a regra INVALID_TIMESTAMP."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_timestamp(sessao)
    assert resultado is None


def test_timestamp_invalido():
    """Uma sessão que termina antes de começar deve violar a regra INVALID_TIMESTAMP."""
    dados = dados_sessao_valida()
    dados["ended_at"] = "2026-09-22T18:00:00"

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_timestamp(sessao)
    assert resultado == "INVALID_TIMESTAMP"


def test_verificar_kwh_valido():
    """Uma sessão com todas as energias positivas não deve violar a regra NEGATIVE_KWH."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_kwh_negativo(sessao)
    assert resultado is None


def test_verificar_kwh_negativo():
    """Uma sessão com alguma energia negativa (aqui, grid_kwh) deve violar a regra NEGATIVE_KWH."""
    dados = dados_sessao_valida()
    dados["grid_kwh"] = -900

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_kwh_negativo(sessao)
    assert resultado == "NEGATIVE_KWH"


def test_verificar_duracao_normal():
    """Uma sessão com duração acima de 1 minuto não deve violar a regra DURATION_TOO_SHORT."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_duracao_curta(sessao)
    assert resultado is None


def test_verificar_duracao_curta():
    """Uma sessão com menos de 1 minuto e energia registrada deve violar a regra DURATION_TOO_SHORT."""
    dados = dados_sessao_valida()
    dados["ended_at"] = "2026-09-22T19:00:30"

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_duracao_curta(sessao)
    assert resultado == "DURATION_TOO_SHORT"

