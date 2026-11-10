"""
Aurora Siger III - Sistema integrado da colônia (Fase 3)
=========================================================
Junta as quatro partes do sistema:
  1. Organização dos dados (hierarquia, chave-valor e listas)
  2. Regras de decisão (simples, combinadas e com prioridade)
  3. Previsão por regressão linear
  4. Análise do uso de energia (geração x consumo x reserva)
e integra tudo no fluxo: previsão -> análise -> decisão.

Roda com Python 3 puro, sem bibliotecas externas.
  python main.py               -> demonstração completa
  python main.py --interativo  -> demonstração + menu para digitar valores
"""
import sys
from copy import deepcopy

from dados import CENARIOS, COLONIA, HISTORICO
from decisoes import analisar_energia, decidir_acao, sistemas_a_manter
from estrutura import listar_subsistemas, mostrar_arvore, navegar, somar_campo
from previsao import prever_comportamento


# ---------------------------------------------------------------
# INTEGRAÇÃO: previsão -> análise -> decisão
# ---------------------------------------------------------------
def simular_cenario(colonia, historico, cenario):
    """
    Recebe um cenário (clima, população e carga da bateria), prevê geração
    e consumo, grava as previsões na hierarquia da colônia, analisa o
    balanço de energia e decide a ação. Não altera a colônia original.
    """
    colonia = deepcopy(colonia)
    clima = cenario["clima"]

    # 1) Previsão: a geração prevista não pode passar da capacidade instalada
    solar = navegar(colonia, "energia/geracao/solar")
    eolica = navegar(colonia, "energia/geracao/eolica")
    prev_solar = prever_comportamento(historico, "solar", clima["horas_sol"])["previsao"]
    prev_eolica = prever_comportamento(historico, "eolica", clima["vento_kmh"])["previsao"]
    solar["geracao_kwh"] = max(0, min(prev_solar, solar["capacidade_kwh"]))
    eolica["geracao_kwh"] = max(0, min(prev_eolica, eolica["capacidade_kwh"]))
    consumo = prever_comportamento(historico, "consumo", cenario["populacao"])["previsao"]

    baterias = navegar(colonia, "energia/armazenamento/baterias")
    baterias["carga_kwh"] = cenario["carga_bateria_kwh"]

    # 2) Totais lidos da hierarquia (soma recursiva do ramo de geração)
    ramo_geracao = navegar(colonia, "energia/geracao")
    geracao_total = somar_campo(ramo_geracao, "geracao_kwh")
    capacidade_geracao = somar_campo(ramo_geracao, "capacidade_kwh")

    # 3) Percentuais usados pelas regras de decisão
    #    energia (%) = carga da bateria em relação à capacidade da bateria
    #    consumo (%) = consumo previsto em relação à capacidade de geração
    energia_pct = baterias["carga_kwh"] / baterias["capacidade_kwh"] * 100
    consumo_pct = min(100, consumo / capacidade_geracao * 100)

    return {
        "solar_kwh": solar["geracao_kwh"],
        "eolica_kwh": eolica["geracao_kwh"],
        "geracao_kwh": geracao_total,
        "consumo_kwh": consumo,
        "reserva_kwh": baterias["carga_kwh"],
        "energia_pct": energia_pct,
        "consumo_pct": consumo_pct,
        "analise": analisar_energia(geracao_total, consumo, baterias["carga_kwh"]),
        "decisao": decidir_acao(energia_pct, consumo_pct),
        "sistemas": sistemas_a_manter(colonia, energia_pct),
    }


# ---------------------------------------------------------------
# DEMONSTRAÇÃO
# ---------------------------------------------------------------
def demonstrar_estrutura():
    print("\n[1] ORGANIZAÇÃO DOS DADOS - HIERARQUIA DA COLÔNIA")
    for linha in mostrar_arvore(COLONIA):
        print("  " + linha)

    print("\n  Navegação entre subsistemas:")
    for caminho in ("energia", "energia/geracao", "suporte_vida"):
        print(f"    {caminho:<16} -> {listar_subsistemas(navegar(COLONIA, caminho))}")
    baterias = navegar(COLONIA, "energia/armazenamento/baterias")
    print(f"    energia/armazenamento/baterias -> {baterias['carga_kwh']} de "
          f"{baterias['capacidade_kwh']} kWh")
    capacidade = somar_campo(navegar(COLONIA, "energia/geracao"), "capacidade_kwh")
    print(f"    Capacidade total de geração (soma do ramo) = {capacidade} kWh")


def demonstrar_regras():
    print("\n[2] REGRAS DE DECISÃO")
    for energia, consumo in [(40, 70), (40, 30), (70, 80), (80, 30), (15, 50)]:
        print(f"  energia = {energia}, consumo = {consumo}"
              f"  ->  {decidir_acao(energia, consumo)}")

    print("\n  Sistemas mantidos por nível de energia (lidos da hierarquia):")
    for nivel in (15, 40, 60, 90):
        print(f"    energia = {nivel:>2}%: {', '.join(sistemas_a_manter(COLONIA, nivel))}")


