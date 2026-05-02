import math
import random

'''
MCTS5 (vs MCTS4)

ESTRUTURA E PERFORMANCE:
1. Rollout Hiper-Rápido: Otimização da simulação de O(n^2) para O(n). Em vez de verificar 
   todas as respostas do adversário, foca-se apenas em vitórias imediatas próprias. 
   Isto permite elevar as iterações de ~150 para +1500 no mesmo tempo.
2. Poda Heurística (max_children): Implementação de limite de ramificação por nó 
   (ex: 5 filhos). Foca o processamento nas colunas centrais (estattísticamente melhores) e jogadas mais promissoras. 

INTELIGÊNCIA E REFLEXOS:
3. Reflexos de 1-Ply (Ataque/Defesa): Adicionado um filtro antes da 
   construção da árvore. O algoritmo deteta vitórias imediatas ou ameaças críticas 
   do adversário, respondendo instantaneamente sem gastar iterações.
4. Constante de Exploração (c) Ajustável: A fórmula UCT agora aceita o parâmetro 'c' 
   variável, permitindo alternar entre uma IA mais conservadora ou exploratória.

QUALIDADE DE DADOS E CORREÇÕES:
5. Temperatura (Diversidade de Abertura): Nas primeiras 6 jogadas, a IA escolhe entre 
   as 2 melhores opções para evitar jogos repetitivos ("Efeito Torre"). Isto gera um 
   dataset muito mais rico para o treino da Árvore de Decisão.
6. Correção de Backpropagation: Inversão correta dos resultados durante a subida na 
   árvore, eliminando o comportamento "suicida" detetado em versões anteriores.
'''

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
            # Assumindo que a tua jogada é um tuplo (coluna, tipo), ex: (3, 'drop')
            # Calculamos o centro dinamicamente consoante a largura do tabuleiro
            centro = len(state.board[0]) // 2 
            
            # Ordena por: 1º Proximidade ao centro, 2º Aleatoriedade para desempatar
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
            if move[1] == 'drop':
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

def mcts(state, iterations=1500, c=1.414, max_children=5):
    # ==========================================
    # NOVO: REFLEXOS BÁSICOS (1-PLY LOOKAHEAD)
    # ==========================================
    legal_moves = state.get_legal_moves()
    
    # 1. Instinto Assassino: Posso ganhar já? (Ataque)
    for move in legal_moves:
        test_state = state.apply_move(move)
        if test_state.get_winner() == state.current_player:
            # Retorna imediatamente um "nó" com a jogada vencedora!
            return Node(state=test_state, move=move)

    # 2. Instinto de Sobrevivência: O adversário ganha a seguir? (Defesa)
    safe_moves = []
    for move in legal_moves:
        test_state = state.apply_move(move)

        if test_state.is_terminal() and test_state.get_winner() != state.current_player:
            continue

        opponent_wins_next = False
        
        if not test_state.is_terminal():
            # Vê se alguma resposta do adversário dá vitória para ele
            for opp_move in test_state.get_legal_moves():
                if test_state.apply_move(opp_move).get_winner() == test_state.current_player:
                    opponent_wins_next = True
                    break
                    
        if not opponent_wins_next:
            safe_moves.append(move)

    # Se há apenas 1 jogada que nos salva de perder, fazê-la de imediato!
    if len(safe_moves) == 1:
        return Node(state=state.apply_move(safe_moves[0]), move=safe_moves[0])

    # ==========================================
    # FIM DOS REFLEXOS - INÍCIO DA ÁRVORE MCTS
    # ==========================================
    
    root = Node(state=state, max_children=max_children)
    
    # GARANTIA: Substituímos as opções da raiz APENAS por jogadas que não dão derrota imediata
    # Isto garante que o "max_children" não apaga as jogadas de bloqueio vitais!
    if safe_moves:
        random.shuffle(safe_moves)
        root.untried_moves = safe_moves[:max_children]

    for _ in range(iterations):
        node = root
        
        while not node.untried_moves and node.children:
            node = uct_best_child(node, c)
            
        if node.untried_moves:
            new_node = expand(node)
            if new_node:
                node = new_node
                
        result = rollout(node.state)
        backpropagate(node, result)
        
    best_children = sorted(root.children, key=lambda c_node: c_node.visits, reverse=True)
    
    if not best_children:
        # Se a árvore ficar encravada (muito raro), joga algo seguro
        fallback = random.choice(safe_moves) if safe_moves else random.choice(legal_moves)
        return Node(state=state.apply_move(fallback), move=fallback)
        
    # Temperatura para espalhar as aberturas do jogo
    pecas_no_tabuleiro = sum(1 for row in state.board for cell in row if cell != 0)
    if pecas_no_tabuleiro < 6 and len(best_children) >= 2:
        return random.choice(best_children[:2])
        
    return best_children[0]