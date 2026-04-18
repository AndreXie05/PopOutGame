import copy

class PopOutBoard:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        # 0 = vazio, 1 = X (Jogador 1), 2 = O (IA)
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 1 # Começamos com 1 (X)
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
            # Se houver um vencedor ou empate, não mostra a vez
            print("FIM DE JOGO\n")
        
    def is_valid_move(self, col, move_type):
        if col < 0 or col >= self.cols: return False
        
        if move_type == 'drop':
            # Válido se o topo da coluna estiver vazio (0)
            return self.board[0][col] == 0
        elif move_type == 'pop':
            # Válido se a peça na base for do jogador atual
            return self.board[self.rows - 1][col] == self.current_player
        return False

    def get_legal_moves(self):
        moves = []
        for c in range(self.cols):
            if self.is_valid_move(c, 'drop'): moves.append((c, 'drop'))
            if self.is_valid_move(c, 'pop'): moves.append((c, 'pop'))
        return moves

    def apply_move(self, move):
        col, move_type = move
        new_state = copy.deepcopy(self)
        
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
        # Alternar jogador: se era 1 vira 2, se era 2 vira 1
        new_state.current_player = 3 - self.current_player 
        return new_state
    
    def check_four_in_a_row(self, p_value):
        # p_value deve ser 1 ou 2
        # (A tua lógica de check_four_in_a_row está correta, 
        # apenas garante que passas 1 ou 2 em vez de 'X' ou 'O')
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if all(self.board[r][c+i] == p_value for i in range(4)): return True
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if all(self.board[r+i][c] == p_value for i in range(4)): return True
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if all(self.board[r-i][c+i] == p_value for i in range(4)): return True
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
              if all(self.board[r+i][c+i] == p_value for i in range(4)): return True
        return False
        
        
    def get_winner(self):
        p1_win = self.check_four_in_a_row(1)
        p2_win = self.check_four_in_a_row(2)
        
        if self.last_move and self.last_move[1] == 'pop':
            if p1_win and p2_win:
                # Quem fez o pop é o adversário do current_player
                return 3 - self.current_player

        if p1_win:
            return 1
        if p2_win:
            return 2
        return None

    def is_terminal(self):
        if self.get_winner() is not None:
            return True
        return len(self.get_legal_moves()) == 0

    def get_result(self, player):
        winner = self.get_winner()
        if winner is None:
            return 0
        if winner == player:
            return 1
        else:
            return -1