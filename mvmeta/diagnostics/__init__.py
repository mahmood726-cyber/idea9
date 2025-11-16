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
from mvmeta.diagnostics.inconsistency import (
    node_splitting,
    design_inconsistency_test,
    loop_inconsistency,
    global_inconsistency_test,
    detect_all_inconsistencies
)

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
    # Inconsistency
    "node_splitting",
    "design_inconsistency_test",
    "loop_inconsistency",
    "global_inconsistency_test",
    "detect_all_inconsistencies",
]
