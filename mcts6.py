"""
MCTS v6 — Política heurística de seleção de candidatos.

Inspirado no AlphaGo: antes de iniciar a pesquisa MCTS, uma função de
política pontua cada jogada candidata e selecciona apenas as K melhores.

Diferença face a v5:
  v5 → explora até 5 jogadas por ordem de centralidade
  v6 → pontua TODAS as jogadas seguras por alinhamentos criados/destruídos
       e explora apenas as top K (padrão K=3)

Vantagem: menos ramos → mais iterações por ramo → estimativas mais precisas.
A perda é que podemos excluir jogadas boas que a heurística sub-avalia.
"""
import math
import random
from rollout_utils import bb_rollout, board_to_bb, COL_MASKS, BOTTOM_BITS, ROWS, COLS


# ---------------------------------------------------------------------------
# Funções da política heurística
# ---------------------------------------------------------------------------

def _bb_after_move(p1, p2, h, move, player):
    """
    Aplica uma jogada ao bitboard e devolve (p1_novo, p2_novo).
    Não modifica os argumentos. Não precisa de actualizar heights
    porque a política só avalia alinhamentos, não validade de jogadas.
    """
    col, mtype = move
    if mtype == 'drop':
        bit = (ROWS - 1 - h[col]) * COLS + col
        if player == 1: return p1 | (1 << bit), p2
        else:           return p1, p2 | (1 << bit)
    else:   # pop — desloca coluna
        cm  = COL_MASKS[col]
        bd  = BOTTOM_BITS[col]
        p1c = ((p1 & cm & ~bd) << COLS) & cm
        p2c = ((p2 & cm & ~bd) << COLS) & cm
        return (p1 & ~cm) | p1c, (p2 & ~cm) | p2c


def _count_alignments(bb):
    """
    Conta formações de 2 e 3 em linha no bitboard (todas as direcções).

    Usa o mesmo truque dos bitboards de vitória: bb & (bb >> k) detecta
    pares separados por k posições. Uma tripla é um par que continua.

    Pesos: triple vale 4× mais que pair — representa uma ameaça concreta.
    """
    score = 0
    for shift in (1, COLS, COLS + 1, COLS - 1):
        pairs   = bb & (bb >> shift)
        triples = pairs & (bb >> (2 * shift))
        score  += pairs.bit_count() + triples.bit_count() * 4
    return score


def _policy_score(p1, p2, h, move, player):
    """
    Pontua uma jogada: alinhamentos criados para mim menos alinhamentos
    deixados ao adversário (com peso 1.5 — bloquear é ligeiramente mais
    importante do que atacar).
    """
    np1, np2 = _bb_after_move(p1, p2, h, move, player)
    my_bb  = np1 if player == 1 else np2
    opp_bb = np2 if player == 1 else np1
    return _count_alignments(my_bb) - int(_count_alignments(opp_bb) * 1.5)


# ---------------------------------------------------------------------------
# Nó da árvore MCTS
# ---------------------------------------------------------------------------

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []
        self.untried_moves = []
        self._p1, self._p2, self._h = board_to_bb(state.board)

    def uct_score(self, c):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self, c):
        return max(self.children, key=lambda n: n.uct_score(c))

    def expand(self):
        move = self.untried_moves.pop(0)
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


# ---------------------------------------------------------------------------
# MCTS com política
# ---------------------------------------------------------------------------

def mcts(state, iterations=2000, c=1.414, max_candidates=5):
    """
    Executa MCTS com pré-selecção de candidatos por heurística.

    Passos:
      1. Reflexo de ataque (igual a v5)
      2. Filtro de segurança (igual a v5)
      3. NOVO — Política: pontua os candidatos seguros e escolhe os K melhores
      4. MCTS só sobre esses K candidatos
    """
    legal = state.get_legal_moves()

    # Reflexo de ataque: vitória imediata não precisa de pesquisa
    for m in legal:
        if state.apply_move(m).get_winner() == state.current_player:
            return Node(state.apply_move(m), move=m)

    # Filtro de segurança
    safe = []
    for m in legal:
        ns = state.apply_move(m)
        if not any(ns.apply_move(opp).get_winner() == ns.current_player
                   for opp in ns.get_legal_moves()):
            safe.append(m)
    candidates = safe if safe else legal

    # Política: pontua cada candidato e selecciona os K melhores
    p1, p2, h = board_to_bb(state.board)
    scored = sorted(
        candidates,
        key=lambda m: _policy_score(p1, p2, h, m, state.current_player),
        reverse=True
    )
    top_k = scored[:max_candidates]

    # MCTS apenas sobre os top_k candidatos
    root = Node(state)
    root.untried_moves = list(top_k)

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
        fallback = top_k[0] if top_k else random.choice(legal)
        return Node(state.apply_move(fallback), move=fallback)

    best = sorted(root.children, key=lambda n: n.visits, reverse=True)

    # Temperatura na abertura
    pieces = sum(cell != 0 for row in state.board for cell in row)
    if pieces < 6 and len(best) >= 2:
        return random.choice(best[:2])
    return best[0]


def get_best_move(state, iterations=2000, c=1.414, max_candidates=5):
    return mcts(state, iterations, c, max_candidates).move
