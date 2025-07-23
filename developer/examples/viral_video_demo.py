from src.config.manim_config import config
from manim import *
from src.components.viral_video_components import (
    RapidTransition, ProductReveal, ViralTextEffect,
    MerchEndScreen, SceneTransitionFactory
)
from src.scenes.base_scene import StudioScene
from src.core.layer_manager import LayerManager

class ViralMerchDemo(StudioScene):
    """Demo of viral video to merch funnel format"""
    
    def construct(self):
        # Setup
        self.camera.background_color = "#0a0a0a"
        self.layer_manager = LayerManager()
        
        # Phase 1: Hook (0-5s)
        hook = ViralTextEffect(
            "What if NASA sold Tacos?",
            style="impact",
            text_manager=self.text_manager,
            font_size=64
        )
        hook.to_edge(UP, buff=1)
        
        self.play(Write(hook.text), run_time=1.5)
        self.wait(0.5)
        
        # Character introduction with rapid cuts
        character = Circle(radius=2, color=BLUE, fill_opacity=0.8)
        self.layer_manager.add_object(character, "main")
        
        character_name = ViralTextEffect(
            "Buzz Aldrin's Taco Truck",
            style="gradient_pop",
            text_manager=self.text_manager,
            font_size=42
        )
        character_name.next_to(character, DOWN, buff=0.5)
        
        # Rapid appearance
        self.play(
            RapidTransition(character, "zoom_cut"),
            Write(character_name.text, run_time=0.5)
        )
        self.wait(0.5)
        
        # Phase 2: Authority Drop (5-10s)
        tech_drop = ViralTextEffect(
            "SpaceX Technology™",
            style="authority",
            text_manager=self.text_manager,
            font_size=36
        )
        tech_drop.to_edge(RIGHT, buff=1)
        
        self.play(
            FadeIn(tech_drop, shift=LEFT),
            Flash(tech_drop, color=TEAL),
            run_time=0.5
        )
        self.wait(1)
        
        # Rapid scene changes
        scenes = VGroup(character, character_name, tech_drop)
        
        # Scene 2: Kitchen
        kitchen = Rectangle(width=6, height=4, color=ORANGE, fill_opacity=0.7)
        self.layer_manager.add_object(kitchen, "environment")
        
        kitchen_label = self.text_manager.create_text(
            "Zero-G Kitchen",
            style='subtitle',
            custom_style={'font_size': 36, 'color': WHITE}
        )
        kitchen_label.next_to(kitchen, UP)
        kitchen_scene = VGroup(kitchen, kitchen_label)
        
        self.play(
            SceneTransitionFactory.create_transition(
                scenes, kitchen_scene, "whip_pan", 0.3
            )
        )
        self.wait(1)
        
        # Scene 3: Product tease
        product_tease = Star(n=8, outer_radius=2, color=YELLOW, fill_opacity=0.9)
        self.layer_manager.add_object(product_tease, "main")
        
        tease_text = self.text_manager.create_text(
            "Revolutionary Space Tacos",
            style='subtitle',
            custom_style={'font_size': 32}
        )
        tease_text.next_to(product_tease, DOWN)
        tease_scene = VGroup(product_tease, tease_text)
        
        self.play(
            SceneTransitionFactory.create_transition(
                kitchen_scene, tease_scene, "zoom_transition", 0.3
            )
        )
        self.wait(1)
        
        # Phase 3: Product Reveal (20-29s)
        self.play(FadeOut(tease_scene, run_time=0.2))
        
        # Merch end screen
        merch_screen = MerchEndScreen(
            product_name="SPACE TACO TEE",
            website="spacetacos.store",
            tagline="Get Yours Now! 🚀",
            bg_color="#1a1a1a",
            text_manager=self.text_manager
        )
        
        # Dramatic product reveal
        self.play(
            ProductReveal(
                merch_screen.product,
                merch_screen.website,
                run_time=2
            )
        )
        
        # CTA entrance with urgency
        self.play(
            Write(merch_screen.cta, run_time=0.5),
            Create(merch_screen.burst, run_time=0.5),
        )
        
        # Pulsing CTA
        self.play(
            merch_screen.cta.animate.scale(1.1).set_color(YELLOW),
            rate_func=there_and_back,
            run_time=0.5
        )
        self.play(
            merch_screen.cta.animate.scale(1.1).set_color(GREEN),
            rate_func=there_and_back,
            run_time=0.5
        )
        
        # Keep pulsing
        for _ in range(3):
            self.play(
                merch_screen.burst.animate.rotate(PI/6),
                merch_screen.cta.animate.scale(1.05),
                rate_func=there_and_back,
                run_time=0.7
            )
        
        self.wait(1)


