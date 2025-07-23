# 3D Asset Integration Guide

## Overview

Manim Studio now supports loading and rendering 3D model assets in GLB, OBJ, and STL formats. This integration builds on the existing 3D scene capabilities and provides a seamless workflow for incorporating external 3D models into your animations.

## Features

✅ **Multiple Format Support**: GLB, OBJ, STL files  
✅ **Intelligent Caching**: Automatic model caching for performance  
✅ **Material System**: Basic PBR material properties  
✅ **Transform Controls**: Position, rotation, scale  
✅ **Smart Placeholders**: Fallback rendering for missing/invalid models  
✅ **Configuration-Driven**: Full YAML configuration support  

## Installation

The 3D asset system requires additional dependencies:

```bash
pip install trimesh>=3.15.0 pygltflib>=1.15.0
```

These are automatically installed when you install/upgrade Manim Studio.

## Quick Start

### 1. Directory Structure

Place your 3D models in the assets directory:

```
assets/
└── models/
    ├── spaceship.glb
    ├── robot.obj
    └── terrain.stl
```

### 2. Configuration

Add 3D models to your scene configuration:

```yaml
# Use 3D camera for 3D model scenes
camera_type: "3d"
camera:
  phi: 1.0472      # 60 degrees
  theta: 0.7854    # 45 degrees  
  distance: 8.0

# Define 3D model objects
objects:
  my_spaceship:
    type: 3d_model
    asset: spaceship.glb
    params:
      scale: 2.0
      position: [0, 0, 0]
      rotation: [0, 0, 0.5236]  # 30 degree Z rotation
      material:
        color: "#4a90e2"
        opacity: 0.9
        metallic: 0.7
        roughness: 0.3
```

### 3. Rendering

Use the CLI to render your scene:

```bash
manim-studio configs/my_3d_scene.yaml
```

## Configuration Reference

### 3D Model Object Type

```yaml
objects:
  model_name:
    type: 3d_model
    asset: "model_file.glb"    # Required: filename in assets/models/
    layer: main                # Optional: layer name
    z_offset: 0               # Optional: layer depth offset
    params:
      # Transform parameters
      scale: 1.0              # Uniform scale factor
      position: [0, 0, 0]     # [x, y, z] position
      rotation: [0, 0, 0]     # [x, y, z] rotations in radians
      center: true            # Center model at origin
      
      # Performance parameters  
      max_points: 1000        # Max points for point cloud models
      
      # Material overrides
      material:
        color: "#ffffff"       # Base color
        opacity: 1.0          # Transparency (0-1)
        metallic: 0.0         # Metallic factor (0-1)
        roughness: 0.5        # Roughness factor (0-1)  
        emission: "#000000"   # Emission color
```

### Supported File Formats

| Format | Extension | Features |
|--------|-----------|----------|
| GLB | `.glb` | Full PBR materials, animations, textures |
| GLTF | `.gltf` | Full PBR materials, animations, textures |
| OBJ | `.obj` | Geometry, basic materials |
| STL | `.stl` | Geometry only |

### Camera Configuration for 3D Models

Use 3D camera type for proper model viewing:

```yaml
camera_type: "3d"
camera:
  phi: 1.0472        # Polar angle (0 to π)
  theta: 0.7854      # Azimuthal angle (0 to 2π)
  distance: 8.0      # Distance from focal point
  focal_point: [0, 0, 0]  # Look-at point
  fov: 50.0         # Field of view
  zoom: 1.0         # Additional zoom factor
```

## Advanced Usage

### Material System

The material system supports PBR (Physically Based Rendering) properties:

```yaml
material:
  color: "#4a90e2"     # Albedo/base color
  opacity: 0.9         # Alpha transparency
  metallic: 0.8        # Metallic workflow (0=dielectric, 1=metallic)
  roughness: 0.2       # Surface roughness (0=mirror, 1=rough)
  emission: "#ffffff"  # Emissive color for glowing effects
```

### Performance Optimization

For complex models, use these parameters:

```yaml
params:
  max_points: 1500     # Limit point cloud density
  center: true         # Pre-center for better performance
  cache: true          # Enable caching (default)
```

### Animation Support

3D models work with all standard Manim animations:

```yaml
animations:
  - target: my_model
    animation_type: rotate
    start_time: 2.0
    duration: 4.0
    params:
      angle: 6.283185    # 2π radians (full rotation)
      axis: [0, 0, 1]    # Z-axis rotation

  - target: my_model
    animation_type: move
    start_time: 6.0
    duration: 2.0
    params:
      to: [2, 0, 1]      # New position
```

## Troubleshooting

### Common Issues

**Model not loading:**
- Check file path: `assets/models/your_model.glb`
- Verify file format is supported
- Check file integrity with a 3D viewer

**Performance issues:**
- Reduce `max_points` for complex models
- Use LOD models when possible
- Enable caching

**Visual issues:**
- Adjust camera position and angles
- Check material properties
- Verify model scale

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `trimesh is required` | Missing dependency | `pip install trimesh` |
| `Asset 'model.glb' not found` | Wrong file path | Check assets/models/ directory |
| `Unsupported 3D model format` | Wrong file type | Use GLB, OBJ, or STL |
| `Invalid mesh data` | Corrupted model | Re-export model file |

## Examples

### Complete Scene Example

See `configs/3d_model_demo.yaml` for a comprehensive example including:
- Multiple 3D models
- Material variations  
- Camera animations
- Lighting effects
- Timeline coordination

### Test Integration

Run the integration test:

```bash
python examples/3d_model_test.py
```

This tests the system without requiring external model files.

## Technical Details

### Architecture

The 3D asset integration consists of:

1. **AssetManager Extension**: `load_3d_model()` method with format detection
2. **SceneBuilder Integration**: `3d_model` object type with material support
3. **Trimesh Integration**: Universal 3D file loading library
4. **Caching System**: Performance optimization with disk/memory cache
5. **Placeholder System**: Graceful fallback for missing models

### Model Processing Pipeline

1. **File Loading**: Trimesh loads the 3D model file
2. **Format Detection**: Automatic format detection by file extension  
3. **Mesh Processing**: Extract vertices, faces, and materials
4. **Manim Conversion**: Convert to ThreeDVMobject or VGroup
5. **Transform Application**: Apply position, rotation, scale
6. **Material Assignment**: Set colors, opacity, and PBR properties
7. **Caching**: Store processed model for reuse

### Performance Considerations

- Models are cached after first load
- Large models use point cloud representation
- Complex meshes are simplified automatically
- Background loading for better UI responsiveness

## Future Roadmap

Planned enhancements:

- [ ] Skeletal animation support
- [ ] Advanced PBR material rendering  
- [ ] Texture mapping and UV coordinates
- [ ] Procedural model generation
- [ ] Real-time model editing
- [ ] Physics simulation integration

## Contributing

To contribute to 3D asset support:

1. Test with various model formats
2. Report performance issues with large models
3. Submit example configurations
4. Suggest material system improvements
5. Add support for additional file formats

---

*For questions or issues, please refer to the main documentation or create an issue in the repository.*