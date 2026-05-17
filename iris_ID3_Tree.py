from ID3_Tree import ID3
import numpy as np
import random
from collections import Counter, defaultdict

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
                
                temp_X.append([float(x) for x in partes[:4]])
                temp_y.append(partes[-1].strip())

            temp_X = np.array(temp_X)
 
        return np.array(temp_X), np.array(temp_y)
    except FileNotFoundError:
        return None, None
    

def stratified_split(X, y, test_size=0.2, seed=42):
    random.seed(seed)
    
    classes_dict = defaultdict(list)
    for idx, label in enumerate(y):
        classes_dict[label].append(idx)
        
    train_indices = []
    test_indices = []
    
    for label, indices in classes_dict.items():
        random.shuffle(indices)
        split_point = int(len(indices) * (1 - test_size))
        train_indices.extend(indices[:split_point])
        test_indices.extend(indices[split_point:])
        
    random.shuffle(train_indices)
    random.shuffle(test_indices)
    
    return train_indices, test_indices


def correr_iris(nome_arquivo="Iris_dataset.csv", test_size=0.2, seed=42):
    """
    Carrega o dataset Iris, treina a Árvore de Decisão ID3 e avalia o modelo.
    
    Parâmetros:
        nome_arquivo: caminho para o ficheiro CSV do dataset Iris
        test_size:    proporção do conjunto de teste (padrão=0.2)
        seed:         semente para reprodutibilidade (padrão=42)
    
    Retorna:
        modelo_id3:  instância treinada do ID3
        tree_iris:   árvore de decisão construída
        resultados:  dicionário com métricas e previsões
    """
    X_raw, y_raw = carregar_iris(nome_arquivo)
    
    if X_raw is None or y_raw is None:
        print("Erro: ficheiro não encontrado:", nome_arquivo)
        return None, None, None

    # Split estratificado
    idx_treino, idx_teste = stratified_split(X_raw, y_raw, test_size=test_size, seed=seed)

    # Divisão dos dados
    X_train, y_train = X_raw[idx_treino], y_raw[idx_treino]
    X_test,  y_test  = X_raw[idx_teste],  y_raw[idx_teste]

    train_data = [list(X_train[i]) + [y_train[i]] for i in range(len(X_train))]
    test_data  = [list(X_test[i])  + [y_test[i]]  for i in range(len(X_test))]

    # Treinar o modelo
    modelo_id3 = ID3()
    indices_colunas = [0, 1, 2, 3]
    tree_iris = modelo_id3.construir(train_data, indices_colunas)

    classe_mais_comum = Counter(y_train).most_common(1)[0][0]

    # Avaliação
    print("\n" + "=" * 45)
    print(f"{'REAL':<20} | {'PREVISTO':<20}")
    print("-" * 45)

    acertos = 0
    previsoes = []

    for row in test_data:
        features = row[:-1]
        real      = row[-1].strip()

        res = modelo_id3.prever(tree_iris, features, classe_default="Desconhecido")

        if res == real:
            acertos += 1

        previsoes.append({"real": real, "previsto": res, "correto": res == real})
        print(f"{real:<20} | {res:<20}")
        print()

    print("=" * 45)
    print(f"Acertos no Teste: {acertos}  |  Total: {len(X_test)}")
    print(f"Precisão: {acertos / len(X_test) * 100:.2f}%")
    print("=" * 45)

    resultados = {
        "acertos":    acertos,
        "total":      len(X_test),
        "precisao":   acertos / len(X_test),
        "previsoes":  previsoes,
        "fallback":   classe_mais_comum,
    }

    return modelo_id3, tree_iris, resultados


# --- Execução direta (quando corrido como script) ---
if __name__ == "__main__":
    correr_iris()