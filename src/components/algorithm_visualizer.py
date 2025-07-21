"""Algorithm visualization components for educational content."""
from manim import *
from typing import List, Tuple, Dict, Optional, Callable, Any
from utils.utilities import (
    myCode, create_code, staggered_animation_group,
    ProgressiveCodeReveal, highlightText
)
from .data_structures import VisualQueue, VisualStack
import numpy as np


class AlgorithmVisualizer:
    """Base class for algorithm visualizations."""
    
    def __init__(self, scene: Scene):
        self.scene = scene
        self.code_block: Optional[Code] = None
        self.data_display: Optional[VGroup] = None
        self.step_counter: Optional[Text] = None
        self.current_step = 0
    
    def setup_layout(
        self,
        code: str,
        language: str = "python",
        code_position: np.ndarray = LEFT * 3,
        data_position: np.ndarray = RIGHT * 3
    ) -> None:
        """Set up the standard algorithm visualization layout."""
        # Create code block
        self.code_block = myCode(
            code=code,
            language=language,
            font_size=18
        ).move_to(code_position)
        
        # Create step counter
        self.step_counter = Text(
            f"Step: {self.current_step}",
            font_size=24
        ).to_edge(UP)
        
        # Add to scene
        self.scene.add(self.code_block, self.step_counter)
    
    def highlight_code_line(
        self,
        line_number: int,
        color: str = YELLOW
    ) -> None:
        """Highlight a specific line of code."""
        if self.code_block and 0 <= line_number < len(self.code_block.code):
            self.scene.play(
                self.code_block.code[line_number].animate.set_color(color),
                run_time=0.3
            )
    
    def update_step_counter(self) -> None:
        """Update the step counter."""
        self.current_step += 1
        if self.step_counter:
            new_counter = Text(
                f"Step: {self.current_step}",
                font_size=24
            ).move_to(self.step_counter)
            self.scene.play(
                Transform(self.step_counter, new_counter),
                run_time=0.3
            )


