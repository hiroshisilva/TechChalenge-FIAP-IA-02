import random
import numpy as np
import matplotlib.pyplot as plt

plt.ion() 

# ---------------------------
# 1. Gerar cidades aleatórias
# ---------------------------
def gerar_cidades(n):
    return np.random.rand(n, 2) * 100


def dividir_rotas(individuo, n_veiculos):
    return np.array_split(individuo, n_veiculos)

# ---------------------------
# 2. Distância entre cidades
# ---------------------------
def distancia(a, b):
    return np.linalg.norm(a - b)


def distancia_total(rota, cidades):
    total = 0
    for i in range(len(rota)):
        cidade_a = cidades[rota[i]]
        cidade_b = cidades[rota[(i + 1) % len(rota)]]
        total += distancia(cidade_a, cidade_b)
    return total


def distancia_total_veiculos(individuo, cidades, n_veiculos):
    rotas = dividir_rotas(individuo, n_veiculos)
    total = 0

    for rota in rotas:
        if len(rota) == 0:
            continue

        rota = list(rota)
        rota_completa = [0] + rota + [0]

        for i in range(len(rota_completa) - 1):
            a = cidades[rota_completa[i]]
            b = cidades[rota_completa[i + 1]]
            total += distancia(a, b)

    return total


# ---------------------------
# 3. População inicial
# ---------------------------
def criar_populacao(tamanho, n_cidades):
    populacao = []
    base = list(range(n_cidades))
    for _ in range(tamanho):
        individuo = base.copy()
        random.shuffle(individuo)
        populacao.append(individuo)
    return populacao


# ---------------------------
# 4. Fitness
# ---------------------------
def fitness(individuo, cidades, n_veiculos):
    return 1 / distancia_total_veiculos(individuo, cidades, n_veiculos)


# ---------------------------
# 5. Seleção (roleta)
# ---------------------------
def selecao(populacao, cidades, n_veiculos):
    fitnesses = [fitness(ind, cidades, n_veiculos) for ind in populacao]
    total = sum(fitnesses)
    probs = [f / total for f in fitnesses]
    return populacao[np.random.choice(len(populacao), p=probs)]


# ---------------------------
# 6. Crossover (Order Crossover)
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
# 7. Mutação (swap)
# ---------------------------
def mutacao(individuo, taxa=0.01):
    for i in range(len(individuo)):
        if random.random() < taxa:
            j = random.randint(0, len(individuo) - 1)
            individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo


# ---------------------------
# 8. Evolução
# ---------------------------
def evoluir(populacao, cidades, taxa_mutacao, n_veiculos):
    nova_pop = []

    for _ in range(len(populacao)):
        pai1 = selecao(populacao, cidades, n_veiculos)
        pai2 = selecao(populacao, cidades, n_veiculos)

        filho = crossover(pai1, pai2)
        filho = mutacao(filho, taxa_mutacao)

        nova_pop.append(filho)

    return nova_pop


# ---------------------------
# 9. Plotar rota
# ---------------------------
def plotar_rota(rota, cidades, titulo="Rota"):
    pontos = cidades[rota + [rota[0]]]
    plt.plot(pontos[:, 0], pontos[:, 1], marker='o')
    plt.title(titulo)
    plt.show()


# ---------------------------
# 9. Plotar rota e evolução
# ---------------------------
def plotar_evolucao(melhor_global, melhor_geracao, cidades, geracao, n_veiculos):
    plt.clf()

    cores = ['b', 'g', 'c', 'm', 'y']

    # Melhor global (linhas sólidas)
    rotas = dividir_rotas(melhor_global, n_veiculos)
    for i, rota in enumerate(rotas):
        rota = list(rota)
        if not rota:
            continue

        completa = [0] + rota + [0]
        pontos = cidades[completa]
        plt.plot(pontos[:, 0], pontos[:, 1], cores[i % len(cores)], label=f"Global V{i}")

    # Melhor da geração (tracejado)
    rotas = dividir_rotas(melhor_geracao, n_veiculos)
    for i, rota in enumerate(rotas):
        rota = list(rota)
        if not rota:
            continue

        completa = [0] + rota + [0]
        pontos = cidades[completa]
        plt.plot(pontos[:, 0], pontos[:, 1], cores[i % len(cores)] + '--')

    plt.title(f"Geração {geracao}")
    plt.legend()
    plt.pause(0.01)


# ---------------------------
# 10. Execução principal
# ---------------------------
def main():
    n_cidades = 20
    n_veiculos = 2
    geracoes = 200
    tamanho_pop = 100
    taxa_mutacao = 0.5

    cidades = gerar_cidades(n_cidades)

    # cidade 0 = depósito → não entra na população
    populacao = criar_populacao(tamanho_pop, n_cidades)
    populacao = [ind[1:] for ind in populacao]

    melhor_global = min(populacao, key=lambda ind: distancia_total_veiculos(ind, cidades, n_veiculos))

    for g in range(geracoes):
        populacao = evoluir(populacao, cidades, taxa_mutacao, n_veiculos)

        melhor_geracao = min(populacao, key=lambda ind: distancia_total_veiculos(ind, cidades, n_veiculos))

        if distancia_total_veiculos(melhor_geracao, cidades, n_veiculos) < distancia_total_veiculos(melhor_global, cidades, n_veiculos):
            melhor_global = melhor_geracao

        print(f"Geração {g} | Atual: {distancia_total_veiculos(melhor_geracao, cidades, n_veiculos):.2f} | Melhor: {distancia_total_veiculos(melhor_global, cidades, n_veiculos):.2f}")

        plotar_evolucao(melhor_global, melhor_geracao, cidades, g, n_veiculos)

    plt.ioff()
    plt.show()

    print("\nMelhor rota final:", melhor_global)
    print("Distância final:", distancia_total(melhor_global, cidades))


if __name__ == "__main__":
    main()