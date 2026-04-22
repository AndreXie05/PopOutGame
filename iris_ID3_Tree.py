from ID3_Tree import ID3
import numpy as np
import random
from collections import Counter

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

def carregar_iris(nome_arquivo):
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
 
        return np.array(temp_X), np.array(temp_y)
    except FileNotFoundError:
        return None

def discretizar(X_train, y_train, X_test, y_test):
    train_data = []
    medias_treino = np.mean(X_train, axis=0)
    for i in range(len(X_train)):
        linha_categorica = []
        # Primeiro: adiciona as 4 características
        for j in range(4):
            linha_categorica.append(f"Baixo_{j}" if X_train[i][j] <= medias_treino[j] else f"Alto_{j}")
        
        # Só DEPOIS do ciclo j é que adicionas o target (y)
        linha_categorica.append(y_train[i])
        # E só agora adicionas a linha completa ao dataset
        train_data.append(linha_categorica)

    test_data = []
    medias_teste = np.mean(X_test, axis=0)
    for i in range(len(X_test)):
        linha_categorica_test = []
        for j in range(4):
            linha_categorica_test.append(f"Baixo_{j}" if X_test[i][j] <= medias_teste[j] else f"Alto_{j}")
        
        linha_categorica_test.append(y_test[i])
        test_data.append(linha_categorica_test)

    return train_data, test_data

# --- Main Execution ---
X_raw, y_raw = carregar_iris("Iris_dataset.csv")
if (X_raw is not None) and (y_raw is not None):
    #Split Manual (não podemos usar sklearn acho eu)
    random.seed(42) # Para resultados consistentes

    # Criar índices e baralhar
    indices = list(range(len(X_raw)))
    random.shuffle(indices) #baralhamos os dados hihi (sei lá se têm alguma ordem associada. Só por precaução)
    
    #divisão dos dados
    split_point = int(len(X_raw) * 0.8) #fica 80% para teste e 20% para treino
    train_indices = indices[:split_point]
    test_indices = indices[split_point:]

    X_train = X_raw[train_indices]
    y_train = y_raw[train_indices]
    X_test = X_raw[test_indices]
    y_test = y_raw[test_indices]

    print(f"Dataset: {len(X_raw)} amostras. Treino: {len(X_train)}, Teste: {len(X_test)}")

    train_data , test_data = discretizar(X_train, y_train, X_test, y_test)

    modelo_id3 = ID3()

    indices_colunas = [0, 1, 2, 3] #neste caso conheço os índices porque espreitei o datasets hihi
    # 2. Construir a árvore APENAS com dados de treino
    tree_iris = modelo_id3.construir(train_data, indices_colunas)

    # 2. Descobre a classe mais comum no conjunto de TREINO
    classe_mais_comum = Counter(y_train).most_common(1)[0][0]

    # 3. Tabela de Previsão vs Real
    print("\n" + "="*45)
    print(f"{'REAL':<20} | {'PREVISTO':<20} ")
    print("-" * 45)
    
    acertos = 0
    for row in test_data:
        features = row[:-1] 
        real = row[-1].strip() 

        # 4. Passa a classe_mais_comum como o teu "Plano B"
        res = modelo_id3.prever(tree_iris, features, classe_default=classe_mais_comum) 

        if res == real:
            acertos += 1

        print(f"{real:<20} | {res:<20} ")
        print()
    
    print("="*45)
else:
    print("Erro: iris.csv não encontrado.")
