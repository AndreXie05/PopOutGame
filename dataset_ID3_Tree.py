import csv
import numpy as np
import random
from ID3_Tree import get_me_vertex, find_result

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

    # 1. Split Manual (não podemos usar sklearn acho eu)
    random.seed(42) # Para resultados consistentes
    random.shuffle(data) #baralhamos os dados hihi (sei lá se têm alguma ordem associada. Só por precaução)

    #divisão dos dados
    split_point = int(len(data) * 0.8)
    train_data = data[:split_point]
    test_data = data[split_point:]

    print(f"Dataset: {len(data)} amostras. Treino: {len(train_data)}, Teste: {len(test_data)}")

    tree = get_me_vertex(train_data)


    # 4. Tabela de Previsão vs Real
    print("\n" + "="*45)
    print(f"{'REAL':<20} | {'PREVISTO':<20}")
    print("-" * 45)

    acertos = 0
    for row in test_data:
        features = row[:-1]
        real = row[-1].strip()

        res = find_result(tree, features)
        
        # Limpa o resultado caso venha com o prefixo "Result: "
        res_limpo = str(res).replace("Result: ", "").strip()

        if res_limpo == real:
            acertos += 1

        print(f"{real:<20} | {res_limpo:<20}")
        print()

    print("="*45)
    print(acertos)
else:
    print("Erro: iris.csv não encontrado.")

    