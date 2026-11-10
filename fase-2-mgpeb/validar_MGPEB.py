"""
Testes de validação do protótipo MGPEB (Fase 2 - Aurora Siger).

Cobre o que o relatório descreve na seção 9:
- as quatro decisões (AUTORIZAR, RESTRINGIR, ADIAR, BLOQUEAR);
- limites de combustível e de sensores;
- meta-regra M01;
- dependências entre módulos;
- atualização do ambiente;
- ordenação e busca;
- fila FIFO, fila de prioridade, lista encadeada e pilha LIFO;
- domínio da função matemática de descida.

Usa apenas a biblioteca padrão (unittest).
Execução, a partir desta pasta:  python validar_MGPEB.py
"""
import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime

from MGPEB import (ControleMissao, Criticidade, Fila, FilaPrioridade,
                   ListaEncadeada, Modulo, Pilha, Prioridade, altura_descida,
                   busca_sequencial, demonstracao, menor_combustivel,
                   montar_cenario, ordenar_insercao)

P, C = Prioridade, Criticidade
ETA_PASSADA = datetime(2026, 10, 12, 10, 0)   # antes do relógio da missão (12h)
ETA_FUTURA = datetime(2026, 10, 12, 15, 0)    # depois do relógio da missão


def modulo(nome="Teste", tipo="ciência", prioridade=P.MEDIA, combustivel=90,
           massa=6_000, criticidade=C.MEDIA, eta=ETA_PASSADA, dependencias=(),
           zona="ZP-1", sensores=(100, 100, 100, 100)):
    """Cria um módulo com valores seguros; cada teste altera só o que precisa."""
    return Modulo(nome, tipo, prioridade, combustivel, massa, criticidade, eta,
                  dependencias, zona=zona, sensores=sensores)


def silencioso(funcao, *args):
    """Executa sem poluir a saída do teste com os logs do controle de missão."""
    with redirect_stdout(io.StringIO()):
        return funcao(*args)


def ids(motivos):
    """Extrai só os códigos das regras, ex.: ['R01', 'M01']."""
    return [m.split(":")[0] for m in motivos]


# ------------------------------------------------------------ decisões
class TestDecisoes(unittest.TestCase):
    def setUp(self):
        self.cm = ControleMissao()

    def test_autorizar_sem_violacoes(self):
        self.assertEqual(self.cm.avaliar(modulo()), ("AUTORIZAR", []))

    def test_restringir_navegacao_degradada(self):
        decisao, motivos = self.cm.avaliar(modulo(sensores=(100, 100, 50, 100)))
        self.assertEqual(decisao, "RESTRINGIR")
        self.assertEqual(ids(motivos), ["R14"])

    def test_restringir_poeira_moderada(self):
        self.cm.tau = 2.5
        decisao, motivos = self.cm.avaliar(modulo())
        self.assertEqual(decisao, "RESTRINGIR")
        self.assertEqual(ids(motivos), ["R13"])

    def test_adiar_vento_excessivo(self):
        self.cm.vento = 20
        decisao, motivos = self.cm.avaliar(modulo())
        self.assertEqual(decisao, "ADIAR")
        self.assertEqual(ids(motivos), ["R06"])

    def test_limite_de_vento_menor_para_habitacao(self):
        self.cm.vento = 15            # passa para 'ciência' (18), viola 'habitação' (12)
        self.assertEqual(self.cm.avaliar(modulo())[0], "AUTORIZAR")
        self.assertEqual(self.cm.avaliar(modulo(tipo="habitação"))[0], "ADIAR")

    def test_adiar_tempestade_enlace_e_chegada_futura(self):
        self.cm.tau, self.cm.enlace = 3.5, False
        decisao, motivos = self.cm.avaliar(modulo(eta=ETA_FUTURA))
        self.assertEqual(decisao, "ADIAR")
        self.assertEqual(ids(motivos), ["R07", "R10", "R11"])

    def test_adiar_zona_lotada(self):
        self.cm.zonas["ZP-1"][3] = 10           # ocupação = capacidade
        self.assertEqual(ids(self.cm.avaliar(modulo())[1]), ["R08"])

    def test_bloquear_massa_acima_da_zona(self):
        decisao, motivos = self.cm.avaliar(modulo(massa=45_000, combustivel=70))
        self.assertEqual(decisao, "BLOQUEAR")
        self.assertIn("R02", ids(motivos))

    def test_precedencia_bloqueio_vence_adiamento(self):
        self.cm.vento = 25
        decisao, motivos = self.cm.avaliar(modulo(massa=45_000, combustivel=70))
        self.assertEqual(decisao, "BLOQUEAR")
        self.assertEqual(ids(motivos), ["R02", "R06"])


