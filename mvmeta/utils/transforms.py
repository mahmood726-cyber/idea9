"""
Transformation utilities for effect sizes.
"""

import numpy as np
from typing import Tuple


def logit_transform(p: np.ndarray) -> np.ndarray:
    """
    Logit transformation for proportions.

    Parameters
    ----------
    p : np.ndarray
        Proportions (0 < p < 1)

    Returns
    -------
    np.ndarray
        Logit-transformed values
    """
    return np.log(p / (1 - p))


def inverse_logit(x: np.ndarray) -> np.ndarray:
    """
    Inverse logit (logistic) transformation.

    Parameters
    ----------
    x : np.ndarray
        Logit values

    Returns
    -------
    np.ndarray
        Proportions (0 < p < 1)
    """
    return 1 / (1 + np.exp(-x))


def fisher_z_transform(r: np.ndarray) -> np.ndarray:
    """
    Fisher's Z transformation for correlations.

    Parameters
    ----------
    r : np.ndarray
        Correlation coefficients (-1 < r < 1)

    Returns
    -------
    np.ndarray
        Fisher Z-transformed values
    """
    return 0.5 * np.log((1 + r) / (1 - r))


def inverse_fisher_z(z: np.ndarray) -> np.ndarray:
    """
    Inverse Fisher Z transformation.

    Parameters
    ----------
    z : np.ndarray
        Fisher Z values

    Returns
    -------
    np.ndarray
        Correlation coefficients
    """
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def log_odds_ratio(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute log odds ratio and its variance from 2x2 table.

    Parameters
    ----------
    a : np.ndarray
        Count in cell (1,1)
    b : np.ndarray
        Count in cell (1,2)
    c : np.ndarray
        Count in cell (2,1)
    d : np.ndarray
        Count in cell (2,2)

    Returns
    -------
    log_or : np.ndarray
        Log odds ratio
    var_log_or : np.ndarray
        Variance of log odds ratio
    """
    # Add continuity correction for zero cells
    a_adj = a + 0.5
    b_adj = b + 0.5
    c_adj = c + 0.5
    d_adj = d + 0.5

    log_or = np.log((a_adj * d_adj) / (b_adj * c_adj))
    var_log_or = 1/a_adj + 1/b_adj + 1/c_adj + 1/d_adj

    return log_or, var_log_or


def correlation_to_covariance(
    corr: np.ndarray,
    sd: np.ndarray
) -> np.ndarray:
    """
    Convert correlation matrix to covariance matrix.

    Parameters
    ----------
    corr : np.ndarray
        Correlation matrix (p x p)
    sd : np.ndarray
        Standard deviations (p,)

    Returns
    -------
    np.ndarray
        Covariance matrix (p x p)
    """
    D = np.diag(sd)
    return D @ corr @ D


def covariance_to_correlation(cov: np.ndarray) -> np.ndarray:
    """
    Convert covariance matrix to correlation matrix.

    Parameters
    ----------
    cov : np.ndarray
        Covariance matrix (p x p)

    Returns
    -------
    np.ndarray
        Correlation matrix (p x p)
    """
    sd = np.sqrt(np.diag(cov))
    D_inv = np.diag(1 / sd)
    return D_inv @ cov @ D_inv


def standardized_mean_difference(
    mean1: np.ndarray,
    mean2: np.ndarray,
    sd1: np.ndarray,
    sd2: np.ndarray,
    n1: np.ndarray,
    n2: np.ndarray,
    method: str = 'hedges_g'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute standardized mean difference.

    Parameters
    ----------
    mean1, mean2 : np.ndarray
        Group means
    sd1, sd2 : np.ndarray
        Group standard deviations
    n1, n2 : np.ndarray
        Group sample sizes
    method : str, default='hedges_g'
        'cohen_d' or 'hedges_g' (bias-corrected)

    Returns
    -------
    smd : np.ndarray
        Standardized mean difference
    var_smd : np.ndarray
        Variance of SMD
    """
    # Pooled standard deviation
    pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))

    # Cohen's d
    d = (mean1 - mean2) / pooled_sd

    if method == 'hedges_g':
        # Bias correction
        J = 1 - (3 / (4 * (n1 + n2 - 2) - 1))
        smd = J * d
    else:
        smd = d

    # Variance
    var_smd = (n1 + n2) / (n1 * n2) + smd**2 / (2 * (n1 + n2))

    return smd, var_smd
