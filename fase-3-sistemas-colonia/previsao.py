"""
PREVISÃO: regressão linear simples (y = a*x + b) pelo método dos mínimos
quadrados, implementada sem bibliotecas externas.
"""


def ajustar_reta(x, y):
    """
    Ajusta a reta y = a*x + b aos dados.
      a = inclinação (quanto y muda a cada +1 em x)
      b = intercepto (valor de y quando x = 0)
    Retorna (a, b).
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("x e y precisam ter o mesmo tamanho (mínimo 2).")

    n = len(x)
    media_x = sum(x) / n
    media_y = sum(y) / n

    numerador = sum((xi - media_x) * (yi - media_y) for xi, yi in zip(x, y))
    denominador = sum((xi - media_x) ** 2 for xi in x)

    if denominador == 0:
        raise ValueError("Todos os valores de x são iguais.")

    a = numerador / denominador
    b = media_y - a * media_x
    return a, b


def prever(a, b, valor):
    """Usa a reta ajustada para estimar um valor novo."""
    return a * valor + b


def calcular_r2(x, y, a, b):
    """
    Coeficiente de determinação R² (0 a 1): mostra o quanto a reta
    explica os dados. Perto de 1 = previsão confiável.
    """
    media_y = sum(y) / len(y)
    ss_total = sum((yi - media_y) ** 2 for yi in y)
    ss_residuo = sum((yi - prever(a, b, xi)) ** 2 for xi, yi in zip(x, y))
    if ss_total == 0:
        return 1.0
    return 1 - ss_residuo / ss_total


def prever_comportamento(historico, chave, valor_x):
    """
    Ajusta a reta com o histórico de `chave` e prevê y para `valor_x`.
    Retorna um dicionário com a reta (a, b), a qualidade (r2) e a previsão.
    """
    dados = historico[chave]
    a, b = ajustar_reta(dados["x"], dados["y"])
    return {
        "a": a,
        "b": b,
        "r2": calcular_r2(dados["x"], dados["y"], a, b),
        "previsao": prever(a, b, valor_x),
    }
