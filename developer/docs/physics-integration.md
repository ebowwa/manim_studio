# Physics Integration in Manim Studio

## Overview

Manim Studio now includes basic physics components that can be used in YAML scenes or Python code.

## Available Physics Objects

### 1. SimplePendulum
- Simulates pendulum motion with customizable length, angle, gravity, and damping
- Properties: `length`, `angle`, `gravity`, `damping`, `bob_radius`

### 2. Spring
- Implements Hooke's law spring physics
- Properties: `rest_length`, `spring_constant`, `mass`, `damping`, `coils`

### 3. ProjectileMotion
- Simulates projectile motion with gravity
- Properties: `initial_velocity`, `gravity`, `trail_length`

## Using Physics in YAML

```yaml
objects:
  - name: my_pendulum
    type: physics.pendulum
    params:
      length: 2.5
      angle: 0.8  # radians
      gravity: 9.8
      damping: 0.995
      position: [0, 0, 0]
      auto_update: true  # Enables automatic physics simulation
```

## Using Physics in Python

```python
from src.components.physics_objects import SimplePendulum, create_physics_updater

# Create pendulum
pendulum = SimplePendulum(length=2, angle=PI/4)

# Add physics updater
pendulum.add_updater(create_physics_updater(pendulum))

# Add to scene
self.add(pendulum)
```

## Physics Effects

Available physics effects that can be applied to any object:

- `physics.gravity` - Apply gravity with bouncing
- `physics.oscillation` - Oscillating motion
- `physics.spring_force` - Spring-like attraction to a point
- `physics.circular_orbit` - Circular orbital motion
- `physics.wave_motion` - Wave-like motion along a direction

### Example in YAML:

```yaml
animations:
  - type: effect
    target: my_object
    effect_type: physics.gravity
    duration: 5
    properties:
      gravity: 9.8
      initial_velocity: [2, 5, 0]
      ground_level: -3
      bounce_damping: 0.7
```

## Examples

1. **Basic Demo**: `scenes/physics_demo.yaml`
2. **Python Examples**: `developer/examples/simple_physics_demo.py`
3. **Integration Test**: `developer/tests/test_physics_integration.py`

## Running Examples

```bash
# YAML scene
manim-studio scenes/physics_demo.yaml -ql

# Python example
manim --media_dir user-data -pql developer/examples/simple_physics_demo.py PhysicsShowcase
```

## Implementation Details

The physics integration is designed to be:
- **Minimal**: Only essential physics components included
- **Reusable**: Components work in both YAML and Python
- **Extensible**: Easy to add new physics objects or effects
- **Non-intrusive**: Physics is optional and doesn't affect existing functionality

## Future Enhancements

Possible additions:
- Collision detection
- Constraints (pins, ropes, etc.)
- Fluid dynamics
- Electromagnetic fields
- More complex physics simulations

The current implementation provides a foundation that can be expanded based on user needs.