"""Leitura das sessões reais do HCA G2 exportadas da SEMS+."""

import glob

import pandas as pd

# Pasta com os CSVs exportados da SEMS+, relativa à raiz do projeto
PASTA_DADOS = "data"


MOTIVO_PARA_STATUS = {
    "Charging stopped at full charge": "completed",
    "Abnormal disconnection of charging gun from vehicle.": "abnormal_disconnection",
    "Generation Loss": "interrupted_by_failure",
}


# Sessões com energia até este valor não são recargas de fato (carro plugado sem carregar)
ENERGIA_MINIMA_KWH = 0.5


def carregar_tabela_real(pasta=PASTA_DADOS):
    """Lê os CSVs da SEMS+ e junta a lista básica (Etapa A) com os detalhes (Etapa B)."""
    lista = pd.read_csv(f"{pasta}/etapa_a_sessoes_fase_morador.csv")

    arquivos_detalhe = sorted(glob.glob(f"{pasta}/etapaB_detalhe_*.csv"))
    detalhes = pd.concat([pd.read_csv(arquivo) for arquivo in arquivos_detalhe])

    tabela = lista.merge(detalhes, on="inicio")
    return tabela


def linha_para_sessao(linha, indice):
    """Converte uma linha da tabela real num dicionário no formato do SessionDTO."""
    total_kwh = linha["energia_total_kwh"]

    # Correção de extração: 35 sessões vieram com o green 10x maior (vírgula decimal lida errado)
    green_kwh = linha["green_kwh"]
    if green_kwh > 2 * total_kwh:
        green_kwh = green_kwh / 10

    return {
        "session_id": f"REAL-{indice:04d}",
        "charger_id": "HCA01",
        "card_id": linha["card_id"],
        "started_at": linha["inicio"],
        "ended_at": linha["fim"],
        "total_kwh": total_kwh,
        "green_kwh": green_kwh,
        "grid_kwh": linha["importada_kwh"],
        "average_power_kw": linha["potencia_media_kw"],
        "max_power_kw": linha["potencia_maxima_kw"],
        "status": MOTIVO_PARA_STATUS.get(linha["motivo_fim"], "interrupted_by_failure"),
    }


def carregar_sessoes_reais(pasta=PASTA_DADOS):
    """Devolve as sessões reais com recarga e, separadas, as sessões sem energia entregue."""
    tabela = carregar_tabela_real(pasta)

    sessoes = []
    sessoes_sem_energia = []
    for indice, linha in tabela.iterrows():
        dados = linha_para_sessao(linha, indice)
        if linha["energia_total_kwh"] > ENERGIA_MINIMA_KWH:
            sessoes.append(dados)
        else:
            sessoes_sem_energia.append(dados)

    return sessoes, sessoes_sem_energia


def separar_treino_validacao(sessoes, fracao_treino=0.8):
    """Separa as sessões em treino (mais antigas) e validação (mais recentes), por ordem cronológica."""
    ordenadas = sorted(sessoes, key=lambda s: s["started_at"])
    corte = int(len(ordenadas) * fracao_treino)
    return ordenadas[:corte], ordenadas[corte:]