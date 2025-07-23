"""Visual array component with advanced property management and animations.

Inspired by manim-data-structures but integrated with Manim Studio's architecture.
"""

from src.config.manim_config import config
from manim import *
from typing import List, Any, Optional, Union, Dict, Callable
from abc import ABC, abstractmethod
import numpy as np


class ComponentPropertyMixin:
    """Mixin for consistent property management across components."""
    
    def merge_props(self, defaults: dict, user_props: dict) -> dict:
        """Deep merge user properties with defaults."""
        result = defaults.copy()
        result.update(user_props)
        return result
    
    def get_component_props(self, component_name: str, **kwargs) -> dict:
        """Get merged properties for a specific component."""
        defaults = getattr(self, f"default_{component_name}_props", {})
        user_props = kwargs.get(f"{component_name}_args", {})
        return self.merge_props(defaults, user_props)


class DisplayFormatter(ABC):
    """Abstract base class for display formatters."""
    
    @abstractmethod
    def format_index(self, index: int, offset: int = 0) -> str:
        """Format an index value."""
        pass
    
    @abstractmethod
    def format_value(self, value: Any) -> str:
        """Format a data value."""
        pass


class DecimalFormatter(DisplayFormatter):
    """Standard decimal formatter."""
    
    def format_index(self, index: int, offset: int = 0) -> str:
        return str(index + offset)
    
    def format_value(self, value: Any) -> str:
        return str(value)


class HexFormatter(DisplayFormatter):
    """Hexadecimal formatter."""
    
    def format_index(self, index: int, offset: int = 0) -> str:
        return f"0x{index + offset:X}"
    
    def format_value(self, value: Any) -> str:
        if isinstance(value, (int, np.integer)):
            return f"0x{value:X}"
        return str(value)


class BinaryFormatter(DisplayFormatter):
    """Binary formatter."""
    
    def format_index(self, index: int, offset: int = 0) -> str:
        return f"0b{index + offset:b}"
    
    def format_value(self, value: Any) -> str:
        if isinstance(value, (int, np.integer)):
            return f"0b{value:b}"
        return str(value)


class VisualArrayElement(VGroup, ComponentPropertyMixin):
    """Visual array element with customizable components."""
    
    def __init__(
        self,
        value: Any,
        index: Optional[int] = None,
        label: Optional[str] = None,
        formatter: Optional[DisplayFormatter] = None,
        **kwargs
    ):
        super().__init__()
        
        self.value = value
        self.index = index
        self.label = label
        self.formatter = formatter or DecimalFormatter()
        
        # Default properties for each component
        self.default_body_props = {
            "color": BLUE_B,
            "fill_color": BLUE_D,
            "fill_opacity": 1,
            "side_length": 1,
        }
        
        self.default_value_props = {
            "color": WHITE,
            "font_size": 36,
            "weight": BOLD,
        }
        
        self.default_index_props = {
            "color": BLUE_D,
            "font_size": 24,
        }
        
        self.default_label_props = {
            "color": GRAY_A,
            "font_size": 20,
        }
        
        # Get merged properties
        body_props = self.get_component_props("body", **kwargs)
        value_props = self.get_component_props("value", **kwargs)
        index_props = self.get_component_props("index", **kwargs)
        label_props = self.get_component_props("label", **kwargs)
        
        # Create components
        self.body = Square(**body_props)
        
        # Value text
        value_text = self.formatter.format_value(value)
        self.value_text = Text(value_text, **value_props)
        self.value_text.move_to(self.body.get_center())
        
        # Index text (optional)
        if index is not None:
            index_offset = kwargs.get("index_offset", 0)
            index_text = self.formatter.format_index(index, index_offset)
            self.index_text = Text(index_text, **index_props)
            
            index_pos = kwargs.get("index_pos", DOWN)
            index_gap = kwargs.get("index_gap", 0.1)
            self.index_text.next_to(self.body, index_pos, buff=index_gap)
            self.add(self.index_text)
        
        # Label text (optional)
        if label is not None:
            self.label_text = Text(label, **label_props)
            
            label_pos = kwargs.get("label_pos", UP)
            label_gap = kwargs.get("label_gap", 0.1)
            self.label_text.next_to(self.body, label_pos, buff=label_gap)
            self.add(self.label_text)
        
        self.add(self.body, self.value_text)
    
    def animate_component(self, component_name: str):
        """Returns animation for specific component."""
        component = getattr(self, f"{component_name}_text", None) or getattr(self, component_name, None)
        if component:
            return component.animate
        raise ValueError(f"Component '{component_name}' not found")
    
    def update_value(self, new_value: Any, scene: Optional[Scene] = None, **kwargs):
        """Update the element's value with optional animation."""
        old_text = self.value_text
        new_text = Text(
            self.formatter.format_value(new_value),
            **self.get_component_props("value", **kwargs)
        )
        new_text.move_to(old_text.get_center())
        
        if scene:
            scene.play(Transform(old_text, new_text))
        else:
            self.remove(old_text)
            self.value_text = new_text
            self.add(new_text)
        
        self.value = new_value


