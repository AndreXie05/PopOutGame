def _build_win_patterns_2d(rows=6, cols=7):
    """
    Pré-computa os 69 padrões de vitória como tuplos de coordenadas (r, c).
    Executado uma única vez na definição da classe — elimina loops aninhados
    em tempo de jogo.
    """
    p = []
    # Horizontal (24)
    for r in range(rows):
        for c in range(cols - 3):
            p.append(((r, c), (r, c+1), (r, c+2), (r, c+3)))
    # Vertical (21)
    for r in range(rows - 3):
        for c in range(cols):
            p.append(((r, c), (r+1, c), (r+2, c), (r+3, c)))
    # Diagonal ↘ (12)
    for r in range(rows - 3):
        for c in range(cols - 3):
            p.append(((r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)))
    # Diagonal ↗ (12)
    for r in range(3, rows):
        for c in range(cols - 3):
            p.append(((r, c), (r-1, c+1), (r-2, c+2), (r-3, c+3)))
    return p


class PopOutBoard:
    __slots__ = ['rows', 'cols', 'board', 'current_player', 'last_move']

    ROWS = 6
    COLS = 7
    # 69 padrões pré-computados: acesso directo sem recalcular ranges em runtime
    WIN_PATTERNS = _build_win_patterns_2d()

    def __init__(self):
        self.rows = self.ROWS
        self.cols = self.COLS
        # 0 = vazio, 1 = X (Jogador 1), 2 = O (Jogador 2)
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.current_player = 1   # Começa com o Jogador 1 (X)
        self.last_move = None

    def display(self):
        print("\n  0   1   2   3   4   5   6")
        print("+---" * self.cols + "+")
        for r in range(self.rows):
            row_str = "|"
            for c in range(self.cols):
                char = " "
                if self.board[r][c] == 1: char = "X"
                if self.board[r][c] == 2: char = "O"
                row_str += f" {char} |"
            print(row_str)
            print("+---" * self.cols + "+")
        if self.get_winner() is None:
            print(f"Vez do Jogador: {'X' if self.current_player == 1 else 'O'}\n")
        else:
            print("FIM DE JOGO\n")

    def is_valid_move(self, col, move_type):
        if col < 0 or col >= self.cols:
            return False
        if move_type == 'drop':
            return self.board[0][col] == 0
        elif move_type == 'pop':
            return self.board[self.rows - 1][col] == self.current_player
        return False

    def get_legal_moves(self):
        moves = []
        for c in range(self.cols):
            if self.is_valid_move(c, 'drop'): moves.append((c, 'drop'))
            if self.is_valid_move(c, 'pop'):  moves.append((c, 'pop'))
        return moves

    def apply_move(self, move):
        col, move_type = move
        new_state = PopOutBoard.__new__(PopOutBoard)
        new_state.rows = self.rows
        new_state.cols = self.cols
        new_state.board = [row[:] for row in self.board]   # cópia sem deepcopy
        new_state.current_player = self.current_player
        new_state.last_move = self.last_move

        if move_type == 'drop':
            for r in range(self.rows - 1, -1, -1):
                if new_state.board[r][col] == 0:
                    new_state.board[r][col] = self.current_player
                    break
        elif move_type == 'pop':
            for r in range(self.rows - 1, 0, -1):
                new_state.board[r][col] = new_state.board[r - 1][col]
            new_state.board[0][col] = 0

        new_state.last_move = move
        new_state.current_player = 3 - self.current_player   # alterna jogador
        return new_state

    def check_four_in_a_row(self, p_value):
        """Usa padrões pré-computados — elimina loops aninhados e chamadas a range()."""
        b = self.board
        for (r0, c0), (r1, c1), (r2, c2), (r3, c3) in self.WIN_PATTERNS:
            if (b[r0][c0] == p_value and b[r1][c1] == p_value
                    and b[r2][c2] == p_value and b[r3][c3] == p_value):
                return True
        return False

    def get_winner(self):
        p1_win = self.check_four_in_a_row(1)
        p2_win = self.check_four_in_a_row(2)

        # Regra 1: se ambos ficarem com 4 após um pop, quem fez o pop ganha
        if self.last_move and self.last_move[1] == 'pop':
            if p1_win and p2_win:
                return 3 - self.current_player

        if p1_win: return 1
        if p2_win: return 2
        return None

    def is_terminal(self):
        if self.get_winner() is not None:
            return True
        return len(self.get_legal_moves()) == 0

    def get_result(self, player):
        winner = self.get_winner()
        if winner is None:   return 0
        if winner == player: return 1
        return -1

    def to_flat(self):
        """Converte o tabuleiro para lista plana de 42 elementos (para rollout rápido)."""
        return [cell for row in self.board for cell in row]
