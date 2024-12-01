from setuptools import setup, find_packages

setup(
    name="manim_studio",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "manim>=0.17.3",
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "pydub>=0.25.1",
        "importlib-metadata>=4.0.0"
    ],
)
