import random
from flask.cli import load_dotenv
import numpy as np
import math
from dataclasses import dataclass
from openai import OpenAI
import os


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# DATA CLASSES
# =========================
@dataclass
class Local:
    id: int
    demanda: int
    x: float
    y: float
    inicio_janela: float
    fim_janela: float
    tempo_servico: float


@dataclass
class Veiculo:
    id: int
    capacidade_max: int


def distancia_locais(a: Local, b: Local):
    R = 6371

    lat1 = math.radians(a.x)
    lon1 = math.radians(a.y)
    lat2 = math.radians(b.x)
    lon2 = math.radians(b.y)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(h))


def gerar_locais(n, lat_dep, lon_dep):

    locais = []

    # depósito
    locais.append(
        Local(
            id=0,
            demanda=0,
            x=lat_dep,
            y=lon_dep,
            inicio_janela=0,
            fim_janela=100,
            tempo_servico=0
        )
    )

    # clientes
    for i in range(1, n):
        lat = lat_dep + (np.random.rand() - 0.5) * 0.2
        lon = lon_dep + (np.random.rand() - 0.5) * 0.2

        locais.append(
            Local(
                id=i,
                demanda=np.random.randint(1, 6),
                x=lat,
                y=lon,
                inicio_janela=0,
                fim_janela=100,
                tempo_servico=0
            )
        )

    return locais


def gerar_veiculos(n, capacidade):
    return [Veiculo(id=i, capacidade_max=capacidade) for i in range(n)]


def criar_populacao(tam, n):
    base = list(range(n))
    pop = []

    for _ in range(tam):
        ind = base.copy()
        random.shuffle(ind)
        ind = [i for i in ind if i != 0]
        pop.append(ind)

    return pop


def dividir_rotas(ind, n_veiculos):
    return [list(r) for r in np.array_split(ind, n_veiculos)]


def distancia_total_veiculos(ind, locais, veiculos):

    if not isinstance(ind, list) or len(ind) == 0:
        return float("inf")

    total = 0
    penalidade = 0

    rotas = dividir_rotas(ind, len(veiculos))

    for i, rota in enumerate(rotas):

        if not rota:
            continue

        v = veiculos[i]
        carga_total = sum(locais[c].demanda for c in rota)

        if carga_total > v.capacidade_max:
            penalidade += (carga_total - v.capacidade_max) * 100

        rota_full = [0] + rota + [0]

        for j in range(len(rota_full) - 1):
            total += distancia_locais(
                locais[rota_full[j]],
                locais[rota_full[j + 1]]
            )

    return total + penalidade


def fitness(ind, locais, veiculos):
    d = distancia_total_veiculos(ind, locais, veiculos)
    return 1 / d if d > 0 else 1


def selecao(pop, locais, veiculos):
    fits = [fitness(i, locais, veiculos) for i in pop]
    total = sum(fits)

    if total == 0:
        return random.choice(pop)

    probs = [f / total for f in fits]
    return pop[np.random.choice(len(pop), p=probs)]


def crossover(p1, p2):
    size = len(p1)

    if size < 2:
        return p1.copy()

    a, b = sorted(random.sample(range(size), 2))

    filho = [None] * size
    filho[a:b] = p1[a:b]

    pos = b
    for g in p2:
        if g not in filho:
            if pos >= size:
                pos = 0
            filho[pos] = g
            pos += 1

    return filho


def mutacao(ind, taxa):
    ind = ind.copy()

    for i in range(len(ind)):
        if random.random() < taxa:
            j = random.randint(0, len(ind) - 1)
            ind[i], ind[j] = ind[j], ind[i]

    return ind


def evoluir(pop, locais, taxa, veiculos):

    pop = [p for p in pop if isinstance(p, list)]

    nova = []

    melhor = min(pop, key=lambda i: distancia_total_veiculos(i, locais, veiculos))
    nova.append(melhor.copy())

    while len(nova) < len(pop):

        p1 = selecao(pop, locais, veiculos)
        p2 = selecao(pop, locais, veiculos)

        filho = mutacao(crossover(p1, p2), taxa)

        if len(set(filho)) != len(filho):
            continue

        nova.append(filho)

    return nova

def gerar_link_google_maps(rota, locais):

    base = f"{locais[0].x},{locais[0].y}"

    waypoints = []
    for idx in rota:
        l = locais[idx]
        waypoints.append(f"{l.x},{l.y}")

    waypoints_str = "|".join(waypoints)

    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={base}"
        f"&destination={base}"
        f"&waypoints={waypoints_str}"
        "&travelmode=driving"
    )



def gerar_instrucoes(rotas, locais):

    dados = []

    for i, rota in enumerate(rotas):
        entregas = []

        for idx in rota:
            l = locais[idx]
            entregas.append({
                "local": l.id,
                "lat": l.x,
                "lon": l.y,
                "demanda": l.demanda
            })

        dados.append({
            "veiculo": i,
            "rota": entregas
        })

    prompt = f"""
    Gere instruções simples para motoristas.

    - ordem de entrega
    - linguagem clara e direta, com o endereço de cada local baseado nas coordenadas de cada local
    - objetivo
    - para facilitar a navegação, gere um link do Google Maps para cada rota

    Dados:
    {dados}
    """

    try:
        r = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Especialista em logística"},
                {"role": "user", "content": prompt}
            ]
        )

        return r.choices[0].message.content

    except Exception as e:
        print(f"Erro ao gerar instruções: {e}")
        return "Erro ao gerar instruções"