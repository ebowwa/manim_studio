"""
Test polygon operations in math3d package
"""
import sys
sys.path.insert(0, 'src')

import numpy as np
import pytest
from utils.math3d import (
    get_winding_number, point_in_polygon, shoelace, polygon_area,
    polygon_orientation, polygon_centroid, earclip_triangulation,
    complex_to_R3, R3_to_complex, complex_func_to_R3_func
)

class TestPolygonOperations:
    """Test suite for polygon operations."""
    
    def test_winding_number(self):
        """Test winding number calculation for various polygons."""
        # Square around origin (counterclockwise)
        square_ccw = np.array([
            [1, 1, 0], [-1, 1, 0], [-1, -1, 0], [1, -1, 0]
        ])
        
        # Square around origin (clockwise)  
        square_cw = np.array([
            [1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0]
        ])
        
        # Square not containing origin
        square_outside = np.array([
            [3, 3, 0], [2, 3, 0], [2, 2, 0], [3, 2, 0]
        ])
        
        assert abs(get_winding_number(square_ccw) - 1.0) < 0.1
        assert abs(get_winding_number(square_cw) + 1.0) < 0.1
        assert abs(get_winding_number(square_outside)) < 0.1
    
    def test_shoelace_area(self):
        """Test area calculation using shoelace formula."""
        # Unit square
        square = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ])
        
        # Right triangle
        triangle = np.array([
            [0, 0, 0], [3, 0, 0], [0, 4, 0]
        ])
        
        assert abs(polygon_area(square) - 1.0) < 0.01
        assert abs(polygon_area(triangle) - 6.0) < 0.01
        assert polygon_orientation(square) == "CCW"
    
    def test_point_in_polygon(self):
        """Test point in polygon detection."""
        square = np.array([
            [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]
        ])
        
        assert point_in_polygon(np.array([0, 0, 0]), square)  # Inside
        assert not point_in_polygon(np.array([2, 0, 0]), square)  # Outside
    
    def test_triangulation(self):
        """Test ear clipping triangulation."""
        square = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ])
        
        triangles = earclip_triangulation(square)
        assert len(triangles) == 2
        
        # Check that all triangle indices are valid
        for tri in triangles:
            assert all(0 <= i < len(square) for i in tri)
    
    def test_complex_conversions(self):
        """Test complex number conversions."""
        z = 3 + 4j
        point_3d = complex_to_R3(z)
        z_back = R3_to_complex(point_3d)
        
        assert abs(z_back - z) < 1e-10
        assert np.allclose(point_3d, [3, 4, 0])
        
        # Test function conversion
        def square_func(z):
            return z**2
        
        func_3d = complex_func_to_R3_func(square_func)
        result = func_3d(point_3d)
        expected = complex_to_R3(z**2)  # (-7 + 24j)
        
        assert np.allclose(result, expected)
    
    def test_polygon_centroid(self):
        """Test polygon centroid calculation."""
        # Regular triangle centered at origin
        triangle = np.array([
            [1, 0, 0], [-0.5, np.sqrt(3)/2, 0], [-0.5, -np.sqrt(3)/2, 0]
        ])
        
        centroid = polygon_centroid(triangle)
        assert np.linalg.norm(centroid[:2]) < 0.01  # Should be near origin

if __name__ == "__main__":
    # Run tests manually if pytest not available
    test_suite = TestPolygonOperations()
    
    tests = [
        test_suite.test_winding_number,
        test_suite.test_shoelace_area,
        test_suite.test_point_in_polygon,
        test_suite.test_triangulation,
        test_suite.test_complex_conversions,
        test_suite.test_polygon_centroid
    ]
    
    passed = 0
    for i, test in enumerate(tests):
        try:
            test()
            print(f"✓ Test {i+1} passed")
            passed += 1
        except Exception as e:
            print(f"✗ Test {i+1} failed: {e}")
    
    print(f"\n{passed}/{len(tests)} tests passed")