import math
from graphviz import Digraph
from collections import Counter

def calculate_whole_entropy(data, feature_index):
    total_samples = len(data)
    feature_entropy = 0.0

    unique_values = set(data[i][feature_index] for i in range(total_samples))

    # print("unique_values", unique_values)

    for value in unique_values:
        subset_data = [data[i] for i in range(
            total_samples) if data[i][feature_index] == value]

        subset_size = len(subset_data)
        # print(subset_size)

        if subset_size == 0:
            continue

        class_counts = [row[-1] for row in subset_data]

        # class_probabilities = [class_counts.count(
        #     c) / subset_size for c in set(class_counts)]

        class_probabilities = len(class_counts) / total_samples

        subset_entropy = -class_probabilities * math.log2(class_probabilities)

        # print(class_probabilities)
        # print(subset_entropy)

        feature_entropy += subset_entropy

    return feature_entropy


def calculate_feature_entropy(data, feature_index):
    total_samples = len(data)
    feature_entropy = 0.0
    subset_entropies = []  # Create an array to store subset entropies

    unique_values = set(data[i][feature_index] for i in range(total_samples))

    # print("unique_values", unique_values)

    for value in unique_values:
        subset_data = [data[i] for i in range(
            total_samples) if data[i][feature_index] == value]

        subset_size = len(subset_data)

        if subset_size == 0:
            continue

        class_counts = [row[-1] for row in subset_data]
        class_probabilities = [class_counts.count(
            c) / subset_size for c in set(class_counts)]

        subset_entropy = 0.0

        for p in class_probabilities:
            if p > 0:
                subset_entropy -= p * math.log2(p)

        feature_entropy += (subset_size / total_samples) * subset_entropy

        # Store (value, subset_entropy) tuple
        subset_entropies.append((value, subset_entropy))

        # print("value:", value)
        # print("class_probabilities:", class_probabilities)
        # print("subset_size:", subset_size)
        # print("subset_entropy:", subset_entropy)
        # print("subset_entropies:", subset_entropies)
        # print("entropy (probability * Ent):", (subset_size / total_samples), " * ", subset_entropy, " = ",
        #       (subset_size / total_samples) * subset_entropy)

    # Return both the feature entropy and subset entropies
    # print("feature_entropy:", feature_entropy)
    # print("\n")
    return feature_entropy, subset_entropies


def calculate_information_gain(data):
    target_entropy = calculate_whole_entropy(data, feature_index=-1)
    num_features = len(data[0]) - 1  # Exclude the target feature
    information_gains = []

    for feature_index in range(num_features):
        feature_entropy, subset_entropies = calculate_feature_entropy(
            data, feature_index)
        information_gain = target_entropy - feature_entropy
        information_gains.append((information_gain, subset_entropies))

    return information_gains


def get_me_max_gain(information_gains):
    maxGain = (0, (0, []))
    for i, ig in enumerate(information_gains):
        # print(maxGain[1])
        if maxGain[1][0] < ig[0]:
            maxGain = (i, ig)

    return maxGain


def get_the_decision(data, feature_index, value):
    res = ""

    for tuple in data:
        if (tuple[feature_index] == value):
            res = tuple[-1]
            break

    return res


def get_me_new_data(data, feature_index, value):
    newData = []

    for tuple in data:
        if (tuple[feature_index] == value):
            # row_without_first_element = tuple[1:]
            touple_without_index_element = tuple[:feature_index] + \
                tuple[feature_index+1:]
            newData.append(touple_without_index_element)
            # print(touple_without_index_element)

    return newData


# -----------Calculate the entropy of the 'buys computer' feature (last column)

# buys_computer_entropy = calculate_whole_entropy(data, feature_index=-1)
# print("Entropy of the 'buys computer' feature:", buys_computer_entropy)

# -----------Modify this to the index of the feature you want to calculate entropy for

