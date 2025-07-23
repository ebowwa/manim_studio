#!/usr/bin/env python3
"""Simple 3D camera test without complex imports"""

from manim import *
import numpy as np


class Simple3DTest(ThreeDScene):
    def construct(self):
        # Set initial camera position
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        
        # Create title
        title = Text("3D Camera Test", font_size=60)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-3, 3, 1]
        )
        axes.set_color(GRAY)
        
        # Create a cube
        cube = Cube(side_length=2, fill_opacity=0.8)
        cube.set_color(BLUE)
        
        # Create spheres
        spheres = VGroup()
        colors = [RED, GREEN, YELLOW]
        positions = [[3, 0, 0], [-3, 0, 0], [0, 3, 0]]
        
        for color, pos in zip(colors, positions):
            sphere = Sphere(radius=0.5)
            sphere.set_color(color)
            sphere.move_to(pos)
            spheres.add(sphere)
        
        # Add objects to scene
        self.play(Create(axes), run_time=2)
        self.play(Create(cube), run_time=1.5)
        self.play(FadeIn(spheres), run_time=1.5)
        
        # Add rotation to cube
        cube.add_updater(lambda m, dt: m.rotate(dt, axis=np.array([1, 1, 1])))
        
        # Camera movement 1: Orbit
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        # Camera movement 2: Different angles using move_camera
        self.move_camera(
            phi=30 * DEGREES,
            theta=60 * DEGREES,
            run_time=2
        )
        self.wait(1)
        
        self.move_camera(
            phi=80 * DEGREES,
            theta=-30 * DEGREES,
            run_time=2
        )
        self.wait(1)
        
        # Final shot
        self.move_camera(
            phi=45 * DEGREES,
            theta=45 * DEGREES,
            run_time=2
        )
        
        self.wait(2)


if __name__ == "__main__":
    # Test render
    scene = Simple3DTest()
    scene.render()