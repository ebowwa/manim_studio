from setuptools import setup, find_packages

setup(
    name="manim_studio",
    version="0.1.0",
    author="ebowwa",
    description="A reusable framework for creating animated videos using Manim",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
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
        "watchdog>=2.0.0"
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Topic :: Artistic Software",
    ],
)
