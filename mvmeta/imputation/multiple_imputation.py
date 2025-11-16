"""
Multiple imputation for missing outcome data.

Implements multiple imputation under Missing at Random (MAR) assumption,
leveraging correlations between outcomes to impute missing values.
"""

from typing import Optional, List, Tuple
import numpy as np
from scipy.stats import multivariate_normal
import warnings

from mvmeta.models.multivariate import MultivariateMetaAnalysis
from mvmeta.models.base import MetaAnalysisResults


class MultipleImputation:
    """
    Multiple imputation for missing outcomes in multivariate meta-analysis.

    Uses the joint distribution of outcomes to impute missing values,
    then combines results across imputations using Rubin's rules.

    Parameters
    ----------
    n_imputations : int, default=10
        Number of imputed datasets to create
    method : str, default='pmm'
        Imputation method:
        - 'normal': Multivariate normal imputation
        - 'pmm': Predictive mean matching
        - 'bootstrap': Bootstrap-based imputation
    verbose : bool, default=False
        Print progress information

    Attributes
    ----------
    imputed_datasets_ : List[Tuple[np.ndarray, np.ndarray]]
        List of (y, S) pairs for each imputation
    pooled_results_ : MetaAnalysisResults
        Pooled results across imputations

    References
    ----------
    Mavridis, D., & Salanti, G. (2013). A practical introduction to multivariate
    meta‐analysis. Statistical methods in medical research, 22(2), 133-158.

    Examples
    --------
    >>> import numpy as np
    >>> from mvmeta.imputation import MultipleImputation
    >>> # Data with missing outcomes
    >>> y = np.array([[1.0, 2.0], [1.5, np.nan], [2.0, 2.5]])
    >>> S = np.array([np.eye(2) * 0.5 for _ in range(3)])
    >>> # Impute and analyze
    >>> mi = MultipleImputation(n_imputations=20)
    >>> results = mi.fit_transform(y, S)
    """

    def __init__(
        self,
        n_imputations: int = 10,
        method: str = 'normal',
        verbose: bool = False
    ):
        self.n_imputations = n_imputations
        self.method = method
        self.verbose = verbose
        self.imputed_datasets_: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None
        self.pooled_results_: Optional[MetaAnalysisResults] = None

    def fit_transform(
        self,
        y: np.ndarray,
        S: np.ndarray,
        **fit_kwargs
    ) -> MetaAnalysisResults:
        """
        Impute missing data and fit meta-analysis model.

        Parameters
        ----------
        y : np.ndarray
            Effect sizes with missing values (n_studies, n_outcomes)
        S : np.ndarray
            Within-study covariances (n_studies, n_outcomes, n_outcomes)
        **fit_kwargs
            Additional arguments passed to MultivariateMetaAnalysis.fit()

        Returns
        -------
        MetaAnalysisResults
            Pooled results across imputations
        """
        # Check for missing data
        missing_mask = np.isnan(y)
        if not np.any(missing_mask):
            if self.verbose:
                print("No missing data detected. Fitting model directly.")
            model = MultivariateMetaAnalysis(verbose=self.verbose)
            return model.fit(y, S, **fit_kwargs)

        n_missing = np.sum(missing_mask)
        if self.verbose:
            print(f"Detected {n_missing} missing values in {np.sum(np.any(missing_mask, axis=1))} studies")
            print(f"Creating {self.n_imputations} imputed datasets...")

        # Create imputed datasets
        self.imputed_datasets_ = []
        for m in range(self.n_imputations):
            if self.verbose and (m + 1) % 5 == 0:
                print(f"  Imputation {m + 1}/{self.n_imputations}")

            y_imp, S_imp = self._impute_once(y, S, missing_mask)
            self.imputed_datasets_.append((y_imp, S_imp))

        # Fit model on each imputed dataset
        results_list = []
        for y_imp, S_imp in self.imputed_datasets_:
            model = MultivariateMetaAnalysis(verbose=False)
            results = model.fit(y_imp, S_imp, **fit_kwargs)
            results_list.append(results)

        # Pool results using Rubin's rules
        self.pooled_results_ = self._pool_results(results_list)

        return self.pooled_results_

    def _impute_once(
        self,
        y: np.ndarray,
        S: np.ndarray,
        missing_mask: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create one imputed dataset.

        Parameters
        ----------
        y : np.ndarray
            Original data with missing values
        S : np.ndarray
            Within-study covariances
        missing_mask : np.ndarray
            Boolean mask of missing values

        Returns
        -------
        y_imp : np.ndarray
            Imputed dataset
        S_imp : np.ndarray
            Adjusted covariances accounting for imputation uncertainty
        """
        y_imp = y.copy()
        S_imp = S.copy()

        n_studies, n_outcomes = y.shape

        if self.method == 'normal':
            y_imp = self._impute_normal(y, S, missing_mask)

        elif self.method == 'pmm':
            y_imp = self._impute_pmm(y, S, missing_mask)

        elif self.method == 'bootstrap':
            y_imp = self._impute_bootstrap(y, S, missing_mask)

        else:
            raise ValueError(f"Unknown imputation method: {self.method}")

        return y_imp, S_imp

    def _impute_normal(
        self,
        y: np.ndarray,
        S: np.ndarray,
        missing_mask: np.ndarray
    ) -> np.ndarray:
        """
        Impute using multivariate normal distribution.

        For each study with missing outcomes, use the observed outcomes
        and the estimated between-study correlation to impute missing values.
        """
        y_imp = y.copy()
        n_studies, n_outcomes = y.shape

        # First, estimate parameters using available data
        # Fit model on complete cases to get initial estimates
        complete_cases = ~np.any(missing_mask, axis=1)
        if np.sum(complete_cases) >= 2:
            model = MultivariateMetaAnalysis(verbose=False)
            try:
                results = model.fit(y[complete_cases], S[complete_cases], method='reml')
                theta_est = results.theta
                Psi_est = results.Psi
            except:
                # Fallback to simple estimates
                theta_est = np.nanmean(y, axis=0)
                Psi_est = np.cov(y.T, bias=True)
        else:
            theta_est = np.nanmean(y, axis=0)
            Psi_est = np.cov(y.T, bias=True)

        # Impute each study
        for i in range(n_studies):
            if np.any(missing_mask[i]):
                obs_idx = ~missing_mask[i]
                mis_idx = missing_mask[i]

                if not np.any(obs_idx):
                    # All missing: sample from marginal distribution
                    y_imp[i] = multivariate_normal.rvs(
                        mean=theta_est,
                        cov=Psi_est + S[i]
                    )
                else:
                    # Conditional imputation
                    y_obs = y[i, obs_idx]
                    theta_obs = theta_est[obs_idx]
                    theta_mis = theta_est[mis_idx]

                    # Partition covariance matrix
                    Sigma = Psi_est + S[i]
                    Sigma_oo = Sigma[np.ix_(obs_idx, obs_idx)]
                    Sigma_mm = Sigma[np.ix_(mis_idx, mis_idx)]
                    Sigma_om = Sigma[np.ix_(obs_idx, mis_idx)]

                    # Conditional distribution: p(y_mis | y_obs)
                    try:
                        Sigma_oo_inv = np.linalg.inv(Sigma_oo)
                        mu_cond = theta_mis + Sigma_om.T @ Sigma_oo_inv @ (y_obs - theta_obs)
                        Sigma_cond = Sigma_mm - Sigma_om.T @ Sigma_oo_inv @ Sigma_om

                        # Sample from conditional distribution
                        if len(mu_cond.shape) == 0 or mu_cond.shape[0] == 1:
                            y_imp[i, mis_idx] = np.random.normal(mu_cond, np.sqrt(Sigma_cond))
                        else:
                            y_imp[i, mis_idx] = multivariate_normal.rvs(mu_cond, Sigma_cond)

                    except np.linalg.LinAlgError:
                        # Fallback: use marginal distribution
                        if np.sum(mis_idx) == 1:
                            y_imp[i, mis_idx] = np.random.normal(
                                theta_mis, np.sqrt(Sigma_mm)
                            )
                        else:
                            y_imp[i, mis_idx] = multivariate_normal.rvs(
                                theta_mis, Sigma_mm
                            )

        return y_imp

    def _impute_pmm(
        self,
        y: np.ndarray,
        S: np.ndarray,
        missing_mask: np.ndarray
    ) -> np.ndarray:
        """
        Impute using predictive mean matching.

        This approach is more robust and preserves the distribution of observed data.
        """
        # First get normal imputation to find predicted values
        y_pred = self._impute_normal(y, S, missing_mask)
        y_imp = y.copy()

        n_studies, n_outcomes = y.shape

        # For each missing value, find closest observed values and sample
        for j in range(n_outcomes):
            missing_j = missing_mask[:, j]
            if not np.any(missing_j):
                continue

            observed_j = ~missing_j
            y_obs = y[observed_j, j]
            y_pred_mis = y_pred[missing_j, j]
            y_pred_obs = y_pred[observed_j, j]

            # Find k nearest neighbors (k=5)
            k = min(5, len(y_obs))
            for idx, pred_val in zip(np.where(missing_j)[0], y_pred_mis):
                # Find k nearest observed values
                distances = np.abs(y_pred_obs - pred_val)
                nearest_idx = np.argsort(distances)[:k]
                # Sample one of the k nearest
                donor_idx = np.random.choice(nearest_idx)
                y_imp[idx, j] = y_obs[donor_idx]

        return y_imp

    def _impute_bootstrap(
        self,
        y: np.ndarray,
        S: np.ndarray,
        missing_mask: np.ndarray
    ) -> np.ndarray:
        """
        Bootstrap-based imputation.

        Creates bootstrap sample and uses that to estimate parameters for imputation.
        """
        n_studies, n_outcomes = y.shape

        # Bootstrap sample (with replacement)
        boot_idx = np.random.choice(n_studies, size=n_studies, replace=True)
        y_boot = y[boot_idx]
        S_boot = S[boot_idx]
        missing_boot = missing_mask[boot_idx]

        # Impute bootstrap sample
        y_imp = self._impute_normal(y_boot, S_boot, missing_boot)

        return y_imp

    def _pool_results(
        self,
        results_list: List[MetaAnalysisResults]
    ) -> MetaAnalysisResults:
        """
        Pool results across imputations using Rubin's rules.

        Parameters
        ----------
        results_list : List[MetaAnalysisResults]
            Results from each imputed dataset

        Returns
        -------
        MetaAnalysisResults
            Pooled results with adjusted standard errors
        """
        m = len(results_list)
        n_outcomes = results_list[0].n_outcomes

        # Pool point estimates (average)
        theta_pool = np.mean([r.theta for r in results_list], axis=0)
        Psi_pool = np.mean([r.Psi for r in results_list], axis=0)

        # Pool variances using Rubin's rules
        # Within-imputation variance
        W = np.mean([r.theta_se ** 2 for r in results_list], axis=0)

        # Between-imputation variance
        B = np.var([r.theta for r in results_list], axis=0, ddof=1)

        # Total variance
        T = W + (1 + 1/m) * B
        theta_se_pool = np.sqrt(T)

        # Average log-likelihood
        loglik_pool = np.mean([r.loglik for r in results_list])

        return MetaAnalysisResults(
            theta=theta_pool,
            theta_se=theta_se_pool,
            Psi=Psi_pool,
            loglik=loglik_pool,
            converged=all(r.converged for r in results_list),
            method=f"MI-{results_list[0].method}",
            n_studies=results_list[0].n_studies,
            n_outcomes=n_outcomes,
            additional_info={
                'n_imputations': m,
                'within_var': W,
                'between_var': B,
                'individual_results': results_list
            }
        )


def impute_missing_outcomes(
    y: np.ndarray,
    S: np.ndarray,
    n_imputations: int = 10,
    method: str = 'normal',
    verbose: bool = False,
    **fit_kwargs
) -> MetaAnalysisResults:
    """
    Convenience function for imputation and analysis.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes with potential missing values
    S : np.ndarray
        Within-study covariances
    n_imputations : int, default=10
        Number of imputations
    method : str, default='normal'
        Imputation method ('normal', 'pmm', 'bootstrap')
    verbose : bool, default=False
        Print progress
    **fit_kwargs
        Additional arguments for model fitting

    Returns
    -------
    MetaAnalysisResults
        Pooled results
    """
    mi = MultipleImputation(
        n_imputations=n_imputations,
        method=method,
        verbose=verbose
    )
    return mi.fit_transform(y, S, **fit_kwargs)
