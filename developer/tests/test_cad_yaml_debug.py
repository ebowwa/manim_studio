from src.config.manim_config import config
import yaml
from src.core import Config, SceneBuilder
from src.core.config import SceneConfig

# Load and print the YAML
with open('configs/cad_simple_test.yaml', 'r') as f:
    yaml_data = yaml.safe_load(f)
    print("YAML Data:")
    print(yaml.dump(yaml_data, indent=2))

# Load through Config
config = Config('configs/cad_simple_test.yaml')
print("\nConfig data keys:", list(config.data.keys()))

# Check if it has scene key
if 'scene' in config.data:
    scene_data = config.data['scene']
    print("\nScene data:", scene_data)
    
    # Create SceneConfig
    scene_config = SceneConfig.from_dict(scene_data)
    print("\nSceneConfig name:", scene_config.name)
    print("SceneConfig objects:", len(scene_config.objects))
    print("SceneConfig animations:", len(scene_config.animations))