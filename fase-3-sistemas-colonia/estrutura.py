"""
ESTRUTURA: funções para navegar na hierarquia da colônia.

A colônia é uma árvore de dicionários. A raiz é a colônia, os filhos são
os sistemas (energia, suporte à vida...) e os netos são os subsistemas
(solar, eólica, baterias...). Um caminho como "energia/geracao/solar"
desce um nível a cada parte.
"""


def navegar(arvore, caminho):
    """
    Desce na árvore seguindo o caminho e devolve o nó encontrado.
    Exemplo: navegar(COLONIA, "energia/geracao/solar")
    """
    no = arvore
    if not caminho:
        return no
    for parte in caminho.split("/"):
        filhos = no.get("subsistemas", {})
        if parte not in filhos:
            opcoes = ", ".join(filhos) or "nenhum (fim da árvore)"
            raise KeyError(f"'{parte}' não existe aqui. Opções: {opcoes}")
        no = filhos[parte]
    return no


def listar_subsistemas(no):
    """Devolve os nomes dos filhos diretos de um nó."""
    return list(no.get("subsistemas", {}))


def mostrar_arvore(no, chave="colonia", nivel=0):
    """
    Percorre a árvore de forma recursiva e devolve uma lista de linhas
    com indentação, para imprimir a hierarquia.
    """
    linhas = ["    " * nivel + f"- {no['nome']} [{chave}]"]
    for filho_chave, filho in no.get("subsistemas", {}).items():
        linhas.extend(mostrar_arvore(filho, filho_chave, nivel + 1))
    return linhas


def somar_campo(no, campo):
    """
    Soma um campo numérico em todo o ramo (o nó e todos os descendentes).
    Exemplo: somar_campo(navegar(COLONIA, "energia/geracao"), "geracao_kwh")
    """
    total = no.get(campo, 0)
    for filho in no.get("subsistemas", {}).values():
        total += somar_campo(filho, campo)
    return total


def consumidores_por_prioridade(colonia):
    """
    Devolve os sistemas consumidores (os que têm 'prioridade'), do mais
    importante para o menos importante, como lista de tuplas
    (nome, prioridade, energia_minima).
    """
    consumidores = []
    for no in colonia["subsistemas"].values():
        if "prioridade" in no:
            consumidores.append((no["nome"], no["prioridade"], no["energia_minima"]))
    consumidores.sort(key=lambda item: item[1])
    return consumidores
