"""
Boundary-aware easing demo with proper dimension handling.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from manim import *
import numpy as np


# Easing functions from our math3d utilities
def smooth_step(t: float) -> float:
    """Smooth interpolation function (3t² - 2t³)."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def elastic_ease_out(t: float, amplitude: float = 1, period: float = 0.3) -> float:
    """Elastic easing out - overshoots then settles."""
    if t == 0:
        return 0
    if t == 1:
        return 1
    
    s = period / (2 * np.pi) * np.arcsin(1 / amplitude) if amplitude >= 1 else period / 4
    return amplitude * np.power(2, -10 * t) * np.sin((t - s) * 2 * np.pi / period) + 1


def bounce_ease_out(t: float) -> float:
    """Bounce easing out - bounces at the end."""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375


class BoundaryAwareEasingDemo(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Store frame dimensions
        self.frame_width = config.frame_width
        self.frame_height = config.frame_height
        self.safe_margin = 0.5  # Safety margin from edges
        
        # Calculate safe boundaries
        self.x_min = -self.frame_width / 2 + self.safe_margin
        self.x_max = self.frame_width / 2 - self.safe_margin
        self.y_min = -self.frame_height / 2 + self.safe_margin
        self.y_max = self.frame_height / 2 - self.safe_margin
        
        print(f"Frame dimensions: {self.frame_width}x{self.frame_height}")
        print(f"Safe area: X[{self.x_min:.1f}, {self.x_max:.1f}], Y[{self.y_min:.1f}, {self.y_max:.1f}]")
    
    def construct(self):
        # Show frame boundaries
        self.show_boundaries()
        
        # Title with proper positioning
        title = Text("Boundary-Aware Animations", font_size=36)
        title.move_to(UP * (self.y_max - 0.5))  # Position near top with margin
        
        self.play(Write(title))
        self.wait(1)
        
        # Demo different boundary-aware animations
        self.demo_horizontal_movement()
        self.demo_elastic_within_bounds()
        self.demo_particle_system()
        self.demo_wave_animation()
        
        self.play(FadeOut(title))
    
    def show_boundaries(self):
        """Visualize the safe boundaries."""
        # Create boundary rectangle
        boundary = Rectangle(
            width=self.x_max - self.x_min,
            height=self.y_max - self.y_min,
            stroke_color=GREY,
            stroke_width=1,
            stroke_opacity=0.3
        )
        boundary.move_to(ORIGIN)
        
        # Add corner markers
        corners = VGroup()
        for x, y in [(self.x_min, self.y_min), (self.x_max, self.y_min), 
                     (self.x_max, self.y_max), (self.x_min, self.y_max)]:
            corner = Cross(scale_factor=0.1, stroke_color=GREY, stroke_width=1)
            corner.move_to([x, y, 0])
            corners.add(corner)
        
        self.add(boundary, corners)
    
    def demo_horizontal_movement(self):
        """Demonstrate horizontal movement within bounds."""
        subtitle = Text("Horizontal Movement", font_size=24)
        subtitle.move_to(UP * (self.y_max - 1))
        self.play(Write(subtitle))
        
        # Create dots that will move horizontally
        dots = VGroup()
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE]
        
        for i, color in enumerate(colors):
            dot = Dot(radius=0.2, color=color)
            # Position dots vertically distributed
            y_pos = self.y_max - 2 - i * 0.8
            dot.move_to([self.x_min, y_pos, 0])
            dots.add(dot)
        
        self.play(*[FadeIn(dot) for dot in dots])
        
        # Move dots with different easings, staying within bounds
        animations = []
        easings = [linear, smooth_step, elastic_ease_out, bounce_ease_out, there_and_back_with_pause]
        
        for dot, easing in zip(dots, easings):
            # Calculate the movement distance to stay within bounds
            target_x = self.x_max - dot.get_width() / 2
            start_x = self.x_min + dot.get_width() / 2
            
            animations.append(
                dot.animate(rate_func=easing, run_time=3).move_to([target_x, dot.get_y(), 0])
            )
        
        self.play(*animations)
        self.wait(1)
        
        self.play(FadeOut(dots), FadeOut(subtitle))
    
    def demo_elastic_within_bounds(self):
        """Demonstrate elastic animations that respect boundaries."""
        subtitle = Text("Elastic Within Bounds", font_size=24)
        subtitle.move_to(UP * (self.y_max - 1))
        self.play(Write(subtitle))
        
        # Create squares that will scale elastically
        squares = VGroup()
        base_size = 0.8
        
        for i in range(3):
            square = Square(side_length=base_size, color=BLUE)
            x_pos = -2 + i * 2
            square.move_to([x_pos, 0, 0])
            squares.add(square)
        
        self.play(*[FadeIn(sq, scale=0) for sq in squares])
        
        # Scale with elastic, but ensure we don't exceed bounds
        for square in squares:
            # Calculate maximum scale that keeps square within bounds
            max_scale_x = (self.x_max - self.x_min) / base_size * 0.8
            max_scale_y = (self.y_max - self.y_min) / base_size * 0.8
            max_scale = min(max_scale_x, max_scale_y, 3)  # Cap at 3x for visual appeal
            
            # Create custom elastic that overshoots but stays in bounds
            def bounded_elastic(t):
                raw_value = elastic_ease_out(t, amplitude=1.5)
                # Scale the overshoot to stay within max_scale
                if raw_value > 1:
                    overshoot = raw_value - 1
                    return 1 + overshoot * (max_scale - 1)
                return raw_value
            
            self.play(
                square.animate(rate_func=bounded_elastic, run_time=1.5).scale(max_scale)
            )
            self.play(
                square.animate(rate_func=smooth_step, run_time=1).scale(1/max_scale)
            )
        
        self.play(FadeOut(squares), FadeOut(subtitle))
    
    def demo_particle_system(self):
        """Demonstrate a particle system that stays within bounds."""
        subtitle = Text("Bounded Particle System", font_size=24)
        subtitle.move_to(UP * (self.y_max - 1))
        self.play(Write(subtitle))
        
        # Create particles
        particles = VGroup()
        num_particles = 20
        
        for _ in range(num_particles):
            particle = Dot(
                radius=0.1,
                color=random_color(),
                fill_opacity=0.8
            )
            # Start from center
            particle.move_to(ORIGIN)
            particles.add(particle)
        
        self.play(*[FadeIn(p, scale=0) for p in particles])
        
        # Animate particles with boundary collision
        def particle_path(particle, angle, speed):
            def updater(mob, dt):
                # Get current position
                pos = mob.get_center()
                
                # Calculate new position
                new_x = pos[0] + speed * np.cos(angle) * dt
                new_y = pos[1] + speed * np.sin(angle) * dt
                
                # Check boundaries and bounce
                if new_x <= self.x_min + mob.get_width()/2 or new_x >= self.x_max - mob.get_width()/2:
                    angle = np.pi - angle  # Reflect horizontally
                    new_x = np.clip(new_x, self.x_min + mob.get_width()/2, self.x_max - mob.get_width()/2)
                
                if new_y <= self.y_min + mob.get_height()/2 or new_y >= self.y_max - mob.get_height()/2:
                    angle = -angle  # Reflect vertically
                    new_y = np.clip(new_y, self.y_min + mob.get_height()/2, self.y_max - mob.get_height()/2)
                
                mob.move_to([new_x, new_y, 0])
                return angle
            
            return updater
        
        # Add updaters to particles
        particle_data = []
        for i in range(num_particles):
            particle_data.append({
                'angle': np.random.uniform(0, 2*np.pi),
                'speed': np.random.uniform(2, 4)
            })
        
        def make_updater(particle_idx):
            def update(mob, dt):
                data = particle_data[particle_idx]
                pos = mob.get_center()
                angle = data['angle']
                speed = data['speed']
                
                # Calculate new position
                new_x = pos[0] + speed * np.cos(angle) * dt
                new_y = pos[1] + speed * np.sin(angle) * dt
                
                # Check boundaries and bounce
                if new_x <= self.x_min + mob.get_width()/2 or new_x >= self.x_max - mob.get_width()/2:
                    data['angle'] = np.pi - angle  # Reflect horizontally
                    new_x = np.clip(new_x, self.x_min + mob.get_width()/2, self.x_max - mob.get_width()/2)
                
                if new_y <= self.y_min + mob.get_height()/2 or new_y >= self.y_max - mob.get_height()/2:
                    data['angle'] = -angle  # Reflect vertically
                    new_y = np.clip(new_y, self.y_min + mob.get_height()/2, self.y_max - mob.get_height()/2)
                
                mob.move_to([new_x, new_y, 0])
            return update
        
        for i, particle in enumerate(particles):
            particle.add_updater(make_updater(i))
        
        self.wait(3)
        
        # Remove updaters and fade out
        for particle in particles:
            particle.clear_updaters()
        
        self.play(FadeOut(particles), FadeOut(subtitle))
    
    def demo_wave_animation(self):
        """Demonstrate wave animation within bounds."""
        subtitle = Text("Bounded Wave Animation", font_size=24)
        subtitle.move_to(UP * (self.y_max - 1))
        self.play(Write(subtitle))
        
        # Create wave that fits within bounds
        wave_width = self.x_max - self.x_min - 1
        wave_height = 1.5  # Maximum wave amplitude
        
        # Ensure wave stays within vertical bounds
        wave_center_y = 0
        if wave_center_y + wave_height > self.y_max - 1:
            wave_center_y = self.y_max - wave_height - 1
        if wave_center_y - wave_height < self.y_min + 1:
            wave_center_y = self.y_min + wave_height + 1
        
        # Create wave function
        def wave_func(x, t):
            return wave_center_y + wave_height * np.sin(2 * np.pi * (x / 2 - t))
        
        # Create initial wave
        wave = FunctionGraph(
            lambda x: wave_func(x, 0),
            x_range=[self.x_min + 0.5, self.x_max - 0.5],
            color=BLUE
        )
        
        self.play(Create(wave))
        
        # Animate wave
        def wave_updater(mob, dt):
            self.time = getattr(self, 'time', 0) + dt
            new_wave = FunctionGraph(
                lambda x: wave_func(x, self.time * 0.5),
                x_range=[self.x_min + 0.5, self.x_max - 0.5],
                color=BLUE
            )
            mob.become(new_wave)
        
        wave.add_updater(wave_updater)
        self.wait(3)
        wave.clear_updaters()
        
        self.play(FadeOut(wave), FadeOut(subtitle))


