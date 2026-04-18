from moves import PopOutBoard
from mcts4 import mcts
from dataset import save_example


def get_move(board):
    while True:
        try:
            col = int(input("Coluna (0-6): "))
            move_type = input("d = drop | p = pop: ").strip().lower()

            if move_type == 'd':
                move_type = 'drop'
            elif move_type == 'p':
                move_type = 'pop'
            else:
                print("Tipo inválido!")
                continue

            if board.is_valid_move(col, move_type):
                return (col, move_type)
            else:
                print("Jogada inválida!")

        except:
            print("Erro no input!")


def run_terminal():
    board = PopOutBoard()

    print("Modo Terminal: 1-HvIA | 2-HvH | 3-IAvIA")
    mode = int(input("Escolhe: "))

    while not board.is_terminal():
        board.display()

        # --- Verificar se o tabuleiro está cheio e sem vencedor ---
        winner = board.get_winner()
        if winner is None:
            # Verifica se todas as células estão ocupadas (tabuleiro cheio)
            tabuleiro_cheio = all(all(cell != 0 for cell in row) for row in board.board)
            if tabuleiro_cheio:
                print("O tabuleiro está completamente cheio!")
                # O jogador atual decide: pop ou empate?
                # Só pode escolher pop se houver pelo menos um pop legal
                pops_disponiveis = any(board.is_valid_move(c, 'pop') for c in range(board.cols))
                if pops_disponiveis:
                    escolha = input("Deseja fazer um pop (p) ou terminar o jogo com empate (e)? ").strip().lower()
                    if escolha == 'e':
                        print("Jogo terminado por empate (opção do jogador).")
                        return  # Sai da função, terminando o jogo
                    # Se escolheu 'p', continua normalmente para pedir o movimento
                else:
                    # Se não houver pops possíveis (caso raro), o jogo empata automaticamente
                    print("Não há pops possíveis. O jogo termina empatado.")
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
        print("Jogador 1 venceu!")
    elif winner == 2:
        print("Jogador 2 venceu!")
    else:
        print("Empate!") 