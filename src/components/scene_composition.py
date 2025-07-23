"""Advanced scene composition techniques from xiaoxiae's videos."""
from src.config.manim_config import config
from manim import *
from typing import List, Tuple, Optional, Callable, Dict, Any
import numpy as np
from src.utils.utilities import fade, staggered_animation_group


class AdvancedScene(Scene):
    """Enhanced Scene class with additional composition features."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sections: List[str] = []
        self.section_times: Dict[str, float] = {}
        self._section_start_time: Optional[float] = None
    
    def next_section(self, name: str, skip_animations: bool = False) -> None:
        """Start a new section with timing tracking."""
        # Record previous section time
        if self._section_start_time is not None and self.sections:
            elapsed = self.renderer.time - self._section_start_time
            self.section_times[self.sections[-1]] = elapsed
        
        # Start new section
        super().next_section(name, skip_animations)
        self.sections.append(name)
        self._section_start_time = self.renderer.time
    
    def fade_all_except(self, *keep_mobjects: Mobject) -> None:
        """Fade out all mobjects except specified ones."""
        to_fade = [mob for mob in self.mobjects if mob not in keep_mobjects]
        if to_fade:
            self.play(*[FadeOut(mob) for mob in to_fade])
    
    def introduce_text_sequence(
        self,
        texts: List[str],
        position: np.ndarray = ORIGIN,
        duration: float = 2.0,
        fade_previous: bool = True
    ) -> None:
        """Introduce a sequence of text with smooth transitions."""
        text_mobs = [Text(text) for text in texts]
        
        for i, text_mob in enumerate(text_mobs):
            text_mob.move_to(position)
            
            if i == 0:
                self.play(FadeIn(text_mob, shift=UP * 0.3))
            else:
                if fade_previous:
                    self.play(
                        FadeOut(text_mobs[i-1], shift=UP * 0.3),
                        FadeIn(text_mob, shift=UP * 0.3)
                    )
                else:
                    self.play(FadeIn(text_mob, shift=UP * 0.3))
            
            self.wait(duration)
        
        # Fade out last text
        if text_mobs:
            self.play(FadeOut(text_mobs[-1], shift=UP * 0.3))
    
    def create_title_card(
        self,
        title: str,
        subtitle: Optional[str] = None,
        authors: Optional[List[str]] = None,
        duration: float = 3.0
    ) -> None:
        """Create a professional title card using TextManager."""
        from ..core.text_manager import TextManager
        text_manager = TextManager(self)
        
        elements = VGroup()
        
        # Title
        title_text = text_manager.create_text(
            title,
            style='title',
            layout='center'
        )
        elements.add(title_text)
        
        # Subtitle
        if subtitle:
            subtitle_text = text_manager.create_text(
                subtitle,
                style='subtitle',
                layout='center'
            )
            subtitle_text.next_to(title_text, DOWN, buff=0.5)
            elements.add(subtitle_text)
        
        # Authors
        if authors:
            author_text = text_manager.create_text(
                ", ".join(authors),
                style='body',
                layout='center'
            )
            author_text.to_edge(DOWN).shift(UP * 0.5)
            elements.add(author_text)
        
        # Animate
        elements.move_to(ORIGIN)
        self.play(
            LaggedStart(
                *[FadeIn(elem, shift=UP * 0.2) for elem in elements],
                lag_ratio=0.3
            )
        )
        self.wait(duration)
        self.play(
            *[FadeOut(elem, shift=UP * 0.2) for elem in elements]
        )


class LayeredScene(AdvancedScene):
    """Scene with explicit layer management."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layers: Dict[str, VGroup] = {
            "background": VGroup(),
            "main": VGroup(),
            "foreground": VGroup(),
            "overlay": VGroup()
        }
        self.layer_z_indices = {
            "background": -10,
            "main": 0,
            "foreground": 10,
            "overlay": 100
        }
    
    def add_to_layer(self, mobject: Mobject, layer: str = "main") -> None:
        """Add mobject to specific layer."""
        if layer not in self.layers:
            raise ValueError(f"Unknown layer: {layer}")
        
        mobject.set_z_index(self.layer_z_indices[layer])
        self.layers[layer].add(mobject)
        self.add(mobject)
    
    def clear_layer(self, layer: str, animate: bool = True) -> None:
        """Clear all objects from a layer."""
        if layer not in self.layers:
            raise ValueError(f"Unknown layer: {layer}")
        
        if animate and self.layers[layer]:
            self.play(*[FadeOut(mob) for mob in self.layers[layer]])
        else:
            self.remove(*self.layers[layer])
        
        self.layers[layer] = VGroup()


