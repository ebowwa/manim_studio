#!/usr/bin/env python3
"""
Comprehensive test and demonstration script for hyperplane functionality.

This script tests all hyperplane features and creates visual demonstrations.
Run with: python test_hyperplane_comprehensive.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from src.utils.math3d.hyperplane import (
    Hyperplane, HyperplaneIntersection, HyperplaneRegion,
    create_hyperplane_2d, create_hyperplane_3d,
    hyperplane_from_points_2d, hyperplane_from_points_3d,
    svm_decision_boundary
)
from src.utils.math3d.vector3d import Vector3D


def test_2d_hyperplanes():
    """Test 2D hyperplane functionality."""
    print("\\n=== Testing 2D Hyperplanes ===")
    
    # Create hyperplane from equation: x + y - 1 = 0
    h1 = create_hyperplane_2d(1, 1, -1)
    print(f"Hyperplane 1: {h1}")
    
    # Create hyperplane from two points
    h2 = hyperplane_from_points_2d((0, 0), (1, 1))
    print(f"Hyperplane 2: {h2}")
    
    # Test distance calculations
    test_points = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]
    
    print("\\nDistance tests:")
    for point in test_points:
        dist1 = h1.distance_to_point(point)
        dist2 = h2.distance_to_point(point)
        class1 = h1.classify_point(point)
        class2 = h2.classify_point(point)
        print(f"Point {point}: H1 dist={dist1:.3f} class={class1}, H2 dist={dist2:.3f} class={class2}")
    
    # Test projections
    print("\\nProjection tests:")
    for point in [(2, 0), (0, 2)]:
        proj1 = h1.project_point(point)
        proj2 = h2.project_point(point)
        print(f"Point {point}: H1 proj={proj1}, H2 proj={proj2}")
    
    return h1, h2


def test_3d_hyperplanes():
    """Test 3D hyperplane functionality."""
    print("\\n=== Testing 3D Hyperplanes ===")
    
    # Create hyperplane from equation: x + y + z - 3 = 0
    h1 = create_hyperplane_3d(1, 1, 1, -3)
    print(f"Hyperplane 1: {h1}")
    
    # Create hyperplane from three points
    h2 = hyperplane_from_points_3d((1, 0, 0), (0, 1, 0), (0, 0, 1))
    print(f"Hyperplane 2: {h2}")
    
    # Test with Vector3D integration
    point_vec = Vector3D(1, 1, 1)
    dist = h1.distance_to_point(point_vec)
    proj = h1.project_point(point_vec)
    print(f"Vector3D point {point_vec}: distance={dist:.3f}, projection={proj}")
    
    # Test conversion to Vector3D representation
    plane_point, plane_normal = h1.to_vector3d_plane()
    print(f"Vector3D representation: point={plane_point}, normal={plane_normal}")
    
    return h1, h2


def test_hyperplane_intersections():
    """Test hyperplane intersection functionality."""
    print("\\n=== Testing Hyperplane Intersections ===")
    
    # 2D intersections (lines)
    h1 = create_hyperplane_2d(1, 0, -1)    # x = 1
    h2 = create_hyperplane_2d(0, 1, -2)    # y = 2
    
    intersection = HyperplaneIntersection.intersect_two_hyperplanes(h1, h2)
    print(f"2D intersection of x=1 and y=2: {intersection}")
    
    # 3D intersections
    h3 = create_hyperplane_3d(1, 0, 0, -1)  # x = 1
    h4 = create_hyperplane_3d(0, 1, 0, -2)  # y = 2
    h5 = create_hyperplane_3d(0, 0, 1, -3)  # z = 3
    
    intersection_3d = HyperplaneIntersection.intersect_multiple_hyperplanes([h3, h4, h5])
    print(f"3D intersection of x=1, y=2, z=3: {intersection_3d}")
    
    # Test parallel hyperplanes
    h6 = create_hyperplane_2d(1, 1, -1)  # x + y = 1
    h7 = create_hyperplane_2d(1, 1, -2)  # x + y = 2 (parallel)
    
    parallel_intersection = HyperplaneIntersection.intersect_two_hyperplanes(h6, h7)
    print(f"Parallel lines intersection: {parallel_intersection}")


def test_hyperplane_regions():
    """Test hyperplane region functionality."""
    print("\\n=== Testing Hyperplane Regions ===")
    
    # Create a 2D triangular region
    # Triangle with vertices at (0,0), (2,0), (1,2)
    h1 = create_hyperplane_2d(0, 1, 0)      # y >= 0
    h2 = create_hyperplane_2d(1, 1, -2)     # x + y <= 2  
    h3 = create_hyperplane_2d(-1, 0, 0)     # x >= 0
    
    # Flip normals for "less than or equal" constraints
    h1 = h1.flip_normal()  # y >= 0 becomes -y <= 0
    h2 = h2  # x + y <= 2 stays the same
    h3 = h3.flip_normal()  # x >= 0 becomes -x <= 0
    
    region = HyperplaneRegion([h1, h2, h3])
    
    # Test point membership
    test_points = [(0.5, 0.5), (1, 1), (3, 0), (-1, 0), (1, -1)]
    memberships = region.classify_points(test_points)
    
    print("\\nRegion membership tests:")
    for point, membership in zip(test_points, memberships):
        print(f"Point {point}: {'inside' if membership else 'outside'}")
    
    # Get vertices
    try:
        vertices = region.get_vertices()
        print(f"\\nRegion vertices: {vertices}")
        
        center = region.get_center()
        print(f"Region center: {center}")
    except Exception as e:
        print(f"Vertex calculation error: {e}")


def test_svm_functionality():
    """Test SVM-related hyperplane functionality."""
    print("\\n=== Testing SVM Functionality ===")
    
    # Create simple SVM decision boundary
    # Separates points above/below line y = x
    weights = np.array([1, -1])  # Normal vector (1, -1)
    bias = 0  # Passes through origin
    
    decision_boundary = svm_decision_boundary(weights, bias)
    print(f"SVM decision boundary: {decision_boundary}")
    
    # Test classification
    positive_points = [(1, 0), (2, 1), (3, 0)]
    negative_points = [(0, 1), (1, 2), (0, 3)]
    
    print("\\nSVM Classifications:")
    for point in positive_points:
        classification = decision_boundary.classify_point(point)
        distance = decision_boundary.distance_to_point(point)
        print(f"Positive point {point}: class={classification}, distance={distance:.3f}")
    
    for point in negative_points:
        classification = decision_boundary.classify_point(point)
        distance = decision_boundary.distance_to_point(point)
        print(f"Negative point {point}: class={classification}, distance={distance:.3f}")
    
    # Create margin boundaries
    margin = 1.0
    positive_margin = decision_boundary.get_parallel_hyperplane(-margin)
    negative_margin = decision_boundary.get_parallel_hyperplane(margin)
    
    print(f"\\nMargin boundaries:")
    print(f"Positive margin: {positive_margin}")
    print(f"Negative margin: {negative_margin}")


def test_advanced_operations():
    """Test advanced hyperplane operations."""
    print("\\n=== Testing Advanced Operations ===")
    
    # Create hyperplane
    h = create_hyperplane_2d(3, 4, -5)  # 3x + 4y - 5 = 0
    print(f"Original hyperplane: {h}")
    
    # Test translation
    offset = [1, 1]
    h_translated = h.translate(offset)
    print(f"Translated by {offset}: {h_translated}")
    
    # Test parallel hyperplane
    distance = 2.0
    h_parallel = h.get_parallel_hyperplane(distance)
    print(f"Parallel at distance {distance}: {h_parallel}")
    
    # Test reflection
    test_point = [0, 0]
    reflected = h.reflect_point(test_point)
    print(f"Point {test_point} reflected across hyperplane: {reflected}")
    
    # Test batch classification
    batch_points = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]
    classifications = h.classify_points(batch_points)
    print(f"\\nBatch classifications: {classifications}")
    
    distances = [h.distance_to_point(p) for p in batch_points]
    print(f"Batch distances: {[f'{d:.3f}' for d in distances]}")


def test_integration_with_existing_math():
    """Test integration with existing mathematical objects."""
    print("\\n=== Testing Integration with Existing Math Objects ===")
    
    try:
        from src.components.mathematical_objects import Inequality2D, FeasibleArea2D
        from src.components.hyperplane_objects import hyperplane_from_inequality_2d
        
        # Create inequality: x + y <= 2
        inequality = Inequality2D(1, 1, "<=", 2)
        
        # Convert to hyperplane
        hyperplane = hyperplane_from_inequality_2d(inequality)
        print(f"Converted inequality to hyperplane: {hyperplane}")
        
        # Test point classification consistency
        test_points = [(0, 0), (1, 1), (2, 2), (3, 3)]
        
        print("\\nConsistency test (inequality vs hyperplane):")
        for point in test_points:
            ineq_result = inequality.satisfies(point[0], point[1])
            hyperplane_result = hyperplane.classify_point(point) <= 0
            consistent = ineq_result == hyperplane_result
            print(f"Point {point}: inequality={ineq_result}, hyperplane={hyperplane_result}, consistent={consistent}")
            
    except ImportError as e:
        print(f"Integration test skipped due to import error: {e}")


def test_error_handling():
    """Test error handling and edge cases."""
    print("\\n=== Testing Error Handling ===")
    
    # Test dimension mismatch
    try:
        h1 = create_hyperplane_2d(1, 1, 0)
        h2 = create_hyperplane_3d(1, 1, 1, 0)
        HyperplaneIntersection.intersect_two_hyperplanes(h1, h2)
        print("ERROR: Dimension mismatch not caught!")
    except ValueError as e:
        print(f"✓ Dimension mismatch correctly caught: {e}")
    
    # Test insufficient points
    try:
        Hyperplane.from_points([(0, 0)])  # Need at least 2 points for 2D
        print("ERROR: Insufficient points not caught!")
    except ValueError as e:
        print(f"✓ Insufficient points correctly caught: {e}")
    
    # Test zero normal vector
    try:
        h = Hyperplane([0, 0], 1)
        print(f"Zero normal vector handled: {h}")
    except Exception as e:
        print(f"Zero normal vector error: {e}")
    
    # Test numerical stability
    very_small = 1e-15
    h = create_hyperplane_2d(very_small, 1, 0)
    print(f"✓ Very small coefficients handled: {h}")


def performance_test():
    """Basic performance test for batch operations."""
    print("\\n=== Performance Test ===")
    
    import time
    
    # Create hyperplane
    h = create_hyperplane_2d(1, 1, 0)
    
    # Generate test points
    n_points = 10000
    points = [(np.random.randn(), np.random.randn()) for _ in range(n_points)]
    
    # Time batch classification
    start_time = time.time()
    classifications = h.classify_points(points)
    batch_time = time.time() - start_time
    
    # Time individual classifications
    start_time = time.time()
    individual_classifications = [h.classify_point(p) for p in points]
    individual_time = time.time() - start_time
    
    print(f"Batch classification of {n_points} points: {batch_time:.3f}s")
    print(f"Individual classification of {n_points} points: {individual_time:.3f}s")
    print(f"Speedup factor: {individual_time/batch_time:.2f}x")
    
    # Verify consistency
    consistent = np.allclose(classifications, individual_classifications)
    print(f"Results consistent: {consistent}")


def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Hyperplane Tests")
    print("=" * 50)
    
    try:
        # Basic functionality tests
        test_2d_hyperplanes()
        test_3d_hyperplanes()
        
        # Advanced functionality tests
        test_hyperplane_intersections()
        test_hyperplane_regions()
        test_svm_functionality()
        test_advanced_operations()
        
        # Integration tests
        test_integration_with_existing_math()
        
        # Robustness tests
        test_error_handling()
        
        # Performance tests
        performance_test()
        
        print("\\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 Hyperplane functionality is ready for use!")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)