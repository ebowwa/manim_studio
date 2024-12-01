from manim import *
from manim_studio.components.effects.text_effects import TextEffects

class SparkleTest(Scene):
    def construct(self):
        # Create text with sparkle effect
        text = TextEffects(
            "✨ Sparkle Magic ✨",
            animation_style="sparkle",
            sparkle_colors=[BLUE_A, PURPLE_A, PINK],
            font_size=48
        )
        
        # Play the animation
        text.animate_text(self)
        
        # Wait to see the effect
        self.wait(2)
