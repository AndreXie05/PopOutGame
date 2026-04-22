import math
from collections import Counter
import graphviz

class ID3:
    def __init__(self):
        self.tree = {}

    def entropia(self, labels):
        """Calcula a entropia de um conjunto de etiquetas (alvos)."""
        contagem = Counter(labels)
        total = len(labels)
        ent = 0
        for classe in contagem:
            p = contagem[classe] / total
            ent -= p * math.log2(p)
        return ent

    def ganho_informacao(self, data, atributo_index, target_index):
        """Calcula o ganho de informação ao dividir por um atributo."""
        # Entropia total do conjunto atual
        ent_total = self.entropia([row[target_index] for row in data])
        
        # Calcular entropia ponderada dos subconjuntos
        valores_atributo = set(row[atributo_index] for row in data) #cria um set com todos os valores que aparecem naquela coluna
        ent_subconjuntos = 0
        for valor in valores_atributo: #percorre os valores desse atributo 
            subconjunto = [row for row in data if row[atributo_index] == valor] #filtra as linhas que tÊm aquele valor específico
            prob = len(subconjunto) / len(data) #vê o peso com base na proporção de casos
            ent_subconjuntos += prob * self.entropia([row[target_index] for row in subconjunto]) #calcula a entropia ponderada e adiciona ao valor do split do atributo
        
        return ent_total - ent_subconjuntos #retorna a information gain de fazer split nesse atributo

    # Adicionamos max_depth, min_samples e a profundidade_atual
    def construir(self, data, atributos, target_index=-1, profundidade_atual=0, max_depth=5, min_samples=10):
        """Algoritmo recursivo principal com prevenção de Overfitting."""
        labels = [row[target_index] for row in data]

        # Caso base 1: Todos os exemplos pertencem à mesma classe
        if len(set(labels)) == 1:
            return labels[0]

        # Caso base 2: Não há mais atributos para dividir
        if not atributos:
            return Counter(labels).most_common(1)[0][0]

        # Se atingimos a profundidade máxima OU se temos muito poucos dados
        if (max_depth is not None and profundidade_atual >= max_depth) or (len(data) < min_samples):
            # Para e devolve a jogada mais comum neste ramo
            return Counter(labels).most_common(1)[0][0]

        # Escolher o melhor atributo (maior Ganho de Informação)
        ganhos = [self.ganho_informacao(data, i, target_index) for i in atributos]
        melhor_atributo_idx = atributos[ganhos.index(max(ganhos))]
        
        arvore = {melhor_atributo_idx: {}}
        
        valores = set(row[melhor_atributo_idx] for row in data)
        novos_atributos = [i for i in atributos if i != melhor_atributo_idx]

        for valor in valores:
            sub_data = [row for row in data if row[melhor_atributo_idx] == valor]
            
            # NOVO: Passar os novos limites e aumentar a profundidade nas chamadas recursivas
            arvore[melhor_atributo_idx][valor] = self.construir(
                sub_data, novos_atributos, target_index, 
                profundidade_atual + 1, max_depth, min_samples
            )
            
        return arvore

    def prever(self, arvore, amostra, classe_default="Desconhecido"):
        """Navega na árvore para prever a classe de uma nova amostra."""
        if not isinstance(arvore, dict): 
            return arvore
        
        atributo = list(arvore.keys())[0] 
        valor = amostra[atributo] 
        
        if valor in arvore[atributo]:
            return self.prever(arvore[atributo][valor], amostra, classe_default) 
        else:
            return classe_default

    def gerar_imagem_arvore(self, arvore, nome_ficheiro="arvore_decisao"):
        """Gera e guarda uma imagem .png da árvore usando a biblioteca Graphviz."""
        if graphviz is None:
            print("Erro: A biblioteca 'graphviz' não foi encontrada no Anaconda.")
            print("Instala-a com: conda install python-graphviz")
            return

        # Criar o objeto Digraph (Direcionado)
        dot = graphviz.Digraph(comment='Árvore de Decisão ID3', format='png')
        dot.attr(rankdir='TB', size='10,10')
        
        # Configuração visual dos nós
        dot.attr('node', shape='box', style='filled, rounded', fontname='helvetica')

        self.contagem_nos = 0

        def adicionar_nos(sub_arvore, pai_id=None, valor_aresta=None):
            self.contagem_nos += 1
            no_id = str(self.contagem_nos)
            
            if not isinstance(sub_arvore, dict):
                # É um nó folha (Resultado)
                dot.node(no_id, f"JOGADA:\n{sub_arvore}", fillcolor='#90EE90') # Verde claro
            else:
                # É um nó de decisão (Atributo)
                atributo = list(sub_arvore.keys())[0]
                dot.node(no_id, f"Índice: {atributo}", fillcolor='#ADD8E6') # Azul claro
                
            # Se houver um pai, cria a ligação (aresta)
            if pai_id:
                dot.edge(pai_id, no_id, label=str(valor_aresta))
            
            # Se for dicionário, continua a recursão
            if isinstance(sub_arvore, dict):
                atributo = list(sub_arvore.keys())[0]
                for valor, filho in sub_arvore[atributo].items():
                    adicionar_nos(filho, no_id, valor)

        adicionar_nos(arvore)
        
        # Guarda e tenta abrir a imagem automaticamente
        output_path = dot.render(nome_ficheiro, view=True)
        print(f"Sucesso! Imagem gerada em: {output_path}")
