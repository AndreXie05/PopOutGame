from moves import PopOutBoard
from mcts  import mcts as _mcts1
from mcts2 import mcts as _mcts2
from mcts3 import mcts as _mcts3
from mcts4 import mcts as _mcts4
from mcts5 import get_best_move as _mcts5
from mcts6 import get_best_move as _mcts6
from dataset import save_example
from popout_ID3_Tree import treinar_modelo

VERSOES_MCTS = {
    1: lambda b, it=1000: _mcts1(b, it).move,
    2: lambda b, it=1000: _mcts2(b, it).move,
    3: lambda b, it=1000: _mcts3(b, it).move,
    4: lambda b, it=1000: _mcts4(b, it).move,
    5: lambda b, it=2000: _mcts5(b, it),
    6: lambda b, it=2000: _mcts6(b, it),
}

NOMES_MCTS = {
    1: "v1 (base)",
    2: "v2 (greedy)",
    3: "v3 (reflexos)",
    4: "v4 (centro)",
    5: "v5 (completo)",
    6: "v6 (política)",
}

def escolher_versao_mcts(prompt="Versão MCTS (1-6) [padrão=6]: "):
    """Menu interativo para escolher a versão do MCTS introduzida pelo utilizador."""
    while True:
        try:
            v = input(prompt).strip()
            if v == "": return 6
            v = int(v)
            if 1 <= v <= 6: return v
            print("Escolhe entre 1 e 6.")
        except ValueError:
            print("Insere um número.")

