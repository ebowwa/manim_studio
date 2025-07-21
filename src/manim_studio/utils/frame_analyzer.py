#!/usr/bin/env python
"""Frame analysis utility for visual inspection of Manim animations.

This module provides functionality to analyze extracted frames and generate
visual reports for debugging and quality assessment.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FrameAnalysisResult:
    """Results from frame analysis."""
    frame_path: str
    timestamp: float
    brightness: float
    contrast: float
    sharpness: float
    dominant_colors: List[Tuple[int, int, int]]
    objects_detected: int
    motion_score: float
    quality_score: float
    issues: List[str]


class FrameAnalyzer:
    """Analyze extracted frames for quality and content."""
    
    def __init__(self):
        """Initialize the frame analyzer."""
        self.prev_frame = None
        
    def analyze_frame(self, frame_path: Union[str, Path], timestamp: float = 0.0) -> FrameAnalysisResult:
        """Analyze a single frame.
        
        Args:
            frame_path: Path to the frame image
            timestamp: Timestamp of the frame in the video
            
        Returns:
            Analysis results
        """
        frame_path = Path(frame_path)
        if not frame_path.exists():
            raise FileNotFoundError(f"Frame not found: {frame_path}")
            
        # Read frame
        frame = cv2.imread(str(frame_path))
        if frame is None:
            raise ValueError(f"Failed to read frame: {frame_path}")
            
        # Perform analysis
        brightness = self._calculate_brightness(frame)
        contrast = self._calculate_contrast(frame)
        sharpness = self._calculate_sharpness(frame)
        dominant_colors = self._get_dominant_colors(frame)
        objects_detected = self._detect_objects(frame)
        motion_score = self._calculate_motion_score(frame)
        
        # Check for issues
        issues = self._detect_issues(frame, brightness, contrast, sharpness)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            brightness, contrast, sharpness, issues
        )
        
        # Store current frame for motion analysis
        self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        return FrameAnalysisResult(
            frame_path=str(frame_path),
            timestamp=timestamp,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            dominant_colors=dominant_colors,
            objects_detected=objects_detected,
            motion_score=motion_score,
            quality_score=quality_score,
            issues=issues
        )
        
    def analyze_frame_sequence(
        self, 
        frames_dir: Union[str, Path],
        pattern: str = "*.jpg"
    ) -> List[FrameAnalysisResult]:
        """Analyze a sequence of frames.
        
        Args:
            frames_dir: Directory containing frames
            pattern: Glob pattern for frame files
            
        Returns:
            List of analysis results
        """
        frames_dir = Path(frames_dir)
        frame_files = sorted(frames_dir.glob(pattern))
        
        results = []
        for frame_file in frame_files:
            # Extract timestamp from filename if available
            timestamp = self._extract_timestamp_from_filename(frame_file.name)
            
            try:
                result = self.analyze_frame(frame_file, timestamp)
                results.append(result)
                logger.debug(f"Analyzed frame: {frame_file.name}")
            except Exception as e:
                logger.error(f"Failed to analyze frame {frame_file}: {e}")
                
        return results
        
    def generate_analysis_report(
        self,
        results: List[FrameAnalysisResult],
        output_path: Union[str, Path],
        include_thumbnails: bool = True
    ) -> None:
        """Generate a visual analysis report.
        
        Args:
            results: List of frame analysis results
            output_path: Path to save the report (PDF)
            include_thumbnails: Whether to include frame thumbnails
        """
        output_path = Path(output_path)
        
        with PdfPages(str(output_path)) as pdf:
            # Overview page
            self._create_overview_page(results, pdf)
            
            # Quality metrics over time
            self._create_metrics_page(results, pdf)
            
            # Individual frame analysis
            if include_thumbnails:
                self._create_frame_pages(results, pdf)
                
            # Issues summary
            self._create_issues_page(results, pdf)
            
        logger.info(f"Generated analysis report: {output_path}")
        
    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """Calculate average brightness of frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) / 255.0
        
    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """Calculate contrast of frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.std(gray) / 255.0
        
    def _calculate_sharpness(self, frame: np.ndarray) -> float:
        """Calculate sharpness using Laplacian variance."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return np.var(laplacian) / 1000.0  # Normalize
        
    def _get_dominant_colors(self, frame: np.ndarray, n_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Get dominant colors in frame."""
        # Reshape frame to list of pixels
        pixels = frame.reshape(-1, 3)
        
        # Simple color quantization without sklearn dependency
        # Use histogram-based approach instead of k-means
        hist_b = np.histogram(pixels[:, 0], bins=32, range=(0, 256))[0]
        hist_g = np.histogram(pixels[:, 1], bins=32, range=(0, 256))[0]
        hist_r = np.histogram(pixels[:, 2], bins=32, range=(0, 256))[0]
        
        # Find peaks in histograms
        dominant_colors = []
        for hist, channel_idx in [(hist_b, 0), (hist_g, 1), (hist_r, 2)]:
            peaks = np.argsort(hist)[-n_colors:]
            for peak in peaks[:1]:  # Take top peak per channel
                color = [128, 128, 128]  # Default gray
                color[channel_idx] = int(peak * 8)  # Convert bin to color value
                dominant_colors.append(tuple(color))
        
        # Add most common actual colors
        if len(dominant_colors) < n_colors:
            # Sample random pixels as additional colors
            sample_size = min(1000, len(pixels))
            indices = np.random.choice(len(pixels), sample_size, replace=False)
            sampled_pixels = pixels[indices]
            unique_colors, counts = np.unique(sampled_pixels, axis=0, return_counts=True)
            top_indices = np.argsort(counts)[-n_colors:]
            for idx in top_indices:
                if len(dominant_colors) < n_colors:
                    dominant_colors.append(tuple(unique_colors[idx]))
        
        return dominant_colors[:n_colors]
        
    def _detect_objects(self, frame: np.ndarray) -> int:
        """Detect number of distinct objects/regions in frame."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours
        min_area = frame.shape[0] * frame.shape[1] * 0.001  # 0.1% of frame
        significant_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        return len(significant_contours)
        
    def _calculate_motion_score(self, frame: np.ndarray) -> float:
        """Calculate motion score compared to previous frame."""
        if self.prev_frame is None:
            return 0.0
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Ensure frames have same dimensions
        if gray.shape != self.prev_frame.shape:
            return 0.0
            
        # Calculate difference
        diff = cv2.absdiff(self.prev_frame, gray)
        motion_score = np.mean(diff) / 255.0
        
        return motion_score
        
    def _detect_issues(
        self, 
        frame: np.ndarray, 
        brightness: float, 
        contrast: float, 
        sharpness: float
    ) -> List[str]:
        """Detect potential issues in frame."""
        issues = []
        
        # Check brightness
        if brightness < 0.1:
            issues.append("Too dark")
        elif brightness > 0.9:
            issues.append("Too bright")
            
        # Check contrast
        if contrast < 0.1:
            issues.append("Low contrast")
            
        # Check sharpness
        if sharpness < 5.0:
            issues.append("Blurry")
            
        # Check for black frames
        if np.mean(frame) < 10:
            issues.append("Black frame")
            
        # Check for artifacts
        if self._has_compression_artifacts(frame):
            issues.append("Compression artifacts")
            
        return issues
        
    def _has_compression_artifacts(self, frame: np.ndarray) -> bool:
        """Check for compression artifacts."""
        # Simple check for blocky patterns
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for regular grid patterns
        horizontal = np.sum(edges, axis=1)
        vertical = np.sum(edges, axis=0)
        
        # Check for periodic peaks
        h_fft = np.abs(np.fft.fft(horizontal))
        v_fft = np.abs(np.fft.fft(vertical))
        
        # Simple heuristic: check for strong frequency components
        h_peaks = len(np.where(h_fft > np.mean(h_fft) * 5)[0])
        v_peaks = len(np.where(v_fft > np.mean(v_fft) * 5)[0])
        
        return h_peaks > 10 or v_peaks > 10
        
    def _calculate_quality_score(
        self,
        brightness: float,
        contrast: float,
        sharpness: float,
        issues: List[str]
    ) -> float:
        """Calculate overall quality score."""
        score = 100.0
        
        # Brightness score (optimal around 0.5)
        brightness_deviation = abs(brightness - 0.5) * 2
        score -= brightness_deviation * 20
        
        # Contrast score (higher is better, up to a point)
        if contrast < 0.2:
            score -= (0.2 - contrast) * 100
            
        # Sharpness score
        if sharpness < 10:
            score -= (10 - sharpness) * 2
            
        # Deduct for issues
        score -= len(issues) * 10
        
        return max(0, min(100, score))
        
    def _extract_timestamp_from_filename(self, filename: str) -> float:
        """Extract timestamp from filename."""
        # Try to extract timestamp from pattern like "frame_001_at_1.23s.jpg"
        import re
        match = re.search(r'at_(\d+\.?\d*)s', filename)
        if match:
            return float(match.group(1))
        return 0.0
        
    def _create_overview_page(self, results: List[FrameAnalysisResult], pdf: PdfPages) -> None:
        """Create overview page for report."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Frame Analysis Overview', fontsize=16)
        
        # Quality scores distribution
        quality_scores = [r.quality_score for r in results]
        ax1.hist(quality_scores, bins=20, edgecolor='black')
        ax1.set_xlabel('Quality Score')
        ax1.set_ylabel('Number of Frames')
        ax1.set_title('Quality Score Distribution')
        
        # Average metrics
        metrics = {
            'Brightness': np.mean([r.brightness for r in results]),
            'Contrast': np.mean([r.contrast for r in results]),
            'Sharpness': np.mean([r.sharpness for r in results]) / 10,  # Normalize
            'Motion': np.mean([r.motion_score for r in results])
        }
        ax2.bar(metrics.keys(), metrics.values())
        ax2.set_ylabel('Average Value')
        ax2.set_title('Average Metrics')
        ax2.set_ylim(0, 1)
        
        # Issues frequency
        all_issues = []
        for r in results:
            all_issues.extend(r.issues)
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
        if issue_counts:
            ax3.bar(issue_counts.keys(), issue_counts.values())
            ax3.set_xlabel('Issue Type')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Issues Found')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, 'No issues found', ha='center', va='center')
            ax3.set_title('Issues Found')
            
        # Summary stats
        summary_text = f"""
Total Frames Analyzed: {len(results)}
Average Quality Score: {np.mean(quality_scores):.1f}
Frames with Issues: {sum(1 for r in results if r.issues)}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        ax4.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_title('Summary')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)
        
    def _create_metrics_page(self, results: List[FrameAnalysisResult], pdf: PdfPages) -> None:
        """Create metrics over time page."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Metrics Over Time', fontsize=16)
        
        timestamps = [r.timestamp for r in results]
        
        # Quality score over time
        ax1.plot(timestamps, [r.quality_score for r in results], 'b-')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Quality Score')
        ax1.set_title('Quality Score')
        ax1.grid(True, alpha=0.3)
        
        # Brightness over time
        ax2.plot(timestamps, [r.brightness for r in results], 'g-')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Brightness')
        ax2.set_title('Brightness')
        ax2.grid(True, alpha=0.3)
        
        # Motion score over time
        ax3.plot(timestamps, [r.motion_score for r in results], 'r-')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Motion Score')
        ax3.set_title('Motion/Change Detection')
        ax3.grid(True, alpha=0.3)
        
        # Sharpness over time
        ax4.plot(timestamps, [r.sharpness for r in results], 'm-')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Sharpness')
        ax4.set_title('Sharpness')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)
        
    def _create_frame_pages(self, results: List[FrameAnalysisResult], pdf: PdfPages) -> None:
        """Create individual frame analysis pages."""
        # Limit to first 20 frames for brevity
        for i in range(0, min(len(results), 20), 4):
            fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
            fig.suptitle('Frame Analysis Details', fontsize=16)
            axes = axes.flatten()
            
            for j, ax in enumerate(axes):
                if i + j < len(results):
                    result = results[i + j]
                    
                    # Load and display frame
                    frame = cv2.imread(result.frame_path)
                    if frame is not None:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        ax.imshow(frame_rgb)
                        
                        # Add metrics text
                        info_text = f"Time: {result.timestamp:.2f}s\n"
                        info_text += f"Quality: {result.quality_score:.1f}\n"
                        if result.issues:
                            info_text += f"Issues: {', '.join(result.issues)}"
                            
                        ax.text(0.02, 0.98, info_text,
                               transform=ax.transAxes,
                               verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                               fontsize=8)
                    
                    ax.set_title(f"Frame at {result.timestamp:.2f}s")
                    ax.axis('off')
                else:
                    ax.axis('off')
                    
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
            
    def _create_issues_page(self, results: List[FrameAnalysisResult], pdf: PdfPages) -> None:
        """Create issues summary page."""
        fig, ax = plt.subplots(figsize=(11, 8.5))
        fig.suptitle('Issues Summary', fontsize=16)
        
        # Collect all frames with issues
        frames_with_issues = [(r.timestamp, r.issues) for r in results if r.issues]
        
        if frames_with_issues:
            # Create table data
            table_data = []
            for timestamp, issues in frames_with_issues[:30]:  # Limit to 30 rows
                table_data.append([f"{timestamp:.2f}s", ", ".join(issues)])
                
            # Create table
            table = ax.table(cellText=table_data,
                           colLabels=['Timestamp', 'Issues'],
                           cellLoc='left',
                           loc='center',
                           colWidths=[0.2, 0.8])
            
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            
            # Style the table
            for (i, j), cell in table.get_celld().items():
                if i == 0:
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        else:
            ax.text(0.5, 0.5, 'No issues found in analyzed frames',
                   ha='center', va='center', fontsize=14)
            
        ax.axis('off')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)


def analyze_video_frames(
    frames_dir: Union[str, Path],
    output_report: Union[str, Path],
    pattern: str = "*.jpg"
) -> List[FrameAnalysisResult]:
    """Convenience function to analyze frames and generate report.
    
    Args:
        frames_dir: Directory containing extracted frames
        output_report: Path to save analysis report
        pattern: Glob pattern for frame files
        
    Returns:
        List of analysis results
    """
    analyzer = FrameAnalyzer()
    results = analyzer.analyze_frame_sequence(frames_dir, pattern)
    analyzer.generate_analysis_report(results, output_report)
    return results