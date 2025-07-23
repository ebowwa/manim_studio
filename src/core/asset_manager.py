"""Asset management system for Manim Studio."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Union, List, Any

from manim import ImageMobject, SVGMobject, VGroup, Rectangle, Text, BLUE, WHITE
from manim import ThreeDVMobject, VectorizedPoint, Sphere
from .cache import get_cache

# 3D model loading dependencies (optional imports)
try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    
try:
    import pygltflib
    PYGLTFLIB_AVAILABLE = True
except ImportError:
    PYGLTFLIB_AVAILABLE = False


class AssetManager:
    """Manages assets like images, fonts, and other resources."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None, use_cache: bool = True):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.assets: Dict[str, Path] = {}
        self.use_cache = use_cache
        self.cache_manager = get_cache() if use_cache else None
        
        # Default asset directories
        self.asset_dirs = {
            'images': self.base_path / 'assets' / 'images',
            'fonts': self.base_path / 'assets' / 'fonts',
            'textures': self.base_path / 'assets' / 'textures',
            'videos': self.base_path / 'assets' / 'videos',
            'data': self.base_path / 'assets' / 'data',
            'models': self.base_path / 'assets' / 'models'
        }
        
        # Create directories if they don't exist
        for dir_path in self.asset_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def register_asset(self, name: str, path: Union[str, Path]) -> None:
        """Register an asset with a name."""
        asset_path = Path(path)
        if not asset_path.is_absolute():
            asset_path = self.base_path / asset_path
        
        if not asset_path.exists():
            raise FileNotFoundError(f"Asset not found: {asset_path}")
        
        self.assets[name] = asset_path
    
    def get_asset_path(self, name: str) -> Path:
        """Get the path to a registered asset."""
        if name not in self.assets:
            # Try to find in default directories
            for asset_type, dir_path in self.asset_dirs.items():
                possible_path = dir_path / name
                if possible_path.exists():
                    self.register_asset(name, possible_path)
                    return possible_path
            
            raise ValueError(f"Asset '{name}' not found")
        
        return self.assets[name]
    
    def load_image(self, name: str, scale: float = 1.0, cache: bool = True) -> ImageMobject:
        """Load an image asset."""
        if self.use_cache and cache and self.cache_manager:
            cache_key = self.cache_manager._generate_cache_key("image", name, scale)
            cached_image = self.cache_manager.get(cache_key)
            if cached_image:
                return cached_image.copy()
        
        path = self.get_asset_path(name)
        image = ImageMobject(str(path)).scale(scale)
        
        if self.use_cache and cache and self.cache_manager:
            self.cache_manager.set(cache_key, image.copy())
        
        return image
    
    def load_svg(self, name: str, scale: float = 1.0, cache: bool = True) -> SVGMobject:
        """Load an SVG asset."""
        if self.use_cache and cache and self.cache_manager:
            cache_key = self.cache_manager._generate_cache_key("svg", name, scale)
            cached_svg = self.cache_manager.get(cache_key)
            if cached_svg:
                return cached_svg.copy()
        
        path = self.get_asset_path(name)
        svg = SVGMobject(str(path)).scale(scale)
        
        if self.use_cache and cache and self.cache_manager:
            self.cache_manager.set(cache_key, svg.copy())
        
        return svg
    
    def load_data(self, name: str) -> Dict[str, Any]:
        """Load JSON data asset."""
        if self.use_cache and self.cache_manager:
            cache_key = self.cache_manager._generate_cache_key("data", name)
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data
        
        path = self.get_asset_path(name)
        
        with open(path, 'r') as f:
            if path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported data format: {path.suffix}")
        
        if self.use_cache and self.cache_manager:
            self.cache_manager.set(cache_key, data)
        
        return data
    
    def load_3d_model(
        self, 
        name: str, 
        scale: float = 1.0, 
        cache: bool = True,
        center: bool = True,
        **kwargs
    ) -> ThreeDVMobject:
        """Load a 3D model asset (GLB, OBJ, STL).
        
        Args:
            name: Asset name or filename
            scale: Scale factor for the model
            cache: Whether to use caching
            center: Whether to center the model at origin
            **kwargs: Additional parameters for model processing
            
        Returns:
            ThreeDVMobject containing the 3D model
        """
        if self.use_cache and cache and self.cache_manager:
            cache_key = self.cache_manager._generate_cache_key("3d_model", name, scale, center)
            cached_model = self.cache_manager.get(cache_key)
            if cached_model:
                return cached_model.copy()
        
        path = self.get_asset_path(name)
        
        # Determine file format and load accordingly
        suffix = path.suffix.lower()
        
        if suffix == '.stl':
            model = self._load_stl(path, scale, center, **kwargs)
        elif suffix == '.obj':
            model = self._load_obj(path, scale, center, **kwargs)
        elif suffix in ['.glb', '.gltf']:
            model = self._load_glb(path, scale, center, **kwargs)
        else:
            raise ValueError(f"Unsupported 3D model format: {suffix}")
        
        if self.use_cache and cache and self.cache_manager:
            self.cache_manager.set(cache_key, model.copy())
        
        return model
    
    def _load_stl(self, path: Path, scale: float = 1.0, center: bool = True, **kwargs) -> ThreeDVMobject:
        """Load STL file using trimesh."""
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for STL loading. Install with: pip install trimesh")
        
        # Load mesh with trimesh
        mesh = trimesh.load_mesh(str(path))
        
        # Convert to Manim ThreeDVMobject
        return self._trimesh_to_mobject(mesh, scale, center, **kwargs)
    
    def _load_obj(self, path: Path, scale: float = 1.0, center: bool = True, **kwargs) -> ThreeDVMobject:
        """Load OBJ file using trimesh."""
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for OBJ loading. Install with: pip install trimesh")
        
        # Load mesh with trimesh
        mesh = trimesh.load_mesh(str(path))
        
        # Convert to Manim ThreeDVMobject
        return self._trimesh_to_mobject(mesh, scale, center, **kwargs)
    
    def _load_glb(self, path: Path, scale: float = 1.0, center: bool = True, **kwargs) -> ThreeDVMobject:
        """Load GLB/GLTF file using pygltflib and trimesh."""
        if not TRIMESH_AVAILABLE:
            raise ImportError("trimesh is required for GLB loading. Install with: pip install trimesh")
        
        # Load mesh with trimesh (trimesh can handle GLB/GLTF)
        mesh = trimesh.load_mesh(str(path))
        
        # Convert to Manim ThreeDVMobject
        return self._trimesh_to_mobject(mesh, scale, center, **kwargs)
    
    def _trimesh_to_mobject(self, mesh, scale: float = 1.0, center: bool = True, **kwargs) -> ThreeDVMobject:
        """Convert trimesh object to Manim ThreeDVMobject."""
        import numpy as np
        
        # Handle multiple meshes (Scene object)
        if hasattr(mesh, 'geometry'):
            # It's a Scene, get the first mesh
            if len(mesh.geometry) == 0:
                # No geometry found, return placeholder
                return self._create_3d_placeholder("No geometry in model")
            
            # Get first mesh
            mesh = list(mesh.geometry.values())[0]
        
        # Ensure we have vertices and faces
        if not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
            return self._create_3d_placeholder("Invalid mesh data")
        
        vertices = np.array(mesh.vertices)
        faces = np.array(mesh.faces) if hasattr(mesh, 'faces') and len(mesh.faces) > 0 else None
        
        if len(vertices) == 0:
            return self._create_3d_placeholder("Empty mesh")
        
        # Center the mesh if requested
        if center:
            centroid = vertices.mean(axis=0)
            vertices = vertices - centroid
        
        # Scale the mesh
        vertices = vertices * scale
        
        # Create ThreeDVMobject
        # For now, we'll create a simple point cloud representation
        # In a full implementation, you'd create proper mesh surfaces
        
        if faces is not None and len(faces) > 0:
            # Create a surface from the mesh
            return self._create_mesh_surface(vertices, faces, **kwargs)
        else:
            # Create point cloud
            return self._create_point_cloud(vertices, **kwargs)
    
    def _create_mesh_surface(self, vertices, faces, **kwargs):
        """Create a surface from mesh vertices and faces."""
        # This is a simplified implementation
        # In practice, you'd want to create proper Surface objects
        
        from manim import Surface, VGroup
        import numpy as np
        
        # For now, create a basic representation using the mesh bounds
        bounds = np.array([
            [vertices[:, 0].min(), vertices[:, 0].max()],
            [vertices[:, 1].min(), vertices[:, 1].max()],
            [vertices[:, 2].min(), vertices[:, 2].max()]
        ])
        
        # Create a simple surface approximation
        # This is a placeholder - real implementation would create proper mesh geometry
        def surface_func(u, v):
            # Simple interpolation between bounds
            x = bounds[0, 0] + u * (bounds[0, 1] - bounds[0, 0])
            y = bounds[1, 0] + v * (bounds[1, 1] - bounds[1, 0])
            z = bounds[2, 0] + 0.5 * (bounds[2, 1] - bounds[2, 0])  # Middle Z
            return np.array([x, y, z])
        
        surface = Surface(
            surface_func,
            u_range=[0, 1],
            v_range=[0, 1],
            **kwargs
        )
        
        return surface
    
    def _create_point_cloud(self, vertices, **kwargs):
        """Create a point cloud from vertices."""
        from manim import VGroup, Sphere
        import numpy as np
        
        # Create small spheres for each vertex
        points = VGroup()
        
        # Limit number of points for performance
        max_points = kwargs.get('max_points', 1000)
        if len(vertices) > max_points:
            # Sample vertices
            indices = np.random.choice(len(vertices), max_points, replace=False)
            vertices = vertices[indices]
        
        for vertex in vertices:
            point = Sphere(radius=0.02)
            point.move_to(vertex)
            points.add(point)
        
        return points
    
    def _create_3d_placeholder(self, message: str) -> ThreeDVMobject:
        """Create a 3D placeholder for failed model loading."""
        from manim import Cube, Text3D
        
        # Create a simple cube as placeholder
        cube = Cube(side_length=2, fill_opacity=0.3, color=BLUE)
        
        # Add text if possible (Text3D might not be available in all Manim versions)
        try:
            text = Text3D(message[:20], height=0.3)
            text.next_to(cube, UP)
            placeholder = VGroup(cube, text)
        except:
            placeholder = cube
        
        return placeholder
    
    def create_placeholder(
        self,
        name: str,
        width: float = 6,
        height: float = 4,
        color: str = BLUE,
        text: Optional[str] = None
    ) -> VGroup:
        """Create a placeholder for missing assets."""
        rect = Rectangle(width=width, height=height, color=color)
        rect.set_fill(color, opacity=0.3)
        
        if text is None:
            text = f"Missing: {name}"
        
        label = Text(text, color=WHITE).scale(0.5)
        label.move_to(rect.get_center())
        
        return VGroup(rect, label)
    
    def scan_directory(self, directory: Union[str, Path], recursive: bool = True) -> None:
        """Scan a directory and register all assets found."""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {dir_path}")
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                # Use relative path as asset name
                rel_path = file_path.relative_to(dir_path)
                asset_name = str(rel_path)
                self.register_asset(asset_name, file_path)
    
    def clear_cache(self) -> None:
        """Clear the asset cache."""
        if self.use_cache and self.cache_manager:
            # Clear only asset-related cache entries
            stats = self.cache_manager.get_stats()
            for entry_key in list(self.cache_manager.metadata.get('entries', {}).keys()):
                if entry_key.startswith(('image_', 'svg_', 'data_', '3d_model_')):
                    self.cache_manager.delete(entry_key)
    
    def list_assets(self, asset_type: Optional[str] = None) -> List[str]:
        """List all registered assets."""
        if asset_type and asset_type in self.asset_dirs:
            # List assets in specific directory
            dir_path = self.asset_dirs[asset_type]
            return [f.name for f in dir_path.iterdir() if f.is_file()]
        
        return list(self.assets.keys())
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'AssetManager':
        """Create AssetManager from configuration."""
        base_path = config.get('base_path', '.')
        manager = cls(base_path)
        
        # Register configured assets
        for name, path in config.get('assets', {}).items():
            manager.register_asset(name, path)
        
        # Scan configured directories
        for dir_config in config.get('scan_dirs', []):
            if isinstance(dir_config, str):
                manager.scan_directory(dir_config)
            else:
                manager.scan_directory(
                    dir_config['path'],
                    dir_config.get('recursive', True)
                )
        
        return manager