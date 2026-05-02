from moves import PopOutBoard
from mcts6 import get_best_move_mcts
from ID3_Tree import ID3
from popout_ID3_Tree import carregar_dataset_jogo
from collections import Counter

def iniciar_duelo():
    """Executa o duelo: MCTS6 (Jogador 1) vs Árvore de Decisão (Jogador 2)"""
    board = PopOutBoard()
    
    print("A carregar dataset e a treinar Árvore de Decisão...")
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

    # --- CÁLCULO DE PRECISÃO ---
    acertos = 0
    for row in data:
        features = row[:-1]
        real = row[-1].strip()
        if modelo_id3.prever(tree, features, classe_default=fallback) == real:
            acertos += 1
    precisao = (acertos / len(data)) * 100
    print(f"🎯 Precisão da Árvore de Decisão: {precisao:.2f}% ({acertos}/{len(data)} jogadas memorizadas)")

    print("\n=== DUELO: MCTS6 (X) vs Árvore de Decisão (O) ===")
    
    while not board.is_terminal():
        board.display()
        
        if board.current_player == 1:
            print("MCTS6 a pensar...")
            # Atualizado para chamar a nova função paralelizada
            move = get_best_move_mcts(board, total_iterations=300)
        else:
            print("Árvore de Decisão a decidir...")
            # Prepara os dados para a árvore
            features = [float(cell) for row in board.board for cell in row] + [float(board.current_player)]
            previsao = modelo_id3.prever(tree, features, classe_default=fallback)
            
            # Validação do formato (ex: "3_drop")
            if isinstance(previsao, str) and "_" in previsao:
                col_str, tipo = previsao.split('_')
                move = (int(col_str), tipo)
            else:
                # Se a árvore falhar, usa MCTS6 rápido
                print("Aviso: Árvore falhou, a usar MCTS6 de emergência...")
                move = get_best_move_mcts(board, total_iterations=100)

            # Verifica se a jogada é legal no PopOut
            if not board.is_valid_move(move[0], move[1]):
                move = get_best_move_mcts(board, total_iterations=100)

        print(f"Jogada: {move}")
        board = board.apply_move(move)

    board.display()
    vencedor = board.get_winner()
    if vencedor == 1: print("VENCEDOR: MCTS6!")
    elif vencedor == 2: print("VENCEDOR: Árvore de Decisão!")
    else: print("EMPATE!")
    return tree