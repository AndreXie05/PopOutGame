'''Simula a jogada
Vê todas as respostas do adversário
Se alguma dá vitória -> Evita essas jogadas'''

import math
import random


class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state              # estado do jogo neste nó
        self.parent = parent            # nó pai
        self.move = move                # jogada que levou a este nó

        self.children = []              # filhos já expandidos
        self.wins = 0                   # número de vitórias / reward acumulada
        self.visits = 0                 # número de visitas

        self.untried_moves = state.get_legal_moves()  # jogadas ainda não exploradas

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c=math.sqrt(2)):
        best_score = -float("inf")
        best_node = None

        for child in self.children:
            exploitation = child.wins / child.visits
            exploration = c * math.sqrt(math.log(self.visits) / child.visits)
            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_node = child

        return best_node

    def expand(self):
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)

        next_state = self.state.apply_move(move)
        child = Node(next_state, parent=self, move=move)

        self.children.append(child)
        return child


def select(node):
    while not node.state.is_terminal():
        if not node.is_fully_expanded():
            return node
        else:
            node = node.best_child()
    return node


def rollout(state):
    current_state = state

    while not current_state.is_terminal():
        legal_moves = current_state.get_legal_moves()

        safe_moves = []

        for move in legal_moves:
            temp_state = current_state.apply_move(move)

            # ver se o adversário ganha logo a seguir
            opponent_moves = temp_state.get_legal_moves()
            opponent_wins = False

            for opp_move in opponent_moves:
                next_state = temp_state.apply_move(opp_move)
                if next_state.check_four_in_a_row(3 - current_state.current_player):
                    opponent_wins = True
                    break

            if not opponent_wins:
                safe_moves.append(move)

        # usar apenas jogadas seguras se existirem
        if safe_moves:
            move = random.choice(safe_moves)
        else:
            move = random.choice(legal_moves)

        current_state = current_state.apply_move(move)

    return current_state.get_result(state.current_player)


def backpropagate(node, result):
    while node is not None:
        node.visits += 1
        node.wins += result
        node = node.parent


def mcts(root_state, iterations=1000):
    root = Node(root_state)

    for _ in range(iterations):
        # 1. Selection
        node = select(root)

        # 2. Expansion
        if not node.state.is_terminal():
            node = node.expand()

        # 3. Simulation
        result = rollout(node.state)

        # 4. Backpropagation
        backpropagate(node, result)

    # Escolha final: filho da raiz com mais visitas
    return max(root.children, key=lambda child: child.visits)