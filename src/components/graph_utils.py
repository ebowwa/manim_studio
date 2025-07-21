"""Graph utilities for advanced visualizations."""
from manim import *
from typing import List, Tuple, Dict, Optional, Set
import networkx as nx
from pulp import *
from random import seed
from itertools import combinations


def parse_graph(
    graph_data: str, 
    scale_x: float = 0.13, 
    scale_y: float = 0.13, 
    scale: float = 2
) -> Graph:
    """Parse a graph from custom format with positions.
    
    Format:
    1 2 <9.118, 4.650> <15.236, 4.832>
    3 2 <20.843, 7.251> <15.236, 4.832>
    """
    layout = {}
    edges = []
    vertices = set()
    
    for line in graph_data.strip().splitlines():
        line = line.strip()
        edge, p1, p2 = line.split("<")
        u, v = list(map(int, edge.strip().split()))
        u_x, u_y = list(map(float, p1[:-2].strip().split(", ")))
        v_x, v_y = list(map(float, p2[:-2].strip().split(", ")))
        
        layout[u] = [u_x, u_y, 0]
        layout[v] = [v_x, v_y, 0]
        
        edges.append((u, v))
        vertices.add(u)
        vertices.add(v)
    
    # Center the graph
    avg_x = sum(pos[0] for pos in layout.values()) / len(layout)
    avg_y = sum(pos[1] for pos in layout.values()) / len(layout)
    
    for vertex in layout:
        layout[vertex] = (
            (layout[vertex][0] - avg_x) * scale_x,
            (layout[vertex][1] - avg_y) * scale_y,
            0
        )
    
    return Graph(sorted(list(vertices)), edges, layout=layout).scale(scale)


def get_graph_coloring(
    vertices: List[int], 
    edges: List[Tuple[int, int]]
) -> Dict[int, str]:
    """Get optimal graph coloring using linear programming.
    
    Returns:
        Dictionary mapping vertex to color
    """
    n = len(vertices)
    colors = [RED, GREEN, BLUE, PINK, ORANGE, LIGHT_BROWN]
    
    # Create vertex mappings
    mapping = {vertex: i for i, vertex in enumerate(vertices)}
    inverse_mapping = {i: vertex for i, vertex in enumerate(vertices)}
    
    seed(0)
    
    # Linear programming model
    model = LpProblem(sense=LpMinimize)
    
    # Chromatic number variable
    chromatic_number = LpVariable(name="chromatic_number", cat='Integer')
    
    # Binary variables: x[i][j] = 1 if vertex i has color j
    variables = [
        [LpVariable(name=f"x_{i}_{j}", cat='Binary') for i in range(n)] 
        for j in range(n)
    ]
    
    # Each vertex has exactly one color
    for i in range(n):
        model += lpSum(variables[i]) == 1
    
    # Adjacent vertices have different colors
    for u, v in edges:
        for color in range(n):
            model += variables[mapping[u]][color] + variables[mapping[v]][color] <= 1
    
    # Minimize chromatic number
    for i in range(n):
        for j in range(n):
            model += chromatic_number >= (j + 2) * variables[i][j]
    
    model += chromatic_number
    
    # Solve
    status = model.solve(PULP_CBC_CMD(msg=False))
    
    return {
        inverse_mapping[i]: colors[j]
        for i in range(n) for j in range(n) if variables[i][j].value()
    }


def get_independent_set(
    vertices: List[int],
    edges: List[Tuple[int, int]]
) -> List[int]:
    """Find maximum independent set using linear programming."""
    n = len(vertices)
    mapping = {vertex: i for i, vertex in enumerate(vertices)}
    
    model = LpProblem(sense=LpMaximize)
    
    # Binary variables for vertex inclusion
    variables = [LpVariable(name=f"x_{i}", cat='Binary') for i in range(n)]
    
    # No adjacent vertices in the set
    for u, v in edges:
        model += variables[mapping[u]] + variables[mapping[v]] <= 1
    
    # Maximize set size
    model += lpSum(variables)
    
    status = model.solve(PULP_CBC_CMD(msg=False))
    return [vertices[i] for i in range(n) if int(variables[i].value()) == 1]


def get_maximum_clique(
    vertices: List[int],
    edges: List[Tuple[int, int]]
) -> List[int]:
    """Find maximum clique using linear programming."""
    n = len(vertices)
    mapping = {vertex: i for i, vertex in enumerate(vertices)}
    inverse_mapping = {i: vertex for i, vertex in enumerate(vertices)}
    
    seed(0)
    model = LpProblem(sense=LpMaximize)
    
    # Binary variables for vertex inclusion
    variables = [LpVariable(name=f"x_{i}", cat='Binary') for i in range(n)]
    
    # Find non-edges
    non_edges = [
        (u, v) for u in range(n) for v in range(u + 1, n)
        if (inverse_mapping[u], inverse_mapping[v]) not in edges and
           (inverse_mapping[v], inverse_mapping[u]) not in edges
    ]
    
    # Non-adjacent vertices cannot both be in clique
    for u, v in non_edges:
        model += variables[u] + variables[v] <= 1
    
    # Maximize clique size
    model += lpSum(variables)
    
    status = model.solve(PULP_CBC_CMD(msg=False))
    return [inverse_mapping[i] for i in range(n) if variables[i].value()]


def induced_subgraphs(
    vertices: List[int],
    edges: List[Tuple[int, int]],
    min_size: int = 1,
    max_size: Optional[int] = None
):
    """Generate all induced subgraphs, sorted by size (largest first)."""
    n = len(vertices)
    if max_size is None:
        max_size = n + 1
    
    for i in reversed(range(min_size, max_size)):
        for subset in combinations(vertices, r=i):
            subset_set = set(subset)
            induced_edges = [
                (u, v) for u, v in edges 
                if u in subset_set and v in subset_set
            ]
            yield list(subset), induced_edges


class GraphVisualizer:
    """Enhanced graph visualization with animations."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.vertices = graph.vertices
        self.edges = graph.edges
    
    def animate_coloring(
        self, 
        scene: Scene,
        coloring: Dict[int, str],
        duration: float = 0.5
    ) -> None:
        """Animate graph coloring."""
        animations = []
        for vertex, color in coloring.items():
            if vertex in self.graph:
                animations.append(
                    self.graph[vertex].animate.set_color(color)
                )
        
        scene.play(*animations, run_time=duration)
    
    def highlight_subgraph(
        self,
        scene: Scene,
        vertices: List[int],
        color: str = YELLOW,
        scale_factor: float = 1.2
    ) -> None:
        """Highlight a subgraph."""
        animations = []
        for vertex in vertices:
            if vertex in self.graph:
                animations.extend([
                    self.graph[vertex].animate.set_color(color),
                    self.graph[vertex].animate.scale(scale_factor),
                    Flash(self.graph[vertex], color=color)
                ])
        
        scene.play(*animations)
    
    def animate_path(
        self,
        scene: Scene,
        path: List[int],
        color: str = GREEN,
        run_time: float = 2.0
    ) -> None:
        """Animate a path through the graph."""
        for i in range(len(path) - 1):
            if path[i] in self.graph and path[i+1] in self.graph:
                edge_line = Line(
                    self.graph[path[i]].get_center(),
                    self.graph[path[i+1]].get_center(),
                    color=color,
                    stroke_width=6
                )
                scene.play(
                    Create(edge_line),
                    run_time=run_time / (len(path) - 1)
                )