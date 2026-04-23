from moves import PopOutBoard
from mcts5 import mcts
from dataset import save_example

def simular_jogos(quantidade_jogos=20):
    print(f"A iniciar simulação de {quantidade_jogos} jogos IA vs IA...")
    
    for i in range(quantidade_jogos):
        board = PopOutBoard()
        jogadas_neste_jogo = 0
        
        while not board.is_terminal():
            # MCTS pensa (com menos iterações para ser mais rápido na geração de dados)
            node = mcts(board, iterations=40) 
            move = node.move
            
            # Guarda no dataset
            save_example(board, move)
            
            # Aplica a jogada e continua
            board = board.apply_move(move)
            jogadas_neste_jogo += 1
            
        print(f"Jogo {i+1}/{quantidade_jogos} concluído! ({jogadas_neste_jogo} jogadas registadas)")

if __name__ == "__main__":
    # Vamos gerar 20 jogos (deve dar umas 600 a 800 linhas novas no CSV)
    # Podes ir beber um café enquanto isto roda!
    simular_jogos(200)
    print("Geração de dados terminada. Corre o popout_ID3_Tree.py agora!")