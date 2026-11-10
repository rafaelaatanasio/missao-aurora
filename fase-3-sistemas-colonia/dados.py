"""
DADOS da colônia Aurora Siger (Fase 3).

Este arquivo guarda apenas dados, sem regras de decisão. Três formas de
organização são usadas:

1. Hierarquia (árvore): COLONIA, os sistemas e seus subsistemas.
2. Chave-valor (dicionário): CLIMA e CENARIOS, as leituras atuais.
3. Listas: HISTORICO, as séries de dados usadas na regressão.

Os valores são premissas acadêmicas definidas pelo grupo para a simulação.
Unidades: energia em kWh, vento em km/h, população em pessoas.
"""

# ---------------------------------------------------------------
# 1) HIERARQUIA DA COLÔNIA
# ---------------------------------------------------------------
# Cada nó é um dicionário. Os filhos ficam em "subsistemas".
# Consumidores de energia têm:
#   prioridade      -> 1 é o mais importante (nunca desligar)
#   energia_minima  -> nível de bateria (%) abaixo do qual o sistema é desligado
COLONIA = {
    "nome": "Colônia Aurora Siger",
    "subsistemas": {
        "energia": {
            "nome": "Sistema energético",
            "subsistemas": {
                "geracao": {
                    "nome": "Geração renovável",
                    "subsistemas": {
                        "solar": {"nome": "Painéis solares",
                                  "capacidade_kwh": 70, "geracao_kwh": 0},
                        "eolica": {"nome": "Turbinas eólicas",
                                   "capacidade_kwh": 50, "geracao_kwh": 0},
                    },
                },
                "armazenamento": {
                    "nome": "Armazenamento",
                    "subsistemas": {
                        "baterias": {"nome": "Banco de baterias",
                                     "capacidade_kwh": 200, "carga_kwh": 120},
                    },
                },
            },
        },
        "suporte_vida": {
            "nome": "Suporte à vida", "prioridade": 1, "energia_minima": 0,
            "subsistemas": {
                "oxigenio": {"nome": "Geração de oxigênio"},
                "agua": {"nome": "Reciclagem de água"},
                "temperatura": {"nome": "Controle de temperatura"},
            },
        },
        "comunicacao": {"nome": "Comunicação", "prioridade": 2, "energia_minima": 20},
        "iluminacao": {"nome": "Iluminação", "prioridade": 3, "energia_minima": 35},
        "laboratorios": {"nome": "Laboratórios", "prioridade": 4, "energia_minima": 50},
        "lazer": {"nome": "Lazer e conforto", "prioridade": 5, "energia_minima": 70},
    },
}

# ---------------------------------------------------------------
# 2) CHAVE-VALOR: CLIMA E CENÁRIOS
# ---------------------------------------------------------------
# Leituras do momento usadas pela integração (previsão -> análise -> decisão).
CENARIOS = {
    "dia_normal": {
        "descricao": "Dia normal",
        "clima": {"vento_kmh": 11, "horas_sol": 7},
        "populacao": 35,
        "carga_bateria_kwh": 120,
    },
    "tempestade_de_poeira": {
        "descricao": "Tempestade de poeira (pouco sol, mais gente na base)",
        "clima": {"vento_kmh": 6, "horas_sol": 2},
        "populacao": 55,
        "carga_bateria_kwh": 80,
    },
}

# ---------------------------------------------------------------
# 3) LISTAS: HISTÓRICO PARA A REGRESSÃO
# ---------------------------------------------------------------
# Cada comportamento tem uma entrada (x) e uma saída (y) observadas.
HISTORICO = {
    "eolica": {
        "descricao": "Energia eólica gerada a partir do vento",
        "x_nome": "vento (km/h)",
        "y_nome": "energia eólica (kWh)",
        "x": [8, 10, 12],
        "y": [20, 25, 30],
    },
    "solar": {
        "descricao": "Energia solar gerada a partir das horas de sol",
        "x_nome": "horas de sol",
        "y_nome": "energia solar (kWh)",
        "x": [4, 6, 8, 10],
        "y": [18, 31, 41, 52],
    },
    "consumo": {
        "descricao": "Consumo de energia a partir da população",
        "x_nome": "população (pessoas)",
        "y_nome": "consumo (kWh)",
        "x": [20, 30, 40, 50],
        "y": [32, 44, 59, 70],
    },
}