# ------------------------------------------------- limites de combustível
class TestCombustivel(unittest.TestCase):
    """Fmin = 12 + 0,5 x toneladas. Para 22 t, Fmin = 23%."""

    def setUp(self):
        self.cm = ControleMissao()

    def test_abaixo_do_minimo_bloqueia(self):
        decisao, motivos = self.cm.avaliar(modulo(massa=22_000, combustivel=22.9))
        self.assertEqual(decisao, "BLOQUEAR")
        self.assertIn("R01", ids(motivos))

    def test_exatamente_no_minimo_restringe(self):
        decisao, motivos = self.cm.avaliar(modulo(massa=22_000, combustivel=23))
        self.assertEqual(decisao, "RESTRINGIR")
        self.assertEqual(ids(motivos), ["R12"])

    def test_margem_de_5_pontos_autoriza(self):
        self.assertEqual(
            self.cm.avaliar(modulo(massa=22_000, combustivel=28))[0], "AUTORIZAR")

    def test_cenario_logistica_bloqueada(self):
        logistica = montar_cenario(datetime(2026, 10, 12, 9, 0))[5]
        self.assertEqual(ids(self.cm.avaliar(logistica)[1]), ["R01"])


# ------------------------------------------------------ limites de sensores
class TestSensores(unittest.TestCase):
    """Ordem dos sensores: radar, IMU, lidar, câmera."""

    def setUp(self):
        self.cm = ControleMissao()

    def test_radar_69_bloqueia_e_70_passa(self):
        self.assertIn("R04", ids(self.cm.avaliar(modulo(sensores=(69, 100, 100, 100)))[1]))
        self.assertEqual(self.cm.avaliar(modulo(sensores=(70, 100, 100, 100)))[0], "AUTORIZAR")

    def test_imu_degradado_bloqueia(self):
        self.assertIn("R04", ids(self.cm.avaliar(modulo(sensores=(100, 60, 100, 100)))[1]))

    def test_menos_de_tres_sensores_operantes(self):
        decisao, motivos = self.cm.avaliar(modulo(sensores=(100, 100, 59, 59)))
        self.assertEqual(decisao, "BLOQUEAR")
        self.assertIn("R05", ids(motivos))

    def test_tres_sensores_operantes_nao_bloqueia(self):
        decisao, motivos = self.cm.avaliar(modulo(sensores=(100, 100, 60, 59)))
        self.assertEqual(decisao, "RESTRINGIR")
        self.assertEqual(ids(motivos), ["R14"])


# ------------------------------------------------------------- meta-regra
class TestMetaRegraM01(unittest.TestCase):
    def setUp(self):
        self.cm = ControleMissao()

    def test_exemplo_do_documento_logistica_em_tempestade(self):
        """22 t, 24% de combustível, vento 24 m/s, tau 3,6, lidar 58%."""
        self.cm.vento, self.cm.tau = 24, 3.6
        m = modulo(massa=22_000, combustivel=24, sensores=(100, 100, 58, 100))
        decisao, motivos = self.cm.avaliar(m)
        self.assertEqual(decisao, "BLOQUEAR")
        self.assertEqual(ids(motivos), ["M01", "R06", "R07", "R12", "R14"])

    def test_com_margem_suficiente_apenas_adia(self):
        self.cm.vento = 24
        decisao, motivos = self.cm.avaliar(modulo(massa=22_000, combustivel=40))
        self.assertEqual(decisao, "ADIAR")
        self.assertNotIn("M01", ids(motivos))


# ------------------------------------------- dependências e reavaliação
class TestFluxo(unittest.TestCase):
    def setUp(self):
        self.cm = ControleMissao()

    def test_dependencia_adia_e_libera_depois_do_pouso(self):
        base = modulo("Base", prioridade=P.ALTA)
        dependente = modulo("Dependente", prioridade=P.MAXIMA, dependencias=("Base",))
        silencioso(self.cm.registrar, base)
        silencioso(self.cm.registrar, dependente)

        silencioso(self.cm.processar_proximo)          # Dependente sai primeiro
        self.assertEqual(dependente.status, "EM_ESPERA")
        self.assertEqual(ids(dependente.alertas), ["R09"])

        while silencioso(self.cm.processar_proximo):
            pass
        self.assertEqual([m.nome for m in self.cm.pousados], ["Base", "Dependente"])
        self.assertEqual(len(self.cm.espera), 0)

    def test_atualizacao_ambiental_libera_a_espera(self):
        self.cm.tau = 3.5
        m = modulo()
        silencioso(self.cm.registrar, m)
        silencioso(self.cm.processar_proximo)
        self.assertEqual(len(self.cm.espera), 1)

        silencioso(self.cm.atualizar_ambiente, 5.0, 1.0, True, self.cm.relogio)
        self.assertEqual(len(self.cm.espera), 0)
        self.assertEqual(len(self.cm.autorizacao), 1)
        self.assertEqual(m.status, "AGUARDANDO_AUTORIZACAO")

    def test_reabastecimento_tira_do_alerta(self):
        m = modulo("Carga", massa=22_000, combustivel=11)
        silencioso(self.cm.registrar, m)
        silencioso(self.cm.processar_proximo)
        self.assertEqual(m.status, "BLOQUEADO")

        silencioso(self.cm.reabastecer_e_reavaliar, "Carga", 40)
        silencioso(self.cm.processar_proximo)
        self.assertEqual(m.status, "POUSADO")
        self.assertEqual(len(self.cm.alerta), 0)

    def test_pouso_ocupa_vaga_da_zona(self):
        silencioso(self.cm.registrar, modulo())
        silencioso(self.cm.processar_proximo)
        self.assertEqual(self.cm.zonas["ZP-1"][3], 1)

    def test_demonstracao_termina_com_sete_pousados(self):
        cm = silencioso(demonstracao)
        self.assertEqual(len(cm.pousados), 7)
        self.assertEqual(len(cm.autorizacao) + len(cm.espera) + len(cm.alerta), 0)


