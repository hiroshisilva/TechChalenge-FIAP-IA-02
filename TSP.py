import random
import numpy as np
import matplotlib.pyplot as plt

from Carga import Carga
from Veiculo import Veiculo

plt.ion() 
# ---------------------------
# GERAR DADOS
# ---------------------------
def gerar_cargas(n):
    cargas = []
    for i in range(n):
        cargas.append(
            Carga(
                id=i,
                demanda=0 if i == 0 else np.random.randint(1, 6),
                x=np.random.rand() * 100,
                y=np.random.rand() * 100
            )
        )
    return cargas


def gerar_veiculos(n):
    return [Veiculo(id=i, capacidade_max=15) for i in range(n)]


# ---------------------------
# DISTÂNCIA
# ---------------------------
def distancia_cargas(a: Carga, b: Carga):
    return np.linalg.norm([a.x - b.x, a.y - b.y])


# ---------------------------
# POPULAÇÃO
# ---------------------------
def criar_populacao(tamanho, n_cargas):
    base = list(range(n_cargas))
    populacao = []

    for _ in range(tamanho):
        ind = base.copy()
        random.shuffle(ind)
        populacao.append(ind)

    return populacao


# ---------------------------
# DIVIDIR ROTAS (VRP)
# ---------------------------
def dividir_rotas(individuo, n_veiculos):
    return np.array_split(individuo, n_veiculos)


# ---------------------------
# FUNÇÃO OBJETIVO
# ---------------------------
def distancia_total_veiculos(individuo, cargas, veiculos):
    rotas = dividir_rotas(individuo, len(veiculos))

    total_distancia = 0
    penalidade = 0

    for i, rota in enumerate(rotas):
        if len(rota) == 0:
            continue

        veiculo = veiculos[i]
        carga_total = 0

        rota = list(rota)
        rota_completa = [0] + rota + [0]

        # soma carga
        for cid in rota:
            carga_total += cargas[cid].demanda

        # penalidade de capacidade
        if carga_total > veiculo.capacidade_max:
            penalidade += (carga_total - veiculo.capacidade_max) * 100

        # distância
        for j in range(len(rota_completa) - 1):
            a = cargas[rota_completa[j]]
            b = cargas[rota_completa[j + 1]]

            total_distancia += distancia_cargas(a, b) * veiculo.custo_por_km

    return total_distancia + penalidade


# ---------------------------
# FITNESS
# ---------------------------
def fitness(individuo, cargas, veiculos):
    return 1 / distancia_total_veiculos(individuo, cargas, veiculos)


# ---------------------------
# SELEÇÃO (ROULETTE)
# ---------------------------
def selecao(populacao, cargas, veiculos):
    fitnesses = [fitness(ind, cargas, veiculos) for ind in populacao]
    total = sum(fitnesses)
    probs = [f / total for f in fitnesses]

    idx = np.random.choice(len(populacao), p=probs)
    return populacao[idx]


# ---------------------------
# CROSSOVER (OX)
# ---------------------------
def crossover(pai1, pai2):
    size = len(pai1)
    start, end = sorted(random.sample(range(size), 2))

    filho = [None] * size
    filho[start:end] = pai1[start:end]

    pos = end
    for gene in pai2:
        if gene not in filho:
            if pos >= size:
                pos = 0
            filho[pos] = gene
            pos += 1

    return filho


# ---------------------------
# MUTAÇÃO
# ---------------------------
def mutacao(individuo, taxa=0.02):
    for i in range(len(individuo)):
        if random.random() < taxa:
            j = random.randint(0, len(individuo) - 1)
            individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo


# ---------------------------
# EVOLUÇÃO
# ---------------------------
def evoluir(populacao, cargas, taxa_mutacao, veiculos):
    nova_pop = []

    # elitismo (mantém melhor)
    melhor = min(populacao, key=lambda ind: distancia_total_veiculos(ind, cargas, veiculos))
    nova_pop.append(melhor)

    while len(nova_pop) < len(populacao):
        pai1 = selecao(populacao, cargas, veiculos)
        pai2 = selecao(populacao, cargas, veiculos)

        filho = crossover(pai1, pai2)
        filho = mutacao(filho, taxa_mutacao)

        nova_pop.append(filho)

    return nova_pop


# ---------------------------
# PLOT
# ---------------------------
def plotar_evolucao(melhor_global, melhor_geracao, cargas, veiculos, geracao):
    plt.clf()
    cores = ['b', 'g', 'c', 'm', 'y']

    def plotar(individuo, estilo):
        rotas = dividir_rotas(individuo, len(veiculos))

        for i, rota in enumerate(rotas):
            if len(rota) == 0:
                continue

            completa = [0] + list(rota) + [0]
            xs = [cargas[c].x for c in completa]
            ys = [cargas[c].y for c in completa]

            plt.plot(xs, ys, cores[i % len(cores)] + estilo)

    plotar(melhor_global, '-')   # melhor global
    plotar(melhor_geracao, '--') # geração atual

    plt.title(f"Geração {geracao}")
    plt.pause(0.01)


# ---------------------------
# MAIN
# ---------------------------
def main():
    plt.ion()

    n_cargas = 20
    n_veiculos = 3
    geracoes = 60
    tamanho_pop = 100
    taxa_mutacao = 0.5

    cargas = gerar_cargas(n_cargas)
    veiculos = gerar_veiculos(n_veiculos)

    populacao = criar_populacao(tamanho_pop, n_cargas)

    # remove depósito da população
    populacao = [ind[1:] for ind in populacao]

    melhor_global = min(
        populacao,
        key=lambda ind: distancia_total_veiculos(ind, cargas, veiculos)
    )

    for g in range(geracoes):
        populacao = evoluir(populacao, cargas, taxa_mutacao, veiculos)

        melhor_geracao = min(
            populacao,
            key=lambda ind: distancia_total_veiculos(ind, cargas, veiculos)
        )

        if distancia_total_veiculos(melhor_geracao, cargas, veiculos) < \
           distancia_total_veiculos(melhor_global, cargas, veiculos):
            melhor_global = melhor_geracao

        print(f"Geração {g} | Atual: {distancia_total_veiculos(melhor_geracao, cargas, veiculos):.2f} | Melhor: {distancia_total_veiculos(melhor_global, cargas, veiculos):.2f}")

        plotar_evolucao(melhor_global, melhor_geracao, cargas, veiculos, g)

    plt.ioff()
    plt.show()

    print("\nMelhor solução:", melhor_global)
    print("Distância final:", distancia_total_veiculos(melhor_global, cargas, veiculos))


if __name__ == "__main__":
    main()