"""Treino do modelo de detecção de anomalias (Camada 3) com as sessões reais da SEMS+."""

import joblib
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from sklearn.preprocessing import StandardScaler

from condocharge_ai import ml_model
from condocharge_ai.schemas import SessionDTO
from condocharge_ai.training.dados_reais import carregar_sessoes_reais, separar_treino_validacao

# Fração do treino aceita como estranha: define a linha de corte dos modelos
CONTAMINACAO = 0.02
SEMENTE = 42
VERSAO_MODELO = "v1.0.0"


def montar_matriz(sessoes):
    """Converte uma lista de sessões (dicionários) na matriz de features do modelo."""
    linhas = [ml_model.extrair_features(SessionDTO.model_validate(dados)) for dados in sessoes]
    return np.array(linhas)


def treinar(sessoes_treino):
    """Treina o padronizador, o Isolation Forest e o LOF, e devolve tudo num único pacote."""
    matriz = montar_matriz(sessoes_treino)

    escalonador = StandardScaler().fit(matriz)
    matriz_padronizada = escalonador.transform(matriz)

    iforest = IForest(contamination=CONTAMINACAO, random_state=SEMENTE).fit(matriz_padronizada)
    lof = LOF(contamination=CONTAMINACAO).fit(matriz_padronizada)

    return {
        "versao": VERSAO_MODELO,
        "nomes_features": ml_model.NOMES_FEATURES,
        "escalonador": escalonador,
        "iforest": iforest,
        "lof": lof,
    }


def main():
    """Carrega as sessões reais, treina com a parte de treino e salva o modelo."""
    normais, _ = carregar_sessoes_reais()
    treino, _ = separar_treino_validacao(normais)

    modelo = treinar(treino)
    joblib.dump(modelo, ml_model.CAMINHO_MODELO)

    print(f"Modelo {VERSAO_MODELO} treinado com {len(treino)} sessões.")
    print(f"Salvo em: {ml_model.CAMINHO_MODELO}")


if __name__ == "__main__":
    main()