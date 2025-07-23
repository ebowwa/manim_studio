📋 **TEXT MIGRATION STATUS REPORT** 📋

**Summary:**
- Files needing migration: 103
- Total issues found: 5198

## 🚨 HIGH PRIORITY (Critical)

**developer/examples/layering_demo.py**
  - Line 19: .to_edge(): ground.to_edge(DOWN, buff=0)
  - Line 36: Text(): title = Text("Layering Demo", font_size=48)
  - Line 37: .to_edge(): title.to_edge(UP)
  - Line 68: Text(): info_text = Text("Z-Index Layers Active", font_size=24, color=WHITE)
  - Line 90: .set_color(): self.play(info_text.animate.set_color(GREEN))
  - ... and 5 more issues

**developer/examples/project_hacks_visualization.py**
  - Line 38: Text(): title = Text("Project-Specific Hacks", font_size=56, weight=BOLD, color=YELLOW)
  - Line 39: Text(): subtitle = Text("Real-World Manim Production Challenges", font_size=36, color=GRAY)
  - Line 42: Text(): repo_info = Text(f"Extracted from: {metadata['repository']}", font_size=24)
  - Line 43: Text(): stats = Text(f"{metadata['total_hacks_found']} hacks found across {len(metadata['categories'])} categories",
  - Line 48: .to_edge(): info_group = VGroup(repo_info, stats).arrange(DOWN, buff=0.3).to_edge(DOWN)
  - ... and 51 more issues

**developer/examples/composer_demo.py**
  - Line 19: Text(): title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
  - Line 22: Text(): subtitle = Text("Professional Animation System", font_size=24)
  - Line 27: Text(): Text("• Layered Timeline", font_size=20),
  - Line 28: Text(): Text("• Keyframe Animation", font_size=20),
  - Line 29: Text(): Text("• Multiple Interpolation Types", font_size=20),
  - ... and 1 more issues

**developer/examples/enhanced_easing_demo.py**
  - Line 24: Text(): title = Text("Enhanced Easing Functions", font_size=48)
  - Line 25: Text(): subtitle = Text("Powered by Math3D Utilities", font_size=24, color=GRAY)
  - Line 53: Text(): header = Text("Smooth Step Variations", font_size=36).to_edge(UP)
  - Line 53: .to_edge(): header = Text("Smooth Step Variations", font_size=36).to_edge(UP)
  - Line 77: Text(): text = Text(label, font_size=20, color=color)
  - ... and 23 more issues

**developer/examples/composer_timeline_demo.py**
  - Line 24: Text(): title = Text("Composer Timeline Demo", font_size=48)
  - Line 25: Text(): subtitle = Text("Layers, Tracks, and Keyframes", font_size=24)
  - Line 136: Text(): title = Text("Timeline Presets Demo", font_size=36)
  - Line 156: .to_edge(): visualizer.to_edge(DOWN, buff=0.5)
  - Line 204: Text(): title = Text("Keyframe Editor", font_size=24)
  - ... and 1 more issues

**developer/examples/boundary_aware_easing_demo.py**
  - Line 68: Text(): title = Text("Boundary-Aware Animations", font_size=36)
  - Line 106: Text(): subtitle = Text("Horizontal Movement", font_size=24)
  - Line 143: Text(): subtitle = Text("Elastic Within Bounds", font_size=24)
  - Line 176: .scale(): square.animate(rate_func=bounded_elastic, run_time=1.5).scale(max_scale)
  - Line 179: .scale(): square.animate(rate_func=smooth_step, run_time=1).scale(1/max_scale)
  - ... and 7 more issues

**developer/examples/product_showcase.py**
  - Line 25: Text(): product_name = Text("MANIM STUDIO", font_size=72, weight=BOLD)
  - Line 29: Text(): tagline = Text("Professional Animation Framework", font_size=32)
  - Line 49: Text(): logo_text = Text("MS", font_size=48, weight=BOLD)
  - Line 194: .to_edge(): viz.to_edge(DOWN, buff=0.1)
  - Line 212: .scale(): logo.scale(logo_scale / (logo.width / 3))  # Normalize scale
  - ... and 9 more issues

**developer/examples/skull_effects_demo.py**
  - Line 23: Text(): title = Text("SKULL EFFECTS SHOWCASE", font_size=48)
  - Line 24: .to_edge(): title.to_edge(UP)
  - Line 30: Text(): style_title = Text("Skull Styles", font_size=36).to_edge(UP)
  - Line 30: .to_edge(): style_title = Text("Skull Styles", font_size=36).to_edge(UP)
  - Line 40: Text(): normal_label = Text("Normal", font_size=20).next_to(LEFT * 4, DOWN * 2)
  - ... and 13 more issues

**developer/examples/magical_effects_demo.py**
  - Line 18: .to_edge(): title.animate.scale(0.6).to_edge(UP),
  - Line 18: .scale(): title.animate.scale(0.6).to_edge(UP),
  - Line 37: .scale(): magic_circle.animate.scale(1.2)

**developer/examples/simple_easing_demo.py**
  - Line 51: Text(): title = Text("Enhanced Easing Functions", font_size=48)
  - Line 52: Text(): subtitle = Text("Integrated Math3D Utilities", font_size=24, color=GRAY)
  - Line 67: Text(): title = Text("Easing Function Comparison", font_size=36).to_edge(UP)
  - Line 67: .to_edge(): title = Text("Easing Function Comparison", font_size=36).to_edge(UP)
  - Line 89: Text(): label = Text(name, font_size=20, color=color)
  - ... and 12 more issues

**developer/examples/simple_timeline_test.py**
  - Line 22: Text(): text = Text("Timeline Demo", font_size=36)

**developer/examples/watch_composer_demo.py**
  - Line 15: Text(): title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
  - Line 77: .scale(): title.set_opacity(title_opacity).scale(title_scale / title.height * 1.5)
  - Line 82: .scale(): circle.move_to(circle_x * RIGHT).scale(circle_scale / circle.width * 2)
  - Line 87: .scale(): square.set_angle(square_rot).scale(square_scale / square.width * 1.5)

**developer/examples/informational_substrate_documentary.py**
  - Line 7: Text(): question = Text('What if reality itself is made of information?', color=WHITE, font_size=42)
  - Line 13: Text(): code = Text('if (universe.exists) { return information; }', color=BLUE, font_size=36, font='Courier')
  - Line 21: Text(): heaven = Text('HEAVEN: A place with no death', color=WHITE, font_size=48)
  - Line 22: Text(): substrate = Text('SUBSTRATE: Where no errors exist', color=GREEN, font_size=48)
  - Line 31: Text(): path_title = Text('THE PATH TO HEAVEN', color=YELLOW, font_size=56, weight=BOLD)
  - ... and 5 more issues

**developer/examples/cache_demo.py**
  - Line 60: Text(): title = Text("Manim Studio Cache Demo", font_size=48)
  - Line 66: Text(): Text(f"Without Cache: {time1:.4f}s", font_size=36),
  - Line 67: Text(): Text(f"With Cache: {time2:.4f}s", font_size=36, color=GREEN),
  - Line 68: Text(): Text(f"Speedup: {time1/time2:.2f}x", font_size=40, color=YELLOW)
  - Line 129: Text(): label1 = Text("Original", font_size=24).next_to(img1, DOWN)
  - ... and 1 more issues

**developer/examples/quick_demo.py**
  - Line 8: Text(): title = Text("COMPOSER TIMELINE", font_size=48, weight=BOLD)
  - Line 11: Text(): subtitle = Text("Keyframe Animation System", font_size=24)
  - Line 33: .scale(): circle.animate.shift(RIGHT * 6).scale(1.5),
  - Line 39: .scale(): circle.animate.shift(LEFT * 6).scale(1/1.5),
  - Line 40: .scale(): square.animate.scale(1.5),

**developer/examples/frame_extraction_demo.py**
  - Line 156: Text(): text = Text("Manual Frame Extraction", color=YELLOW)
  - Line 163: .set_color(): circle.animate.scale(2).set_color(RED),
  - Line 163: .scale(): circle.animate.scale(2).set_color(RED),
  - Line 164: .set_color(): text.animate.set_color(GREEN)

**developer/examples/demo_layer_system.py**
  - Line 47: Text(): title = Text("Layer Z-Index Demo", font_size=48, weight=BOLD).to_edge(UP)
  - Line 47: .to_edge(): title = Text("Layer Z-Index Demo", font_size=48, weight=BOLD).to_edge(UP)
  - Line 74: Text(): Text("Background: Blue Rectangle (z=0)", font_size=20, color=BLUE),
  - Line 75: Text(): Text("Middle: Red Circle (z=100)", font_size=20, color=RED),
  - Line 76: Text(): Text("Foreground: Green Square (z=200)", font_size=20, color=GREEN)
  - ... and 4 more issues

**developer/examples/rate_function_integration_test.py**
  - Line 38: Text(): title = Text("Direct Manim Rate Functions", font_size=36).to_edge(UP)
  - Line 38: .to_edge(): title = Text("Direct Manim Rate Functions", font_size=36).to_edge(UP)
  - Line 56: Text(): label = Text(name, font_size=20)
  - Line 76: Text(): title = Text("Custom Easing Functions", font_size=36).to_edge(UP)
  - Line 76: .to_edge(): title = Text("Custom Easing Functions", font_size=36).to_edge(UP)
  - ... and 5 more issues

**developer/examples/simple_boundary_demo.py**
  - Line 17: Text(): title = Text(f"Frame: {fw:.1f}x{fh:.1f} units", font_size=36)
  - Line 18: .to_edge(): title.to_edge(UP, buff=margin)
  - Line 31: Text(): safe_text = Text("Safe Area", font_size=20, color=GREY)
  - Line 63: .scale(): self.play(square.animate(run_time=1.5).scale(max_scale))
  - Line 64: .scale(): self.play(square.animate(run_time=1).scale(1/max_scale))
  - ... and 2 more issues

**developer/examples/inspiration/videos/11-catalan/scenes.py**
  - Line 59: Tex(): llb = Tex(r"$$\mathrm{LLB}_{2n + 1} = C_n (n + 1)!$$").scale(TEXT_SCALE).next_to(tree, LEFT, buff=1)
  - Line 59: .scale(): llb = Tex(r"$$\mathrm{LLB}_{2n + 1} = C_n (n + 1)!$$").scale(TEXT_SCALE).next_to(tree, LEFT, buff=1)
  - Line 61: Tex(): llb_compute = Tex(r"$$= \left(2 \cdot 1\right) \left(2 \cdot 3\right) \ldots \left(2 \cdot (2n + 1)\right)$$").scale(TEXT_SCALE)
  - Line 61: .scale(): llb_compute = Tex(r"$$= \left(2 \cdot 1\right) \left(2 \cdot 3\right) \ldots \left(2 \cdot (2n + 1)\right)$$").scale(TEXT_SCALE)
  - Line 93: .set_color(): ldot = Dot().move_to(StarUtilities.get_star_position(tree, "r", LEFT, star_offset=star_offset)).scale(0.5).set_color(DARK_GRAY)
  - ... and 85 more issues

**developer/examples/inspiration/videos/11-catalan/utilities.py**
  - Line 52: .scale(): star = Star(cls.STAR_N, density=1.5, color=cls.STAR_COLOR, fill_opacity=1).scale(cls.STAR_SCALE)
  - Line 57: Tex(): text = Tex(str(number), color=BLACK).scale(3 * cls.STAR_SCALE).move_to(star)
  - Line 57: .scale(): text = Tex(str(number), color=BLACK).scale(3 * cls.STAR_SCALE).move_to(star)
  - Line 135: .scale(): star[0].animate(rate_func=there_and_back).scale(0.75),
  - Line 214: .set_color(): edge.set_color(StarUtilities.STAR_COLOR)
  - ... and 9 more issues

**developer/examples/inspiration/videos/05-sorting-networks/scenes.py**
  - Line 61: Tex(): self.comparator_layer_numbers.append((subpos, Tex(f"${number}$")))
  - Line 125: .set_color(): number_circle = self.get_circle(0.15).move_to(circle.get_center()).set_color(rainbow_to_rgb(numbers[i] / self.n))
  - Line 126: Tex(): label = Tex(f"${numbers[i]}$").move_to(circle.get_center()).set_color(BLACK).scale(0.5)
  - Line 126: .set_color(): label = Tex(f"${numbers[i]}$").move_to(circle.get_center()).set_color(BLACK).scale(0.5)
  - Line 126: .scale(): label = Tex(f"${numbers[i]}$").move_to(circle.get_center()).set_color(BLACK).scale(0.5)
  - ... and 11 more issues

**developer/examples/inspiration/videos/05-sorting-networks/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/12-state-space/scenes.py**
  - Line 88: Tex(): self.mobject.become(Tex(r"\textbf{" + str(self.number) + "}").move_to(self.mobject))
  - Line 105: Tex(): theseus_text = Tex("Theseus").next_to(theseus, DOWN, buff=-0.08).scale(0.25)
  - Line 105: .scale(): theseus_text = Tex("Theseus").next_to(theseus, DOWN, buff=-0.08).scale(0.25)
  - Line 121: Tex(): minotaur_text = Tex("Minotaur").next_to(minotaur, DOWN, buff=-0.08).scale(0.25)
  - Line 121: .scale(): minotaur_text = Tex("Minotaur").next_to(minotaur, DOWN, buff=-0.08).scale(0.25)
  - ... and 285 more issues

**developer/examples/inspiration/videos/12-state-space/utilities.py**
  - Line 31: Tex(): Tex("In").scale(ARROW_SIZE * 2/3),
  - Line 31: .scale(): Tex("In").scale(ARROW_SIZE * 2/3),
  - Line 45: Tex(): Tex("Out").scale(ARROW_SIZE * 2/3),
  - Line 45: .scale(): Tex("Out").scale(ARROW_SIZE * 2/3),
  - Line 62: .scale(): self.scale(scale)
  - ... and 5 more issues

**developer/examples/inspiration/videos/14-funf/scenes.py**
  - Line 11: Tex(): q = Tex(r"\underline{How does it work?}").scale(1.15)
  - Line 11: .scale(): q = Tex(r"\underline{How does it work?}").scale(1.15)
  - Line 38: .scale(): output = MyCode(contents).code.next_to(brace, UP).scale(1.5)
  - Line 77: .scale(): sum = MyCodeKindaTho("x = sum").scale(0.75)
  - Line 78: .scale(): carry = MyCodeKindaTho("y = carry").scale(0.75)
  - ... and 56 more issues

**developer/examples/inspiration/videos/14-funf/utilities.py**
  - Line 8: .set_color(): code[0].set_color(GRAY)

**developer/examples/inspiration/videos/10-sat/scenes.py**
  - Line 57: Tex(): (VGroup(*[Tex(p) for p in pgroup]).arrange(DOWN, buff=0.25).next_to(factories[i], DOWN, buff=0.45)
  - Line 59: Tex(): else VGroup(*[Tex(p) for p in pgroup]).arrange(DOWN, buff=0.25).next_to(factories[i], DOWN, buff=0.45).shift(DOWN * 0.3))
  - Line 71: .scale(): factory.scale(uniform(1 - p, 1 + p))
  - Line 106: Tex(): unique = Tex(r"$$\{\text{Mars}, \text{Oreos}, \text{Sprite}, \text{Pepsi}\}$$").next_to(VGroup(*texts[offset:offset+3]), DOWN, buff=1).scale(0.8)
  - Line 106: .scale(): unique = Tex(r"$$\{\text{Mars}, \text{Oreos}, \text{Sprite}, \text{Pepsi}\}$$").next_to(VGroup(*texts[offset:offset+3]), DOWN, buff=1).scale(0.8)
  - ... and 331 more issues

**developer/examples/inspiration/videos/13-primes-dots/scenes.py**
  - Line 66: Tex(): numbers_factors = VGroup(*[Tex("$$" + r" \cdot ".join(map(str, factors(i))) + "$$").scale(1.25) for i in range(nnn)]).arrange(DOWN, buff=0.3)
  - Line 66: .scale(): numbers_factors = VGroup(*[Tex("$$" + r" \cdot ".join(map(str, factors(i))) + "$$").scale(1.25) for i in range(nnn)]).arrange(DOWN, buff=0.3)
  - Line 67: Tex(): numbers_factors_zero = VGroup(*[Tex("$$" + r" \cdot ".join(map(str, factors_with_zeroes(i))) + "$$").scale(1.25) for i in range(nnn)]).arrange(DOWN, buff=0.3)
  - Line 67: .scale(): numbers_factors_zero = VGroup(*[Tex("$$" + r" \cdot ".join(map(str, factors_with_zeroes(i))) + "$$").scale(1.25) for i in range(nnn)]).arrange(DOWN, buff=0.3)
  - Line 68: Tex(): numbers_original = VGroup(*[Tex(i).scale(1.25) for i in range(nnn)]).arrange(DOWN, buff=0.3)
  - ... and 4 more issues

**developer/examples/inspiration/videos/03-vizing/scenes.py**
  - Line 20: .set_color(): self.play( A.edges[(0, 1)].animate.set_color(RED),
  - Line 21: .set_color(): A.edges[(0, 4)].animate.set_color(BLUE),
  - Line 22: .set_color(): A.edges[(0, 5)].animate.set_color(GREEN),
  - Line 23: .set_color(): A.edges[(1, 2)].animate.set_color(PINK),
  - Line 24: .set_color(): A.edges[(1, 6)].animate.set_color(BLUE),
  - ... and 463 more issues

**developer/examples/inspiration/videos/03-vizing/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/ksp-intro/scenes.py**
  - Line 35: .scale(): hand_l = SVGMobject("ksp-hand-l.svg").shift(LEFT * e).scale(0.2)
  - Line 36: .scale(): hand_r = SVGMobject("ksp-hand-r.svg").shift(RIGHT * e).scale(0.2)
  - Line 45: .scale(): bezier = CubicBezier(*point_coordinates).scale(1.5)
  - Line 76: .scale(): self.camera.frame.animate(rate_func=rush_into).move_to(text.copy().shift(DOWN * 0.15)).scale(0.001),

**developer/examples/inspiration/videos/18-lopt/scenes.py**
  - Line 57: Tex(): Group(kantorovich, Tex(r"\textit{Kantorovich} (USSR)").scale(subtext_scale)).arrange(DOWN, buff=0.3),
  - Line 57: .scale(): Group(kantorovich, Tex(r"\textit{Kantorovich} (USSR)").scale(subtext_scale)).arrange(DOWN, buff=0.3),
  - Line 58: Tex(): Group(koopmans, Tex(r"\textit{Koopmans} (US)").scale(subtext_scale)).arrange(DOWN, buff=0.3),
  - Line 58: .scale(): Group(koopmans, Tex(r"\textit{Koopmans} (US)").scale(subtext_scale)).arrange(DOWN, buff=0.3),
  - Line 59: .scale(): ).scale(1.1).arrange(RIGHT, buff=5.5)
  - ... and 1559 more issues

**developer/examples/inspiration/videos/18-lopt/utilities.py**
  - Line 69: .scale(): G.vertices[v].scale(2)
  - Line 77: .set_color(): G.edges[(u, v)].set_color(DARKER_GRAY)
  - Line 83: .set_color(): G.edges[(u, v)].set_color(DARKER_GRAY)
  - Line 90: .set_color(): G.vertices[v].set_color(DARKER_GRAY)
  - Line 107: Tex(): Tex(text).set_z_index(1001).move_to(sr),
  - ... and 14 more issues

**developer/examples/inspiration/videos/16-tutte-short/scenes.py**
  - Line 150: .scale(): a = Dot(ax.c2p(0, 0)).scale(1.5).set_z_index(1)
  - Line 151: .scale(): b = Dot(ax.c2p(1, 0)).scale(1.5).set_z_index(1)
  - Line 152: .scale(): c = Dot(ax.c2p(2, 0)).scale(1.5).set_z_index(1)
  - Line 153: .scale(): d = Dot(ax.c2p(3, 24)).scale(1.5).set_z_index(1)
  - Line 155: Tex(): bn = Tex("0").next_to(b, UP).set_z_index(1)
  - ... and 28 more issues

**developer/examples/inspiration/videos/01-lopt/scenes.py**
  - Line 5: Tex(): title = Tex("\Large Chromatic Number ($\chi$)")
  - Line 9: Tex(): text = Tex(r"\parbox{23em}{is the ","smallest"," number of colors needed to color the vertices of a graph $G$, such that ","no two"," neighbouring vertices have the ","same color",".}")
  - Line 12: .set_color(): text[i].set_color(YELLOW)
  - Line 46: Tex(): text = Tex(r"$\chi(G) = 3$")
  - Line 79: Tex(): title = Tex("\Large Linear Programming")
  - ... and 13 more issues

**developer/examples/inspiration/videos/01-lopt/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/20-dfs-vs-bfs/scenes.py**
  - Line 119: Tex(): bfs = Tex(r"\underline{BFS}").scale(s)
  - Line 119: .scale(): bfs = Tex(r"\underline{BFS}").scale(s)
  - Line 120: Tex(): vs = Tex(r"vs.").scale(s)
  - Line 120: .scale(): vs = Tex(r"vs.").scale(s)
  - Line 121: Tex(): dfs = Tex(r"\underline{DFS}").scale(s)
  - ... and 15 more issues

**developer/examples/inspiration/videos/99-miscellaneous/scenes.py**
  - Line 5: .scale(): t = SVGMobject("logo-t.svg").scale(2).set_color_by_gradient((WHITE, WHITE, GRAY, DARK_GRAY))
  - Line 6: .scale(): s = SVGMobject("logo-s.svg").scale(2)
  - Line 24: .scale(): t = SVGMobject("logo-t.svg").scale(0.7).set_color_by_gradient((WHITE, WHITE, GRAY, GRAY))
  - Line 25: .scale(): s = SVGMobject("logo-s.svg").scale(0.7)

**developer/examples/inspiration/videos/00-template-short/scenes.py**
  - Line 8: Tex(): text = Tex("\Huge Intro")

**developer/examples/inspiration/videos/06-edmonds-blossom/scenes.py**
  - Line 26: MathTex(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - Line 26: .scale(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - Line 37: Tex(): text = Tex(a, r"$\mid$", b).move_to(part)
  - Line 38: .set_color(): text[2].set_color(YELLOW),
  - Line 40: MathTex(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - ... and 131 more issues

**developer/examples/inspiration/videos/06-edmonds-blossom/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/07-cayley/scenes.py**
  - Line 37: .scale(): layout="circular", layout_scale=0.7).scale(GRAPH_SCALE)
  - Line 41: .scale(): layout="circular", layout_scale=0.7).scale(GRAPH_SCALE)
  - Line 47: .scale(): layout="circular", layout_scale=0.5).scale(GRAPH_SCALE)
  - Line 51: .scale(): layout="circular", layout_scale=0.5).scale(GRAPH_SCALE)
  - Line 57: .scale(): layout="circular", layout_scale=0.3).scale(GRAPH_SCALE)
  - ... and 110 more issues

