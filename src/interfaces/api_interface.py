"""API Interface using Shared Features

This module provides REST API functionality while leveraging the shared core features.
Uses FastAPI for the web API.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
import logging
import uvicorn
from pathlib import Path

# Import shared features
from src.interfaces.shared_features import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult,
    TextObject,
    ShapeObject,
    AnimationSequence,
    SceneDefinition
)

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class CreateSceneRequest(BaseModel):
    name: str = Field(..., description="Scene name")
    duration: float = Field(5.0, ge=0.1, description="Duration in seconds")
    background_color: str = Field("#000000", description="Background color hex")
    resolution: List[int] = Field([1920, 1080], description="Resolution [width, height]")
    fps: int = Field(60, ge=1, description="Frames per second")


class AddTextRequest(BaseModel):
    id: str = Field(..., description="Unique text identifier")
    content: str = Field(..., description="Text content")
    color: str = Field("#FFFFFF", description="Text color hex")
    position: List[float] = Field([0, 0, 0], description="Position [x, y, z]")
    font_size: int = Field(48, ge=1, description="Font size")
    font: str = Field("Arial", description="Font family")


class AddShapeRequest(BaseModel):
    id: str = Field(..., description="Unique shape identifier")
    shape_type: ShapeType = Field(..., description="Shape type")
    color: str = Field("#FFFFFF", description="Shape color hex")
    size: float = Field(1.0, ge=0.1, description="Shape size")
    position: List[float] = Field([0, 0, 0], description="Position [x, y, z]")


class AddAnimationRequest(BaseModel):
    target: str = Field(..., description="Target object ID")
    animation_type: AnimationType = Field(..., description="Animation type")
    start_time: float = Field(0.0, ge=0, description="Start time in seconds")
    duration: float = Field(1.0, ge=0.1, description="Duration in seconds")
    easing: str = Field("ease_in_out", description="Easing function")
    properties: Dict[str, Any] = Field({}, description="Animation properties")


class ApplyPresetRequest(BaseModel):
    preset_name: str = Field(..., description="Preset name to apply")
    parameters: Dict[str, Any] = Field({}, description="Custom preset parameters")


class PrepareRenderRequest(BaseModel):
    output_path: str = Field(..., description="Output video file path")
    quality: RenderQuality = Field(RenderQuality.HIGH, description="Render quality")


class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message")


class APIInterface:
    """API-specific interface implementation using shared features."""
    
    def __init__(self):
        from src.interfaces.shared_state import shared_core
        self.core = shared_core
        self.app = self.create_app()
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application with all endpoints."""
        
        app = FastAPI(
            title="Manim Studio API",
            description="REST API for creating animations using Manim Studio",
            version="0.3.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Scene Management Endpoints
        @app.post("/scenes", response_model=APIResponse, tags=["Scenes"])
        async def create_scene(request: CreateSceneRequest):
            """Create a new animation scene."""
            result = self.core.create_scene(
                name=request.name,
                duration=request.duration,
                background_color=request.background_color,
                resolution=request.resolution,
                fps=request.fps
            )
            return self._to_api_response(result)
        
        @app.get("/scenes", response_model=APIResponse, tags=["Scenes"])
        async def list_scenes():
            """List all created scenes."""
            result = self.core.list_scenes()
            return self._to_api_response(result)
        
        @app.get("/scenes/{scene_name}", response_model=APIResponse, tags=["Scenes"])
        async def get_scene(scene_name: str):
            """Get scene configuration by name."""
            result = self.core.get_scene(scene_name)
            return self._to_api_response(result)
        
        @app.get("/scenes/current", response_model=APIResponse, tags=["Scenes"])
        async def get_current_scene():
            """Get current active scene configuration."""
            result = self.core.get_scene()
            return self._to_api_response(result)
        
        # Object Creation Endpoints
        @app.post("/objects/text", response_model=APIResponse, tags=["Objects"])
        async def add_text(request: AddTextRequest):
            """Add text object to current scene."""
            result = self.core.add_text(
                text_id=request.id,
                content=request.content,
                color=request.color,
                position=request.position,
                font_size=request.font_size,
                font=request.font
            )
            return self._to_api_response(result)
        
        @app.post("/objects/shapes", response_model=APIResponse, tags=["Objects"])
        async def add_shape(request: AddShapeRequest):
            """Add shape object to current scene."""
            result = self.core.add_shape(
                shape_id=request.id,
                shape_type=request.shape_type,
                color=request.color,
                size=request.size,
                position=request.position
            )
            return self._to_api_response(result)
        
        # Animation Endpoints
        @app.post("/animations", response_model=APIResponse, tags=["Animations"])
        async def add_animation(request: AddAnimationRequest):
            """Add animation to an object in current scene."""
            result = self.core.add_animation(
                target=request.target,
                animation_type=request.animation_type,
                start_time=request.start_time,
                duration=request.duration,
                easing=request.easing,
                properties=request.properties
            )
            return self._to_api_response(result)
        
        # Timeline Preset Endpoints
        @app.get("/presets", response_model=APIResponse, tags=["Timeline Presets"])
        async def list_presets(category: Optional[str] = None):
            """List all available timeline presets."""
            result = self.core.list_presets(category)
            return self._to_api_response(result)
        
        @app.get("/presets/{preset_name}", response_model=APIResponse, tags=["Timeline Presets"])
        async def get_preset_info(preset_name: str):
            """Get detailed information about a specific preset."""
            result = self.core.get_preset_info(preset_name)
            return self._to_api_response(result)
        
        @app.post("/presets/apply", response_model=APIResponse, tags=["Timeline Presets"])
        async def apply_preset(request: ApplyPresetRequest):
            """Apply a timeline preset to the current scene."""
            result = self.core.apply_preset(
                preset_name=request.preset_name,
                parameters=request.parameters
            )
            return self._to_api_response(result)
        
        # Rendering Endpoints
        @app.post("/render/prepare", response_model=APIResponse, tags=["Rendering"])
        async def prepare_render(request: PrepareRenderRequest):
            """Prepare current scene for rendering."""
            result = self.core.prepare_render(
                output_path=request.output_path,
                quality=request.quality
            )
            return self._to_api_response(result)
        
        # Utility Endpoints
        @app.get("/health", tags=["Utility"])
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "message": "Manim Studio API is running"}
        
        @app.get("/openapi.json", tags=["Utility"])
        async def get_openapi_schema():
            """Get OpenAPI schema for API discovery."""
            return app.openapi()
        
        @app.get("/api-info", response_model=Dict[str, Any], tags=["Utility"])
        async def get_api_info():
            """Get comprehensive API information for MCP and other integrations."""
            openapi_schema = app.openapi()
            
            # Extract endpoint information
            endpoints = []
            for path, methods in openapi_schema.get("paths", {}).items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        endpoints.append({
                            "path": path,
                            "method": method.upper(),
                            "summary": details.get("summary", ""),
                            "description": details.get("description", ""),
                            "tags": details.get("tags", []),
                            "parameters": details.get("parameters", []),
                            "requestBody": details.get("requestBody"),
                            "responses": details.get("responses", {})
                        })
            
            # Extract data models
            components = openapi_schema.get("components", {})
            schemas = components.get("schemas", {})
            
            return {
                "api_info": {
                    "title": openapi_schema.get("info", {}).get("title", ""),
                    "version": openapi_schema.get("info", {}).get("version", ""),
                    "description": openapi_schema.get("info", {}).get("description", "")
                },
                "endpoints": endpoints,
                "schemas": schemas,
                "base_url": "http://localhost:8000",  # Could be made configurable
                "total_endpoints": len(endpoints)
            }
        
        @app.get("/animation-types", response_model=List[str], tags=["Utility"])
        async def get_animation_types():
            """Get all available animation types."""
            return [anim.value for anim in AnimationType]
        
        @app.get("/shape-types", response_model=List[str], tags=["Utility"])
        async def get_shape_types():
            """Get all available shape types."""
            return [shape.value for shape in ShapeType]
        
        @app.get("/render-qualities", response_model=List[str], tags=["Utility"])
        async def get_render_qualities():
            """Get all available render quality levels."""
            return [quality.value for quality in RenderQuality]
        
        # Exception handlers
        @app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            logger.error(f"HTTP Exception: {exc.detail}")
            return APIResponse(
                status="error",
                error=exc.detail
            ).dict()
        
        @app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            logger.error(f"Unexpected error: {str(exc)}")
            return APIResponse(
                status="error",
                error="Internal server error"
            ).dict()
        
        return app
    
    def _to_api_response(self, result: InterfaceResult) -> APIResponse:
        """Convert InterfaceResult to API response."""
        return APIResponse(
            status=result.status,
            data=result.data,
            message=result.message,
            error=result.error
        )
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the API server."""
        logger.info(f"Starting Manim Studio API on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, **kwargs)


# Enhanced API with additional endpoints for batch operations
class EnhancedAPIInterface(APIInterface):
    """Enhanced API with batch operations and additional features."""
    
    def create_app(self) -> FastAPI:
        """Create enhanced FastAPI application."""
        app = super().create_app()
        
        # Batch operation models
        class BatchTextRequest(BaseModel):
            texts: List[AddTextRequest] = Field(..., description="List of text objects to add")
        
        class BatchShapeRequest(BaseModel):
            shapes: List[AddShapeRequest] = Field(..., description="List of shape objects to add")
        
        class BatchAnimationRequest(BaseModel):
            animations: List[AddAnimationRequest] = Field(..., description="List of animations to add")
        
        class SceneTemplateRequest(BaseModel):
            name: str = Field(..., description="Scene name")
            template_type: str = Field(..., description="Template type")
            parameters: Dict[str, Any] = Field({}, description="Template parameters")
        
        # Batch endpoints
        @app.post("/objects/text/batch", response_model=APIResponse, tags=["Batch Operations"])
        async def add_batch_text(request: BatchTextRequest):
            """Add multiple text objects to current scene."""
            results = []
            for text_req in request.texts:
                result = self.core.add_text(
                    text_id=text_req.id,
                    content=text_req.content,
                    color=text_req.color,
                    position=text_req.position,
                    font_size=text_req.font_size,
                    font=text_req.font
                )
                results.append(result.to_dict())
            
            return APIResponse(
                status="success",
                data={"results": results},
                message=f"Added {len(request.texts)} text objects"
            )
        
        @app.post("/objects/shapes/batch", response_model=APIResponse, tags=["Batch Operations"])
        async def add_batch_shapes(request: BatchShapeRequest):
            """Add multiple shape objects to current scene."""
            results = []
            for shape_req in request.shapes:
                result = self.core.add_shape(
                    shape_id=shape_req.id,
                    shape_type=shape_req.shape_type,
                    color=shape_req.color,
                    size=shape_req.size,
                    position=shape_req.position
                )
                results.append(result.to_dict())
            
            return APIResponse(
                status="success",
                data={"results": results},
                message=f"Added {len(request.shapes)} shape objects"
            )
        
        @app.post("/animations/batch", response_model=APIResponse, tags=["Batch Operations"])
        async def add_batch_animations(request: BatchAnimationRequest):
            """Add multiple animations to current scene."""
            results = []
            for anim_req in request.animations:
                result = self.core.add_animation(
                    target=anim_req.target,
                    animation_type=anim_req.animation_type,
                    start_time=anim_req.start_time,
                    duration=anim_req.duration,
                    easing=anim_req.easing,
                    properties=anim_req.properties
                )
                results.append(result.to_dict())
            
            return APIResponse(
                status="success",
                data={"results": results},
                message=f"Added {len(request.animations)} animations"
            )
        
        # Template endpoints
        @app.post("/scenes/from-template", response_model=APIResponse, tags=["Templates"])
        async def create_scene_from_template(request: SceneTemplateRequest):
            """Create scene from predefined template."""
            # This would use template definitions to create complex scenes
            # For now, just create a basic scene and apply a preset
            
            scene_result = self.core.create_scene(name=request.name)
            if scene_result.status != "success":
                return self._to_api_response(scene_result)
            
            # Apply template-specific preset if available
            if request.template_type in ["intro", "title", "outro"]:
                preset_result = self.core.apply_preset(
                    f"{request.template_type}_sequence", 
                    request.parameters
                )
                
                return APIResponse(
                    status="success",
                    data={
                        "scene": scene_result.data,
                        "preset_applied": preset_result.data if preset_result.status == "success" else None
                    },
                    message=f"Created scene '{request.name}' from template '{request.template_type}'"
                )
            
            return self._to_api_response(scene_result)
        
        @app.get("/templates", response_model=List[str], tags=["Templates"])
        async def list_templates():
            """List available scene templates."""
            return ["intro", "title", "outro", "presentation", "tutorial"]
        
        return app


def main():
    """Main entry point for API interface."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Manim Studio API Interface...")
    
    # Use enhanced API by default
    api = EnhancedAPIInterface()
    api.run(
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()