from manim import *
from ..components.base_components import StudioText, StudioImage, StudioTransitions

class StudioScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = StudioText()
        self.image = StudioImage()
        self.transitions = StudioTransitions()
    
    def show_title_card(self, title_text, duration=2):
        title_group = self.text.create_title(title_text)
        
        # Position at center and initially transparent
        title_group.move_to(ORIGIN)
        title_group.set_opacity(0)
        
        # Animate background and text separately for better effect
        background, title = title_group
        
        self.play(
            FadeIn(background, run_time=0.5),
            Write(title, run_time=1.5)
        )
        self.wait(duration)
        self.play(
            FadeOut(background, run_time=0.5),
            FadeOut(title, run_time=0.5)
        )
    
    def show_image_with_caption(self, image_path, caption_text, scale=1.0, duration=3, position=DOWN):
        # Load and position image
        image = self.image.load_image(image_path, scale=scale)
        image.move_to(ORIGIN)
        
        # Create and position caption
        caption_group = self.text.create_subtitle(caption_text)
        caption_group.next_to(image, position, buff=0.5)
        
        # Get caption components
        caption_bg, caption = caption_group
        
        # Animate elements with proper timing
        self.play(
            FadeIn(image, run_time=0.7),
            FadeIn(caption_bg, run_time=0.3),
            Write(caption, run_time=1.0)
        )
        
        self.wait(duration)
        return image, caption_group
    
    def transition_scenes(self, out_mobjects, in_mobjects, style="fade", duration=1.0):
        if style == "fade":
            self.transitions.fade_transform(
                self, out_mobjects, in_mobjects, 
                duration=duration
            )
        elif style == "slide":
            self.transitions.slide_transform(
                self, out_mobjects, in_mobjects,
                duration=duration
            )
