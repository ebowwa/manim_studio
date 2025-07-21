"""Enhanced MCP Server for Manim Studio with automatic script preservation."""

import asyncio
import json
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import the base server
from clean_server import ManimStudioServer as BaseManimStudioServer

class ManimStudioServerWithScriptSaving(BaseManimStudioServer):
    """Enhanced MCP Server that automatically saves generated scripts."""
    
    def __init__(self):
        super().__init__()
        # Configure script storage directory
        self.script_storage_dir = Path("/Users/ebowwa/apps/manim_studio/user-data/mcp-scripts")
        self.script_storage_dir.mkdir(parents=True, exist_ok=True)
        
    async def handle_call(self, name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Override handle_call to intercept render_scene calls."""
        
        if name == "render_scene":
            if not self.current_scene:
                return {"status": "error", "message": "No active scene. Create a scene first."}
            
            output_path = arguments["output_path"]
            quality = arguments.get("quality", "medium")
            
            # Generate the Manim script
            script_content = self._generate_manim_script()
            
            # Save to permanent location with timestamp and scene name
            script_hash = hashlib.md5(script_content.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_name = self.current_scene.get("name", "Scene")
            permanent_filename = f"{timestamp}_{scene_name}_{script_hash}.py"
            permanent_path = self.script_storage_dir / permanent_filename
            
            # Check if identical script already exists
            existing_scripts = list(self.script_storage_dir.glob(f"*_{scene_name}_*.py"))
            script_already_saved = False
            
            for existing_script in existing_scripts:
                try:
                    existing_content = existing_script.read_text()
                    if existing_content == script_content:
                        script_already_saved = True
                        permanent_path = existing_script
                        break
                except Exception:
                    continue
            
            # Save script if not already saved
            if not script_already_saved:
                permanent_path.write_text(script_content)
            
            # Also create temporary file for immediate rendering
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(script_content)
            temp_file.close()
            
            # Create metadata file
            metadata = {
                "scene_name": scene_name,
                "timestamp": timestamp,
                "quality": quality,
                "output_path": output_path,
                "scene_config": self.current_scene,
                "script_hash": script_hash,
                "permanent_script": str(permanent_path),
                "temp_script": temp_file.name
            }
            
            metadata_path = permanent_path.with_suffix('.json')
            metadata_path.write_text(json.dumps(metadata, indent=2))
            
            return {
                "status": "success",
                "message": f"Scene prepared for rendering. Script saved to {permanent_path}",
                "script_path": temp_file.name,
                "permanent_script_path": str(permanent_path),
                "output_path": output_path,
                "quality": quality,
                "render_command": f"manim {temp_file.name} Scene -o {output_path}",
                "saved_as": permanent_filename
            }
        else:
            # Delegate to parent for all other calls
            return await super().handle_call(name, arguments)
    
    async def run_stdio(self):
        """Run the MCP server over stdio."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="manim-studio-enhanced",
                    server_version="0.1.1",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

def main():
    """Main entry point."""
    import asyncio
    import logging
    
    logging.basicConfig(level=logging.INFO)
    server = ManimStudioServerWithScriptSaving()
    asyncio.run(server.run_stdio())

if __name__ == "__main__":
    main()