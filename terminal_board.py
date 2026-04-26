from moves import PopOutBoard
from mcts5 import mcts
from dataset import save_example
from ID3_Tree import ID3
from collections import Counter
from ia_vs_ia import iniciar_duelo
from popout_ID3_Tree import carregar_dataset_jogo

def get_move(board):
    # Jogadas válidas para o jogador 1 quando o tabuleiro estiver cheio
    colunas_pop_validas = [c for c in range(board.cols) if board.board[board.rows - 1][c] == board.current_player]
    
    # Verifica se o tabuleiro está cheio (nenhuma célula com 0 na linha do topo)
    tabuleiro_cheio = all(board.board[0][c] != 0 for c in range(board.cols))
    
    # Verifica se o jogador ATUAL tem peças na base para fazer pop
    tem_pecas_na_base = any(board.board[board.rows - 1][c] == board.current_player for c in range(board.cols))

    # REGRA 2
    #-----------------------------------------------------------------------------------------------------------------
    if tabuleiro_cheio:
        print(f"\n[!] ATENÇÃO: O tabuleiro está cheio, Jogador {board.current_player}!")
        
        # Se não tiver peças na base, não há escolha: é empate obrigatório
        if not tem_pecas_na_base:
            print("Não tens peças da tua cor na base para fazer 'pop'.")
            print("🤝 Empate obrigatório por falta de jogadas.")
            return "FORCED_DRAW"
        
        # REGRA 2: O jogador decide se quer empatar ou fazer pop
        while True:
            print("Podes declarar EMPATE ou tentar um POP-OUT.")
            escolha = input("[!] REGRA 2: Escreve 'e' para Empate ou 'p' para continuar com Pop: ").strip().lower()
            if escolha == 'e':
                return "FORCED_DRAW"
            if escolha == 'p':
                print("Ok! Escolhe a coluna para o pop.")
                break
            print("Escolha inválida. Digita apenas 'e' ou 'p'.")
    #-----------------------------------------------------------------------------------------------------------------
    while True:
        try:
            # Mostra a lista que calculámos lá em cima
            prompt = f"Jogadas possíveis {colunas_pop_validas} | Coluna: " if tabuleiro_cheio else "Coluna (0-6): "
            col_input = input(prompt).strip()
            if not col_input: continue
            col = int(col_input)
            if tabuleiro_cheio:
                move_type = 'pop'
                print(f"Tabuleiro cheio: A assumir 'pop' na coluna {col}...")
            else:
                tipo = input("d = drop | p = pop: ").strip().lower()
                if tipo == 'd': move_type = 'drop'
                elif tipo == 'p': move_type = 'pop'
                else: continue
            if board.is_valid_move(col, move_type): return (col, move_type)
            else: print("Jogada inválida. Tenta outra vez.")
        except ValueError: print("Erro: Insere um número válido.")

def run_terminal():
    board = PopOutBoard()

    print("\nModos de Jogo:")
    print("1- Humano vs MCTS5 | 2- Humano vs Árvore (DT) | 3- MCTS5 vs Árvore")
    print("4- Humano vs Humano | 5- MCTS5 vs MCTS5")
    
    while True:
        try:
            mode = int(input("Escolhe (1-5): "))
            if 1 <= mode <= 5: break
            else: print("Escolha inválida!")
        except ValueError: print("Insere um número.")
            
    if mode == 3:
        iniciar_duelo() # Chama o duelo especializado
        return

    # --- INICIALIZAÇÃO DA ÁRVORE (Apenas para modo 2) ---
    tree, modelo_id3, fallback = None, None, None
    if mode == 2:
        print("A treinar Árvore de Decisão...")
        data = carregar_dataset_jogo("dataset.csv")
        if data:
            modelo_id3 = ID3()
            tree = modelo_id3.construir(data, list(range(len(data[0])-1)))
            fallback = Counter([row[-1] for row in data]).most_common(1)[0][0]
        else:
            print("Erro: dataset.csv necessário para o modo DT!"); return

    forced_draw = False
    
    # REGRA 3
    #----------------------------------------------------------------------------------
    historico_estados = []  #guarda os estados para a regra 3
    while not board.is_terminal():
        # --- BLOCO DA REGRA 3 ---
        # Criamos uma "fotografia" do tabuleiro + jogador atual
        estado_atual = (tuple(tuple(row) for row in board.board), board.current_player)
        historico_estados.append(estado_atual)
        
        if historico_estados.count(estado_atual) >= 3:
            print("\n[!] REGRA 3: Empate por repetição (3 vezes o mesmo estado)!")
            forced_draw = True
            break
     #----------------------------------------------------------------------------------
        board.display()

        # 1. Determinar se é Humano
        if mode == 1 or mode == 2: 
            is_human = (board.current_player == 1)
        elif mode == 4: 
            is_human = True
        else: # modo 5 (MCTS vs MCTS)
            is_human = False

        if is_human:
            print(f"Jogador {board.current_player}")
            move = get_move(board)
            if move == "FORCED_DRAW": forced_draw = True; break
        else:
            # 2. Determinar qual IA joga
            if mode == 2: # No modo 2, o Jogador 2 é sempre a Árvore
                print(f"IA (Árvore - Jogador {board.current_player})...")
                feat = [float(c) for r in board.board for c in r] + [float(board.current_player)]
                previsao = modelo_id3.prever(tree, feat, classe_default=fallback)
                
                if isinstance(previsao, str) and "_" in previsao:
                    c_str, t = previsao.split('_')
                    move = (int(c_str), t)
                else: 
                    move = mcts(board, iterations=100).move # Fallback de segurança
            else:
                # Modos 1 e 5 usam MCTS5
                print(f"IA (MCTS5 - Jogador {board.current_player}) a pensar...")
                move = mcts(board, iterations=1500).move
                save_example(board, move) # Grava dados para treino futuro

            if not move or not board.is_valid_move(move[0], move[1]):
                forced_draw = True; break
            print(f"IA jogou: {move}")

        board = board.apply_move(move)

    board.display()
    if forced_draw: 
        print("🤝 EMPATE FORÇADO!")
    else:
        w = board.get_winner()
        
        # --- REGRA 1: IMPRIME APENAS SE AMBOS FIZEREM 4 AO MESMO TEMPO ---
        if board.last_move and board.last_move[1] == 'pop' and \
           board.check_four_in_a_row(1) and board.check_four_in_a_row(2):
            print(f"[!] Regra 1: jogador {w} ganhou")
        # ---------------------------------------------------------------

        if w == 1: 
            print("🎉 JOGADOR 1 (X) VENCEU!")
        elif w == 2: 
            print("🎉 JOGADOR 2 (O) VENCEU!")
        else: 
            print("🤝 EMPATE!")
