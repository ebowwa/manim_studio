#!/usr/bin/env python3
"""
Simple test for the new TextManager system
"""

from manim import *
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.manim_config import config
from core.text_manager import TextManager


class TextManagerTest(Scene):
    """Simple test of text manager features"""
    
    def construct(self):
        # Initialize text manager
        text_manager = TextManager(self)
        
        # Test basic text creation
        text_manager.add_text(
            "TextManager Test",
            style='title',
            layout='title',
            key='main_title',
            animation=Write
        )
        
        self.wait(1)
        
        # Test text update
        text_manager.update_text(
            'main_title',
            "Text System Fixed!",
            animation=Transform
        )
        
        self.wait(1)
        
        # Test different positions
        positions = [
            ("Top Left", 'body', 'center'),
            ("Center", 'heading', 'center'),
            ("Bottom Right", 'caption', 'center')
        ]
        
        for i, (text, style, layout) in enumerate(positions):
            text_manager.add_text(
                text,
                style=style,
                layout=layout,
                key=f'test_{i}',
                animation=FadeIn
            )
            self.wait(0.5)
        
        self.wait(2)
        
        # Clean up
        text_manager.clear_all_text(animation=FadeOut)
        self.wait(1)


if __name__ == "__main__":
    # Render the test
    from manim import config
    
    config.pixel_height = 720
    config.pixel_width = 1280
    config.frame_rate = 30
    config.media_dir = "user-data"
    
    scene = TextManagerTest()
    scene.render()