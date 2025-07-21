"""
Color Math Utilities

This module provides comprehensive color space conversions and operations:
- RGB, HSV, HSL color spaces
- LAB, XYZ color spaces
- Color interpolation and blending
- Color harmonies and palettes
- Perceptual color differences
- Color temperature conversions
"""

import numpy as np
from typing import Tuple, List, Union
from dataclasses import dataclass
from .vector3d import Vector3D


@dataclass
class Color:
    """Color representation with multiple color space support."""
    r: float  # Red (0-1)
    g: float  # Green (0-1)
    b: float  # Blue (0-1)
    a: float = 1.0  # Alpha (0-1)
    
    def __post_init__(self):
        """Clamp color values to valid range."""
        self.r = np.clip(self.r, 0, 1)
        self.g = np.clip(self.g, 0, 1)
        self.b = np.clip(self.b, 0, 1)
        self.a = np.clip(self.a, 0, 1)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create color from hex string."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return cls(r/255, g/255, b/255)
        elif len(hex_color) == 8:
            r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
            return cls(r/255, g/255, b/255, a/255)
        else:
            raise ValueError(f"Invalid hex color: {hex_color}")
    
    @classmethod
    def from_rgb255(cls, r: int, g: int, b: int, a: int = 255) -> 'Color':
        """Create color from 0-255 RGB values."""
        return cls(r/255, g/255, b/255, a/255)
    
    def to_hex(self, include_alpha: bool = False) -> str:
        """Convert to hex string."""
        if include_alpha:
            return f"#{int(self.r*255):02x}{int(self.g*255):02x}{int(self.b*255):02x}{int(self.a*255):02x}"
        else:
            return f"#{int(self.r*255):02x}{int(self.g*255):02x}{int(self.b*255):02x}"
    
    def to_rgb255(self) -> Tuple[int, int, int, int]:
        """Convert to 0-255 RGB values."""
        return (int(self.r*255), int(self.g*255), int(self.b*255), int(self.a*255))
    
    def to_vector3d(self) -> Vector3D:
        """Convert to Vector3D (RGB only)."""
        return Vector3D(self.r, self.g, self.b)
    
    @classmethod
    def from_vector3d(cls, vec: Vector3D, alpha: float = 1.0) -> 'Color':
        """Create color from Vector3D."""
        return cls(vec.x, vec.y, vec.z, alpha)
    
    def lerp(self, other: 'Color', t: float) -> 'Color':
        """Linear interpolation between colors."""
        t = np.clip(t, 0, 1)
        return Color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t
        )
    
    def __mul__(self, scalar: float) -> 'Color':
        """Multiply color by scalar."""
        return Color(self.r * scalar, self.g * scalar, self.b * scalar, self.a)
    
    def __add__(self, other: 'Color') -> 'Color':
        """Add two colors."""
        return Color(self.r + other.r, self.g + other.g, self.b + other.b, self.a)
    
    def __sub__(self, other: 'Color') -> 'Color':
        """Subtract two colors."""
        return Color(self.r - other.r, self.g - other.g, self.b - other.b, self.a)


