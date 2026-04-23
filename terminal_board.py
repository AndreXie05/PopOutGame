from moves import PopOutBoard 
from mcts5 import mcts 
from dataset import save_example 
from ia_vs_ia import iniciar_duelo

def get_move(board):
    # Verifica se o tabuleiro está cheio (nenhuma célula com 0 na linha do topo)
    tabuleiro_cheio = all(board.board[0][c] != 0 for c in range(board.cols))
    
    # Verifica se o jogador ATUAL tem peças na base para fazer pop
    tem_pecas_na_base = any(board.board[board.rows - 1][c] == board.current_player for c in range(board.cols))

    # PREVENÇÃO DO BUG DO LOOP INFINITO (Regra do Tabuleiro Cheio)
    if tabuleiro_cheio and not tem_pecas_na_base:
        print(f"\n[!] Tabuleiro cheio e o Jogador {board.current_player} não tem peças na base para fazer pop!")
        return "FORCED_DRAW" # Sinal especial para terminar o jogo

    while True:
        try:
            col_input = input("Coluna (0-6): ").strip()
            if not col_input: continue
            col = int(col_input)

            if tabuleiro_cheio:
                # Se está cheio, sabemos que ele tem peças (por causa do if ali de cima)
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

    while True:
        print("\nModo Terminal: 1-HvIA | 2-HvH | 3- MCTS vs Árvore")
        try:
            mode = int(input("Escolhe (1-3): "))
            if mode in [1, 2, 3]:
                break
            else:
                print("Escolha inválida! Por favor, escolhe 1, 2 ou 3.")
        except ValueError:
            print("Erro: Insere um número (1, 2 ou 3).")
            
    if mode == 3:
        iniciar_duelo()
        return

    # MODO 1 (HvIA) e MODO 2 (HvH)
    forced_draw = False
    
    while not board.is_terminal():
        board.display()

        if mode == 1:
            is_human = board.current_player == 1
        else: # mode == 2
            is_human = True

        if is_human:
            print(f"Jogador {board.current_player}")
            move = get_move(board)
            if move == "FORCED_DRAW":
                forced_draw = True
                break
        else:
            print(f"IA (MCTS5 - Jogador {board.current_player}) a pensar...")
            node = mcts(board, iterations=1500) # Iterações afinadas para a nova velocidade
            move = node.move
            
            # Se a IA não tiver peças e o tabuleiro estiver cheio (cenário raro, mas possível)
            if not move: 
                print(f"\n[!] A IA não tem jogadas legais e o tabuleiro está bloqueado!")
                forced_draw = True
                break
                
            print(f"IA jogou: {move}")
            # Grava a jogada da IA para o teu dataset!
            save_example(board, move) 

        board = board.apply_move(move)

    board.display()
    
    # Tratamento do Fim do Jogo
    if forced_draw:
        print("🤝 EMPATE FORÇADO! (Um jogador ficou sem jogadas possíveis com o tabuleiro cheio)")
    else:
        winner = board.get_winner()
        if winner == 1:
            print("🎉 JOGADOR 1 (X) VENCEU!")
        elif winner == 2:
            print("🎉 JOGADOR 2 (O) VENCEU!")
        else:
            print("🤝 EMPATE!")