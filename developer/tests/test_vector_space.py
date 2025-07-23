"""
Comprehensive tests for the Vector Space system.
"""

from src.config.manim_config import config
import pytest
import numpy as np
from manim import *
from src.core.vector_space import (
    VectorSpace, CoordinateSystem, ViewportConfig, 
    TransformContext, get_vector_space, set_vector_space
)
from src.core.vector_space_extensions import (
    CoordinateFrame, SphericalCoordinates, CylindricalCoordinates,
    BarycentricCoordinates, PolarCoordinates, VectorFieldSpace
)
from src.core.viewport_manager import (
    ViewportManager, ViewportMode, Viewport, Frustum
)
from src.core.transform_pipeline import (
    TransformPipeline, TransformStage, TransformNode, TransformController
)
from src.utils.math3d import Vector3D, Matrix4x4


class TestVectorSpace:
    """Test core VectorSpace functionality."""
    
    def test_initialization(self):
        """Test VectorSpace initialization."""
        vs = VectorSpace()
        assert vs.viewport is not None
        assert vs.viewport.width == 1920
        assert vs.viewport.height == 1080
        assert vs.viewport.aspect_ratio == pytest.approx(1.777, rel=0.01)
    
    def test_custom_viewport(self):
        """Test VectorSpace with custom viewport."""
        viewport = ViewportConfig(width=1280, height=720, scene_width=16, scene_height=9)
        vs = VectorSpace(viewport)
        assert vs.viewport.width == 1280
        assert vs.viewport.height == 720
        assert vs.viewport.pixels_per_unit == 80  # 1280/16
    
    def test_coordinate_transformation(self):
        """Test point transformation between coordinate systems."""
        vs = VectorSpace()
        
        # Test identity transformation
        point = Vector3D(1, 2, 3)
        result = vs.transform_point(point, CoordinateSystem.WORLD, CoordinateSystem.WORLD)
        assert result == point
        
        # Test scene to screen transformation
        scene_point = Vector3D(0, 0, 0)  # Center of scene
        screen_point = vs.transform_point(scene_point, CoordinateSystem.SCENE, CoordinateSystem.SCREEN)
        assert screen_point.x == pytest.approx(960)  # Half of 1920
        assert screen_point.y == pytest.approx(540)  # Half of 1080
    
    def test_scene_bounds(self):
        """Test scene boundary calculations."""
        vs = VectorSpace()
        left, right, bottom, top = vs.get_scene_bounds()
        assert left == pytest.approx(-7.111, rel=0.01)
        assert right == pytest.approx(7.111, rel=0.01)
        assert bottom == -4.0
        assert top == 4.0
    
    def test_viewport_clamping(self):
        """Test point clamping to viewport."""
        vs = VectorSpace()
        
        # Test clamping in scene coordinates
        point = Vector3D(10, 10, 0)  # Outside bounds
        clamped = vs.clamp_to_viewport(point, CoordinateSystem.SCENE)
        assert clamped.x < 8  # Should be within scene bounds
        assert clamped.y < 4
    
    def test_camera_setup(self):
        """Test camera matrix setup."""
        vs = VectorSpace()
        
        eye = Vector3D(0, 0, 5)
        target = Vector3D(0, 0, 0)
        up = Vector3D(0, 1, 0)
        
        vs.set_camera(eye, target, up)
        
        # Verify view matrix is set
        assert vs.transform_context.view_matrix.determinant() != 0
    
    def test_projection_setup(self):
        """Test projection matrix setup."""
        vs = VectorSpace()
        
        # Test perspective projection
        vs.set_perspective_projection(np.radians(60), 0.1, 100)
        assert vs.transform_context.projection_matrix.matrix[3, 2] == -1  # Perspective flag
        
        # Test orthographic projection
        vs.set_orthographic_projection(10, 10, -10, 10)
        assert vs.transform_context.projection_matrix.matrix[3, 3] == 1  # Orthographic flag
    
    def test_pixel_scene_conversion(self):
        """Test conversion between pixel and scene coordinates."""
        vs = VectorSpace()
        
        # Test scene to pixel
        scene_point = Vector3D(1, 1, 0)
        x, y = vs.scene_to_pixel(scene_point)
        assert isinstance(x, int) and isinstance(y, int)
        
        # Test pixel to scene
        scene_back = vs.pixel_to_scene(x, y)
        assert scene_back.x == pytest.approx(1, rel=0.1)
        assert scene_back.y == pytest.approx(1, rel=0.1)
    
    def test_global_instance(self):
        """Test global vector space instance."""
        vs1 = get_vector_space()
        vs2 = get_vector_space()
        assert vs1 is vs2  # Should be same instance
        
        # Test setting new instance
        new_vs = VectorSpace()
        set_vector_space(new_vs)
        assert get_vector_space() is new_vs


