"""
DECISÕES: regras que transformam dados em uma ação clara.
"""
from estrutura import consumidores_por_prioridade

CONSUMO_ALTO = 60      # consumo (%) acima disso é considerado alto
ENERGIA_BAIXA = 50     # energia (%) abaixo disso exige ação
ENERGIA_CRITICA = 20   # energia (%) abaixo disso: só suporte à vida


def decidir_acao(energia, consumo):
    """
    Transforma energia (%) e consumo (%) em uma decisão clara.

    Regras em ordem de prioridade (a primeira verdadeira vence):
      1. energia < 20                 -> CRÍTICO: manter só o suporte à vida
      2. energia < 50 E consumo alto  -> ativar modo economia
      3. energia < 50                 -> reduzir consumo
      4. consumo alto                 -> atenção ao consumo
      5. caso contrário               -> operação normal
    """
    # Prioridade 1: o suporte à vida nunca é desligado
    if energia < ENERGIA_CRITICA:
        return ("CRÍTICO: manter apenas suporte à vida, "
                "desligar sistemas não essenciais")

    # Prioridade 2: condição combinada (E)
    if energia < ENERGIA_BAIXA and consumo > CONSUMO_ALTO:
        return "ALERTA: ativar modo economia"

    # Prioridade 3: regra básica
    if energia < ENERGIA_BAIXA:
        return "ALERTA: reduzir consumo"

    # Prioridade 4
    if consumo > CONSUMO_ALTO:
        return "ATENÇÃO: consumo alto, monitorar"

    return "OK: operação normal"


def sistemas_a_manter(colonia, energia):
    """
    Percorre os consumidores da hierarquia, do mais importante para o
    menos importante, e devolve os que continuam ligados com esse nível
    de energia (%). O suporte à vida (energia_minima = 0) nunca sai.
    """
    return [nome for nome, _, minimo in consumidores_por_prioridade(colonia)
            if energia >= minimo]


def analisar_energia(geracao, consumo, reserva=None):
    """Compara geração, consumo e (opcionalmente) a reserva das baterias."""
    saldo = geracao - consumo

    if consumo > geracao:
        if reserva is not None and reserva >= -saldo:
            return ("ALERTA: consumo maior que geração "
                    "(reserva cobre o déficit por enquanto)")
        if reserva is not None:
            return "ALERTA CRÍTICO: consumo maior que geração e reserva insuficiente"
        return "ALERTA: consumo maior que geração"

    if geracao > consumo:
        return "SUGESTÃO: armazenar energia excedente"

    return "OK: geração e consumo equilibrados"