class ColorSpaceConversions:
    """Color space conversion utilities."""
    
    @staticmethod
    def rgb_to_hsv(color: Color) -> Tuple[float, float, float]:
        """Convert RGB to HSV (Hue, Saturation, Value)."""
        r, g, b = color.r, color.g, color.b
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        v = max_val
        
        # Saturation
        if max_val == 0:
            s = 0
        else:
            s = diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = ((g - b) / diff) % 6
        elif max_val == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4
        
        h = h / 6  # Normalize to 0-1
        
        return h, s, v
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Color:
        """Convert HSV to RGB."""
        h = h * 6  # Convert back to 0-6 range
        i = int(h)
        f = h - i
        
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        if i == 0:
            return Color(v, t, p)
        elif i == 1:
            return Color(q, v, p)
        elif i == 2:
            return Color(p, v, t)
        elif i == 3:
            return Color(p, q, v)
        elif i == 4:
            return Color(t, p, v)
        else:
            return Color(v, p, q)
    
    @staticmethod
    def rgb_to_hsl(color: Color) -> Tuple[float, float, float]:
        """Convert RGB to HSL (Hue, Saturation, Lightness)."""
        r, g, b = color.r, color.g, color.b
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Lightness
        l = (max_val + min_val) / 2
        
        if diff == 0:
            h = s = 0
        else:
            # Saturation
            if l < 0.5:
                s = diff / (max_val + min_val)
            else:
                s = diff / (2 - max_val - min_val)
            
            # Hue (same as HSV)
            if max_val == r:
                h = ((g - b) / diff) % 6
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            
            h = h / 6
        
        return h, s, l
    
    @staticmethod
    def hsl_to_rgb(h: float, s: float, l: float) -> Color:
        """Convert HSL to RGB."""
        if s == 0:
            return Color(l, l, l)
        
        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
        
        return Color(r, g, b)
    
    @staticmethod
    def rgb_to_xyz(color: Color) -> Tuple[float, float, float]:
        """Convert RGB to XYZ color space."""
        # Convert to linear RGB
        def to_linear(c: float) -> float:
            if c <= 0.04045:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4
        
        r = to_linear(color.r)
        g = to_linear(color.g)
        b = to_linear(color.b)
        
        # Observer = 2°, Illuminant = D65
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        return x * 100, y * 100, z * 100
    
    @staticmethod
    def xyz_to_rgb(x: float, y: float, z: float) -> Color:
        """Convert XYZ to RGB color space."""
        # Normalize
        x = x / 100
        y = y / 100
        z = z / 100
        
        # Observer = 2°, Illuminant = D65
        r = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
        g = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
        b = x *  0.0556434 + y * -0.2040259 + z *  1.0572252
        
        # Convert from linear to sRGB
        def from_linear(c: float) -> float:
            if c <= 0.0031308:
                return 12.92 * c
            else:
                return 1.055 * (c ** (1/2.4)) - 0.055
        
        return Color(from_linear(r), from_linear(g), from_linear(b))
    
    @staticmethod
    def xyz_to_lab(x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Convert XYZ to LAB color space."""
        # Reference white D65
        xn, yn, zn = 95.047, 100.000, 108.883
        
        def f(t: float) -> float:
            if t > 0.008856:
                return t ** (1/3)
            else:
                return 7.787 * t + 16/116
        
        fx = f(x / xn)
        fy = f(y / yn)
        fz = f(z / zn)
        
        l = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        
        return l, a, b
    
    @staticmethod
    def lab_to_xyz(l: float, a: float, b: float) -> Tuple[float, float, float]:
        """Convert LAB to XYZ color space."""
        # Reference white D65
        xn, yn, zn = 95.047, 100.000, 108.883
        
        fy = (l + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200
        
        def f_inv(t: float) -> float:
            if t ** 3 > 0.008856:
                return t ** 3
            else:
                return (t - 16/116) / 7.787
        
        x = xn * f_inv(fx)
        y = yn * f_inv(fy)
        z = zn * f_inv(fz)
        
        return x, y, z
    
    @staticmethod
    def rgb_to_lab(color: Color) -> Tuple[float, float, float]:
        """Convert RGB to LAB color space."""
        x, y, z = ColorSpaceConversions.rgb_to_xyz(color)
        return ColorSpaceConversions.xyz_to_lab(x, y, z)
    
    @staticmethod
    def lab_to_rgb(l: float, a: float, b: float) -> Color:
        """Convert LAB to RGB color space."""
        x, y, z = ColorSpaceConversions.lab_to_xyz(l, a, b)
        return ColorSpaceConversions.xyz_to_rgb(x, y, z)


class ColorOperations:
    """Color manipulation and analysis operations."""
    
    @staticmethod
    def blend(color1: Color, color2: Color, mode: str = 'normal', opacity: float = 1.0) -> Color:
        """Blend two colors using various blend modes."""
        opacity = np.clip(opacity, 0, 1)
        
        if mode == 'normal':
            return color1.lerp(color2, opacity)
        
        elif mode == 'multiply':
            result = Color(
                color1.r * color2.r,
                color1.g * color2.g,
                color1.b * color2.b
            )
            return color1.lerp(result, opacity)
        
        elif mode == 'screen':
            result = Color(
                1 - (1 - color1.r) * (1 - color2.r),
                1 - (1 - color1.g) * (1 - color2.g),
                1 - (1 - color1.b) * (1 - color2.b)
            )
            return color1.lerp(result, opacity)
        
        elif mode == 'overlay':
            def overlay_channel(a: float, b: float) -> float:
                if a < 0.5:
                    return 2 * a * b
                else:
                    return 1 - 2 * (1 - a) * (1 - b)
            
            result = Color(
                overlay_channel(color1.r, color2.r),
                overlay_channel(color1.g, color2.g),
                overlay_channel(color1.b, color2.b)
            )
            return color1.lerp(result, opacity)
        
        elif mode == 'add':
            result = Color(
                min(1, color1.r + color2.r),
                min(1, color1.g + color2.g),
                min(1, color1.b + color2.b)
            )
            return color1.lerp(result, opacity)
        
        elif mode == 'subtract':
            result = Color(
                max(0, color1.r - color2.r),
                max(0, color1.g - color2.g),
                max(0, color1.b - color2.b)
            )
            return color1.lerp(result, opacity)
        
        elif mode == 'difference':
            result = Color(
                abs(color1.r - color2.r),
                abs(color1.g - color2.g),
                abs(color1.b - color2.b)
            )
            return color1.lerp(result, opacity)
        
        else:
            raise ValueError(f"Unknown blend mode: {mode}")
    
    @staticmethod
    def brightness(color: Color, amount: float) -> Color:
        """Adjust brightness of color."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        v = np.clip(v + amount, 0, 1)
        return ColorSpaceConversions.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def saturation(color: Color, amount: float) -> Color:
        """Adjust saturation of color."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        s = np.clip(s + amount, 0, 1)
        return ColorSpaceConversions.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def hue_shift(color: Color, amount: float) -> Color:
        """Shift hue of color."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        h = (h + amount) % 1
        return ColorSpaceConversions.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def contrast(color: Color, amount: float) -> Color:
        """Adjust contrast of color."""
        return Color(
            0.5 + (color.r - 0.5) * (1 + amount),
            0.5 + (color.g - 0.5) * (1 + amount),
            0.5 + (color.b - 0.5) * (1 + amount),
            color.a
        )
    
    @staticmethod
    def gamma(color: Color, gamma: float) -> Color:
        """Apply gamma correction."""
        inv_gamma = 1.0 / gamma
        return Color(
            color.r ** inv_gamma,
            color.g ** inv_gamma,
            color.b ** inv_gamma,
            color.a
        )
    
    @staticmethod
    def grayscale(color: Color, method: str = 'luminance') -> Color:
        """Convert to grayscale."""
        if method == 'average':
            gray = (color.r + color.g + color.b) / 3
        elif method == 'luminance':
            # ITU-R BT.709 luminance coefficients
            gray = 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b
        elif method == 'desaturate':
            max_val = max(color.r, color.g, color.b)
            min_val = min(color.r, color.g, color.b)
            gray = (max_val + min_val) / 2
        else:
            raise ValueError(f"Unknown grayscale method: {method}")
        
        return Color(gray, gray, gray, color.a)
    
    @staticmethod
    def invert(color: Color) -> Color:
        """Invert color."""
        return Color(1 - color.r, 1 - color.g, 1 - color.b, color.a)


class ColorHarmonies:
    """Generate color harmonies and palettes."""
    
    @staticmethod
    def complementary(color: Color) -> Color:
        """Get complementary color."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        h = (h + 0.5) % 1
        return ColorSpaceConversions.hsv_to_rgb(h, s, v)
    
    @staticmethod
    def analogous(color: Color, angle: float = 30) -> Tuple[Color, Color]:
        """Get analogous colors."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        angle_norm = angle / 360
        
        h1 = (h + angle_norm) % 1
        h2 = (h - angle_norm) % 1
        
        return (
            ColorSpaceConversions.hsv_to_rgb(h1, s, v),
            ColorSpaceConversions.hsv_to_rgb(h2, s, v)
        )
    
    @staticmethod
    def triadic(color: Color) -> Tuple[Color, Color]:
        """Get triadic colors."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        
        h1 = (h + 1/3) % 1
        h2 = (h + 2/3) % 1
        
        return (
            ColorSpaceConversions.hsv_to_rgb(h1, s, v),
            ColorSpaceConversions.hsv_to_rgb(h2, s, v)
        )
    
    @staticmethod
    def tetradic(color: Color) -> Tuple[Color, Color, Color]:
        """Get tetradic (square) colors."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        
        h1 = (h + 0.25) % 1
        h2 = (h + 0.5) % 1
        h3 = (h + 0.75) % 1
        
        return (
            ColorSpaceConversions.hsv_to_rgb(h1, s, v),
            ColorSpaceConversions.hsv_to_rgb(h2, s, v),
            ColorSpaceConversions.hsv_to_rgb(h3, s, v)
        )
    
    @staticmethod
    def split_complementary(color: Color, angle: float = 30) -> Tuple[Color, Color]:
        """Get split-complementary colors."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        angle_norm = angle / 360
        
        h_comp = (h + 0.5) % 1
        h1 = (h_comp + angle_norm) % 1
        h2 = (h_comp - angle_norm) % 1
        
        return (
            ColorSpaceConversions.hsv_to_rgb(h1, s, v),
            ColorSpaceConversions.hsv_to_rgb(h2, s, v)
        )
    
    @staticmethod
    def monochromatic(color: Color, count: int = 5) -> List[Color]:
        """Generate monochromatic color scheme."""
        h, s, v = ColorSpaceConversions.rgb_to_hsv(color)
        colors = []
        
        for i in range(count):
            # Vary brightness
            v_new = (i + 1) / (count + 1)
            colors.append(ColorSpaceConversions.hsv_to_rgb(h, s, v_new))
        
        return colors


class ColorMetrics:
    """Color difference and perception metrics."""
    
    @staticmethod
    def delta_e_cie76(color1: Color, color2: Color) -> float:
        """Calculate CIE76 Delta E color difference."""
        l1, a1, b1 = ColorSpaceConversions.rgb_to_lab(color1)
        l2, a2, b2 = ColorSpaceConversions.rgb_to_lab(color2)
        
        return np.sqrt((l2 - l1)**2 + (a2 - a1)**2 + (b2 - b1)**2)
    
    @staticmethod
    def delta_e_cie2000(color1: Color, color2: Color) -> float:
        """Calculate CIE2000 Delta E color difference (more accurate)."""
        l1, a1, b1 = ColorSpaceConversions.rgb_to_lab(color1)
        l2, a2, b2 = ColorSpaceConversions.rgb_to_lab(color2)
        
        # Constants
        kL = kC = kH = 1
        
        # Calculate C and h
        c1 = np.sqrt(a1**2 + b1**2)
        c2 = np.sqrt(a2**2 + b2**2)
        c_avg = (c1 + c2) / 2
        
        g = 0.5 * (1 - np.sqrt(c_avg**7 / (c_avg**7 + 25**7)))
        a1_prime = (1 + g) * a1
        a2_prime = (1 + g) * a2
        
        c1_prime = np.sqrt(a1_prime**2 + b1**2)
        c2_prime = np.sqrt(a2_prime**2 + b2**2)
        
        h1_prime = np.arctan2(b1, a1_prime) % (2 * np.pi)
        h2_prime = np.arctan2(b2, a2_prime) % (2 * np.pi)
        
        # Calculate deltas
        delta_l_prime = l2 - l1
        delta_c_prime = c2_prime - c1_prime
        
        h_diff = h2_prime - h1_prime
        if h_diff > np.pi:
            h_diff -= 2 * np.pi
        elif h_diff < -np.pi:
            h_diff += 2 * np.pi
        
        delta_h_prime = 2 * np.sqrt(c1_prime * c2_prime) * np.sin(h_diff / 2)
        
        # Calculate averages
        l_avg = (l1 + l2) / 2
        c_prime_avg = (c1_prime + c2_prime) / 2
        
        h_prime_avg = (h1_prime + h2_prime) / 2
        if abs(h1_prime - h2_prime) > np.pi:
            h_prime_avg += np.pi
        
        # Calculate T
        t = (1 - 0.17 * np.cos(h_prime_avg - np.pi/6) +
             0.24 * np.cos(2 * h_prime_avg) +
             0.32 * np.cos(3 * h_prime_avg + np.pi/30) -
             0.20 * np.cos(4 * h_prime_avg - 63*np.pi/180))
        
        # Calculate SL, SC, SH
        sl = 1 + (0.015 * (l_avg - 50)**2) / np.sqrt(20 + (l_avg - 50)**2)
        sc = 1 + 0.045 * c_prime_avg
        sh = 1 + 0.015 * c_prime_avg * t
        
        # Calculate RT
        delta_theta = 30 * np.exp(-((h_prime_avg - 275*np.pi/180) / (25*np.pi/180))**2)
        rc = 2 * np.sqrt(c_prime_avg**7 / (c_prime_avg**7 + 25**7))
        rt = -np.sin(2 * delta_theta * np.pi/180) * rc
        
        # Final calculation
        delta_e = np.sqrt(
            (delta_l_prime / (kL * sl))**2 +
            (delta_c_prime / (kC * sc))**2 +
            (delta_h_prime / (kH * sh))**2 +
            rt * (delta_c_prime / (kC * sc)) * (delta_h_prime / (kH * sh))
        )
        
        return delta_e
    
    @staticmethod
    def perceived_brightness(color: Color) -> float:
        """Calculate perceived brightness using relative luminance."""
        # ITU-R BT.709
        return 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b
    
    @staticmethod
    def contrast_ratio(color1: Color, color2: Color) -> float:
        """Calculate contrast ratio between two colors (WCAG)."""
        l1 = ColorMetrics.perceived_brightness(color1) + 0.05
        l2 = ColorMetrics.perceived_brightness(color2) + 0.05
        
        return max(l1, l2) / min(l1, l2)


class ColorTemperature:
    """Color temperature utilities."""
    
    @staticmethod
    def kelvin_to_rgb(temperature: float) -> Color:
        """Convert color temperature (Kelvin) to RGB."""
        # Clamp temperature to reasonable range
        temp = np.clip(temperature, 1000, 40000) / 100
        
        # Calculate red
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = np.clip(red, 0, 255)
        
        # Calculate green
        if temp <= 66:
            green = temp
            green = 99.4708025861 * np.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = np.clip(green, 0, 255)
        
        # Calculate blue
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * np.log(blue) - 305.0447927307
            blue = np.clip(blue, 0, 255)
        
        return Color(red/255, green/255, blue/255)
    
    @staticmethod
    def rgb_to_temperature(color: Color) -> float:
        """Estimate color temperature from RGB (approximate)."""
        # This is an approximation based on the dominant channel
        r, g, b = color.r, color.g, color.b
        
        # Normalize to max channel
        max_val = max(r, g, b)
        if max_val == 0:
            return 6500  # Default daylight
        
        r_norm = r / max_val
        g_norm = g / max_val
        b_norm = b / max_val
        
        # Estimate based on ratios
        if r_norm >= g_norm and r_norm >= b_norm:
            # Warm (low temperature)
            return 2000 + (1 - b_norm) * 2000
        elif b_norm >= r_norm and b_norm >= g_norm:
            # Cool (high temperature)
            return 6500 + (1 - r_norm) * 3500
        else:
            # Neutral
            return 5500


# Convenience functions
def rgb(r: float, g: float, b: float, a: float = 1.0) -> Color:
    """Create RGB color."""
    return Color(r, g, b, a)


def rgb255(r: int, g: int, b: int, a: int = 255) -> Color:
    """Create color from 0-255 values."""
    return Color.from_rgb255(r, g, b, a)


def hex_color(hex_string: str) -> Color:
    """Create color from hex string."""
    return Color.from_hex(hex_string)


def hsv(h: float, s: float, v: float, a: float = 1.0) -> Color:
    """Create color from HSV values."""
    color = ColorSpaceConversions.hsv_to_rgb(h, s, v)
    color.a = a
    return color


def hsl(h: float, s: float, l: float, a: float = 1.0) -> Color:
    """Create color from HSL values."""
    color = ColorSpaceConversions.hsl_to_rgb(h, s, l)
    color.a = a
    return color


def interpolate_colors(colors: List[Color], t: float, 
                      space: str = 'rgb') -> Color:
    """Interpolate between multiple colors."""
    if not colors:
        return Color(0, 0, 0)
    if len(colors) == 1:
        return colors[0]
    
    t = np.clip(t, 0, 1)
    scaled_t = t * (len(colors) - 1)
    index = int(scaled_t)
    local_t = scaled_t - index
    
    if index >= len(colors) - 1:
        return colors[-1]
    
    if space == 'rgb':
        return colors[index].lerp(colors[index + 1], local_t)
    elif space == 'hsv':
        h1, s1, v1 = ColorSpaceConversions.rgb_to_hsv(colors[index])
        h2, s2, v2 = ColorSpaceConversions.rgb_to_hsv(colors[index + 1])
        
        # Handle hue wrapping
        if abs(h2 - h1) > 0.5:
            if h1 > h2:
                h2 += 1
            else:
                h1 += 1
        
        h = h1 + (h2 - h1) * local_t
        s = s1 + (s2 - s1) * local_t
        v = v1 + (v2 - v1) * local_t
        
        return ColorSpaceConversions.hsv_to_rgb(h % 1, s, v)
    elif space == 'lab':
        l1, a1, b1 = ColorSpaceConversions.rgb_to_lab(colors[index])
        l2, a2, b2 = ColorSpaceConversions.rgb_to_lab(colors[index + 1])
        
        l = l1 + (l2 - l1) * local_t
        a = a1 + (a2 - a1) * local_t
        b = b1 + (b2 - b1) * local_t
        
        return ColorSpaceConversions.lab_to_rgb(l, a, b)
    else:
        raise ValueError(f"Unknown color space: {space}")


# Color constants
class Colors:
    """Common color constants."""
    # Primary colors
    RED = Color(1, 0, 0)
    GREEN = Color(0, 1, 0)
    BLUE = Color(0, 0, 1)
    
    # Secondary colors
    CYAN = Color(0, 1, 1)
    MAGENTA = Color(1, 0, 1)
    YELLOW = Color(1, 1, 0)
    
    # Neutral colors
    WHITE = Color(1, 1, 1)
    BLACK = Color(0, 0, 0)
    GRAY = Color(0.5, 0.5, 0.5)
    
    # Common colors
    ORANGE = Color(1, 0.5, 0)
    PURPLE = Color(0.5, 0, 0.5)
    PINK = Color(1, 0.75, 0.8)
    BROWN = Color(0.6, 0.3, 0.1)
    
    # Transparent
    TRANSPARENT = Color(0, 0, 0, 0)