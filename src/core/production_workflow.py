"""Production workflow tools inspired by xiaoxiae's video creation process."""
import subprocess
import shutil
import os
import argparse
import re
from glob import glob
from typing import List, Tuple, Optional, Dict
import soundfile as sf
import pyloudnorm as pyln
from pathlib import Path


class VideoBuilder:
    """Automated video building and scene management."""
    
    def __init__(
        self,
        scenes_file: str = "scenes.py",
        video_dir: str = "video",
        quality: str = "k"  # m=720p, h=1080p, k=4K
    ):
        self.scenes_file = scenes_file
        self.video_dir = video_dir
        self.quality = quality
        self.quality_mapping = {
            "m": (1280, 720, 30),
            "h": (1920, 1080, 60),
            "k": (3840, 2160, 60),
        }
    
    def get_all_scenes(self) -> List[str]:
        """Extract all scene class names from the scenes file."""
        scenes = []
        
        with open(self.scenes_file, "r") as f:
            for line in f.read().splitlines():
                # Match class definitions that inherit from Scene
                if match := re.match(r"\s*class\s+(.+?)\(.*Scene\)\s*:", line):
                    scene_name = match.group(1)
                    # Skip test scenes
                    if "Test" not in scene_name:
                        scenes.append(scene_name)
        
        return scenes
    
    def render_scene(
        self,
        scene_name: str,
        transparent: bool = None,
        preview: bool = False
    ) -> None:
        """Render a single scene with specified quality."""
        w, h, fps = self.quality_mapping[self.quality]
        
        # Check for short-form video marker
        if os.path.isfile(".short"):
            w, h = h, w  # Swap for vertical format
        
        # Build manim command
        args = [
            "manim",
            self.scenes_file,
            scene_name,
            "--fps", str(fps),
            "-r", f"{w},{h}",
            "--disable_caching"
        ]
        
        # Auto-detect transparent scenes or use parameter
        if transparent or (transparent is None and scene_name.lower().startswith("transparent")):
            args.append("-t")
        
        if preview:
            args.append("-p")
        
        # Run manim
        process = subprocess.Popen(args)
        process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Build failed for scene {scene_name} with exit code {process.returncode}")
    
    def rename_partial_movies(self, scene_name: str) -> None:
        """Rename partial movie files to sequential numbers."""
        partial_file_path = os.path.join(self.video_dir, scene_name, "partial_movie_file_list.txt")
        
        if not os.path.exists(partial_file_path):
            print(f"WARNING: Partial movie file list for '{scene_name}' doesn't exist")
            return
        
        with open(partial_file_path) as f:
            lines = f.read().splitlines()
            
            # Skip first line (header)
            for i, video_line in enumerate(lines[1:], 1):
                # Extract file path from format: file 'path/to/file.mp4'
                match = re.match(r"file '(.+)'", video_line)
                if match:
                    original_path = match.group(1)
                    path, name = os.path.split(original_path)
                    ext = os.path.splitext(name)[1]
                    
                    # Rename to sequential number
                    new_path = os.path.join(path, f"{i}{ext}")
                    if os.path.exists(original_path):
                        os.rename(original_path, new_path)
        
        # Clean up
        os.remove(partial_file_path)
    
    def build_all_scenes(
        self,
        scenes: Optional[List[str]] = None,
        clean: bool = True
    ) -> None:
        """Build all or specified scenes."""
        if scenes is None:
            scenes = self.get_all_scenes()
            
            # Clean output directory when building all
            if clean and os.path.exists(self.video_dir):
                shutil.rmtree(self.video_dir)
        
        for scene in scenes:
            print(f"Building scene: {scene}")
            
            if clean:
                # Clean scene-specific files
                scene_folder = os.path.join(self.video_dir, scene)
                if os.path.exists(scene_folder):
                    shutil.rmtree(scene_folder)
                
                # Clean scene video files
                for ext in ["mp4", "mov"]:
                    scene_video = os.path.join(self.video_dir, f"{scene}.{ext}")
                    if os.path.exists(scene_video):
                        os.remove(scene_video)
            
            # Render and rename
            self.render_scene(scene)
            self.rename_partial_movies(scene)


