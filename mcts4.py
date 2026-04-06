'''mcts3 demorava muito, porque verificavas todas as jogadase todas as respostas -> fazia tipo um minimax O(n**2)
agora, joga assim que encontras uma jogada segura -> O(n)
filtro na raiz (retira movimentos que dão a vitória ao opponent de forma imediata) e no rollout (corta jogadas nas simulações que dão derrota imediata)
'''

'''PROBLEMA:
não trata bem do pop. o pop, por mover várias peças estraga a estratégia de ver só o proximo movimento
'''

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

        random.shuffle(legal_moves)  # evitar padrões

        move_escolhido = None

        for move in legal_moves:
            temp_state = current_state.apply_move(move)

            # verifica só se existe UMA resposta vencedora do adversário
            opponent_can_win = False

            for opp_move in temp_state.get_legal_moves():
                next_state = temp_state.apply_move(opp_move)

                if next_state.check_four_in_a_row(temp_state.current_player):
                    opponent_can_win = True
                    break

            # escolhe a primeira jogada segura
            if not opponent_can_win:
                move_escolhido = move
                break

        # fallback
        if move_escolhido is None:
            move_escolhido = random.choice(legal_moves)

        current_state = current_state.apply_move(move_escolhido)

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

    safe_children = []

    for child in root.children:
        temp_state = child.state

        opponent_moves = temp_state.get_legal_moves()
        opponent_wins = False

        for opp_move in opponent_moves:
            next_state = temp_state.apply_move(opp_move)

            if next_state.check_four_in_a_row(temp_state.current_player):
                opponent_wins = True
                break

        if not opponent_wins:
            safe_children.append(child)

    # escolher apenas entre jogadas seguras
    if safe_children:
        return max(safe_children, key=lambda child: child.visits)
    else:
        return max(root.children, key=lambda child: child.visits)