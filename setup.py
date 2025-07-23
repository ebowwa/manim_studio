from setuptools import setup, find_packages

setup(
    name="manim_studio",
    version="2.0.0",
    author="ebowwa",
    author_email="your.email@example.com",
    description="Professional animation framework for Python - Create stunning mathematical animations and visualizations with code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ebowwa/manim_studio",
    project_urls={
        "Bug Tracker": "https://github.com/ebowwa/manim_studio/issues",
        "Documentation": "https://github.com/ebowwa/manim_studio/tree/main/docs",
        "Source Code": "https://github.com/ebowwa/manim_studio",
        "Discord": "https://discord.gg/manim-studio",
    },
    keywords=[
        "manim", "animation", "video", "visualization", "mathematical animation",
        "educational content", "motion graphics", "data visualization",
        "creative coding", "animation framework", "video production",
        "python animation", "3blue1brown", "math videos", "science visualization"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "manim>=0.17.3",
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "pydub>=0.25.1",
        "importlib-metadata>=4.0.0",
        "manimpango>=0.5.0",
        "pycairo>=1.13.0",
        "pygments>=2.0.0",
        "rich>=12.0.0",
        "watchdog>=2.0.0",
        "trimesh>=3.15.0",
        "pygltflib>=1.15.0",
        "pydantic>=2.0.0"
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=22.0',
            'isort>=5.0',
            'flake8>=3.9'
        ],
        'latex': [
            'latexmk>=4.0',
            'texlive-core>=2021',
            'texlive-latex-extra>=2021'
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Education",
        "Topic :: Artistic Software",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Manim",
    ],
    entry_points={
        'console_scripts': [
            'manim-studio=src.cli:main',
        ],
    },
)