class SortingVisualizer(AlgorithmVisualizer):
    """Visualizer for sorting algorithms."""
    
    def __init__(
        self,
        scene: Scene,
        data: List[int],
        bar_width: float = 0.5,
        max_height: float = 4.0
    ):
        super().__init__(scene)
        self.data = data.copy()
        self.bars: List[Rectangle] = []
        self.bar_width = bar_width
        self.max_height = max_height
        self.comparisons = 0
        self.swaps = 0
        
        # Create bars
        self._create_bars()
        
        # Create statistics
        self.stats = VGroup(
            Text(f"Comparisons: {self.comparisons}", font_size=20),
            Text(f"Swaps: {self.swaps}", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(DR)
        self.scene.add(self.stats)
    
    def _create_bars(self) -> None:
        """Create bar representations of data."""
        max_val = max(self.data)
        total_width = self.bar_width * len(self.data)
        start_x = -total_width / 2
        
        for i, value in enumerate(self.data):
            height = (value / max_val) * self.max_height
            bar = Rectangle(
                width=self.bar_width * 0.9,
                height=height,
                fill_opacity=1,
                color=BLUE
            )
            bar.move_to(
                [start_x + i * self.bar_width, -self.max_height/2 + height/2, 0]
            )
            self.bars.append(bar)
            self.scene.add(bar)
    
    def compare(
        self,
        i: int,
        j: int,
        highlight_time: float = 0.3
    ) -> bool:
        """Animate comparison of two elements."""
        self.comparisons += 1
        self._update_stats()
        
        # Highlight bars
        self.scene.play(
            self.bars[i].animate.set_color(YELLOW),
            self.bars[j].animate.set_color(YELLOW),
            run_time=highlight_time
        )
        
        result = self.data[i] > self.data[j]
        
        # Reset colors
        self.scene.play(
            self.bars[i].animate.set_color(BLUE),
            self.bars[j].animate.set_color(BLUE),
            run_time=highlight_time
        )
        
        return result
    
    def swap(
        self,
        i: int,
        j: int,
        swap_time: float = 0.5
    ) -> None:
        """Animate swapping two elements."""
        self.swaps += 1
        self._update_stats()
        
        # Swap in data
        self.data[i], self.data[j] = self.data[j], self.data[i]
        
        # Animate swap
        pos_i = self.bars[i].get_center()
        pos_j = self.bars[j].get_center()
        
        self.scene.play(
            self.bars[i].animate.move_to(pos_j),
            self.bars[j].animate.move_to(pos_i),
            run_time=swap_time
        )
        
        # Swap bar references
        self.bars[i], self.bars[j] = self.bars[j], self.bars[i]
    
    def _update_stats(self) -> None:
        """Update statistics display."""
        new_stats = VGroup(
            Text(f"Comparisons: {self.comparisons}", font_size=20),
            Text(f"Swaps: {self.swaps}", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT).move_to(self.stats)
        
        self.scene.play(
            Transform(self.stats, new_stats),
            run_time=0.2
        )
    
    def bubble_sort(self) -> None:
        """Visualize bubble sort algorithm."""
        n = len(self.data)
        
        for i in range(n):
            for j in range(0, n - i - 1):
                self.update_step_counter()
                self.highlight_code_line(2)  # Comparison line
                
                if self.compare(j, j + 1):
                    self.highlight_code_line(3)  # Swap line
                    self.swap(j, j + 1)
    
    def quick_sort(
        self,
        low: int = 0,
        high: Optional[int] = None
    ) -> None:
        """Visualize quick sort algorithm."""
        if high is None:
            high = len(self.data) - 1
        
        if low < high:
            # Partition
            pivot_index = self._partition(low, high)
            
            # Recursively sort
            self.quick_sort(low, pivot_index - 1)
            self.quick_sort(pivot_index + 1, high)
    
    def _partition(self, low: int, high: int) -> int:
        """Partition for quick sort."""
        # Highlight pivot
        self.scene.play(
            self.bars[high].animate.set_color(RED),
            run_time=0.3
        )
        
        i = low - 1
        
        for j in range(low, high):
            self.update_step_counter()
            if self.compare(high, j):  # Compare with pivot
                i += 1
                if i != j:
                    self.swap(i, j)
        
        # Place pivot in correct position
        self.swap(i + 1, high)
        
        # Reset pivot color
        self.scene.play(
            self.bars[i + 1].animate.set_color(BLUE),
            run_time=0.3
        )
        
        return i + 1


class GraphAlgorithmVisualizer(AlgorithmVisualizer):
    """Visualizer for graph algorithms."""
    
    def __init__(
        self,
        scene: Scene,
        graph: Graph
    ):
        super().__init__(scene)
        self.graph = graph
        self.visited: Set[int] = set()
        self.distances: Dict[int, float] = {}
        self.parents: Dict[int, Optional[int]] = {}
    
    def mark_visited(
        self,
        vertex: int,
        color: str = GREEN
    ) -> None:
        """Mark a vertex as visited."""
        if vertex in self.graph:
            self.visited.add(vertex)
            self.scene.play(
                self.graph[vertex].animate.set_color(color),
                Flash(self.graph[vertex], color=color),
                run_time=0.5
            )
    
    def highlight_edge(
        self,
        u: int,
        v: int,
        color: str = YELLOW,
        width: float = 4
    ) -> None:
        """Highlight an edge in the graph."""
        edge = self.graph.edges[(u, v)]
        original_width = edge.stroke_width
        
        self.scene.play(
            edge.animate.set_stroke(color=color, width=width),
            run_time=0.3
        )
    
    def bfs(
        self,
        start: int,
        target: Optional[int] = None
    ) -> Optional[List[int]]:
        """Visualize breadth-first search."""
        # Initialize
        queue = VisualQueue(capacity=10)
        queue.move_to(RIGHT * 4)
        self.scene.add(queue)
        
        # Add start to queue
        start_node = Text(str(start), font_size=20)
        queue.enqueue(self.scene, start_node, start)
        self.mark_visited(start)
        self.parents[start] = None
        
        while queue.elements:
            # Dequeue
            current_elem, current = queue.dequeue(self.scene)
            self.update_step_counter()
            
            # Check if target found
            if current == target:
                path = self._reconstruct_path(start, target)
                self._highlight_path(path)
                return path
            
            # Explore neighbors
            for neighbor in self.graph[current]:
                if neighbor not in self.visited:
                    # Highlight edge
                    self.highlight_edge(current, neighbor)
                    
                    # Mark visited and enqueue
                    self.mark_visited(neighbor)
                    self.parents[neighbor] = current
                    
                    neighbor_elem = Text(str(neighbor), font_size=20)
                    queue.enqueue(self.scene, neighbor_elem, neighbor)
        
        return None
    
    def dfs(
        self,
        start: int,
        target: Optional[int] = None
    ) -> Optional[List[int]]:
        """Visualize depth-first search."""
        # Initialize
        stack = VisualStack(capacity=10)
        stack.move_to(RIGHT * 4)
        self.scene.add(stack)
        
        # Add start to stack
        start_node = Text(str(start), font_size=20)
        stack.push(self.scene, start_node, start)
        
        while stack.elements:
            # Pop from stack
            current_elem, current = stack.pop(self.scene)
            self.update_step_counter()
            
            if current not in self.visited:
                self.mark_visited(current)
                
                # Check if target found
                if current == target:
                    return self._reconstruct_path(start, target)
                
                # Add unvisited neighbors to stack
                for neighbor in reversed(list(self.graph[current])):
                    if neighbor not in self.visited:
                        # Highlight edge
                        self.highlight_edge(current, neighbor)
                        
                        neighbor_elem = Text(str(neighbor), font_size=20)
                        stack.push(self.scene, neighbor_elem, neighbor)
                        self.parents[neighbor] = current
        
        return None
    
    def _reconstruct_path(
        self,
        start: int,
        end: int
    ) -> List[int]:
        """Reconstruct path from start to end."""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = self.parents.get(current)
        
        return list(reversed(path))
    
    def _highlight_path(
        self,
        path: List[int],
        color: str = GOLD
    ) -> None:
        """Highlight a path in the graph."""
        for i in range(len(path) - 1):
            self.highlight_edge(path[i], path[i + 1], color, 6)
            self.scene.play(
                self.graph[path[i]].animate.set_color(color),
                run_time=0.3
            )