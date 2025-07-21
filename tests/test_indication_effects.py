"""
Test script for indication effects
"""
from manim import *
from src.manim_studio.components.effects.indication_effects import *

class TestIndicationEffects(Scene):
    def construct(self):
        # Test objects
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=1.5, color=RED).shift(RIGHT * 3)
        triangle = Triangle(color=GREEN).shift(LEFT * 3)
        
        # Add objects to scene
        self.add(circle, square, triangle)
        self.wait(0.5)
        
        # Test Indicate effect
        self.play(Indicate(circle))
        self.wait(0.5)
        
        # Test Flash effect  
        self.play(Flash(square.get_center()))
        self.wait(0.5)
        
        # Test CircleIndicate
        self.play(CircleIndicate(triangle))
        self.wait(0.5)
        
        # Test WiggleOutThenIn
        self.play(WiggleOutThenIn(circle))
        self.wait(0.5)
        
        # Test ApplyWave
        line = Line(LEFT * 2, RIGHT * 2, color=YELLOW)
        self.add(line)
        self.play(ApplyWave(line))
        self.wait(0.5)
        
        # Test FocusOn
        self.play(FocusOn(square.get_center()))
        self.wait(1)

if __name__ == "__main__":
    scene = TestIndicationEffects()
    scene.render()