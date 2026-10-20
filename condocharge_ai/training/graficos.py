"""Gera os gráficos do README a partir das sessões de validação e das anomalias de avaliação.

Usa os mesmos conjuntos do avaliar.py. Os PNGs são salvos em docs/img/.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

from condocharge_ai.anomaly import check_session
from condocharge_ai.ml_model import carregar_modelo, extrair_features
from condocharge_ai.schemas import SessionDTO
from condocharge_ai.training.dados_reais import carregar_sessoes_reais, separar_treino_validacao
from condocharge_ai.training.dataset import criar_anomalias

PASTA_SAIDA = Path(__file__).resolve().parents[2] / "docs" / "img"

COR_NORMAL = "#2a78d6"
COR_ANOMALIA = "#eb6834"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_GRADE = "#e4e3df"


def sessoes_que_chegam_ao_ml(sessoes):
    """Mantém só as sessões aprovadas nas Camadas 1 e 2, que são as avaliadas pelo modelo."""
    return [s for s in sessoes if check_session(s)["layer"] in ("passed", "ml")]


def scores_combinados(sessoes):
    """Score devolvido pela check_session (maior predict_proba entre IForest e LOF)."""
    return np.array([check_session(s)["score"] for s in sessoes])


def scores_lof(sessoes):
    """Score bruto do LOF (decision_function) e o limiar de corte aprendido no treino."""
    modelo = carregar_modelo()
    matriz = np.array([extrair_features(SessionDTO.model_validate(s)) for s in sessoes])
    padronizadas = modelo["escalonador"].transform(matriz)
    return modelo["lof"].decision_function(padronizadas), modelo["lof"].threshold_


def estilizar_eixo(eixo):
    """Grade e bordas discretas, texto nas cores neutras."""
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        eixo.spines[lado].set_color(COR_GRADE)
    eixo.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    eixo.grid(axis="x", color=COR_GRADE, linewidth=0.8)
    eixo.set_axisbelow(True)


def grafico_dispersao(valores_normais, valores_anomalias, titulo, rotulo_x, caminho,
                      limiar=None, escala_log=False):
    """Pontos de cada grupo em uma faixa horizontal, com deslocamento vertical aleatório."""
    gerador = np.random.default_rng(0)
    figura, eixo = plt.subplots(figsize=(9, 3.2), dpi=110)

    grupos = [
        ("Sessões reais de validação", valores_normais, COR_NORMAL, 1),
        ("Anomalias de medição", valores_anomalias, COR_ANOMALIA, 0),
    ]
    for nome, valores, cor, posicao in grupos:
        deslocamento = gerador.uniform(-0.18, 0.18, len(valores))
        eixo.scatter(valores, posicao + deslocamento, s=36, color=cor,
                     edgecolor="white", linewidth=1.2, zorder=3)
        eixo.text(1.01, posicao, f"{nome}\n(n = {len(valores)})", transform=eixo.get_yaxis_transform(),
                  va="center", ha="left", fontsize=9, color=COR_TEXTO)

    if limiar is not None:
        eixo.axvline(limiar, color=COR_TEXTO_SECUNDARIO, linestyle="--", linewidth=1.2, zorder=2)
        eixo.text(limiar, 1.45, " limiar do LOF", fontsize=9, color=COR_TEXTO_SECUNDARIO, va="center")

    if escala_log:
        eixo.set_xscale("log")
        eixo.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda valor, _: f"{valor:g}"))
    eixo.set_ylim(-0.6, 1.6)
    eixo.set_yticks([])
    eixo.set_xlabel(rotulo_x, fontsize=9, color=COR_TEXTO_SECUNDARIO)
    eixo.set_title(titulo, loc="left", fontsize=11, color=COR_TEXTO)
    estilizar_eixo(eixo)
    eixo.spines["left"].set_visible(False)

    figura.tight_layout()
    figura.subplots_adjust(right=0.76)
    figura.savefig(caminho, facecolor="white")
    plt.close(figura)


def main():
    """Monta os dois conjuntos, calcula os scores e salva os gráficos."""
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    normais, _ = carregar_sessoes_reais()
    _, validacao = separar_treino_validacao(normais)
    anomalias = criar_anomalias(validacao)

    validacao_ml = sessoes_que_chegam_ao_ml(validacao)
    anomalias_ml = sessoes_que_chegam_ao_ml(anomalias)

    grafico_dispersao(
        scores_combinados(validacao_ml),
        scores_combinados(anomalias_ml),
        "Score da Camada 3 por sessão",
        "score (escala relativa ao treino; não é probabilidade)",
        PASTA_SAIDA / "score_camada3.png",
    )

    lof_normais, limiar = scores_lof(validacao_ml)
    lof_anomalias, _ = scores_lof(anomalias_ml)
    grafico_dispersao(
        lof_normais,
        lof_anomalias,
        "Score bruto do LOF e limiar de decisão",
        "decision_function do LOF (escala log)",
        PASTA_SAIDA / "lof_limiar.png",
        limiar=limiar,
        escala_log=True,
    )

    print(f"Gráficos salvos em {PASTA_SAIDA}")


if __name__ == "__main__":
    main()
