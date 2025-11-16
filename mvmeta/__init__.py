"""
MVMeta: Multivariate Meta-Analysis in Python

A comprehensive package for multivariate and multi-endpoint meta-analysis.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from mvmeta.models.multivariate import MultivariateMetaAnalysis
from mvmeta.models.network import MultivariateNetworkMetaAnalysis

__all__ = [
    "MultivariateMetaAnalysis",
    "MultivariateNetworkMetaAnalysis",
]