class VisualArray(VGroup, ComponentPropertyMixin):
    """Visual array with advanced features and animations."""
    
    def __init__(
        self,
        values: List[Any],
        labels: Optional[List[str]] = None,
        show_indices: bool = True,
        formatter: Optional[Union[str, DisplayFormatter]] = None,
        growth_direction: np.ndarray = RIGHT,
        element_spacing: float = 0.1,
        **kwargs
    ):
        super().__init__()
        
        self.values = values
        self.labels = labels
        self.show_indices = show_indices
        self.growth_direction = growth_direction
        self.element_spacing = element_spacing
        
        # Set up formatter
        if isinstance(formatter, str):
            formatter_map = {
                "hex": HexFormatter(),
                "binary": BinaryFormatter(),
                "decimal": DecimalFormatter(),
            }
            self.formatter = formatter_map.get(formatter, DecimalFormatter())
        else:
            self.formatter = formatter or DecimalFormatter()
        
        # Create elements
        self.elements = []
        for i, value in enumerate(values):
            element_kwargs = kwargs.copy()
            element_kwargs["index"] = i if show_indices else None
            element_kwargs["label"] = labels[i] if labels and i < len(labels) else None
            element_kwargs["formatter"] = self.formatter
            
            element = VisualArrayElement(value, **element_kwargs)
            
            # Position element
            if i > 0:
                element.next_to(
                    self.elements[-1],
                    self.growth_direction,
                    buff=self.element_spacing
                )
            
            self.elements.append(element)
            self.add(element)
    
    def __getitem__(self, index: int) -> VisualArrayElement:
        """Get element by index."""
        return self.elements[index]
    
    def __len__(self) -> int:
        """Get array length."""
        return len(self.elements)
    
    def animate_element(self, index: int):
        """Animate a specific element."""
        return self.elements[index].animate
    
    def animate_value(self, index: int):
        """Animate just the value of an element."""
        return self.elements[index].animate_component("value")
    
    def animate_body(self, index: int):
        """Animate just the body of an element."""
        return self.elements[index].animate_component("body")
    
    def animate_index(self, index: int):
        """Animate just the index of an element."""
        return self.elements[index].animate_component("index")
    
    def highlight_elements(
        self,
        indices: List[int],
        color: str = YELLOW,
        scene: Optional[Scene] = None
    ):
        """Highlight multiple elements."""
        animations = []
        for i in indices:
            if 0 <= i < len(self.elements):
                animations.append(self.elements[i].body.animate.set_fill(color))
        
        if scene and animations:
            scene.play(*animations)
        elif animations:
            return AnimationGroup(*animations)
    
    def append_element(
        self,
        value: Any,
        scene: Optional[Scene] = None,
        **kwargs
    ) -> VisualArrayElement:
        """Append a new element to the array."""
        index = len(self.elements) if self.show_indices else None
        element_kwargs = kwargs.copy()
        element_kwargs["index"] = index
        element_kwargs["formatter"] = self.formatter
        
        new_element = VisualArrayElement(value, **element_kwargs)
        
        # Position new element
        if self.elements:
            new_element.next_to(
                self.elements[-1],
                self.growth_direction,
                buff=self.element_spacing
            )
        
        self.elements.append(new_element)
        self.values.append(value)
        
        if scene:
            scene.play(FadeIn(new_element, shift=self.growth_direction * 0.3))
        
        self.add(new_element)
        return new_element
    
    def remove_element(
        self,
        index: int,
        scene: Optional[Scene] = None
    ):
        """Remove an element from the array."""
        if not 0 <= index < len(self.elements):
            raise IndexError("Index out of range")
        
        element = self.elements.pop(index)
        self.values.pop(index)
        
        if scene:
            # Animate removal
            scene.play(FadeOut(element, shift=UP * 0.5))
            
            # Shift remaining elements
            if index < len(self.elements):
                animations = []
                for i in range(index, len(self.elements)):
                    # Update indices if shown
                    if self.show_indices:
                        self.elements[i].index = i
                        new_index_text = Text(
                            self.formatter.format_index(i),
                            **self.elements[i].default_index_props
                        )
                        new_index_text.move_to(self.elements[i].index_text)
                        animations.append(Transform(
                            self.elements[i].index_text,
                            new_index_text
                        ))
                    
                    # Shift position
                    if i == index:
                        target_pos = element.get_center()
                    else:
                        target_pos = self.elements[i-1].get_center() + \
                                   self.growth_direction * (
                                       self.elements[i-1].width + self.element_spacing
                                   )
                    animations.append(self.elements[i].animate.move_to(target_pos))
                
                scene.play(*animations)
        
        self.remove(element)
    
    def swap_elements(
        self,
        i: int,
        j: int,
        scene: Optional[Scene] = None
    ):
        """Swap two elements with animation."""
        if not (0 <= i < len(self.elements) and 0 <= j < len(self.elements)):
            raise IndexError("Index out of range")
        
        if i == j:
            return
        
        # Swap in data
        self.values[i], self.values[j] = self.values[j], self.values[i]
        
        # Get elements
        elem_i = self.elements[i]
        elem_j = self.elements[j]
        
        if scene:
            # Animate swap
            pos_i = elem_i.get_center()
            pos_j = elem_j.get_center()
            
            # Arc swap animation
            scene.play(
                elem_i.animate.move_to(pos_j),
                elem_j.animate.move_to(pos_i),
                path_arc=PI/2 if i < j else -PI/2
            )
        
        # Swap in list
        self.elements[i], self.elements[j] = self.elements[j], self.elements[i]


