class Graph:
    def __init__(self, name: str, color: tuple[int, ...],
                 graph_data: list[float], graph_x: list[float] | None = None):
        self.name: str = name
        self.color: tuple[int, ...] = color

        self.graph_data: list[float] = graph_data
        self.graph_x: list[float] | None = graph_x