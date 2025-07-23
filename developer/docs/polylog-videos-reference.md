# Polylog Videos Reference

## Source Information

- **Source**: YouTube channel videos source code
- **YouTube Channel**: https://www.youtube.com/channel/UC_IaBSHmisYbiYlv32EeNkQ
- **Location**: `/developer/examples/inspiration/videos/`
- **Date Archived**: 2025-07-23

## Video Collection

### Graph Theory Videos
1. **The Most Elegant Search Structure | (a,b)-trees** (2023/04/09)
   - Introduction to (a,b)-trees – definition, operations, usage
   - Source: `17-ab/`

2. **Cayley's Formula** (2021/10/06)
   - Elegant proof of the number of spanning trees of a complete graph
   - Source: `07-cayley/`

3. **The Blossom Algorithm** (2021/08/23)
   - Overview of the Blossom algorithm for maximum graph matching
   - Source: `06-edmonds-blossom/`

4. **Weak Perfect Graph Theorem** (2021/06/01)
   - Proof of the weak perfect graph theorem
   - Source: `04-perfect-graphs/`

5. **Vizing's theorem** (2021/04/28)
   - Proof of Vizing's theorem about graph edge coloring
   - Source: `03-vizing/`

### Other Topics
1. **The Art of Linear Programming** (2023/7/03)
   - Visual introduction to Linear Programming, Simplex method, and duality
   - Source: `18-lopt/`

2. **Theseus and the Minotaur | Exploring State Space** (2023/1/20)
   - Visual introduction to state space exploration algorithms (BFS, Dijkstra, A*)
   - Source: `12-state-space/`

3. **The Remarkable BEST-SAT Algorithm** (2022/8/16)
   - Deep dive into BEST-SAT approximation algorithm
   - Source: `10-sat/`

4. **Bathroom Tile Programming** (2021/12/31)
   - Unconventional bathroom tile programming model
   - Source: `09-bathroom-tiles/`

### Shorts
1. **What does this weird C program do?** (2022/11/16)
   - Strange C program that adds numbers
   - Source: `14-funf/`

2. **Encoding Numbers using Dots and Parentheses** (2022/11/14)
   - Unique number encoding system
   - Source: `13-primes-dots/`

3. **The real difference between BFS and DFS** (2023/07/10)
   - Comparison of breadth-first and depth-first search
   - Source: `20-dfs-vs-bfs/`

## Key Learnings for Manim Studio

### Animation Techniques
- Complex graph visualizations
- Mathematical proof animations
- Algorithm step-by-step visualization
- State space exploration animations

### Code Organization
- Each video has its own directory with:
  - `scenes.py` - Main animation code
  - `utilities.py` - Helper functions
  - `SCRIPT.md` - Video script
  - `DESCRIPTION.md` - Video description
  - Assets folder for images/SVGs

### Useful Patterns
- Modular scene composition
- Custom utility functions for specific visualizations
- Integration of external assets (SVG, images)
- Script-driven animation timing

## Integration Ideas

1. **Graph Visualization Components**
   - Reusable graph drawing utilities
   - Algorithm animation helpers
   - State transition visualizers

2. **Mathematical Proof Templates**
   - Step-by-step proof animations
   - Theorem visualization patterns
   - Mathematical notation helpers

3. **Educational Animation Patterns**
   - Clear visual explanations
   - Synchronized narration timing
   - Pause points for comprehension

## Notes
- Uses standard Manim patterns
- Heavy use of custom utilities for each video
- Well-documented with scripts and descriptions
- Includes build scripts and configuration files