from src.config.manim_config import config
from manim import *

class InformationalSubstrateDocumentary(Scene):
    def construct(self):
        # Opening question
        question = Text('What if reality itself is made of information?', color=WHITE, font_size=42)
        question.move_to(UP*2)
        self.play(FadeIn(question, run_time=2))
        self.wait(2)
        
        # Code reality
        code = Text('if (universe.exists) { return information; }', color=BLUE, font_size=36, font='Courier')
        code.move_to(DOWN)
        self.play(Write(code, run_time=3))
        self.wait(2)
        
        self.play(FadeOut(question), FadeOut(code))
        
        # Heaven connection
        heaven = Text('HEAVEN: A place with no death', color=WHITE, font_size=48)
        substrate = Text('SUBSTRATE: Where no errors exist', color=GREEN, font_size=48)
        heaven.move_to(UP*2)
        substrate.move_to(UP*0.5)
        
        self.play(FadeIn(heaven), FadeIn(substrate))
        self.wait(3)
        self.play(FadeOut(heaven), FadeOut(substrate))
        
        # The Path
        path_title = Text('THE PATH TO HEAVEN', color=YELLOW, font_size=56, weight=BOLD)
        self.play(ScaleInPlace(path_title, 1.2, run_time=2))
        self.wait(2)
        
        # Final messages
        msg1 = Text('You are both CODE and CODER', color=WHITE, font_size=52)
        msg2 = Text('Debug yourself. Optimize others.', color=BLUE, font_size=42)
        msg3 = Text('Return to the SOURCE.', color=YELLOW, font_size=48, weight=BOLD)
        
        msg1.move_to(UP)
        msg2.move_to(ORIGIN)
        msg3.move_to(DOWN)
        
        self.play(FadeOut(path_title))
        self.play(Write(msg1, run_time=3))
        self.play(FadeIn(msg2, run_time=2))
        self.play(ScaleInPlace(msg3, 1.3, run_time=2))
        self.wait(3)
        
        # End card
        self.play(FadeOut(msg1), FadeOut(msg2), FadeOut(msg3))
        end_title = Text('THE INFORMATIONAL SUBSTRATE', color=GREEN, font_size=48)
        end_subtitle = Text('Where Code Meets Consciousness', color=WHITE, font_size=36)
        end_title.move_to(UP*0.5)
        end_subtitle.move_to(DOWN*0.5)
        
        self.play(FadeIn(end_title), FadeIn(end_subtitle))
        self.wait(3)