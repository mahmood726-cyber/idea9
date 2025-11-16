"""
Heterogeneity assessment for multivariate meta-analysis.
"""

from typing import Tuple, Optional
import numpy as np
from scipy.stats import chi2
import pandas as pd

from mvmeta.models.base import MetaAnalysisResults


def assess_heterogeneity(
    results: MetaAnalysisResults,
    y: np.ndarray,
    S: np.ndarray
) -> pd.DataFrame:
    """
    Comprehensive heterogeneity assessment.

    Parameters
    ----------
    results : MetaAnalysisResults
        Fitted model results
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)

    Returns
    -------
    pd.DataFrame
        Heterogeneity statistics for each outcome
    """
    n_studies, n_outcomes = y.shape

    het_stats = []

    for j in range(n_outcomes):
        # Cochran's Q statistic for outcome j
        Q_j, df_j, p_value_j = cochran_q_test(
            y[:, j],
            S[:, j, j],
            results.theta[j]
        )

        # I-squared
        if results.I2 is not None:
            I2_j = results.I2[j]
        else:
            I2_j = max(0, (Q_j - df_j) / Q_j) if Q_j > 0 else 0

        # H-squared
        H2_j = Q_j / df_j if df_j > 0 else 1.0

        # Tau-squared (between-study variance)
        tau2_j = results.Psi[j, j]

        # Prediction interval
        pred_se = np.sqrt(results.theta_se[j]**2 + tau2_j)
        pred_lower = results.theta[j] - 1.96 * pred_se
        pred_upper = results.theta[j] + 1.96 * pred_se

        het_stats.append({
            'outcome': j,
            'Q': Q_j,
            'df': df_j,
            'p_value': p_value_j,
            'I2': I2_j * 100,  # As percentage
            'H2': H2_j,
            'tau2': tau2_j,
            'tau': np.sqrt(tau2_j),
            'pred_interval_lower': pred_lower,
            'pred_interval_upper': pred_upper,
            'interpretation': interpret_i2(I2_j)
        })

    return pd.DataFrame(het_stats)


def cochran_q_test(
    y: np.ndarray,
    variances: np.ndarray,
    pooled_effect: float
) -> Tuple[float, int, float]:
    """
    Cochran's Q test for heterogeneity.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies,)
    variances : np.ndarray
        Within-study variances (n_studies,)
    pooled_effect : float
        Pooled effect estimate

    Returns
    -------
    Q : float
        Q statistic
    df : int
        Degrees of freedom
    p_value : float
        P-value from chi-squared test
    """
    # Remove missing values
    mask = ~np.isnan(y) & ~np.isnan(variances)
    y_clean = y[mask]
    var_clean = variances[mask]

    if len(y_clean) < 2:
        return np.nan, 0, np.nan

    # Weights
    weights = 1 / var_clean

    # Q statistic
    Q = np.sum(weights * (y_clean - pooled_effect)**2)

    # Degrees of freedom
    df = len(y_clean) - 1

    # P-value
    p_value = 1 - chi2.cdf(Q, df) if df > 0 else np.nan

    return Q, df, p_value


def multivariate_q_test(
    y: np.ndarray,
    S: np.ndarray,
    theta: np.ndarray
) -> Tuple[float, int, float]:
    """
    Multivariate generalization of Cochran's Q test.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    theta : np.ndarray
        Pooled effects (n_outcomes,)

    Returns
    -------
    Q : float
        Multivariate Q statistic
    df : int
        Degrees of freedom
    p_value : float
        P-value
    """
    n_studies, n_outcomes = y.shape

    Q = 0.0
    valid_studies = 0

    for i in range(n_studies):
        # Skip if any missing values
        if np.any(np.isnan(y[i])) or np.any(np.isnan(S[i])):
            continue

        resid = y[i] - theta
        try:
            S_inv = np.linalg.inv(S[i])
            Q += resid @ S_inv @ resid
            valid_studies += 1
        except np.linalg.LinAlgError:
            continue

    # Degrees of freedom
    df = valid_studies * n_outcomes - n_outcomes

    # P-value
    p_value = 1 - chi2.cdf(Q, df) if df > 0 else np.nan

    return Q, df, p_value


def interpret_i2(i2: float) -> str:
    """
    Interpret I-squared statistic.

    Parameters
    ----------
    i2 : float
        I-squared value (0 to 1)

    Returns
    -------
    str
        Interpretation
    """
    i2_pct = i2 * 100 if i2 <= 1 else i2

    if i2_pct < 25:
        return "Low heterogeneity"
    elif i2_pct < 50:
        return "Moderate heterogeneity"
    elif i2_pct < 75:
        return "Substantial heterogeneity"
    else:
        return "Considerable heterogeneity"


def compute_prediction_interval(
    results: MetaAnalysisResults,
    coverage: float = 0.95
) -> np.ndarray:
    """
    Compute prediction intervals for future studies.

    Parameters
    ----------
    results : MetaAnalysisResults
        Fitted model results
    coverage : float, default=0.95
        Coverage probability

    Returns
    -------
    np.ndarray
        Prediction intervals (n_outcomes, 2)
    """
    from scipy.stats import norm

    n_outcomes = results.n_outcomes
    z = norm.ppf(1 - (1 - coverage) / 2)

    pred_intervals = np.zeros((n_outcomes, 2))

    for j in range(n_outcomes):
        # Prediction standard error
        pred_se = np.sqrt(results.theta_se[j]**2 + results.Psi[j, j])

        pred_intervals[j, 0] = results.theta[j] - z * pred_se
        pred_intervals[j, 1] = results.theta[j] + z * pred_se

    return pred_intervals


def test_homogeneity(
    y: np.ndarray,
    S: np.ndarray,
    alpha: float = 0.05
) -> dict:
    """
    Test homogeneity assumption (no between-study heterogeneity).

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    alpha : float, default=0.05
        Significance level

    Returns
    -------
    dict
        Test results
    """
    n_studies, n_outcomes = y.shape

    # Fit fixed-effect model (assuming homogeneity)
    from mvmeta.models.multivariate import MultivariateMetaAnalysis

    # Compute pooled estimate under homogeneity
    V_inv_sum = np.zeros((n_outcomes, n_outcomes))
    V_inv_y_sum = np.zeros(n_outcomes)

    for i in range(n_studies):
        if not np.any(np.isnan(y[i])) and not np.any(np.isnan(S[i])):
            try:
                S_inv = np.linalg.inv(S[i])
                V_inv_sum += S_inv
                V_inv_y_sum += S_inv @ y[i]
            except np.linalg.LinAlgError:
                continue

    theta_fixed = np.linalg.solve(V_inv_sum, V_inv_y_sum)

    # Multivariate Q test
    Q, df, p_value = multivariate_q_test(y, S, theta_fixed)

    return {
        'Q': Q,
        'df': df,
        'p_value': p_value,
        'reject_homogeneity': p_value < alpha if not np.isnan(p_value) else None,
        'conclusion': 'Significant heterogeneity detected' if (p_value < alpha and not np.isnan(p_value)) else 'No significant heterogeneity'
    }
