"""Timeline presets and templates for common animation patterns."""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .composer_timeline import (
    ComposerTimeline, TimelineTrack, TrackType, 
    InterpolationType, Keyframe
)
from .easing import EasingPresets as EasingPresetLibrary

class PresetCategory(Enum):
    """Categories of timeline presets."""
    INTRO = "intro"
    OUTRO = "outro"
    TRANSITION = "transition"
    TITLE = "title"
    DATA_VIZ = "data_visualization"
    MOTION_GRAPHICS = "motion_graphics"
    EDUCATIONAL = "educational"
    SOCIAL_MEDIA = "social_media"

@dataclass
class TimelinePreset:
    """A reusable timeline preset."""
    name: str
    category: PresetCategory
    description: str
    duration: float
    parameters: Dict[str, Any]
    setup_function: Callable[[ComposerTimeline, Dict[str, Any]], None]
    tags: List[str] = None
    preview_image: Optional[str] = None
    
    def apply(self, timeline: ComposerTimeline, params: Dict[str, Any] = None):
        """Apply this preset to a timeline."""
        # Merge default parameters with provided ones
        final_params = self.parameters.copy()
        if params:
            final_params.update(params)
        
        # Call setup function
        self.setup_function(timeline, final_params)

class TimelinePresets:
    """Collection of timeline presets and templates."""
    
    def __init__(self):
        self.presets: Dict[str, TimelinePreset] = {}
        self._register_default_presets()
    
    def _register_default_presets(self):
        """Register built-in presets."""
        
        # Fade In/Out Preset
        self.register_preset(TimelinePreset(
            name="fade_in_out",
            category=PresetCategory.INTRO,
            description="Simple fade in and fade out",
            duration=3.0,
            parameters={
                "fade_in_duration": 1.0,
                "hold_duration": 1.0,
                "fade_out_duration": 1.0,
                "target_objects": ["*"]  # All objects
            },
            setup_function=self._setup_fade_in_out,
            tags=["simple", "basic", "fade"]
        ))
        
        # Title Sequence Preset
        self.register_preset(TimelinePreset(
            name="title_sequence",
            category=PresetCategory.TITLE,
            description="Animated title with subtitle",
            duration=5.0,
            parameters={
                "title_text": "Your Title Here",
                "subtitle_text": "Subtitle",
                "title_color": "#FFFFFF",
                "subtitle_color": "#CCCCCC",
                "background_effect": "particles"
            },
            setup_function=self._setup_title_sequence,
            tags=["title", "intro", "text"]
        ))
        
        # Data Reveal Preset
        self.register_preset(TimelinePreset(
            name="data_reveal",
            category=PresetCategory.DATA_VIZ,
            description="Progressive data visualization reveal",
            duration=8.0,
            parameters={
                "chart_type": "bar",
                "reveal_style": "sequential",
                "data_points": 5,
                "show_labels": True,
                "animate_values": True
            },
            setup_function=self._setup_data_reveal,
            tags=["data", "chart", "visualization"]
        ))
        
        # Kinetic Typography Preset
        self.register_preset(TimelinePreset(
            name="kinetic_typography",
            category=PresetCategory.MOTION_GRAPHICS,
            description="Dynamic text animation",
            duration=6.0,
            parameters={
                "text_lines": ["Line 1", "Line 2", "Line 3"],
                "animation_style": "bounce",
                "stagger_delay": 0.2,
                "color_scheme": "gradient"
            },
            setup_function=self._setup_kinetic_typography,
            tags=["text", "motion", "typography"]
        ))
        
        # Educational Diagram Preset
        self.register_preset(TimelinePreset(
            name="educational_diagram",
            category=PresetCategory.EDUCATIONAL,
            description="Step-by-step diagram explanation",
            duration=10.0,
            parameters={
                "steps": 4,
                "highlight_color": "#FFFF00",
                "explanation_position": "bottom",
                "show_arrows": True,
                "pause_between_steps": 1.5
            },
            setup_function=self._setup_educational_diagram,
            tags=["education", "tutorial", "diagram"]
        ))
        
        # Social Media Preset
        self.register_preset(TimelinePreset(
            name="social_media_post",
            category=PresetCategory.SOCIAL_MEDIA,
            description="Short-form social media animation",
            duration=15.0,
            parameters={
                "platform": "instagram",
                "aspect_ratio": "1:1",
                "loop": True,
                "captions": True,
                "branding_position": "bottom_right"
            },
            setup_function=self._setup_social_media,
            tags=["social", "short", "loop"]
        ))
        
        # Smooth Transition Preset
        self.register_preset(TimelinePreset(
            name="smooth_transition",
            category=PresetCategory.TRANSITION,
            description="Smooth scene transition",
            duration=2.0,
            parameters={
                "transition_type": "morph",
                "easing": "ease_in_out",
                "overlap": 0.5,
                "blur_amount": 0.3
            },
            setup_function=self._setup_smooth_transition,
            tags=["transition", "morph", "smooth"]
        ))
        
        # Logo Animation Preset
        self.register_preset(TimelinePreset(
            name="logo_animation",
            category=PresetCategory.INTRO,
            description="Professional logo reveal",
            duration=4.0,
            parameters={
                "reveal_style": "draw",
                "add_shine": True,
                "bounce_effect": False,
                "particle_burst": True,
                "hold_time": 1.0
            },
            setup_function=self._setup_logo_animation,
            tags=["logo", "brand", "professional"]
        ))
        
        # Material Design Animation Preset
        self.register_preset(TimelinePreset(
            name="material_design",
            category=PresetCategory.MOTION_GRAPHICS,
            description="Google Material Design style animations",
            duration=5.0,
            parameters={
                "element_count": 3,
                "stagger_delay": 0.1,
                "elevation_effect": True,
                "ripple_effect": True
            },
            setup_function=self._setup_material_design,
            tags=["material", "modern", "google"]
        ))
        
        # Elastic Pop Preset
        self.register_preset(TimelinePreset(
            name="elastic_pop",
            category=PresetCategory.MOTION_GRAPHICS,
            description="Fun elastic pop-in animation",
            duration=3.0,
            parameters={
                "overshoot": 1.5,
                "bounce_count": 2,
                "rotation_wiggle": True,
                "scale_pulse": True
            },
            setup_function=self._setup_elastic_pop,
            tags=["playful", "elastic", "bounce"]
        ))
        
        # Smooth Morph Preset
        self.register_preset(TimelinePreset(
            name="smooth_morph",
            category=PresetCategory.TRANSITION,
            description="Ultra-smooth morphing between shapes",
            duration=4.0,
            parameters={
                "morph_precision": "high",
                "intermediate_shapes": 3,
                "color_transition": True,
                "path_optimization": True
            },
            setup_function=self._setup_smooth_morph,
            tags=["morph", "smooth", "organic"]
        ))
    
    def register_preset(self, preset: TimelinePreset):
        """Register a new preset."""
        self.presets[preset.name] = preset
    
    def get_preset(self, name: str) -> Optional[TimelinePreset]:
        """Get a preset by name."""
        return self.presets.get(name)
    
    def get_presets_by_category(self, category: PresetCategory) -> List[TimelinePreset]:
        """Get all presets in a category."""
        return [p for p in self.presets.values() if p.category == category]
    
    def get_presets_by_tags(self, tags: List[str]) -> List[TimelinePreset]:
        """Get presets matching any of the given tags."""
        matching = []
        for preset in self.presets.values():
            if preset.tags and any(tag in preset.tags for tag in tags):
                matching.append(preset)
        return matching
    
    # Preset Setup Functions
    
    def _setup_fade_in_out(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup fade in/out animation."""
        fade_in_dur = params["fade_in_duration"]
        hold_dur = params["hold_duration"]
        fade_out_dur = params["fade_out_duration"]
        
        # Add keyframes for opacity
        main_layer = timeline.get_layer("Main")
        if main_layer:
            for track in main_layer.tracks:
                # Fade in
                track.add_keyframe("opacity", Keyframe(0, 0, InterpolationType.EASE_OUT))
                track.add_keyframe("opacity", Keyframe(fade_in_dur, 1, InterpolationType.LINEAR))
                
                # Hold
                track.add_keyframe("opacity", Keyframe(fade_in_dur + hold_dur, 1, InterpolationType.EASE_IN))
                
                # Fade out
                track.add_keyframe("opacity", Keyframe(
                    fade_in_dur + hold_dur + fade_out_dur, 0, InterpolationType.LINEAR
                ))
    
    def _setup_title_sequence(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup title sequence animation."""
        # Title track
        title_track = timeline.get_layer("Main").get_track("text")
        if title_track:
            # Title animation
            title_track.add_keyframe("position_y", Keyframe(0, 10, InterpolationType.EASE_OUT))
            title_track.add_keyframe("position_y", Keyframe(1, 0, InterpolationType.EASE_OUT))
            title_track.add_keyframe("scale", Keyframe(0, 0, InterpolationType.EASE_OUT))
            title_track.add_keyframe("scale", Keyframe(1, 1.2, InterpolationType.EASE_OUT))
            title_track.add_keyframe("scale", Keyframe(1.2, 1, InterpolationType.EASE_IN_OUT))
        
        # Background effect
        if params["background_effect"] == "particles":
            effects_track = timeline.get_layer("Effects").get_track("particles")
            if effects_track:
                effects_track.add_keyframe("emit_rate", Keyframe(0.5, 0, InterpolationType.LINEAR))
                effects_track.add_keyframe("emit_rate", Keyframe(1, 50, InterpolationType.EASE_OUT))
                effects_track.add_keyframe("emit_rate", Keyframe(4, 10, InterpolationType.LINEAR))
    
    def _setup_data_reveal(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup data visualization reveal."""
        num_points = params["data_points"]
        reveal_style = params["reveal_style"]
        
        main_track = timeline.get_layer("Main").get_track("objects")
        if not main_track:
            return
        
        if reveal_style == "sequential":
            # Reveal data points one by one
            for i in range(num_points):
                start_time = i * 1.0
                main_track.add_keyframe(f"data_{i}_scale_y", 
                    Keyframe(start_time, 0, InterpolationType.EASE_OUT))
                main_track.add_keyframe(f"data_{i}_scale_y", 
                    Keyframe(start_time + 0.8, 1, InterpolationType.EASE_OUT))
                
                if params["show_labels"]:
                    main_track.add_keyframe(f"label_{i}_opacity", 
                        Keyframe(start_time + 0.5, 0, InterpolationType.LINEAR))
                    main_track.add_keyframe(f"label_{i}_opacity", 
                        Keyframe(start_time + 1, 1, InterpolationType.LINEAR))
        
        elif reveal_style == "simultaneous":
            # Reveal all at once
            for i in range(num_points):
                main_track.add_keyframe(f"data_{i}_scale_y", 
                    Keyframe(0, 0, InterpolationType.EASE_OUT))
                main_track.add_keyframe(f"data_{i}_scale_y", 
                    Keyframe(1.5, 1, InterpolationType.EASE_OUT))
    
    def _setup_kinetic_typography(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup kinetic typography animation."""
        text_lines = params["text_lines"]
        style = params["animation_style"]
        stagger = params["stagger_delay"]
        
        text_track = timeline.get_layer("Main").get_track("text")
        if not text_track:
            return
        
        for i, line in enumerate(text_lines):
            start_time = i * stagger
            
            if style == "bounce":
                # Bounce in animation
                text_track.add_keyframe(f"line_{i}_position_y", 
                    Keyframe(start_time, -10, InterpolationType.EASE_OUT))
                text_track.add_keyframe(f"line_{i}_position_y", 
                    Keyframe(start_time + 0.5, 0, InterpolationType.SPRING,
                            spring_params={"stiffness": 200, "damping": 10}))
                text_track.add_keyframe(f"line_{i}_opacity", 
                    Keyframe(start_time, 0, InterpolationType.LINEAR))
                text_track.add_keyframe(f"line_{i}_opacity", 
                    Keyframe(start_time + 0.2, 1, InterpolationType.LINEAR))
            
            elif style == "typewriter":
                # Typewriter effect
                text_track.add_keyframe(f"line_{i}_reveal", 
                    Keyframe(start_time, 0, InterpolationType.LINEAR))
                text_track.add_keyframe(f"line_{i}_reveal", 
                    Keyframe(start_time + 1, 1, InterpolationType.LINEAR))
    
    def _setup_educational_diagram(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup educational diagram animation."""
        steps = params["steps"]
        pause = params["pause_between_steps"]
        
        diagram_track = timeline.get_layer("Main").get_track("shapes")
        if not diagram_track:
            return
        
        current_time = 0
        for i in range(steps):
            # Highlight current step
            diagram_track.add_keyframe(f"step_{i}_highlight", 
                Keyframe(current_time, 0, InterpolationType.EASE_IN_OUT))
            diagram_track.add_keyframe(f"step_{i}_highlight", 
                Keyframe(current_time + 0.3, 1, InterpolationType.EASE_IN_OUT))
            
            # Show explanation
            if params["explanation_position"]:
                diagram_track.add_keyframe(f"explanation_{i}_opacity", 
                    Keyframe(current_time + 0.2, 0, InterpolationType.LINEAR))
                diagram_track.add_keyframe(f"explanation_{i}_opacity", 
                    Keyframe(current_time + 0.5, 1, InterpolationType.LINEAR))
            
            # Show arrow to next step
            if params["show_arrows"] and i < steps - 1:
                diagram_track.add_keyframe(f"arrow_{i}_opacity", 
                    Keyframe(current_time + pause - 0.3, 0, InterpolationType.LINEAR))
                diagram_track.add_keyframe(f"arrow_{i}_opacity", 
                    Keyframe(current_time + pause, 1, InterpolationType.LINEAR))
            
            current_time += pause
    
    def _setup_social_media(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup social media animation."""
        platform = params["platform"]
        loop = params["loop"]
        
        # Quick, attention-grabbing intro
        main_track = timeline.get_layer("Main").get_track("objects")
        if main_track:
            main_track.add_keyframe("scale", Keyframe(0, 0.8, InterpolationType.EASE_OUT))
            main_track.add_keyframe("scale", Keyframe(0.2, 1.1, InterpolationType.EASE_OUT))
            main_track.add_keyframe("scale", Keyframe(0.3, 1, InterpolationType.EASE_IN_OUT))
        
        # Add captions
        if params["captions"]:
            subtitle_track = timeline.get_layer("Foreground").add_track(
                TimelineTrack("captions", TrackType.SUBTITLE)
            )
            # Caption timing would be set based on audio/narration
        
        # Loop setup
        if loop:
            # Add smooth transition at end to loop back
            main_track.add_keyframe("opacity", Keyframe(14.5, 1, InterpolationType.EASE_IN))
            main_track.add_keyframe("opacity", Keyframe(15, 0, InterpolationType.LINEAR))
    
    def _setup_smooth_transition(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup smooth transition between scenes."""
        transition_type = params["transition_type"]
        overlap = params["overlap"]
        
        # Assuming two scene layers
        scene1_track = timeline.get_layer("Main").get_track("objects")
        scene2_track = timeline.get_layer("Main").add_track(
            TimelineTrack("objects_2", TrackType.ANIMATION)
        )
        
        if transition_type == "morph":
            # Morph transition
            scene1_track.add_keyframe("morph_amount", 
                Keyframe(0, 0, InterpolationType.EASE_IN_OUT))
            scene1_track.add_keyframe("morph_amount", 
                Keyframe(2, 1, InterpolationType.EASE_IN_OUT))
            
            scene2_track.add_keyframe("opacity", 
                Keyframe(2 - overlap, 0, InterpolationType.EASE_IN_OUT))
            scene2_track.add_keyframe("opacity", 
                Keyframe(2, 1, InterpolationType.EASE_IN_OUT))
    
    def _setup_logo_animation(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup logo animation."""
        reveal_style = params["reveal_style"]
        
        logo_track = timeline.get_layer("Main").get_track("shapes")
        if not logo_track:
            return
        
        if reveal_style == "draw":
            # Draw-on effect
            logo_track.add_keyframe("stroke_progress", 
                Keyframe(0, 0, InterpolationType.EASE_IN_OUT))
            logo_track.add_keyframe("stroke_progress", 
                Keyframe(1.5, 1, InterpolationType.EASE_IN_OUT))
            logo_track.add_keyframe("fill_opacity", 
                Keyframe(1.2, 0, InterpolationType.EASE_OUT))
            logo_track.add_keyframe("fill_opacity", 
                Keyframe(2, 1, InterpolationType.EASE_OUT))
        
        # Add effects
        if params["add_shine"]:
            effects_track = timeline.get_layer("Effects").get_track("shaders")
            if effects_track:
                effects_track.add_keyframe("shine_position", 
                    Keyframe(2, -1, InterpolationType.LINEAR))
                effects_track.add_keyframe("shine_position", 
                    Keyframe(2.5, 1, InterpolationType.LINEAR))
        
        if params["particle_burst"]:
            particle_track = timeline.get_layer("Effects").get_track("particles")
            if particle_track:
                particle_track.add_keyframe("burst_amount", 
                    Keyframe(2, 0, InterpolationType.LINEAR))
                particle_track.add_keyframe("burst_amount", 
                    Keyframe(2.1, 100, InterpolationType.LINEAR))
                particle_track.add_keyframe("burst_amount", 
                    Keyframe(2.2, 0, InterpolationType.LINEAR))
    
    def _setup_material_design(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup Material Design style animation."""
        element_count = params["element_count"]
        stagger = params["stagger_delay"]
        
        main_track = timeline.get_layer("Main").get_track("objects")
        if not main_track:
            return
        
        for i in range(element_count):
            start_time = i * stagger
            
            # Use Material Design standard easing preset
            timeline.add_keyframe("Main", "objects", f"element_{i}_position_y",
                                start_time, -5, preset="MATERIAL_STANDARD")
            timeline.add_keyframe("Main", "objects", f"element_{i}_position_y",
                                start_time + 0.3, 0, preset="MATERIAL_STANDARD")
            
            # Opacity with decelerated easing
            timeline.add_keyframe("Main", "objects", f"element_{i}_opacity",
                                start_time, 0, preset="MATERIAL_DECELERATED")
            timeline.add_keyframe("Main", "objects", f"element_{i}_opacity",
                                start_time + 0.25, 1, preset="MATERIAL_DECELERATED")
            
            # Elevation effect
            if params["elevation_effect"]:
                timeline.add_keyframe("Main", "objects", f"element_{i}_shadow",
                                    start_time + 0.2, 0, preset="MATERIAL_STANDARD")
                timeline.add_keyframe("Main", "objects", f"element_{i}_shadow",
                                    start_time + 0.4, 4, preset="MATERIAL_STANDARD")
            
            # Ripple effect
            if params["ripple_effect"]:
                effects_track = timeline.get_layer("Effects").get_track("shaders")
                if effects_track:
                    timeline.add_keyframe("Effects", "shaders", f"ripple_{i}_radius",
                                        start_time + 0.3, 0, preset="MATERIAL_ACCELERATED")
                    timeline.add_keyframe("Effects", "shaders", f"ripple_{i}_radius",
                                        start_time + 0.6, 1, preset="MATERIAL_ACCELERATED")
                    timeline.add_keyframe("Effects", "shaders", f"ripple_{i}_opacity",
                                        start_time + 0.3, 0.3, InterpolationType.LINEAR)
                    timeline.add_keyframe("Effects", "shaders", f"ripple_{i}_opacity",
                                        start_time + 0.6, 0, InterpolationType.LINEAR)
    
    def _setup_elastic_pop(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup elastic pop animation."""
        main_track = timeline.get_layer("Main").get_track("objects")
        if not main_track:
            return
        
        # Scale with elastic easing
        timeline.add_keyframe("Main", "objects", "scale",
                            0, 0, InterpolationType.ELASTIC,
                            easing_params={"amplitude": params["overshoot"], "period": 0.4})
        timeline.add_keyframe("Main", "objects", "scale",
                            1.5, 1, InterpolationType.ELASTIC,
                            easing_params={"amplitude": params["overshoot"], "period": 0.4})
        
        # Rotation wiggle
        if params["rotation_wiggle"]:
            timeline.add_keyframe("Main", "objects", "rotation",
                                0, 0, InterpolationType.ELASTIC,
                                easing_params={"amplitude": 1.2, "period": 0.3})
            timeline.add_keyframe("Main", "objects", "rotation",
                                1.2, 15, InterpolationType.ELASTIC,
                                easing_params={"amplitude": 1.2, "period": 0.3})
            timeline.add_keyframe("Main", "objects", "rotation",
                                1.8, 0, InterpolationType.ELASTIC,
                                easing_params={"amplitude": 1.2, "period": 0.3})
        
        # Scale pulse
        if params["scale_pulse"]:
            for i in range(params["bounce_count"]):
                pulse_time = 2 + i * 0.3
                timeline.add_keyframe("Main", "objects", "scale",
                                    pulse_time, 1, InterpolationType.BOUNCE)
                timeline.add_keyframe("Main", "objects", "scale",
                                    pulse_time + 0.15, 1.1, InterpolationType.BOUNCE)
                timeline.add_keyframe("Main", "objects", "scale",
                                    pulse_time + 0.3, 1, InterpolationType.BOUNCE)
    
    def _setup_smooth_morph(self, timeline: ComposerTimeline, params: Dict[str, Any]):
        """Setup smooth morphing animation."""
        morph_track = timeline.get_layer("Main").get_track("shapes")
        if not morph_track:
            return
        
        # Use smoothest step for ultra-smooth morphing
        timeline.add_keyframe("Main", "shapes", "morph_progress",
                            0, 0, InterpolationType.SMOOTH_STEP)
        timeline.add_keyframe("Main", "shapes", "morph_progress",
                            3, 1, InterpolationType.SMOOTH_STEP)
        
        # Color transition with smooth interpolation
        if params["color_transition"]:
            timeline.add_keyframe("Main", "shapes", "color_blend",
                                0, 0, InterpolationType.SMOOTH_STEP)
            timeline.add_keyframe("Main", "shapes", "color_blend",
                                3, 1, InterpolationType.SMOOTH_STEP)
        
        # Intermediate shape keyframes for smoother morphing
        if params["intermediate_shapes"] > 0:
            for i in range(1, params["intermediate_shapes"] + 1):
                t = i / (params["intermediate_shapes"] + 1)
                time = t * 3
                timeline.add_keyframe("Main", "shapes", f"intermediate_{i}",
                                    time, t, InterpolationType.SMOOTH_STEP)
    
    def export_preset(self, preset_name: str, filepath: Path):
        """Export a preset to JSON file."""
        preset = self.get_preset(preset_name)
        if not preset:
            raise ValueError(f"Preset '{preset_name}' not found")
        
        data = {
            "name": preset.name,
            "category": preset.category.value,
            "description": preset.description,
            "duration": preset.duration,
            "parameters": preset.parameters,
            "tags": preset.tags or []
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_preset(self, filepath: Path, setup_function: Callable):
        """Import a preset from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        preset = TimelinePreset(
            name=data["name"],
            category=PresetCategory(data["category"]),
            description=data["description"],
            duration=data["duration"],
            parameters=data["parameters"],
            setup_function=setup_function,
            tags=data.get("tags", [])
        )
        
        self.register_preset(preset)
        return preset