# -------------------------------------------------- busca e ordenação
class TestBuscaOrdenacao(unittest.TestCase):
    def setUp(self):
        self.modulos = montar_cenario(datetime(2026, 10, 12, 9, 0))

    def test_menor_combustivel(self):
        self.assertEqual(menor_combustivel(self.modulos).nome, "Logística/Suprimentos")
        self.assertIsNone(menor_combustivel([]))

    def test_busca_por_tipo(self):
        self.assertEqual([m.nome for m in busca_sequencial(self.modulos, "energia")],
                         ["Energia (Reator)"])
        self.assertEqual(busca_sequencial(self.modulos, "inexistente"), [])

    def test_ordenacao_por_prioridade_criticidade_e_eta(self):
        esperado = ["Trem de Pouso", "Energia (Reator)", "Habitação", "Suporte Médico",
                    "Logística/Suprimentos", "Laboratório Científico", "Rover de Exploração"]
        embaralhado = list(reversed(self.modulos))
        self.assertEqual([m.nome for m in ordenar_insercao(embaralhado)], esperado)

    def test_ordenacao_e_estavel(self):
        a, b = modulo("A"), modulo("B")         # mesma chave
        self.assertEqual([m.nome for m in ordenar_insercao([a, b])], ["A", "B"])
        self.assertEqual([m.nome for m in ordenar_insercao([b, a])], ["B", "A"])

    def test_ordenacao_nao_altera_a_lista_original(self):
        original = list(self.modulos)
        ordenar_insercao(self.modulos)
        self.assertEqual(self.modulos, original)


# ----------------------------------------------------- estruturas lineares
class TestEstruturas(unittest.TestCase):
    def test_fila_fifo(self):
        f = Fila()
        for x in ("a", "b", "c"):
            f.adicionar(x)
        self.assertEqual([f.desenfileirar() for _ in range(4)], ["a", "b", "c", None])
        self.assertEqual(len(f), 0)

    def test_pilha_lifo(self):
        p = Pilha()
        for x in (1, 2, 3):
            p.empilhar(x)
        self.assertEqual(list(p), [3, 2, 1])
        self.assertEqual([p.desempilhar() for _ in range(4)], [3, 2, 1, None])

    def test_fila_de_prioridade(self):
        fp = FilaPrioridade()
        baixa, maxima, alta = modulo("Baixa", prioridade=P.BAIXA), \
            modulo("Maxima", prioridade=P.MAXIMA), modulo("Alta", prioridade=P.ALTA)
        for m in (baixa, maxima, alta):
            fp.adicionar(m)
        self.assertEqual([fp.desenfileirar().nome for _ in range(3)],
                         ["Maxima", "Alta", "Baixa"])

    def test_lista_encadeada_remover(self):
        lista = ListaEncadeada()
        a, b, c = modulo("A"), modulo("B"), modulo("C")
        for m in (a, b, c):
            lista.adicionar(m)
        self.assertTrue(lista.remover(b))
        self.assertFalse(lista.remover(b))
        self.assertEqual([m.nome for m in lista], ["A", "C"])
        self.assertTrue(lista.contem_nome("C"))
        self.assertEqual(len(lista), 2)


# ---------------------------------------------------- função matemática
class TestAlturaDescida(unittest.TestCase):
    def test_valores_da_reta(self):
        self.assertEqual([altura_descida(t) for t in (0, 10, 40, 50)], [1000, 800, 200, 0])

    def test_fora_do_dominio(self):
        for t in (-1, 51):
            with self.assertRaises(ValueError):
                altura_descida(t)


if __name__ == "__main__":
    unittest.main(verbosity=2)
