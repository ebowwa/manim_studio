"""Visual Array Component Demo

Demonstrates the new VisualArray component with various features:
- Basic arrays with values and indices
- Hex and binary display formats
- Array operations (append, remove, swap)
- Pointers and sliding windows
- Custom styling
"""

import sys
import os
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.manim_config import config
from manim import *
from src.components.visual_array import (
    VisualArray, ArrayBuilder, ArrayPointer, ArraySlidingWindow
)


class VisualArrayDemo(Scene):
    def construct(self):
        # Title
        title = Text("Visual Array Component Demo", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP))
        
        # 1. Basic array
        subtitle = Text("Basic Array", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        basic_array = VisualArray([3, 1, 4, 1, 5, 9])
        basic_array.move_to(ORIGIN)
        self.play(Create(basic_array))
        self.wait(2)
        
        # 2. Array with custom styling
        self.play(FadeOut(basic_array), FadeOut(subtitle))
        subtitle = Text("Custom Styled Array", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        styled_array = ArrayBuilder()\
            .with_values([10, 20, 30, 40, 50])\
            .with_style(
                body_args={'fill_color': BLUE_E, 'side_length': 1.2},
                value_args={'color': YELLOW, 'font_size': 42},
                index_args={'color': ORANGE, 'font_size': 20}
            )\
            .build()
        styled_array.move_to(ORIGIN)
        self.play(Create(styled_array))
        self.wait(2)
        
        # 3. Hex display format
        self.play(FadeOut(styled_array), FadeOut(subtitle))
        subtitle = Text("Hexadecimal Format", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        hex_array = ArrayBuilder()\
            .with_values([255, 16, 32, 64, 128])\
            .with_hex_indices(offset=0x1000)\
            .build()
        hex_array.move_to(ORIGIN)
        self.play(Create(hex_array))
        self.wait(2)
        
        # 4. Binary format
        self.play(FadeOut(hex_array), FadeOut(subtitle))
        subtitle = Text("Binary Format", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        binary_array = ArrayBuilder()\
            .with_values([1, 2, 4, 8, 16])\
            .with_binary_format()\
            .build()
        binary_array.move_to(ORIGIN)
        self.play(Create(binary_array))
        self.wait(2)
        
        # 5. Array operations
        self.play(FadeOut(binary_array), FadeOut(subtitle))
        subtitle = Text("Array Operations", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        ops_array = VisualArray([1, 2, 3, 4])
        ops_array.move_to(ORIGIN + UP)
        self.play(Create(ops_array))
        
        # Append element
        operation_text = Text("Append 5", font_size=24).to_edge(DOWN)
        self.play(Write(operation_text))
        ops_array.append_element(5, self)
        self.wait()
        
        # Remove element
        self.play(operation_text.animate.become(Text("Remove index 2", font_size=24).to_edge(DOWN)))
        ops_array.remove_element(2, self)
        self.wait()
        
        # Swap elements
        self.play(operation_text.animate.become(Text("Swap indices 0 and 3", font_size=24).to_edge(DOWN)))
        ops_array.swap_elements(0, 3, self)
        self.wait()
        
        # 6. Array pointer
        self.play(FadeOut(operation_text))
        self.play(ops_array.animate.move_to(ORIGIN))
        
        pointer = ArrayPointer(label="ptr", color=RED)
        pointer.point_to_element(ops_array[0])
        self.play(Create(pointer))
        
        # Move pointer through array
        for i in range(1, len(ops_array)):
            self.play(pointer.animate.point_to_element(ops_array[i], run_time=0.5))
        self.wait()
        
        # 7. Sliding window
        self.play(FadeOut(pointer), FadeOut(subtitle))
        subtitle = Text("Sliding Window", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        window_array = VisualArray([1, 2, 3, 4, 5, 6, 7, 8])
        window_array.move_to(ORIGIN)
        self.play(ReplacementTransform(ops_array, window_array))
        
        window = ArraySlidingWindow(window_array, window_size=3)
        self.play(Create(window))
        
        # Slide window
        for i in range(1, 6):
            self.play(window.animate.slide_to(i, run_time=0.7))
            self.wait(0.3)
        
        # 8. Array with labels
        self.play(FadeOut(window), FadeOut(window_array), FadeOut(subtitle))
        subtitle = Text("Labeled Array", font_size=36).next_to(title, DOWN)
        self.play(Write(subtitle))
        
        labeled_array = ArrayBuilder()\
            .with_values(['A', 'B', 'C', 'D'])\
            .with_labels(['Alpha', 'Beta', 'Gamma', 'Delta'])\
            .with_style(
                label_args={'color': GREEN, 'font_size': 18}
            )\
            .build()
        labeled_array.move_to(ORIGIN)
        self.play(Create(labeled_array))
        self.wait(2)
        
        # Highlight elements
        labeled_array.highlight_elements([1, 3], YELLOW, self)
        self.wait()
        
        # Final cleanup
        self.play(FadeOut(labeled_array), FadeOut(subtitle), FadeOut(title))
        
        # End card
        end_text = VGroup(
            Text("Visual Array Features:", font_size=36),
            Text("• Customizable styling", font_size=24),
            Text("• Multiple display formats", font_size=24),
            Text("• Array operations", font_size=24),
            Text("• Pointers & sliding windows", font_size=24),
            Text("• Labels & highlighting", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        end_text.move_to(ORIGIN)
        
        self.play(Write(end_text))
        self.wait(3)


class AlgorithmVisualizationDemo(Scene):
    """Demonstrates using VisualArray for algorithm visualization."""
    
    def construct(self):
        title = Text("Bubble Sort Visualization", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP))
        
        # Create array for sorting
        values = [64, 34, 25, 12, 22, 11, 90]
        array = VisualArray(values)
        array.move_to(ORIGIN)
        self.play(Create(array))
        
        # Add comparison counter
        comparison_text = Text("Comparisons: 0", font_size=24).to_edge(LEFT)
        swap_text = Text("Swaps: 0", font_size=24).to_edge(RIGHT)
        self.play(Write(comparison_text), Write(swap_text))
        
        comparisons = 0
        swaps = 0
        
        # Bubble sort
        n = len(values)
        for i in range(n):
            for j in range(0, n-i-1):
                # Highlight elements being compared
                self.play(
                    array[j].body.animate.set_stroke(RED, width=4),
                    array[j+1].body.animate.set_stroke(RED, width=4),
                    run_time=0.3
                )
                
                comparisons += 1
                self.play(
                    comparison_text.animate.become(
                        Text(f"Comparisons: {comparisons}", font_size=24).to_edge(LEFT)
                    ),
                    run_time=0.1
                )
                
                # Compare and swap if needed
                if values[j] > values[j+1]:
                    values[j], values[j+1] = values[j+1], values[j]
                    array.swap_elements(j, j+1, self)
                    swaps += 1
                    self.play(
                        swap_text.animate.become(
                            Text(f"Swaps: {swaps}", font_size=24).to_edge(RIGHT)
                        ),
                        run_time=0.1
                    )
                
                # Remove highlight
                self.play(
                    array[j].body.animate.set_stroke(BLUE_B, width=2),
                    array[j+1].body.animate.set_stroke(BLUE_B, width=2),
                    run_time=0.2
                )
            
            # Mark sorted element
            self.play(
                array[n-i-1].body.animate.set_fill(GREEN_D),
                run_time=0.3
            )
        
        # Mark first element as sorted
        self.play(array[0].body.animate.set_fill(GREEN_D))
        
        # Show completion
        complete_text = Text("Sorting Complete!", font_size=36, color=GREEN)\
            .next_to(array, DOWN, buff=1)
        self.play(Write(complete_text))
        self.wait(2)


if __name__ == "__main__":
    # Run with: manim --media_dir user-data visual_array_demo.py VisualArrayDemo -q l -p
    from manim import config as manim_config
    manim_config.media_dir = "user-data"