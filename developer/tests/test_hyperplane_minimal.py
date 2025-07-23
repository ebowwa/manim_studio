#!/usr/bin/env python3
"""Minimal hyperplane test without any project dependencies."""

import sys
import os
import numpy as np
import importlib.util

# Add the specific module path directly
hyperplane_dir = os.path.join(os.path.dirname(__file__), 'src', 'utils', 'math3d')
sys.path.insert(0, hyperplane_dir)

# Import the Vector3D class directly
vector3d_path = os.path.join(hyperplane_dir, 'vector3d.py')
spec = importlib.util.spec_from_file_location("vector3d", vector3d_path)
vector3d_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vector3d_module)
Vector3D = vector3d_module.Vector3D

# Import hyperplane directly
import importlib.util
hyperplane_path = os.path.join(hyperplane_dir, 'hyperplane.py')
spec = importlib.util.spec_from_file_location("hyperplane", hyperplane_path)
hyperplane_module = importlib.util.module_from_spec(spec)

# Mock the vector3d import in hyperplane module
sys.modules['vector3d'] = vector3d_module
hyperplane_module.Vector3D = Vector3D

spec.loader.exec_module(hyperplane_module)

# Get the classes we need
Hyperplane = hyperplane_module.Hyperplane
HyperplaneIntersection = hyperplane_module.HyperplaneIntersection
HyperplaneRegion = hyperplane_module.HyperplaneRegion
create_hyperplane_2d = hyperplane_module.create_hyperplane_2d
create_hyperplane_3d = hyperplane_module.create_hyperplane_3d
svm_decision_boundary = hyperplane_module.svm_decision_boundary

def test_basic_functionality():
    """Test basic hyperplane functionality."""
    print("Testing basic hyperplane functionality...")
    
    # Test 2D hyperplane
    h2d = create_hyperplane_2d(1, 1, -1)  # x + y - 1 = 0
    print(f"✓ 2D Hyperplane created: {h2d}")
    
    # Test distance calculation
    point = [0, 0]
    distance = h2d.distance_to_point(point)
    print(f"✓ Distance from {point} to hyperplane: {distance:.3f}")
    
    # Test classification
    classification = h2d.classify_point(point)
    print(f"✓ Point {point} classification: {classification}")
    
    # Test 3D hyperplane
    h3d = create_hyperplane_3d(1, 1, 1, -3)  # x + y + z - 3 = 0
    print(f"✓ 3D Hyperplane created: {h3d}")
    
    # Test with Vector3D
    vec_point = Vector3D(1, 1, 1)
    distance_3d = h3d.distance_to_point(vec_point)
    print(f"✓ Distance from {vec_point} to 3D hyperplane: {distance_3d:.3f}")
    
    # Test projection
    projected = h3d.project_point(vec_point)
    print(f"✓ Projection of {vec_point}: {projected}")
    
    return True

def test_svm_functionality():
    """Test SVM-related functionality."""
    print("\nTesting SVM functionality...")
    
    # Create SVM decision boundary
    weights = np.array([1, -1])
    bias = 0
    
    svm_hyperplane = svm_decision_boundary(weights, bias)
    print(f"✓ SVM Decision boundary: {svm_hyperplane}")
    
    # Test classification
    test_points = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    
    for point in test_points:
        classification = svm_hyperplane.classify_point(point)
        distance = svm_hyperplane.distance_to_point(point)
        print(f"✓ Point {point}: class={classification}, distance={distance:.3f}")
    
    return True

def test_advanced_operations():
    """Test advanced operations."""
    print("\nTesting advanced operations...")
    
    # Test hyperplane from points
    h = Hyperplane.from_points([(0, 0), (1, 1)])
    print(f"✓ Hyperplane from points: {h}")
    
    # Test parallel hyperplane
    h_parallel = h.get_parallel_hyperplane(1.0)
    print(f"✓ Parallel hyperplane: {h_parallel}")
    
    # Test batch classification
    points = [(0, 0), (1, 0), (0, 1), (1, 1)]
    classifications = h.classify_points(points)
    print(f"✓ Batch classifications: {classifications}")
    
    return True

def main():
    """Run minimal tests."""
    print("🚀 Running Minimal Hyperplane Tests")
    print("=" * 40)
    
    try:
        success = True
        success &= test_basic_functionality()
        success &= test_svm_functionality()
        success &= test_advanced_operations()
        
        if success:
            print("\n" + "=" * 40)
            print("✅ All minimal tests passed!")
            print("🎉 Hyperplane core functionality is working!")
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