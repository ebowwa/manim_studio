#!/bin/bash
# Render the comprehensive Manim Studio feature showcase

echo "🎬 Manim Studio - Comprehensive Feature Showcase Renderer"
echo "========================================================="
echo ""
echo "This will render a 3-minute video demonstrating ALL features of Manim Studio."
echo ""

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the manim_studio directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Quality options
echo "Select rendering quality:"
echo "1) Low (480p) - Fastest, ~5 minutes"
echo "2) Medium (720p) - Good quality, ~10 minutes"
echo "3) High (1080p) - Full HD, ~15 minutes"
echo "4) Production (1440p) - Best quality, ~20 minutes"
echo ""
read -p "Enter choice (1-4) [default: 2]: " quality_choice

case $quality_choice in
    1) QUALITY="-q l"; QUALITY_NAME="480p" ;;
    3) QUALITY="-q h"; QUALITY_NAME="1080p" ;;
    4) QUALITY="-q p"; QUALITY_NAME="1440p" ;;
    *) QUALITY="-q m"; QUALITY_NAME="720p" ;;
esac

echo ""
echo "🎯 Rendering at $QUALITY_NAME quality..."
echo ""

# Create a timestamp for the output
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_NAME="comprehensive_showcase_${TIMESTAMP}_${QUALITY_NAME}.mp4"

# Run the render command
echo "⚙️  Starting render process..."
echo "📁 Output will be saved to: user-data/ComprehensiveFeatureShowcase/${QUALITY_NAME}/"
echo ""

# Use the manim-studio command with media_dir specified
python main.py configs/comprehensive_feature_showcase.yaml $QUALITY --media_dir user-data -p

# Check if render was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Render completed successfully!"
    echo ""
    echo "📍 Video location:"
    echo "   user-data/ComprehensiveFeatureShowcase/${QUALITY_NAME}/ComprehensiveFeatureShowcase.mp4"
    echo ""
    echo "📊 Video details:"
    echo "   - Duration: 3 minutes"
    echo "   - Resolution: $QUALITY_NAME"
    echo "   - Features demonstrated:"
    echo "     • Basic shapes and text objects"
    echo "     • CAD technical drawing components"
    echo "     • Physics simulations (pendulum, spring, projectile)"
    echo "     • Hyperplane and SVM visualizations"
    echo "     • Visual arrays and sorting animations"
    echo "     • Viral video effects and transitions"
    echo "     • 3D model loading and animation"
    echo "     • Advanced camera movements"
    echo "     • Special effects (glow, particles, neon, lens flare)"
    echo "     • Post-processing effects"
    echo ""
    echo "🎉 Enjoy your comprehensive showcase!"
else
    echo ""
    echo "❌ Render failed. Please check the error messages above."
    echo "💡 Common issues:"
    echo "   - Missing dependencies: pip install -e ."
    echo "   - Invalid YAML syntax: python developer/scripts/validate_yaml.py configs/comprehensive_feature_showcase.yaml"
    echo "   - Missing assets: Check that placeholder assets exist"
fi