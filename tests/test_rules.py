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


def test_carregador_conhecido_passa():
    """Uma sessão com carregador cadastrado não deve violar a regra UNKNOWN_CHARGER."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_carregador_conhecido(sessao)
    assert resultado is None


def test_carregador_desconhecido_e_detectado():
    """Uma sessão com carregador não cadastrado deve violar a regra UNKNOWN_CHARGER."""
    dados = dados_sessao_valida()
    dados["charger_id"] = "HCA99"

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_carregador_conhecido(sessao)
    assert resultado == "UNKNOWN_CHARGER"


def test_potencia_dentro_do_nominal_passa():
    """Uma sessão com potência dentro da margem do nominal não deve violar a regra POWER_EXCEEDS_NOMINAL."""
    dados = dados_sessao_valida()  # max_power_kw=7.1, dentro da tolerância de 7.35
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_potencia(sessao)
    assert resultado is None


def test_potencia_acima_do_nominal_e_detectada():
    """Uma sessão com potência acima do nominal do carregador deve violar a regra POWER_EXCEEDS_NOMINAL."""
    dados = dados_sessao_valida()
    dados["max_power_kw"] = 15.0

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_potencia(sessao)
    assert resultado == "POWER_EXCEEDS_NOMINAL"


def test_energia_dentro_da_capacidade_passa():
    """Uma sessão com energia compatível com potência e duração não deve violar a regra KWH_EXCEEDS_CAPACITY."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_capacidade(sessao)
    assert resultado is None


def test_energia_acima_da_capacidade_e_detectada():
    """Uma sessão com mais energia do que o carregador consegue entregar no período deve violar a regra KWH_EXCEEDS_CAPACITY."""
    dados = dados_sessao_valida()
    dados["total_kwh"] = 50.0  # máximo físico em 2h10 a 7 kW é ~15,9 kWh

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_capacidade(sessao)
    assert resultado == "KWH_EXCEEDS_CAPACITY"


def test_atribuicao_de_energia_coerente_passa():
    """Uma sessão em que solar + rede explica o total não deve violar a regra ENERGY_SOURCE_ATTRIBUTION_MISMATCH."""
    dados = dados_sessao_valida()  # 4.2 + 10.6 = 14.8
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_atribuicao_energia(sessao)
    assert resultado is None


def test_atribuicao_de_energia_incoerente_e_detectada():
    """Uma sessão com origens zeradas e total positivo (padrão observado na SEMS+) deve violar a regra ENERGY_SOURCE_ATTRIBUTION_MISMATCH."""
    dados = dados_sessao_valida()
    dados["green_kwh"] = 0.0
    dados["grid_kwh"] = 0.0

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_atribuicao_energia(sessao)
    assert resultado == "ENERGY_SOURCE_ATTRIBUTION_MISMATCH"


def test_sessao_plausivel_nao_viola_nenhuma_regra():
    """Uma sessão plausível deve passar por todas as regras sem violações."""
    dados = dados_sessao_valida()
    sessao = SessionDTO.model_validate(dados)
    resultado = rules.verificar_regras(sessao)
    assert resultado == []


def test_sessao_com_varios_problemas_retorna_todas_as_violacoes():
    """Uma sessão com mais de um problema deve ter todas as violações listadas."""
    dados = dados_sessao_valida()
    dados["grid_kwh"] = -900
    dados["max_power_kw"] = 15.0

    sessao = SessionDTO.model_validate(dados)

    resultado = rules.verificar_regras(sessao)
    assert "NEGATIVE_KWH" in resultado
    assert "POWER_EXCEEDS_NOMINAL" in resultado