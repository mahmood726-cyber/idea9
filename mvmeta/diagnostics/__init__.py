"""
Diagnostic tools for multivariate meta-analysis.
"""

from mvmeta.diagnostics.heterogeneity import (
    assess_heterogeneity,
    cochran_q_test,
    multivariate_q_test,
    test_homogeneity,
    compute_prediction_interval
)
from mvmeta.diagnostics.influence import (
    leave_one_out_analysis,
    cook_distance,
    identify_outliers,
    studentized_residuals,
    hat_values,
    dfbetas,
    comprehensive_diagnostics
)

# NOTE: Inconsistency detection functions (node_splitting, etc.) are available in
# mvmeta.diagnostics.inconsistency but not exported in the public API.
# These require full network meta-analysis implementation and are marked as future work.
# They can be accessed via:
#   from mvmeta.diagnostics.inconsistency import node_splitting  # etc.
# but are NOT considered stable or complete.

__all__ = [
    # Heterogeneity
    "assess_heterogeneity",
    "cochran_q_test",
    "multivariate_q_test",
    "test_homogeneity",
    "compute_prediction_interval",
    # Influence
    "leave_one_out_analysis",
    "cook_distance",
    "identify_outliers",
    "studentized_residuals",
    "hat_values",
    "dfbetas",
    "comprehensive_diagnostics",
]
