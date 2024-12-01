from manim import *
import os

class StudioText:
    @staticmethod
    def create_title(text, scale=1.5):
        return Tex(text).scale(scale)
    
    @staticmethod
    def create_subtitle(text, scale=1.0):
        return Tex(text).scale(scale)

class StudioImage:
    @staticmethod
    def load_image(image_path, scale=1.0):
        if not os.path.exists(image_path):
            # Create a placeholder rectangle if image doesn't exist
            return Rectangle(height=4, width=6, color=BLUE).scale(scale)
        return ImageMobject(image_path).scale(scale)

class StudioTransitions:
    @staticmethod
    def fade_transform(scene, out_mobjects, in_mobjects, duration=1):
        scene.play(
            *[FadeOut(mob) for mob in out_mobjects],
            *[FadeIn(mob) for mob in in_mobjects],
            run_time=duration
        )
    
    @staticmethod
    def slide_transform(scene, out_mobjects, in_mobjects, direction=LEFT):
        scene.play(
            *[mob.animate.shift(direction*10) for mob in out_mobjects],
            *[mob.animate.shift(-direction*10) for mob in in_mobjects]
        )
