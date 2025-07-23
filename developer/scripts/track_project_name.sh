#!/bin/bash

# Script to track every mention and declaration of the manim_studio project name

echo "=== Tracking all mentions of manim_studio project name ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Output file
OUTPUT_FILE="project_name_mentions.txt"

# Clear output file
> "$OUTPUT_FILE"

echo "Project Name Tracking Report" > "$OUTPUT_FILE"
echo "===========================" >> "$OUTPUT_FILE"
echo "Generated on: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Function to search using grep (more reliable)
search_with_grep() {
    local pattern="$1"
    local description="$2"
    
    echo -e "${BLUE}Searching for: ${YELLOW}$description${NC}"
    echo "" >> "$OUTPUT_FILE"
    echo "Pattern: $description" >> "$OUTPUT_FILE"
    echo "----------------------------------------" >> "$OUTPUT_FILE"
    
    # Use grep -r for recursive search
    local count=0
    while IFS= read -r file; do
        # Skip binary files and certain directories
        if [[ "$file" == *".git"* ]] || [[ "$file" == *"node_modules"* ]] || 
           [[ "$file" == *"__pycache__"* ]] || [[ "$file" == *".pyc" ]] ||
           [[ "$file" == *"project_name_mentions.txt" ]] || 
           [[ "$file" == *"track_project_name.sh" ]]; then
            continue
        fi
        
        # Search in the file
        grep -n "$pattern" "$file" 2>/dev/null | while IFS= read -r line; do
            echo "$file:$line" >> "$OUTPUT_FILE"
            ((count++))
        done
    done < <(find . -type f -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.sh" -o -name "*.toml" 2>/dev/null)
    
    local total_count=$(grep -c "^[^:]*:" "$OUTPUT_FILE" 2>/dev/null || echo "0")
    echo -e "${GREEN}Found matches in files${NC}"
    echo "" >> "$OUTPUT_FILE"
}

# Search for variations
echo "Searching for project name variations..."
echo ""

# Main searches
search_with_grep "manim_studio" "Snake case (manim_studio)"
search_with_grep "manim-studio" "Kebab case (manim-studio)"
search_with_grep "ManimStudio" "PascalCase (ManimStudio)"
search_with_grep "Manim Studio" "Title case with space (Manim Studio)"

# Configuration file specific check
echo "" >> "$OUTPUT_FILE"
echo "Configuration Files" >> "$OUTPUT_FILE"
echo "==================" >> "$OUTPUT_FILE"

if [ -f "setup.py" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "setup.py:" >> "$OUTPUT_FILE"
    grep -n "name.*=" setup.py 2>/dev/null >> "$OUTPUT_FILE" || echo "  No name field found" >> "$OUTPUT_FILE"
fi

if [ -f "pyproject.toml" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "pyproject.toml:" >> "$OUTPUT_FILE"
    grep -n "name.*=" pyproject.toml 2>/dev/null >> "$OUTPUT_FILE" || echo "  No name field found" >> "$OUTPUT_FILE"
fi

# Summary
echo "" >> "$OUTPUT_FILE"
echo "Summary" >> "$OUTPUT_FILE"
echo "=======" >> "$OUTPUT_FILE"

# Count occurrences by pattern
echo "" >> "$OUTPUT_FILE"
echo "Occurrences by pattern:" >> "$OUTPUT_FILE"
for pattern in "manim_studio" "manim-studio" "ManimStudio" "Manim Studio"; do
    count=$(grep -r "$pattern" . --include="*.py" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.md" --include="*.txt" --include="*.sh" --include="*.toml" 2>/dev/null | grep -v "project_name_mentions.txt" | grep -v "track_project_name.sh" | wc -l)
    echo "  $pattern: $count occurrences" >> "$OUTPUT_FILE"
done

# Files with most mentions
echo "" >> "$OUTPUT_FILE"
echo "Files with project name mentions:" >> "$OUTPUT_FILE"
grep -r "manim_studio\|manim-studio\|ManimStudio\|Manim Studio" . --include="*.py" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.md" --include="*.txt" --include="*.sh" --include="*.toml" 2>/dev/null | 
    grep -v "project_name_mentions.txt" | 
    grep -v "track_project_name.sh" | 
    cut -d: -f1 | sort | uniq -c | sort -nr | head -10 >> "$OUTPUT_FILE"

# Display completion message
echo -e "\n${GREEN}Search complete!${NC}"
echo -e "Results saved to: ${YELLOW}$OUTPUT_FILE${NC}"
echo ""
echo -e "${BLUE}View results with:${NC} cat $OUTPUT_FILE"
echo -e "${BLUE}Or page through:${NC} less $OUTPUT_FILE"