**developer/examples/inspiration/videos/07-cayley/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/17-ab/scenes.py**
  - Line 19: .scale(): ).scale(1.8)
  - Line 23: .scale(): r = Square(fill_opacity=1, color=RED).scale(10)
  - Line 39: Tex(): a = Tex("Why")
  - Line 40: Tex(): b = Tex("should")
  - Line 41: Tex(): c = Tex("I")
  - ... and 650 more issues

**developer/examples/inspiration/videos/17-ab/utilities.py**
  - Line 63: Tex(): Tex(r"Average operation {\bf time} (in $\mu$s)").scale(0.65).rotate(90 * DEGREES),
  - Line 63: .scale(): Tex(r"Average operation {\bf time} (in $\mu$s)").scale(0.65).rotate(90 * DEGREES),
  - Line 70: Tex(): Tex(r"Value for $\mathbf{a}$ ($b = 2a$)").scale(0.65),
  - Line 70: .scale(): Tex(r"Value for $\mathbf{a}$ ($b = 2a$)").scale(0.65),
  - Line 77: Tex(): Tex("Insertion").set_color(RED),
  - ... and 57 more issues

**developer/examples/inspiration/videos/15-people/scenes.py**
  - Line 52: .scale(): self.camera.frame.scale(0.54)
  - Line 96: .set_color(): return total_distance, DashedPath([p1, p2, p3], num_dashes=int(total_distance * 10)).set_color(GRAY)
  - Line 113: Tex(): obj.become(Tex(f"{d:.1f}").scale(0.5).set_opacity(opacity))
  - Line 113: .scale(): obj.become(Tex(f"{d:.1f}").scale(0.5).set_opacity(opacity))
  - Line 161: Tex(): p:Tex()
  - ... and 4 more issues

