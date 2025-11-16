"""
Base classes for meta-analysis models.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class MetaAnalysisResults:
    """
    Container for meta-analysis results.

    Attributes
    ----------
    theta : np.ndarray
        Pooled effect estimates (p,) for p outcomes
    theta_se : np.ndarray
        Standard errors of pooled estimates (p,)
    Psi : np.ndarray
        Between-study covariance matrix (p, p)
    loglik : float
        Log-likelihood of the model
    converged : bool
        Whether the optimization converged
    method : str
        Estimation method used
    n_studies : int
        Number of studies
    n_outcomes : int
        Number of outcomes
    study_effects : Optional[np.ndarray]
        Study-specific effect estimates if available
    residuals : Optional[np.ndarray]
        Residuals from the model
    Q_stat : Optional[float]
        Cochran's Q statistic
    I2 : Optional[np.ndarray]
        I-squared statistics for each outcome
    fitted_values : Optional[np.ndarray]
        Fitted values from the model
    additional_info : Dict[str, Any]
        Additional information from estimation
    """
    theta: np.ndarray
    theta_se: np.ndarray
    Psi: np.ndarray
    loglik: float
    converged: bool
    method: str
    n_studies: int
    n_outcomes: int
    study_effects: Optional[np.ndarray] = None
    residuals: Optional[np.ndarray] = None
    Q_stat: Optional[float] = None
    I2: Optional[np.ndarray] = None
    fitted_values: Optional[np.ndarray] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def between_study_correlation(self) -> np.ndarray:
        """
        Compute between-study correlation matrix from Psi.

        Returns
        -------
        np.ndarray
            Correlation matrix (p, p)
        """
        D = np.sqrt(np.diag(self.Psi))
        if np.any(D == 0):
            return np.eye(self.n_outcomes)
        return self.Psi / np.outer(D, D)

    @property
    def ci_lower(self) -> np.ndarray:
        """95% confidence interval lower bounds."""
        return self.theta - 1.96 * self.theta_se

    @property
    def ci_upper(self) -> np.ndarray:
        """95% confidence interval upper bounds."""
        return self.theta + 1.96 * self.theta_se

    def summary(self) -> str:
        """
        Generate a summary of the results.

        Returns
        -------
        str
            Formatted summary string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("Multivariate Meta-Analysis Results")
        lines.append("=" * 70)
        lines.append(f"Method: {self.method}")
        lines.append(f"Number of studies: {self.n_studies}")
        lines.append(f"Number of outcomes: {self.n_outcomes}")
        lines.append(f"Converged: {self.converged}")
        lines.append(f"Log-likelihood: {self.loglik:.4f}")
        lines.append("")
        lines.append("Pooled Effect Estimates:")
        lines.append("-" * 70)
        lines.append(f"{'Outcome':<10} {'Estimate':>10} {'SE':>10} {'95% CI Lower':>12} {'95% CI Upper':>12}")
        lines.append("-" * 70)
        for i in range(self.n_outcomes):
            lines.append(
                f"{i+1:<10} {self.theta[i]:>10.4f} {self.theta_se[i]:>10.4f} "
                f"{self.ci_lower[i]:>12.4f} {self.ci_upper[i]:>12.4f}"
            )
        lines.append("")
        lines.append("Between-Study Covariance Matrix (Psi):")
        lines.append("-" * 70)
        for row in self.Psi:
            lines.append("  " + "  ".join(f"{x:8.4f}" for x in row))
        lines.append("")
        lines.append("Between-Study Correlation Matrix:")
        lines.append("-" * 70)
        corr = self.between_study_correlation
        for row in corr:
            lines.append("  " + "  ".join(f"{x:8.4f}" for x in row))

        if self.I2 is not None:
            lines.append("")
            lines.append("Heterogeneity (I-squared):")
            lines.append("-" * 70)
            for i, i2 in enumerate(self.I2):
                lines.append(f"Outcome {i+1}: {i2*100:.2f}%")

        lines.append("=" * 70)
        return "\n".join(lines)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert results to a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            Results as a DataFrame
        """
        return pd.DataFrame({
            'outcome': range(1, self.n_outcomes + 1),
            'estimate': self.theta,
            'se': self.theta_se,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
        })


class BaseMetaAnalysis(ABC):
    """
    Abstract base class for meta-analysis models.

    Parameters
    ----------
    verbose : bool, default=False
        Whether to print progress information
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results_: Optional[MetaAnalysisResults] = None

    @abstractmethod
    def fit(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None,
        **kwargs
    ) -> MetaAnalysisResults:
        """
        Fit the meta-analysis model.

        Parameters
        ----------
        y : np.ndarray
            Effect size estimates, shape (n_studies, n_outcomes)
        S : np.ndarray
            Within-study covariance matrices, shape (n_studies, n_outcomes, n_outcomes)
        X : np.ndarray, optional
            Study-level covariates for meta-regression, shape (n_studies, n_covariates)
        **kwargs
            Additional method-specific parameters

        Returns
        -------
        MetaAnalysisResults
            Results object containing estimates and diagnostics
        """
        pass

    def _validate_inputs(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """
        Validate and prepare input data.

        Parameters
        ----------
        y : np.ndarray
            Effect sizes
        S : np.ndarray
            Within-study covariances
        X : np.ndarray, optional
            Covariates

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]
            Validated y, S, X

        Raises
        ------
        ValueError
            If inputs have incompatible shapes or invalid values
        """
        y = np.asarray(y)
        S = np.asarray(S)

        # Handle 1D input (single outcome)
        if y.ndim == 1:
            y = y[:, np.newaxis]

        if S.ndim == 2:
            S = S[:, np.newaxis, np.newaxis]

        # Validate shapes
        n_studies, n_outcomes = y.shape

        if S.shape != (n_studies, n_outcomes, n_outcomes):
            raise ValueError(
                f"S must have shape ({n_studies}, {n_outcomes}, {n_outcomes}), "
                f"got {S.shape}"
            )

        # Check for missing data
        if np.any(np.isnan(y)) or np.any(np.isnan(S)):
            if self.verbose:
                print("Warning: Missing data detected. Consider using imputation methods.")

        # Validate covariance matrices are positive semi-definite
        for i in range(n_studies):
            if not np.all(np.isnan(S[i])):
                eigvals = np.linalg.eigvalsh(S[i])
                if np.any(eigvals < -1e-10):
                    raise ValueError(
                        f"Study {i} covariance matrix is not positive semi-definite"
                    )

        # Validate covariates
        if X is not None:
            X = np.asarray(X)
            if X.shape[0] != n_studies:
                raise ValueError(
                    f"X must have {n_studies} rows, got {X.shape[0]}"
                )

        return y, S, X

    @property
    def results(self) -> MetaAnalysisResults:
        """Get the results of the fitted model."""
        if self.results_ is None:
            raise ValueError("Model has not been fitted yet. Call fit() first.")
        return self.results_
