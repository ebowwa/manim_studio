#!/usr/bin/env python
"""Frame extraction utility for Manim animations.

This module provides functionality to extract frames from rendered Manim videos
at specified intervals or timestamps for analysis and debugging.
"""

import cv2
import os
import numpy as np
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FrameExtractionConfig:
    """Configuration for frame extraction."""
    frame_interval: int = 15  # Extract every N frames
    timestamp_list: Optional[List[float]] = None  # Extract at specific timestamps
    output_format: str = "jpg"  # Output format (jpg, png)
    quality: int = 95  # JPEG quality (0-100)
    resize_factor: Optional[float] = None  # Resize frames by this factor
    max_frames: Optional[int] = None  # Maximum number of frames to extract


class FrameExtractor:
    """Extract frames from video files."""
    
    def __init__(self, config: Optional[FrameExtractionConfig] = None):
        """Initialize the frame extractor.
        
        Args:
            config: Configuration for frame extraction
        """
        self.config = config or FrameExtractionConfig()
        
    def extract_frames(
        self, 
        video_path: Union[str, Path], 
        output_dir: Union[str, Path],
        prefix: str = "frame"
    ) -> List[Dict[str, Union[str, float, int]]]:
        """Extract frames from a video file.
        
        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted frames
            prefix: Prefix for output filenames
            
        Returns:
            List of dictionaries containing frame information
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
            
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video properties: FPS={fps}, Total frames={total_frames}, Duration={duration:.2f}s")
            
            # Extract frames
            extracted_frames = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Check if we should extract this frame
                should_extract = False
                timestamp = frame_count / fps if fps > 0 else 0
                
                if self.config.timestamp_list:
                    # Extract at specific timestamps
                    for ts in self.config.timestamp_list:
                        if abs(timestamp - ts) < (0.5 / fps):  # Within half a frame
                            should_extract = True
                            break
                else:
                    # Extract at intervals
                    if frame_count % self.config.frame_interval == 0:
                        should_extract = True
                        
                if should_extract:
                    # Check max frames limit
                    if self.config.max_frames and extracted_count >= self.config.max_frames:
                        break
                        
                    # Process frame
                    processed_frame = self._process_frame(frame)
                    
                    # Save frame
                    filename = f"{prefix}_{extracted_count:04d}_at_{timestamp:.2f}s.{self.config.output_format}"
                    filepath = output_dir / filename
                    
                    self._save_frame(processed_frame, filepath)
                    
                    extracted_frames.append({
                        "filename": filename,
                        "filepath": str(filepath),
                        "frame_number": frame_count,
                        "timestamp": timestamp,
                        "width": processed_frame.shape[1],
                        "height": processed_frame.shape[0]
                    })
                    
                    extracted_count += 1
                    logger.debug(f"Extracted frame {extracted_count}: {filename}")
                    
                frame_count += 1
                
            logger.info(f"Extracted {extracted_count} frames from {video_path}")
            return extracted_frames
            
        finally:
            cap.release()
            
    def extract_keyframes(
        self,
        video_path: Union[str, Path],
        output_dir: Union[str, Path],
        threshold: float = 30.0,
        prefix: str = "keyframe"
    ) -> List[Dict[str, Union[str, float, int]]]:
        """Extract keyframes based on scene changes.
        
        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted frames
            threshold: Threshold for scene change detection
            prefix: Prefix for output filenames
            
        Returns:
            List of dictionaries containing frame information
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
            
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            extracted_frames = []
            frame_count = 0
            extracted_count = 0
            prev_frame = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate difference
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff)
                    
                    # Check if this is a keyframe
                    if mean_diff > threshold:
                        timestamp = frame_count / fps if fps > 0 else 0
                        
                        # Process and save frame
                        processed_frame = self._process_frame(frame)
                        filename = f"{prefix}_{extracted_count:04d}_at_{timestamp:.2f}s.{self.config.output_format}"
                        filepath = output_dir / filename
                        
                        self._save_frame(processed_frame, filepath)
                        
                        extracted_frames.append({
                            "filename": filename,
                            "filepath": str(filepath),
                            "frame_number": frame_count,
                            "timestamp": timestamp,
                            "width": processed_frame.shape[1],
                            "height": processed_frame.shape[0],
                            "scene_change_score": mean_diff
                        })
                        
                        extracted_count += 1
                        logger.debug(f"Extracted keyframe {extracted_count}: {filename} (diff={mean_diff:.2f})")
                        
                prev_frame = gray
                frame_count += 1
                
            logger.info(f"Extracted {extracted_count} keyframes from {video_path}")
            return extracted_frames
            
        finally:
            cap.release()
            
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a frame before saving.
        
        Args:
            frame: Input frame
            
        Returns:
            Processed frame
        """
        # Resize if needed
        if self.config.resize_factor and self.config.resize_factor != 1.0:
            height, width = frame.shape[:2]
            new_width = int(width * self.config.resize_factor)
            new_height = int(height * self.config.resize_factor)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
        return frame
        
    def _save_frame(self, frame: np.ndarray, filepath: Path) -> None:
        """Save a frame to disk.
        
        Args:
            frame: Frame to save
            filepath: Output filepath
        """
        if self.config.output_format.lower() == "jpg":
            cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, self.config.quality])
        elif self.config.output_format.lower() == "png":
            cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        else:
            cv2.imwrite(str(filepath), frame)
            
    def create_frame_grid(
        self,
        frames_dir: Union[str, Path],
        output_path: Union[str, Path],
        grid_size: Tuple[int, int] = (4, 4),
        frame_size: Tuple[int, int] = (320, 240)
    ) -> None:
        """Create a grid visualization of extracted frames.
        
        Args:
            frames_dir: Directory containing extracted frames
            output_path: Path to save the grid image
            grid_size: Grid dimensions (cols, rows)
            frame_size: Size of each frame in the grid
        """
        frames_dir = Path(frames_dir)
        output_path = Path(output_path)
        
        # Get list of frame files
        frame_files = sorted(frames_dir.glob(f"*.{self.config.output_format}"))
        if not frame_files:
            logger.warning(f"No frames found in {frames_dir}")
            return
            
        cols, rows = grid_size
        grid_width = cols * frame_size[0]
        grid_height = rows * frame_size[1]
        
        # Create grid image
        grid = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
        
        for idx, frame_file in enumerate(frame_files[:cols * rows]):
            # Read and resize frame
            frame = cv2.imread(str(frame_file))
            if frame is None:
                continue
                
            frame = cv2.resize(frame, frame_size)
            
            # Calculate position in grid
            row = idx // cols
            col = idx % cols
            y = row * frame_size[1]
            x = col * frame_size[0]
            
            # Place frame in grid
            grid[y:y + frame_size[1], x:x + frame_size[0]] = frame
            
        # Save grid
        cv2.imwrite(str(output_path), grid)
        logger.info(f"Created frame grid: {output_path}")


def extract_frames_from_video(
    video_path: Union[str, Path],
    output_dir: Union[str, Path],
    frame_interval: int = 30,
    max_frames: Optional[int] = None
) -> List[Dict[str, Union[str, float, int]]]:
    """Convenience function to extract frames from a video.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        frame_interval: Extract every N frames
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of extracted frame information
    """
    config = FrameExtractionConfig(
        frame_interval=frame_interval,
        max_frames=max_frames
    )
    extractor = FrameExtractor(config)
    return extractor.extract_frames(video_path, output_dir)