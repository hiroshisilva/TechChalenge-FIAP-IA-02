import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import requests

import os
from dotenv import load_dotenv

from vrp import *

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

app = dash.Dash(__name__)
server = app.server

cache_rotas = {}

def rota_real(a, b):
    key = (a.id, b.id)

    if key in cache_rotas:
        print(f"Usando rota em cache entre {a.id} e {b.id}")
        print(f"Coords: {cache_rotas[key]}")
        return cache_rotas[key]

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{a.y},{a.x};{b.y},{b.x}"

    params = {
        "geometries": "geojson",
        "access_token": MAPBOX_TOKEN
    }

    try:
        r = requests.get(url, params=params)
        coords = r.json()["routes"][0]["geometry"]["coordinates"]

        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]

    except Exception as e:
        lats = [a.x, b.x]
        lons = [a.y, b.y]

        print(f"Erro ao buscar rota real entre {a.id} e {b.id}, usando linha reta")
        print(f"Erro: {e}")

    cache_rotas[key] = (lats, lons)
    
    return lats, lons


estado = {
    "rodando": False,
    "historico": [],
    "geracao_atual": 0,
    "max_geracoes": 10,
    "ultimo_mapa": go.Figure(),
    "ultimo_grafico": go.Figure(),
    "ultimo_roteiro": html.Div(),
    "mutacao": 0.5
}


