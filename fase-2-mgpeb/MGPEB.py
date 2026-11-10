"""
Simulação de pouso em Marte com estruturas de dados lineares.

Estruturas implementadas manualmente:
- Nodo / ListaEncadeada : lista simples (pousados, alerta)
- FilaPrioridade        : lista encadeada ordenada (aguardando autorização de pouso)
- Fila (FIFO)           : módulos em espera (bloqueados por dependência)
- Pilha (LIFO)          : histórico de eventos do controle de missão
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum


# ---------------------------------------------------------------- domínio
class Prioridade(IntEnum):      # menor valor = pousa primeiro
    MAXIMA = 1
    ALTA = 2
    MEDIA = 3
    BAIXA = 4


class Criticidade(IntEnum):     # maior valor = carga mais crítica
    BAIXA = 1
    MEDIA = 2
    ALTA = 3
    VITAL = 4


@dataclass
class Modulo:
    nome: str
    tipo: str
    prioridade: Prioridade
    combustivel_pct: float          # combustível restante para o pouso (%)
    massa_kg: float
    criticidade: Criticidade
    eta_orbita: datetime            # chegada estimada à órbita de Marte
    dependencias: tuple = ()        # nomes de módulos que devem estar pousados antes
    status: str = "AGUARDANDO_AUTORIZACAO"
    alertas: list = field(default_factory=list)
    zona: str = "ZP-1"
    sensores: tuple = (100, 100, 100, 100)  # radar, IMU, lidar, câmera


    def __str__(self):
        return (f"{self.nome:<22} P={self.prioridade.name:<6} "
                f"CRIT={self.criticidade.name:<5} COMB={self.combustivel_pct:5.1f}% "
                f"MASSA={self.massa_kg:>7.0f}kg ETA={self.eta_orbita:%d/%m %H:%M}")


# ------------------------------------------------- estruturas lineares
class Nodo:
    def __init__(self, dado):
        self.dado, self.prox = dado, None


class ListaEncadeada:
    def __init__(self):
        self.inicio, self.tamanho = None, 0

    def adicionar(self, dado):
        n = Nodo(dado)
        if not self.inicio:
            self.inicio = n
        else:
            atual = self.inicio
            while atual.prox:
                atual = atual.prox
            atual.prox = n
        self.tamanho += 1

    def remover(self, dado):
        ant, atual = None, self.inicio
        while atual:
            if atual.dado is dado:
                if ant:
                    ant.prox = atual.prox
                else:
                    self.inicio = atual.prox
                self.tamanho -= 1
                return True
            ant, atual = atual, atual.prox
        return False

    def __iter__(self):
        atual = self.inicio
        while atual:
            yield atual.dado
            atual = atual.prox

    def __len__(self):
        return self.tamanho

    def contem_nome(self, nome):
        return any(m.nome == nome for m in self)


class FilaPrioridade(ListaEncadeada):
    """Inserção ordenada: prioridade ↑, criticidade ↓, ETA ↑ (desempate)."""

    @staticmethod
    def _chave(m):
        return (m.prioridade, -m.criticidade, m.eta_orbita)

    def adicionar(self, m):
        n = Nodo(m)
        if not self.inicio or self._chave(m) < self._chave(self.inicio.dado):
            n.prox, self.inicio = self.inicio, n
        else:
            atual = self.inicio
            while atual.prox and self._chave(atual.prox.dado) <= self._chave(m):
                atual = atual.prox
            n.prox, atual.prox = atual.prox, n
        self.tamanho += 1

    def desenfileirar(self):
        if not self.inicio:
            return None
        m = self.inicio.dado
        self.inicio = self.inicio.prox
        self.tamanho -= 1
        return m


class Fila(ListaEncadeada):
    """FIFO simples (enfileira no fim, desenfileira no início)."""

    def desenfileirar(self):
        if not self.inicio:
            return None
        m = self.inicio.dado
        self.inicio = self.inicio.prox
        self.tamanho -= 1
        return m


class Pilha:
    def __init__(self):
        self.topo, self.tamanho = None, 0

    def empilhar(self, dado):
        n = Nodo(dado)
        n.prox, self.topo = self.topo, n
        self.tamanho += 1

    def desempilhar(self):
        if not self.topo:
            return None
        d = self.topo.dado
        self.topo = self.topo.prox
        self.tamanho -= 1
        return d

    def __iter__(self):
        atual = self.topo
        while atual:
            yield atual.dado
            atual = atual.prox


# --------------------------------------------------- controle de missão
class ControleMissao:
    def __init__(self):
        self.autorizacao = FilaPrioridade()
        self.espera = Fila()
        self.alerta = ListaEncadeada()
        self.pousados = ListaEncadeada()
        self.historico = Pilha()
        self.vento, self.tau, self.enlace = 5.0, 1.0, True
        self.relogio = datetime(2026, 10, 12, 12, 0)
        # carga máxima (kg), inclinação (graus), capacidade, ocupação, interdição
        self.zonas = {"ZP-1": [40000, 2, 10, 0, False],
                      "ZP-2": [50000, 3, 10, 0, False]}

    def _log(self, msg):
        self.historico.empilhar(msg)
        print("  •", msg)

    def registrar(self, m):
        self.autorizacao.adicionar(m)
        self._log(f"Registrado: {m.nome}")

    def avaliar(self, m):
        """R01-R14 e M01. Limites didáticos, não dados reais de missão."""
        minimo = 12 + 0.5 * (m.massa_kg / 1000)
        margem = m.combustivel_pct - minimo
        carga, inclinacao, capacidade, ocupacao, interditada = self.zonas[m.zona]
        radar, imu, lidar, camera = m.sensores
        bloqueios, adiamentos, restricoes = [], [], []
        if m.combustivel_pct < minimo: bloqueios.append("R01: combustível insuficiente")
        if m.massa_kg > carga: bloqueios.append("R02: massa acima da zona")
        if inclinacao > 8: bloqueios.append("R03: inclinação excessiva")
        if radar < 70 or imu < 70: bloqueios.append("R04: sensor crítico degradado")
        if sum(valor >= 60 for valor in m.sensores) < 3:
            bloqueios.append("R05: menos de três sensores operantes")
        limite = 12 if m.tipo in ("habitação", "médico") else 18
        if self.vento > limite: adiamentos.append("R06: vento excessivo")
        if self.tau > 3: adiamentos.append("R07: tempestade de poeira")
        if interditada or ocupacao >= capacidade: adiamentos.append("R08: zona indisponível")
        if self._dependencias_ok(m): adiamentos.append("R09: dependência pendente")
        if not self.enlace: adiamentos.append("R10: enlace indisponível")
        if m.eta_orbita > self.relogio: adiamentos.append("R11: chegada futura")
        if 0 <= margem < 5: restricoes.append("R12: descida direta sem reposicionamento")
        if 2 < self.tau <= 3: restricoes.append("R13: perfil conservador")
        if lidar < 60 or camera < 60: restricoes.append("R14: reforçar navegação inercial")
        if adiamentos and margem < 3: bloqueios.append("M01: sem margem para esperar")
        if bloqueios: return "BLOQUEAR", bloqueios + adiamentos + restricoes
        elif adiamentos: return "ADIAR", adiamentos + restricoes
        elif restricoes: return "RESTRINGIR", restricoes
        else: return "AUTORIZAR", []

    def _dependencias_ok(self, m):
        return [d for d in m.dependencias if not self.pousados.contem_nome(d)]

    def processar_proximo(self):
        m = self.autorizacao.desenfileirar()
        if m is None:
            return False
        decisao, motivos = self.avaliar(m)
        m.alertas = motivos
        if decisao == "BLOQUEAR":
            m.status = "BLOQUEADO"
            self.alerta.adicionar(m)
        elif decisao == "ADIAR":
            m.status = "EM_ESPERA"
            self.espera.adicionar(m)
        else:
            m.status = "POUSADO_COM_RESTRICAO" if decisao == "RESTRINGIR" else "POUSADO"
            self.pousados.adicionar(m)
            self.zonas[m.zona][3] += 1
        self._log(f"{decisao}: {m.nome}" + (" | " + "; ".join(motivos) if motivos else ""))
        if decisao in ("AUTORIZAR", "RESTRINGIR"):
            self._reavaliar_espera()
        return True

    def _reavaliar_espera(self):
        """Devolve para a fila de autorização quem teve dependências liberadas."""
        for m in list(self.espera):
            if self.avaliar(m)[0] != "ADIAR":
                self.espera.remover(m)
                m.status = "AGUARDANDO_AUTORIZACAO"
                self.autorizacao.adicionar(m)
                self._log(f"Liberado da espera: {m.nome}")

    def atualizar_ambiente(self, vento, tau, enlace, relogio):
        self.vento, self.tau, self.enlace, self.relogio = vento, tau, enlace, relogio
        self._reavaliar_espera()

    def reabastecer_e_reavaliar(self, nome, novo_pct):
        for m in list(self.alerta):
            if m.nome == nome:
                self.alerta.remover(m)
                m.combustivel_pct, m.alertas = novo_pct, []
                m.status = "AGUARDANDO_AUTORIZACAO"
                self.autorizacao.adicionar(m)
                self._log(f"{nome} corrigido (combustível {novo_pct}%), reenfileirado")

    def relatorio(self):
        for titulo, estrutura in [("AGUARDANDO AUTORIZAÇÃO", self.autorizacao),
                                  ("EM ESPERA", self.espera),
                                  ("EM ALERTA", self.alerta),
                                  ("POUSADOS", self.pousados)]:
            print(f"\n[{titulo}] ({len(estrutura)})")
            for m in estrutura:
                extra = f"  <- {'; '.join(m.alertas)}" if m.alertas else ""
                print("  ", m, extra)


# ------------------------------------------------------------ cenário
def montar_cenario(t0):
    h = lambda x: t0 + timedelta(hours=x)
    P, C = Prioridade, Criticidade
    return [
        Modulo("Trem de Pouso",       "estrutura",  P.MAXIMA, 92, 6_500,  C.VITAL, h(1.0)),
        Modulo("Energia (Reator)",    "energia",    P.MAXIMA, 78, 12_000, C.VITAL, h(1.2), ("Trem de Pouso",)),
        Modulo("Habitação",           "habitação",  P.ALTA,   64, 18_000, C.VITAL, h(1.5), ("Energia (Reator)",)),
        Modulo("Suporte Médico",      "médico",     P.ALTA,   55, 4_200,  C.ALTA,  h(1.6), ("Habitação",)),
        Modulo("Laboratório Científico", "ciência", P.MEDIA,  47, 9_800,  C.MEDIA, h(2.0), ("Energia (Reator)",)),
        Modulo("Logística/Suprimentos", "logística", P.MEDIA, 11, 22_000, C.ALTA,  h(2.3)),   # combustível baixo
        Modulo("Rover de Exploração", "mobilidade", P.BAIXA,  70, 45_000, C.BAIXA, h(3.0)),   # massa excessiva
    ]


def busca_sequencial(modulos, tipo):
    """Busca todos os módulos de um tipo: O(n)."""
    encontrados = []
    for m in modulos:
        if m.tipo == tipo:
            encontrados.append(m)
    return encontrados


def menor_combustivel(modulos):
    menor = None
    for m in modulos:
        if menor is None or m.combustivel_pct < menor.combustivel_pct:
            menor = m
    return menor


def ordenar_insercao(modulos):
    """Insertion sort estável: prioridade, criticidade e ETA. O(n²)."""
    resultado = list(modulos)
    for i in range(1, len(resultado)):
        atual = resultado[i]
        j = i - 1
        while j >= 0 and FilaPrioridade._chave(resultado[j]) > FilaPrioridade._chave(atual):
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = atual
    return resultado


def altura_descida(t):
    """Modelo linear didático: h(t)=1000-20t, válido para 0<=t<=50 s."""
    if not 0 <= t <= 50:
        raise ValueError("Tempo fora do domínio de 0 a 50 segundos")
    return 1000 - 20 * t


def demonstracao():
    cm = ControleMissao()
    modulos = montar_cenario(datetime(2026, 10, 12, 9, 0))
    print("AURORA SIGER - MGPEB\nBusca: menor combustível:", menor_combustivel(modulos).nome)
    print("Busca por energia:", [m.nome for m in busca_sequencial(modulos, "energia")])
    print("Maior prioridade:", ordenar_insercao(modulos)[0].nome)
    for m in ordenar_insercao(modulos): cm.registrar(m)
    print("\nPrimeira rodada")
    while cm.processar_proximo(): pass
    cm.relatorio()
    print("\nCorreções simuladas: combustível da Logística e zona do Rover")
    cm.reabastecer_e_reavaliar("Logística/Suprimentos", 40)
    for m in list(cm.alerta):
        if m.nome == "Rover de Exploração":
            cm.alerta.remover(m)
            m.zona = "ZP-2"
            cm.autorizacao.adicionar(m)
    # Libera o Rover que chegou à órbita às 12h; todas as condições são reavaliadas.
    while cm.processar_proximo(): pass
    cm.relatorio()
    print("\nÚltimo evento (LIFO):", cm.historico.desempilhar())
    print("\nAltura simulada:", [(t, altura_descida(t)) for t in (0, 10, 25, 40, 50)])
    return cm


if __name__ == "__main__":
    demonstracao()
