import random
from collections import deque

import networkx as nx
import matplotlib.pyplot as plt

class FirePreventionandFight:
    
    def __init__(
            self,
            num_vertices=None,
            num_arestas=None,
            postos_brigadistas=None,
            pontos_agua=None,
            capacidade_caminhoes=10,
            consumo_por_fogo=1,
            grafo=None
        ):
        """
        Inicializa o sistema de combate a incêndios com um grafo representando
        o ambiente, os postos dos brigadistas, pontos de água, capacidade dos
        caminhões e consumo de água por foco de incêndio.

        Parâmetros:
        - num_vertices (int): número total de vértices no grafo (opcional se grafo for passado).
        - num_arestas (int): número de arestas (opcional se grafo for passado).
        - postos_brigadistas (list[int]): vértices com postos de brigadistas.
        - pontos_agua (list[int]): vértices com fontes de água.
        - capacidade_caminhoes (int): capacidade de água por caminhão.
        - consumo_por_fogo (int): quantidade de água consumida por foco de fogo.
        - grafo (nx.Graph): grafo customizado já construído (opcional).
        """

        # Define o consumo de água por foco de incêndio
        self.consumo_por_fogo = consumo_por_fogo

        # Define a capacidade de água dos caminhões
        self.capacidade_caminhoes = capacidade_caminhoes

        # Inicializa o dicionário de brigadistas
        self.brigadistas = {}

        # Lista para armazenar os focos de fogo ativos
        self.fogo_ativo = []

        # Lista para armazenar os focos de fogo que já foram apagados
        self.fogos_apagados = []

        # Verifica se um grafo já foi fornecido
        if grafo is not None:

            # Atribui o grafo fornecido à instância
            self.grafo = grafo

            # Converte a lista de postos de brigadistas para um conjunto
            self.postos_brigadistas = set(postos_brigadistas or [])

            # Para cada nó do grafo, define atributos padrão
            for i in self.grafo.nodes:
                self.grafo.nodes[i].setdefault('fogo', False)
                self.grafo.nodes[i].setdefault('agua', False)
                self.grafo.nodes[i].setdefault('queimado', False)

                # Define se o nó é um posto de brigadistas
                self.grafo.nodes[i]['posto_brigadista'] = i in self.postos_brigadistas

            # Inicializa os brigadistas nos respectivos postos
            for p in self.postos_brigadistas:
                self.brigadistas[p] = (p, self.capacidade_caminhoes)

                # Marca o posto como contendo água
                self.grafo.nodes[p]['agua'] = True

            # Marca os pontos de água adicionais no grafo
            for p in pontos_agua or []:
                self.grafo.nodes[p]['agua'] = True

        else:
            # Se nenhum grafo for passado, número de vértices e arestas são obrigatórios
            if num_vertices is None or num_arestas is None:
                raise ValueError("Se o grafo não for fornecido, num_vertices e num_arestas são obrigatórios.")

            # Cria um novo grafo vazio
            self.grafo = nx.Graph()

            # Converte a lista de postos de brigadistas para um conjunto
            self.postos_brigadistas = set(postos_brigadistas or [])

            # Adiciona vértices ao grafo com atributos padrão
            for i in range(num_vertices):
                self.grafo.add_node(
                    i,
                    fogo=False,
                    agua=False,
                    queimado=False,
                    posto_brigadista=(i in self.postos_brigadistas)
                )

            # Gera arestas aleatórias com pesos entre os vértices
            arestas_adicionadas = set()
            while len(arestas_adicionadas) < num_arestas:
                u, v = random.sample(range(num_vertices), 2)

                # Adiciona aresta se ainda não tiver sido criada
                if (u, v) not in arestas_adicionadas and (v, u) not in arestas_adicionadas:
                    peso = random.randint(1, 10)
                    self.grafo.add_edge(u, v, weight=peso)
                    arestas_adicionadas.add((u, v))

            # Inicializa os brigadistas nos respectivos postos
            for p in self.postos_brigadistas:
                self.brigadistas[p] = (p, self.capacidade_caminhoes)

                # Marca o posto como contendo água
                self.grafo.nodes[p]['agua'] = True

            # Marca os pontos de água adicionais no grafo
            for p in pontos_agua or []:
                self.grafo.nodes[p]['agua'] = True

        # Calcula posições dos nós para visualização com layout de molas
        self.pos = nx.spring_layout(self.grafo)



    def iniciar_fogo(self, inicio):
        """
        Inicia um foco de incêndio em um vértice do grafo, desde que o local
        não possua água, não tenha sido queimado anteriormente e não seja um
        posto de brigadistas.

        Parâmetros:
        - inicio (int): índice do vértice onde o fogo deve começar.

        A função verifica se é possível iniciar o fogo no local:
        - Não pode iniciar fogo em locais com fonte de água.
        - Não pode iniciar fogo em locais já queimados.
        - Não pode iniciar fogo em postos de brigadistas.
        Caso o local seja válido, marca o vértice com fogo e adiciona à lista
        de focos ativos.
        """
        # Não inicia fogo em locais inválidos
        if (self.grafo.nodes[inicio]['agua'] or
            self.grafo.nodes[inicio]['queimado'] or
            self.grafo.nodes[inicio]['posto_brigadista']):
            return  

        # Marca o vértice como com fogo ativo
        self.fogo_ativo.append(inicio)
        self.grafo.nodes[inicio]['fogo'] = True


    def propagar_fogo(self):
        """
        Propaga o fogo utilizando busca em largura (BFS) a partir dos vértices atualmente em chamas.

        A propagação só ocorre se o vértice vizinho:
        - Não estiver em chamas.
        - Não tiver fonte de água.
        - Não tiver sido queimado anteriormente.
        - Não for um posto de brigadistas.

        Os novos focos são marcados e adicionados à lista de fogo ativo.
        """
        fila = deque(self.fogo_ativo)  # Fila BFS inicial com os vértices em chamas
        visitados = set(self.fogo_ativo)  # Para evitar reprocessar vértices

        novos_focos = []

        while fila:
            atual = fila.popleft()

            for vizinho in self.grafo.neighbors(atual):
                if (vizinho not in visitados and
                    not self.grafo.nodes[vizinho]['fogo'] and
                    not self.grafo.nodes[vizinho]['agua'] and
                    not self.grafo.nodes[vizinho]['queimado'] and
                    not self.grafo.nodes[vizinho]['posto_brigadista']):
                    
                    # Marca o vizinho como novo foco
                    self.grafo.nodes[vizinho]['fogo'] = True
                    novos_focos.append(vizinho)
                    fila.append(vizinho)
                    visitados.add(vizinho)

        # Atualiza a lista de fogo ativo
        self.fogo_ativo.extend(novos_focos)


    def apagar_fogo(self, vertice):
        """
        Apaga o fogo em um vértice específico do grafo.

        Parâmetros:
        - vertice (int): índice do vértice onde o fogo será apagado.

        A função realiza as seguintes ações:
        - Marca o vértice como não estando mais em chamas.
        - Marca o vértice como queimado (registro do incêndio).
        - Remove o vértice da lista de focos de fogo ativos.
        - Adiciona o vértice à lista de fogos apagados.
        """

        # Marca o vértice como não estando mais em chamas
        self.grafo.nodes[vertice]['fogo'] = False

        # Marca o vértice como queimado (registro do incêndio)
        self.grafo.nodes[vertice]['queimado'] = True

        # Remove o vértice da lista de focos de fogo ativos
        self.fogo_ativo.remove(vertice)

        # Adiciona o vértice à lista de fogos apagados
        self.fogos_apagados.append(vertice)


    def caminho_mais_curto(self, origem, destino):
        """
        Calcula o caminho mais curto entre dois vértices no grafo,
        usando o algoritmo dijkstra que leva
        em consideração os pesos das arestas.

        Parâmetros:
        - origem (int): vértice de partida.
        - destino (int): vértice de chegada.

        Retorna:
        - Lista com os vértices do caminho mais curto, incluindo origem e
        destino, ou None se não houver caminho entre os dois vértices.
        """

        # Calcular o caminho mais curto usando Dijkstra com base nos pesos das arestas
        try:
            return nx.shortest_path(
                self.grafo,          # Grafo no qual será buscado o caminho
                source=origem,       # Vértice de origem
                target=destino,      # Vértice de destino
                weight='weight'      # Considera o peso das arestas
            )

        # Se não existir caminho possível entre os dois vértices, retorna None
        except nx.NetworkXNoPath:
            return None


    def enviar_brigadistas(self):
        """
        Move os brigadistas pelo grafo para combater os focos de incêndio
        ou reabastecer água, conforme necessário.

        A lógica funciona da seguinte forma:
        - Se não há fogo ativo, a função retorna imediatamente.
        - Para cada brigadista:
            - Se estiver sem água, ele é enviado ao ponto de reabastecimento
            mais próximo.
            - Caso tenha água, ele é enviado ao foco de fogo mais próximo.
        - A posição e a quantidade de água do brigadista são atualizadas
        conforme ele se move.

        Observações:
        - A movimentação é baseada no caminho mais curto (menor peso).
        - Os focos ativos e pontos de reabastecimento são dinâmicos.
        """

        # Verifica se há algum foco de fogo ativo; se não houver, retorna imediatamente
        if not self.fogo_ativo:
            return  

        # Itera sobre todos os brigadistas e suas respectivas posições e níveis de água
        for brigadista, (posicao_atual, agua) in self.brigadistas.items():

            # Se o brigadista não tem água suficiente para apagar o fogo
            if agua < self.consumo_por_fogo:

                # Encontra o ponto de reabastecimento mais próximo usando caminho mais curto
                ponto_reabastecimento = min(
                    (n for n in self.grafo.nodes if self.grafo.nodes[n]['agua']),
                    key=lambda p: nx.shortest_path_length(
                        self.grafo, posicao_atual, p, weight='weight'
                    ),
                    default=None
                )

                # Se encontrou um ponto de reabastecimento
                if ponto_reabastecimento:
                    print(
                        f"💧 Brigadista {brigadista} sem água indo reabastecer "
                        f"em {ponto_reabastecimento}."
                    )

                    # Atualiza a posição do brigadista e recarrega a água
                    self.brigadistas[brigadista] = (
                        ponto_reabastecimento, self.capacidade_caminhoes
                    )

                # Passa para o próximo brigadista
                continue

            # Se o brigadista tem água, encontra o foco de fogo mais próximo
            foco_mais_proximo = min(
                (f for f in self.fogo_ativo if f != posicao_atual),
                key=lambda f: nx.shortest_path_length(
                    self.grafo, posicao_atual, f, weight='weight'
                ),
                default=None
            )

            # Se encontrou um foco mais próximo
            if foco_mais_proximo:

                # Obtém o caminho mais curto até o foco
                caminho = self.caminho_mais_curto(posicao_atual, foco_mais_proximo)

                # Se o caminho foi encontrado com sucesso
                if caminho:

                    # Move o brigadista ao longo do caminho e atualiza sua posição e água restante
                    self.brigadistas[brigadista] = self.deslocar_brigadista(
                        brigadista, caminho, agua
                    )

                        
    def encontrar_caminho_ate_agua_ou_posto(self, origem):
        """
        Encontra o caminho mais curto de 'origem' até um ponto com água 
        ou um posto de brigadistas, para reabastecimento.

        Parâmetros:
        - origem (str): o nó atual onde o brigadista se encontra.

        Retorna:
        - list[str] | None: lista de nós que compõem o caminho mais curto 
        até o ponto de reabastecimento. Retorna None se não houver caminho.
        """

        # Filtra os nós do grafo que têm água ou são postos de brigadistas
        destinos_possiveis = [
            n for n in self.grafo.nodes
            if self.grafo.nodes[n].get('agua') or
            self.grafo.nodes[n].get('posto_brigadista')
        ]

        # Inicializa o menor caminho como None e a menor distância como infinita
        menor_caminho = None
        menor_distancia = float('inf')

        # Itera sobre todos os destinos possíveis para encontrar o mais próximo
        for destino in destinos_possiveis:
            try:
                # Calcula o caminho mais curto entre a origem e o destino atual
                caminho = nx.shortest_path(
                    self.grafo, origem, destino, weight='weight'
                )

                # Calcula o comprimento (peso total) do caminho encontrado
                distancia = nx.shortest_path_length(
                    self.grafo, origem, destino, weight='weight'
                )

                # Atualiza o menor caminho e distância, se esse for melhor
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    menor_caminho = caminho

            # Ignora o destino se não houver caminho até ele
            except nx.NetworkXNoPath:
                continue


            return menor_caminho
        
    def deslocar_brigadista(self, brigadista, caminho, agua):
        """
        Move o brigadista ao longo do caminho indicado ou até um ponto
        de reabastecimento se estiver sem água. Apaga o fogo ao final.

        Parâmetros:
        - brigadista (str): nome ou ID do brigadista.
        - caminho (list[str]): lista de nós representando o trajeto.
        - agua (int): quantidade atual de água do brigadista.

        Retorna:
        - tuple(str, int): nova posição do brigadista e nova quantidade de água.
        """

        # Se não houver caminho, retorna a posição atual do brigadista
        if not caminho:
            print(f"🧭 Caminho percorrido por {brigadista}: nenhum (sem deslocamento)")
            return self.brigadistas[brigadista]

        # Define a posição inicial, destino final e o trecho intermediário
        posicao_atual = caminho[0]
        destino = caminho[-1]
        caminho_percorrido = caminho[1:-1]

        # Se o brigadista está sem água, tenta encontrar ponto de reabastecimento
        if agua <= 0:
            print(f"🚫 Brigadista {brigadista} está sem água. "
                f"Buscando ponto de reabastecimento...")

            caminho_ate_agua = self.encontrar_caminho_ate_agua_ou_posto(posicao_atual)

            if caminho_ate_agua:
                nova_posicao = caminho_ate_agua[-1]
                print(f"💧 Brigadista {brigadista} indo reabastecer em "
                    f"{nova_posicao} via {caminho_ate_agua}")
                print(f"🧭 Caminho percorrido por {brigadista}: {caminho_ate_agua}")
                return (nova_posicao, self.capacidade_caminhoes)

            print(f"🛑 Brigadista {brigadista} não encontrou ponto de água.")
            print(f"🧭 Caminho percorrido por {brigadista}: nenhum (sem deslocamento)")
            return self.brigadistas[brigadista]

        # Mensagem de deslocamento do brigadista com água suficiente
        print(f"🚒 Brigadista {brigadista} ({agua}L) saindo de {posicao_atual} "
            f"para apagar fogo em {destino}. Passou por {caminho_percorrido}")
        print(f"🧭 Caminho percorrido por {brigadista}: {caminho}")

        # Verifica se há ponto de água no caminho e reabastece se encontrar
        for v in caminho_percorrido:
            if self.grafo.nodes[v]['agua']:
                print(f"💧 Brigadista {brigadista} reabastecendo em {v}.")
                return (v, self.capacidade_caminhoes)

        # Se o destino tiver fogo, apaga e consome água
        if self.grafo.nodes[destino]['fogo']:
            self.apagar_fogo(destino)
            agua -= self.consumo_por_fogo
            print(f"🔥 Fogo apagado em {destino} pelo brigadista {brigadista} "
                f"(Restante: {agua}L).")
            return (destino, agua)

        # Se não há fogo no destino, apenas atualiza a posição
        return (destino, agua)


    def simular(self, inicio_fogo):
        """
        Inicia e executa a simulação da propagação e combate ao fogo.

        Parâmetro:
        - inicio_fogo (int): vértice onde o fogo começa.

        Lógica:
        - Inicia o fogo no vértice especificado.
        - Exibe o estado inicial do grafo.
        - Enquanto houver fogo ativo:
            * Propaga o fogo para os vizinhos.
            * Envia brigadistas para tentar apagá-lo.
            * Exibe os estados atualizados do grafo.
        - Ao final, imprime os vértices onde os fogos foram apagados.
        """

        # Inicia o fogo no vértice especificado
        self.iniciar_fogo(inicio_fogo)

        # Exibe o estado inicial do grafo
        print("🖼️ Exibindo estado inicial do grafo...")
        self.desenhar_grafo(1)

        estado = 2
        # Loop enquanto ainda houver fogo ativo no grafo
        while self.fogo_ativo:
            # Propaga o fogo para os vértices vizinhos
            self.propagar_fogo()
            print('estado:',estado)
            # Exibe os vértices com fogo antes da atuação dos brigadistas
            print(
                "🔥 Fogo ativo nos vértices antes da ação dos brigadistas: "
                f"{sorted(self.fogo_ativo)}"
            )

            # Envia os brigadistas para combater o fogo
            self.enviar_brigadistas()

            # Exibe os vértices com fogo após a atuação dos brigadistas
            print(
                "🔥 Fogo ativo nos vértices após a ação dos brigadistas: "
                f"{sorted(self.fogo_ativo)}"
            )

            # Atualiza a visualização do grafo com o estado atual
            self.desenhar_grafo(estado)
            estado += 1

        # Exibe os vértices nos quais o fogo foi apagado ao final da simulação
        print(
            f"✅ Simulação concluída. Fogos apagados: "
            f"{sorted(self.fogos_apagados)}"
        )
            
    def desenhar_grafo(self, estado):
        """
        Exibe graficamente o estado atual do grafo durante a simulação.

        Parâmetro:
        - estado (int): número que representa o estágio atual da simulação.

        Lógica:
        - Define a cor dos nós com base no seu estado:
            * 🔴 Vermelho: está pegando fogo
            * 🟡 Amarelo: ocupado por um brigadista
            * 🔵 Azul: possui água ou é posto de brigadista
            * ⚫ Cinza: já foi queimado
            * 🟢 Verde: está seguro
        - Desenha o grafo com seus nós, arestas e pesos.
        - Exibe o gráfico por 1.5 segundos.
        """

        # Limpa o gráfico anterior
        plt.clf()

        node_colors = []
        # Percorre todos os nós do grafo para determinar sua cor com base no estado
        for n in self.grafo.nodes:
            if self.grafo.nodes[n]['fogo']:
                # 🔴 Nó em chamas
                node_colors.append('red')
            elif any(self.brigadistas[b][0] == n for b in self.brigadistas):
                # 🟡 Brigadista presente neste nó
                node_colors.append('yellow')
            elif (self.grafo.nodes[n]['agua'] or
                self.grafo.nodes[n]['posto_brigadista']):
                # 🔵 Ponto com água ou posto de brigadistas
                node_colors.append('blue')
            elif self.grafo.nodes[n]['queimado']:
                # ⚫ Nó já queimado
                node_colors.append('gray')
            else:
                # 🟢 Nó seguro
                node_colors.append('green')

        # Define o tamanho da figura do gráfico
        plt.figure(figsize=(10, 8))

        # Desenha os nós e as arestas do grafo com rótulos
        nx.draw(
            self.grafo,
            self.pos,
            with_labels=True,
            node_size=500,
            node_color=node_colors,
            font_size=10
        )

        # Obtém os rótulos das arestas (os pesos de cada conexão)
        edge_labels = nx.get_edge_attributes(self.grafo, 'weight')

        # Desenha os rótulos das arestas (pesos) no grafo
        nx.draw_networkx_edge_labels(
            self.grafo,
            self.pos,
            edge_labels=edge_labels,
            font_size=9
        )

        # Título indicando o estado atual da simulação
        plt.title(f"Estado Atual do Grafo [estado {estado}]")

        # Atualiza e exibe o gráfico, pausando por 1.5 segundos para visualização
        plt.draw()
        plt.pause(1.5)