def get_move(board):
    """gere a jogada introduzida por um jogador humano (verificando se é válida)."""
    colunas_pop_validas = [c for c in range(board.cols) if board.board[board.rows - 1][c] == board.current_player] #quais as colunas onde o jogador atual possui peças na base (para pop)
    tabuleiro_cheio = all(board.board[0][c] != 0 for c in range(board.cols)) # Avalia se a linha do topo (linha 0) está sem espaços vazios, indicando tabuleiro cheio
    tem_pecas_na_base = any(board.board[board.rows - 1][c] == board.current_player for c in range(board.cols)) # Avalia se existe pelo menos uma peça própria na linha de base

    # REGRA 2
    #-----------------------------------------------------------------------------------------------------------------
    if tabuleiro_cheio:
        print(f"\n[!] ATENÇÃO: O tabuleiro está cheio, Jogador {board.current_player}!")
        if not tem_pecas_na_base:
            print("Não tens peças da tua cor na base para fazer 'pop'.")
            print("Empate obrigatório por falta de jogadas.")
            return "FORCED_DRAW"
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

    #prints iniciais para mostrar as opções de escolha
    print("\nModos de Jogo:")
    print("1- Humano vs IA | 2- Humano vs Árvore de Decisão | 3- IA vs Árvore de Decisão")
    print("4- Humano vs Humano | 5- IA vs IA")
    print("\nVersões de MCTS: 1=base | 2=greedy | 3=reflexos | 4=centro | 5=completo | 6=política")
    
    #escolha do utilizador do modo
    while True:
        try:
            mode = int(input("\nEscolhe modo (1-5): "))
            if 1 <= mode <= 5: break
            else: print("Escolha inválida!")
        except ValueError: print("Insere um número.")

    # Selecionar versão(ões) de MCTS (utilizador escolhe)
    versao_ia1 = 6
    versao_ia2 = 6
    if mode in (1, 3):
        versao_ia1 = escolher_versao_mcts("Versão MCTS da IA (1-6) [padrão=6]: ")
    elif mode == 5:
        print("Jogador 1 (X):")
        versao_ia1 = escolher_versao_mcts("  Versão MCTS (1-6) [padrão=6]: ")
        print("Jogador 2 (O):")
        versao_ia2 = escolher_versao_mcts("  Versão MCTS (1-6) [padrão=6]: ")

    fn_ia1 = VERSOES_MCTS[versao_ia1]
    fn_ia2 = VERSOES_MCTS[versao_ia2]

    tree, modelo_id3, fallback = None, None, None
    if mode in (2, 3):
        modelo_id3, tree, fallback = treinar_modelo("dataset.csv")
        if modelo_id3 is None:
            print("Erro: dataset.csv necessário para o modo DT!")
            return

    forced_draw = False

    # REGRA 3
    #----------------------------------------------------------------------------------
    historico_estados = []
    while not board.is_terminal():
        tabuleiro_snapshot = tuple(tuple(int(c) for c in row) for row in board.board)
        estado_atual = (tabuleiro_snapshot, board.current_player)
        historico_estados.append(estado_atual)

        if historico_estados.count(estado_atual) >= 3:
            print("\n[!] REGRA 3: O mesmo estado de jogo repetiu-se 3 vezes!")
            
            p1_is_human = (mode in (1, 2, 4))
            p2_is_human = (mode == 4)
            
            # 1. Decisão do Jogador 1
            if p1_is_human:
                while True:
                    decisao1 = input("Jogador 1 (X) -> Desejas continuar a jogar (c) ou aceitar o Empate (e)? ").strip().lower()
                    if decisao1 in ('c', 'e'): break
                    print("Opção inválida. Digita apenas 'c' ou 'e'.")
            else:
                print("IA (Jogador 1) decidiu aceitar o empate para evitar um loop infinito.")
                decisao1 = 'e'
                
            # Atalho: Se o Jogador 1 escolheu empate, não vale a pena perguntar ao Jogador 2
            if decisao1 == 'e':
                print("[!] Partida terminada: Jogador 1 aceitou o empate.")
                forced_draw = True
                break
            
            # 2. Decisão do Jogador 2 (só acontece se o Jogador 1 quis continuar)
            if p2_is_human:
                while True:
                    decisao2 = input("Jogador 2 (O) -> Desejas continuar a jogar (c) ou aceitar o Empate (e)? ").strip().lower()
                    if decisao2 in ('c', 'e'): break
                    print("Opção inválida. Digita apenas 'c' ou 'e'.")
            else:
                print("IA (Jogador 2) decidiu aceitar o empate para evitar um loop infinito.")
                decisao2 = 'e'
            
            if decisao2 == 'e':
                print("[!] Partida terminada: Jogador 2 aceitou o empate.")
                forced_draw = True
                break
            
            # Se ninguém escolheu 'e', o jogo continua
            print("[!] Ambos os jogadores escolheram continuar! O jogo prossegue...\n")    
    #----------------------------------------------------------------------------------
        board.display() # Imprime graficamente o estado atual do tabuleiro no terminal

        # Define se o turno corrente pertence a uma entidade humana
        if mode == 1 or mode == 2:
            is_human = (board.current_player == 1)
        elif mode == 4:
            is_human = True
        else:
            is_human = False

        # No modo 3, jogador 2 é a Árvore de Decisão
        use_dt = (mode == 2 and not is_human) or (mode == 3 and board.current_player == 2)

        if is_human:
            # Fluxo do Jogador Humano
            print(f"Jogador {board.current_player}")
            move = get_move(board)
            if move == "FORCED_DRAW": forced_draw = True; break
        elif use_dt:
            # Fluxo do Agente baseado na Árvore de Decisão ID3
            print(f"IA (Árvore - Jogador {board.current_player})...")
            feat = [float(c) for r in board.board for c in r] + [float(board.current_player)] # Converte a matriz 2D para lista unidimensional de floats e anexa o ID do jogador ativo
            previsao = modelo_id3.prever(tree, feat, classe_default=fallback) # Efetua a previsão da jogada ótima a partir da Árvore de Decisão numérica
            # Converte a string retornada "coluna_tipo" (ex: "4_drop") num tuplo de execução (4, "drop")
            if isinstance(previsao, str) and "_" in previsao:
                c_str, t = previsao.split('_')
                move = (int(c_str), t)
            else:
                move = fn_ia1(board) #fallback é o mcts se algo correr mal
        else:
            # Fluxo do Agente baseado em Busca Adversária MCTS
            fn_ia = fn_ia1 if board.current_player == 1 else fn_ia2
            nome_v = NOMES_MCTS[versao_ia1 if board.current_player == 1 else versao_ia2]
            print(f"IA (MCTS {nome_v} - Jogador {board.current_player}) a pensar...")
            move = fn_ia(board)
            save_example(board, move) # Alimenta e expande o dataset.csv em tempo de execução

            # Cláusula de segurança: encerra se o MCTS falhar ou gerar jogadas inválidas
            if not move or not board.is_valid_move(move[0], move[1]):
                forced_draw = True; break
            print(f"IA jogou: {move}")

        board = board.apply_move(move)

    board.display() #imprime o tabuleiro no terminal
    if forced_draw:
        print("EMPATE FORÇADO!")
    else:
        w = board.get_winner()

        # REGRA 1: imprime apenas se ambos fizerem 4 ao mesmo tempo
        if board.last_move and board.last_move[1] == 'pop' and \
           board.check_four_in_a_row(1) and board.check_four_in_a_row(2):
            print(f"[!] Regra 1: jogador {w} ganhou")

        if w == 1:
            print("JOGADOR 1 (X) VENCEU!")
        elif w == 2:
            print("JOGADOR 2 (O) VENCEU!")
        else:
            print("EMPATE!")