**developer/examples/inspiration/videos/00-template-long/scenes.py**
  - Line 6: Tex(): text = Tex("\Huge Intro")

**developer/examples/inspiration/videos/04-perfect-graphs/scenes.py**
  - Line 22: MathTex(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - Line 22: .scale(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - Line 33: Tex(): text = Tex(a, r"$\mid$", b).move_to(part)
  - Line 34: .set_color(): text[2].set_color(YELLOW),
  - Line 36: MathTex(): dot = MathTex("\\cdot").scale(self.dot_scale_factor)
  - ... and 346 more issues

**developer/examples/inspiration/videos/04-perfect-graphs/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/08-tutte/scenes.py**
  - Line 78: .scale(): ).scale(GRAPH_SCALE)
  - Line 104: .scale(): axes.scale(1.5)
  - Line 105: .scale(): surface.scale(1.5)
  - Line 122: .scale(): a = g.vertices[u].copy().scale(vertex_scale)
  - Line 123: .scale(): b = g.vertices[v].copy().scale(vertex_scale)
  - ... and 7 more issues

**developer/examples/inspiration/videos/08-tutte/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**developer/examples/inspiration/videos/09-bathroom-tiles/scenes.py**
  - Line 82: .set_color(): lines.set_color(self.color)
  - Line 132: .scale(): submobject.scale(
  - Line 211: Tex(): Tex(color)
  - Line 212: .scale(): .scale(Tile.TEXT_SCALE * self.size)
  - Line 356: Tex(): Tex(self.input[i])
  - ... and 190 more issues

**developer/examples/inspiration/videos/ksp-29-1-5/scenes.py**
  - Line 35: Tex(): lucistnici = VGroup(Tex("$n$ lučištníků")).arrange().next_to(upper_dots, UP, buff=0.5).scale(0.6)
  - Line 35: .scale(): lucistnici = VGroup(Tex("$n$ lučištníků")).arrange().next_to(upper_dots, UP, buff=0.5).scale(0.6)
  - Line 36: Tex(): cile = VGroup(Tex("$n$ cílů")).arrange().next_to(lower_dots, DOWN, buff=0.5).scale(0.6)
  - Line 36: .scale(): cile = VGroup(Tex("$n$ cílů")).arrange().next_to(lower_dots, DOWN, buff=0.5).scale(0.6)
  - Line 83: .set_color(): *[arrows[i].animate.set_color(mapping_colors[i]) for i in archers],
  - ... and 87 more issues

**developer/examples/inspiration/videos/ksp-29-1-5/utilities.py**
  - Line 4: .scale(): return Square(fill_opacity=1, color=BLACK).set_opacity(opacity).set_z_index(z).scale(10000)

**developer/examples/inspiration/videos/22-delaunay/scenes.py**
  - Line 48: .scale(): graph[v].scale(2.5)

**developer/examples/inspiration/videos/21-photogrammetry/scenes.py**
  - Line 150: .scale(): .scale(1/5))

**developer/examples/inspiration/videos/21-photogrammetry/utilities.py**
  - Line 154: .set_color(): self.pointcloud.set_color(WHITE)

**developer/examples/inspiration/videos/02-voronoi/scenes.py**
  - Line 32: Tex(): text = Tex("\Huge Voronoi Diagrams")
  - Line 39: Tex(): text = Tex("\Large Creating a Voronoi diagram")
  - Line 57: Tex(): text = Tex("\Large Distributing points evenly")
  - Line 136: Tex(): text = Tex("\Large Chosing a different metric")
  - Line 147: Tex(): formula = Tex("$\sqrt{x^2 + y^2}$")
  - ... and 8 more issues

**developer/examples/inspiration/videos/02-voronoi/utilities.py**
  - Line 33: .set_color(): text[i].set_color(YELLOW)
  - Line 39: Tex(): text = Tex(r"\parbox{" + str(width) + "em}{" + size + " " + args[0], *args[1:-1], args[-1] + "}")
  - Line 57: .set_color(): *[a.animate.set_color(b) for a, b in l],
  - Line 154: .scale(): return Graph(sorted(list(vertices)), edges, layout=lt).scale(scale)

**examples/fixed_camera_3d_demo.py**
  - Line 58: .set_color(): cube.set_color("#4a90e2")
  - Line 71: .set_color(): sphere.set_color(color)
  - Line 188: .set_color(): torus.set_color("#e74c3c")
  - Line 196: .set_color(): sat.set_color(interpolate_color("#3498db", "#9b59b6", i/3))

**examples/camera_3d_demo.py**
  - Line 58: .set_color(): cube.set_color("#4a90e2")
  - Line 71: .set_color(): sphere.set_color(color)
  - Line 184: .set_color(): central.set_color("#ffd700")
  - Line 191: .set_color(): small_sphere.set_color(interpolate_color("#ff0000", "#0000ff", i/5))

**src/scenes/base_scene_3d.py**
  - Line 131: .set_color(): axes.set_color(GREY)
  - Line 137: .set_color(): grid.set_color(GREY)

**src/components/timeline_visualizer.py**
  - Line 38: .to_edge(): ruler.to_edge(UP, buff=0.1)
  - Line 84: Text(): label = Text(f"{int(time)}s", font_size=16).next_to(tick, DOWN)
  - Line 129: Text(): name_text = Text(layer.name, font_size=14, color=WHITE)
  - Line 130: .to_edge(): name_text.to_edge(LEFT, buff=0.2)
  - Line 190: Text(): label = Text(event.name[:10], font_size=10, color=BLACK)
  - ... and 3 more issues

**src/components/base_components.py**
  - Line 17: Text(): title = Text(
  - Line 22: .scale(): ).scale(scale)
  - Line 40: Text(): subtitle = Text(
  - Line 44: .scale(): ).scale(scale)
  - Line 61: MarkupText(): paragraph = MarkupText(
  - ... and 3 more issues

**src/components/graph_utils.py**
  - Line 51: .scale(): return Graph(sorted(list(vertices)), edges, layout=layout).scale(scale)
  - Line 206: .set_color(): self.graph[vertex].animate.set_color(color)
  - Line 223: .set_color(): self.graph[vertex].animate.set_color(color),
  - Line 224: .scale(): self.graph[vertex].animate.scale(scale_factor),

**src/components/algorithm_visualizer.py**
  - Line 38: Text(): self.step_counter = Text(
  - Line 41: .to_edge(): ).to_edge(UP)
  - Line 54: .set_color(): self.code_block.code[line_number].animate.set_color(color),
  - Line 62: Text(): new_counter = Text(
  - Line 95: Text(): Text(f"Comparisons: {self.comparisons}", font_size=20),
  - ... and 16 more issues

**src/components/mathematical_objects.py**
  - Line 103: .scale(): ).scale(length / np.linalg.norm(p2 - p1)).move_to((*offset, 0))
  - Line 139: .scale(): dot = Dot().move_to([*point, 0]).scale(OPTIMUM_DOT_SCALE)
  - Line 229: .set_color(): half_plane.set_color(self.get_color())
  - Line 292: .set_color(): new_area.set_color(self.area.get_color())
  - Line 334: .scale(): dot = Dot().move_to([*point, 0]).scale(NORMAL_DOT_SCALE)

**src/components/data_structures.py**
  - Line 33: Text(): self.in_label = Text("In", font_size=24).next_to(
  - Line 36: Text(): self.out_label = Text("Out", font_size=24).next_to(
  - Line 90: .set_color(): self.in_arrow.animate.set_color(YELLOW),
  - Line 93: .set_color(): scene.play(self.in_arrow.animate.set_color(GREEN), run_time=0.2)
  - Line 114: .set_color(): self.out_arrow.animate.set_color(YELLOW),
  - ... and 8 more issues

**src/components/keyframe_editor.py**
  - Line 154: Text(): x_label = Text("Time (s)", font_size=20).next_to(axes.x_axis, DOWN)
  - Line 155: Text(): y_label = Text("Value", font_size=20).next_to(axes.y_axis, LEFT).rotate(PI/2)
  - Line 238: Text(): label = Text(curve.property_name, font_size=14, color=curve.color)
  - Line 274: .scale(): handle = RegularPolygon(n=6, color=color, fill_opacity=1).scale(0.1)
  - Line 297: Text(): title = Text("Interpolation Types", font_size=16, weight=BOLD)
  - ... and 3 more issues

**src/components/scene_composition.py**
  - Line 43: Text(): text_mobs = [Text(text) for text in texts]
  - Line 103: .to_edge(): author_text.to_edge(DOWN).shift(UP * 0.5)
  - Line 325: .scale(): in_mobject.scale(0.1).move_to(zoom_point)
  - Line 330: .scale(): in_mobject.animate.scale(10).move_to(ORIGIN),
  - Line 353: .to_edge(): code_obj.to_edge(LEFT)
  - ... and 12 more issues

**src/components/magical_effects.py**
  - Line 66: Text(): rune = Text("*", color=rune_color).scale(0.5)
  - Line 66: .scale(): rune = Text("*", color=rune_color).scale(0.5)
  - Line 74: Text(): sym = Text(symbol, color=symbol_color).scale(0.4)
  - Line 74: .scale(): sym = Text(symbol, color=symbol_color).scale(0.4)
  - Line 90: Text(): return Text(text, gradient=gradient, weight=weight).scale(scale)
  - ... and 3 more issues

**src/components/advanced_animations.py**
  - Line 57: Tex(): Tex(r"\textbf{" + str(self.number) + "}").move_to(self.mobject)
  - Line 92: .scale(): self.mobject.scale(

**src/components/effects/blur_effects.py**
  - Line 95: .scale(): layer.scale(scale_factor, about_point=center)
  - Line 188: .set_color(): focused.set_color(interpolate_color(obj.get_color(), WHITE, 0.2))
  - Line 287: .set_color(): channel_layer.set_color(color)
  - Line 416: .scale(): glow.scale(1.5)

**src/components/effects/skull_effects_v2.py**
  - Line 50: .set_color(): part.set_color(shaded_color)
  - Line 52: .set_color(): skull.set_color(base_color)
  - Line 352: .scale(): nose.scale(size * 0.3)

**src/components/effects/skull_effects.py**
  - Line 41: .set_color(): skull.set_color(self.get_config('color'))
  - Line 68: .scale(): nose.scale(size * 0.2)
  - Line 164: .scale(): tooth.scale(size * 0.15)
  - Line 422: .scale(): layer.scale(1 + i * 0.1)
  - Line 549: .set_color(): intermediate.set_color(

**src/components/effects/wave_effects.py**
  - Line 30: .set_color(): wave_obj.set_color(self.get_config('wave_color'))
  - Line 117: .scale(): ).scale(max_radius / 0.01)
  - Line 306: .scale(): ).scale(max_radius / 0.01),
  - Line 330: .scale(): ).scale(1 + strength)

**src/components/effects/indication_effects.py**
  - Line 79: .scale(): target.scale(self.scale_factor)
  - Line 80: .set_color(): target.set_color(self.color)
  - Line 153: .scale(): pre_circle.scale(1 / scale_factor)
  - Line 229: .scale(): self.mobject.scale(

**src/components/effects/magical_circle.py**
  - Line 73: .scale(): symbols.scale(radius * 0.3)
  - Line 85: Text(): return Text("✦", color=colors['runes']).scale(0.5)
  - Line 85: .scale(): return Text("✦", color=colors['runes']).scale(0.5)
  - Line 89: .scale(): return Triangle(color=colors['runes']).scale(0.3)
  - Line 107: Text(): return Text("*", color=colors['runes']).scale(0.5)
  - ... and 4 more issues

**src/components/effects/morph_effects.py**
  - Line 253: .scale(): return shape.animate.scale(1.5).scale(1/1.5)

**src/components/effects/glow_effects.py**
  - Line 41: .set_color(): glow_layer.set_color(glow_color)
  - Line 44: .scale(): glow_layer.scale(layer_scale)
  - Line 59: .scale(): mob.scale(pulse_factor)
  - Line 60: .scale(): mob.scale(1 / pulse_factor)
  - Line 110: .scale(): ambient.scale(1.1)
  - ... and 1 more issues

**src/components/effects/text_effects.py**
  - Line 33: .scale(): glow.scale(factor)
  - Line 39: .scale(): self.glow.animate.scale(1.2).set_opacity(0.5),
  - Line 79: Text(): text = Text(

## ⚠️  MEDIUM PRIORITY

**developer/tests/test_auto_layered_scene.py** (20 issues)
**developer/tests/test_camera_render.py** (4 issues)
**developer/tests/test_improved_timeline_layers.py** (17 issues)
**developer/tests/test_layers_standalone.py** (13 issues)
**developer/tests/test_math3d.py** (2 issues)
**developer/tests/test_skull_effects.py** (12 issues)
**developer/tests/test_skulls_with_layers.py** (8 issues)
**developer/tests/test_skulls_layered_fixed.py** (14 issues)
**developer/tests/test_improved_skulls.py** (12 issues)

## ℹ️  LOW PRIORITY

**test_3d_camera.py** (5 issues)
**camera_scenes.py** (48 issues)
**src/core/asset_manager.py** (4 issues)
**src/core/camera_controller.py** (3 issues)
**src/core/scene_builder.py** (6 issues)
**src/core/visual_polish.py** (5 issues)
**src/core/timeline/layer_manager.py** (1 issues)
**src/utils/boundary_manager.py** (3 issues)
**src/utils/timeline_debugger.py** (8 issues)
**src/utils/utilities.py** (6 issues)
**src/utils/frame_analyzer.py** (1 issues)
**src/utils/math3d/matrix4x4.py** (2 issues)

## 🔧 Next Steps

1. **High Priority**: Update core scene and component files immediately
2. **Medium Priority**: Update example and test files as needed
3. **Low Priority**: Update remaining files during normal development

**See `src/core/TEXT_MIGRATION_GUIDE.md` for detailed migration instructions.**
