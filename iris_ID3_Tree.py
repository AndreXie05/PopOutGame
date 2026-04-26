from ID3_Tree import ID3
import numpy as np
import random
from collections import Counter, defaultdict

"""
Discretização do dataset: processo de transformar valores numéricos contínuos 
(números infinitos com casas decimais) em categorias discretas (grupos ou "baldes" finitos). 
Como não poderiamos criar categorias discretas para cada valor, atribuimos a categoria alta se o valor contínuo estiver 
acima do melhor threshold e baixo se for menor. Vantagens: minimiza o tamanho (exigido no enunciado) e garante que não 
haverá um valor de atributo desconhecido no teste, o que causaria problemas na previsão
Desvantagem: podemos perder alguma precisão/informação
NOTA: agora este processo é feito no ficheiro ID3_Tree
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
                if len(partes) < 5: continue #verificação porque sabemos que o iris tem 5 colunas
                
                #os X são até à coluna 3 [0, 1, 2, 3] e os y são a última coluna
                temp_X.append([float(x) for x in partes[:4]])
                temp_y.append(partes[-1].strip()) # strip() limpa espaços e \n


            temp_X = np.array(temp_X)
 
        return np.array(temp_X), np.array(temp_y)
    except FileNotFoundError:
        return None, None
    

def stratified_split(X, y, test_size=0.2, seed=42):
    random.seed(seed)
    
    # Agrupa índices por classe para garantir a proporção
    classes_dict = defaultdict(list)
    for idx, label in enumerate(y):
        classes_dict[label].append(idx)
        
    train_indices = []
    test_indices = []
    
    for label, indices in classes_dict.items():
        random.shuffle(indices) #baralhamos os dados (neste caso os índices que vamos usar para selecionar os dados)
        split_point = int(len(indices) * (1 - test_size))
        train_indices.extend(indices[:split_point])
        test_indices.extend(indices[split_point:])
        
    # Baralha os índices finais para não ficarem ordenados por classe
    random.shuffle(train_indices)
    random.shuffle(test_indices)
    
    return train_indices, test_indices


# --- Main Execution ---
X_raw, y_raw = carregar_iris("Iris_dataset.csv")
if (X_raw is not None) and (y_raw is not None):

    #Split estratificado
    idx_treino, idx_teste = stratified_split(X_raw, y_raw, test_size=0.2)

    #Divisão dos dados
    X_train, y_train = X_raw[idx_treino], y_raw[idx_treino]
    X_test, y_test = X_raw[idx_teste], y_raw[idx_teste]

    # Já não chamamos a função discretizar()
    train_data = [list(X_train[i]) + [y_train[i]] for i in range(len(X_train))]
    test_data = [list(X_test[i]) + [y_test[i]] for i in range(len(X_test))]


    # Instanciar e treinar o modelo
    modelo_id3 = ID3()
    indices_colunas = [0, 1, 2, 3] 
    tree_iris = modelo_id3.construir(train_data, indices_colunas)

    #Descobre a classe mais comum no conjunto de TREINO
    classe_mais_comum = Counter(y_train).most_common(1)[0][0]

    #Tabela de Previsão vs Real
    print("\n" + "="*45)
    print(f"{'REAL':<20} | {'PREVISTO':<20} ")
    print("-" * 45)
    
    acertos = 0
    for row in test_data:
        features = row[:-1] 
        real = row[-1].strip() 

        # 4. Passa a classe_mais_comum como o teu "Plano B"
        res = modelo_id3.prever(tree_iris, features, classe_default="Desconhecido") 

        if res == real:
            acertos += 1

        print(f"{real:<20} | {res:<20} ")
        print()
    
    print("="*45)

    print("Acertos no Teste: ", acertos, " Linhas no Teste: ", len(X_test))
else:
    print("Erro: iris.csv não encontrado.")
