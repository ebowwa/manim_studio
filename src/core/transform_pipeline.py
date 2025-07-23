"""
Transformation Pipeline Manager for Manim Studio

This module provides a comprehensive transformation pipeline that manages
the flow of coordinates through various transformation stages.
"""

from typing import List, Optional, Dict, Any, Callable, Tuple
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from manim import *
from .vector_space import VectorSpace, CoordinateSystem, Vector3D
from ..utils.math3d import Matrix4x4


class TransformStage(Enum):
    """Transformation pipeline stages."""
    MODEL = "model"              # Object local space
    WORLD = "world"              # World space
    VIEW = "view"                # Camera/eye space
    PROJECTION = "projection"    # After projection
    CLIP = "clip"                # Normalized device coordinates
    VIEWPORT = "viewport"        # Screen space


@dataclass
class TransformNode:
    """Node in the transformation hierarchy."""
    name: str
    parent: Optional['TransformNode'] = None
    children: List['TransformNode'] = field(default_factory=list)
    local_transform: Matrix4x4 = field(default_factory=Matrix4x4.identity)
    world_transform: Matrix4x4 = field(default_factory=Matrix4x4.identity)
    
    def add_child(self, child: 'TransformNode'):
        """Add a child node."""
        child.parent = self
        self.children.append(child)
        child.update_world_transform()
    
    def remove_child(self, child: 'TransformNode'):
        """Remove a child node."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def update_world_transform(self):
        """Update world transform based on parent hierarchy."""
        if self.parent:
            self.world_transform = self.parent.world_transform * self.local_transform
        else:
            self.world_transform = self.local_transform
        
        # Update children
        for child in self.children:
            child.update_world_transform()
    
    def set_local_transform(self, transform: Matrix4x4):
        """Set local transform and update hierarchy."""
        self.local_transform = transform
        self.update_world_transform()


class TransformPipeline:
    """
    Manages the complete transformation pipeline from object space to screen space.
    Provides caching, debugging, and optimization features.
    """
    
    def __init__(self, vector_space: VectorSpace):
        self.vector_space = vector_space
        self.root_node = TransformNode("root")
        self.nodes: Dict[str, TransformNode] = {"root": self.root_node}
        self.transform_cache: Dict[Tuple[str, TransformStage], Matrix4x4] = {}
        self.debug_mode = False
        self.stats = {
            'transforms_computed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def create_node(self, name: str, parent_name: str = "root") -> TransformNode:
        """Create a new transform node in the hierarchy."""
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists")
        
        parent = self.nodes.get(parent_name)
        if not parent:
            raise ValueError(f"Parent node '{parent_name}' not found")
        
        node = TransformNode(name)
        parent.add_child(node)
        self.nodes[name] = node
        return node
    
    def get_node(self, name: str) -> Optional[TransformNode]:
        """Get a transform node by name."""
        return self.nodes.get(name)
    
    def remove_node(self, name: str):
        """Remove a node and its children from the hierarchy."""
        if name == "root":
            raise ValueError("Cannot remove root node")
        
        node = self.nodes.get(name)
        if not node:
            return
        
        # Remove from parent
        if node.parent:
            node.parent.remove_child(node)
        
        # Remove node and all children from registry
        def remove_recursive(n: TransformNode):
            if n.name in self.nodes:
                del self.nodes[n.name]
            for child in n.children:
                remove_recursive(child)
        
        remove_recursive(node)
        self._clear_cache()
    
    def set_node_transform(self, name: str, transform: Matrix4x4):
        """Set the local transform for a node."""
        node = self.nodes.get(name)
        if node:
            node.set_local_transform(transform)
            self._clear_cache()
    
    def get_transform_matrix(self, node_name: str, stage: TransformStage) -> Matrix4x4:
        """Get the transformation matrix for a node at a specific stage."""
        cache_key = (node_name, stage)
        
        # Check cache
        if cache_key in self.transform_cache:
            self.stats['cache_hits'] += 1
            return self.transform_cache[cache_key]
        
        self.stats['cache_misses'] += 1
        self.stats['transforms_computed'] += 1
        
        # Compute transform
        node = self.nodes.get(node_name)
        if not node:
            return Matrix4x4.identity()
        
        if stage == TransformStage.MODEL:
            matrix = node.local_transform
        elif stage == TransformStage.WORLD:
            matrix = node.world_transform
        elif stage == TransformStage.VIEW:
            matrix = self.vector_space.transform_context.view_matrix * node.world_transform
        elif stage == TransformStage.PROJECTION:
            view_matrix = self.vector_space.transform_context.view_matrix * node.world_transform
            matrix = self.vector_space.transform_context.projection_matrix * view_matrix
        elif stage == TransformStage.CLIP:
            mvp = self.get_transform_matrix(node_name, TransformStage.PROJECTION)
            matrix = mvp  # Already in clip space after projection
        elif stage == TransformStage.VIEWPORT:
            clip_matrix = self.get_transform_matrix(node_name, TransformStage.CLIP)
            matrix = self.vector_space.transform_context.viewport_matrix * clip_matrix
        else:
            matrix = Matrix4x4.identity()
        
        # Cache result
        self.transform_cache[cache_key] = matrix
        return matrix
    
    def transform_point(self, point: Vector3D, node_name: str, 
                       from_stage: TransformStage, to_stage: TransformStage) -> Vector3D:
        """Transform a point between pipeline stages for a specific node."""
        if from_stage == to_stage:
            return point
        
        # Get transformation matrices
        from_matrix = self.get_transform_matrix(node_name, from_stage)
        to_matrix = self.get_transform_matrix(node_name, to_stage)
        
        # Compute relative transformation
        if from_stage.value < to_stage.value:  # Forward transform
            transform = to_matrix * from_matrix.inverse()
        else:  # Inverse transform
            transform = from_matrix.inverse() * to_matrix
        
        return transform.transform_point(point)
    
    def transform_points_batch(self, points: List[Vector3D], node_name: str,
                             from_stage: TransformStage, to_stage: TransformStage) -> List[Vector3D]:
        """Efficiently transform multiple points."""
        if from_stage == to_stage:
            return points
        
        # Get transformation matrix once
        from_matrix = self.get_transform_matrix(node_name, from_stage)
        to_matrix = self.get_transform_matrix(node_name, to_stage)
        
        if from_stage.value < to_stage.value:
            transform = to_matrix * from_matrix.inverse()
        else:
            transform = from_matrix.inverse() * to_matrix
        
        # Use batch transformation
        return transform.transform_points(points)
    
    def _clear_cache(self):
        """Clear the transformation cache."""
        self.transform_cache.clear()
    
    def get_mvp_matrix(self, node_name: str) -> Matrix4x4:
        """Get the Model-View-Projection matrix for a node."""
        return self.get_transform_matrix(node_name, TransformStage.PROJECTION)
    
    def get_normal_matrix(self, node_name: str) -> Matrix4x4:
        """Get the normal transformation matrix (inverse transpose of model-view)."""
        mv_matrix = self.get_transform_matrix(node_name, TransformStage.VIEW)
        # Extract 3x3 portion and compute inverse transpose
        upper_left = mv_matrix.matrix[:3, :3]
        normal_matrix = np.linalg.inv(upper_left).T
        result = Matrix4x4()
        result.matrix[:3, :3] = normal_matrix
        return result
    
    def create_debug_visualization(self, node_name: str = None) -> VGroup:
        """Create visual representation of transformation pipeline."""
        viz = VGroup()
        
        # Show coordinate axes at different stages
        stages_to_show = [
            TransformStage.MODEL,
            TransformStage.WORLD,
            TransformStage.VIEW
        ]
        
        colors = {
            TransformStage.MODEL: RED,
            TransformStage.WORLD: GREEN,
            TransformStage.VIEW: BLUE
        }
        
        node_names = [node_name] if node_name else list(self.nodes.keys())
        
        for name in node_names:
            node = self.nodes.get(name)
            if not node:
                continue
            
            for stage in stages_to_show:
                matrix = self.get_transform_matrix(name, stage)
                
                # Extract position and orientation
                translation, rotation, scale = matrix.decompose()
                
                # Create coordinate axes
                axes = VGroup()
                for i, (direction, color) in enumerate([(RIGHT, RED), (UP, GREEN), (OUT, BLUE)]):
                    arrow = Arrow(
                        start=translation.array,
                        end=translation.array + direction * 0.5,
                        color=colors.get(stage, WHITE),
                        stroke_width=2
                    )
                    axes.add(arrow)
                
                # Add label
                label = Text(f"{name}:{stage.value}", font_size=12)
                label.next_to(translation.array, UP)
                axes.add(label)
                
                viz.add(axes)
        
        return viz
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline performance statistics."""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = self.stats['cache_hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'total_nodes': len(self.nodes),
            'transforms_computed': self.stats['transforms_computed'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{hit_rate:.2%}",
            'cache_size': len(self.transform_cache)
        }


class TransformController:
    """
    High-level controller for managing object transformations in scenes.
    Integrates with Manim's Mobject system.
    """
    
    def __init__(self, pipeline: TransformPipeline):
        self.pipeline = pipeline
        self.mobject_nodes: Dict[Mobject, str] = {}
        self.node_counter = 0
    
    def register_mobject(self, mobject: Mobject, parent: Optional[Mobject] = None) -> str:
        """Register a Mobject with the transform pipeline."""
        # Generate unique node name
        node_name = f"mobject_{self.node_counter}"
        self.node_counter += 1
        
        # Determine parent node
        parent_name = "root"
        if parent and parent in self.mobject_nodes:
            parent_name = self.mobject_nodes[parent]
        
        # Create transform node
        node = self.pipeline.create_node(node_name, parent_name)
        self.mobject_nodes[mobject] = node_name
        
        # Set initial transform from mobject
        self.update_mobject_transform(mobject)
        
        return node_name
    
    def unregister_mobject(self, mobject: Mobject):
        """Remove a Mobject from the transform pipeline."""
        if mobject in self.mobject_nodes:
            node_name = self.mobject_nodes[mobject]
            self.pipeline.remove_node(node_name)
            del self.mobject_nodes[mobject]
    
    def update_mobject_transform(self, mobject: Mobject):
        """Update transform node from Mobject's current state."""
        if mobject not in self.mobject_nodes:
            return
        
        node_name = self.mobject_nodes[mobject]
        
        # Extract transform from mobject
        position = mobject.get_center()
        scale = mobject.get_scale()
        
        # Build transformation matrix
        transform = Matrix4x4.translation(*position)
        
        # Apply scale if not uniform 1
        if not np.allclose(scale, 1.0):
            if isinstance(scale, (int, float)):
                transform = transform * Matrix4x4.uniform_scale(scale)
            else:
                transform = transform * Matrix4x4.scale(*scale)
        
        # Apply rotation if available
        if hasattr(mobject, 'get_rotation'):
            rotation = mobject.get_rotation()
            transform = transform * Matrix4x4.rotation_euler(*rotation)
        
        self.pipeline.set_node_transform(node_name, transform)
    
    def get_mobject_screen_position(self, mobject: Mobject) -> Optional[Tuple[int, int]]:
        """Get the screen position of a Mobject's center."""
        if mobject not in self.mobject_nodes:
            return None
        
        node_name = self.mobject_nodes[mobject]
        center = Vector3D(0, 0, 0)  # Local center
        
        # Transform to screen space
        screen_pos = self.pipeline.transform_point(
            center, node_name,
            TransformStage.MODEL,
            TransformStage.VIEWPORT
        )
        
        return (int(screen_pos.x), int(screen_pos.y))
    
    def create_transform_updater(self, mobject: Mobject) -> Callable:
        """Create an updater function that syncs Mobject with transform pipeline."""
        def updater(mob, dt):
            self.update_mobject_transform(mob)
        
        return updater