class CameraController:
    """Advanced camera movement controller."""
    
    def __init__(self, scene: MovingCameraScene):
        self.scene = scene
        self.camera = scene.camera
        self.frame = scene.camera.frame
    
    def focus_on(
        self,
        mobject: Mobject,
        zoom: float = 1.2,
        shift: np.ndarray = ORIGIN,
        run_time: float = 1.5
    ) -> None:
        """Focus camera on a specific mobject."""
        target_center = mobject.get_center() + shift
        target_width = mobject.width * zoom
        target_height = mobject.height * zoom
        
        self.scene.play(
            self.frame.animate.move_to(target_center)
                .set_width(max(target_width, target_height)),
            run_time=run_time
        )
    
    def pan_between(
        self,
        mobjects: List[Mobject],
        zoom: float = 1.5,
        dwell_time: float = 1.0,
        transition_time: float = 1.0
    ) -> None:
        """Pan camera between multiple objects."""
        for mob in mobjects:
            self.focus_on(mob, zoom, run_time=transition_time)
            self.scene.wait(dwell_time)
    
    def reveal_scene(
        self,
        start_width: float = 2.0,
        end_width: float = 14.0,
        run_time: float = 3.0
    ) -> None:
        """Gradually reveal the full scene."""
        self.frame.set_width(start_width)
        self.scene.play(
            self.frame.animate.set_width(end_width),
            run_time=run_time
        )
    
    def create_focus_rect(
        self,
        mobject: Mobject,
        buff: float = 0.2,
        corner_radius: float = 0.1,
        stroke_color: str = YELLOW,
        stroke_width: float = 4
    ) -> RoundedRectangle:
        """Create a focus rectangle around an object."""
        rect = SurroundingRectangle(
            mobject,
            buff=buff,
            corner_radius=corner_radius,
            stroke_color=stroke_color,
            stroke_width=stroke_width
        )
        return rect


