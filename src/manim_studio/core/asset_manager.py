"""Asset management system for Manim Studio."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Union, List, Any

from manim import ImageMobject, SVGMobject, VGroup, Rectangle, Text, BLUE, WHITE


class AssetManager:
    """Manages assets like images, fonts, and other resources."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.assets: Dict[str, Path] = {}
        self.cache: Dict[str, Any] = {}
        
        # Default asset directories
        self.asset_dirs = {
            'images': self.base_path / 'assets' / 'images',
            'fonts': self.base_path / 'assets' / 'fonts',
            'textures': self.base_path / 'assets' / 'textures',
            'videos': self.base_path / 'assets' / 'videos',
            'data': self.base_path / 'assets' / 'data'
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
        cache_key = f"image_{name}_{scale}"
        
        if cache and cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        path = self.get_asset_path(name)
        image = ImageMobject(str(path)).scale(scale)
        
        if cache:
            self.cache[cache_key] = image.copy()
        
        return image
    
    def load_svg(self, name: str, scale: float = 1.0, cache: bool = True) -> SVGMobject:
        """Load an SVG asset."""
        cache_key = f"svg_{name}_{scale}"
        
        if cache and cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        path = self.get_asset_path(name)
        svg = SVGMobject(str(path)).scale(scale)
        
        if cache:
            self.cache[cache_key] = svg.copy()
        
        return svg
    
    def load_data(self, name: str) -> Dict[str, Any]:
        """Load JSON data asset."""
        cache_key = f"data_{name}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        path = self.get_asset_path(name)
        
        with open(path, 'r') as f:
            if path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported data format: {path.suffix}")
        
        self.cache[cache_key] = data
        return data
    
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
        self.cache.clear()
    
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