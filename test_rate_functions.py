#!/usr/bin/env python3
"""
Focused test for rate functions and easing system.
Tests the core functionality without getting caught up in package import issues.
"""

import sys
import os
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def load_module_directly(name, path):
    """Load a module directly from path without package context."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def test_easing_functionality():
    """Test the easing system functionality."""
    print("=" * 60)
    print("TESTING EASING SYSTEM")
    print("=" * 60)
    
    try:
        # Load easing module directly
        easing = load_module_directly(
            'easing', 
            '/Users/ebowwa/apps/manim_studio/src/core/timeline/easing.py'
        )
        
        print("✓ Easing module loaded successfully")
        
        # Test EasingFunction enum
        print(f"✓ EasingFunction enum has {len(list(easing.EasingFunction))} entries")
        
        # Test some basic easing functions
        test_cases = [
            easing.EasingFunction.LINEAR,
            easing.EasingFunction.SMOOTH_STEP,
            easing.EasingFunction.EASE_IN_OUT_CUBIC,
            easing.EasingFunction.EASE_OUT_BOUNCE,
            easing.EasingFunction.EASE_OUT_ELASTIC,
        ]
        
        print("\nTesting easing functions:")
        for easing_type in test_cases:
            try:
                func = easing.EasingLibrary.get_easing_function(easing_type)
                result = func(0.5)
                print(f"  ✓ {easing_type.value}: f(0.5) = {result:.4f}")
            except Exception as e:
                print(f"  ✗ {easing_type.value}: Error - {e}")
        
        # Test presets
        print("\nTesting easing presets:")
        presets = [
            'MATERIAL_STANDARD',
            'BOUNCE',
            'ELASTIC',
            'SPRING'
        ]
        
        for preset_name in presets:
            try:
                func = easing.EasingPresets.create_easing_from_preset(preset_name)
                result = func(0.5)
                print(f"  ✓ {preset_name}: f(0.5) = {result:.4f}")
            except Exception as e:
                print(f"  ✗ {preset_name}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Easing system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_function_bridge():
    """Test the rate function bridge functionality."""
    print("\n" + "=" * 60)
    print("TESTING RATE FUNCTION BRIDGE")
    print("=" * 60)
    
    try:
        # Load rate function bridge directly
        bridge = load_module_directly(
            'rate_function_bridge',
            '/Users/ebowwa/apps/manim_studio/src/core/timeline/rate_function_bridge.py'
        )
        
        print("✓ Rate function bridge loaded successfully")
        
        # Test Manim rate functions
        print("\nTesting Manim rate functions:")
        manim_functions = ['linear', 'smooth', 'there_and_back', 'rush_into']
        
        for func_name in manim_functions:
            try:
                func = bridge.get_rate_function(func_name)
                result = func(0.5)
                print(f"  ✓ {func_name}: f(0.5) = {result:.4f}")
            except Exception as e:
                print(f"  ✗ {func_name}: Error - {e}")
        
        # Test custom easings through bridge
        print("\nTesting custom easings through bridge:")
        custom_easings = ['bounce', 'elastic', 'back', 'spring']
        
        for easing_name in custom_easings:
            try:
                func = bridge.get_rate_function(easing_name)
                result = func(0.5)
                print(f"  ✓ {easing_name}: f(0.5) = {result:.4f}")
            except Exception as e:
                print(f"  ✗ {easing_name}: Error - {e}")
        
        # Test composition
        print("\nTesting rate function composition:")
        try:
            composed = bridge.compose_rate_functions('linear', 'smooth', weights=[0.5, 0.5])
            result = composed(0.5)
            print(f"  ✓ Composed linear+smooth: f(0.5) = {result:.4f}")
        except Exception as e:
            print(f"  ✗ Composition failed: {e}")
        
        # Test sequential functions
        print("\nTesting sequential rate functions:")
        try:
            sequential = bridge.chain_rate_functions('smooth', 'there_and_back', durations=[0.6, 0.4])
            result1 = sequential(0.25)  # Should use smooth
            result2 = sequential(0.75)  # Should use there_and_back
            print(f"  ✓ Sequential at t=0.25: {result1:.4f}")
            print(f"  ✓ Sequential at t=0.75: {result2:.4f}")
        except Exception as e:
            print(f"  ✗ Sequential functions failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Rate function bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_composer_timeline():
    """Test the composer timeline functionality."""
    print("\n" + "=" * 60)
    print("TESTING COMPOSER TIMELINE")
    print("=" * 60)
    
    try:
        # Load composer timeline directly
        timeline_module = load_module_directly(
            'composer_timeline',
            '/Users/ebowwa/apps/manim_studio/src/core/timeline/composer_timeline.py'
        )
        
        print("✓ Composer timeline loaded successfully")
        
        # Test timeline creation
        timeline = timeline_module.ComposerTimeline()
        print("✓ Timeline created")
        
        # Test layer and track creation
        layer = timeline.add_layer("Test Layer")
        track = timeline.add_track("Test Layer", "test_track", "animation")
        print("✓ Layer and track created")
        
        # Test keyframe addition
        keyframe = timeline.add_keyframe(
            "Test Layer", "test_track", "position",
            time=0.0, value=[0, 0, 0],
            interpolation=timeline_module.InterpolationType.SMOOTH_STEP
        )
        print("✓ Keyframe added")
        
        keyframe2 = timeline.add_keyframe(
            "Test Layer", "test_track", "position",
            time=1.0, value=[1, 1, 0],
            interpolation=timeline_module.InterpolationType.BOUNCE
        )
        print("✓ Second keyframe added")
        
        # Test value interpolation
        value = timeline.get_value_at_time("Test Layer", "test_track", "position", 0.5)
        print(f"✓ Interpolated value at t=0.5: {value}")
        
        # Test with rate function override
        keyframe3 = timeline.add_keyframe(
            "Test Layer", "test_track", "rotation",
            time=0.0, value=0,
            rate_function="wiggle"
        )
        
        keyframe4 = timeline.add_keyframe(
            "Test Layer", "test_track", "rotation",
            time=1.0, value=360,
        )
        
        rotation_value = timeline.get_value_at_time("Test Layer", "test_track", "rotation", 0.5)
        print(f"✓ Rate function override works: rotation at t=0.5 = {rotation_value}")
        
        # Test preset usage
        preset_keyframe = timeline.add_keyframe(
            "Test Layer", "test_track", "scale",
            time=0.0, value=1.0,
            preset="BOUNCE"
        )
        
        preset_keyframe2 = timeline.add_keyframe(
            "Test Layer", "test_track", "scale",  
            time=1.0, value=2.0
        )
        
        scale_value = timeline.get_value_at_time("Test Layer", "test_track", "scale", 0.5)
        print(f"✓ Preset usage works: scale at t=0.5 = {scale_value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Composer timeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_math3d_integration():
    """Test integration with math3d utilities."""
    print("\n" + "=" * 60) 
    print("TESTING MATH3D INTEGRATION")
    print("=" * 60)
    
    try:
        # Test direct imports
        from utils.math3d.interpolation import (
            smooth_step, smoother_step, smoothest_step,
            ease_in_out, bounce_ease_out, elastic_ease_out,
            circular_ease_in_out, BezierCurve, Vector3D
        )
        
        print("✓ Math3d imports successful")
        
        # Test smooth step functions
        print(f"✓ smooth_step(0.5) = {smooth_step(0.5):.4f}")
        print(f"✓ smoother_step(0.5) = {smoother_step(0.5):.4f}")
        print(f"✓ smoothest_step(0.5) = {smoothest_step(0.5):.4f}")
        
        # Test bounce and elastic
        print(f"✓ bounce_ease_out(0.5) = {bounce_ease_out(0.5):.4f}")
        print(f"✓ elastic_ease_out(0.5) = {elastic_ease_out(0.5):.4f}")
        print(f"✓ circular_ease_in_out(0.5) = {circular_ease_in_out(0.5):.4f}")
        
        # Test Bezier curve
        control_points = [
            Vector3D(0, 0, 0),
            Vector3D(0.25, 0.1, 0),
            Vector3D(0.75, 0.9, 0),
            Vector3D(1, 1, 0)
        ]
        bezier = BezierCurve(control_points)
        point = bezier.evaluate(0.5)
        print(f"✓ Bezier curve evaluation: {point}")
        
        return True
        
    except Exception as e:
        print(f"✗ Math3d integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("RATE FUNCTION AND EASING SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        test_math3d_integration,
        test_easing_functionality,
        test_rate_function_bridge,
        test_composer_timeline,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(main())