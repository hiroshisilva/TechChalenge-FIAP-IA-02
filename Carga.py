from dataclasses import dataclass

@dataclass
class Carga:
    id: int
    demanda: int
    x: float
    y: float