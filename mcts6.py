import math
import random
import concurrent.futures
import os

# Adaptador avançado para tornar o MCTS6 compatível com o simulador E com o gravador de datasets
class MCTS6Result:
    def __init__(self, move):
        self.move = move

    # Permite que o código faça move[0] ou move[1] (usado no dataset.py)
    def __getitem__(self, index):
        return self.move[index]

    # Permite que o código use len(move) se necessário
    def __len__(self):
        return len(self.move)
    
    # Define como o objeto aparece quando é impresso (print)
    def __repr__(self):
        return str(self.move)

    def __str__(self):
        return str(self.move)
    
class Node:
    def __init__(self, state, parent=None, move=None, max_children=5):
        self.state = state
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visits = 0
        self.children = []
        self.max_children = max_children
        
        self.untried_moves = state.get_legal_moves()
        
        if self.untried_moves:
            # CORREÇÃO: Foco verdadeiro no centro! 
            # Ordena por proximidade ao centro (coluna 3) e usa random para desempatar
            centro = len(state.board[0]) // 2 if state.board else 3
            self.untried_moves.sort(key=lambda m: (abs(m[0] - centro), random.random()))
            
            if self.max_children and len(self.untried_moves) > self.max_children:
                self.untried_moves = self.untried_moves[:self.max_children]

def uct_best_child(node, c=1.414):
    best_score = float('-inf')
    best_children = []
    
    for child in node.children:
        if child.visits == 0:
            score = float('inf')
        else:
            exploit = child.wins / child.visits
            explore = math.sqrt(math.log(node.visits) / child.visits)
            score = exploit + c * explore
            
        if score > best_score:
            best_score = score
            best_children = [child]
        elif score == best_score:
            best_children.append(child)
            
    return random.choice(best_children) if best_children else None

def expand(node):
    if node.untried_moves:
        move = node.untried_moves.pop(0)
        next_state = node.state.apply_move(move)
        child_node = Node(state=next_state, parent=node, move=move, max_children=node.max_children)
        node.children.append(child_node)
        return child_node
    return None

def rollout(state):
    current_state = state
    while not current_state.is_terminal():
        legal_moves = current_state.get_legal_moves()
        winning_move = None
        
        for move in legal_moves:
            test_state = current_state.apply_move(move)
            if test_state.get_winner() == current_state.current_player:
                winning_move = move
                break
                    
        if winning_move:
            current_state = current_state.apply_move(winning_move)
        else:
            current_state = current_state.apply_move(random.choice(legal_moves))
            
    return current_state.get_result(state.current_player)

def backpropagate(node, result):
    result = -result 
    while node is not None:
        node.visits += 1
        if result == 1:
            node.wins += 1
        result = -result 
        node = node.parent


# WORKER INDIVIDUAL (Corre num núcleo isolado)
def mcts_worker(state, safe_moves, iterationsss, c, max_children):
    root = Node(state=state, max_children=max_children)
    
    # Restringe a raiz apenas às jogadas que não são suicídio imediato
    if safe_moves:
        root.untried_moves = safe_moves[:max_children]

    for _ in range(iterationsss):
        node = root
        while not node.untried_moves and node.children:
            node = uct_best_child(node, c)
            
        if node.untried_moves:
            new_node = expand(node)
            if new_node:
                node = new_node
                
        result = rollout(node.state)
        backpropagate(node, result)
        
    # Retorna um dicionário com os votos: {jogada: numero_de_visitas}
    return {child.move: child.visits for child in root.children}

# CÉREBRO PRINCIPAL (Paralelização e Reflexos)
def get_best_move_mcts(state, iterations=6000, c=1.414, max_children=5):
    legal_moves = state.get_legal_moves()
    
    # 1. Reflexos de Sobrevivência (Correm apenas 1x na thread principal)
    safe_moves = []
    for move in legal_moves:
        test_state = state.apply_move(move)
        
        # Posso ganhar já? Joga e acaba.
        if test_state.get_winner() == state.current_player:
            return MCTS6Result(move)

        # O adversário ganha a seguir?
        if test_state.is_terminal() and test_state.get_winner() != state.current_player:
            continue

        opponent_wins_next = False
        if not test_state.is_terminal():
            for opp_move in test_state.get_legal_moves():
                if test_state.apply_move(opp_move).get_winner() == test_state.current_player:
                    opponent_wins_next = True
                    break
                    
        if not opponent_wins_next:
            safe_moves.append(move)

    if len(safe_moves) == 1:
        return MCTS6Result(safe_moves[0])
        
    if not safe_moves:
        # Xeque-mate inevitável, joga algo legal.
        return MCTS6Result(random.choice(legal_moves))

    # 2. Paralelização de Raiz (Root Parallelization)
    num_cores = os.cpu_count() or 4
    iters_per_core = iterations // num_cores
    
    combined_visits = {move: 0 for move in safe_moves}
    
    # Lança N processos em paralelo
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = [
            executor.submit(mcts_worker, state, safe_moves, iters_per_core, c, max_children)
            for _ in range(num_cores)
        ]
        
        # Junta os resultados à medida que os núcleos terminam
        for future in concurrent.futures.as_completed(futures):
            worker_results = future.result()
            for move, visits in worker_results.items():
                if move in combined_visits:
                    combined_visits[move] += visits

    # 3. Escolhe a jogada mais votada por todos os núcleos
    # Ordena as jogadas pelo total de visitas (votos)
    best_moves = sorted(combined_visits.keys(), key=lambda m: combined_visits[m], reverse=True)
    
    # Temperatura para gerar diversidade no dataset do ID3 (primeiras jogadas)
    pecas_no_tabuleiro = sum(1 for row in state.board for cell in row if cell != 0)
    if pecas_no_tabuleiro < 6 and len(best_moves) >= 2:
        return MCTS6Result(random.choice(best_moves[:2]))
        
    return MCTS6Result(safe_moves[0])