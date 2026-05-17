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
            next(reader) 
            for row in reader:
                # Converte tabuleiro e jogador para float para a árvore numérica
                tabuleiro = [float(x) for x in row[0].split(',')]
                jogador = float(row[1])
                jogada = row[2].strip()
                
                # Linha: [f1, f2, ..., f42, jogador, classe]
                linha = tabuleiro + [jogador, jogada]
                data_formatada.append(linha)
        return data_formatada
    except FileNotFoundError:
        return None

def stratified_split(data, test_size=0.2, seed=42):
    """Split estratificado recebendo a lista única 'data'"""
    random.seed(seed)
    
    # Agrupa índices por classe para garantir a proporção
    classes_dict = defaultdict(list)
    for row in data:
        label = row[-1] # A classe está na última posição
        classes_dict[label].append(row)
        
    train_data = []
    test_data = []
    
    for label, rows in classes_dict.items():
        random.shuffle(rows)
        split_point = int(len(rows) * (1 - test_size))
        train_data.extend(rows[:split_point])
        test_data.extend(rows[split_point:])
    
    # Baralha os índices finais para não ficarem ordenados por classe
    random.shuffle(train_data)
    random.shuffle(test_data)
    
    return train_data, test_data

def treinar_modelo(nome_arquivo="dataset.csv"):
    """Carrega o dataset, treina a árvore e devolve (modelo, tree, fallback)."""
    data = carregar_dataset_jogo(nome_arquivo)
    if not data:
        return None, None, None

    train_data, test_data = stratified_split(data, test_size=0.2)

    modelo_id3 = ID3()
    num_atributos = len(data[0]) - 1
    indices_atributos = list(range(num_atributos))

    print("A treinar a Árvore de Decisão...")
    tree_jogo = modelo_id3.construir(train_data, indices_atributos, max_depth=10, min_samples=5)

    todas_as_jogadas = [row[-1] for row in train_data]
    fallback = Counter(todas_as_jogadas).most_common(1)[0][0]

    print("A testar com o conjunto de teste...")
    acertos = sum(
        1 for row in test_data
        if modelo_id3.prever(tree_jogo, row[:-1], classe_default=fallback) == row[-1].strip()
    )
    print("=" * 45)
    print(f"Acertos: {acertos} em {len(test_data)} ({acertos/len(test_data)*100:.2f}%)")
    print("=" * 45)

    return modelo_id3, tree_jogo, fallback