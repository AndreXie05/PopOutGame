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

        # definir se é humano
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

            # guardar no dataset (antes de aplicar a jogada)
            save_example(board, move)

            print("IA jogou:", move)

        board = board.apply_move(move)

    # resultado final
    board.display()

    if board.check_four_in_a_row(1):
        print("Jogador 1 venceu!")
    elif board.check_four_in_a_row(2):
        print("Jogador 2 venceu!")
    else:
        print("Empate!")