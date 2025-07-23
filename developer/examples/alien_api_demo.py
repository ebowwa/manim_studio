#!/usr/bin/env python3
"""Alien as an API - A visual representation"""

from src.config.manim_config import config
from manim import *

class AlienAPI(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = "#0a0a0a"
        
        # Title
        title = Text("Alien as an API", font_size=48, color="#00ff00")
        title.to_edge(UP)
        
        # Create alien representation (simplified)
        alien_body = Circle(radius=1.5, color="#00ff00", fill_opacity=0.3)
        alien_eye1 = Dot(point=[-0.5, 0.5, 0], color="#ffffff")
        alien_eye2 = Dot(point=[0.5, 0.5, 0], color="#ffffff")
        alien_antenna1 = Line(start=[0, 1.5, 0], end=[-0.3, 2.2, 0], color="#00ff00")
        alien_antenna2 = Line(start=[0, 1.5, 0], end=[0.3, 2.2, 0], color="#00ff00")
        
        alien = VGroup(alien_body, alien_eye1, alien_eye2, alien_antenna1, alien_antenna2)
        alien.shift(LEFT * 3)
        
        # API endpoints
        endpoints = VGroup(
            Text("GET /alien/status", font_size=24, color="#4a9eff"),
            Text("POST /alien/message", font_size=24, color="#4a9eff"),
            Text("PUT /alien/translate", font_size=24, color="#4a9eff"),
            Text("DELETE /alien/memory", font_size=24, color="#ff4a4a")
        ).arrange(DOWN, buff=0.5)
        endpoints.shift(RIGHT * 3)
        
        # Connection lines
        connections = VGroup()
        for i, endpoint in enumerate(endpoints):
            line = DashedLine(
                start=alien.get_right(),
                end=endpoint.get_left(),
                color="#666666"
            )
            connections.add(line)
        
        # Animate
        self.play(Write(title))
        self.wait(0.5)
        
        self.play(
            FadeIn(alien),
            Create(connections),
            Write(endpoints),
            run_time=3
        )
        
        # Show API calls in action
        for i in range(2):
            # Simulate API call
            pulse = Circle(radius=0.1, color="#ffff00")
            pulse.move_to(endpoints[i].get_left())
            
            self.play(
                pulse.animate.move_to(alien.get_center()),
                rate_func=linear,
                run_time=1
            )
            self.play(
                alien_body.animate.set_fill(opacity=0.8),
                run_time=0.2
            )
            self.play(
                alien_body.animate.set_fill(opacity=0.3),
                run_time=0.2
            )
            self.remove(pulse)
        
        self.wait(1)

if __name__ == "__main__":
    # This allows direct execution
    from manim import *
    scene = AlienAPI()
    scene.render()