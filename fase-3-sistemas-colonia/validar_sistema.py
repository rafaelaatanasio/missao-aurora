"""
Testes de validação do sistema integrado da colônia (Fase 3).
Usa apenas a biblioteca padrão (unittest).

Execução, a partir desta pasta:  python validar_sistema.py
"""
import unittest

from dados import CENARIOS, COLONIA, HISTORICO
from decisoes import analisar_energia, decidir_acao, sistemas_a_manter
from estrutura import (consumidores_por_prioridade, listar_subsistemas,
                       mostrar_arvore, navegar, somar_campo)
from main import simular_cenario
from previsao import ajustar_reta, calcular_r2, prever, prever_comportamento


class TestEstrutura(unittest.TestCase):
    def test_navegar_ate_um_subsistema(self):
        self.assertEqual(navegar(COLONIA, "energia/geracao/solar")["nome"], "Painéis solares")

    def test_caminho_vazio_devolve_a_raiz(self):
        self.assertIs(navegar(COLONIA, ""), COLONIA)

    def test_caminho_invalido_mostra_opcoes(self):
        with self.assertRaises(KeyError) as erro:
            navegar(COLONIA, "energia/nuclear")
        self.assertIn("geracao", erro.exception.args[0])

    def test_listar_subsistemas(self):
        self.assertEqual(listar_subsistemas(navegar(COLONIA, "energia/geracao")),
                         ["solar", "eolica"])
        self.assertEqual(listar_subsistemas(navegar(COLONIA, "comunicacao")), [])

    def test_soma_recursiva_do_ramo(self):
        ramo = navegar(COLONIA, "energia/geracao")
        self.assertEqual(somar_campo(ramo, "capacidade_kwh"), 120)

    def test_arvore_tem_indentacao_por_nivel(self):
        linhas = mostrar_arvore(COLONIA)
        self.assertTrue(linhas[0].startswith("- Colônia"))
        self.assertIn("            - Painéis solares [solar]", linhas)

    def test_consumidores_ordenados_por_prioridade(self):
        nomes = [nome for nome, _, _ in consumidores_por_prioridade(COLONIA)]
        self.assertEqual(nomes[0], "Suporte à vida")
        self.assertEqual(nomes[-1], "Lazer e conforto")


class TestDecisoes(unittest.TestCase):
    def test_exemplo_do_enunciado(self):
        self.assertEqual(decidir_acao(40, 70), "ALERTA: ativar modo economia")

    def test_regra_basica(self):
        self.assertEqual(decidir_acao(40, 30), "ALERTA: reduzir consumo")

    def test_prioridade_do_suporte_a_vida(self):
        self.assertTrue(decidir_acao(15, 90).startswith("CRÍTICO"))

    def test_consumo_alto_e_normal(self):
        self.assertTrue(decidir_acao(70, 80).startswith("ATENÇÃO"))
        self.assertEqual(decidir_acao(80, 30), "OK: operação normal")

    def test_limites_exatos(self):
        self.assertEqual(decidir_acao(50, 60), "OK: operação normal")
        self.assertEqual(decidir_acao(20, 30), "ALERTA: reduzir consumo")

    def test_suporte_a_vida_nunca_desliga(self):
        self.assertEqual(sistemas_a_manter(COLONIA, 0), ["Suporte à vida"])
        self.assertEqual(len(sistemas_a_manter(COLONIA, 100)), 5)


class TestAnaliseEnergia(unittest.TestCase):
    def test_exemplos_do_enunciado(self):
        self.assertEqual(analisar_energia(40, 70), "ALERTA: consumo maior que geração")
        self.assertEqual(analisar_energia(80, 30), "SUGESTÃO: armazenar energia excedente")

    def test_reserva(self):
        self.assertIn("reserva cobre", analisar_energia(45, 60, 15))
        self.assertIn("CRÍTICO", analisar_energia(45, 60, 14))

    def test_equilibrio(self):
        self.assertEqual(analisar_energia(50, 50), "OK: geração e consumo equilibrados")


class TestPrevisao(unittest.TestCase):
    def test_exemplo_do_enunciado_vento_11(self):
        r = prever_comportamento(HISTORICO, "eolica", 11)
        self.assertAlmostEqual(r["previsao"], 27.5)
        self.assertAlmostEqual(r["r2"], 1.0)

    def test_reta_do_consumo(self):
        a, b = ajustar_reta(HISTORICO["consumo"]["x"], HISTORICO["consumo"]["y"])
        self.assertAlmostEqual(a, 1.29)
        self.assertAlmostEqual(b, 6.1)

    def test_r2_entre_0_e_1(self):
        dados = HISTORICO["solar"]
        a, b = ajustar_reta(dados["x"], dados["y"])
        self.assertTrue(0.99 < calcular_r2(dados["x"], dados["y"], a, b) <= 1)

    def test_prever(self):
        self.assertEqual(prever(2, 1, 3), 7)

    def test_dados_invalidos(self):
        with self.assertRaises(ValueError):
            ajustar_reta([1, 2], [1])
        with self.assertRaises(ValueError):
            ajustar_reta([5, 5, 5], [1, 2, 3])


class TestIntegracao(unittest.TestCase):
    def test_dia_normal(self):
        r = simular_cenario(COLONIA, HISTORICO, CENARIOS["dia_normal"])
        self.assertAlmostEqual(r["geracao_kwh"], 63.0)
        self.assertEqual(r["analise"], "SUGESTÃO: armazenar energia excedente")
        self.assertEqual(r["decisao"], "OK: operação normal")

    def test_tempestade_de_poeira(self):
        r = simular_cenario(COLONIA, HISTORICO, CENARIOS["tempestade_de_poeira"])
        self.assertIn("reserva cobre", r["analise"])
        self.assertEqual(r["decisao"], "ALERTA: ativar modo economia")
        self.assertNotIn("Laboratórios", r["sistemas"])

    def test_previsao_limitada_a_capacidade(self):
        cenario = {"clima": {"vento_kmh": 40, "horas_sol": 30},
                   "populacao": 10, "carga_bateria_kwh": 200}
        r = simular_cenario(COLONIA, HISTORICO, cenario)
        self.assertEqual(r["solar_kwh"], 70)
        self.assertEqual(r["eolica_kwh"], 50)

    def test_nao_altera_a_colonia_original(self):
        simular_cenario(COLONIA, HISTORICO, CENARIOS["dia_normal"])
        self.assertEqual(navegar(COLONIA, "energia/geracao/solar")["geracao_kwh"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
