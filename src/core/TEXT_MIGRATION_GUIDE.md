# TextManager Migration Guide

## Overview

All text creation in Manim Studio must now go through the centralized `TextManager` system to ensure consistency, prevent fragmentation, and provide proper text lifecycle management.

## Quick Migration Reference

### ❌ Old Way (DO NOT USE)
```python
# Direct text creation - DEPRECATED
title = Text("My Title", font_size=72, color=WHITE)
title.to_edge(UP)
self.add(title)
self.play(Write(title))

# Manual positioning and styling
subtitle = Text("Subtitle", font_size=48)
subtitle.set_color("#00d4ff")
subtitle.next_to(title, DOWN)
self.add(subtitle)

# 3D scene text problems  
label = Text("Label", font_size=36).to_edge(DOWN)
self.add_fixed_in_frame_mobjects(label)
```

### ✅ New Way (USE THIS)
```python
# Initialize TextManager (once per scene)
text_manager = TextManager(self)

# Create text with semantic styling and positioning
text_manager.add_text(
    "My Title",
    style='title',                    # Predefined consistent style
    layout='title',                   # Semantic positioning
    key='main_title',                 # Key for easy updates
    animation=Write                   # Clean animation
)

# Update text easily
text_manager.update_text(
    'main_title',
    "New Title Text", 
    animation=Transform
)

# 3D scenes - automatic fixed frame handling
text_manager.add_text(
    "3D Label",
    style='label_3d',
    layout='fixed_label_3d',          # Handles fixed frames automatically
    key='label'
)
```

## Predefined Styles

Use these instead of manual font_size and color settings:

```python
STYLES = {
    'title': TextStyle(font_size=72, weight=BOLD, color=WHITE),
    'subtitle': TextStyle(font_size=48, color="#00d4ff"),
    'heading': TextStyle(font_size=36, weight=BOLD),
    'body': TextStyle(font_size=24),
    'caption': TextStyle(font_size=18, color=GRAY),
    'overlay': TextStyle(font_size=36, background=True),
    'label_3d': TextStyle(font_size=28, background=True, background_opacity=0.8)
}
```

## Predefined Layouts

Use these instead of manual positioning:

```python
LAYOUTS = {
    'center': Center of screen
    'title': Top center with offset
    'subtitle': Below title
    'bottom_label': Bottom center
    'corner_info': Bottom right corner
    'fixed_title_3d': Top center, fixed in 3D frame
    'fixed_label_3d': Bottom center, fixed in 3D frame
}
```

## Common Migration Patterns

### 1. Scene Classes
```python
# OLD
class MyScene(Scene):
    def construct(self):
        title = Text("Title", font_size=60)
        
# NEW  
class MyScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_manager = TextManager(self)  # Add to constructor
        
    def construct(self):
        self.text_manager.add_text("Title", style='title', key='title')
```

### 2. 3D Scenes
```python
# OLD
class My3DScene(ThreeDScene):
    def construct(self):
        title = Text("3D Title", font_size=60).to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        
# NEW
class My3DScene(StudioScene3D):  # Use StudioScene3D base class
    def construct(self):
        # text_manager already available from base class
        self.text_manager.add_text(
            "3D Title",
            style='title',
            layout='fixed_title_3d'
        )
```

### 3. Component Methods
```python
# OLD
def create_label(self, text: str):
    label = Text(text, font_size=24)
    label.set_color(YELLOW)
    return label

# NEW  
def create_label(self, text: str):
    from ..core.text_manager import TextManager
    text_manager = TextManager(self.scene)  # Pass scene reference
    return text_manager.create_text(text, style='body', color=YELLOW)
```

### 4. Text Updates and Sequences
```python
# OLD - Manual removal and recreation
self.remove(old_text)
new_text = Text("New Text", font_size=36).to_edge(DOWN)
self.add(new_text)
self.play(Transform(old_text, new_text))

# NEW - Managed updates
text_manager.update_text(
    'label_key',
    "New Text", 
    animation=Transform
)

# Text sequences
text_sequence = [
    ("First Text", 'title', 'center'),
    ("Second Text", 'subtitle', 'center'),
    ("Final Text", 'body', 'center')
]
text_manager.create_text_sequence(text_sequence, duration=2.0)
```

### 5. Text Cleanup
```python
# OLD - Manual cleanup
for text_obj in text_objects:
    self.remove(text_obj)

# NEW - Automatic cleanup
text_manager.clear_all_text(animation=FadeOut)
# Or remove specific text
text_manager.remove_text('text_key', animation=FadeOut)
```

## Migration Checklist

When updating a file:

- [ ] Replace all `Text()` calls with `text_manager.add_text()` or `text_manager.create_text()`
- [ ] Replace all `MathTex()` calls with `text_manager.create_text(style={'font': 'math'})`
- [ ] Remove manual positioning (`.to_edge()`, `.move_to()`, `.next_to()`) and use layouts
- [ ] Remove manual styling (`.set_color()`, `.scale()`) and use predefined styles
- [ ] Replace `self.add_fixed_in_frame_mobjects()` for text with `layout='fixed_*_3d'`
- [ ] Add `TextManager` initialization to scene constructor or method
- [ ] Use text keys for any text that needs updates
- [ ] Use `text_manager.update_text()` instead of recreating text

## Custom Styles and Layouts

If you need custom styling:

```python
# Custom style
custom_style = TextStyle(
    font_size=32,
    color="#ff6b6b", 
    background=True,
    background_color=BLACK
)

text_manager.add_text(
    "Custom Text",
    style=custom_style,
    layout='center'
)

# Custom layout
custom_layout = TextLayout(
    position=TextPosition.TOP_RIGHT,
    offset=np.array([-1, -1, 0]),
    layer=TextLayer.UI
)
```

## Benefits of Migration

✅ **No more text fragmentation** - Unified text rendering  
✅ **Consistent styling** - Predefined styles prevent inconsistency  
✅ **Proper 3D support** - Automatic fixed frame handling  
✅ **Easy updates** - Text management by key  
✅ **Automatic cleanup** - Prevent memory leaks  
✅ **Professional layouts** - Semantic positioning system  
✅ **Better animations** - Integrated animation handling  

## Need Help?

- Check `src/core/text_manager.py` for full API reference
- See `examples/fixed_camera_3d_demo.py` for working examples
- Use `test_text_manager.py` to test TextManager features

## Files That Must Be Updated

All files containing direct text creation need migration:

### High Priority (Critical for 3D scenes)
- All 3D demo files in `examples/`
- All files in `src/scenes/`
- All files in `src/components/`

### Medium Priority  
- Demo files in `developer/examples/`
- Test files in `developer/tests/`
- Interface files in `src/interfaces/`

### Verification
After migration, ensure:
- No direct `Text()`, `MathTex()`, or `Tex()` calls remain
- All text positioning goes through TextManager layouts
- 3D scenes use `fixed_*_3d` layouts
- Text updates use `text_manager.update_text()`
- Scene cleanup calls `text_manager.clear_all_text()`