class TestCoordinateSystemExtensions:
    """Test coordinate system extensions."""
    
    def test_coordinate_frame(self):
        """Test CoordinateFrame functionality."""
        frame = CoordinateFrame(
            origin=Vector3D(1, 0, 0),
            x_axis=Vector3D(0, 1, 0),
            y_axis=Vector3D(-1, 0, 0)
        )
        
        # Test orthonormalization
        assert frame.x_axis.dot(frame.y_axis) == pytest.approx(0)
        assert frame.x_axis.magnitude() == pytest.approx(1)
        
        # Test transformation
        local_point = Vector3D(1, 0, 0)
        world_point = frame.transform_to_world(local_point)
        assert world_point == Vector3D(1, 1, 0)
    
    def test_spherical_coordinates(self):
        """Test spherical coordinate conversions."""
        # Test conversion to spherical
        point = Vector3D(1, 0, 0)
        r, theta, phi = SphericalCoordinates.from_cartesian(point)
        assert r == pytest.approx(1)
        assert theta == pytest.approx(0)
        assert phi == pytest.approx(np.pi/2)
        
        # Test conversion back
        point_back = SphericalCoordinates.to_cartesian(r, theta, phi)
        assert point_back.x == pytest.approx(1)
        assert point_back.y == pytest.approx(0)
        assert point_back.z == pytest.approx(0)
    
    def test_cylindrical_coordinates(self):
        """Test cylindrical coordinate conversions."""
        point = Vector3D(1, 1, 2)
        r, theta, z = CylindricalCoordinates.from_cartesian(point)
        assert r == pytest.approx(np.sqrt(2))
        assert theta == pytest.approx(np.pi/4)
        assert z == 2
        
        point_back = CylindricalCoordinates.to_cartesian(r, theta, z)
        assert point_back.x == pytest.approx(1)
        assert point_back.y == pytest.approx(1)
        assert point_back.z == pytest.approx(2)
    
    def test_barycentric_coordinates(self):
        """Test barycentric coordinate conversions."""
        # Triangle vertices
        v0 = Vector3D(0, 0, 0)
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        
        # Point at centroid
        point = Vector3D(1/3, 1/3, 0)
        u, v, w = BarycentricCoordinates.from_cartesian(point, v0, v1, v2)
        assert u == pytest.approx(1/3)
        assert v == pytest.approx(1/3)
        assert w == pytest.approx(1/3)
        assert u + v + w == pytest.approx(1)
    
    def test_polar_coordinates(self):
        """Test 2D polar coordinate conversions."""
        x, y = 1, 1
        r, theta = PolarCoordinates.from_cartesian(x, y)
        assert r == pytest.approx(np.sqrt(2))
        assert theta == pytest.approx(np.pi/4)
        
        x_back, y_back = PolarCoordinates.to_cartesian(r, theta)
        assert x_back == pytest.approx(1)
        assert y_back == pytest.approx(1)


class TestViewportManager:
    """Test ViewportManager functionality."""
    
    def test_viewport_creation(self):
        """Test viewport creation and management."""
        vs = VectorSpace()
        vm = ViewportManager(vs)
        
        # Test default viewport
        assert "main" in vm.viewports
        assert vm.active_viewport == "main"
        
        # Test creating new viewport
        vp = vm.create_viewport("test", 100, 100, 200, 200)
        assert vp.name == "test"
        assert vp.contains_point(150, 150)
        assert not vp.contains_point(50, 50)
    
    def test_viewport_modes(self):
        """Test different viewport layout modes."""
        vs = VectorSpace()
        vm = ViewportManager(vs, 1920, 1080)
        
        # Test split horizontal
        vm.set_mode(ViewportMode.SPLIT_HORIZONTAL)
        assert "left" in vm.viewports
        assert "right" in vm.viewports
        assert vm.viewports["left"].width == 960
        
        # Test quad mode
        vm.set_mode(ViewportMode.QUAD)
        assert len([name for name in vm.viewports if "top" in name or "bottom" in name]) >= 4
    
    def test_frustum_culling(self):
        """Test frustum construction and culling."""
        vs = VectorSpace()
        vm = ViewportManager(vs)
        
        # Setup camera
        vm.setup_viewport_camera("main", Vector3D(0, 0, 5), Vector3D(0, 0, 0))
        
        frustum = vm.get_frustum("main")
        assert frustum is not None
        
        # Test point visibility
        assert frustum.contains_point(Vector3D(0, 0, 0))  # Center should be visible
        assert not frustum.contains_point(Vector3D(100, 0, 0))  # Far off to side


