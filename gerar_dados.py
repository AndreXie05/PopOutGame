"""
Geração paralela de dados de treino para o ID3.
Cada jogo corre num processo independente → speedup linear com o nº de cores.
"""
import os
import csv
import random
from multiprocessing import Pool, cpu_count


FILE_DATASET = "dataset.csv"


def _simular_jogo(seed):
    """
    Worker: simula um jogo completo IA vs IA e retorna os exemplos gerados.
    Corre num processo separado — importações feitas aqui para evitar problemas
    de serialização entre processos.
    """
    random.seed(seed)

    from moves import PopOutBoard
    from mcts5 import get_best_move

    board = PopOutBoard()
    exemplos = []
    historico = []

    while not board.is_terminal():
        # Regra 3: empate por repetição de estado
        estado = (tuple(tuple(r) for r in board.board), board.current_player)
        historico.append(estado)
        if historico.count(estado) >= 3:
            break

        move = get_best_move(board, iterations=10000)
        if move is None:
            break

        flat = board.to_flat()
        exemplos.append((flat, board.current_player, f"{move[0]}_{move[1]}"))
        board = board.apply_move(move)

    return exemplos


def simular_jogos(quantidade_jogos=1000):
    if os.path.isfile(FILE_DATASET):
        resp = input(f"{FILE_DATASET} já existe. Apagar e recomeçar do zero? (s/n) [padrão=s]: ").strip().lower()
        if resp != 'n':
            os.remove(FILE_DATASET)
            print("Dataset anterior removido. A gerar dados novos...")
        else:
            print("A adicionar ao dataset existente...")

    n_workers = min(cpu_count(), quantidade_jogos)
    print(f"A iniciar simulação de {quantidade_jogos} jogos IA vs IA")

    # Seed diferente por worker para garantir diversidade entre jogos
    seeds = [random.randint(0, 10**9) for _ in range(quantidade_jogos)]

    file_exists = os.path.isfile(FILE_DATASET)
    total_jogadas = 0

    with Pool(n_workers) as pool:
        # imap_unordered: processa jogos à medida que terminam (não espera por todos)
        for i, exemplos in enumerate(pool.imap_unordered(_simular_jogo, seeds), 1):
            with open(FILE_DATASET, mode="a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["board", "player", "move"])
                    file_exists = True
                for flat, player, move_str in exemplos:
                    writer.writerow([",".join(map(str, flat)), player, move_str])

            total_jogadas += len(exemplos)
            print(f"Jogo {i}/{quantidade_jogos} concluído ({len(exemplos)} jogadas) | "
                  f"Total: {total_jogadas} exemplos")


if __name__ == "__main__":
    simular_jogos()
    print("Geração de dados terminada. Corre o popout_ID3_Tree.py agora!")
