import networkx as nx
import random
import matplotlib.pyplot as plt

class FirePreventionandFight:
    
    def __init__(
                self,
                num_vertices,
                num_arestas,
                postos_brigadistas,
                pontos_agua,
                capacidade_caminhoes,
                consumo_por_fogo=1
                ):
        """
        Inicializa o sistema de combate a incêndios com um grafo representando
        o ambiente, os postos dos brigadistas, pontos de água, capacidade dos
        caminhões e consumo de água por foco de incêndio.

        Parâmetros:
        - num_vertices (int): número total de vértices no grafo.
        - num_arestas (int): número de arestas (conexões entre vértices).
        - postos_brigadistas (list[int]): vértices com postos de brigadistas.
        - pontos_agua (list[int]): vértices com fontes de água.
        - capacidade_caminhoes (int): capacidade de água por caminhão.
        - consumo_por_fogo (int): quantidade de água consumida por foco de fogo.
        """
        self.grafo = nx.Graph()
        self.consumo_por_fogo = consumo_por_fogo
        self.capacidade_caminhoes = capacidade_caminhoes
        self.brigadistas = {}
        self.postos_brigadistas = set(postos_brigadistas)

        for i in range(num_vertices):
            self.grafo.add_node(
                i,
                fogo=False,
                agua=False,
                queimado=False,
                posto_brigadista=(i in self.postos_brigadistas)
            )

        arestas_adicionadas = set()
        while len(arestas_adicionadas) < num_arestas:
            u, v = random.sample(range(num_vertices), 2)
            if (u, v) not in arestas_adicionadas and (v, u) not in arestas_adicionadas:
                peso = random.randint(1, 10)
                self.grafo.add_edge(u, v, weight=peso)
                arestas_adicionadas.add((u, v))

        for p in postos_brigadistas:
            self.brigadistas[p] = (p, self.capacidade_caminhoes)
            self.grafo.nodes[p]['agua'] = True

        for p in pontos_agua:
            self.grafo.nodes[p]['agua'] = True

        self.fogo_ativo = []
        self.fogos_apagados = []
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
        Propaga o fogo dos vértices atualmente em chamas para seus vizinhos,
        seguindo algumas condições.

        A propagação só ocorre se o vértice vizinho:
        - Não estiver em chamas.
        - Não tiver fonte de água.
        - Não tiver sido queimado anteriormente.
        - Não for um posto de brigadistas.

        Os novos focos são marcados e adicionados à lista de fogo ativo.
        """
        novos_focos = []

        # Itera sobre os vértices com fogo ativo
        for v in self.fogo_ativo:
            # Verifica todos os vizinhos do vértice em chamas
            for vizinho in self.grafo.neighbors(v):
                # Se o vizinho for um local válido para pegar fogo
                if (not self.grafo.nodes[vizinho]['fogo'] and
                    not self.grafo.nodes[vizinho]['agua'] and
                    not self.grafo.nodes[vizinho]['queimado'] and
                    not self.grafo.nodes[vizinho]['posto_brigadista']):
                    
                    # Marca o vizinho como novo foco de fogo
                    novos_focos.append(vizinho)
                    self.grafo.nodes[vizinho]['fogo'] = True

        # Adiciona os novos focos à lista de fogo ativo
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
        self.grafo.nodes[vertice]['fogo'] = False
        self.grafo.nodes[vertice]['queimado'] = True
        self.fogo_ativo.remove(vertice)
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
        try:
            return nx.shortest_path(
                self.grafo,
                source=origem,
                target=destino,
                weight='weight'
            )
        except nx.NetworkXNoPath:
            return None  # Retorna None se não houver caminho possível

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
        #  Nenhum fogo ativo, nenhuma ação necessária
        if not self.fogo_ativo:
            return  

        for brigadista, (posicao_atual, agua) in self.brigadistas.items():
            # Se o brigadista está sem água, vai reabastecer
            if agua < self.consumo_por_fogo:
                ponto_reabastecimento = min(
                    (n for n in self.grafo.nodes if self.grafo.nodes[n]['agua']),
                    key=lambda p: nx.shortest_path_length(
                        self.grafo, posicao_atual, p, weight='weight'
                    ),
                    default=None
                )

                if ponto_reabastecimento:
                    print(
                        f"💧 Brigadista {brigadista} sem água indo reabastecer "
                        f"em {ponto_reabastecimento}."
                    )
                    self.brigadistas[brigadista] = (
                        ponto_reabastecimento, self.capacidade_caminhoes
                    )
                continue  # Pula para o próximo brigadista

            # Busca o foco de fogo mais próximo (excluindo onde ele já está)
            foco_mais_proximo = min(
                (f for f in self.fogo_ativo if f != posicao_atual),
                key=lambda f: nx.shortest_path_length(
                    self.grafo, posicao_atual, f, weight='weight'
                ),
                default=None
            )

            # Move até o foco de fogo mais próximo
            if foco_mais_proximo:
                caminho = self.caminho_mais_curto(posicao_atual, foco_mais_proximo)
                if caminho:
                    self.brigadistas[brigadista] = self.deslocar_brigadista(
                        brigadista, caminho, agua
                    )

    def deslocar_brigadista(self, brigadista, caminho, agua):
        """
        Move o brigadista ao longo de um caminho até o destino, podendo 
        reabastecer água ou apagar fogo no final do trajeto.

        Parâmetros:
        - brigadista (int): identificador do brigadista.
        - caminho (list[int]): lista de vértices que representam o trajeto.
        - agua (int): quantidade atual de água do brigadista.

        Retorno:
        - Tupla (nova_posição, nova_quantidade_agua) representando o estado
        atualizado do brigadista após o deslocamento.

        Lógica:
        - Se o caminho for vazio, o brigadista permanece na posição atual.
        - Durante o percurso (exceto destino), se passar por um ponto de 
        água, reabastece e termina o movimento ali.
        - Se o destino estiver em chamas, o fogo é apagado e a água consumida.
        - Se não houver fogo no destino, apenas atualiza a posição.
        """
        if not caminho:
            return self.brigadistas[brigadista]

        posicao_atual = caminho[0]
        destino = caminho[-1]
        caminho_percorrido = caminho[1:-1]

        print(
            f"🚒 Brigadista {brigadista} ({agua}L) saindo de {posicao_atual} "
            f"para apagar fogo em {destino}. Passou por {caminho_percorrido}"
        )

        # Reabastecimento durante o trajeto (antes do destino)
        for v in caminho_percorrido:
            if self.grafo.nodes[v]['agua']:
                print(f"💧 Brigadista {brigadista} reabastecendo em {v}.")
                return (v, self.capacidade_caminhoes)

        # Apaga o fogo se ainda estiver ativo no destino
        if self.grafo.nodes[destino]['fogo']:
            self.apagar_fogo(destino)
            agua -= self.consumo_por_fogo
            print(
                f"🔥 Fogo apagado em {destino} pelo brigadista {brigadista} "
                f"(Restante: {agua}L)."
            )
            return (destino, agua)

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
        self.iniciar_fogo(inicio_fogo)

        print("🖼️ Exibindo estado inicial do grafo...")
        self.desenhar_grafo(1)

        estado = 2
        while self.fogo_ativo:
            self.propagar_fogo()

            # Exibe fogos ativos antes da atuação dos brigadistas
            print(
                "🔥 Fogo ativo nos vértices antes da ação dos brigadistas: "
                f"{sorted(self.fogo_ativo)}"
            )

            self.enviar_brigadistas()

            # Exibe fogos ativos após a atuação dos brigadistas
            print(
                "🔥 Fogo ativo nos vértices após a ação dos brigadistas: "
                f"{sorted(self.fogo_ativo)}"
            )

            self.desenhar_grafo(estado)
            estado += 1

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
        plt.clf()
        node_colors = []
        for n in self.grafo.nodes:
            if self.grafo.nodes[n]['fogo']:
                node_colors.append('red')
            elif any(self.brigadistas[b][0] == n for b in self.brigadistas):
                node_colors.append('yellow')
            elif (self.grafo.nodes[n]['agua'] or
                self.grafo.nodes[n]['posto_brigadista']):
                node_colors.append('blue')
            elif self.grafo.nodes[n]['queimado']:
                node_colors.append('gray')
            else:
                node_colors.append('green')

        plt.figure(figsize=(10, 8))
        nx.draw(
            self.grafo,
            self.pos,
            with_labels=True,
            node_size=500,
            node_color=node_colors,
            font_size=10
        )

        edge_labels = nx.get_edge_attributes(self.grafo, 'weight')
        nx.draw_networkx_edge_labels(
            self.grafo,
            self.pos,
            edge_labels=edge_labels,
            font_size=9
        )

        plt.title(f"Estado Atual do Grafo [estado {estado}]")
        plt.draw()
        plt.pause(1.5)
