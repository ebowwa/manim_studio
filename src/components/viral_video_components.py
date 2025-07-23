from src.config.manim_config import config
from manim import *
from typing import List, Tuple, Optional, Dict, Any
import random
from ..core.text_manager import TextManager, TextPosition
from ..core.layer_manager import LayerManager

class RapidTransition(AnimationGroup):
    """Quick cut-style transitions for viral video pacing"""
    
    def __init__(self, mobject: Mobject, transition_type: str = "glitch", **kwargs):
        self.transition_type = transition_type
        
        if transition_type == "glitch":
            animations = [
                Flash(mobject, color=random.choice([RED, BLUE, GREEN]), run_time=0.1),
                mobject.animate.shift(random.uniform(-0.5, 0.5) * RIGHT).set_opacity(0.5),
                mobject.animate.shift(random.uniform(-0.5, 0.5) * UP).set_opacity(1),
            ]
        elif transition_type == "zoom_cut":
            animations = [
                mobject.animate.scale(1.5).set_opacity(0),
                mobject.animate.scale(0.67).set_opacity(1),
            ]
        elif transition_type == "slide_cut":
            animations = [
                mobject.animate.shift(5 * RIGHT),
                mobject.animate.shift(10 * LEFT).set_opacity(0),
            ]
        else:  # "fade_cut"
            animations = [
                FadeOut(mobject, run_time=0.2),
                FadeIn(mobject, run_time=0.2),
            ]
        
        super().__init__(*animations, lag_ratio=0, run_time=0.3, **kwargs)


class ProductReveal(AnimationGroup):
    """Dramatic product reveal animation for merch drops"""
    
    def __init__(self, product: Mobject, website_text: Optional[Mobject] = None, **kwargs):
        animations = []
        
        # Main product entrance
        animations.append(
            Succession(
                product.animate.scale(0.1).set_opacity(0),
                GrowFromCenter(product, run_time=0.5),
                product.animate.scale(1.2),
                product.animate.scale(0.9),
                product.animate.scale(1.0),
                run_time=1.5
            )
        )
        
        # Add pulsing glow
        glow = Circle(radius=product.width * 0.6, color=YELLOW, fill_opacity=0.3)
        glow.move_to(product.get_center())
        animations.append(
            Succession(
                FadeIn(glow),
                glow.animate.scale(1.5).set_opacity(0),
                run_time=1.0
            )
        )
        
        # Website text slide-in if provided
        if website_text:
            animations.append(
                Succession(
                    Wait(0.5),
                    website_text.animate.shift(UP * 0.5).set_opacity(1),
                    run_time=1.0
                )
            )
        
        super().__init__(*animations, **kwargs)


class ViralTextEffect(VGroup):
    """Text with built-in viral video styling using TextManager"""
    
    def __init__(self, text: str, style: str = "impact", text_manager=None, **kwargs):
        super().__init__()
        self.layer_manager = LayerManager()
        
        # Use provided text_manager or create new one
        if text_manager is None:
            text_manager = TextManager(None)
        
        if style == "impact":
            # Classic impact font style using title style
            self.text = text_manager.create_text(
                text,
                style='title',
                custom_style={
                    'font': 'Arial Black',
                    'stroke_width': 4,
                    'stroke_color': BLACK,
                    'fill_color': WHITE,
                    **kwargs
                }
            )
        elif style == "gradient_pop":
            # Gradient with pop effect
            self.text = text_manager.create_text(
                text,
                style='title',
                custom_style=kwargs
            )
            self.text.set_color_by_gradient(BLUE, PURPLE, PINK)
        elif style == "authority":
            # Tech authority style
            self.text = text_manager.create_text(
                text,
                style='caption',
                custom_style={
                    'font': 'Courier New',
                    'slant': ITALIC,
                    'color': TEAL,
                    **kwargs
                }
            )
            # Add tech-looking box
            box = SurroundingRectangle(
                self.text,
                color=TEAL,
                stroke_width=2,
                buff=0.3,
                corner_radius=0.1
            )
            self.layer_manager.add_object(box, "effects")
            self.add(box)
        else:  # "cta" - Call to action
            self.text = text_manager.create_text(
                text,
                style='title',
                custom_style={
                    'font': 'Arial Black',
                    'color': GREEN,
                    **kwargs
                }
            )
            # Add urgency arrows
            arrow1 = Arrow(
                start=self.text.get_left() + LEFT,
                end=self.text.get_left(),
                color=GREEN
            )
            arrow2 = Arrow(
                start=self.text.get_right() + RIGHT,
                end=self.text.get_right(),
                color=GREEN
            )
            self.layer_manager.add_object(arrow1, "effects")
            self.layer_manager.add_object(arrow2, "effects")
            self.add(arrow1, arrow2)
        
        self.layer_manager.add_object(self.text, "text")
        self.add(self.text)


