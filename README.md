# 🚀 Missão Aurora Siger

Projeto acadêmico contínuo do curso de **Ciência da Computação da FIAP**, desenvolvido pelo **Grupo 37**.

A cada fase do curso, a nave Aurora Siger avança uma etapa da missão a Marte, e o grupo constrói um novo módulo computacional que aplica os conteúdos estudados naquela fase.

> Todos os valores e limites utilizados são premissas acadêmicas definidas pelo grupo para fins de simulação.

---

## 🧭 Fases da missão

| Fase | Etapa da missão | Módulo | Conteúdos aplicados |
|---|---|---|---|
| [**Fase 1**](fase-1-pre-decolagem/) | Pré-decolagem na Terra | Relatório Operacional de Pré-Decolagem (GO / NOT-GO) | Lógica booleana, algoritmos, Python, análise energética, IA como apoio, ética e sustentabilidade |
| [**Fase 2**](fase-2-mgpeb/) | Pouso em Marte | MGPEB — Gerenciamento de Pouso e Estabilização de Base | Portas lógicas, listas, filas e pilhas, busca e ordenação, funções matemáticas, evolução da computação, ESG |
| [**Fase 3**](fase-3-sistemas-colonia/) | Primeiros sistemas da colônia | Sistema integrado: dados, decisões e previsão | Hierarquia e chave-valor, regras de decisão, regressão linear, energia solar e eólica |

### Fase 1 · Pré-decolagem

Verifica a telemetria da nave (integridade estrutural, energia, pressão dos tanques, módulos críticos e temperaturas) e decide **GO PARA LANÇAMENTO** ou **NOT-GO**. Inclui uma análise energética da decolagem e uma análise dos resultados assistida por IA.

➡️ [Ver a Fase 1](fase-1-pre-decolagem/)

### Fase 2 · MGPEB

Organiza o pouso de sete módulos da colônia em Marte usando estruturas de dados implementadas manualmente (fila de prioridade, fila FIFO, listas encadeadas e pilha). Cada módulo passa por 14 regras de segurança e uma meta-regra, que decidem entre **autorizar**, **restringir**, **adiar** ou **bloquear** o pouso.

➡️ [Ver a Fase 2](fase-2-mgpeb/)

### Fase 3 · Sistemas da colônia

Organiza a colônia como uma hierarquia de sistemas (energia → solar / eólica / baterias, suporte à vida, comunicação...), prevê geração e consumo com regressão linear, compara geração, consumo e reserva, e decide automaticamente a ação e quais sistemas ficam ligados. Exemplo: energia = 40% e consumo = 70% → **ALERTA: ativar modo economia**.

➡️ [Ver a Fase 3](fase-3-sistemas-colonia/)

---

## 📁 Estrutura do repositório

```
missao-aurora/
├── README.md                  ← esta página
├── fase-1-pre-decolagem/      ← notebook, script, relatório e prints da Fase 1
├── fase-2-mgpeb/              ← protótipo MGPEB, relatório, regras e prints da Fase 2
└── fase-3-sistemas-colonia/   ← sistema integrado da colônia, testes e prints da Fase 3
```

Cada pasta tem seu próprio README, com a explicação do módulo, as instruções de execução e as evidências.

---

## 🛠️ Tecnologias utilizadas

- Python 3 (apenas biblioteca padrão)
- Jupyter Notebook
- Visual Studio Code
- GitHub
- Inteligência Artificial como ferramenta de apoio

---

## 👥 Integrantes — Grupo 37

- **Enzo Yugi Kloiwa** — RM 574398
- **Guilherme de Souza Santos** — RM 574908
- **Luke Malaquias Lage** — RM 574356
- **Rafaela Aparecida dos Santos Atanásio** — RM 574868
- **Yasmin Sampaio Barbieri** — RM 576282

---

## 📚 Sobre o projeto

Este projeto possui finalidade exclusivamente acadêmica e foi desenvolvido como parte do curso de Ciência da Computação da FIAP.

O estado do repositório entregue na Fase 1 está preservado na branch [`entrega-fase-1`](https://github.com/rafaelaatanasio/missao-aurora/tree/entrega-fase-1).
