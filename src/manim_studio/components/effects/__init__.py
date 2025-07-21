"""
Manim Studio Effects System

This package provides a comprehensive system for creating and managing
high-quality visual effects in Manim animations.
"""

from .base_effect import BaseEffect
from .effect_registry import EffectRegistry, register_effect
from .particle_system import ParticleSystem
from .magical_circle import MagicalCircle
from .text_effects import TextEffects
from .transitions import EffectTransitions

# Glow and lighting effects
from .glow_effects import (
    GlowEffect,
    NeonEffect,
    SpotlightEffect,
    LensFlareEffect
)

# Morphing effects
from .morph_effects import (
    MorphEffect,
    ShapeShifterEffect,
    LiquidMorphEffect,
    GeometricMorphEffect,
    ParticleMorphEffect
)

# Wave effects
from .wave_effects import (
    WaveEffect,
    RippleEffect,
    OceanWaveEffect,
    ShockwaveEffect,
    SoundWaveEffect
)

# Blur and focus effects
from .blur_effects import (
    BlurEffect,
    DepthOfFieldEffect,
    FocusPullEffect,
    ChromaticAberrationEffect,
    TiltShiftEffect,
    BokehEffect
)

# Skull effects
from .skull_effects import (
    SkullEffect,
    SkullParticleEffect,
    GhostlySkullEffect,
    SkullTransformEffect
)
from .skull_effects_v2 import ImprovedSkullEffect

__all__ = [
    'BaseEffect',
    'EffectRegistry',
    'register_effect',
    'ParticleSystem',
    'MagicalCircle',
    'TextEffects',
    'EffectTransitions',
    # Glow effects
    'GlowEffect',
    'NeonEffect',
    'SpotlightEffect',
    'LensFlareEffect',
    # Morph effects
    'MorphEffect',
    'ShapeShifterEffect',
    'LiquidMorphEffect',
    'GeometricMorphEffect',
    'ParticleMorphEffect',
    # Wave effects
    'WaveEffect',
    'RippleEffect',
    'OceanWaveEffect',
    'ShockwaveEffect',
    'SoundWaveEffect',
    # Blur effects
    'BlurEffect',
    'DepthOfFieldEffect',
    'FocusPullEffect',
    'ChromaticAberrationEffect',
    'TiltShiftEffect',
    'BokehEffect',
    # Skull effects
    'SkullEffect',
    'SkullParticleEffect',
    'GhostlySkullEffect',
    'SkullTransformEffect',
    'ImprovedSkullEffect',
]
