from io import TextIOWrapper
from typing import Callable
from .graph import Graph

import matplotlib.pyplot as plt
from matplotlib import font_manager



class GraphRenderer:
    def __init__(self, graph_name: str, formater: Callable[[float, int], str], x_label: str, y_label: str, font_file_path: str):
        self.graph_name: str = graph_name
        self.graphs: list[Graph] = list()

        self.formater: Callable[[float, int], str] = formater

        self.x_label: str = x_label
        self.y_label: str = y_label

        self.font_file_path: str = font_file_path

    def add_graph(self, name: str, color: tuple[int, ...], graph_data: list[float]):
        self.graphs.append(
            Graph(
                name, color, graph_data
            )
        )



    def render(self, fp: TextIOWrapper):
        font_prop = font_manager.FontProperties(
            fname=self.font_file_path)
        plt.rcParams['font.family'] = font_prop.get_name()

        fig, ax = plt.subplots()

        # 전체 배경색 설정
        fig.patch.set_facecolor((0.1, 0.1, 0.1))
        # 안쪽 그래프 영역 색 설정
        ax.set_facecolor((0.1, 0.1, 0.1))
        # 그리드 색 설정 (+ 그리드 설정)
        ax.grid(color=(0.2, 0.2, 0.2))

        # X 축의 단위 표시 설정
        ax.xaxis.set_major_formatter(self.formater)

        # 그래프 영역의 윤곽선 불투명도 설정
        for spine in ax.spines.values(): spine.set_alpha(0)

        # 그래프 추가
        for graph in self.graphs:
            plt.plot(graph.graph_data, linestyle='-', color=graph.color, label=graph.name)

        # 좌표축 색상 변경
        ax.tick_params(axis='x', labelcolor='white')
        ax.tick_params(axis='y', labelcolor='white')

        # 범례 설정
        legend = ax.legend(loc="lower left", labelcolor=(1, 1, 1))
        # 범례의 뒷배경 불투명도 설정
        legend.get_frame().set_alpha(0)

        # 그래프 제목, 레이블 설정
        plt.title(self.graph_name, color='white')
        plt.xlabel(self.x_label, color='white')
        plt.ylabel(self.y_label, color='white')

        # 이미지 파일로 저장
        plt.savefig(fp, format='png')
        fp.seek(0)