class ArrayPointer(VGroup):
    """Animated pointer for array traversal."""
    
    def __init__(
        self,
        label: str = "",
        direction: np.ndarray = UP,
        color: str = RED,
        **kwargs
    ):
        super().__init__()
        
        self.direction = direction
        
        # Create arrow
        self.arrow = Arrow(
            ORIGIN,
            -direction * 0.5,
            color=color,
            buff=0
        )
        
        # Create label if provided
        if label:
            self.label = Text(label, font_size=24, color=color)
            self.label.next_to(self.arrow, direction, buff=0.1)
            self.add(self.label)
        
        self.add(self.arrow)
    
    def point_to_element(
        self,
        element: VisualArrayElement,
        scene: Optional[Scene] = None,
        **kwargs
    ):
        """Point to a specific array element."""
        target_pos = element.get_center() + self.direction * (
            element.height / 2 + 0.3
        )
        
        if scene:
            scene.play(self.animate.move_to(target_pos), **kwargs)
        else:
            self.move_to(target_pos)


class ArraySlidingWindow(VGroup):
    """Sliding window visualization for arrays."""
    
    def __init__(
        self,
        array: VisualArray,
        window_size: int,
        color: str = GREEN,
        **kwargs
    ):
        super().__init__()
        
        self.array = array
        self.window_size = window_size
        self.current_start = 0
        
        # Create window rectangle
        if window_size > 0 and len(array) > 0:
            # Calculate window dimensions
            first_elem = array[0]
            last_elem = array[min(window_size - 1, len(array) - 1)]
            
            width = abs(last_elem.get_right()[0] - first_elem.get_left()[0]) + 0.2
            height = first_elem.height + 0.4
            
            self.window = Rectangle(
                width=width,
                height=height,
                color=color,
                stroke_width=3,
                fill_opacity=0.1,
                fill_color=color
            )
            
            # Position window
            center_x = (first_elem.get_center()[0] + last_elem.get_center()[0]) / 2
            center_y = first_elem.get_center()[1]
            self.window.move_to([center_x, center_y, 0])
            
            self.add(self.window)
    
    def slide_to(
        self,
        start_index: int,
        scene: Optional[Scene] = None
    ):
        """Slide window to new position."""
        if start_index < 0 or start_index + self.window_size > len(self.array):
            raise ValueError("Invalid window position")
        
        self.current_start = start_index
        
        # Calculate new position
        first_elem = self.array[start_index]
        last_elem = self.array[start_index + self.window_size - 1]
        
        center_x = (first_elem.get_center()[0] + last_elem.get_center()[0]) / 2
        center_y = first_elem.get_center()[1]
        
        if scene:
            scene.play(self.window.animate.move_to([center_x, center_y, 0]))
        else:
            self.window.move_to([center_x, center_y, 0])


class ArrayBuilder:
    """Builder pattern for creating complex array configurations."""
    
    def __init__(self):
        self.values = []
        self.labels = None
        self.show_indices = True
        self.formatter = None
        self.growth_direction = RIGHT
        self.element_spacing = 0.1
        self.kwargs = {}
    
    def with_values(self, values: List[Any]) -> 'ArrayBuilder':
        """Set array values."""
        self.values = values
        return self
    
    def with_labels(self, labels: List[str]) -> 'ArrayBuilder':
        """Add labels to elements."""
        self.labels = labels
        return self
    
    def with_indices(self, show: bool = True) -> 'ArrayBuilder':
        """Show/hide indices."""
        self.show_indices = show
        return self
    
    def with_hex_indices(self, offset: int = 0) -> 'ArrayBuilder':
        """Use hexadecimal indices."""
        self.formatter = HexFormatter()
        self.kwargs['index_offset'] = offset
        return self
    
    def with_binary_format(self) -> 'ArrayBuilder':
        """Use binary format."""
        self.formatter = BinaryFormatter()
        return self
    
    def with_growth_direction(self, direction: np.ndarray) -> 'ArrayBuilder':
        """Set growth direction."""
        self.growth_direction = direction
        return self
    
    def with_spacing(self, spacing: float) -> 'ArrayBuilder':
        """Set element spacing."""
        self.element_spacing = spacing
        return self
    
    def with_style(self, **style_kwargs) -> 'ArrayBuilder':
        """Add custom style arguments."""
        self.kwargs.update(style_kwargs)
        return self
    
    def build(self) -> VisualArray:
        """Build the array."""
        return VisualArray(
            values=self.values,
            labels=self.labels,
            show_indices=self.show_indices,
            formatter=self.formatter,
            growth_direction=self.growth_direction,
            element_spacing=self.element_spacing,
            **self.kwargs
        )