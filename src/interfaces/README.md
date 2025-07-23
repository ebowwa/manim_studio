# Manim Studio Interfaces

This directory contains multiple interface implementations for Manim Studio, all built on a shared features foundation to avoid code duplication and ensure consistency.

## Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   MCP Interface     │    │   GUI Interface     │    │   API Interface     │
│   (AI Assistants)   │    │   (Web UI)          │    │   (REST API)        │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
                            ┌─────────▼───────────┐
                            │  Shared Features    │
                            │  (Core Logic)       │
                            └─────────┬───────────┘
                                      │
                            ┌─────────▼───────────┐
                            │   Manim Studio      │
                            │   Core Modules      │
                            └─────────────────────┘
```

## Shared Features (`shared_features.py`)

The foundation layer that provides:

### Core Components
- **ManimStudioCore**: Main interface combining all functionality
- **SceneManager**: Scene creation and object management
- **PresetManager**: Timeline preset handling
- **RenderEngine**: Script generation and rendering preparation

### Data Models
- **SceneDefinition**: Standardized scene representation
- **TextObject**, **ShapeObject**: Object models
- **AnimationSequence**: Animation configuration
- **InterfaceResult**: Consistent response format

### Enums
- **AnimationType**: Standardized animation types
- **ShapeType**: Available shape types  
- **RenderQuality**: Render quality levels

## Interface Implementations

All interfaces can now be launched through the unified launcher system:

### Unified Launcher

**Main Entry Point** (`main.py`):
```bash
# New unified syntax
python main.py cli scene.yaml -q l -p        # CLI interface
python main.py api --port 8000               # API server  
python main.py gui --port 7860               # GUI interface
python main.py mcp                           # MCP server

# Backwards compatibility
python main.py scene.yaml -q l -p            # Auto-detects CLI mode

# Help and discovery
python main.py --help                        # Show all options
python main.py --list-interfaces             # List available interfaces
```

**Multi-Interface Launcher** (`src/interfaces/start_all_interfaces.py`):
```bash
python src/interfaces/start_all_interfaces.py               # Start API + GUI
python src/interfaces/start_all_interfaces.py --all         # Start API + GUI + MCP
python src/interfaces/start_all_interfaces.py --api --gui   # Start specific interfaces
python src/interfaces/start_all_interfaces.py --ports 8001 7861  # Custom ports
```

### 1. MCP Interface (`mcp_interface.py`)

**Purpose**: Integration with AI assistants via Model Context Protocol

**Features**:
- Tool-based interaction model
- JSON-structured responses
- Async operation support
- Direct integration with Claude, ChatGPT, etc.
- API discovery capabilities

**Usage**:
```bash
# Via unified launcher (recommended)
python main.py mcp

# Direct execution
python src/interfaces/mcp_interface.py
```

**Tools Available**:
- `create_scene` - Create new animation scenes
- `add_text`, `add_shape` - Add objects to scenes
- `add_animation` - Create animations
- `list_timeline_presets`, `apply_timeline_preset` - Timeline management
- `prepare_render` - Generate rendering scripts
- `discover_api_endpoints` - Discover all available API endpoints
- `call_api_endpoint` - Call specific API endpoints directly

### 2. GUI Interface (`gui_interface.py`)

**Purpose**: Web-based visual interface for non-programmers

**Features**:
- Gradio-powered web interface
- Form-based input with validation
- Real-time JSON output
- Tabbed organization
- Color pickers and dropdowns

**Usage**:
```bash
# Via unified launcher (recommended)
python main.py gui --port 7860

# Direct execution  
python src/interfaces/gui_interface.py
```

**Interface Sections**:
- **Scene Management**: Create and manage scenes
- **Add Objects**: Text and shape creation with visual controls
- **Animations**: Animation configuration with easing options
- **Timeline Presets**: Browse and apply animation presets
- **Rendering**: Prepare scenes for video generation

### 3. API Interface (`api_interface.py`)

**Purpose**: REST API for programmatic access and integration

**Features**:
- FastAPI-powered REST endpoints
- OpenAPI/Swagger documentation
- Pydantic data validation
- CORS support
- Batch operations
- Template system

**Usage**:
```bash
# Via unified launcher (recommended)
python main.py api --port 8000

# Direct execution
python src/interfaces/api_interface.py
```

**Key Endpoints**:
- `POST /scenes` - Create scenes
- `POST /objects/text`, `POST /objects/shapes` - Add objects
- `POST /animations` - Add animations
- `GET /presets`, `POST /presets/apply` - Timeline presets
- `POST /render/prepare` - Prepare rendering
- `POST /objects/text/batch` - Batch text creation

**API Documentation**: Available at `http://localhost:8000/docs`

