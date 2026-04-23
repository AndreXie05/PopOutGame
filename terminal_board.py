from moves import PopOutBoard 
from mcts4 import mcts 
from dataset import save_example 
from ID3_Tree import ID3 
from popout_ID3_Tree import carregar_dataset_jogo 
from collections import Counter
from ia_vs_ia import iniciar_duelo

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

    while True: # Loop para garantir uma escolha válida
        print("\nModo Terminal: 1-HvIA | 2-HvH | 3- MCTS vs Árvore")
        try:
            mode = int(input("Escolhe (1-3): "))
            if mode in [1, 2, 3]:
                break # Sai do loop se a escolha for correta
            else:
                print("Escolha inválida! Por favor, escolhe 1, 2 ou 3.")
        except ValueError:
            print("Erro: Insere um número (1, 2 ou 3).")
    if mode == 3:
        iniciar_duelo() # Chama o ficheiro novo
        return # Termina para não correr o loop antigo

    historico_estados = {}
    while not board.is_terminal(): #
        board.display() #

        # Determinar quem joga
        if mode == 1:
            is_human = board.current_player == 1
        elif mode == 2:
            is_human = True
        else: # No modo 3, ninguém é humano
            is_human = False

        if is_human:
            print(f"Jogador {board.current_player}")
            move = get_move(board)
        else:
            # --- LÓGICA IA vs IA (MODO 3) ---
            if mode == 3 and board.current_player == 2:
                print("IA (Árvore de Decisão - Jogador 2)...")
                # Prepara os dados para a árvore
                features = [str(cell) for row in board.board for cell in row] + [str(board.current_player)]
                previsao = modelo_id3.prever(tree, features, classe_default=fallback_move) #
                
                # Converte string "3_drop" para tuplo (3, 'drop')
                col_str, tipo = previsao.split('_')
                move = (int(col_str), tipo)

                # Segurança: se a árvore sugerir erro, usa MCTS rápido
                if not board.is_valid_move(move[0], move[1]): #
                    print("Árvore falhou, a usar MCTS de emergência...")
                    node = mcts(board, iterations=100) #
                    move = node.move
            else:
                # Caso padrão: MCTS4 (Jogador 1 no modo 3, ou Jogador 2 no modo 1)
                print(f"IA (MCTS4 - Jogador {board.current_player})...")
                node = mcts(board, iterations=300) #
                move = node.move
                save_example(board, move) #
            
            print("IA jogou:", move)

        board = board.apply_move(move) #

    # Após o loop, mostrar o resultado usando get_winner()
    board.display()
    winner = board.get_winner()
    if winner == 1:
        print("🎉 JOGADOR 1 (X) VENCEU!")
    elif winner == 2:
        print("🎉 JOGADOR 2 (O) VENCEU!")
    else:
        print("🤝 EMPATE!")