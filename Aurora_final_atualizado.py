print("=== AURORA SINGER - CHECKLIST DE DECOLAGEM ===")

# Integridade estrutural (5 componentes)
print("\n-- Integridade estrutural --")
c1 = int(input("motores (1=OK / 0=falha): "))
c2 = int(input("Tanques de pressão (1=OK / 0=falha): "))
c3 = int(input("Estruturas de suporte de carga (1=OK / 0=falha): "))
c4 = int(input("Câmara de combustão(Nozzle) (1=OK / 0=falha): "))
c5 = int(input("Estrutura principal(Fuselagem) (1=OK / 0=falha): "))

# Niveis de energia
print("\n-- Niveis de energia --")
bateria = float(input("Bateria principal (%): "))
sistema_critico = float(input("Sistema critico (%): "))

# Pressao dos tanques
print("\n-- Pressao dos tanques --")
p_lox = float(input("Pressao LOX (psia): "))
p_lh2 = float(input("Pressao LH2 (psia): "))
p_helio = float(input("Pressao Helio (psi): "))
p_camara = float(input("Pressao da camara (psi): "))

# Status dos modulos criticos (6 modulos)
print("\n-- Status dos modulos criticos --")
m1 = int(input("Sistema de propulsão(1=operacional / 0=falha): "))
m2 = int(input("Aviônicos e controle de voo (1=operacional / 0=falha): "))
m3 = int(input("Telemetria e Comunicação (1=operacional / 0=falha): "))
m4 = int(input("Sistemas de energia (1=operacional / 0=falha): "))
m5 = int(input("Controle Térmico (1=operacional / 0=falha): "))
m6 = int(input("Estrutura e carga (1=operacional / 0=falha): "))

# Temperaturas
print("\n-- Temperaturas --")
t_camara = float(input("Temperatura da camara (K): "))
t_lox = float(input("Temperatura do tanque LOX (K): "))
t_lh2 = float(input("Temperatura do tanque LH2 (K): "))

# Integridade estrutural
ok_estrutural = (c1 == 1 and c2 == 1 and c3 == 1 and c4 == 1 and c5 == 1)

# Niveis de energia
ok_energia = (bateria >= 70 and sistema_critico >= 70)

# Pressao dos tanques
ok_lox = (30 <= p_lox <= 50)
ok_lh2 = (30 <= p_lh2 <= 50)
ok_helio = (2175 <= p_helio <= 4350)
ok_camara_p = (150 <= p_camara <= 3000)
ok_pressao = (ok_lox and ok_lh2 and ok_helio and ok_camara_p)

# Status dos modulos
ok_modulos = (m1 == 1 and m2 == 1 and m3 == 1 and m4 == 1 and m5 == 1 and m6 == 1)

# Temperaturas
# Faixas de referencia para os tanques criogenicos (ajustar se o projeto
# definir valores especificos)
ok_temp_camara = (2700 <= t_camara <= 3600)
ok_temp_lox = (90 <= t_lox <= 165)
ok_temp_lh2 = (20 <= t_lh2 <= 33)
ok_temperaturas = (ok_temp_camara and ok_temp_lox and ok_temp_lh2)

print("\n============================================================")
print("RELATORIO DE VERIFICACAO - AURORA SINGER")
print("============================================================")

if ok_estrutural:
    print("[APROVADO] Integridade estrutural")
else:
    print("[REPROVADO] Integridade estrutural")

if ok_energia:
    print("[APROVADO] Niveis de energia")
else:
    print("[REPROVADO] Niveis de energia")

if ok_pressao:
    print("[APROVADO] Pressao dos tanques")
else:
    print("[REPROVADO] Pressao dos tanques")

if ok_modulos:
    print("[APROVADO] Status dos modulos")
else:
    print("[REPROVADO] Status dos modulos")

if ok_temperaturas:
    print("[APROVADO] Temperaturas")
else:
    print("[REPROVADO] Temperaturas")

