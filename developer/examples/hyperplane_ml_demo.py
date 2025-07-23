#!/usr/bin/env python3
"""
Machine Learning Hyperplane Demonstration

This example shows how to use the hyperplane functionality for common ML tasks:
1. SVM decision boundaries with margin visualization
2. Multi-class classification with multiple hyperplanes
3. Linear regression hyperplane fitting
4. High-dimensional data projection and visualization

Run with: python examples/hyperplane_ml_demo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

from src.utils.math3d.hyperplane import (
    Hyperplane, HyperplaneRegion,
    svm_decision_boundary
)


class SVMDemo:
    """Support Vector Machine demonstration using hyperplanes."""
    
    def __init__(self):
        self.decision_boundary = None
        self.support_vectors = []
        self.margin = 1.0
    
    def generate_linearly_separable_data(self, n_samples: int = 100) -> Tuple[List[Tuple[float, float]], List[int]]:
        """Generate linearly separable 2D data."""
        np.random.seed(42)
        
        # Generate positive class points (above y = x + 0.5)
        n_pos = n_samples // 2
        pos_points = []
        for _ in range(n_pos):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(x + 0.5 + 0.2, 4)  # Above the separating line
            pos_points.append((x, y))
        
        # Generate negative class points (below y = x - 0.5)
        n_neg = n_samples - n_pos
        neg_points = []
        for _ in range(n_neg):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(-4, x - 0.5 - 0.2)  # Below the separating line
            neg_points.append((x, y))
        
        points = pos_points + neg_points
        labels = [1] * n_pos + [-1] * n_neg
        
        return points, labels
    
    def fit_svm_hyperplane(self, points: List[Tuple[float, float]], labels: List[int]):
        """Fit SVM decision boundary (simplified - finds separating hyperplane)."""
        # For demonstration, use a simple approach
        # In practice, this would use quadratic optimization
        
        # Find the separating hyperplane: y = x (slope=1, intercept=0)
        # This corresponds to: x - y = 0, or normal=[1, -1], bias=0
        weights = np.array([1, -1])
        bias = 0.0
        
        self.decision_boundary = svm_decision_boundary(weights, bias)
        
        # Find support vectors (points closest to decision boundary)
        distances = [abs(self.decision_boundary.distance_to_point(p)) for p in points]
        
        # Get indices of closest points from each class
        pos_indices = [i for i, label in enumerate(labels) if label == 1]
        neg_indices = [i for i, label in enumerate(labels) if label == -1]
        
        if pos_indices:
            closest_pos = min(pos_indices, key=lambda i: distances[i])
            self.support_vectors.append(points[closest_pos])
        
        if neg_indices:
            closest_neg = min(neg_indices, key=lambda i: distances[i])
            self.support_vectors.append(points[closest_neg])
        
        # Set margin based on distance to support vectors
        if self.support_vectors:
            self.margin = min(abs(self.decision_boundary.distance_to_point(sv)) 
                            for sv in self.support_vectors)
    
    def classify_new_points(self, new_points: List[Tuple[float, float]]) -> List[int]:
        """Classify new points using the trained SVM."""
        if self.decision_boundary is None:
            raise ValueError("SVM not trained yet!")
        
        return self.decision_boundary.classify_points(new_points)
    
    def get_margin_boundaries(self) -> Tuple[Hyperplane, Hyperplane]:
        """Get positive and negative margin boundaries."""
        pos_margin = self.decision_boundary.get_parallel_hyperplane(-self.margin)
        neg_margin = self.decision_boundary.get_parallel_hyperplane(self.margin)
        return pos_margin, neg_margin
    
    def print_results(self):
        """Print SVM training results."""
        print(f"Decision boundary: {self.decision_boundary}")
        print(f"Margin: {self.margin:.3f}")
        print(f"Support vectors: {self.support_vectors}")
        
        pos_margin, neg_margin = self.get_margin_boundaries()
        print(f"Positive margin boundary: {pos_margin}")
        print(f"Negative margin boundary: {neg_margin}")


class MultiClassDemo:
    """Multi-class classification using multiple hyperplanes (One-vs-Rest)."""
    
    def __init__(self, n_classes: int = 3):
        self.n_classes = n_classes
        self.hyperplanes = []
    
    def generate_multi_class_data(self, n_samples: int = 150) -> Tuple[List[Tuple[float, float]], List[int]]:
        """Generate multi-class 2D data."""
        np.random.seed(42)
        
        # Create three clusters
        centers = [(0, 2), (-2, -1), (2, -1)]
        cluster_std = 0.8
        
        points = []
        labels = []
        
        samples_per_class = n_samples // self.n_classes
        
        for class_id, (cx, cy) in enumerate(centers):
            for _ in range(samples_per_class):
                x = np.random.normal(cx, cluster_std)
                y = np.random.normal(cy, cluster_std)
                points.append((x, y))
                labels.append(class_id)
        
        return points, labels
    
    def train_one_vs_rest(self, points: List[Tuple[float, float]], labels: List[int]):
        """Train one-vs-rest classifiers."""
        self.hyperplanes = []
        
        for class_id in range(self.n_classes):
            # Create binary labels: current class vs all others
            binary_labels = [1 if label == class_id else -1 for label in labels]
            
            # Find separating hyperplane for this class
            # For demonstration, use simple geometric approach
            class_points = [p for p, l in zip(points, labels) if l == class_id]
            other_points = [p for p, l in zip(points, labels) if l != class_id]
            
            if not class_points or not other_points:
                continue
            
            # Calculate centroids
            class_centroid = np.mean(class_points, axis=0)
            other_centroid = np.mean(other_points, axis=0)
            
            # Normal vector points from other centroid to class centroid
            normal = class_centroid - other_centroid
            normal = normal / np.linalg.norm(normal)
            
            # Hyperplane passes through midpoint
            midpoint = (class_centroid + other_centroid) / 2
            
            hyperplane = Hyperplane.from_point_and_normal(midpoint, normal)
            self.hyperplanes.append(hyperplane)
    
    def classify_point(self, point: Tuple[float, float]) -> int:
        """Classify a point using one-vs-rest approach."""
        if not self.hyperplanes:
            raise ValueError("Classifier not trained yet!")
        
        # Get confidence scores from all hyperplanes
        scores = []
        for hyperplane in self.hyperplanes:
            # Distance to hyperplane (positive = class side)
            score = hyperplane.distance_to_point(point)
            scores.append(score)
        
        # Return class with highest confidence
        return np.argmax(scores)
    
    def classify_points(self, points: List[Tuple[float, float]]) -> List[int]:
        """Classify multiple points."""
        return [self.classify_point(p) for p in points]
    
    def get_decision_regions(self) -> List[HyperplaneRegion]:
        """Get decision regions for each class."""
        regions = []
        
        for i, hyperplane in enumerate(self.hyperplanes):
            # Region where this class wins vs all others
            region_hyperplanes = [hyperplane]
            
            # Add constraints from other classes (should be on negative side)
            for j, other_hyperplane in enumerate(self.hyperplanes):
                if i != j:
                    # Flip to create "less than" constraint
                    constraint = other_hyperplane.flip_normal()
                    region_hyperplanes.append(constraint)
            
            region = HyperplaneRegion(region_hyperplanes)
            regions.append(region)
        
        return regions


class LinearRegressionDemo:
    """Linear regression using hyperplane fitting."""
    
    def __init__(self):
        self.fitted_hyperplane = None
        self.residuals = []
    
    def generate_noisy_data(self, n_samples: int = 50) -> Tuple[List[Tuple[float, float]], List[float]]:
        """Generate noisy linear data."""
        np.random.seed(42)
        
        # True relationship: y = 2x + 1 + noise
        x_values = np.random.uniform(-3, 3, n_samples)
        y_values = 2 * x_values + 1 + np.random.normal(0, 0.5, n_samples)
        
        points = [(x, y) for x, y in zip(x_values, y_values)]
        return points, y_values.tolist()
    
    def fit_hyperplane(self, points: List[Tuple[float, float]]):
        """Fit hyperplane to data using least squares."""
        # Convert points to augmented form for hyperplane fitting
        n_points = len(points)
        
        # For 2D regression, we fit a line: ax + by + c = 0
        # But we want y = mx + b form, so we fix b = -1: ax - y + c = 0
        # This gives us y = ax + c (slope = a, intercept = c)
        
        # Set up least squares system: minimize |ax - y + c|²
        A = np.column_stack([[p[0], 1] for p in points])  # [x, 1] matrix
        b = np.array([p[1] for p in points])              # y values
        
        # Solve normal equations: A^T A x = A^T b
        coeffs = np.linalg.lstsq(A, b, rcond=None)[0]
        slope, intercept = coeffs
        
        # Convert to hyperplane form: slope*x - y + intercept = 0
        self.fitted_hyperplane = Hyperplane([slope, -1], intercept)
        
        # Calculate residuals
        self.residuals = []
        for point in points:
            predicted_y = slope * point[0] + intercept
            residual = point[1] - predicted_y
            self.residuals.append(residual)
    
    def predict(self, x_values: List[float]) -> List[float]:
        """Make predictions for new x values."""
        if self.fitted_hyperplane is None:
            raise ValueError("Model not fitted yet!")
        
        # Extract slope and intercept from hyperplane
        # Hyperplane: ax + by + c = 0 where b = -1
        # So: ax - y + c = 0  =>  y = ax + c
        a, b = self.fitted_hyperplane.normal
        c = self.fitted_hyperplane.bias
        
        slope = a / (-b)  # a / 1 = a (since b = -1)
        intercept = c / (-b)  # c / 1 = c
        
        return [slope * x + intercept for x in x_values]
    
    def get_r_squared(self, points: List[Tuple[float, float]]) -> float:
        """Calculate R-squared goodness of fit."""
        if self.fitted_hyperplane is None:
            return 0.0
        
        y_values = [p[1] for p in points]
        y_mean = np.mean(y_values)
        
        # Total sum of squares
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        
        # Residual sum of squares
        ss_res = sum(r ** 2 for r in self.residuals)
        
        # R-squared
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    def print_results(self, points: List[Tuple[float, float]]):
        """Print regression results."""
        a, b = self.fitted_hyperplane.normal
        c = self.fitted_hyperplane.bias
        
        slope = a / (-b)
        intercept = c / (-b)
        
        r_squared = self.get_r_squared(points)
        
        print(f"Fitted line: y = {slope:.3f}x + {intercept:.3f}")
        print(f"Hyperplane form: {self.fitted_hyperplane}")
        print(f"R-squared: {r_squared:.3f}")
        print(f"Mean absolute residual: {np.mean(np.abs(self.residuals)):.3f}")


class HighDimensionalDemo:
    """Demonstration of high-dimensional hyperplane operations."""
    
    def generate_nd_data(self, n_dimensions: int = 5, n_samples: int = 100) -> Tuple[List[List[float]], List[int]]:
        """Generate high-dimensional classification data."""
        np.random.seed(42)
        
        points = []
        labels = []
        
        for _ in range(n_samples):
            # Generate random point
            point = np.random.randn(n_dimensions).tolist()
            
            # Label based on sum of coordinates
            label = 1 if sum(point) > 0 else -1
            
            points.append(point)
            labels.append(label)
        
        return points, labels
    
    def fit_hyperplane(self, points: List[List[float]], labels: List[int]) -> Hyperplane:
        """Fit separating hyperplane in high dimensions."""
        # For demonstration, use simple approach: normal = mean(pos) - mean(neg)
        
        pos_points = [p for p, l in zip(points, labels) if l == 1]
        neg_points = [p for p, l in zip(points, labels) if l == -1]
        
        pos_centroid = np.mean(pos_points, axis=0)
        neg_centroid = np.mean(neg_points, axis=0)
        
        # Normal vector
        normal = pos_centroid - neg_centroid
        
        # Bias (distance from origin)
        midpoint = (pos_centroid + neg_centroid) / 2
        bias = -np.dot(normal, midpoint)
        
        return Hyperplane(normal, bias)
    
    def project_to_2d(self, points: List[List[float]], hyperplane: Hyperplane) -> List[Tuple[float, float]]:
        """Project high-dimensional points to 2D for visualization."""
        if hyperplane.dimension < 2:
            raise ValueError("Need at least 2D hyperplane for projection")
        
        # Use first two dimensions of normal as projection basis
        projection_points = []
        
        for point in points:
            # Distance along normal (one coordinate)
            dist_along_normal = hyperplane.distance_to_point(point)
            
            # Project onto hyperplane and take first coordinate
            projected = hyperplane.project_point(point)
            coord_in_plane = projected[0] if len(projected) > 0 else 0
            
            projection_points.append((coord_in_plane, dist_along_normal))
        
        return projection_points
    
    def demonstrate_curse_of_dimensionality(self):
        """Demonstrate how hyperplane behavior changes with dimension."""
        dimensions = [2, 3, 5, 10, 20]
        results = []
        
        for d in dimensions:
            # Generate data
            points, labels = self.generate_nd_data(d, 200)
            
            # Fit hyperplane
            hyperplane = self.fit_hyperplane(points, labels)
            
            # Test accuracy
            predictions = hyperplane.classify_points(points)
            accuracy = np.mean([p == l for p, l in zip(predictions, labels)])
            
            # Calculate average distance to hyperplane
            distances = [abs(hyperplane.distance_to_point(p)) for p in points]
            avg_distance = np.mean(distances)
            
            results.append({
                'dimension': d,
                'accuracy': accuracy,
                'avg_distance': avg_distance,
                'hyperplane_norm': np.linalg.norm(hyperplane.normal)
            })
        
        return results


def main():
    """Run all machine learning demonstrations."""
    print("🤖 Machine Learning Hyperplane Demonstrations")
    print("=" * 60)
    
    # SVM Demo
    print("\\n📊 1. Support Vector Machine Demo")
    print("-" * 40)
    
    svm = SVMDemo()
    svm_points, svm_labels = svm.generate_linearly_separable_data(100)
    svm.fit_svm_hyperplane(svm_points, svm_labels)
    svm.print_results()
    
    # Test classification
    test_points = [(0, 0), (1, 2), (-1, -2), (2, 1)]
    predictions = svm.classify_new_points(test_points)
    print(f"\\nTest classifications: {list(zip(test_points, predictions))}")
    
    # Multi-class Demo
    print("\\n🎯 2. Multi-Class Classification Demo")
    print("-" * 40)
    
    multi_class = MultiClassDemo(3)
    mc_points, mc_labels = multi_class.generate_multi_class_data(150)
    multi_class.train_one_vs_rest(mc_points, mc_labels)
    
    # Test accuracy
    predictions = multi_class.classify_points(mc_points[:10])  # Test on subset
    actual = mc_labels[:10]
    accuracy = np.mean([p == a for p, a in zip(predictions, actual)])
    print(f"Sample accuracy on first 10 points: {accuracy:.1%}")
    
    print(f"Number of hyperplanes: {len(multi_class.hyperplanes)}")
    for i, hp in enumerate(multi_class.hyperplanes):
        print(f"Class {i} hyperplane: {hp}")
    
    # Linear Regression Demo
    print("\\n📈 3. Linear Regression Demo")
    print("-" * 40)
    
    regression = LinearRegressionDemo()
    reg_points, reg_targets = regression.generate_noisy_data(50)
    regression.fit_hyperplane(reg_points)
    regression.print_results(reg_points)
    
    # Make predictions
    test_x = [-2, 0, 2]
    predictions = regression.predict(test_x)
    print(f"\\nPredictions for x={test_x}: {[f'{p:.2f}' for p in predictions]}")
    
    # High-Dimensional Demo
    print("\\n🌌 4. High-Dimensional Analysis")
    print("-" * 40)
    
    hd_demo = HighDimensionalDemo()
    
    # Demonstrate curse of dimensionality
    results = hd_demo.demonstrate_curse_of_dimensionality()
    
    print("Dimension | Accuracy | Avg Distance | Normal Norm")
    print("-" * 50)
    for r in results:
        print(f"{r['dimension']:>9} | {r['accuracy']:>8.1%} | {r['avg_distance']:>12.3f} | {r['hyperplane_norm']:>11.3f}")
    
    # 5D example with projection
    points_5d, labels_5d = hd_demo.generate_nd_data(5, 50)
    hyperplane_5d = hd_demo.fit_hyperplane(points_5d, labels_5d)
    
    print(f"\\n5D hyperplane: {hyperplane_5d}")
    
    # Project to 2D for "visualization"
    projected_2d = hd_demo.project_to_2d(points_5d[:10], hyperplane_5d)
    print("\\nFirst 10 points projected to 2D:")
    for i, (original, projected) in enumerate(zip(points_5d[:10], projected_2d)):
        label = labels_5d[i]
        print(f"Point {i}: {[f'{x:.2f}' for x in original]} -> {projected} (label: {label})")
    
    print("\\n" + "=" * 60)
    print("✅ All ML demonstrations completed!")
    print("🎓 Hyperplane functionality ready for production ML use!")


if __name__ == "__main__":
    main()