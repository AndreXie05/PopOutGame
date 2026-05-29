# AI Project: PopOut (MCTS & Decision Tree)

---

## Authors

- André Chen Xie
- Beatriz Morais Vieira
- Manuel Henrique da Silva Mota 

## Course

*Artificial Intelligence and Data Science* 

## Project Description

Implementation of an AI agent capable of playing **PopOut** (a variant of Connect-4) using Adversarial Search techniques (Monte Carlo Tree Search) and Supervised Learning (Decision Trees - ID3).

## Rules and Game Mechanics

PopOut follows the core mechanics of Connect-4 but introduces additional features that increase strategic complexity:
- **Drop**: Place a piece at the top of a column, falling to the lowest available position.
- **Pop**: Remove a piece of your own color from the bottom row of the board. As a consequence, all pieces above it in that column shift down by one position.

*Special Rules:*
- **Rule 1**: If a *Pop* results in a line of four for both players simultaneously, the victory is awarded to the player who made the *Pop*.
- **Rule 2**: If the board is completely full, the player whose turn it is has the option to accept a draw or continue playing by performing a *Pop*.
- **Rule 3**: If the exact same board state is repeated 3 times, the game ends in a draw.

*Game Modes:*
- **Mode 1**: Human vs AI (MCTS5)
- **Mode 2**: Human vs AI (DT)
- **Mode 3**: AI (MCTS5) vs AI (DT)
- **Mode 4**: Human vs Human
- **Mode 5**: AI (MCTS5) vs AI (MCTS5)

```bash
# 1. Install dependencies
pip install numpy graphviz

# 2. How to run
# Generate training data (MCTS Pipeline)
python gerar_dados.py

# Train and Evaluate the Decision Tree (ID3)
python popout_ID3_Tree.py

# Launch the main menu
python main.py