print("============================================================")

if ok_estrutural and ok_energia and ok_pressao and ok_modulos and ok_temperaturas:
    print("RESULTADO FINAL: GO PARA LANÇAMENTO")
else:
    print("RESULTADO FINAL: NOT-GO - LANÇAMENTO ABORTADO")

print("============================================================")


# ============================================================
# 1.4 - ANALISE ENERGETICA
# ============================================================

# Premissas academicas definidas pelo grupo para a simulacao
capacidade_total = 5000          # kWh
consumo_decolagem = 1500        # kWh
perdas = 0.05                    # 5%

# O percentual de carga vem da telemetria informada anteriormente
carga_atual = bateria / 100

# Calculos energeticos
energia_disponivel = capacidade_total * carga_atual
energia_perdida = energia_disponivel * perdas
energia_util = energia_disponivel - energia_perdida
energia_restante = energia_util - consumo_decolagem

print("\n============================================================")
print("ANALISE ENERGETICA - AURORA SINGER")
print("============================================================")
print("Capacidade total do sistema:", capacidade_total, "kWh")
print("Carga atual da bateria:", bateria, "%")
print("Energia disponivel:", round(energia_disponivel, 2), "kWh")
print("Perdas energeticas:", perdas * 100, "%")
print("Energia perdida:", round(energia_perdida, 2), "kWh")
print("Energia util:", round(energia_util, 2), "kWh")
print("Consumo estimado na decolagem:", consumo_decolagem, "kWh")
print("Energia restante apos a decolagem:", round(energia_restante, 2), "kWh")
print("============================================================")


# ============================================================
# 1.5 - ANALISE ASSISTIDA POR IA
# ============================================================

resultado_estrutural = "APROVADO" if ok_estrutural else "REPROVADO"
resultado_energia = "APROVADO" if ok_energia else "REPROVADO"
resultado_pressao = "APROVADO" if ok_pressao else "REPROVADO"
resultado_modulos = "APROVADO" if ok_modulos else "REPROVADO"
resultado_temperaturas = "APROVADO" if ok_temperaturas else "REPROVADO"

resultado_final = (
    "GO PARA LANCAMENTO"
    if ok_estrutural and ok_energia and ok_pressao and ok_modulos and ok_temperaturas
    else "NOT-GO - LANCAMENTO ABORTADO"
)

prompt_ia = f"""
Estou desenvolvendo um relatorio academico para a disciplina de
Ciencia da Computacao da FIAP.

Voce deve atuar apenas como ferramenta de apoio a interpretacao
dos dados simulados da Missao Aurora Singer, sem criar novas faixas,
limites ou especificacoes tecnicas.

Os valores e limites utilizados sao premissas academicas definidas
pelo grupo para esta simulacao.

Resultados obtidos pelo algoritmo:

- Integridade estrutural: {resultado_estrutural}
- Niveis de energia: {resultado_energia}
- Pressao dos tanques: {resultado_pressao}
- Status dos modulos criticos: {resultado_modulos}
- Temperaturas: {resultado_temperaturas}
- Energia util estimada: {energia_util:.2f} kWh
- Consumo estimado na decolagem: {consumo_decolagem:.2f} kWh
- Energia restante apos a decolagem: {energia_restante:.2f} kWh
- Resultado final do algoritmo: {resultado_final}

Com base somente nesses dados:

1. Classifique os resultados como normais ou anomalos.
2. Identifique possiveis anomalias.
3. Indique riscos relacionados aos criterios que foram reprovados.
4. Escreva uma conclusao explicando que a Inteligencia Artificial
   foi utilizada apenas como apoio a interpretacao dos dados
   simulados e que a decisao final permanece baseada nas regras
   implementadas pelo algoritmo desenvolvido pelo grupo.
"""

print("\\n============================================================")
print("PROMPT PARA ANALISE ASSISTIDA POR IA")
print("============================================================")
print(prompt_ia)
print("============================================================")
