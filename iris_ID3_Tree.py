from ID3_Tree import get_me_vertex, visualize_tree, find_result
import numpy as np
import random

"""
Discretização do dataset: processo de transformar valores numéricos contínuos 
(números infinitos com casas decimais) em categorias discretas (grupos ou "baldes" finitos). 
Como não poderiamos criar categorias discretas para cada valor, atribuimos a categoria alta se o valor contínuo estivel 
acima da média e baixo se for menor que a média. Vantagem: minimiza o tamanho (exigido no enunciado). 
Desvantagem: podemos perder alguma precisão/informação
Outra solução possível: intervalos de valores? (maior recisão mas árvore mais larga)
"""

"""
Problema: no ID3 se a árvore não reconhece a combinação de atributos do dado novo ela pára e retorna desconhecido. 
Possível sol: implementar um valor defeito/aumentar conjunto de treino/melhorar o find_result
"""

def carregar_e_discretizar_iris(nome_arquivo):
    data_discretizada = []
    try:
        with open(nome_arquivo, 'r') as f:
            linhas = f.readlines()
            corpo = linhas[1:] 

            temp_X = []
            temp_y = []
            for linha in corpo:
                partes = linha.strip().split(',')
                if len(partes) < 5: continue
                
                # Se aparecerem números no REAL, tente partes[5] em vez de partes[4]
                # Vamos usar partes[-1] para pegar sempre na ÚLTIMA coluna
                temp_X.append([float(x) for x in partes[:4]])
                temp_y.append(partes[-1].strip()) # strip() limpa espaços e \n

            temp_X = np.array(temp_X)
            medias = np.mean(temp_X, axis=0)

            for i in range(len(temp_X)):
                linha_categorica = []
                for j in range(4):
                    linha_categorica.append(f"Baixo_{j}" if temp_X[i][j] <= medias[j] else f"Alto_{j}")
                
                linha_categorica.append(temp_y[i])
                data_discretizada.append(linha_categorica)
        return data_discretizada
    except FileNotFoundError:
        return None
    

# --- Main Execution ---
data_iris = carregar_e_discretizar_iris("iris.csv")

if data_iris:
    # 1. Split Manual (não podemos usar sklearn acho eu)
    random.seed(42) # Para resultados consistentes
    random.shuffle(data_iris) #baralhamos os dados hihi (sei lá se têm alguma ordem associada. Só por precaução)
    
    #divisão dos dados
    split_point = int(len(data_iris) * 0.8)
    train_data = data_iris[:split_point]
    test_data = data_iris[split_point:]

    print(f"Dataset: {len(data_iris)} amostras. Treino: {len(train_data)}, Teste: {len(test_data)}")

    # 2. Construir a árvore APENAS com dados de treino
    tree_iris = get_me_vertex(train_data)

    # 3. Visualização (Gera ficheiro 'iris_tree.png')
    graph = visualize_tree(tree_iris)
    graph.render("iris_tree", view=True)
    print("Árvore visualizada e guardada como 'iris_tree.png'.")

    # 4. Tabela de Previsão vs Real
    print("\n" + "="*45)
    print(f"{'REAL':<20} | {'PREVISTO':<20}")
    print("-" * 45)
    
    acertos = 0
    for row in test_data:
        features = row[:-1]
        real = row[-1].strip()

        res = find_result(tree_iris, features)
        
        # Limpa o resultado caso venha com o prefixo "Result: "
        res_limpo = str(res).replace("Result: ", "").strip()

        if res_limpo == real:
            acertos += 1

        print(f"{real:<20} | {res_limpo:<20}")
        print()

    
    print("="*45)
else:
    print("Erro: iris.csv não encontrado.")