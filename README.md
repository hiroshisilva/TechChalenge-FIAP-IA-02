# TechChalenge-FIAP-IA-02

## Sobre o Projeto

Esta aplicação utiliza algoritmos genéticos para a roteirização de rotas de entregas (problema VRP). Foi desenvolvida como trabalho de conclusão de curso do Módulo 2 da pós-graduação FIAP — IA para Devs. O objetivo é demonstrar como meta-heurísticas (seleção, crossover, mutação e evolução) podem gerar roteiros eficientes respeitando restrições de capacidade e custo.

## Participantes

- **André Hiroshi da Silva** — RM: 369664
- **Noriaki Odan Junior** — RM: 369719

## Arquivo de referência

O trabalho do curso está descrito no arquivo: [8IADT - Fase 2 - Tech challenge.pdf](8IADT%20-%20Fase%202%20-%20Tech%20challenge.pdf)

## Funcionalidades principais

- Geração aleatória de locais (depósito + clientes)
- Modelagem de cargas e veículos com restrições de capacidade
- Algoritmo genético para otimização de rotas
- Visualização interativa das rotas (Dash + Plotly)
- Geração de relatório/roteiro de navegação

## Execução rápida

1. Ative o ambiente virtual (opcional):

```bash
python -m venv techChallenge02
source techChallenge02/bin/activate
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Execute a aplicação:

```bash
./techChallenge02/bin/python app_dash.py
```

## Vídeo de demonstração

Veja o projeto em execução no vídeo abaixo:

[Vídeo de demonstração no YouTube](https://youtu.be/)




