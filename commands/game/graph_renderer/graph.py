class Graph:
    def __init__(self, name: str, color: tuple[int, ...], graph_data: list[float]):
        self.name: str = name
        self.color: tuple[int, ...] = color
        self.graph_data: list[float] = graph_data