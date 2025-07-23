from src.config.manim_config import config
from manim import *
from src.components.cad_objects import RoundCorners, LinearDimension, HatchPattern

class TestCADSimple(Scene):
    def construct(self):
        # Create a rounded rectangle
        rect = Rectangle(width=4, height=2, color=BLUE)
        rounded = RoundCorners.apply(rect, radius=0.3)
        
        # Add dimension
        dim = LinearDimension(
            start=rounded.get_corner(DL),
            end=rounded.get_corner(DR),
            text="4.00",
            direction=DOWN,
            offset=1,
            color=RED
        )
        
        # Add hatching
        hatch = HatchPattern(rounded, angle=PI/4, spacing=0.2)
        hatch.set_color(BLUE_A)
        
        # Animate
        self.play(Create(rounded))
        self.play(Create(dim))
        self.play(Create(hatch))
        self.wait()

if __name__ == "__main__":
    from manim import tempconfig
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = TestCADSimple()
        scene.render()