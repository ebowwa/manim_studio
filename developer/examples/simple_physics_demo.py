"""Simple demonstration of physics components."""
from src.config.manim_config import config
from manim import *
from src.components.physics_objects import SimplePendulum, Spring, ProjectileMotion, create_physics_updater


class PhysicsShowcase(Scene):
    """Showcase all physics components."""
    
    def construct(self):
        # Title
        title = Text("Physics Components", font_size=48).to_edge(UP)
        self.play(Write(title))
        
        # Create physics objects
        pendulum = SimplePendulum(length=2, angle=PI/3, damping=0.998)
        pendulum.shift(LEFT * 4)
        
        spring = Spring(rest_length=2, spring_constant=5, mass=0.8)
        spring.shift(ORIGIN)
        spring.displacement = 1.0  # Initial stretch
        
        projectile = ProjectileMotion(initial_velocity=np.array([2, 4, 0]))
        projectile.shift(RIGHT * 3 + DOWN * 2)
        
        # Add labels
        pendulum_label = Text("Pendulum", font_size=24).next_to(pendulum, UP)
        spring_label = Text("Spring", font_size=24).next_to(spring, UP)
        projectile_label = Text("Projectile", font_size=24).move_to(RIGHT * 3 + UP * 2)
        
        # Add physics updaters
        pendulum.add_updater(create_physics_updater(pendulum))
        spring.add_updater(create_physics_updater(spring))
        projectile.add_updater(create_physics_updater(projectile))
        
        # Animate
        self.play(
            FadeIn(pendulum), FadeIn(pendulum_label),
            FadeIn(spring), FadeIn(spring_label),
            FadeIn(projectile), FadeIn(projectile_label),
            run_time=1
        )
        
        # Let physics run
        self.wait(8)
        
        # Clean up
        pendulum.clear_updaters()
        spring.clear_updaters()
        projectile.clear_updaters()
        
        self.play(FadeOut(*self.mobjects))


class InteractivePhysics(Scene):
    """Interactive physics demonstration."""
    
    def construct(self):
        # Create multiple pendulums with different properties
        pendulums = VGroup()
        
        for i, (length, color) in enumerate([(1.5, RED), (2.0, GREEN), (2.5, BLUE)]):
            p = SimplePendulum(
                length=length,
                angle=PI/4,
                damping=0.999,
                bob_radius=0.12
            )
            p.bob.set_color(color)
            p.shift(LEFT * 4 + RIGHT * i * 3)
            p.add_updater(create_physics_updater(p))
            pendulums.add(p)
        
        title = Text("Pendulum Length Comparison", font_size=36).to_edge(UP)
        
        self.add(title)
        self.play(FadeIn(pendulums), run_time=1)
        
        # Show different periods
        self.wait(10)
        
        # Clean up
        for p in pendulums:
            p.clear_updaters()
            
        self.play(FadeOut(*self.mobjects))


if __name__ == "__main__":
    # Run with: manim --media_dir user-data -pql developer/examples/simple_physics_demo.py PhysicsShowcase