def criar_figura(rotas, locais):

    fig = go.Figure()
    cores = ["red", "blue", "green", "purple"]

    # depósito
    fig.add_trace(go.Scattermap(
        lat=[locais[0].x],
        lon=[locais[0].y],
        mode='markers',
        marker=dict(size=16, color="black"),
        name="Depósito"
    ))

    # clientes
    fig.add_trace(go.Scattermap(
        lat=[l.x for l in locais if l.id != 0],
        lon=[l.y for l in locais if l.id != 0],
        mode='markers',
        marker=dict(size=14, color="red"),
        name="Entregas"
    ))

    for i, rota in enumerate(rotas):

        if not rota:
            continue

        pontos = [0] + rota + [0]

        lat_total = []
        lon_total = []

        for j in range(len(pontos) - 1):
            a = locais[pontos[j]]
            b = locais[pontos[j + 1]]

            lats, lons = rota_real(a, b)

            lat_total += lats
            lon_total += lons

        fig.add_trace(go.Scattermap(
            lat=lat_total,
            lon=lon_total,
            mode='lines',
            line=dict(width=4, color=cores[i % len(cores)]),
            name=f"Rota {i}"
        ))

    fig.update_layout(
        map=dict(
            style="open-street-map",
            zoom=12,
            center=dict(lat=locais[0].x, lon=locais[0].y)
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig



app.layout = html.Div([

    html.H2("Sistema de roterização de entregas - Tech Challenge FIAP IA 02"),

    html.Div([

        html.Div([
            html.Label("Quantidade de Locais"),
            dcc.Input(id="n_locais", type="number", value=2)
        ]),

        html.Div([
            html.Label("Veículos"),
            dcc.Input(id="n_veiculos", type="number", value=1)
        ]),

        html.Div([
            html.Label("Capacidade"),
            dcc.Input(id="capacidade", type="number", value=15)
        ]),

        html.Div([
            html.Label("Gerações"),
            dcc.Input(id="geracoes", type="number", value=10)
        ]),

        html.Div([
            html.Label("Lat Depósito"),
            dcc.Input(id="lat", type="number", value=-23.55)
        ]),

        html.Div([
            html.Label("Lon Depósito"),
            dcc.Input(id="lon", type="number", value=-46.63)
        ]),

        html.Div([
            html.Label("mutação"),
            dcc.Input(id="mutacao", type="number", value=0.5)
        ]),

        html.Button("Rodar", id="btn", n_clicks=0)

    ], style={"display": "flex", "gap": "20px"}),

    html.Div(id="status"),

    dcc.Graph(id="mapa", style={"height": "650px"}),
    dcc.Graph(id="grafico"),
    dcc.Interval(id="interval", interval=800),
    html.Div(id="roteiro", style={"marginTop": "20px"})
])

def gerar_relatorio(rotas, locais):
    print("Gerando relatório detalhado para rotas reais...")
    blocos = []
    
    for i, rota in enumerate(rotas):

        link = gerar_link_google_maps(rota, locais)

        blocos.append(html.Div([
            html.H4(f"Veículo {i}"),
            html.A("Abrir navegação", href=link, target="_blank")
        ]))

    texto = gerar_instrucoes(rotas, locais)

    print("Relatório gerado com sucesso!")
    print(f"Texto das instruções: {texto}")

    return html.Div([
        html.H3("🚗 Navegação"),
        *blocos,
        html.H3("📋 Instruções"),
        html.Pre(texto)
    ])


@app.callback(
    Output("btn", "n_clicks"),
    Input("btn", "n_clicks"),
    State("n_locais", "value"),
    State("n_veiculos", "value"),
    State("capacidade", "value"),
    State("geracoes", "value"),
    State("mutacao", "value"),
    State("lat", "value"),
    State("lon", "value")
)
def iniciar(n, nl, nv, cap, gen, mut,lat, lon):
    

    if n > 0:
        cache_rotas.clear()
        estado["mutacao"] = mut
        estado["locais"] = gerar_locais(nl, lat, lon)
        estado["veiculos"] = gerar_veiculos(nv, cap)
        estado["pop"] = criar_populacao(80, nl)
        estado["melhor"] = min(
            estado["pop"],
            key=lambda i: distancia_total_veiculos(i, estado["locais"], estado["veiculos"])
        )
        estado["historico"] = []
        estado["ultimo_mapa"] = go.Figure(data=[], layout={})
        estado["ultimo_grafico"] = go.Figure(data=[], layout={})
        estado["ultimo_roteiro"] = html.Div()
        estado["rodando"] = True
        estado["geracao_atual"] = 0
        estado["max_geracoes"] = gen

    return n


@app.callback(
    [Output("mapa", "figure"),
     Output("grafico", "figure"),
     Output("status", "children"),
     Output("roteiro", "children")],
    Input("interval", "n_intervals")
)
def atualizar(n):

    if not estado["rodando"]:
        return estado["ultimo_mapa"], estado["ultimo_grafico"], "Parado", estado.get("ultimo_roteiro", html.Div())

    if estado["geracao_atual"] >= estado["max_geracoes"]:
        estado["rodando"] = False
        return estado["ultimo_mapa"], estado["ultimo_grafico"], "Finalizado", estado.get("ultimo_roteiro", html.Div())

    pop = evoluir(estado["pop"], estado["locais"], estado["mutacao"], estado["veiculos"])

    atual = min(
        pop,
        key=lambda i: distancia_total_veiculos(i, estado["locais"], estado["veiculos"])
    )

    if distancia_total_veiculos(atual, estado["locais"], estado["veiculos"]) < \
       distancia_total_veiculos(estado["melhor"], estado["locais"], estado["veiculos"]):
        estado["melhor"] = atual

    estado["pop"] = pop
    estado["historico"].append(
        distancia_total_veiculos(estado["melhor"], estado["locais"], estado["veiculos"])
    )
    estado["geracao_atual"] += 1

    rotas = dividir_rotas(estado["melhor"], len(estado["veiculos"]))

    mapa = criar_figura(rotas, estado["locais"])

    grafico = go.Figure()
    grafico.add_trace(go.Scatter(y=estado["historico"], mode="lines"))

    estado["ultimo_mapa"] = mapa
    estado["ultimo_grafico"] = grafico

    status = f"Geração {estado['geracao_atual']} / {estado['max_geracoes']}"

    relatorio = gerar_relatorio(rotas, estado["locais"])
    # salva o último relatório no estado para retornos posteriores
    estado["ultimo_roteiro"] = relatorio

    return mapa, grafico, status, relatorio

if __name__ == "__main__":
    app.run(debug=True)