class IfXWasYExample(StudioScene):
    """Example using the 'If X was Y' formula"""
    
    def construct(self):
        self.camera.background_color = "#000000"
        self.layer_manager = LayerManager()
        
        # Opening hook
        hook = ViralTextEffect(
            "If Apple made Pizza",
            style="impact",
            text_manager=self.text_manager,
            font_size=72
        )
        hook.to_edge(UP, buff=1)
        
        self.play(Write(hook.text, run_time=1))
        
        # Quick cuts through absurd scenarios
        # Scenario 1: Minimalist pizza
        pizza = Circle(radius=2, color="#333333", fill_opacity=1)
        topping = Dot(color=WHITE).move_to(pizza.get_center())
        self.layer_manager.add_object(pizza, "main")
        self.layer_manager.add_object(topping, "main")
        pizza_group = VGroup(pizza, topping)
        
        label1 = self.text_manager.create_text(
            "iPizza Pro",
            style='subtitle',
            custom_style={'font_size': 36, 'color': WHITE}
        )
        label1.next_to(pizza_group, DOWN)
        
        self.play(
            FadeIn(pizza_group, scale=0.5),
            Write(label1, run_time=0.5)
        )
        self.wait(1)
        
        # Glitch transition
        self.play(RapidTransition(VGroup(pizza_group, label1), "glitch"))
        
        # Scenario 2: Genius Bar for pizza
        counter = Rectangle(width=8, height=2, color=GREY, fill_opacity=0.8)
        self.layer_manager.add_object(counter, "environment")
        
        genius = self.text_manager.create_text(
            "Pizza Genius Bar",
            style='title',
            custom_style={'font_size': 42, 'color': WHITE}
        )
        genius.next_to(counter, UP)
        
        scene2 = VGroup(counter, genius)
        self.play(FadeIn(scene2, shift=UP, run_time=0.3))
        self.wait(1)
        
        # Authority drop
        auth = ViralTextEffect(
            "Silicon Valley Tech™",
            style="authority",
            text_manager=self.text_manager,
            font_size=32
        )
        auth.to_corner(UR)
        self.play(FadeIn(auth, run_time=0.3))
        self.wait(0.5)
        
        # Clear for product
        self.play(
            FadeOut(VGroup(hook, scene2, auth), run_time=0.3)
        )
        
        # Product reveal
        product = ViralTextEffect(
            "iPIZZA MERCH",
            style="gradient_pop",
            text_manager=self.text_manager,
            font_size=84
        )
        product.shift(UP)
        
        website = self.text_manager.create_text(
            "ipizzastore.com",
            style='subtitle',
            custom_style={'font_size': 48, 'color': WHITE}
        )
        website.next_to(product, DOWN, buff=0.5)
        
        cta = ViralTextEffect(
            "Swipe Up Now! ☝️",
            style="cta",
            text_manager=self.text_manager,
            font_size=56
        )
        cta.next_to(website, DOWN, buff=1)
        
        self.play(
            ProductReveal(product, website, run_time=1.5)
        )
        self.play(FadeIn(cta, scale=0.8, run_time=0.3))
        
        # Final urgency
        for _ in range(4):
            self.play(
                cta.animate.scale(1.1).set_color(YELLOW),
                run_time=0.4,
                rate_func=there_and_back
            )
        
        self.wait(1)