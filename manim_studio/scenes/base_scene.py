from manim import *
from ..components.base_components import StudioText, StudioImage, StudioTransitions

class StudioScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = StudioText()
        self.image = StudioImage()
        self.transitions = StudioTransitions()
    
    def show_title_card(self, title_text, duration=2):
        title = self.text.create_title(title_text)
        self.play(Write(title))
        self.wait(duration)
        self.play(FadeOut(title))
    
    def show_image_with_caption(self, image_path, caption_text, scale=1.0, duration=3):
        image = self.image.load_image(image_path, scale=scale)
        caption = self.text.create_subtitle(caption_text).next_to(image, DOWN, buff=0.5)
        
        self.play(FadeIn(image), Write(caption))
        self.wait(duration)
        return image, caption
    
    def transition_scenes(self, out_mobjects, in_mobjects, style="fade"):
        if style == "fade":
            self.transitions.fade_transform(self, out_mobjects, in_mobjects)
        elif style == "slide":
            self.transitions.slide_transform(self, out_mobjects, in_mobjects)