def demonstrar_regressao():
    print("\n[3] REGRESSÃO LINEAR - PREVISÃO DE COMPORTAMENTOS")
    entradas = {"eolica": [11, 14], "solar": [7, 12], "consumo": [35, 60]}
    for chave, valores in entradas.items():
        dados = HISTORICO[chave]
        print(f"\n  {dados['descricao']}")
        print(f"    {dados['x_nome']}: {dados['x']}")
        print(f"    {dados['y_nome']}: {dados['y']}")
        r = prever_comportamento(HISTORICO, chave, valores[0])
        sinal = "+" if r["b"] >= 0 else "-"
        print(f"    Reta: y = {r['a']:.2f} * x {sinal} {abs(r['b']):.2f}"
              f"   (R² = {r['r2']:.3f})")
        for v in valores:
            prev = prever_comportamento(HISTORICO, chave, v)["previsao"]
            print(f"    {dados['x_nome']} = {v}  ->  {dados['y_nome']} ≈ {prev:.1f}")


def demonstrar_analise():
    print("\n[4] ANÁLISE DE USO DE ENERGIA")
    casos = [(40, 70, None), (80, 30, None), (45, 60, 50), (45, 60, 5), (50, 50, None)]
    for geracao, consumo, reserva in casos:
        extra = f", reserva = {reserva}" if reserva is not None else ""
        print(f"  geração = {geracao}, consumo = {consumo}{extra}")
        print(f"    -> {analisar_energia(geracao, consumo, reserva)}")


def demonstrar_integracao():
    print("\n[5] INTEGRAÇÃO: previsão -> análise -> decisão")
    for cenario in CENARIOS.values():
        clima = cenario["clima"]
        r = simular_cenario(COLONIA, HISTORICO, cenario)
        print(f"\n  Cenário: {cenario['descricao']}")
        print(f"    Entrada: vento = {clima['vento_kmh']} km/h, "
              f"horas de sol = {clima['horas_sol']}, população = {cenario['populacao']}, "
              f"bateria = {cenario['carga_bateria_kwh']} kWh")
        print(f"    Previsão: solar ≈ {r['solar_kwh']:.1f}, eólica ≈ {r['eolica_kwh']:.1f}, "
              f"geração ≈ {r['geracao_kwh']:.1f}, consumo ≈ {r['consumo_kwh']:.1f} kWh")
        print(f"    Análise: {r['analise']}")
        print(f"    Energia ≈ {r['energia_pct']:.0f}%, consumo ≈ {r['consumo_pct']:.0f}%"
              f"  ->  Decisão: {r['decisao']}")
        print(f"    Sistemas mantidos: {', '.join(r['sistemas'])}")


# ---------------------------------------------------------------
# MODO INTERATIVO
# ---------------------------------------------------------------
def ler_numero(mensagem):
    """Lê um número digitado (aceita vírgula). Devolve None se for inválido."""
    texto = input(mensagem).strip().replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        print("  Valor inválido.")
        return None


def modo_interativo():
    """Menu para o usuário digitar os próprios valores."""
    chaves = list(HISTORICO)
    while True:
        print("\n--- MODO INTERATIVO ---")
        print("  1) Prever geração ou consumo (regressão)")
        print("  2) Decidir ação (energia % e consumo %)")
        print("  3) Analisar energia (geração, consumo e reserva)")
        print("  4) Navegar na hierarquia da colônia")
        print("  0) Sair")
        opcao = input("Opção: ").strip()

        if opcao == "0":
            break
        elif opcao == "1":
            for i, chave in enumerate(chaves, 1):
                print(f"    {i}) {HISTORICO[chave]['descricao']}")
            escolha = input("  Qual? ").strip()
            if not escolha.isdigit() or not 1 <= int(escolha) <= len(chaves):
                print("  Opção inválida.")
                continue
            chave = chaves[int(escolha) - 1]
            valor = ler_numero(f"  Informe {HISTORICO[chave]['x_nome']}: ")
            if valor is not None:
                r = prever_comportamento(HISTORICO, chave, valor)
                print(f"  Previsão de {HISTORICO[chave]['y_nome']} ≈ {r['previsao']:.1f}"
                      f"  (R² = {r['r2']:.3f})")
        elif opcao == "2":
            energia = ler_numero("  Energia (%): ")
            consumo = ler_numero("  Consumo (%): ")
            if energia is not None and consumo is not None:
                print(f"  -> {decidir_acao(energia, consumo)}")
                print(f"  Sistemas mantidos: {', '.join(sistemas_a_manter(COLONIA, energia))}")
        elif opcao == "3":
            geracao = ler_numero("  Geração (kWh): ")
            consumo = ler_numero("  Consumo (kWh): ")
            texto = input("  Reserva (kWh, Enter para nenhuma): ").strip()
            try:
                reserva = float(texto.replace(",", ".")) if texto else None
            except ValueError:
                print("  Reserva inválida, considerada como nenhuma.")
                reserva = None
            if geracao is not None and consumo is not None:
                print(f"  -> {analisar_energia(geracao, consumo, reserva)}")
        elif opcao == "4":
            caminho = input("  Caminho (ex.: energia/geracao/solar, Enter = raiz): ").strip()
            try:
                no = navegar(COLONIA, caminho)
            except KeyError as erro:
                print(f"  {erro.args[0]}")
                continue
            dados_no = {k: v for k, v in no.items() if k != "subsistemas"}
            print(f"  Dados: {dados_no}")
            print(f"  Subsistemas: {listar_subsistemas(no) or 'nenhum'}")
        else:
            print("  Opção inválida.")


def main():
    print("=" * 60)
    print("  AURORA SIGER III - Sistema integrado da colônia")
    print("=" * 60)
    demonstrar_estrutura()
    demonstrar_regras()
    demonstrar_regressao()
    demonstrar_analise()
    demonstrar_integracao()
    if "--interativo" in sys.argv:
        modo_interativo()


if __name__ == "__main__":
    main()
