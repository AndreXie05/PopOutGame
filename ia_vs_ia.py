from moves import PopOutBoard
from mcts5 import mcts
from ID3_Tree import ID3
from popout_ID3_Tree import carregar_dataset_jogo
from collections import Counter

def iniciar_duelo():
    """Executa o duelo: MCTS4 (Jogador 1) vs Árvore de Decisão (Jogador 2)"""
    board = PopOutBoard()
    
    data = carregar_dataset_jogo("dataset.csv")
    
    if not data:    
        print("Erro: Precisas de um dataset...")
        return

    num_features = len(data[0]) - 1 
    indices_atributos = list(range(num_features))
    modelo_id3 = ID3()
    tree = modelo_id3.construir(data, indices_atributos)
    
    todas_as_jogadas = [row[-1] for row in data]
    fallback = Counter(todas_as_jogadas).most_common(1)[0][0]

    print("\n=== DUELO: MCTS4 (X) vs Árvore de Decisão (O) ===")
    
    while not board.is_terminal():
        board.display()
        
        if board.current_player == 1:
            print("MCTS4 a pensar...")
            node = mcts(board, iterations=300)
            move = node.move
        else:
            print("Árvore de Decisão a decidir...")
            # Prepara os dados para a árvore
            features = [str(cell) for row in board.board for cell in row] + [str(board.current_player)]
            previsao = modelo_id3.prever(tree, features, classe_default=fallback)
            
            # Validação do formato (ex: "3_drop")
            if isinstance(previsao, str) and "_" in previsao:
                col_str, tipo = previsao.split('_')
                move = (int(col_str), tipo)
            else:
                # Se a árvore falhar, usa MCTS4 rápido
                print("Aviso: Árvore falhou, a usar MCTS4 de emergência...")
                move = mcts(board, iterations=100).move

            # Verifica se a jogada é legal no PopOut
            if not board.is_valid_move(move[0], move[1]):
                move = mcts(board, iterations=100).move

        print(f"Jogada: {move}")
        board = board.apply_move(move)

    board.display()
    vencedor = board.get_winner()
    if vencedor == 1: print("VENCEDOR: MCTS4!")
    elif vencedor == 2: print("VENCEDOR: Árvore de Decisão!")
    else: print("EMPATE!")