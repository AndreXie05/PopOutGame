import csv
import os

FILE_NAME = "dataset.csv"

def save_example(state, move):
    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["board", "player", "move"])

        board_flat = flatten_board(state.board)
        move_str = f"{move[0]}_{move[1]}"

        writer.writerow([
            ",".join(map(str, board_flat)),
            state.current_player,
            move_str
        ])


def flatten_board(board):
    return [cell for row in board for cell in row]