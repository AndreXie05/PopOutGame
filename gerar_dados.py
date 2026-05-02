from moves import PopOutBoard
from mcts6 import get_best_move_mcts
from dataset import save_example

def simular_jogos(quantidade_jogos=200):
    print(f"A iniciar simulação de {quantidade_jogos} jogos IA vs IA...")
    
    for i in range(quantidade_jogos):
        board = PopOutBoard()
        jogadas_neste_jogo = 0
        
        while not board.is_terminal():
            move = get_best_move_mcts(board, total_iterations=200) 
            
            # Guarda no dataset (o save_example já está perfeito)
            save_example(board, move)
            
            # Aplica a jogada e continua
            board = board.apply_move(move)
            jogadas_neste_jogo += 1
            
        print(f"Jogo {i+1}/{quantidade_jogos} concluído! ({jogadas_neste_jogo} jogadas registadas)")

if __name__ == "__main__":
    # Gerar 200 jogos treinar a Árvore de Decisão
    simular_jogos(200)
    print("Geração de dados terminada. Corre o popout_ID3_Tree.py agora!")