from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mvmeta",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multivariate Meta-Analysis in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mvmeta",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Statistics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "pymc>=5.0.0",
        "arviz>=0.15.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "networkx>=2.6.0",
        "statsmodels>=0.13.0",
        "numdifftools>=0.9.40",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "jax": [
            "jax>=0.4.0",
            "jaxlib>=0.4.0",
        ],
    },
    package_data={
        "mvmeta": ["data/*.csv", "data/*.json"],
    },
)