# feature_index = 3
# feature_entropy, subset_entropies = calculate_feature_entropy(
#     data, feature_index)
# print("Entropy of the specified feature:", feature_entropy)
# print("Subset entropies:", subset_entropies)
# print("IG:", buys_computer_entropy - feature_entropy)

"""
retorna uma lista de tuplas aninhadas que representa a estrutura hierárquica da árvore. É, essencialmente, um dicionário construído com listas onde cada nível da árvore é uma nova lista dentro da anterior.

Aqui está o que compõe cada tupla retornada: (valor_do_atributo, resultado).
"""

def get_me_vertex(data):

    information_gains = calculate_information_gain(data)

    # Print the information gains for each feature
    # for i, ig in enumerate(information_gains):
    #     print(f"Information Gain for feature {i}: {ig}")

    # -----------returns maxGain = (vertex feature number, (gain, [subset_entropies]))
    maxGain = get_me_max_gain(information_gains=information_gains)

    root_vertex = maxGain[0]
    res_touple = maxGain[1][1]
    # print(root_vertex)
    # print(res_touple)

    temp_dictionary = []
    for i in res_touple:
        sub_touple = ()
        if (i[1] == 0): #se a entropia for 0, cria um nó folha
            decision = get_the_decision(data, root_vertex, i[0])
            # print("FORM_if: ", i[0])
            # print((i[0], decision))

            sub_touple = (decision)

        else: #se não, gera um novo subset = faz split
            # break
            newData = []
            # print("FORM_else: ", i[0])
            newData = get_me_new_data(data, root_vertex, i[0])

            sub_touple = get_me_vertex(newData)
            # print("tempRes inside: ", sub_touple)

        #print("\n")

        temp_dictionary.append((i[0], sub_touple))

    return temp_dictionary

def find_result(tree, input_data):
    if not isinstance(tree, list):
        return tree

    # 1. Tentativa de correspondência exata
    for branch in tree:
        valor_no_ramo, conteudo = branch
        if valor_no_ramo in input_data:
            if isinstance(conteudo, list):
                res = find_result(conteudo, input_data)
                if res != "Desconhecido":
                    return res
            else:
                return conteudo

    # 2. Se chegou aqui, não encontrou o ramo exato. 
    # Sol. temporária: Em vez de retornar "Desconhecido", tentamos atribuir-lhe o valor da maioria?
    return obter_voto_majoritario(tree)

def obter_voto_majoritario(item):
    """
    Percorre todos os ramos abaixo deste nó e conta qual a classe 
    que aparece mais vezes para dar um palpite educado.
    """
    folhas = []
    
    def extrair_folhas(obj):
        if not isinstance(obj, list):
            folhas.append(obj)
        else:
            for b in obj:
                extrair_folhas(b[1]) #se não for folha percorre os tuples, nomeadamente a pos 1 dos tuples, 
                #quer isso seja uma folha quer seja outro ramo(lista de tuples)
    
    extrair_folhas(item)
    
    if not folhas:
        return "Desconhecido"
    
    # Retorna a classe mais frequente entre as folhas deste ramo
    return Counter(folhas).most_common(1)[0][0]

def visualize_tree(tree, parent_id=None, edge_label="", graph=None):
    if graph is None:
        graph = Digraph(format='png', engine='dot')
        graph.attr('node', shape='ellipse')

    for branch in tree:
        attr_value, content = branch
        
        # Criar um ID único para este nó baseado no hash da estrutura
        node_id = str(id(branch))
        
        if isinstance(content, list):
            # É um nó de decisão (sub-árvore)
            graph.node(node_id, label=f"Atributo?")
            if parent_id:
                graph.edge(parent_id, node_id, label=str(attr_value))
            visualize_tree(content, parent_id=node_id, graph=graph)
        else:
            # É um nó folha
            leaf_id = str(id(content)) + str(node_id)
            graph.node(leaf_id, label=str(content), shape='box', color='green')
            if parent_id:
                graph.edge(parent_id, leaf_id, label=str(attr_value))
    
    return graph

