# Interface Collaboration Guide

## Overview

Manim Studio provides multiple interfaces (GUI, MCP, API, CLI) that can work together for AI-human collaboration. All interfaces share a common core, enabling seamless interaction between AI assistants and human users.

## Architecture

### Shared State
All interfaces use a single shared instance of `ManimStudioCore` (defined in `src/interfaces/shared_state.py`):

```python
from interfaces.shared_features import ManimStudioCore

# Single shared instance used by all interfaces
shared_core = ManimStudioCore()
```

This means:
- Changes made in one interface are immediately visible in others
- No synchronization needed - they literally share the same memory
- True real-time collaboration between AI and human

### One Project at a Time
The system is designed for focused work on a single project:
- Only one active scene at a time (`current_scene`)
- All data stored in memory during work session
- Simple and straightforward workflow

## Collaboration Workflows

### AI-Initiated, Human-Refined
1. AI creates scene structure via MCP based on description
2. Human opens GUI to see the current scene
3. Human adjusts colors, positions via visual controls
4. AI adds complex animation sequences
5. Human reviews and triggers render

### Human-Initiated, AI-Enhanced
1. Human creates basic scene in GUI
2. AI accesses the same scene via MCP
3. AI analyzes and suggests improvements
4. AI applies timeline presets for professional animations
5. Human makes final adjustments

### Parallel Collaboration
1. Both interfaces run simultaneously:
   ```bash
   python start_all_interfaces.py --all
   ```
2. Human works on visual aspects in GUI
3. AI handles complex calculations/patterns via MCP
4. Real-time updates visible in both interfaces

## Project Management

### Switching Between Projects

Since only one project can be active at a time, use these functions to manage multiple projects:

#### 1. Export Current Project
```python
# Export to YAML format
result = core.export_scene()
yaml_config = result.data

# Save to file
import yaml
with open('my_project.yaml', 'w') as f:
    yaml.dump(yaml_config, f)
```

#### 2. Clear Workspace
```python
# Clear all scenes and reset
result = core.clear_workspace()
```

#### 3. Import Project
```python
# Load from YAML file
import yaml
with open('my_project.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f)

result = core.import_scene(yaml_config)
```

### Workflow Example
```python
# Work on Project A
core.create_scene("ProjectA", duration=10)
core.add_text("title", "My First Project")
# ... more work ...

# Save Project A
projectA_config = core.export_scene().data

# Switch to Project B
core.clear_workspace()
core.create_scene("ProjectB", duration=5)
# ... work on Project B ...

# Later, switch back to Project A
core.clear_workspace()
core.import_scene(projectA_config)
```

## Interface Capabilities

### MCP Interface (AI Assistants)
- Tool-based interaction via Model Context Protocol
- Programmatic access with structured outputs
- Auto-saves generated scripts
- Async operations for performance

### GUI Interface (Human Users)
- Visual form-based interface using Gradio
- Color pickers and dropdown menus
- Real-time JSON preview
- No coding required

### API Interface (External Integration)
- REST endpoints for all operations
- OpenAPI documentation
- Batch operations support
- Webhook capabilities

### CLI Interface (Command Line)
- Direct YAML scene rendering
- Quality and output control
- Validation features
- Batch processing

## Technical Benefits

1. **No Data Sync Issues**: Single source of truth in memory
2. **Consistent Validation**: Shared validation logic
3. **Unified Error Handling**: Same patterns across interfaces
4. **Easy Extension**: New features automatically available to all
5. **Simple Architecture**: No complex state management needed

## Best Practices

1. **Start Simple**: Begin with one interface, add others as needed
2. **Clear Communication**: AI and human should communicate about changes
3. **Regular Exports**: Save work frequently with export_scene()
4. **Modular Work**: Break complex scenes into smaller, manageable parts
5. **Leverage Strengths**: Let AI handle math/patterns, humans handle aesthetics

## Example: Complete Collaboration Session

```bash
# Terminal 1: Start all interfaces
python start_all_interfaces.py --all

# Terminal 2: Human uses GUI
# Open browser to http://localhost:7860
# Create basic scene structure

# Terminal 3: AI uses MCP
# AI reads current scene
# Adds mathematical animations
# Applies timeline presets

# Human refreshes GUI view
# Makes final color adjustments
# Exports final scene

# Both can see the same data throughout!
```

## Limitations and Considerations

1. **Memory-Based**: All work is lost if process stops (unless exported)
2. **Single Scene**: Can't work on multiple scenes simultaneously
3. **Local Only**: No built-in remote collaboration
4. **No History**: No undo/redo across interfaces (yet)

## Future Enhancements

While keeping the simple architecture, potential improvements include:
- Automatic periodic exports for backup
- Scene history/versioning in memory
- Template library accessible by all interfaces
- Shared asset management system
- Real-time preview synchronization