class AudioNormalizer:
    """Normalize audio recordings for consistent volume."""
    
    def __init__(
        self,
        input_dir: str = "audio/raw",
        output_dir: str = "audio/normalized",
        target_loudness: float = -25.0  # LUFS
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_loudness = target_loudness
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def normalize_file(self, input_path: str, output_path: str) -> None:
        """Normalize a single audio file."""
        # Read audio
        data, rate = sf.read(input_path)
        
        # Measure loudness
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        
        # Normalize
        normalized_audio = pyln.normalize.loudness(
            data,
            loudness,
            self.target_loudness
        )
        
        # Write normalized audio
        sf.write(output_path, normalized_audio, rate)
    
    def normalize_all(self, pattern: str = "*.wav") -> None:
        """Normalize all audio files matching pattern."""
        input_pattern = os.path.join(self.input_dir, pattern)
        
        for input_path in glob(input_pattern):
            filename = os.path.basename(input_path)
            output_path = os.path.join(self.output_dir, filename)
            
            print(f"Normalizing: {filename}")
            self.normalize_file(input_path, output_path)


class SceneOrganizer:
    """Organize scenes and manage video project structure."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
    
    def create_video_project(
        self,
        name: str,
        video_type: str = "long"  # long or short
    ) -> None:
        """Create a new video project from template."""
        template_dir = self.project_root / f"00-template-{video_type}"
        new_dir = self.project_root / name
        
        if not template_dir.exists():
            raise ValueError(f"Template directory {template_dir} not found")
        
        if new_dir.exists():
            raise ValueError(f"Project {name} already exists")
        
        # Copy template
        shutil.copytree(template_dir, new_dir)
        
        # Create marker for short videos
        if video_type == "short":
            (new_dir / ".short").touch()
        
        print(f"Created new {video_type} video project: {name}")
    
    def get_project_info(self) -> Dict[str, Dict]:
        """Get information about all video projects."""
        projects = {}
        
        for project_dir in sorted(self.project_root.glob("[0-9][0-9]-*/")):
            info = {
                "name": project_dir.name,
                "has_script": (project_dir / "SCRIPT.md").exists(),
                "has_description": (project_dir / "DESCRIPTION.md").exists(),
                "has_scenes": (project_dir / "scenes.py").exists(),
                "is_short": (project_dir / ".short").exists(),
                "scene_count": 0
            }
            
            # Count scenes
            if info["has_scenes"]:
                builder = VideoBuilder(scenes_file=str(project_dir / "scenes.py"))
                info["scene_count"] = len(builder.get_all_scenes())
            
            projects[project_dir.name] = info
        
        return projects


class ProductionConfig:
    """Manage production configuration and settings."""
    
    def __init__(self, config_file: str = "manim.cfg"):
        self.config_file = config_file
        self.config = {
            "video_dir": "video",
            "partial_movie_dir": "{video_dir}/{scene_name}",
            "max_files_cached": "10000000000000"
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from manim.cfg."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                section = None
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        section = line[1:-1]
                    elif "=" in line and section == "CLI":
                        key, value = line.split("=", 1)
                        self.config[key.strip()] = value.strip()
    
    def save_config(self) -> None:
        """Save configuration to manim.cfg."""
        with open(self.config_file, "w") as f:
            f.write("[CLI]\n")
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
    
    def get(self, key: str, default: str = None) -> str:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        self.config[key] = value


# Command-line interface
def create_cli() -> argparse.ArgumentParser:
    """Create command-line interface for production tools."""
    parser = argparse.ArgumentParser(
        description="Manim production workflow tools"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build video scenes")
    build_parser.add_argument(
        "-s", "--scenes",
        nargs="*",
        help="Scene names to build (builds all if omitted)"
    )
    build_parser.add_argument(
        "-q", "--quality",
        choices=["m", "h", "k"],
        default="k",
        help="Video quality: m=720p, h=1080p, k=4K (default: k)"
    )
    build_parser.add_argument(
        "-r", "--rename-only",
        action="store_true",
        help="Only rename partial movies without rendering"
    )
    
    # Normalize command
    norm_parser = subparsers.add_parser("normalize", help="Normalize audio files")
    norm_parser.add_argument(
        "-i", "--input",
        default="audio/raw",
        help="Input directory (default: audio/raw)"
    )
    norm_parser.add_argument(
        "-o", "--output",
        default="audio/normalized",
        help="Output directory (default: audio/normalized)"
    )
    norm_parser.add_argument(
        "-l", "--loudness",
        type=float,
        default=-25.0,
        help="Target loudness in LUFS (default: -25.0)"
    )
    
    # Project command
    proj_parser = subparsers.add_parser("project", help="Manage video projects")
    proj_parser.add_argument(
        "action",
        choices=["create", "list"],
        help="Project action"
    )
    proj_parser.add_argument(
        "name",
        nargs="?",
        help="Project name (for create)"
    )
    proj_parser.add_argument(
        "-t", "--type",
        choices=["long", "short"],
        default="long",
        help="Video type (default: long)"
    )
    
    return parser