class DimensionAwareUI(Scene):
    """Example of UI elements that adapt to video dimensions."""
    
    def construct(self):
        # Get frame dimensions
        fw = config.frame_width
        fh = config.frame_height
        
        # Create adaptive UI layout
        header_height = 0.8
        footer_height = 0.6
        sidebar_width = 2
        margin = 0.3
        
        # Header
        header = Rectangle(
            width=fw - 2*margin,
            height=header_height,
            fill_color=BLUE_E,
            fill_opacity=0.8
        )
        header.to_edge(UP, buff=margin)
        
        header_text = Text("Adaptive UI Layout", font_size=24, color=WHITE)
        header_text.move_to(header.get_center())
        
        # Sidebar
        sidebar = Rectangle(
            width=sidebar_width,
            height=fh - header_height - footer_height - 3*margin,
            fill_color=GREEN_E,
            fill_opacity=0.8
        )
        sidebar.to_edge(LEFT, buff=margin)
        sidebar.shift(DOWN * (header_height/2 + margin))
        
        # Main content area
        content_width = fw - sidebar_width - 3*margin
        content_height = fh - header_height - footer_height - 3*margin
        
        content = Rectangle(
            width=content_width,
            height=content_height,
            fill_color=GREY_E,
            fill_opacity=0.5
        )
        content.next_to(sidebar, RIGHT, buff=margin)
        
        # Footer
        footer = Rectangle(
            width=fw - 2*margin,
            height=footer_height,
            fill_color=PURPLE_E,
            fill_opacity=0.8
        )
        footer.to_edge(DOWN, buff=margin)
        
        # Animate UI elements appearing
        self.play(
            FadeIn(header, shift=DOWN*0.3),
            Write(header_text)
        )
        self.play(
            FadeIn(sidebar, shift=RIGHT*0.3),
            FadeIn(content, scale=0.9),
            FadeIn(footer, shift=UP*0.3)
        )
        
        # Add some content
        content_text = Text(
            f"Frame: {fw:.1f}x{fh:.1f}\nContent: {content_width:.1f}x{content_height:.1f}",
            font_size=18
        )
        content_text.move_to(content.get_center())
        
        self.play(Write(content_text))
        self.wait(2)


if __name__ == "__main__":
    # Render with specific dimensions
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 60
    
    # Print configuration
    print(f"Rendering at {config.pixel_width}x{config.pixel_height} @ {config.frame_rate}fps")
    print(f"Frame dimensions: {config.frame_width}x{config.frame_height} units")
    
    # Render scenes
    scene1 = BoundaryAwareEasingDemo()
    scene1.render()
    
    scene2 = DimensionAwareUI()
    scene2.render()