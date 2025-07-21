"""Demo script to test caching functionality in Manim Studio."""

from manim import *
from src.core import AssetManager, get_cache, configure_cache
import time


class CacheDemo(Scene):
    """Demonstrates caching functionality."""
    
    def construct(self):
        # Configure cache with custom settings
        configure_cache(
            cache_dir="./demo_cache",
            max_size_mb=100,
            ttl_seconds=3600,  # 1 hour
            enabled=True
        )
        
        # Get cache instance
        cache = get_cache()
        
        # Show initial cache stats
        stats = cache.get_stats()
        print("\nInitial Cache Stats:")
        print(f"  Enabled: {stats['enabled']}")
        print(f"  Disk entries: {stats['disk_entries']}")
        print(f"  Disk size: {stats['disk_size_mb']:.2f} MB")
        print(f"  Memory entries: {stats['memory_entries']}")
        print(f"  Memory size: {stats['memory_size_mb']:.2f} MB")
        
        # Create asset manager with caching enabled
        asset_manager = AssetManager(use_cache=True)
        
        # Test caching with decorators
        @cache.cached("fibonacci")
        def fibonacci(n):
            """Compute fibonacci number (cached)."""
            print(f"Computing fibonacci({n})...")
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        # First call - will compute
        start = time.time()
        result1 = fibonacci(10)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        result2 = fibonacci(10)
        time2 = time.time() - start
        
        print(f"\nFibonacci(10) = {result1}")
        print(f"First call took: {time1:.4f} seconds")
        print(f"Second call took: {time2:.4f} seconds (from cache)")
        print(f"Speedup: {time1/time2:.2f}x")
        
        # Create animation showing cache benefits
        title = Text("Manim Studio Cache Demo", font_size=48)
        self.play(Write(title))
        self.wait(1)
        
        # Show computation times
        results = VGroup(
            Text(f"Without Cache: {time1:.4f}s", font_size=36),
            Text(f"With Cache: {time2:.4f}s", font_size=36, color=GREEN),
            Text(f"Speedup: {time1/time2:.2f}x", font_size=40, color=YELLOW)
        ).arrange(DOWN, buff=0.5)
        
        self.play(
            title.animate.shift(UP * 2),
            FadeIn(results)
        )
        
        # Show final cache stats
        final_stats = cache.get_stats()
        print("\nFinal Cache Stats:")
        print(f"  Disk entries: {final_stats['disk_entries']}")
        print(f"  Disk size: {final_stats['disk_size_mb']:.2f} MB")
        print(f"  Memory entries: {final_stats['memory_entries']}")
        print(f"  Memory size: {final_stats['memory_size_mb']:.2f} MB")
        
        self.wait(3)


# Example of using cache with asset loading
class AssetCacheDemo(Scene):
    """Demonstrates asset caching."""
    
    def construct(self):
        # Create asset manager
        asset_manager = AssetManager(use_cache=True)
        
        # Create a placeholder image to demonstrate caching
        # In real use, this would load actual images
        placeholder1 = asset_manager.create_placeholder(
            "example_image.png",
            width=4,
            height=3,
            text="Cached Image"
        )
        
        # Simulate loading the same asset multiple times
        print("\nAsset Loading Times:")
        
        # First load
        start = time.time()
        img1 = placeholder1.copy()
        time1 = time.time() - start
        print(f"  First load: {time1:.4f}s")
        
        # Second load (should be faster due to caching)
        start = time.time()
        img2 = placeholder1.copy()
        time2 = time.time() - start
        print(f"  Second load: {time2:.4f}s")
        
        # Display the assets
        img1.shift(LEFT * 3)
        img2.shift(RIGHT * 3)
        
        self.play(
            FadeIn(img1),
            FadeIn(img2)
        )
        
        # Add labels
        label1 = Text("Original", font_size=24).next_to(img1, DOWN)
        label2 = Text("Cached Copy", font_size=24).next_to(img2, DOWN)
        
        self.play(
            Write(label1),
            Write(label2)
        )
        
        self.wait(2)


if __name__ == "__main__":
    # Run the demos
    from manim import config
    
    # Configure Manim
    config.quality = "m"  # Medium quality for faster rendering
    config.preview = True
    
    # Run cache demo
    scene = CacheDemo()
    scene.render()
    
    # Run asset cache demo
    scene = AssetCacheDemo()
    scene.render()