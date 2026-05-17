"""
Rollout com bitboards.

O tabuleiro de cada jogador é representado como um único inteiro Python de 42 bits.
Cada bit i corresponde à célula (linha i//7, coluna i%7).

Vantagem principal: a detecção de vitória usa 4 operações bitwise em vez de
percorrer 69 padrões — cada direcção é resolvida em 3 operações sobre inteiros.
"""
import random

ROWS, COLS = 6, 7


# ---------------------------------------------------------------------------
# Pré-computação de máscaras (executada uma única vez no arranque)
# ---------------------------------------------------------------------------

def _precompute():
    # Posições válidas de início de 4-em-linha por direcção
    # (a máscara filtra resultados espúrios nas bordas do tabuleiro)
    MASK_H  = sum(1 << (r*COLS+c) for r in range(ROWS)   for c in range(COLS-3))  # horizontal
    MASK_V  = sum(1 << (r*COLS+c) for r in range(ROWS-3) for c in range(COLS))    # vertical
    MASK_D1 = sum(1 << (r*COLS+c) for r in range(ROWS-3) for c in range(COLS-3))  # diagonal ↘
    MASK_D2 = sum(1 << (r*COLS+c) for r in range(ROWS-3) for c in range(3, COLS)) # diagonal ↗

    # Máscara de cada coluna (todos os bits dessa coluna)
    COL_MASKS   = [sum(1 << (r*COLS+c) for r in range(ROWS)) for c in range(COLS)]
    # Bit da linha de base (linha 5) por coluna — necessário para verificar pop
    BOTTOM_BITS = [1 << ((ROWS-1)*COLS + c) for c in range(COLS)]

    return MASK_H, MASK_V, MASK_D1, MASK_D2, COL_MASKS, BOTTOM_BITS


MASK_H, MASK_V, MASK_D1, MASK_D2, COL_MASKS, BOTTOM_BITS = _precompute()


# ---------------------------------------------------------------------------
# Detecção de vitória — O(1), ~8 operações bitwise para as 4 direcções
# ---------------------------------------------------------------------------

def bb_check_win(bb):
    """
    Verifica se o bitboard bb contém 4 em linha em qualquer direcção.

    Truque: bb & (bb >> k) dá '1' nas posições onde existem dois bits
    separados exactamente k posições. Aplicando duas vezes (offsets 0 e 2k),
    detectamos 4 consecutivos. Uma máscara elimina falsos positivos nas bordas.

    Horizontal  : k=1  (colunas adjacentes)
    Vertical    : k=7  (linhas adjacentes)
    Diagonal ↘  : k=8  (linha+1, coluna+1)
    Diagonal ↗  : k=6  (linha+1, coluna-1)
    """
    m = bb & (bb >> 1)
    if m & (m >> 2) & MASK_H:  return True
    m = bb & (bb >> COLS)
    if m & (m >> (2*COLS)) & MASK_V:  return True
    m = bb & (bb >> (COLS + 1))
    if m & (m >> (2*(COLS + 1))) & MASK_D1:  return True
    m = bb & (bb >> (COLS - 1))
    if m & (m >> (2*(COLS - 1))) & MASK_D2:  return True
    return False


# ---------------------------------------------------------------------------
# Conversores
# ---------------------------------------------------------------------------

def board_to_bb(board_2d):
    """
    Converte tabuleiro 2D → (p1_bits, p2_bits, heights).
    heights[c] = número de peças na coluna c (as peças estão compactadas na base).
    """
    p1, p2 = 0, 0
    heights = [0] * COLS
    for c in range(COLS):
        for r in range(ROWS - 1, -1, -1):   # da base para o topo
            v = board_2d[r][c]
            if v == 0:
                break
            heights[c] += 1
            bit = r * COLS + c
            if v == 1: p1 |= (1 << bit)
            else:      p2 |= (1 << bit)
    return p1, p2, heights


def board_to_flat(board_2d):
    """Lista plana de 42 elementos — usada para serialização nos workers."""
    return [cell for row in board_2d for cell in row]


def flat_to_board_2d(flat):
    """Lista plana → tabuleiro 2D (6x7)."""
    return [[flat[r * COLS + c] for c in range(COLS)] for r in range(ROWS)]


# ---------------------------------------------------------------------------
# Rollout principal com bitboard
# ---------------------------------------------------------------------------

def bb_rollout(p1_in, p2_in, heights_in, player, last_move, greedy=True):
    """
    Simula um jogo completo a partir do estado dado. Não altera os argumentos.

    greedy=True  : antes de jogar aleatoriamente, verifica se existe uma
                   jogada vencedora imediata (melhor qualidade, padrão v2–v5).
    greedy=False : escolha puramente aleatória (v1).

    Retorna: +1 se 'player' ganhar, -1 se perder, 0 se empate.
    """
    p1, p2 = p1_in, p2_in
    h = heights_in[:]   # cópia local de 7 inteiros — barata
    orig = player
    lm = last_move

    while True:
        pp = p1 if player == 1 else p2   # peças do jogador actual

        # Gerar jogadas legais
        moves = []
        for c in range(COLS):
            if h[c] < ROWS:          moves.append((c, 'drop'))
            if pp & BOTTOM_BITS[c]:  moves.append((c, 'pop'))
        if not moves:
            break

        # Verificar vitória imediata (greedy)
        chosen = None
        if greedy:
            for col, mtype in moves:
                if mtype == 'drop':
                    # Coloca peça temporariamente e verifica — 1 OR + win check
                    test_bit = 1 << ((ROWS - 1 - h[col]) * COLS + col)
                    if bb_check_win(pp | test_bit):
                        chosen = (col, mtype); break
                else:
                    # Simula pop apenas para a coluna do jogador actual
                    cm = COL_MASKS[col]
                    pp_col_shifted = ((pp & cm & ~BOTTOM_BITS[col]) << COLS) & cm
                    if bb_check_win((pp & ~cm) | pp_col_shifted):
                        chosen = (col, mtype); break

        if chosen is None:
            chosen = random.choice(moves)

        col, mtype = chosen

        # Aplicar jogada ao estado
        if mtype == 'drop':
            bit = (ROWS - 1 - h[col]) * COLS + col
            if player == 1: p1 |= (1 << bit)
            else:           p2 |= (1 << bit)
            h[col] += 1
        else:   # pop — desloca toda a coluna para baixo uma linha
            cm  = COL_MASKS[col]
            bd  = BOTTOM_BITS[col]
            p1c = ((p1 & cm & ~bd) << COLS) & cm
            p2c = ((p2 & cm & ~bd) << COLS) & cm
            p1  = (p1 & ~cm) | p1c
            p2  = (p2 & ~cm) | p2c
            h[col] -= 1

        lm     = (col, mtype)
        player = 3 - player

        # Verificar vencedor
        p1w = bb_check_win(p1)
        p2w = bb_check_win(p2)
        if lm[1] == 'pop' and p1w and p2w:
            # Regra 1: ambos com 4 após pop → quem fez o pop ganha
            winner = 3 - player
            return 1 if winner == orig else -1
        if p1w: return 1 if orig == 1 else -1
        if p2w: return 1 if orig == 2 else -1

    return 0   # empate (sem jogadas disponíveis)
