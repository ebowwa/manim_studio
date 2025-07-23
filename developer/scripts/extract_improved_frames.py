#!/usr/bin/env python
"""Extract frames from improved skull video."""

import cv2
import os

video_path = "../../user-data/videos/1080p60/ImprovedSkullShowcase.mp4"
output_dir = "../../user-data/images/improved_skull_frames"

os.makedirs(output_dir, exist_ok=True)

vidcap = cv2.VideoCapture(video_path)
fps = vidcap.get(cv2.CAP_PROP_FPS)

# Extract key frames at specific times
key_times = [
    2.0,   # Realistic skull intro
    4.0,   # Skull rotation
    8.0,   # All skull styles
    12.0,  # Particle formation
    16.0,  # Animated effects
    20.0   # Finale
]

for time_sec in key_times:
    frame_number = int(time_sec * fps)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, image = vidcap.read()
    
    if success:
        filename = f"improved_frame_at_{time_sec:.1f}s.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, image)
        print(f"Saved {filename}")

vidcap.release()
print(f"\nExtracted {len(key_times)} key frames to {output_dir}")