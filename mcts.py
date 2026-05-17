import math
import random
from rollout_utils import bb_rollout, board_to_bb


class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []
        self.untried_moves = state.get_legal_moves()
        # Estado bitboard em cache — evita conversão repetida por iteração
        self._p1, self._p2, self._h = board_to_bb(state.board)

    def uct_score(self, c):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self, c):
        return max(self.children, key=lambda n: n.uct_score(c))

    def expand(self):
        move = self.untried_moves.pop()
        child = Node(self.state.apply_move(move), parent=self, move=move)
        self.children.append(child)
        return child


def backpropagate(node, result):
    result = -result
    while node:
        node.visits += 1
        node.wins += (result == 1)
        result = -result
        node = node.parent


def mcts(state, iterations=1000, c=math.sqrt(2)):
    root = Node(state)

    for _ in range(iterations):
        node = root

        while not node.untried_moves and node.children:
            node = node.best_child(c)

        if node.untried_moves and not node.state.is_terminal():
            node = node.expand()

        # Rollout aleatório puro — greedy=False distingue v1 das versões seguintes
        result = bb_rollout(node._p1, node._p2, node._h,
                            node.state.current_player, node.state.last_move,
                            greedy=False)
        backpropagate(node, result)

    return max(root.children, key=lambda n: n.visits)