class MerchEndScreen(VGroup):
    """Complete merchandising end screen setup with proper text and layer management"""
    
    def __init__(
        self,
        product_name: str,
        website: str,
        tagline: str = "Link in Bio 👆",
        bg_color: str = "#1a1a1a",
        text_manager=None,
        **kwargs
    ):
        super().__init__()
        self.layer_manager = LayerManager()
        
        # Use provided text_manager or create new one
        if text_manager is None:
            text_manager = TextManager(None)
        
        # Background
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=bg_color,
            fill_opacity=1,
            stroke_width=0
        )
        self.layer_manager.add_object(bg, "background")
        self.add(bg)
        
        # Product name with gradient
        product_text = text_manager.create_text(
            product_name,
            style='title',
            layout='upper',
            custom_style={
                'font_size': 72,
                'font': 'Arial Black'
            }
        )
        product_text.set_color_by_gradient(RED, YELLOW, ORANGE)
        
        # Website URL
        website_text = text_manager.create_text(
            website,
            style='subtitle',
            layout='center',
            custom_style={
                'font_size': 48,
                'color': WHITE
            }
        )
        website_text.next_to(product_text, DOWN, buff=0.5)
        
        # CTA with pulsing effect
        cta_text = text_manager.create_text(
            tagline,
            style='title',
            layout='lower',
            custom_style={
                'font_size': 56,
                'color': GREEN,
                'font': 'Arial Black'
            }
        )
        cta_text.next_to(website_text, DOWN, buff=0.8)
        
        # Add decorative elements
        burst_lines = VGroup()
        for i in range(12):
            angle = i * TAU / 12
            line = Line(
                start=cta_text.get_center(),
                end=cta_text.get_center() + 2 * np.array([np.cos(angle), np.sin(angle), 0]),
                color=YELLOW,
                stroke_width=3
            )
            self.layer_manager.add_object(line, "effects")
            burst_lines.add(line)
        
        # Add all text to proper layers
        self.layer_manager.add_object(product_text, "text")
        self.layer_manager.add_object(website_text, "text")
        self.layer_manager.add_object(cta_text, "overlay")
        
        self.add(product_text, website_text, cta_text, burst_lines)
        self.product = product_text
        self.website = website_text
        self.cta = cta_text
        self.burst = burst_lines


class SceneTransitionFactory:
    """Factory for creating rapid scene transitions"""
    
    @staticmethod
    def create_transition(
        from_scene: VGroup,
        to_scene: VGroup,
        transition_type: str = "cut",
        run_time: float = 0.3
    ) -> AnimationGroup:
        """Create viral-style scene transitions"""
        
        if transition_type == "whip_pan":
            return AnimationGroup(
                from_scene.animate.shift(10 * LEFT).set_opacity(0),
                to_scene.animate.shift(10 * RIGHT).set_opacity(1),
                lag_ratio=0.1,
                run_time=run_time
            )
        elif transition_type == "zoom_transition":
            return AnimationGroup(
                from_scene.animate.scale(10).set_opacity(0),
                to_scene.animate.scale(0.1).set_opacity(1),
                lag_ratio=0,
                run_time=run_time
            )
        elif transition_type == "glitch":
            return AnimationGroup(
                Flash(from_scene, color=RED, run_time=0.1),
                from_scene.animate.set_opacity(0),
                Flash(to_scene, color=BLUE, run_time=0.1),
                to_scene.animate.set_opacity(1),
                lag_ratio=0,
                run_time=run_time
            )
        else:  # "cut"
            return AnimationGroup(
                FadeOut(from_scene, run_time=0.1),
                FadeIn(to_scene, run_time=0.1),
                lag_ratio=0,
                run_time=0.2
            )