class TestTransformPipeline:
    """Test TransformPipeline functionality."""
    
    def test_node_hierarchy(self):
        """Test transform node hierarchy."""
        vs = VectorSpace()
        pipeline = TransformPipeline(vs)
        
        # Create parent-child hierarchy
        parent = pipeline.create_node("parent")
        child = pipeline.create_node("child", "parent")
        
        assert child.parent == parent
        assert child in parent.children
        
        # Test transform propagation
        parent.set_local_transform(Matrix4x4.translation(1, 0, 0))
        assert child.world_transform != child.local_transform
    
    def test_transform_stages(self):
        """Test transformation through pipeline stages."""
        vs = VectorSpace()
        pipeline = TransformPipeline(vs)
        
        node = pipeline.create_node("test")
        node.set_local_transform(Matrix4x4.translation(1, 2, 3))
        
        # Test getting transforms at different stages
        model_matrix = pipeline.get_transform_matrix("test", TransformStage.MODEL)
        world_matrix = pipeline.get_transform_matrix("test", TransformStage.WORLD)
        
        assert model_matrix == world_matrix  # No parent, so should be same
    
    def test_transform_caching(self):
        """Test transform matrix caching."""
        vs = VectorSpace()
        pipeline = TransformPipeline(vs)
        
        node = pipeline.create_node("test")
        
        # First access should miss cache
        initial_misses = pipeline.stats['cache_misses']
        pipeline.get_transform_matrix("test", TransformStage.WORLD)
        assert pipeline.stats['cache_misses'] == initial_misses + 1
        
        # Second access should hit cache
        initial_hits = pipeline.stats['cache_hits']
        pipeline.get_transform_matrix("test", TransformStage.WORLD)
        assert pipeline.stats['cache_hits'] == initial_hits + 1
    
    def test_mobject_integration(self):
        """Test integration with Manim Mobjects."""
        vs = VectorSpace()
        pipeline = TransformPipeline(vs)
        controller = TransformController(pipeline)
        
        # Create and register mobject
        circle = Circle()
        node_name = controller.register_mobject(circle)
        assert node_name in pipeline.nodes
        
        # Test transform update
        circle.shift(RIGHT * 2)
        controller.update_mobject_transform(circle)
        
        # Verify transform was updated
        transform = pipeline.get_transform_matrix(node_name, TransformStage.WORLD)
        position = transform.transform_point(Vector3D(0, 0, 0))
        assert position.x == pytest.approx(2)


def test_integration():
    """Test integration of all vector space components."""
    # Create complete vector space system
    viewport_config = ViewportConfig(width=1920, height=1080)
    vector_space = VectorSpace(viewport_config)
    
    # Setup camera
    vector_space.set_camera(
        Vector3D(5, 5, 5),
        Vector3D(0, 0, 0),
        Vector3D(0, 1, 0)
    )
    vector_space.set_perspective_projection(np.radians(60))
    
    # Create viewport manager
    viewport_manager = ViewportManager(vector_space)
    viewport_manager.set_mode(ViewportMode.SPLIT_HORIZONTAL)
    
    # Create transform pipeline
    pipeline = TransformPipeline(vector_space)
    controller = TransformController(pipeline)
    
    # Test complete transformation
    test_object = Dot()
    node_name = controller.register_mobject(test_object)
    
    # Transform point through entire pipeline
    local_point = Vector3D(0, 0, 0)
    screen_point = pipeline.transform_point(
        local_point, node_name,
        TransformStage.MODEL,
        TransformStage.VIEWPORT
    )
    
    # Verify we get valid screen coordinates
    assert 0 <= screen_point.x <= viewport_config.width
    assert 0 <= screen_point.y <= viewport_config.height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])