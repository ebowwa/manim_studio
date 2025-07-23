from manim import *

class TestScene(Scene):
    def construct(self):
        # Create a simple text
        text = Text("HELLO WORLD", font_size=72, color=WHITE)
        
        # Add to scene
        self.add(text)
        
        # Play animation
        self.play(Write(text))
        self.wait(2)

if __name__ == "__main__":
    import os
    os.system('manim --media_dir user-data -pql test_direct.py TestScene')