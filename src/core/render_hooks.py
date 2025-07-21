#!/usr/bin/env python
"""Render hooks for integrating frame extraction into the animation pipeline.

This module provides hooks that can be attached to the Manim rendering process
to automatically extract and analyze frames during or after rendering.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
import logging
import shutil
from datetime import datetime

from utils.frame_extractor import FrameExtractor, FrameExtractionConfig
from utils.frame_analyzer import FrameAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class RenderHookConfig:
    """Configuration for render hooks."""
    extract_frames: bool = False
    analyze_frames: bool = False
    frame_interval: int = 30
    keyframe_extraction: bool = False
    keyframe_threshold: float = 30.0
    output_dir: Optional[str] = None
    generate_report: bool = True
    report_format: str = "pdf"
    cleanup_temp_files: bool = True
    max_frames: Optional[int] = None


class RenderHooks:
    """Hooks for the Manim rendering pipeline."""
    
    def __init__(self, config: Optional[RenderHookConfig] = None):
        """Initialize render hooks.
        
        Args:
            config: Configuration for render hooks
        """
        self.config = config or RenderHookConfig()
        self.extractor = None
        self.analyzer = None
        self.extracted_frames: List[Dict[str, Any]] = []
        
        # Initialize components if needed
        if self.config.extract_frames:
            extraction_config = FrameExtractionConfig(
                frame_interval=self.config.frame_interval,
                max_frames=self.config.max_frames
            )
            self.extractor = FrameExtractor(extraction_config)
            
        if self.config.analyze_frames:
            self.analyzer = FrameAnalyzer()
            
    def post_render_hook(self, scene_name: str, video_path: str) -> Dict[str, Any]:
        """Hook to run after scene rendering is complete.
        
        Args:
            scene_name: Name of the rendered scene
            video_path: Path to the rendered video
            
        Returns:
            Dictionary containing results of post-processing
        """
        results = {
            'scene_name': scene_name,
            'video_path': video_path,
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.config.extract_frames:
            return results
            
        try:
            # Determine output directory
            if self.config.output_dir:
                output_dir = Path(self.config.output_dir)
            else:
                # Create directory next to video
                video_path_obj = Path(video_path)
                output_dir = video_path_obj.parent / f"{video_path_obj.stem}_frames"
                
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract frames
            logger.info(f"Extracting frames from {video_path}")
            
            if self.config.keyframe_extraction:
                self.extracted_frames = self.extractor.extract_keyframes(
                    video_path,
                    output_dir,
                    threshold=self.config.keyframe_threshold,
                    prefix=f"{scene_name}_keyframe"
                )
            else:
                self.extracted_frames = self.extractor.extract_frames(
                    video_path,
                    output_dir,
                    prefix=f"{scene_name}_frame"
                )
                
            results['extracted_frames'] = len(self.extracted_frames)
            results['frames_dir'] = str(output_dir)
            
            # Analyze frames if requested
            if self.config.analyze_frames and self.analyzer:
                logger.info("Analyzing extracted frames")
                
                analysis_results = []
                for frame_info in self.extracted_frames:
                    try:
                        analysis = self.analyzer.analyze_frame(
                            frame_info['filepath'],
                            frame_info['timestamp']
                        )
                        analysis_results.append(analysis)
                    except Exception as e:
                        logger.error(f"Failed to analyze frame {frame_info['filename']}: {e}")
                        
                results['analysis_count'] = len(analysis_results)
                
                # Generate report if requested
                if self.config.generate_report and analysis_results:
                    report_path = output_dir / f"{scene_name}_analysis.{self.config.report_format}"
                    logger.info(f"Generating analysis report: {report_path}")
                    
                    self.analyzer.generate_analysis_report(
                        analysis_results,
                        report_path,
                        include_thumbnails=True
                    )
                    
                    results['report_path'] = str(report_path)
                    
                    # Also create a frame grid visualization
                    grid_path = output_dir / f"{scene_name}_grid.jpg"
                    self.extractor.create_frame_grid(
                        output_dir,
                        grid_path,
                        grid_size=(4, 4)
                    )
                    results['grid_path'] = str(grid_path)
                    
            # Print summary
            self._print_summary(results)
            
        except Exception as e:
            logger.error(f"Error in post-render hook: {e}")
            results['error'] = str(e)
            
        return results
        
    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of the extraction/analysis results."""
        print("\n" + "="*60)
        print("⏺ Frame Extraction Complete")
        print("="*60)
        
        if 'extracted_frames' in results:
            print(f"  ⎿ Extracted {results['extracted_frames']} frames")
            
        if 'frames_dir' in results:
            print(f"  ⎿ Frames saved to: {results['frames_dir']}")
            
        if 'analysis_count' in results:
            print(f"  ⎿ Analyzed {results['analysis_count']} frames")
            
        if 'report_path' in results:
            print(f"  ⎿ Analysis report: {results['report_path']}")
            
        if 'grid_path' in results:
            print(f"  ⎿ Frame grid: {results['grid_path']}")
            
        print("="*60 + "\n")
        
    def register_with_scene(self, scene_class: type) -> type:
        """Register hooks with a scene class.
        
        Args:
            scene_class: The scene class to register with
            
        Returns:
            Modified scene class with hooks
        """
        original_render = scene_class.render
        hooks = self
        
        def render_with_hooks(self, *args, **kwargs):
            """Wrapped render method with hooks."""
            # Call original render
            result = original_render(*args, **kwargs)
            
            # Get output file path
            output_file = self.renderer.file_writer.movie_file_path
            if output_file and os.path.exists(output_file):
                # Run post-render hook
                hooks.post_render_hook(
                    scene_name=self.__class__.__name__,
                    video_path=output_file
                )
                
            return result
            
        scene_class.render = render_with_hooks
        return scene_class


