"""Advanced data structure visualizations for Manim."""
from manim import *
from typing import List, Any, Optional, Callable
from utils.utilities import staggered_animation_group


class VisualQueue(VMobject):
    """Visual representation of a queue data structure."""
    
    def __init__(
        self,
        capacity: int = 10,
        element_width: float = 1.0,
        element_height: float = 0.8,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.capacity = capacity
        self.element_width = element_width
        self.element_height = element_height
        self.elements: List[VMobject] = []
        self.queue_data: List[Any] = []
        
        # Create container
        self.container = Rectangle(
            width=element_width,
            height=element_height * capacity,
            stroke_color=WHITE,
            stroke_width=2
        )
        
        # Create in/out labels
        self.in_label = Text("In", font_size=24).next_to(
            self.container, UP, buff=0.2
        )
        self.out_label = Text("Out", font_size=24).next_to(
            self.container, DOWN, buff=0.2
        )
        
        # Create arrows
        self.in_arrow = Arrow(
            self.in_label.get_bottom(),
            self.container.get_top(),
            buff=0.1,
            color=GREEN
        )
        self.out_arrow = Arrow(
            self.container.get_bottom(),
            self.out_label.get_top(),
            buff=0.1,
            color=RED
        )
        
        self.add(
            self.container,
            self.in_label,
            self.out_label,
            self.in_arrow,
            self.out_arrow
        )
    
    def enqueue(
        self,
        scene: Scene,
        element: VMobject,
        data: Any = None,
        run_time: float = 1.0
    ) -> None:
        """Animate adding an element to the queue."""
        if len(self.elements) >= self.capacity:
            raise ValueError("Queue is full")
        
        # Scale element to fit
        element.set_width(self.element_width * 0.9)
        element.set_height(self.element_height * 0.9)
        
        # Position element
        if self.elements:
            element.next_to(self.elements[-1], UP, buff=0.05)
        else:
            element.move_to(self.container.get_bottom() + UP * self.element_height * 0.5)
        
        # Animate
        element.save_state()
        element.move_to(self.in_arrow.get_start())
        element.set_opacity(0)
        
        scene.play(
            element.animate.restore().set_opacity(1),
            self.in_arrow.animate.set_color(YELLOW),
            run_time=run_time
        )
        scene.play(self.in_arrow.animate.set_color(GREEN), run_time=0.2)
        
        self.elements.append(element)
        self.queue_data.append(data)
        self.add(element)
    
    def dequeue(
        self,
        scene: Scene,
        run_time: float = 1.0
    ) -> Optional[Tuple[VMobject, Any]]:
        """Animate removing an element from the queue."""
        if not self.elements:
            return None
        
        element = self.elements.pop(0)
        data = self.queue_data.pop(0)
        
        # Animate removal
        scene.play(
            element.animate.move_to(self.out_arrow.get_end()).set_opacity(0),
            self.out_arrow.animate.set_color(YELLOW),
            run_time=run_time
        )
        scene.play(self.out_arrow.animate.set_color(RED), run_time=0.2)
        
        # Shift remaining elements down
        if self.elements:
            animations = [
                elem.animate.shift(DOWN * self.element_height)
                for elem in self.elements
            ]
            scene.play(*animations, run_time=0.5)
        
        self.remove(element)
        return element, data
    
    def clear(self, scene: Scene) -> None:
        """Clear all elements from the queue."""
        if self.elements:
            scene.play(
                *[FadeOut(elem) for elem in self.elements],
                run_time=0.5
            )
            for elem in self.elements:
                self.remove(elem)
            self.elements.clear()
            self.queue_data.clear()


class VisualStack(VMobject):
    """Visual representation of a stack data structure."""
    
    def __init__(
        self,
        capacity: int = 10,
        element_width: float = 2.0,
        element_height: float = 0.5,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.capacity = capacity
        self.element_width = element_width
        self.element_height = element_height
        self.elements: List[VMobject] = []
        self.stack_data: List[Any] = []
        
        # Create base
        self.base = Line(
            LEFT * element_width * 0.6,
            RIGHT * element_width * 0.6,
            stroke_width=4
        )
        
        # Create walls
        wall_height = element_height * capacity
        self.left_wall = Line(
            self.base.get_start(),
            self.base.get_start() + UP * wall_height,
            stroke_width=2
        )
        self.right_wall = Line(
            self.base.get_end(),
            self.base.get_end() + UP * wall_height,
            stroke_width=2
        )
        
        # Create top arrow
        self.top_arrow = Arrow(
            self.base.get_center() + UP * (wall_height + 0.5),
            self.base.get_center() + UP * wall_height,
            color=BLUE
        )
        
        self.add(
            self.base,
            self.left_wall,
            self.right_wall,
            self.top_arrow
        )
    
    def push(
        self,
        scene: Scene,
        element: VMobject,
        data: Any = None,
        run_time: float = 1.0
    ) -> None:
        """Animate pushing an element onto the stack."""
        if len(self.elements) >= self.capacity:
            raise ValueError("Stack overflow!")
        
        # Scale element
        element.set_width(self.element_width * 0.9)
        element.set_height(self.element_height * 0.9)
        
        # Position element
        stack_height = len(self.elements) * self.element_height
        element.move_to(
            self.base.get_center() + UP * (stack_height + self.element_height * 0.5)
        )
        
        # Animate
        element.save_state()
        element.move_to(self.top_arrow.get_start())
        element.set_opacity(0)
        
        scene.play(
            element.animate.restore().set_opacity(1),
            self.top_arrow.animate.set_color(YELLOW),
            run_time=run_time
        )
        scene.play(self.top_arrow.animate.set_color(BLUE), run_time=0.2)
        
        self.elements.append(element)
        self.stack_data.append(data)
        self.add(element)
    
    def pop(
        self,
        scene: Scene,
        run_time: float = 1.0
    ) -> Optional[Tuple[VMobject, Any]]:
        """Animate popping an element from the stack."""
        if not self.elements:
            return None
        
        element = self.elements.pop()
        data = self.stack_data.pop()
        
        scene.play(
            element.animate.move_to(self.top_arrow.get_start()).set_opacity(0),
            self.top_arrow.animate.set_color(YELLOW),
            run_time=run_time
        )
        scene.play(self.top_arrow.animate.set_color(BLUE), run_time=0.2)
        
        self.remove(element)
        return element, data


class VisualBinaryTree(VMobject):
    """Visual representation of a binary tree."""
    
    def __init__(
        self,
        root_value: Any,
        node_radius: float = 0.3,
        level_height: float = 1.5,
        sibling_distance: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.root_value = root_value
        self.node_radius = node_radius
        self.level_height = level_height
        self.sibling_distance = sibling_distance
        
        # Create root node
        self.root = self._create_node(root_value)
        self.nodes = {"root": self.root}
        self.edges = {}
        self.add(self.root)
    
    def _create_node(self, value: Any) -> VGroup:
        """Create a node with value."""
        circle = Circle(
            radius=self.node_radius,
            color=WHITE,
            fill_opacity=1,
            fill_color=BLACK
        )
        text = Text(str(value), font_size=24).move_to(circle)
        return VGroup(circle, text)
    
    def add_left_child(
        self,
        parent_key: str,
        child_value: Any,
        child_key: str,
        scene: Optional[Scene] = None
    ) -> None:
        """Add left child to a node."""
        if parent_key not in self.nodes:
            raise ValueError(f"Parent node {parent_key} not found")
        
        parent = self.nodes[parent_key]
        child = self._create_node(child_value)
        
        # Position child
        level = parent_key.count("_") + 1
        offset = self.sibling_distance * (2 ** (3 - level))
        child.move_to(
            parent.get_center() + 
            DOWN * self.level_height + 
            LEFT * offset
        )
        
        # Create edge
        edge = Line(
            parent.get_bottom(),
            child.get_top(),
            color=GRAY
        )
        
        self.nodes[child_key] = child
        self.edges[f"{parent_key}_to_{child_key}"] = edge
        
        if scene:
            scene.play(
                Create(edge),
                FadeIn(child, shift=DOWN * 0.3),
                run_time=0.5
            )
        
        self.add(edge, child)
    
    def add_right_child(
        self,
        parent_key: str,
        child_value: Any,
        child_key: str,
        scene: Optional[Scene] = None
    ) -> None:
        """Add right child to a node."""
        if parent_key not in self.nodes:
            raise ValueError(f"Parent node {parent_key} not found")
        
        parent = self.nodes[parent_key]
        child = self._create_node(child_value)
        
        # Position child
        level = parent_key.count("_") + 1
        offset = self.sibling_distance * (2 ** (3 - level))
        child.move_to(
            parent.get_center() + 
            DOWN * self.level_height + 
            RIGHT * offset
        )
        
        # Create edge
        edge = Line(
            parent.get_bottom(),
            child.get_top(),
            color=GRAY
        )
        
        self.nodes[child_key] = child
        self.edges[f"{parent_key}_to_{child_key}"] = edge
        
        if scene:
            scene.play(
                Create(edge),
                FadeIn(child, shift=DOWN * 0.3),
                run_time=0.5
            )
        
        self.add(edge, child)
    
    def highlight_node(
        self,
        node_key: str,
        color: str = YELLOW,
        scene: Optional[Scene] = None
    ) -> None:
        """Highlight a specific node."""
        if node_key in self.nodes:
            node = self.nodes[node_key]
            if scene:
                scene.play(
                    node[0].animate.set_color(color),
                    Flash(node, color=color)
                )
            else:
                node[0].set_color(color)