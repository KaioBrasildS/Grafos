# Relatório: Sistema de Combate a Incêndios Florestais
 **Nome**: Kaio Brasil da Silva.  
 **Matricula**: 2021007286  

Os exemplos de como utilizar a simulação e os codigos encontram-se na pasta notebook, já os código em si encontram-se na pasta FirePrevention.  

Este sistema simula o comportamento de brigadistas em um grafo de localidades, onde eles combatem incêndios, recarregam água e se movimentam estrategicamente.
O sistema considera a capacidade dos caminhões-pipa, a distância entre os nós e a presença de recursos como água e postos de brigadistas.Abaixo, é explicado algumas pontos de interesses sobre a simulação e o seu funcionamento.  
* Este relatório é dividido em três seções que são elas:
    * Descrição das decisões de implementação.
    * Análise dos resultados obtidos.
    * Possíveis Melhorias e discussões sobre os desafios encontrados.


## Descrição das decisões de implementação 

O código foi desenvolvido em Python por ser uma linguagem robusta e amplamente utilizada, com diversas bibliotecas que facilitam o desenvolvimento. Dentre elas, destaca-se a biblioteca específica para grafos `networkx`, cuja adoção permitiu uma implementação mais eficiente, intuitiva e com códigos mais robustos.
Abaixo apresentamos a explicação das partes mais complexas do código. Essas funções possuem uma lógica mais robusta e são responsáveis pela maior parte do funcionamento da simulação de incêndio.

### `enviar_brigadistas(self)`

Esta função é responsável por despachar os brigadistas ativos no sistema, direcionando-os aos focos de incêndio mais próximos ou, caso estejam sem água suficiente, aos pontos de reabastecimento. Para isso, ela utiliza o algoritmo de Dijkstra para calcular o caminho mais curto até o destino. Durante a execução, a função identifica o foco de incêndio mais próximo, redireciona os brigadistas sem água para o ponto de reabastecimento adequado e, ao final de cada deslocamento, atualiza tanto a posição quanto o nível de água de cada brigadista, garantindo que o estado da simulação reflita com precisão a dinâmica do combate ao incêndio.

```python
def enviar_brigadistas(self):
    if not self.fogo_ativo:
        return  

    for brigadista, (posicao_atual, agua) in self.brigadistas.items():
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
            continue

        foco_mais_proximo = min(
            (f for f in self.fogo_ativo if f != posicao_atual),
            key=lambda f: nx.shortest_path_length(
                self.grafo, posicao_atual, f, weight='weight'
            ),
            default=None
        )

        if foco_mais_proximo:
            caminho = self.caminho_mais_curto(posicao_atual, foco_mais_proximo)
            if caminho:
                self.brigadistas[brigadista] = self.deslocar_brigadista(
                    brigadista, caminho, agua
                )
```
### `encontrar_caminho_ate_agua_ou_posto(self, origem)`
A função retorna o caminho mais curto a partir de um ponto de origem até o ponto acessível mais próximo que contenha água ou um posto de brigadistas. Para isso, utiliza o algoritmo de caminho mínimo da biblioteca networkx, garantindo eficiência na busca. Caso não exista um caminho viável entre os pontos, a função retorna None, indicando a impossibilidade de deslocamento.
```python
def encontrar_caminho_ate_agua_ou_posto(self, origem):
    destinos_possiveis = [
        n for n in self.grafo.nodes
        if self.grafo.nodes[n].get('agua') or
        self.grafo.nodes[n].get('posto_brigadista')
    ]

    menor_caminho = None
    menor_distancia = float('inf')

    for destino in destinos_possiveis:
        try:
            caminho = nx.shortest_path(
                self.grafo, origem, destino, weight='weight'
            )
            distancia = nx.shortest_path_length(
                self.grafo, origem, destino, weight='weight'
            )
            if distancia < menor_distancia:
                menor_distancia = distancia
                menor_caminho = caminho
        except nx.NetworkXNoPath:
            continue

    return menor_caminho
```

