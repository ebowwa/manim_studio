"""Demonstration of improved 2D layering system."""

from manim import *
from src.core.layer_manager import LayerManager

class LayeringDemo(Scene):
    """Demonstrates proper 2D layering with the LayerManager."""
    
    def construct(self):
        # Create layer manager
        layer_manager = LayerManager()
        
        # Create background elements
        bg_rect = Rectangle(width=14, height=8, color=BLUE_E, fill_opacity=0.3)
        layer_manager.add_object(bg_rect, "background")
        
        # Create environment elements
        ground = Rectangle(width=14, height=2, color=GREEN_E, fill_opacity=0.5)
        ground.to_edge(DOWN, buff=0)
        layer_manager.add_object(ground, "environment")
        
        # Create main objects with deliberate overlapping
        # These circles will overlap to demonstrate layering
        circle1 = Circle(radius=1.5, color=RED, fill_opacity=0.8)
        circle1.shift(LEFT * 2)
        layer_manager.add_object(circle1, "main", z_offset=0)
        
        circle2 = Circle(radius=1.5, color=YELLOW, fill_opacity=0.8)
        circle2.shift(LEFT * 1)
        layer_manager.add_object(circle2, "main", z_offset=10)
        
        circle3 = Circle(radius=1.5, color=GREEN, fill_opacity=0.8)
        layer_manager.add_object(circle3, "main", z_offset=20)
        
        # Create text that should appear above main objects
        title = Text("Layering Demo", font_size=48)
        title.to_edge(UP)
        layer_manager.add_object(title, "text")
        
        # Create effect elements
        glow1 = Circle(radius=2, color=YELLOW, fill_opacity=0)
        glow1.set_stroke(YELLOW, width=8, opacity=0.3)
        glow1.shift(RIGHT * 2)
        layer_manager.add_object(glow1, "effects")
        
        # Create particles that should be above effects
        particles = VGroup()
        for i in range(20):
            particle = Dot(radius=0.05, color=WHITE)
            particle.move_to([
                np.random.uniform(-5, 5),
                np.random.uniform(-2, 2),
                0
            ])
            particles.add(particle)
        layer_manager.add_object(particles, "particles")
        
        # Create foreground overlay
        overlay = Rectangle(
            width=14, height=8,
            color=BLACK,
            fill_opacity=0.2,
            stroke_width=0
        )
        layer_manager.add_object(overlay, "foreground")
        
        # Create UI elements (should be on top)
        info_text = Text("Z-Index Layers Active", font_size=24, color=WHITE)
        info_text.to_corner(DR)
        layer_manager.add_object(info_text, "ui")
        
        # Add all objects to scene
        all_objects = layer_manager.get_all_objects_sorted()
        self.add(*all_objects)
        
        # Animate to show layering
        self.wait(1)
        
        # Show overlapping circles animation
        self.play(
            circle1.animate.shift(RIGHT * 2),
            circle2.animate.shift(RIGHT * 2),
            circle3.animate.shift(RIGHT * 2),
            run_time=2
        )
        
        self.wait(1)
        
        # Demonstrate moving objects between layers
        self.play(info_text.animate.set_color(GREEN))
        
        # Move circle3 to background
        layer_manager.clear_layer("main")
        layer_manager.add_object(circle1, "main", z_offset=0)
        layer_manager.add_object(circle2, "main", z_offset=10)
        layer_manager.add_object(circle3, "background", z_offset=50)
        
        self.play(
            circle3.animate.set_color(BLUE).set_fill_opacity(0.4),
            run_time=1
        )
        
        self.wait(2)


class BadLayeringExample(Scene):
    """Example showing bad layering without LayerManager."""
    
    def construct(self):
        # Create same objects but without proper layering
        bg_rect = Rectangle(width=14, height=8, color=BLUE_E, fill_opacity=0.3)
        ground = Rectangle(width=14, height=2, color=GREEN_E, fill_opacity=0.5)
        ground.to_edge(DOWN, buff=0)
        
        circle1 = Circle(radius=1.5, color=RED, fill_opacity=0.8)
        circle1.shift(LEFT * 2)
        
        circle2 = Circle(radius=1.5, color=YELLOW, fill_opacity=0.8)
        circle2.shift(LEFT * 1)
        
        circle3 = Circle(radius=1.5, color=GREEN, fill_opacity=0.8)
        
        title = Text("Bad Layering Example", font_size=48)
        title.to_edge(UP)
        
        glow1 = Circle(radius=2, color=YELLOW, fill_opacity=0)
        glow1.set_stroke(YELLOW, width=8, opacity=0.3)
        glow1.shift(RIGHT * 2)
        
        particles = VGroup()
        for i in range(20):
            particle = Dot(radius=0.05, color=WHITE)
            particle.move_to([
                np.random.uniform(-5, 5),
                np.random.uniform(-2, 2),
                0
            ])
            particles.add(particle)
        
        overlay = Rectangle(
            width=14, height=8,
            color=BLACK,
            fill_opacity=0.2,
            stroke_width=0
        )
        
        info_text = Text("No Z-Index Management", font_size=24, color=RED)
        info_text.to_corner(DR)
        
        # Add objects in wrong order - demonstrates the problem
        self.add(overlay)  # Overlay added first - will be behind everything!
        self.add(title)
        self.add(particles)
        self.add(circle1, circle2, circle3)
        self.add(bg_rect)  # Background added after circles!
        self.add(ground)
        self.add(glow1)
        self.add(info_text)
        
        self.wait(1)
        
        # Animation will look wrong due to bad layering
        self.play(
            circle1.animate.shift(RIGHT * 2),
            circle2.animate.shift(RIGHT * 2),
            circle3.animate.shift(RIGHT * 2),
            run_time=2
        )
        
        self.wait(2)