"""
TAWHIRI Space Domain Awareness Platform
Setup configuration for package installation
"""

from setuptools import setup, find_packages
import pathlib

# Read the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="tawhiri",
    version="1.0.0",
    description="TAWHIRI Space Domain Awareness Platform for NZDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NZDF Space Domain Awareness Team",
    author_email="",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Defense/Military",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="space weather, satellite tracking, orbital mechanics, space domain awareness",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "plotly>=5.17.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "fpdf>=1.7.2",
        "skyfield>=1.45",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "pdf": [
            "kaleido>=0.2.1",  # For PDF chart export
        ],
    },
    entry_points={
        "console_scripts": [
            "tawhiri-spaceweather=tawhiri.space_weather.app:main",
            "tawhiri-orbitviz=tawhiri.orbit_viz.app:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/nzdf/tawhiri/issues",
        "Source": "https://github.com/nzdf/tawhiri/",
    },
)
