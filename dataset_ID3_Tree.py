import csv
import numpy as np
import random
from ID3_Tree import ID3

def carregar_dataset_jogo(nome_arquivo):
    data_formatada = []
    with open(nome_arquivo, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Pula o cabeçalho (board, player, move)
        for row in reader:
            # row[0] é o board "0,0,1..."
            # row[1] é o player "1"
            # row[2] é o move "6_drop"
            
            # Convertemos a string do board numa lista de strings/caracteres
            tabuleiro = row[0].split(',')
            jogador = row[1]
            jogada = row[2]
            
            # Criamos uma linha única: [celula0, celula1, ..., jogador, jogada]
            linha_completa = tabuleiro + [jogador, jogada]
            data_formatada.append(linha_completa)
            
    return data_formatada


data = carregar_dataset_jogo("dataset.csv")

if(data):

    # Split Manual (não podemos usar sklearn acho eu)
    random.seed(42) # Para resultados consistentes
    random.shuffle(data) #baralhamos os dados hihi (sei lá se têm alguma ordem associada. Só por precaução)

    #divisão dos dados
    split_point = int(len(data) * 0.8)
    train_data = data[:split_point]
    test_data = data[split_point:]

    print(f"Dataset: {len(data)} amostras. Treino: {len(train_data)}, Teste: {len(test_data)}")
    
    # O número de colunas de atributos é o tamanho de uma linha menos 1 (a jogada)
    num_features = len(train_data[0]) - 1 

    # Criamos a lista de índices das colunas: [0, 1, 2, ..., 42]
    indices_atributos = list(range(num_features))

    modelo_id3 = ID3()
    tree = modelo_id3.construir(train_data, indices_atributos)


    # Tabela de Previsão vs Real
    print("\n" + "="*45)
    print(f"{'REAL':<20} | {'PREVISTO':<20}")
    print("-" * 45)

    acertos = 0
    for row in test_data:
        features = row[:-1]
        real = row[-1].strip()

        res = modelo_id3.prever(tree, features)
        
        if res == real:
            acertos += 1

        print(f"{real:<20} | {res:<20}")
        print()

    print("="*45)
    print(acertos)

    modelo_id3.gerar_imagem_arvore(tree)
else:
    print("Erro: iris.csv não encontrado.")

    
