"""
Manim Studio Effects System

This package provides a comprehensive system for creating and managing
high-quality visual effects in Manim animations.
"""

from .base_effect import BaseEffect
from .particle_system import ParticleSystem
from .magical_circle import MagicalCircle
from .text_effects import TextEffects
from .transitions import EffectTransitions

__all__ = [
    'BaseEffect',
    'ParticleSystem',
    'MagicalCircle',
    'TextEffects',
    'EffectTransitions',
]
