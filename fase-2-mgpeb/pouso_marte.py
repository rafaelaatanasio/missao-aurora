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
    COMBUSTIVEL_MINIMO = 15.0       # abaixo disso: alerta
    MASSA_MAXIMA_KG = 40_000        # acima disso: alerta de massa

    def __init__(self):
        self.autorizacao = FilaPrioridade()   # aguardando autorização de pouso
        self.espera = Fila()                  # bloqueados por dependência
        self.alerta = ListaEncadeada()        # situação de alerta
        self.pousados = ListaEncadeada()      # pouso concluído
        self.historico = Pilha()              # log (mais recente no topo)

    def _log(self, msg):
        self.historico.empilhar(msg)
        print("  •", msg)

    def registrar(self, m):
        self.autorizacao.adicionar(m)
        self._log(f"Registrado: {m.nome}")

    def _verificar(self, m):
        """Retorna lista de falhas de segurança (vazia = apto)."""
        falhas = []
        if m.combustivel_pct < self.COMBUSTIVEL_MINIMO:
            falhas.append(f"combustível {m.combustivel_pct:.1f}% < {self.COMBUSTIVEL_MINIMO}%")
        if m.massa_kg > self.MASSA_MAXIMA_KG:
            falhas.append(f"massa {m.massa_kg:.0f}kg > {self.MASSA_MAXIMA_KG}kg")
        return falhas

    def _dependencias_ok(self, m):
        return [d for d in m.dependencias if not self.pousados.contem_nome(d)]

    def processar_proximo(self):
        m = self.autorizacao.desenfileirar()
        if m is None:
            return False
        falhas = self._verificar(m)
        if falhas:
            m.status, m.alertas = "ALERTA", falhas
            self.alerta.adicionar(m)
            self._log(f"ALERTA {m.nome}: {'; '.join(falhas)}")
            return True
        pendentes = self._dependencias_ok(m)
        if pendentes:
            m.status = "EM_ESPERA"
            self.espera.adicionar(m)
            self._log(f"ESPERA {m.nome}: aguarda {', '.join(pendentes)}")
            return True
        self._pousar(m)
        self._reavaliar_espera()
        return True

    def _pousar(self, m):
        m.status = "POUSADO"
        self.pousados.adicionar(m)
        self._log(f"POUSO AUTORIZADO e concluído: {m.nome}")

    def _reavaliar_espera(self):
        """Devolve para a fila de autorização quem teve dependências liberadas."""
        for m in list(self.espera):
            if not self._dependencias_ok(m):
                self.espera.remover(m)
                m.status = "AGUARDANDO_AUTORIZACAO"
                self.autorizacao.adicionar(m)
                self._log(f"Liberado da espera: {m.nome}")

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


if __name__ == "__main__":
    t0 = datetime(2026, 10, 12, 9, 0)
    cm = ControleMissao()
    print("== Registro dos módulos ==")
    for mod in montar_cenario(t0):
        cm.registrar(mod)

    print("\n== Processamento da fila de autorização ==")
    while cm.processar_proximo():
        pass

    print("\n== Situação após 1ª rodada ==")
    cm.relatorio()

    print("\n== Ação corretiva: reabastecimento da Logística ==")
    cm.reabastecer_e_reavaliar("Logística/Suprimentos", 40)
    while cm.processar_proximo():
        pass

    print("\n== Situação final ==")
    cm.relatorio()

    print("\n== Últimos 5 eventos (pilha) ==")
    for i, ev in enumerate(cm.historico):
        if i == 5:
            break
        print("  ", ev)
