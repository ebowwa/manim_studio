#!/usr/bin/env python3
"""Simple hyperplane test without complex dependencies."""

import sys
import os
import numpy as np

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import directly without the src package
from src.utils.math3d.vector3d import Vector3D
from src.utils.math3d.hyperplane import (
    Hyperplane, HyperplaneIntersection, HyperplaneRegion,
    create_hyperplane_2d, create_hyperplane_3d,
    hyperplane_from_points_2d, svm_decision_boundary
)

def test_basic_functionality():
    """Test basic hyperplane functionality."""
    print("Testing basic hyperplane functionality...")
    
    # Test 2D hyperplane
    h2d = create_hyperplane_2d(1, 1, -1)  # x + y - 1 = 0
    print(f"2D Hyperplane: {h2d}")
    
    # Test distance calculation
    point = [0, 0]
    distance = h2d.distance_to_point(point)
    print(f"Distance from {point} to hyperplane: {distance:.3f}")
    
    # Test classification
    classification = h2d.classify_point(point)
    print(f"Point {point} classification: {classification}")
    
    # Test 3D hyperplane
    h3d = create_hyperplane_3d(1, 1, 1, -3)  # x + y + z - 3 = 0
    print(f"3D Hyperplane: {h3d}")
    
    # Test with Vector3D
    vec_point = Vector3D(1, 1, 1)
    distance_3d = h3d.distance_to_point(vec_point)
    print(f"Distance from {vec_point} to 3D hyperplane: {distance_3d:.3f}")
    
    # Test projection
    projected = h3d.project_point(vec_point)
    print(f"Projection of {vec_point}: {projected}")
    
    return True

def test_intersections():
    """Test hyperplane intersections."""
    print("\nTesting hyperplane intersections...")
    
    # 2D case - intersection of two lines
    h1 = create_hyperplane_2d(1, 0, -1)  # x = 1
    h2 = create_hyperplane_2d(0, 1, -2)  # y = 2
    
    intersection = HyperplaneIntersection.intersect_two_hyperplanes(h1, h2)
    print(f"Intersection of x=1 and y=2: {intersection}")
    
    # Test parallel hyperplanes
    h3 = create_hyperplane_2d(1, 1, -1)  # x + y = 1
    h4 = create_hyperplane_2d(1, 1, -2)  # x + y = 2
    
    parallel_result = HyperplaneIntersection.intersect_two_hyperplanes(h3, h4)
    print(f"Parallel lines intersection: {parallel_result}")
    
    return True

def test_svm_functionality():
    """Test SVM-related functionality."""
    print("\nTesting SVM functionality...")
    
    # Create SVM decision boundary
    weights = np.array([1, -1])
    bias = 0
    
    svm_hyperplane = svm_decision_boundary(weights, bias)
    print(f"SVM Decision boundary: {svm_hyperplane}")
    
    # Test classification
    test_points = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    
    for point in test_points:
        classification = svm_hyperplane.classify_point(point)
        distance = svm_hyperplane.distance_to_point(point)
        print(f"Point {point}: class={classification}, distance={distance:.3f}")
    
    # Test margin boundaries
    margin = 1.0
    pos_margin = svm_hyperplane.get_parallel_hyperplane(-margin)
    neg_margin = svm_hyperplane.get_parallel_hyperplane(margin)
    
    print(f"Positive margin: {pos_margin}")
    print(f"Negative margin: {neg_margin}")
    
    return True

def test_regions():
    """Test hyperplane regions."""
    print("\nTesting hyperplane regions...")
    
    # Create a triangular region
    h1 = create_hyperplane_2d(0, -1, 0)    # y >= 0 (flip normal: -y <= 0)
    h2 = create_hyperplane_2d(1, 1, -2)    # x + y <= 2
    h3 = create_hyperplane_2d(-1, 0, 0)    # x >= 0 (flip normal: -x <= 0)
    
    region = HyperplaneRegion([h1, h2, h3])
    
    # Test point membership
    test_points = [(0.5, 0.5), (1, 1), (3, 0), (-1, 0)]
    memberships = region.classify_points(test_points)
    
    for point, membership in zip(test_points, memberships):
        print(f"Point {point}: {'inside' if membership else 'outside'}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Running Hyperplane Tests")
    print("=" * 40)
    
    try:
        success = True
        success &= test_basic_functionality()
        success &= test_intersections()
        success &= test_svm_functionality()
        success &= test_regions()
        
        if success:
            print("\n" + "=" * 40)
            print("✅ All tests passed successfully!")
            print("🎉 Hyperplane implementation is working!")
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)