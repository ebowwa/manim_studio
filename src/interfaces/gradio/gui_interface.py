"""GUI Interface using Shared Features

This module provides GUI-specific functionality while leveraging the shared core features.
Uses Gradio for the web-based interface.
"""

import gradio as gr
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# Import shared features
from src.interfaces.shared_features import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult
)

logger = logging.getLogger(__name__)


class GUIInterface:
    """GUI-specific interface implementation using shared features."""
    
    def __init__(self):
        from src.interfaces.shared_state import shared_core
        self.core = shared_core
        
    def create_scene_gui(self, name: str, duration: float, background_color: str, 
                        width: int, height: int, fps: int) -> Tuple[str, str]:
        """GUI wrapper for scene creation."""
        try:
            result = self.core.create_scene(
                name=name,
                duration=duration,
                background_color=background_color,
                resolution=[width, height],
                fps=fps
            )
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except Exception as e:
            logger.error(f"GUI scene creation error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def add_text_gui(self, text_id: str, content: str, color: str, 
                    x: float, y: float, z: float, font_size: int, font: str) -> Tuple[str, str]:
        """GUI wrapper for adding text."""
        try:
            result = self.core.add_text(
                text_id=text_id,
                content=content,
                color=color,
                position=[x, y, z],
                font_size=font_size,
                font=font
            )
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except Exception as e:
            logger.error(f"GUI text addition error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def add_shape_gui(self, shape_id: str, shape_type: str, color: str, 
                     size: float, x: float, y: float, z: float) -> Tuple[str, str]:
        """GUI wrapper for adding shapes."""
        try:
            result = self.core.add_shape(
                shape_id=shape_id,
                shape_type=shape_type,
                color=color,
                size=size,
                position=[x, y, z]
            )
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except Exception as e:
            logger.error(f"GUI shape addition error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def add_animation_gui(self, target: str, animation_type: str, start_time: float, 
                         duration: float, easing: str, properties_json: str) -> Tuple[str, str]:
        """GUI wrapper for adding animations."""
        try:
            properties = {}
            if properties_json.strip():
                properties = json.loads(properties_json)
            
            result = self.core.add_animation(
                target=target,
                animation_type=animation_type,
                start_time=start_time,
                duration=duration,
                easing=easing,
                properties=properties
            )
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in properties: {str(e)}", json.dumps({"error": f"Invalid JSON in properties: {str(e)}"}, indent=2)
        except Exception as e:
            logger.error(f"GUI animation addition error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def list_scenes_gui(self) -> Tuple[str, str]:
        """GUI wrapper for listing scenes."""
        try:
            result = self.core.list_scenes()
            
            if result.status == "success":
                scenes_info = f"Found {result.data['total']} scenes"
                if result.data['current_scene']:
                    scenes_info += f" (Current: {result.data['current_scene']})"
                return scenes_info, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", ""
                
        except Exception as e:
            logger.error(f"GUI list scenes error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def get_scene_gui(self, scene_name: str = "") -> Tuple[str, str]:
        """GUI wrapper for getting scene info."""
        try:
            result = self.core.get_scene(scene_name if scene_name.strip() else None)
            
            if result.status == "success":
                scene_data = result.data
                info = f"Scene: {scene_data['name']}, Duration: {scene_data['duration']}s"
                info += f", Objects: {len(scene_data['objects'])}, Animations: {len(scene_data['animations'])}"
                return info, json.dumps(scene_data, indent=2)
            else:
                return f"Error: {result.error}", ""
                
        except Exception as e:
            logger.error(f"GUI get scene error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def list_presets_gui(self, category: str = "") -> Tuple[str, str]:
        """GUI wrapper for listing timeline presets."""
        try:
            result = self.core.list_presets(category if category.strip() else None)
            
            if result.status == "success":
                presets_info = f"Found {result.data['total']} presets"
                if category:
                    presets_info += f" in category '{category}'"
                return presets_info, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", ""
                
        except Exception as e:
            logger.error(f"GUI list presets error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def get_preset_info_gui(self, preset_name: str) -> Tuple[str, str]:
        """GUI wrapper for getting preset info."""
        try:
            result = self.core.get_preset_info(preset_name)
            
            if result.status == "success":
                preset_data = result.data
                info = f"Preset: {preset_data['name']}, Category: {preset_data['category']}"
                info += f", Duration: {preset_data['duration']}s"
                return info, json.dumps(preset_data, indent=2)
            else:
                return f"Error: {result.error}", ""
                
        except Exception as e:
            logger.error(f"GUI get preset info error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def apply_preset_gui(self, preset_name: str, parameters_json: str = "") -> Tuple[str, str]:
        """GUI wrapper for applying timeline presets."""
        try:
            parameters = {}
            if parameters_json.strip():
                parameters = json.loads(parameters_json)
            
            result = self.core.apply_preset(preset_name, parameters)
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in parameters: {str(e)}", json.dumps({"error": f"Invalid JSON in parameters: {str(e)}"}, indent=2)
        except Exception as e:
            logger.error(f"GUI apply preset error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def prepare_render_gui(self, output_path: str, quality: str) -> Tuple[str, str]:
        """GUI wrapper for preparing renders."""
        try:
            result = self.core.prepare_render(output_path, quality)
            
            if result.status == "success":
                return result.message, json.dumps(result.data, indent=2)
            else:
                return f"Error: {result.error}", json.dumps({"error": result.error}, indent=2)
                
        except Exception as e:
            logger.error(f"GUI prepare render error: {e}")
            return f"Error: {str(e)}", json.dumps({"error": str(e)}, indent=2)
    
    def render_scene_gui(self, output_path: str, quality: str, preview: bool) -> Tuple[str, str, str]:
        """GUI wrapper for complete rendering."""
        try:
            result = self.core.render_scene(output_path, quality, preview=preview)
            
            if result.status == "success":
                output_info = f"Output file: {result.data.get('output_file', 'Unknown')}"
                logs = result.data.get('stdout', '') + '\n' + result.data.get('stderr', '')
                return result.message, output_info, logs
            else:
                logs = result.data.get('stdout', '') + '\n' + result.data.get('stderr', '') if result.data else ''
                return f"Error: {result.error}", "", logs
                
        except Exception as e:
            logger.error(f"GUI render error: {e}")
            return f"Error: {str(e)}", "", ""
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        with gr.Blocks(title="Manim Studio", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# Manim Studio - Animation Creation Interface")
            gr.Markdown("Create animations using a visual interface powered by shared features.")
            
            with gr.Tabs():
                # Scene Management Tab
                with gr.Tab("Scene Management"):
                    gr.Markdown("## Create and Manage Scenes")
                    
                    with gr.Row():
                        with gr.Column():
                            scene_name = gr.Textbox(label="Scene Name", placeholder="MyAwesomeScene")
                            scene_duration = gr.Number(label="Duration (seconds)", value=5.0, minimum=0.1)
                            scene_bg_color = gr.ColorPicker(label="Background Color", value="#000000")
                            
                        with gr.Column():
                            scene_width = gr.Number(label="Width", value=1920, precision=0)
                            scene_height = gr.Number(label="Height", value=1080, precision=0)
                            scene_fps = gr.Number(label="FPS", value=60, precision=0)
                    
                    create_scene_btn = gr.Button("Create Scene", variant="primary")
                    scene_status = gr.Textbox(label="Status", interactive=False)
                    scene_data = gr.JSON(label="Scene Data")
                    
                    create_scene_btn.click(
                        self.create_scene_gui,
                        inputs=[scene_name, scene_duration, scene_bg_color, scene_width, scene_height, scene_fps],
                        outputs=[scene_status, scene_data]
                    )
                    
                    with gr.Row():
                        list_scenes_btn = gr.Button("List Scenes")
                        get_scene_name = gr.Textbox(label="Scene Name (empty for current)", placeholder="")
                        get_scene_btn = gr.Button("Get Scene Info")
                    
                    scenes_status = gr.Textbox(label="Scenes Status", interactive=False)
                    scenes_data = gr.JSON(label="Scenes Data")
                    
                    list_scenes_btn.click(self.list_scenes_gui, outputs=[scenes_status, scenes_data])
                    get_scene_btn.click(self.get_scene_gui, inputs=[get_scene_name], outputs=[scenes_status, scenes_data])
                
                # Objects Tab
                with gr.Tab("Add Objects"):
                    gr.Markdown("## Add Text and Shapes")
                    
                    with gr.Tab("Text"):
                        with gr.Row():
                            with gr.Column():
                                text_id = gr.Textbox(label="Text ID", placeholder="title1")
                                text_content = gr.Textbox(label="Text Content", placeholder="Hello World!")
                                text_color = gr.ColorPicker(label="Text Color", value="#FFFFFF")
                                
                            with gr.Column():
                                text_x = gr.Number(label="X Position", value=0)
                                text_y = gr.Number(label="Y Position", value=0)
                                text_z = gr.Number(label="Z Position", value=0)
                                text_font_size = gr.Number(label="Font Size", value=48, precision=0)
                                text_font = gr.Textbox(label="Font", value="Arial")
                        
                        add_text_btn = gr.Button("Add Text", variant="primary")
                        text_status = gr.Textbox(label="Status", interactive=False)
                        text_data = gr.JSON(label="Text Data")
                        
                        add_text_btn.click(
                            self.add_text_gui,
                            inputs=[text_id, text_content, text_color, text_x, text_y, text_z, text_font_size, text_font],
                            outputs=[text_status, text_data]
                        )
                    
                    with gr.Tab("Shapes"):
                        with gr.Row():
                            with gr.Column():
                                shape_id = gr.Textbox(label="Shape ID", placeholder="circle1")
                                shape_type = gr.Dropdown(
                                    label="Shape Type",
                                    choices=[shape.value for shape in ShapeType],
                                    value="circle"
                                )
                                shape_color = gr.ColorPicker(label="Shape Color", value="#FFFFFF")
                                
                            with gr.Column():
                                shape_size = gr.Number(label="Size", value=1.0, minimum=0.1)
                                shape_x = gr.Number(label="X Position", value=0)
                                shape_y = gr.Number(label="Y Position", value=0)
                                shape_z = gr.Number(label="Z Position", value=0)
                        
                        add_shape_btn = gr.Button("Add Shape", variant="primary")
                        shape_status = gr.Textbox(label="Status", interactive=False)
                        shape_data = gr.JSON(label="Shape Data")
                        
                        add_shape_btn.click(
                            self.add_shape_gui,
                            inputs=[shape_id, shape_type, shape_color, shape_size, shape_x, shape_y, shape_z],
                            outputs=[shape_status, shape_data]
                        )
                
                # Animations Tab
                with gr.Tab("Animations"):
                    gr.Markdown("## Add Animations to Objects")
                    
                    with gr.Row():
                        with gr.Column():
                            anim_target = gr.Textbox(label="Target Object ID", placeholder="title1")
                            anim_type = gr.Dropdown(
                                label="Animation Type",
                                choices=[anim.value for anim in AnimationType],
                                value="fadein"
                            )
                            anim_start = gr.Number(label="Start Time (seconds)", value=0, minimum=0)
                            
                        with gr.Column():
                            anim_duration = gr.Number(label="Duration (seconds)", value=1.0, minimum=0.1)
                            anim_easing = gr.Dropdown(
                                label="Easing",
                                choices=["linear", "ease_in", "ease_out", "ease_in_out", "bounce", "elastic", "back", "expo"],
                                value="ease_in_out"
                            )
                            anim_properties = gr.Textbox(
                                label="Properties (JSON)",
                                placeholder='{"position": [1, 0, 0], "scale": 1.5}',
                                lines=3
                            )
                    
                    add_animation_btn = gr.Button("Add Animation", variant="primary")
                    anim_status = gr.Textbox(label="Status", interactive=False)
                    anim_data = gr.JSON(label="Animation Data")
                    
                    add_animation_btn.click(
                        self.add_animation_gui,
                        inputs=[anim_target, anim_type, anim_start, anim_duration, anim_easing, anim_properties],
                        outputs=[anim_status, anim_data]
                    )
                
                # Timeline Presets Tab
                with gr.Tab("Timeline Presets"):
                    gr.Markdown("## Apply Timeline Presets")
                    
                    with gr.Row():
                        preset_category = gr.Textbox(label="Category Filter (optional)", placeholder="intro")
                        list_presets_btn = gr.Button("List Presets")
                    
                    presets_status = gr.Textbox(label="Status", interactive=False)
                    presets_data = gr.JSON(label="Presets Data")
                    
                    list_presets_btn.click(
                        self.list_presets_gui,
                        inputs=[preset_category],
                        outputs=[presets_status, presets_data]
                    )
                    
                    with gr.Row():
                        preset_name = gr.Textbox(label="Preset Name", placeholder="fade_in_out")
                        get_preset_btn = gr.Button("Get Preset Info")
                    
                    preset_info_status = gr.Textbox(label="Preset Info Status", interactive=False)
                    preset_info_data = gr.JSON(label="Preset Info")
                    
                    get_preset_btn.click(
                        self.get_preset_info_gui,
                        inputs=[preset_name],
                        outputs=[preset_info_status, preset_info_data]
                    )
                    
                    with gr.Row():
                        apply_preset_name = gr.Textbox(label="Preset to Apply", placeholder="fade_in_out")
                        apply_preset_params = gr.Textbox(
                            label="Parameters (JSON, optional)",
                            placeholder='{"duration": 3.0}',
                            lines=2
                        )
                        apply_preset_btn = gr.Button("Apply Preset", variant="primary")
                    
                    apply_status = gr.Textbox(label="Apply Status", interactive=False)
                    apply_data = gr.JSON(label="Apply Result")
                    
                    apply_preset_btn.click(
                        self.apply_preset_gui,
                        inputs=[apply_preset_name, apply_preset_params],
                        outputs=[apply_status, apply_data]
                    )
                
                # Rendering Tab
                with gr.Tab("Rendering"):
                    gr.Markdown("## Render Scene")
                    
                    with gr.Row():
                        with gr.Column():
                            render_output = gr.Textbox(label="Output Path", placeholder="/path/to/output.mp4", value="output.mp4")
                            render_quality = gr.Dropdown(
                                label="Quality",
                                choices=[quality.value for quality in RenderQuality],
                                value="high"
                            )
                            render_preview = gr.Checkbox(label="Open preview after rendering", value=True)
                        
                        with gr.Column():
                            prepare_render_btn = gr.Button("Prepare Render Only", variant="secondary")
                            render_btn = gr.Button("Render Scene", variant="primary", size="lg")
                    
                    # Prepare render outputs
                    with gr.Group(visible=True) as prepare_group:
                        render_status = gr.Textbox(label="Prepare Status", interactive=False)
                        render_data = gr.JSON(label="Render Configuration")
                    
                    # Render outputs
                    with gr.Group(visible=True) as render_group:
                        render_result = gr.Textbox(label="Render Result", interactive=False)
                        render_output_info = gr.Textbox(label="Output File", interactive=False)
                        render_logs = gr.Textbox(label="Render Logs", lines=10, max_lines=20, interactive=False)
                    
                    prepare_render_btn.click(
                        self.prepare_render_gui,
                        inputs=[render_output, render_quality],
                        outputs=[render_status, render_data]
                    )
                    
                    render_btn.click(
                        self.render_scene_gui,
                        inputs=[render_output, render_quality, render_preview],
                        outputs=[render_result, render_output_info, render_logs]
                    )
                    
                    gr.Markdown("""
                    ### Instructions:
                    1. Click "Render Scene" to automatically render your animation
                    2. Use "Prepare Render Only" if you just want to generate the script
                    3. Rendered videos will be saved to the user-data directory
                    4. Check the render logs for progress and any errors
                    """)
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        interface.launch(**kwargs)


def main():
    """Main entry point for GUI interface."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Manim Studio GUI Interface...")
    
    gui = GUIInterface()
    gui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )


if __name__ == "__main__":
    main()