## Common Workflow

Regardless of interface, the typical workflow is:

1. **Create Scene**: Define scene parameters (name, duration, resolution)
2. **Add Objects**: Create text and shape objects with positioning
3. **Add Animations**: Define how objects move and transform over time
4. **Apply Presets** (Optional): Use predefined animation sequences
5. **Prepare Render**: Generate Manim script and render commands

## Benefits of Shared Architecture

### 1. **Consistency**
- All interfaces use identical data models
- Same validation and error handling
- Consistent behavior across interfaces

### 2. **Maintainability** 
- Business logic centralized in shared features
- Interface-specific code focuses on presentation
- Single point of truth for core functionality

### 3. **Extensibility**
- New interfaces can be added easily
- Core features automatically available in all interfaces
- Interface-specific enhancements don't affect others

### 4. **Testing**
- Core functionality tested once
- Interface tests focus on presentation layer
- Reduced test complexity and maintenance

## Development Guidelines

### Adding New Features

1. **Core Logic**: Implement in `shared_features.py`
2. **Interface Integration**: Add interface-specific wrappers
3. **Documentation**: Update this README and interface docs
4. **Testing**: Add tests for core logic and interface integration

### Interface-Specific Considerations

#### MCP Interface
- Keep tools focused and atomic
- Provide clear JSON schemas
- Handle async operations properly
- Log to stderr to maintain protocol compliance

#### GUI Interface  
- Design intuitive form layouts
- Provide helpful defaults and validation
- Show real-time feedback
- Use appropriate Gradio components

#### API Interface
- Follow REST conventions
- Provide comprehensive OpenAPI docs
- Implement proper error codes
- Consider rate limiting for production

### Data Flow

```
User Input → Interface Layer → Shared Features → Core Modules → Manim
                    ↓
Interface Response ← Result Processing ← Operation Result
```

## Example Usage

### MCP Interface (AI Assistant)
```json
{
  "tool": "create_scene",
  "arguments": {
    "name": "MyScene",
    "duration": 10.0,
    "background_color": "#1a1a1a"
  }
}
```

### GUI Interface (Web Form)
- Fill out scene creation form
- Click "Create Scene" button
- View JSON result in output panel

### API Interface (HTTP Request)
```bash
curl -X POST "http://localhost:8000/scenes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyScene",
    "duration": 10.0,
    "background_color": "#1a1a1a"
  }'
```

All three approaches create the same scene using the same underlying functionality, demonstrating the power of the shared architecture.

## API Discovery and Integration

The system now includes automatic API discovery capabilities that allow the MCP interface to discover and interact with the REST API endpoints dynamically.

### API Discovery Features

1. **OpenAPI Schema Exposure**: The API automatically exposes its OpenAPI schema at `/openapi.json`
2. **Structured API Info**: Enhanced endpoint at `/api-info` provides organized endpoint information
3. **MCP Discovery Tools**: The MCP interface can discover and call API endpoints

### Usage Examples

#### Discover Available Endpoints
```json
{
  "tool": "discover_api_endpoints",
  "arguments": {
    "api_base_url": "http://localhost:8000",
    "include_schemas": false
  }
}
```

Response includes:
- List of all available endpoints
- HTTP methods and descriptions
- Request/response schemas (if requested)
- Total endpoint count

#### Call API Endpoints Directly
```json
{
  "tool": "call_api_endpoint", 
  "arguments": {
    "endpoint": "/scenes",
    "method": "POST",
    "data": {
      "name": "MyScene",
      "duration": 10.0
    }
  }
}
```

### Benefits for Integration

1. **Dynamic Discovery**: MCP can discover new API endpoints without code changes
2. **Hybrid Workflows**: Combine MCP tools with direct API calls
3. **External Integration**: Other systems can discover and use the API
4. **Development Aid**: Developers can explore API capabilities through MCP

### API Endpoints for Discovery

- `GET /openapi.json` - Full OpenAPI specification
- `GET /api-info` - Structured endpoint information with schemas
- `GET /health` - API health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

This creates a self-documenting and discoverable API ecosystem where MCP clients can automatically discover and utilize all available functionality.

## Future Enhancements

- **CLI Interface**: Command-line interface for scripting
- **Plugin System**: Allow third-party interface extensions
- **Real-time Preview**: Live animation preview in GUI
- **Collaborative Editing**: Multi-user scene editing
- **Template Gallery**: Predefined scene templates
- **Asset Management**: Shared asset library across interfaces