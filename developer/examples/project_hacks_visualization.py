"""
Video visualization of project-specific hacks found in xiaoxiae's repository.
This scene reads from project_specific_hacks.yaml and creates an educational video
about real-world Manim production challenges and workarounds.
"""

from manim import *
import yaml
from pathlib import Path

class ProjectHacksVisualization(Scene):
    def construct(self):
        # Load the YAML data
        yaml_path = Path("/Users/ebowwa/apps/manim_studio/project_specific_hacks.yaml")
        with open(yaml_path, 'r') as file:
            hack_data = yaml.safe_load(file)
        
        # Title sequence
        self.create_title_sequence(hack_data['metadata'])
        
        # Overview of categories
        self.show_hack_categories(hack_data['metadata']['categories'])
        
        # Detailed examples
        self.show_circumscribe_hack(hack_data['animation_workarounds']['circumscribe_hack'])
        self.show_positioning_hacks(hack_data['positioning_hacks']['tile_specific_adjustments'])
        self.show_magic_numbers(hack_data['magic_numbers']['bathroom_tiles_constants'])
        
        # Analysis summary
        self.show_analysis_summary(hack_data['analysis_summary'])
        
        # Call to action
        self.create_outro()
    
    def create_title_sequence(self, metadata):
        """Create opening title sequence"""
        # Main title
        title = Text("Project-Specific Hacks", font_size=56, weight=BOLD, color=YELLOW)
        subtitle = Text("Real-World Manim Production Challenges", font_size=36, color=GRAY)
        
        # Repository info
        repo_info = Text(f"Extracted from: {metadata['repository']}", font_size=24)
        stats = Text(f"{metadata['total_hacks_found']} hacks found across {len(metadata['categories'])} categories", 
                    font_size=20, color=GREEN)
        
        # Arrange elements
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        info_group = VGroup(repo_info, stats).arrange(DOWN, buff=0.3).to_edge(DOWN)
        
        # Animations
        self.play(FadeIn(title_group, shift=UP))
        self.wait(1)
        self.play(Write(info_group))
        self.wait(2)
        self.play(FadeOut(title_group), FadeOut(info_group))
    
    def show_hack_categories(self, categories):
        """Show overview of hack categories"""
        title = Text("Categories of Hacks Found", font_size=48, color=BLUE).to_edge(UP)
        
        # Create category cards
        category_cards = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, GRAY, WHITE, TEAL]
        
        for i, category in enumerate(categories):
            # Clean up category name for display
            display_name = category.replace('_', ' ').title()
            
            # Create card
            card = RoundedRectangle(
                width=2.5, height=1.2, 
                corner_radius=0.1,
                fill_color=colors[i % len(colors)],
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=2
            )
            
            text = Text(display_name, font_size=16, color=BLACK, weight=BOLD)
            text.move_to(card)
            
            card_group = VGroup(card, text)
            category_cards.add(card_group)
        
        # Arrange in grid
        category_cards.arrange_in_grid(rows=2, cols=5, buff=0.3)
        category_cards.move_to(ORIGIN)
        
        # Animate
        self.play(Write(title))
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP*0.2) for card in category_cards],
                lag_ratio=0.1
            )
        )
        self.wait(2)
        self.play(FadeOut(title), FadeOut(category_cards))
    
    def show_circumscribe_hack(self, hack_data):
        """Demonstrate the Circumscribe performance hack"""
        title = Text("Animation Workaround: Circumscribe Hack", font_size=40, color=RED).to_edge(UP)
        
        # Problem description
        problem_text = Text("Problem: Built-in Circumscribe has poor performance", 
                          font_size=24, color=YELLOW).next_to(title, DOWN, buff=0.5)
        
        # Show the hack code
        code_text = Code(
            code_string=hack_data['code'].strip(),
            language="python",
            formatter_style="monokai"
        ).scale(0.8).next_to(problem_text, DOWN, buff=0.5)
        
        # Demonstration
        # Create objects to circumscribe
        objects = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT*2),
            Square(side_length=1, color=GREEN),
            Triangle().scale(0.7).shift(RIGHT*2).set_color(PURPLE)
        ).shift(DOWN*2)
        
        # Show normal vs hack approach
        normal_label = Text("Normal Circumscribe", font_size=20, color=GRAY)
        hack_label = Text("Hack Circumscribe", font_size=20, color=GREEN)
        
        labels = VGroup(normal_label, hack_label).arrange(RIGHT, buff=4).next_to(objects, DOWN)
        
        self.play(Write(title), Write(problem_text))
        self.play(Create(code_text))
        self.play(Create(objects), Write(labels))
        
        # Demonstrate the difference
        normal_circ = Circle(radius=0.8, color=YELLOW, stroke_width=4).move_to(objects[0])
        hack_circ = Circle(radius=0.8, color=GREEN, stroke_width=4).move_to(objects[2])
        
        # Show "poor" performance vs smooth performance
        self.play(
            Create(normal_circ, run_time=2),  # Slow/choppy
            Create(hack_circ, run_time=0.5),   # Fast/smooth
        )
        
        # Technical debt indicator
        debt_indicator = Text(f"Technical Debt: {hack_data['technical_debt'].title()}", 
                            font_size=18, color=ORANGE).to_corner(DR)
        self.play(FadeIn(debt_indicator))
        
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))
    
    def show_positioning_hacks(self, hack_data):
        """Show manual positioning adjustments"""
        title = Text("Positioning Hacks: Manual Micro-adjustments", font_size=36, color=ORANGE).to_edge(UP)
        
        # Problem visualization
        problem_text = Text("Reality: Video production requires pixel-perfect tweaks", 
                          font_size=24, color=YELLOW).next_to(title, DOWN)
        
        # Show code examples
        examples = VGroup()
        for i, instance in enumerate(hack_data['instances']):
            code = Code(
                code_string=instance['code'].strip(),
                language="python",
                formatter_style="monokai"
            ).scale(0.6)
            examples.add(code)
        
        examples.arrange(DOWN, buff=0.3).next_to(problem_text, DOWN)
        
        # Visual demonstration of micro-adjustments
        base_objects = VGroup()
        adjusted_objects = VGroup()
        
        for i in range(3):
            # Base position
            base_rect = Rectangle(width=1, height=0.5, color=BLUE, fill_opacity=0.5)
            base_rect.shift(LEFT*2 + UP*(1-i*0.7))
            base_objects.add(base_rect)
            
            # Adjusted position (with micro-shifts)
            adj_rect = base_rect.copy().set_color(GREEN)
            if i == 0:
                adj_rect.shift(UP * 0.07)  # Micro-adjustment
            elif i == 1:
                adj_rect.shift(UP * 0.08 + LEFT * 0.02)
            else:
                adj_rect.shift(RIGHT * 0.1)
            adjusted_objects.add(adj_rect)
        
        # Labels
        before_label = Text("Before", font_size=16, color=BLUE).next_to(base_objects, LEFT)
        after_label = Text("After", font_size=16, color=GREEN).next_to(adjusted_objects, RIGHT)
        
        demo_group = VGroup(base_objects, adjusted_objects, before_label, after_label)
        demo_group.scale(0.8).to_edge(RIGHT)
        
        self.play(Write(title), Write(problem_text))
        self.play(Create(examples))
        self.play(Create(demo_group))
        
        # Animate the adjustments
        arrows = VGroup()
        for base, adj in zip(base_objects, adjusted_objects):
            arrow = Arrow(base.get_center(), adj.get_center(), 
                         color=YELLOW, stroke_width=2, max_tip_length_to_length_ratio=0.3)
            arrows.add(arrow)
        
        self.play(Create(arrows))
        self.wait(2)
        
        # Technical debt warning
        warning = Text(f"Technical Debt: {hack_data['technical_debt'].upper()}", 
                      font_size=20, color=RED, weight=BOLD).to_corner(DR)
        self.play(FadeIn(warning, scale=1.2))
        
        self.wait(1)
        self.play(FadeOut(Group(*self.mobjects)))
    
    def show_magic_numbers(self, hack_data):
        """Visualize magic numbers and constants"""
        title = Text("Magic Numbers: Video-Specific Constants", font_size=36, color=PURPLE).to_edge(UP)
        
        # Create visual representation of constants
        constants_display = VGroup()
        
        y_pos = 2
        for const_name, value in hack_data['constants'].items():
            # Constant name
            name_text = Text(f"{const_name}:", font_size=18, color=BLUE)
            
            # Value with visual representation
            if isinstance(value, (int, float)):
                value_text = Text(f"{value}", font_size=18, color=YELLOW)
                # Visual bar representing the value
                bar_width = min(abs(float(value)) * 0.5, 3)  # Scale for visibility
                bar = Rectangle(width=bar_width, height=0.2, 
                              fill_color=GREEN, fill_opacity=0.7)
                bar.next_to(value_text, RIGHT, buff=0.2)
                const_group = VGroup(name_text, value_text, bar)
            else:
                value_text = Text(f'"{value}"', font_size=18, color=YELLOW)
                const_group = VGroup(name_text, value_text)
            
            const_group.arrange(RIGHT, buff=0.3)
            const_group.move_to(UP * y_pos)
            constants_display.add(const_group)
            y_pos -= 0.4
        
        constants_display.to_edge(LEFT)
        
        # Problem illustration
        problem_box = RoundedRectangle(
            width=4, height=3,
            corner_radius=0.2,
            stroke_color=RED,
            stroke_width=3,
            fill_color=RED,
            fill_opacity=0.1
        ).to_edge(RIGHT)
        
        problem_title = Text("Problems:", font_size=20, color=RED, weight=BOLD)
        problems = VGroup(
            Text("• Video-specific", font_size=16),
            Text("• Hard to maintain", font_size=16),
            Text("• Not reusable", font_size=16),
            Text("• Magic calculations", font_size=16)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        
        problem_content = VGroup(problem_title, problems).arrange(DOWN, buff=0.3)
        problem_content.move_to(problem_box)
        
        self.play(Write(title))
        self.play(
            LaggedStart(
                *[FadeIn(const, shift=RIGHT*0.2) for const in constants_display],
                lag_ratio=0.2
            )
        )
        self.play(Create(problem_box), Write(problem_content))
        
        # Solution suggestion
        solution = Text("Solution: Theme-based scaling system", 
                       font_size=18, color=GREEN).to_edge(DOWN)
        self.play(FadeIn(solution, shift=UP*0.2))
        
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))
    
    def show_analysis_summary(self, analysis_data):
        """Show the overall analysis summary"""
        title = Text("Analysis Summary", font_size=48, color=GOLD).to_edge(UP)
        
        # Technical debt level
        debt_level = analysis_data['total_technical_debt']
        debt_text = Text(f"Overall Technical Debt: {debt_level.title()}", 
                        font_size=24, color=RED if 'high' in debt_level else ORANGE)
        
        # Most common patterns
        patterns_title = Text("Most Common Patterns:", font_size=20, color=BLUE)
        patterns_list = VGroup()
        for pattern in analysis_data['most_common_patterns']:
            bullet = Text(f"• {pattern}", font_size=18)
            patterns_list.add(bullet)
        patterns_list.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        
        patterns_section = VGroup(patterns_title, patterns_list).arrange(DOWN, buff=0.3)
        
        # Insights
        insights_title = Text("Key Insights:", font_size=20, color=GREEN)
        insights_list = VGroup()
        for insight in analysis_data['insights_for_manim_studio']:
            bullet = Text(f"• {insight}", font_size=16)
            insights_list.add(bullet)
        insights_list.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        
        insights_section = VGroup(insights_title, insights_list).arrange(DOWN, buff=0.3)
        
        # Layout
        content = VGroup(
            debt_text,
            patterns_section,
            insights_section
        ).arrange(DOWN, buff=0.8).next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(Write(debt_text))
        self.play(FadeIn(patterns_section, shift=UP*0.2))
        self.play(FadeIn(insights_section, shift=UP*0.2))
        
        self.wait(3)
        self.play(FadeOut(Group(*self.mobjects)))
    
    def create_outro(self):
        """Create closing sequence"""
        title = Text("Lessons Learned", font_size=48, color=GOLD)
        
        lessons = VGroup(
            Text("1. Professional video production requires extensive manual tweaking", font_size=20),
            Text("2. Standard Manim has limitations needing creative workarounds", font_size=20),
            Text("3. Real-world projects accumulate technical debt under time pressure", font_size=20),
            Text("4. Better tooling can automate many of these manual processes", font_size=20, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        
        call_to_action = Text(
            "These insights inform the development of manim_studio",
            font_size=24, color=BLUE, weight=BOLD
        )
        
        content = VGroup(title, lessons, call_to_action).arrange(DOWN, buff=0.8)
        
        self.play(FadeIn(title, shift=UP))
        self.play(
            LaggedStart(
                *[Write(lesson) for lesson in lessons],
                lag_ratio=0.3
            )
        )
        self.wait(1)
        self.play(FadeIn(call_to_action, scale=1.1))
        self.wait(3)
        
        # Final fade
        self.play(FadeOut(Group(*self.mobjects)))


# Additional scene for interactive exploration
class HackExplorer(Scene):
    def construct(self):
        """Interactive exploration of specific hacks"""
        title = Text("Hack Explorer", font_size=48, color=PURPLE)
        subtitle = Text("Click through different categories", font_size=24)
        
        self.play(FadeIn(VGroup(title, subtitle).arrange(DOWN)))
        self.wait(2)
        
        # This could be extended with interactive elements
        # for exploring different hack categories


if __name__ == "__main__":
    # Render the main visualization
    scene = ProjectHacksVisualization()
    scene.render()