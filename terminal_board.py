from moves import PopOutBoard
from mcts4 import mcts
from dataset import save_example

def get_move(board):
    # Verifica se o tabuleiro está cheio (nenhuma célula com 0 na linha do topo)
    tabuleiro_cheio = all(board.board[0][c] != 0 for c in range(board.cols))
    
    while True:
        try:
            col_input = input("Coluna (0-6): ").strip()
            if not col_input: continue
            col = int(col_input)

            if tabuleiro_cheio:
                # Se está cheio, ignoramos a pergunta do tipo e forçamos 'pop'
                move_type = 'pop'
                print(f"Tabuleiro cheio: A assumir 'pop' na coluna {col}...")
            else:
                # Se NÃO está cheio, pergunta normalmente
                tipo = input("d = drop | p = pop: ").strip().lower()
                if tipo == 'd':
                    move_type = 'drop'
                elif tipo == 'p':
                    move_type = 'pop'
                else:
                    print("Tipo inválido! Escolha 'd' ou 'p'.")
                    continue

            # Validar a jogada no motor do jogo
            if board.is_valid_move(col, move_type):
                return (col, move_type)
            else:
                motivo = "não tens uma peça tua na base" if move_type == 'pop' else "coluna cheia"
                print(f"Jogada inválida ({motivo}). Tenta outra vez.")

        except ValueError:
            print("Erro: Insere um número válido para a coluna (0-6).")

def run_terminal():
    board = PopOutBoard()

    print("Modo Terminal: 1-HvIA | 2-HvH | 3-IAvIA")
    mode = int(input("Escolhe: "))

    historico_estados = {}
    while not board.is_terminal():
        board.display()
        # 2. Registar o estado ANTES de mostrar ou pedir a jogada
        estado_serializado = (tuple(tuple(row) for row in board.board), board.current_player)
        historico_estados[estado_serializado] = historico_estados.get(estado_serializado, 0) + 1

        # 3. Verificar repetição (Regra 3)
        if historico_estados[estado_serializado] >= 3:
            board.display()
            print("\n--- EMPATE POR REPETIÇÃO DE ESTADO (3ª VEZ) ---")
            return
        
        # --- Verificar se o tabuleiro está cheio e sem vencedor ---
        winner = board.get_winner()
        if winner is None:
            tabuleiro_cheio = all(all(cell != 0 for cell in row) for row in board.board)
            if tabuleiro_cheio:
                print("\n--- O TABULEIRO ESTÁ COMPLETAMENTE CHEIO! ---")
                
                # 1. Calcular quais colunas permitem 'pop' para o jogador atual
                colunas_validas = [c for c in range(board.cols) if board.is_valid_move(c, 'pop')]
                
                if colunas_validas:
                    # 2. Mostrar as opções ao jogador
                    print(f"Podes fazer 'pop' nas colunas: {colunas_validas}")
                    
                    escolha = input("Deseja fazer um pop (p) ou terminar o jogo com empate (e)? Resposta: ").strip().lower()
                    if escolha == 'e':
                        print("Jogo terminado por empate (opção do jogador).")
                        return
                    
                    # Se ele escolheu 'p', o código continua e vai chamar o get_move(board) abaixo
                else:
                    print("Não tens peças na linha de base para retirar. O jogo termina empatado.")
                    return
        # --- Fim da verificação de tabuleiro cheio ---

        # determinar se é humano a jogar
        if mode == 1:
            is_human = board.current_player == 1
        elif mode == 2:
            is_human = True
        else:
            is_human = False

        if is_human:
            print(f"Jogador {board.current_player}")
            move = get_move(board)
        else:
            print(f"IA ({board.current_player})...")
            node = mcts(board, iterations=300)
            move = node.move
            save_example(board, move)
            print("IA jogou:", move)

        board = board.apply_move(move)

    # Após o loop, mostrar o resultado usando get_winner()
    board.display()
    winner = board.get_winner()
    if winner == 1:
        print("🎉 JOGADOR 1 (X) VENCEU!")
    elif winner == 2:
        print("🎉 JOGADOR 2 (O) VENCEU!")
    else:
        print("🤝 EMPATE!")