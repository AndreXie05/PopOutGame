# Projeto de IA: PopOut (MCTS & Decision Tree)

---

## Autores

André Chen Xie, Beatriz Morais Vieira, Manuel Henrique da Silva Mota 
*Inteligência Artificial e Ciências de Dados* 
**Data:** 26 de abril de 2026

## Descrição do Projeto

Implementação de um agente capaz de jogar **PopOut** (uma variante do Connect-4) utilizando técnicas de Procura Adversarial (Monte Carlo Tree Search) e Aprendizagem Supervisionada (Árvores de Decisão - ID3)

## Regras e Mecânica de Jogo:

O PopOut segue a abse do Connect-4, mas com mecânicas adicionais que aumentam a complexidade estratégica:
  -> **Drop**: Jogar uma peça no topo de uma coluna, caindo até a posição livre mais baixa.
  -> **Pop**: Remover uma peça da própria cor da base do tabuleiro. Como consequência, todas as peças acima dessa coluna descem uma posição.

Regras Especiais:
  -> **Regra 1**: Se um Pop resultar em quatro em linha, para ambos os jogadores simultaneamente, a vitória é atribuída ao jogador que fez o Pop.
  -> **Regra 2**: Se um tabuleiro estiver cheio, o jogador da vez tem a opção de empate ou de continuar a jogar, fazendo Pop.
  -> **Regra 3**: Se um estado repetir 3 vezes, o jogo termina empatado.

Modos de jogo:
  -> **Modo 1**: Humano vs IA (MCTS5)
  -> **Modo 2**: Humano vs IA (DT)
  -> **Modo 3**: IA (MCTS5) vs IA (DT)
  -> **Modo 4**: Humano vs Humano
  -> **Modo 5**: IA (MCTS5) vs IA (MCTS5)

```bash
# 1. Instalar dependencias
pip install numpy graphviz

# 2. Como executar
# Gerar os dados de treino (Pipeline MCTS)
python gerar_dados.py

# Treinar e Avaliar a Árvore de Decisão (ID3)
python popout_ID3_Tree.py

# Iniciar menu princial
python main.py

```

## Como jogar:
  -> Selecionar a coluna (0-6)
  -> Se pretende fazer Drop ('**d**') ou se pretende fazer Pop ('**p**')