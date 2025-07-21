"""
Shared Manim configuration to ensure consistent media output directory.
Import this module before any Manim imports to override the default media directory.
"""
import os
from pathlib import Path

# Set the media directory before importing Manim
os.environ["MANIM_MEDIA_DIR"] = str(Path("user-data").absolute())

# Now import Manim config and set it directly as well
from manim import config

# Ensure media_dir points to user-data
config.media_dir = Path("user-data").absolute()

# Additional configuration to ensure subdirectories are created properly
config.video_dir = "{media_dir}/videos"
config.images_dir = "{media_dir}/images"
config.text_dir = "{media_dir}/texts"
config.tex_dir = "{media_dir}/Tex"
config.partial_movie_dir = "{media_dir}/partial_movie_files"

# Export config for other modules to use
__all__ = ["config"]