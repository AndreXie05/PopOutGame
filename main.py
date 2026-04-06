from board import PopOutGame
from terminal_board import run_terminal


def main():
    print("Escolhe interface:")
    print("1 - Gráfica")
    print("2 - Terminal")

    choice = input("Opção: ")

    if choice == "1":
        game = PopOutGame()
        game.run()
    else:
        run_terminal()


if __name__ == "__main__":
    main()