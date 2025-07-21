"""
Noise Utilities

This module provides various noise generation algorithms including:
- Perlin noise (1D, 2D, 3D)
- Simplex noise (2D, 3D, 4D)
- Fractal noise (fBm, turbulence, ridged)
- Voronoi/Worley noise
- Value noise
"""

import numpy as np
from typing import Tuple, Optional, Callable
from .vector3d import Vector3D


class PerlinNoise:
    """Perlin noise generator for smooth, natural-looking randomness."""
    
    def __init__(self, seed: int = 0):
        """Initialize Perlin noise with optional seed."""
        self.seed = seed
        np.random.seed(seed)
        
        # Create permutation table
        self.perm = np.arange(256, dtype=int)
        np.random.shuffle(self.perm)
        self.perm = np.tile(self.perm, 2)
        
        # Generate gradient vectors for 3D
        self.grad3 = np.array([
            [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
            [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
            [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]
        ], dtype=float)
    
    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float, y: float = 0, z: float = 0) -> float:
        """Calculate gradient dot product."""
        g = self.grad3[hash_val % 12]
        return g[0] * x + g[1] * y + g[2] * z
    
    def noise1d(self, x: float) -> float:
        """Generate 1D Perlin noise."""
        xi = int(np.floor(x)) & 255
        xf = x - np.floor(x)
        
        u = self._fade(xf)
        
        a = self.perm[xi]
        b = self.perm[xi + 1]
        
        return self._lerp(self._grad(a, xf), self._grad(b, xf - 1), u)
    
    def noise2d(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise."""
        xi = int(np.floor(x)) & 255
        yi = int(np.floor(y)) & 255
        xf = x - np.floor(x)
        yf = y - np.floor(y)
        
        u = self._fade(xf)
        v = self._fade(yf)
        
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)
        
        return self._lerp(x1, x2, v)
    
    def noise3d(self, x: float, y: float, z: float) -> float:
        """Generate 3D Perlin noise."""
        xi = int(np.floor(x)) & 255
        yi = int(np.floor(y)) & 255
        zi = int(np.floor(z)) & 255
        xf = x - np.floor(x)
        yf = y - np.floor(y)
        zf = z - np.floor(z)
        
        u = self._fade(xf)
        v = self._fade(yf)
        w = self._fade(zf)
        
        aaa = self.perm[self.perm[self.perm[xi] + yi] + zi]
        aba = self.perm[self.perm[self.perm[xi] + yi + 1] + zi]
        aab = self.perm[self.perm[self.perm[xi] + yi] + zi + 1]
        abb = self.perm[self.perm[self.perm[xi] + yi + 1] + zi + 1]
        baa = self.perm[self.perm[self.perm[xi + 1] + yi] + zi]
        bba = self.perm[self.perm[self.perm[xi + 1] + yi + 1] + zi]
        bab = self.perm[self.perm[self.perm[xi + 1] + yi] + zi + 1]
        bbb = self.perm[self.perm[self.perm[xi + 1] + yi + 1] + zi + 1]
        
        x1 = self._lerp(self._grad(aaa, xf, yf, zf), self._grad(baa, xf - 1, yf, zf), u)
        x2 = self._lerp(self._grad(aba, xf, yf - 1, zf), self._grad(bba, xf - 1, yf - 1, zf), u)
        y1 = self._lerp(x1, x2, v)
        
        x1 = self._lerp(self._grad(aab, xf, yf, zf - 1), self._grad(bab, xf - 1, yf, zf - 1), u)
        x2 = self._lerp(self._grad(abb, xf, yf - 1, zf - 1), self._grad(bbb, xf - 1, yf - 1, zf - 1), u)
        y2 = self._lerp(x1, x2, v)
        
        return self._lerp(y1, y2, w)


class SimplexNoise:
    """Simplex noise generator - faster and smoother than Perlin noise."""
    
    def __init__(self, seed: int = 0):
        """Initialize Simplex noise with optional seed."""
        self.seed = seed
        np.random.seed(seed)
        
        # Create permutation table
        self.perm = np.arange(256, dtype=int)
        np.random.shuffle(self.perm)
        self.perm = np.tile(self.perm, 2)
        
        # Gradients for 2D
        self.grad2 = np.array([
            [1, 1], [-1, 1], [1, -1], [-1, -1],
            [1, 0], [-1, 0], [0, 1], [0, -1]
        ], dtype=float) / np.sqrt(2)
        
        # Gradients for 3D
        self.grad3 = np.array([
            [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
            [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
            [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]
        ], dtype=float)
        
        # Skewing factors
        self.F2 = 0.5 * (np.sqrt(3) - 1)
        self.G2 = (3 - np.sqrt(3)) / 6
        self.F3 = 1.0 / 3.0
        self.G3 = 1.0 / 6.0
    
    def noise2d(self, x: float, y: float) -> float:
        """Generate 2D Simplex noise."""
        # Skew the input space
        s = (x + y) * self.F2
        i = int(np.floor(x + s))
        j = int(np.floor(y + s))
        
        t = (i + j) * self.G2
        X0 = i - t
        Y0 = j - t
        x0 = x - X0
        y0 = y - Y0
        
        # Determine which simplex we're in
        if x0 > y0:
            i1, j1 = 1, 0
        else:
            i1, j1 = 0, 1
        
        x1 = x0 - i1 + self.G2
        y1 = y0 - j1 + self.G2
        x2 = x0 - 1 + 2 * self.G2
        y2 = y0 - 1 + 2 * self.G2
        
        # Hash coordinates of the 3 simplex corners
        ii = i & 255
        jj = j & 255
        gi0 = self.perm[ii + self.perm[jj]] % 8
        gi1 = self.perm[ii + i1 + self.perm[jj + j1]] % 8
        gi2 = self.perm[ii + 1 + self.perm[jj + 1]] % 8
        
        # Calculate contributions from the 3 corners
        t0 = 0.5 - x0*x0 - y0*y0
        if t0 < 0:
            n0 = 0
        else:
            t0 *= t0
            n0 = t0 * t0 * (self.grad2[gi0][0] * x0 + self.grad2[gi0][1] * y0)
        
        t1 = 0.5 - x1*x1 - y1*y1
        if t1 < 0:
            n1 = 0
        else:
            t1 *= t1
            n1 = t1 * t1 * (self.grad2[gi1][0] * x1 + self.grad2[gi1][1] * y1)
        
        t2 = 0.5 - x2*x2 - y2*y2
        if t2 < 0:
            n2 = 0
        else:
            t2 *= t2
            n2 = t2 * t2 * (self.grad2[gi2][0] * x2 + self.grad2[gi2][1] * y2)
        
        # Return scaled sum
        return 70 * (n0 + n1 + n2)
    
    def noise3d(self, x: float, y: float, z: float) -> float:
        """Generate 3D Simplex noise."""
        # Skew the input space
        s = (x + y + z) * self.F3
        i = int(np.floor(x + s))
        j = int(np.floor(y + s))
        k = int(np.floor(z + s))
        
        t = (i + j + k) * self.G3
        X0 = i - t
        Y0 = j - t
        Z0 = k - t
        x0 = x - X0
        y0 = y - Y0
        z0 = z - Z0
        
        # Determine which simplex we're in
        if x0 >= y0:
            if y0 >= z0:
                i1, j1, k1, i2, j2, k2 = 1, 0, 0, 1, 1, 0
            elif x0 >= z0:
                i1, j1, k1, i2, j2, k2 = 1, 0, 0, 1, 0, 1
            else:
                i1, j1, k1, i2, j2, k2 = 0, 0, 1, 1, 0, 1
        else:
            if y0 < z0:
                i1, j1, k1, i2, j2, k2 = 0, 0, 1, 0, 1, 1
            elif x0 < z0:
                i1, j1, k1, i2, j2, k2 = 0, 1, 0, 0, 1, 1
            else:
                i1, j1, k1, i2, j2, k2 = 0, 1, 0, 1, 1, 0
        
        x1 = x0 - i1 + self.G3
        y1 = y0 - j1 + self.G3
        z1 = z0 - k1 + self.G3
        x2 = x0 - i2 + 2 * self.G3
        y2 = y0 - j2 + 2 * self.G3
        z2 = z0 - k2 + 2 * self.G3
        x3 = x0 - 1 + 3 * self.G3
        y3 = y0 - 1 + 3 * self.G3
        z3 = z0 - 1 + 3 * self.G3
        
        # Hash coordinates of the 4 simplex corners
        ii = i & 255
        jj = j & 255
        kk = k & 255
        gi0 = self.perm[ii + self.perm[jj + self.perm[kk]]] % 12
        gi1 = self.perm[ii + i1 + self.perm[jj + j1 + self.perm[kk + k1]]] % 12
        gi2 = self.perm[ii + i2 + self.perm[jj + j2 + self.perm[kk + k2]]] % 12
        gi3 = self.perm[ii + 1 + self.perm[jj + 1 + self.perm[kk + 1]]] % 12
        
        # Calculate contributions from the 4 corners
        t0 = 0.6 - x0*x0 - y0*y0 - z0*z0
        if t0 < 0:
            n0 = 0
        else:
            t0 *= t0
            n0 = t0 * t0 * (self.grad3[gi0][0] * x0 + self.grad3[gi0][1] * y0 + self.grad3[gi0][2] * z0)
        
        t1 = 0.6 - x1*x1 - y1*y1 - z1*z1
        if t1 < 0:
            n1 = 0
        else:
            t1 *= t1
            n1 = t1 * t1 * (self.grad3[gi1][0] * x1 + self.grad3[gi1][1] * y1 + self.grad3[gi1][2] * z1)
        
        t2 = 0.6 - x2*x2 - y2*y2 - z2*z2
        if t2 < 0:
            n2 = 0
        else:
            t2 *= t2
            n2 = t2 * t2 * (self.grad3[gi2][0] * x2 + self.grad3[gi2][1] * y2 + self.grad3[gi2][2] * z2)
        
        t3 = 0.6 - x3*x3 - y3*y3 - z3*z3
        if t3 < 0:
            n3 = 0
        else:
            t3 *= t3
            n3 = t3 * t3 * (self.grad3[gi3][0] * x3 + self.grad3[gi3][1] * y3 + self.grad3[gi3][2] * z3)
        
        # Return scaled sum
        return 32 * (n0 + n1 + n2 + n3)


class FractalNoise:
    """Fractal noise generator for complex, multi-scale patterns."""
    
    def __init__(self, noise_func: Callable, octaves: int = 4, 
                 persistence: float = 0.5, lacunarity: float = 2.0):
        """Initialize fractal noise with base noise function."""
        self.noise_func = noise_func
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
    
    def fbm(self, x: float, y: float = 0, z: float = 0) -> float:
        """Fractal Brownian Motion - sum of noise at different frequencies."""
        value = 0
        amplitude = 1
        frequency = 1
        max_value = 0
        
        for _ in range(self.octaves):
            if z != 0:
                value += amplitude * self.noise_func(x * frequency, y * frequency, z * frequency)
            elif y != 0:
                value += amplitude * self.noise_func(x * frequency, y * frequency)
            else:
                value += amplitude * self.noise_func(x * frequency)
            
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity
        
        return value / max_value
    
    def turbulence(self, x: float, y: float = 0, z: float = 0) -> float:
        """Turbulence - sum of absolute noise values."""
        value = 0
        amplitude = 1
        frequency = 1
        max_value = 0
        
        for _ in range(self.octaves):
            if z != 0:
                value += amplitude * abs(self.noise_func(x * frequency, y * frequency, z * frequency))
            elif y != 0:
                value += amplitude * abs(self.noise_func(x * frequency, y * frequency))
            else:
                value += amplitude * abs(self.noise_func(x * frequency))
            
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity
        
        return value / max_value
    
    def ridged(self, x: float, y: float = 0, z: float = 0, offset: float = 1.0) -> float:
        """Ridged fractal noise - creates sharp ridges."""
        value = 0
        amplitude = 0.5
        frequency = 1
        prev = 1.0
        
        for i in range(self.octaves):
            if z != 0:
                n = self.noise_func(x * frequency, y * frequency, z * frequency)
            elif y != 0:
                n = self.noise_func(x * frequency, y * frequency)
            else:
                n = self.noise_func(x * frequency)
            
            n = abs(n)
            n = offset - n
            n = n * n
            value += n * amplitude * prev
            prev = n
            frequency *= self.lacunarity
            amplitude *= self.persistence
        
        return value


class VoronoiNoise:
    """Voronoi/Worley noise generator for cellular patterns."""
    
    def __init__(self, seed: int = 0):
        """Initialize Voronoi noise with optional seed."""
        self.seed = seed
        np.random.seed(seed)
    
    def _get_cell_points(self, x: int, y: int, z: int = 0) -> list:
        """Get random points within a cell."""
        # Use a hash function to generate consistent random points
        hash_val = x * 73856093 ^ y * 19349663 ^ z * 83492791
        np.random.seed((hash_val + self.seed) & 0x7fffffff)
        
        # Generate 1-4 points per cell
        num_points = np.random.randint(1, 5)
        points = []
        
        for _ in range(num_points):
            px = x + np.random.random()
            py = y + np.random.random()
            if z != 0:
                pz = z + np.random.random()
                points.append((px, py, pz))
            else:
                points.append((px, py))
        
        return points
    
    def noise2d(self, x: float, y: float, distance_func: str = 'euclidean') -> Tuple[float, float]:
        """Generate 2D Voronoi noise. Returns (F1, F2) distances."""
        xi = int(np.floor(x))
        yi = int(np.floor(y))
        
        f1 = float('inf')
        f2 = float('inf')
        
        # Check surrounding cells
        for i in range(-1, 2):
            for j in range(-1, 2):
                cell_points = self._get_cell_points(xi + i, yi + j)
                
                for px, py in cell_points:
                    if distance_func == 'euclidean':
                        dist = np.sqrt((x - px)**2 + (y - py)**2)
                    elif distance_func == 'manhattan':
                        dist = abs(x - px) + abs(y - py)
                    elif distance_func == 'chebyshev':
                        dist = max(abs(x - px), abs(y - py))
                    else:
                        dist = np.sqrt((x - px)**2 + (y - py)**2)
                    
                    if dist < f1:
                        f2 = f1
                        f1 = dist
                    elif dist < f2:
                        f2 = dist
        
        return f1, f2
    
    def noise3d(self, x: float, y: float, z: float, 
                distance_func: str = 'euclidean') -> Tuple[float, float]:
        """Generate 3D Voronoi noise. Returns (F1, F2) distances."""
        xi = int(np.floor(x))
        yi = int(np.floor(y))
        zi = int(np.floor(z))
        
        f1 = float('inf')
        f2 = float('inf')
        
        # Check surrounding cells
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    cell_points = self._get_cell_points(xi + i, yi + j, zi + k)
                    
                    for px, py, pz in cell_points:
                        if distance_func == 'euclidean':
                            dist = np.sqrt((x - px)**2 + (y - py)**2 + (z - pz)**2)
                        elif distance_func == 'manhattan':
                            dist = abs(x - px) + abs(y - py) + abs(z - pz)
                        elif distance_func == 'chebyshev':
                            dist = max(abs(x - px), abs(y - py), abs(z - pz))
                        else:
                            dist = np.sqrt((x - px)**2 + (y - py)**2 + (z - pz)**2)
                        
                        if dist < f1:
                            f2 = f1
                            f1 = dist
                        elif dist < f2:
                            f2 = dist
        
        return f1, f2


# Convenience functions
def perlin_noise_2d(x: float, y: float, seed: int = 0) -> float:
    """Generate 2D Perlin noise value."""
    noise = PerlinNoise(seed)
    return noise.noise2d(x, y)


def perlin_noise_3d(x: float, y: float, z: float, seed: int = 0) -> float:
    """Generate 3D Perlin noise value."""
    noise = PerlinNoise(seed)
    return noise.noise3d(x, y, z)


def simplex_noise_2d(x: float, y: float, seed: int = 0) -> float:
    """Generate 2D Simplex noise value."""
    noise = SimplexNoise(seed)
    return noise.noise2d(x, y)


def simplex_noise_3d(x: float, y: float, z: float, seed: int = 0) -> float:
    """Generate 3D Simplex noise value."""
    noise = SimplexNoise(seed)
    return noise.noise3d(x, y, z)


def fbm_2d(x: float, y: float, octaves: int = 4, persistence: float = 0.5, 
           lacunarity: float = 2.0, seed: int = 0) -> float:
    """Generate 2D fractal Brownian motion."""
    noise = PerlinNoise(seed)
    fractal = FractalNoise(noise.noise2d, octaves, persistence, lacunarity)
    return fractal.fbm(x, y)


def fbm_3d(x: float, y: float, z: float, octaves: int = 4, 
           persistence: float = 0.5, lacunarity: float = 2.0, seed: int = 0) -> float:
    """Generate 3D fractal Brownian motion."""
    noise = PerlinNoise(seed)
    fractal = FractalNoise(noise.noise3d, octaves, persistence, lacunarity)
    return fractal.fbm(x, y, z)


def turbulence_2d(x: float, y: float, octaves: int = 4, 
                  persistence: float = 0.5, lacunarity: float = 2.0, seed: int = 0) -> float:
    """Generate 2D turbulence."""
    noise = PerlinNoise(seed)
    fractal = FractalNoise(noise.noise2d, octaves, persistence, lacunarity)
    return fractal.turbulence(x, y)


def voronoi_2d(x: float, y: float, seed: int = 0) -> float:
    """Generate 2D Voronoi noise (F1 distance)."""
    noise = VoronoiNoise(seed)
    f1, _ = noise.noise2d(x, y)
    return f1


def voronoi_edge_2d(x: float, y: float, seed: int = 0) -> float:
    """Generate 2D Voronoi edge noise (F2 - F1)."""
    noise = VoronoiNoise(seed)
    f1, f2 = noise.noise2d(x, y)
    return f2 - f1


def noise_vector_field_2d(x: float, y: float, seed: int = 0) -> Vector3D:
    """Generate 2D vector field from noise."""
    noise = PerlinNoise(seed)
    # Use different seeds for each component
    nx = noise.noise2d(x, y)
    ny = PerlinNoise(seed + 1).noise2d(x, y)
    return Vector3D(nx, ny, 0).normalize()


def noise_vector_field_3d(x: float, y: float, z: float, seed: int = 0) -> Vector3D:
    """Generate 3D vector field from noise."""
    noise = PerlinNoise(seed)
    # Use different seeds for each component
    nx = noise.noise3d(x, y, z)
    ny = PerlinNoise(seed + 1).noise3d(x, y, z)
    nz = PerlinNoise(seed + 2).noise3d(x, y, z)
    return Vector3D(nx, ny, nz).normalize()