# Viral Video Creation Guide for Manim Studio

This guide explains how to create viral-style videos using Manim Studio's text and layer management systems.

## Key Components

### 1. Viral Video Components (`src/components/viral_video_components.py`)

Provides specialized components for viral video creation:

- **ViralTextEffect**: Pre-styled text effects (impact, gradient, authority, CTA)
- **RapidTransition**: Quick-cut transitions (glitch, zoom, slide)
- **ProductReveal**: Dramatic product entrance animations
- **MerchEndScreen**: Complete merchandising end screen
- **SceneTransitionFactory**: Factory for creating rapid scene changes

### 2. Text Management Integration

All text creation uses the TextManager system:

```python
# Components accept text_manager parameter
hook = ViralTextEffect(
    "What if X was Y?",
    style="impact",
    text_manager=self.text_manager,  # Pass text_manager directly
    font_size=64
)
```

### 3. Layer Management

Proper z-ordering is handled automatically:

- Background elements: `layer_manager.add_object(obj, "background")`
- Main content: `layer_manager.add_object(obj, "main")`
- Effects: `layer_manager.add_object(obj, "effects")`
- Text: Automatically layered by TextManager
- UI/CTA: `layer_manager.add_object(obj, "overlay")`

## Usage Examples

### Basic Viral Video Structure

```python
from src.scenes.base_scene import StudioScene
from src.components.viral_video_components import *
from src.core.layer_manager import LayerManager

class MyViralVideo(StudioScene):
    def construct(self):
        self.layer_manager = LayerManager()
        
        # 1. Hook
        hook = ViralTextEffect(
            "What if NASA sold Tacos?",
            style="impact",
            text_manager=self.text_manager
        )
        
        # 2. Rapid content
        character = Circle(radius=2)
        self.layer_manager.add_object(character, "main")
        
        # 3. Authority drop
        tech = ViralTextEffect(
            "SpaceX Technology™",
            style="authority",
            text_manager=self.text_manager
        )
        
        # 4. Product reveal
        merch = MerchEndScreen(
            product_name="SPACE TACO TEE",
            website="example.com",
            text_manager=self.text_manager
        )
```

### YAML Configuration

The YAML system automatically uses proper text handling when rendered through the scene builder.

```yaml
name: "IfXWasY"
objects:
  hook_text:
    type: text
    text: "What if ${brand_x} was ${culture_y}?"
    params:
      style: title  # Uses TextManager styles
      font_size: 72
```

## Text Styles Available

- `title`: Large, bold text for hooks
- `subtitle`: Medium text for secondary info
- `caption`: Small text for details
- `overlay`: UI text that stays on top

## Best Practices

1. **Always pass text_manager** to components that create text (not the scene itself)
2. **Initialize LayerManager** in your construct method
3. **Use LayerManager** for all non-text objects
4. **Follow the formula**: Hook → Content → Authority → Product
5. **Keep it fast**: 29 seconds total, rapid transitions
6. **Test with text policy**: Ensure no direct Text() usage

## Rendering

```bash
# Using YAML template
manim-studio configs/if_x_was_y_template.yaml -q l -p

# Using Python directly
python -m manim --media_dir user-data developer/examples/viral_video_demo.py ViralMerchDemo -q l -p
```

## Common Patterns

### Tech Authority Drop
```python
auth = ViralTextEffect(
    "Azerbaijan Technology™",
    style="authority",
    text_manager=self.text_manager
)
```

### Product Reveal Sequence
```python
self.play(
    ProductReveal(
        merch_screen.product,
        merch_screen.website,
        run_time=2
    )
)
```

### Rapid Scene Transition
```python
self.play(
    SceneTransitionFactory.create_transition(
        old_scene, new_scene, "whip_pan", 0.3
    )
)
```

## Troubleshooting

- **Text not appearing**: Check text_manager is passed correctly
- **Pickle error**: Don't pass scene object, only text_manager
- **Wrong layering**: Use LayerManager for all objects
- **Slow rendering**: Use `-q l` for low quality during testing
- **Text policy warnings**: Update any direct Text() usage to use TextManager