class TransitionLibrary:
    """Collection of reusable transition effects."""
    
    @staticmethod
    def cross_fade(
        scene: Scene,
        out_mobjects: List[Mobject],
        in_mobjects: List[Mobject],
        run_time: float = 1.0
    ) -> None:
        """Cross-fade between two sets of objects."""
        scene.play(
            *[FadeOut(mob) for mob in out_mobjects],
            *[FadeIn(mob) for mob in in_mobjects],
            run_time=run_time
        )
    
    @staticmethod
    def wipe_transition(
        scene: Scene,
        out_mobjects: List[Mobject],
        in_mobjects: List[Mobject],
        direction: np.ndarray = RIGHT,
        run_time: float = 1.5
    ) -> None:
        """Wipe transition effect."""
        # Create wipe rectangle
        wipe = Rectangle(
            width=config.frame_width * 2,
            height=config.frame_height,
            fill_opacity=1,
            stroke_width=0
        )
        
        # Position off-screen
        wipe.next_to(ORIGIN, -direction, buff=config.frame_width)
        
        # Animate wipe
        scene.play(
            wipe.animate.move_to(ORIGIN),
            *[mob.animate.shift(-direction * 2) for mob in out_mobjects],
            run_time=run_time/2
        )
        
        # Switch objects
        scene.remove(*out_mobjects)
        for mob in in_mobjects:
            mob.shift(direction * 2)
        scene.add(*in_mobjects)
        
        # Wipe out
        scene.play(
            wipe.animate.shift(direction * config.frame_width * 2),
            *[mob.animate.shift(-direction * 2) for mob in in_mobjects],
            run_time=run_time/2
        )
        scene.remove(wipe)
    
    @staticmethod
    def morph_transition(
        scene: Scene,
        start: Mobject,
        end: Mobject,
        path_arc: float = PI/4,
        run_time: float = 2.0
    ) -> None:
        """Morphing transition with arc path."""
        scene.play(
            Transform(
                start, end,
                path_arc=path_arc,
                run_time=run_time
            )
        )
    
    @staticmethod
    def zoom_transition(
        scene: MovingCameraScene,
        out_mobject: Mobject,
        in_mobject: Mobject,
        zoom_point: np.ndarray = ORIGIN,
        run_time: float = 2.0
    ) -> None:
        """Zoom in/out transition."""
        frame = scene.camera.frame
        
        # Zoom into point
        scene.play(
            frame.animate.move_to(zoom_point).set_width(0.1),
            FadeOut(out_mobject, scale=0.1),
            run_time=run_time/2
        )
        
        # Switch and zoom out
        scene.remove(out_mobject)
        in_mobject.scale(0.1).move_to(zoom_point)
        scene.add(in_mobject)
        
        scene.play(
            frame.animate.move_to(ORIGIN).set_width(config.frame_width),
            in_mobject.animate.scale(10).move_to(ORIGIN),
            run_time=run_time/2
        )


class SceneTemplate:
    """Base template for common scene patterns."""
    
    @staticmethod
    def algorithm_explanation(
        scene: AdvancedScene,
        title: str,
        algorithm_name: str,
        code: str,
        steps: List[str]
    ) -> None:
        """Template for algorithm explanation scenes."""
        # Title card
        scene.create_title_card(title, f"Understanding {algorithm_name}")
        
        # Show code
        from utils.utilities import myCode
        code_obj = myCode(code=code, language="python")
        code_obj.to_edge(LEFT)
        
        scene.play(FadeIn(code_obj))
        
        # Show steps
        step_list = VGroup(*[
            Text(f"{i+1}. {step}", font_size=32)
            for i, step in enumerate(steps)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        step_list.to_edge(RIGHT)
        
        for step in step_list:
            scene.play(Write(step))
            scene.wait(0.5)
    
    @staticmethod
    def comparison_scene(
        scene: AdvancedScene,
        title: str,
        item1: Tuple[str, Mobject],
        item2: Tuple[str, Mobject],
        comparison_points: List[Tuple[str, str, str]]  # (aspect, item1_value, item2_value)
    ) -> None:
        """Template for comparison scenes."""
        # Title
        title_text = Text(title, font_size=48).to_edge(UP)
        scene.play(FadeIn(title_text))
        
        # Items
        name1, mob1 = item1
        name2, mob2 = item2
        
        mob1.scale(0.8).move_to(LEFT * 3)
        mob2.scale(0.8).move_to(RIGHT * 3)
        
        label1 = Text(name1).next_to(mob1, UP)
        label2 = Text(name2).next_to(mob2, UP)
        
        scene.play(
            FadeIn(mob1, shift=UP * 0.2),
            FadeIn(mob2, shift=UP * 0.2),
            Write(label1),
            Write(label2)
        )
        
        # Comparison table
        table_data = [["Aspect", name1, name2]] + comparison_points
        table = Table(
            table_data,
            include_outer_lines=True
        ).scale(0.5).to_edge(DOWN)
        
        scene.play(Create(table))
        
        # Highlight differences
        for i, (aspect, val1, val2) in enumerate(comparison_points, 1):
            if val1 != val2:
                scene.play(
                    table.get_cell((i, 1)).animate.set_color(YELLOW),
                    table.get_cell((i, 2)).animate.set_color(YELLOW)
                )