### `deslocar_brigadista(self, brigadista, caminho, agua)`
Esta função gerencia o deslocamento de um brigadista ao longo de um caminho determinado. Durante o trajeto, verifica se há água suficiente para combater o incêndio ao chegar no destino. Caso o local contenha um foco ativo e o brigadista tenha água, o fogo é apagado. Se o trajeto incluir pontos com disponibilidade de água, o brigadista é automaticamente reabastecido. Ao final do deslocamento, tanto a posição quanto o nível de água do brigadista são atualizados. Se o brigadista estiver sem água no início da ação, a função tenta redirecioná-lo para o ponto de reabastecimento mais próximo.
```python
def deslocar_brigadista(self, brigadista, caminho, agua):
    if not caminho:
        print(f"🧭 Caminho percorrido por {brigadista}: nenhum (sem deslocamento)")
        return self.brigadistas[brigadista]

    posicao_atual = caminho[0]
    destino = caminho[-1]
    caminho_percorrido = caminho[1:-1]

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

    print(f"🚒 Brigadista {brigadista} ({agua}L) saindo de {posicao_atual} "
          f"para apagar fogo em {destino}. Passou por {caminho_percorrido}")
    print(f"🧭 Caminho percorrido por {brigadista}: {caminho}")

    for v in caminho_percorrido:
        if self.grafo.nodes[v]['agua']:
            print(f"💧 Brigadista {brigadista} reabastecendo em {v}.")
            return (v, self.capacidade_caminhoes)

    if self.grafo.nodes[destino]['fogo']:
        self.apagar_fogo(destino)
        agua -= self.consumo_por_fogo
        print(f"🔥 Fogo apagado em {destino} pelo brigadista {brigadista} "
              f"(Restante: {agua}L).")
        return (destino, agua)

    return (destino, agua)
```


Além das decisões lógicas implementadas, optou-se também pela utilização de uma biblioteca gráfica para uma melhor interpretação dos grafos, bem como uma saída textual a cada atualização do grafo, facilitando o entendimento de toda a sua estrutura.

## Análise dos resultados obtidos 

Os resultados obtidos com a simulação foram bastante satisfatórios. A saída do código nos permite visualizar de forma clara o comportamento dos brigadistas, a propagação do fogo e o estado do grafo ao longo do tempo.

Essas informações são fundamentais para avaliarmos a qualidade do sistema, pois demonstram como ele reage em diferentes situações. Observa-se que o sistema opera de maneira eficiente: os brigadistas sempre conseguem apagar todos os focos de incêndio utilizando o menor caminho disponível.

Além disso, é possível notar que não há desperdício de energia durante o processo. Os brigadistas não percorrem caminhos desnecessários para buscar água, e o sistema evita que múltiplos brigadistas sejam enviados para apagar o mesmo foco de incêndio, o que também evitaria perdas de energia.
estado: 2

Abaixo vemos um exemplo de funcionaento  do codigo:  
estado: 2  
🔥 Fogo ativo nos vértices antes da ação dos brigadistas: [1, 3, 6, 7]  
🚒 Brigadista 0 (3L) saindo de 0 para apagar fogo em 7. Passou por [2, 5]  
🧭 Caminho percorrido por 0: [0, 2, 5, 7]  
💧 Brigadista 0 reabastecendo em 5.  
🚒 Brigadista 4 (3L) saindo de 4 para apagar fogo em 1. Passou por []  
🧭 Caminho percorrido por 4: [4, 1]  
🔥 Fogo apagado em 1 pelo brigadista 4 (Restante: 2L).  
🔥 Fogo ativo nos vértices após a ação dos brigadistas: [3, 6, 7]


![ texto](images/output2.png)


Esse exemplo mostra que o brigadista foi acionado corretamente, seguiu o trajeto ideal e extinguiu o fogo de forma eficiente, mantendo parte de sua energia disponível para futuras ações.


Além disso, a imagem gerada ao final da simulação ilustra o estado do grafo após todas as movimentações realizadas. Essa visualização proporciona uma representação mais clara e intuitiva do que está acontecendo no sistema, bem como do que ocorreu ao longo da simulação.
Ela nos permite compreender melhor a dinâmica dos brigadistas, os caminhos percorridos, os focos de incêndio combatidos e a situação final de cada vértice do grafo. Isso contribui significativamente para a análise e validação do funcionamento do sistema.



## Possíveis Melhorias e discussões sobre os desafios encontrados

O projeto se mostrou bastante desafiador, especialmente no desenvolvimento da lógica que orienta as ações dos brigadistas. Definir com precisão para onde cada brigadista deve se dirigir, evitando que todos se desloquem para o mesmo local, e ao mesmo tempo garantir que não haja desperdício de energia, foram aspectos que exigiram bastante raciocínio e planejamento — e que se destacaram como desafios particularmente interessantes.

Apesar dos bons resultados, ainda há espaço para melhorias, especialmente no que diz respeito à compreensão visual da simulação. Melhorias na amostragem do grafo e na visualização dos passos realizados pelos brigadistas durante o combate ao fogo poderiam tornar a simulação mais intuitiva. A implementação de uma interface gráfica mais clara e interativa contribuiria significativamente para facilitar a compreensão do sistema por usuários futuros.  
Além disso, melhorias na lógica podem ser estudadas futuramente com o objetivo de minimizar o desperdício, tanto em termos de poder computacional quanto na eficiência do deslocamento dos brigadistas