class FrameExtractionMixin:
    """Mixin class to add frame extraction capabilities to Manim scenes."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mixin."""
        super().__init__(*args, **kwargs)
        self.frame_extraction_config = RenderHookConfig()
        self._render_hooks = None
        
    def enable_frame_extraction(
        self,
        frame_interval: int = 30,
        analyze: bool = True,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> None:
        """Enable frame extraction for this scene.
        
        Args:
            frame_interval: Extract every N frames
            analyze: Whether to analyze extracted frames
            output_dir: Directory to save frames
            **kwargs: Additional configuration options
        """
        self.frame_extraction_config = RenderHookConfig(
            extract_frames=True,
            analyze_frames=analyze,
            frame_interval=frame_interval,
            output_dir=output_dir,
            **kwargs
        )
        
        # Create render hooks
        self._render_hooks = RenderHooks(self.frame_extraction_config)
        
    def render(self, *args, **kwargs):
        """Override render to include frame extraction."""
        # Call parent render
        result = super().render(*args, **kwargs)
        
        # Run frame extraction if enabled
        if self._render_hooks and self.frame_extraction_config.extract_frames:
            output_file = self.renderer.file_writer.movie_file_path
            if output_file and os.path.exists(output_file):
                self._render_hooks.post_render_hook(
                    scene_name=self.__class__.__name__,
                    video_path=output_file
                )
                
        return result


def create_extraction_scene(base_scene: type) -> type:
    """Create a scene class with frame extraction capabilities.
    
    Args:
        base_scene: Base scene class to extend
        
    Returns:
        Extended scene class with frame extraction
    """
    class ExtractedScene(FrameExtractionMixin, base_scene):
        """Scene with frame extraction capabilities."""
        pass
        
    ExtractedScene.__name__ = f"{base_scene.__name__}WithExtraction"
    ExtractedScene.__doc__ = f"{base_scene.__doc__}\n\nWith frame extraction capabilities."
    
    return ExtractedScene


# Convenience functions for quick setup
def auto_extract_frames(scene_class: type, **config_kwargs) -> type:
    """Automatically add frame extraction to a scene class.
    
    Args:
        scene_class: Scene class to modify
        **config_kwargs: Configuration options for extraction
        
    Returns:
        Modified scene class
    """
    config = RenderHookConfig(extract_frames=True, **config_kwargs)
    hooks = RenderHooks(config)
    return hooks.register_with_scene(scene_class)