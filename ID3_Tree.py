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

    def melhor_threshold_para_atributo(self, data, atributo_index, target_index):
        """Testa vários pontos de corte e retorna o que der maior Ganho de Informação."""
        # Extrai valores únicos e ordena-os
        valores = sorted(list(set(row[atributo_index] for row in data)))
        
        # Se só houver 1 valor, não há divisão possível
        if len(valores) < 2:
            return -1, valores[0] if valores else 0

        melhor_ganho = -1
        melhor_thr = 0
        ent_total = self.entropia([row[target_index] for row in data])

        # Testar pontos médios entre valores consecutivos
        for i in range(len(valores) - 1):
            threshold_teste = (valores[i] + valores[i+1]) / 2
            
            esq = [row[target_index] for row in data if row[atributo_index] <= threshold_teste] #seleciona os que estão à esquerda do threshold atual
            dir = [row[target_index] for row in data if row[atributo_index] > threshold_teste] ##seleciona os que estão à direita do threshold atual

            #aplica a fórmula dada nas aulas
            p_esq = len(esq) / len(data) 
            p_dir = len(dir) / len(data)
            ent_ponderada = (p_esq * self.entropia(esq) + p_dir * self.entropia(dir))
            
            #ganho de informação
            ganho = ent_total - ent_ponderada
            
            #vai atualizando para encontrar o melhor ganho de informação
            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_thr = threshold_teste
                
        return melhor_ganho, melhor_thr

    # Adicionamos max_depth, min_samples e a profundidade_atual
    def construir(self, data, atributos, target_index=-1, profundidade_atual=0, max_depth=5, min_samples=10):
        """Algoritmo ID3 adaptado para múltiplos thresholds numéricos."""
        labels = [row[target_index] for row in data]

        # Caso base 1: Todos os exemplos pertencem à mesma classe
        if len(set(labels)) == 1:
            return labels[0]

        # Caso base 2: Não há mais atributos ou atingimos limites de segurança (Overfitting)
        if not atributos or (max_depth is not None and profundidade_atual >= max_depth) or (len(data) < min_samples):
            return Counter(labels).most_common(1)[0][0]

        # --- NOVA LÓGICA: PROCURA DO MELHOR CORTES EM TODOS OS ATRIBUTOS ---
        melhor_ganho_global = -1
        melhor_idx = -1
        thr_escolhido = 0

        for i in atributos:
            # Esta função testa vários pontos e devolve o melhor ganho e o ponto de corte (threshold)
            ganho, thr = self.melhor_threshold_para_atributo(data, i, target_index)
            
            if ganho > melhor_ganho_global:
                melhor_ganho_global = ganho
                melhor_idx = i
                thr_escolhido = thr

        # Se mesmo o melhor threshold não ajudar a separar os dados (ganho zero), paramos
        if melhor_ganho_global <= 0:
            return Counter(labels).most_common(1)[0][0]
        
        # --- ESTRUTURA (binária porque dividimos entre maior ou menor que o threshold) DA ÁRVORE ---
        arvore = {
            'indice': melhor_idx, #indice do atributo
            'threshold': thr_escolhido, 
            'filhos': {}
        }
        
        # Divisão dos dados com base no threshold encontrado
        sub_esq = [row for row in data if row[melhor_idx] <= thr_escolhido]
        sub_dir = [row for row in data if row[melhor_idx] > thr_escolhido]
        
        # Chamadas recursivas para os dois ramos
        # Nota: não removemos o atributo da lista 'atributos' porque ele pode 
        # ser reutilizado com um threshold diferente em níveis mais profundos!
        arvore['filhos']['<='] = self.construir(
            sub_esq, atributos, target_index, 
            profundidade_atual + 1, max_depth, min_samples
        )
        arvore['filhos']['>'] = self.construir(
            sub_dir, atributos, target_index, 
            profundidade_atual + 1, max_depth, min_samples
        )
        
        return arvore

    def prever(self, arvore, amostra, classe_default="Desconhecido"):
        if not isinstance(arvore, dict): 
            return arvore
        
        # Aceder aos novos campos da árvore
        idx = arvore['indice']
        thr = arvore['threshold']
        
        # Lógica de decisão binária
        if amostra[idx] <= thr:
            return self.prever(arvore['filhos']['<='], amostra, classe_default)
        else:
            return self.prever(arvore['filhos']['>'], amostra, classe_default)


    #foi usada para visualizar a árvore do Iris_ID3_Tree.py mas agora é inútil
    def gerar_imagem_arvore(self, arvore, nome_ficheiro="arvore_decisao"):
        dot = graphviz.Digraph(comment='ID3 Numerical', format='png')
        dot.attr('node', shape='box', style='filled, rounded', fontname='helvetica')
        self.contagem_nos = 0

        def adicionar_nos(sub_arvore, pai_id=None, valor_aresta=None):
            self.contagem_nos += 1
            no_id = str(self.contagem_nos)
            
            if not isinstance(sub_arvore, dict):
                # Nó Folha
                dot.node(no_id, f"CLASSE:\n{sub_arvore}", fillcolor='#90EE90')
            else:
                # Nó de Decisão (Acedendo às chaves 'indice' e 'threshold')
                idx = sub_arvore['indice']
                thr = round(sub_arvore['threshold'], 2)
                dot.node(no_id, f"Atributo {idx}\n(<= {thr}?)", fillcolor='#ADD8E6')
                
            if pai_id:
                dot.edge(pai_id, no_id, label=str(valor_aresta))
            
            if isinstance(sub_arvore, dict):
                # Percorre os dois ramos binários
                for relacao, filho in sub_arvore['filhos'].items():
                    adicionar_nos(filho, no_id, relacao)

        adicionar_nos(arvore)
        try:
            output_path = dot.render(nome_ficheiro, view=True)
            print(f"Imagem gerada: {output_path}")
        except Exception as e:
            print(f"Erro ao gerar imagem: {e}. Certifica-te que o Graphviz está instalado no sistema.")
