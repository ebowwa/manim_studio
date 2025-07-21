#!/usr/bin/env python3
"""
Test script to demonstrate the unified rate function integration.
Shows how both Manim rate functions and custom easings can be used together.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manim import *
from core.timeline.composer_timeline import ComposerTimeline, InterpolationType
from core.timeline.easing import EasingFunction
from core.timeline.rate_function_bridge import get_rate_function, compose_rate_functions


class RateFunctionDemoScene(Scene):
    """Demonstrates unified rate function integration."""
    
    def construct(self):
        # Test 1: Using Manim rate functions directly
        self.test_manim_rate_functions()
        self.clear()
        
        # Test 2: Using custom easing functions
        self.test_custom_easings()
        self.clear()
        
        # Test 3: Using the unified interface
        self.test_unified_interface()
        self.clear()
        
        # Test 4: Timeline integration
        self.test_timeline_integration()
    
    def test_manim_rate_functions(self):
        """Test direct use of Manim rate functions."""
        title = Text("Direct Manim Rate Functions", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Create test objects
        squares = VGroup()
        labels = VGroup()
        
        rate_functions = [
            ("linear", linear),
            ("smooth", smooth),
            ("there_and_back", there_and_back),
            ("rush_into", rush_into)
        ]
        
        for i, (name, func) in enumerate(rate_functions):
            square = Square(side_length=0.5, color=BLUE)
            square.move_to(LEFT * 4 + UP * (1.5 - i * 1))
            
            label = Text(name, font_size=20)
            label.next_to(square, LEFT)
            
            squares.add(square)
            labels.add(label)
        
        self.play(FadeIn(squares), Write(labels))
        
        # Animate with different rate functions
        animations = []
        for square, (name, func) in zip(squares, rate_functions):
            animations.append(
                square.animate(rate_func=func, run_time=2).shift(RIGHT * 6)
            )
        
        self.play(*animations)
        self.wait(1)
    
    def test_custom_easings(self):
        """Test custom easing functions."""
        title = Text("Custom Easing Functions", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Test custom easings through the unified interface
        squares = VGroup()
        labels = VGroup()
        
        custom_easings = [
            "bounce",
            "elastic", 
            "back",
            "spring"
        ]
        
        for i, name in enumerate(custom_easings):
            square = Square(side_length=0.5, color=GREEN)
            square.move_to(LEFT * 4 + UP * (1.5 - i * 1))
            
            label = Text(name, font_size=20)
            label.next_to(square, LEFT)
            
            squares.add(square)
            labels.add(label)
        
        self.play(FadeIn(squares), Write(labels))
        
        # Animate with custom easings via unified interface
        animations = []
        for square, name in zip(squares, custom_easings):
            rate_func = get_rate_function(name)
            animations.append(
                square.animate(rate_func=rate_func, run_time=2).shift(RIGHT * 6)
            )
        
        self.play(*animations)
        self.wait(1)
    
    def test_unified_interface(self):
        """Test the unified rate function interface."""
        title = Text("Unified Interface", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Test mixing Manim and custom functions
        circle = Circle(radius=0.5, color=YELLOW)
        self.play(FadeIn(circle))
        
        # Test 1: there_and_back (Manim function)
        rate_func1 = get_rate_function("there_and_back")
        self.play(
            circle.animate(rate_func=rate_func1, run_time=2).shift(UP * 2)
        )
        
        # Test 2: bounce (Custom easing)
        rate_func2 = get_rate_function("bounce")
        self.play(
            circle.animate(rate_func=rate_func2, run_time=2).shift(DOWN * 2)
        )
        
        # Test 3: Composed rate function
        composed = compose_rate_functions("smooth", "wiggle", weights=[0.7, 0.3])
        self.play(
            circle.animate(rate_func=composed, run_time=2).shift(RIGHT * 3)
        )
        
        self.wait(1)
    
    def test_timeline_integration(self):
        """Test rate function integration with the timeline system."""
        title = Text("Timeline Integration", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Create timeline
        timeline = ComposerTimeline()
        timeline.add_layer("Main")
        timeline.add_track("Main", "objects", "animation")
        
        # Create test object
        square = Square(color=PURPLE)
        self.play(FadeIn(square))
        
        # Test 1: Using InterpolationType with new Manim types
        timeline.add_keyframe("Main", "objects", "position", 0, square.get_center())
        timeline.add_keyframe("Main", "objects", "position", 1, square.get_center() + UP * 2, 
                            interpolation=InterpolationType.THERE_AND_BACK)
        timeline.add_keyframe("Main", "objects", "position", 2, square.get_center() + RIGHT * 3, 
                            interpolation=InterpolationType.RUSH_INTO)
        
        # Animate timeline keyframes
        for t in np.linspace(0, 2, 60):
            pos = timeline.get_value_at_time("Main", "objects", "position", t)
            if pos is not None:
                square.move_to(pos)
            self.wait(1/30)
        
        # Test 2: Using rate_function parameter directly
        timeline.clear_keyframes("Main", "objects", "position")
        timeline.add_keyframe("Main", "objects", "position", 0, square.get_center())
        timeline.add_keyframe("Main", "objects", "position", 1, square.get_center() + LEFT * 4, 
                            rate_function="wiggle")
        
        # Animate with direct rate function
        for t in np.linspace(0, 1, 60):
            pos = timeline.get_value_at_time("Main", "objects", "position", t)
            if pos is not None:
                square.move_to(pos)
            self.wait(1/30)
        
        self.wait(1)


def test_rate_function_bridge():
    """Test the rate function bridge directly."""
    print("Testing Rate Function Bridge...")
    
    # Test 1: Get Manim functions
    manim_smooth = get_rate_function("smooth")
    print(f"Manim smooth(0.5) = {manim_smooth(0.5)}")
    
    # Test 2: Get custom easings
    bounce_func = get_rate_function("bounce")
    print(f"Custom bounce(0.5) = {bounce_func(0.5)}")
    
    # Test 3: Compose functions
    composed = compose_rate_functions("linear", "there_and_back", weights=[0.5, 0.5])
    print(f"Composed function(0.5) = {composed(0.5)}")
    
    print("Bridge tests completed successfully!")


if __name__ == "__main__":
    # Test the bridge first
    test_rate_function_bridge()
    
    # Then run the scene
    print("\\nRunning animation scene...")
    from manim import config
    config.pixel_height = 720
    config.pixel_width = 1280
    config.frame_rate = 30
    
    scene = RateFunctionDemoScene()
    scene.render()