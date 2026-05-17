import math
import random
from rollout_utils import bb_rollout, board_to_bb


class Node:
    def __init__(self, state, parent=None, move=None, max_children=5):
        self.state = state
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []
        self.max_children = max_children
        self._p1, self._p2, self._h = board_to_bb(state.board)

        moves = state.get_legal_moves()
        center = len(state.board[0]) // 2
        moves.sort(key=lambda m: abs(m[0] - center))
        self.untried_moves = moves[:max_children]

    def uct_score(self, c):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self, c):
        return max(self.children, key=lambda n: n.uct_score(c))

    def expand(self):
        move = self.untried_moves.pop(0)
        child = Node(self.state.apply_move(move), parent=self, move=move,
                     max_children=self.max_children)
        self.children.append(child)
        return child


def backpropagate(node, result):
    result = -result
    while node:
        node.visits += 1
        node.wins += (result == 1)
        result = -result
        node = node.parent


def mcts(state, iterations=2000, c=1.414, max_children=5):
    legal = state.get_legal_moves()

    # Reflexo de ataque: vitória imediata
    for m in legal:
        if state.apply_move(m).get_winner() == state.current_player:
            return Node(state.apply_move(m), move=m)

    # Filtro de segurança: remove jogadas que dão vitória imediata ao adversário
    safe = []
    for m in legal:
        ns = state.apply_move(m)
        if not any(ns.apply_move(opp).get_winner() == ns.current_player
                   for opp in ns.get_legal_moves()):
            safe.append(m)
    candidates = safe if safe else legal

    # Ordena por proximidade ao centro e limita o nº de candidatos
    center = len(state.board[0]) // 2
    candidates.sort(key=lambda m: abs(m[0] - center))

    root = Node(state, max_children=max_children)
    root.untried_moves = candidates[:max_children]

    for _ in range(iterations):
        node = root
        while not node.untried_moves and node.children:
            node = node.best_child(c)
        if node.untried_moves and not node.state.is_terminal():
            node = node.expand()
        result = bb_rollout(node._p1, node._p2, node._h,
                            node.state.current_player, node.state.last_move)
        backpropagate(node, result)

    if not root.children:
        fallback = candidates[0] if candidates else random.choice(legal)
        return Node(state.apply_move(fallback), move=fallback)

    best = sorted(root.children, key=lambda n: n.visits, reverse=True)

    # Temperatura na abertura: diversidade para o dataset do ID3
    pieces = sum(cell != 0 for row in state.board for cell in row)
    if pieces < 6 and len(best) >= 2:
        return random.choice(best[:2])
    return best[0]


def get_best_move(state, iterations=2000, c=1.414, max_children=5):
    return mcts(state, iterations, c, max_children).move
