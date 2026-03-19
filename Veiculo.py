from dataclasses import dataclass

@dataclass
class Veiculo:
    id: int
    capacidade_max: int
    custo_por_km: float = 1.0