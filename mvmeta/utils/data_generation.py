"""
Data generation utilities for simulation and examples.
"""

from typing import Tuple, Optional, List
import numpy as np
import pandas as pd


def simulate_multivariate_ma(
    n_studies: int = 20,
    n_outcomes: int = 2,
    true_effects: Optional[np.ndarray] = None,
    between_study_sd: float = 0.5,
    within_study_sd: float = 0.3,
    correlation: float = 0.5,
    missing_rate: float = 0.0,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate data for multivariate meta-analysis.

    Parameters
    ----------
    n_studies : int, default=20
        Number of studies
    n_outcomes : int, default=2
        Number of outcomes
    true_effects : np.ndarray, optional
        True pooled effects. If None, uses [0.5, 0.3, ...]
    between_study_sd : float, default=0.5
        Between-study standard deviation
    within_study_sd : float, default=0.3
        Within-study standard deviation
    correlation : float, default=0.5
        Between-study correlation
    missing_rate : float, default=0.0
        Proportion of missing outcome data (0 to 1)
    seed : int, optional
        Random seed for reproducibility

    Returns
    -------
    y : np.ndarray
        Effect size estimates (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariance matrices (n_studies, n_outcomes, n_outcomes)

    Examples
    --------
    >>> from mvmeta.utils import simulate_multivariate_ma
    >>> y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=3, seed=42)
    >>> print(y.shape)
    (15, 3)
    """
    if seed is not None:
        np.random.seed(seed)

    # True effects
    if true_effects is None:
        true_effects = np.linspace(0.5, 0.3, n_outcomes)

    # Between-study covariance matrix
    Psi = between_study_sd**2 * (
        correlation * np.ones((n_outcomes, n_outcomes)) +
        (1 - correlation) * np.eye(n_outcomes)
    )

    # Within-study covariance (assumed constant across studies for simplicity)
    S_common = within_study_sd**2 * (
        0.3 * np.ones((n_outcomes, n_outcomes)) +
        0.7 * np.eye(n_outcomes)
    )

    # Generate study-specific effects
    study_effects = np.random.multivariate_normal(
        mean=true_effects,
        cov=Psi,
        size=n_studies
    )

    # Generate observed effects (with within-study noise)
    y = np.zeros((n_studies, n_outcomes))
    S = np.zeros((n_studies, n_outcomes, n_outcomes))

    for i in range(n_studies):
        # Add within-study variation with some heterogeneity
        S_i = S_common * np.random.gamma(2, 0.5)
        y[i] = np.random.multivariate_normal(study_effects[i], S_i)
        S[i] = S_i

    # Add missing data
    if missing_rate > 0:
        n_missing = int(n_studies * n_outcomes * missing_rate)
        missing_idx = np.random.choice(
            n_studies * n_outcomes,
            size=n_missing,
            replace=False
        )
        for idx in missing_idx:
            study_idx = idx // n_outcomes
            outcome_idx = idx % n_outcomes
            y[study_idx, outcome_idx] = np.nan

    return y, S


def simulate_network_ma(
    n_treatments: int = 4,
    n_outcomes: int = 2,
    n_studies: int = 15,
    true_effects: Optional[np.ndarray] = None,
    between_study_sd: float = 0.5,
    within_study_sd: float = 0.3,
    correlation: float = 0.4,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Simulate data for multivariate network meta-analysis.

    Parameters
    ----------
    n_treatments : int, default=4
        Number of treatments
    n_outcomes : int, default=2
        Number of outcomes
    n_studies : int, default=15
        Number of studies
    true_effects : np.ndarray, optional
        True treatment effects relative to reference,
        shape (n_treatments-1, n_outcomes)
    between_study_sd : float, default=0.5
        Between-study standard deviation
    within_study_sd : float, default=0.3
        Within-study standard deviation
    correlation : float, default=0.4
        Between-study correlation between outcomes
    seed : int, optional
        Random seed

    Returns
    -------
    pd.DataFrame
        Network data with columns: study, t1, t2, outcome columns, variance columns

    Examples
    --------
    >>> from mvmeta.utils import simulate_network_ma
    >>> data = simulate_network_ma(n_treatments=3, n_outcomes=2, seed=42)
    >>> print(data.head())
    """
    if seed is not None:
        np.random.seed(seed)

    treatment_names = [f"T{i}" for i in range(n_treatments)]

    # True treatment effects (relative to T0)
    if true_effects is None:
        true_effects = np.random.uniform(-0.5, 0.5, (n_treatments - 1, n_outcomes))

    # Between-study covariance
    Psi = between_study_sd**2 * (
        correlation * np.ones((n_outcomes, n_outcomes)) +
        (1 - correlation) * np.eye(n_outcomes)
    )

    # Generate studies
    studies = []
    for i in range(n_studies):
        # Randomly select two treatments to compare
        t1_idx, t2_idx = np.random.choice(n_treatments, size=2, replace=False)
        t1_idx, t2_idx = min(t1_idx, t2_idx), max(t1_idx, t2_idx)

        # True effect for this comparison
        if t1_idx == 0:
            true_d = true_effects[t2_idx - 1]
        elif t2_idx == 0:
            true_d = -true_effects[t1_idx - 1]
        else:
            true_d = true_effects[t2_idx - 1] - true_effects[t1_idx - 1]

        # Add between-study variation
        d_i = np.random.multivariate_normal(true_d, Psi)

        # Within-study covariance
        S_i = within_study_sd**2 * (
            0.2 * np.ones((n_outcomes, n_outcomes)) +
            0.8 * np.eye(n_outcomes)
        )

        # Observed effect with within-study noise
        y_i = np.random.multivariate_normal(d_i, S_i)

        # Create study record
        study_record = {
            'study': f'Study_{i+1}',
            't1': treatment_names[t1_idx],
            't2': treatment_names[t2_idx]
        }

        for j in range(n_outcomes):
            study_record[f'outcome_{j+1}'] = y_i[j]
            study_record[f'var_outcome_{j+1}'] = S_i[j, j]

        # Add covariances
        for j in range(n_outcomes):
            for k in range(j + 1, n_outcomes):
                study_record[f'cov_outcome_{j+1}_outcome_{k+1}'] = S_i[j, k]

        studies.append(study_record)

    return pd.DataFrame(studies)


def simulate_with_covariates(
    n_studies: int = 25,
    n_outcomes: int = 2,
    n_covariates: int = 1,
    true_effects: Optional[np.ndarray] = None,
    covariate_effects: Optional[np.ndarray] = None,
    between_study_sd: float = 0.4,
    within_study_sd: float = 0.3,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate data with study-level covariates.

    Parameters
    ----------
    n_studies : int, default=25
        Number of studies
    n_outcomes : int, default=2
        Number of outcomes
    n_covariates : int, default=1
        Number of covariates
    true_effects : np.ndarray, optional
        Baseline true effects
    covariate_effects : np.ndarray, optional
        Covariate effects, shape (n_covariates, n_outcomes)
    between_study_sd : float, default=0.4
        Between-study SD
    within_study_sd : float, default=0.3
        Within-study SD
    seed : int, optional
        Random seed

    Returns
    -------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    X : np.ndarray
        Covariates (n_studies, n_covariates)
    """
    if seed is not None:
        np.random.seed(seed)

    if true_effects is None:
        true_effects = np.ones(n_outcomes) * 0.5

    if covariate_effects is None:
        covariate_effects = np.random.uniform(-0.3, 0.3, (n_covariates, n_outcomes))

    # Generate covariates
    X = np.random.randn(n_studies, n_covariates)

    # Compute study-specific true effects
    true_effects_studies = np.tile(true_effects, (n_studies, 1))
    for i in range(n_studies):
        for k in range(n_covariates):
            true_effects_studies[i] += X[i, k] * covariate_effects[k]

    # Between-study covariance
    Psi = between_study_sd**2 * np.eye(n_outcomes)

    # Generate data
    y = np.zeros((n_studies, n_outcomes))
    S = np.zeros((n_studies, n_outcomes, n_outcomes))

    for i in range(n_studies):
        # Study-specific effect
        study_effect = np.random.multivariate_normal(true_effects_studies[i], Psi)

        # Within-study covariance
        S_i = within_study_sd**2 * np.eye(n_outcomes)

        # Observed effect
        y[i] = np.random.multivariate_normal(study_effect, S_i)
        S[i] = S_i

    return y, S, X
