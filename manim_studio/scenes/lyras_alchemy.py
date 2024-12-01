from manim import *
from manim_studio.scenes.base_scene import StudioScene
import os

class LyrasAlchemy(StudioScene):
    def construct(self):
        # Define asset paths
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        umbra_forest = os.path.join(assets_dir, "umbra_forest.png")
        lunar_lily = os.path.join(assets_dir, "lunar_lily.png")
        ashborne_academy = os.path.join(assets_dir, "ashborne_academy.png")
        vampire = os.path.join(assets_dir, "vampire.png")
        battle_scene = os.path.join(assets_dir, "battle_scene.png")

        # Title Card
        self.show_title_card("Lyra's Alchemy: A Fantasy Novel")

        # Introduction
        forest_img, forest_text = self.show_image_with_caption(
            umbra_forest,
            "A young alchemist, Lyra, discovers a magical world...",
            scale=0.8
        )

        # Lunar Lily
        lily_img, lily_text = self.show_image_with_caption(
            lunar_lily,
            "...filled with powerful essence and secrets, like the Lunar Lily.",
            scale=0.6
        )
        self.transition_scenes([forest_img, forest_text], [lily_img, lily_text])

        # Ashborne Academy
        academy_img, academy_text = self.show_image_with_caption(
            ashborne_academy,
            "Lyra's journey leads her to Ashborne Academy...",
            scale=0.7
        )
        self.transition_scenes([lily_img, lily_text], [academy_img, academy_text])

        # Vampire Conflict
        vampire_img, vampire_text = self.show_image_with_caption(
            vampire,
            "...a world of danger and intrigue, where vampires rule.",
            scale=0.5
        )
        self.transition_scenes([academy_img, academy_text], [vampire_img, vampire_text])

        # Battle Scene
        battle_img, battle_text = self.show_image_with_caption(
            battle_scene,
            "Lyra must use her alchemy and newfound powers in epic battles...",
            scale=0.8
        )
        self.transition_scenes([vampire_img, vampire_text], [battle_img, battle_text])

        # Friends Scene (using shapes instead of images)
        friends = Group(*[
            Circle(radius=0.5, color=BLUE).set_fill(BLUE, opacity=0.5) 
            for _ in range(3)
        ]).arrange(RIGHT, buff=0.5)
        friends_text = self.text.create_subtitle(
            "...with the help of her courageous friends."
        ).next_to(friends, DOWN, buff=0.5)
        
        self.transition_scenes(
            [battle_img, battle_text], 
            [friends, friends_text]
        )

        # Call to Action
        call_to_action = self.text.create_title(
            "Discover Lyra's fate! Read Lyra's Alchemy today!"
        ).scale(0.8)
        
        self.transition_scenes(
            [friends, friends_text],
            [call_to_action]
        )
        self.wait(5)
        self.play(FadeOut(call_to_action))
