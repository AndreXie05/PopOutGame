import csv
import numpy as np
import random
from collections import Counter, defaultdict
from ID3_Tree import ID3

def carregar_dataset_jogo(nome_arquivo):
    data_formatada = []
    try:
        with open(nome_arquivo, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Pula o cabeçalho (board, player, move)
            for row in reader:
                # row[0] é o board "0,0,1..."
                # row[1] é o player "1" ou "2"
                # row[2] é o move "6_drop"
                
                # Desempacota a string do tabuleiro numa lista de números
                tabuleiro = [x.strip() for x in row[0].split(',')] 
                jogador = row[1].strip()
                jogada = row[2].strip() 
                
                # Cria uma lista de atributos plana: [celula0, celula1... celula41, jogador, jogada]
                linha_completa = tabuleiro + [jogador, jogada]
                data_formatada.append(linha_completa)
        return data_formatada
    except FileNotFoundError:
        return None

def stratified_split(data, test_size=0.2, seed=42):
    random.seed(seed)
    classes_dict = defaultdict(list)
    for row in data:
        label = row[-1] # A jogada é a nossa class a prever
        classes_dict[label].append(row)
        
    train_data = []
    test_data = []
    
    for label, rows in classes_dict.items():
        random.shuffle(rows)
        split_point = int(len(rows) * (1 - test_size))
        train_data.extend(rows[:split_point])
        test_data.extend(rows[split_point:])
        
    random.shuffle(train_data)
    random.shuffle(test_data)
    
    return train_data, test_data

# --- Execução Principal ---
data = carregar_dataset_jogo("dataset.csv")

if data:
    # Divide os dados em treino e teste (mantendo as proporções das jogadas)
    train_data, test_data = stratified_split(data, test_size=0.2)

    print(f"Dataset: {len(data)} amostras totais.")
    print(f"Treino: {len(train_data)}, Teste: {len(test_data)}")
    
    # O número de features é o tamanho da linha (tabuleiro + jogador) menos 1 (a jogada)
    num_features = len(train_data[0]) - 1 
    indices_atributos = list(range(num_features))

    print("\nA treinar a Árvore de Decisão... (Isto pode demorar uns segundos)")
    modelo_id3 = ID3()
    tree = modelo_id3.construir(train_data, indices_atributos)

    # Descobre a jogada mais comum no treino (O nosso "Plano B" para tabuleiros desconhecidos)
    todas_as_jogadas = [row[-1] for row in train_data]
    jogada_mais_comum = Counter(todas_as_jogadas).most_common(1)[0][0]

    print("\nA testar com o conjunto de teste...")
    acertos = 0
    for row in test_data:
        features = row[:-1]
        real = row[-1].strip()

        # Usa o Plano B para a árvore não parar se vir um tabuleiro novo!
        res = modelo_id3.prever(tree, features, classe_default=jogada_mais_comum)
        
        if res == real:
            acertos += 1

    print("\n" + "="*45)
    print(f"Acertos: {acertos} em {len(test_data)} ({acertos/len(test_data)*100:.2f}%)")
    print("="*45)

    # Gera a imagem visual da árvore
    modelo_id3.gerar_imagem_arvore(tree, "arvore_popout")
else:
    print("Erro: dataset.csv não encontrado. Garante que já jogaste com o MCTS para gerar dados.")