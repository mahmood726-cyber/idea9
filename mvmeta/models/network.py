"""
Multivariate network meta-analysis models.

Extends network meta-analysis to handle multiple correlated outcomes jointly.
"""

from typing import Optional, Dict, List, Tuple, Literal
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import warnings

from mvmeta.models.base import BaseMetaAnalysis, MetaAnalysisResults


class MultivariateNetworkMetaAnalysis(BaseMetaAnalysis):
    """
    Multivariate network meta-analysis.

    Handles multiple treatments and multiple outcomes simultaneously,
    accounting for:
    1. Correlation between outcomes within studies
    2. Correlation between treatment comparisons
    3. Network structure of treatment comparisons

    The model is:
        y_ijk ~ N(d_jk, S_ijk + Psi)

    where:
        y_ijk: observed effect for study i, comparing treatments j and k, for all outcomes
        d_jk: relative treatment effects (j vs k) across all outcomes (p x 1)
        S_ijk: within-study covariance
        Psi: between-study covariance (p x p)

    Parameters
    ----------
    consistency_model : bool, default=True
        Whether to enforce consistency (transitivity) in the network
    variance_structure : str, default='unstructured'
        Structure for between-study covariance matrix
    verbose : bool, default=False
        Print progress information

    References
    ----------
    Efthimiou, O., Mavridis, D., Riley, R. D., Cipriani, A., & Salanti, G. (2019).
    Joint synthesis of multiple correlated outcomes in networks of interventions.
    Biostatistics, 20(1), 84-98.

    Examples
    --------
    >>> import numpy as np
    >>> from mvmeta import MultivariateNetworkMetaAnalysis
    >>> # Network with 3 treatments, 2 outcomes, 5 studies
    >>> model = MultivariateNetworkMetaAnalysis()
    >>> results = model.fit(data, method='reml')
    """

    def __init__(
        self,
        consistency_model: bool = True,
        variance_structure: Literal['unstructured', 'diagonal'] = 'unstructured',
        verbose: bool = False
    ):
        super().__init__(verbose=verbose)
        self.consistency_model = consistency_model
        self.variance_structure = variance_structure

    def fit(
        self,
        data: pd.DataFrame,
        treatments: Optional[List[str]] = None,
        outcomes: Optional[List[str]] = None,
        reference_treatment: Optional[str] = None,
        method: Literal['reml', 'ml', 'bayesian'] = 'reml',
        **kwargs
    ) -> MetaAnalysisResults:
        """
        Fit multivariate network meta-analysis.

        Parameters
        ----------
        data : pd.DataFrame
            Network data with columns:
            - 'study': study identifier
            - 't1', 't2': treatment codes for comparison
            - One column per outcome with effect sizes
            - Variance/covariance columns (outcome-specific or full covariance)
        treatments : List[str], optional
            List of treatment names. If None, inferred from data.
        outcomes : List[str], optional
            List of outcome names. If None, inferred from data.
        reference_treatment : str, optional
            Reference treatment for effect estimates. If None, uses first treatment.
        method : {'reml', 'ml', 'bayesian'}, default='reml'
            Estimation method
        **kwargs
            Additional arguments for estimation

        Returns
        -------
        MetaAnalysisResults
            Results with treatment effects for all outcomes
        """
        # Parse network data
        y, S, design_matrix, treatment_names, outcome_names = self._parse_network_data(
            data, treatments, outcomes
        )

        n_studies, n_outcomes = y.shape
        n_treatments = len(treatment_names)

        if reference_treatment is None:
            reference_treatment = treatment_names[0]

        if self.verbose:
            print(f"Fitting multivariate network meta-analysis:")
            print(f"  - {n_studies} studies")
            print(f"  - {n_treatments} treatments")
            print(f"  - {n_outcomes} outcomes")
            print(f"  - Reference: {reference_treatment}")

        # Fit the model
        if method == 'reml':
            results = self._fit_network_reml(
                y, S, design_matrix, treatment_names, outcome_names, reference_treatment
            )
        elif method == 'ml':
            results = self._fit_network_ml(
                y, S, design_matrix, treatment_names, outcome_names, reference_treatment
            )
        elif method == 'bayesian':
            results = self._fit_network_bayesian(
                y, S, design_matrix, treatment_names, outcome_names, reference_treatment, **kwargs
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        # Add network-specific information
        results.additional_info['treatment_names'] = treatment_names
        results.additional_info['outcome_names'] = outcome_names
        results.additional_info['reference_treatment'] = reference_treatment
        results.additional_info['design_matrix'] = design_matrix

        self.results_ = results
        return results

    def _parse_network_data(
        self,
        data: pd.DataFrame,
        treatments: Optional[List[str]],
        outcomes: Optional[List[str]]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
        """
        Parse network data into arrays for analysis.

        Returns
        -------
        y : np.ndarray
            Effect sizes (n_studies, n_outcomes)
        S : np.ndarray
            Within-study covariances (n_studies, n_outcomes, n_outcomes)
        design_matrix : np.ndarray
            Design matrix encoding treatment comparisons (n_studies, n_comparisons)
        treatment_names : List[str]
            Names of treatments
        outcome_names : List[str]
            Names of outcomes
        """
        # Identify treatment columns
        if 't1' not in data.columns or 't2' not in data.columns:
            raise ValueError("Data must contain 't1' and 't2' columns for treatment comparisons")

        # Get unique treatments
        if treatments is None:
            all_treatments = pd.concat([data['t1'], data['t2']]).unique()
            treatment_names = sorted(all_treatments)
        else:
            treatment_names = treatments

        # Identify outcome columns
        meta_columns = {'study', 't1', 't2'}
        if outcomes is None:
            # Assume columns not in meta_columns and not starting with 'var_' or 'cov_' are outcomes
            outcome_cols = [c for c in data.columns
                           if c not in meta_columns and
                           not c.startswith('var_') and
                           not c.startswith('cov_') and
                           not c.startswith('se_')]
            outcome_names = outcome_cols
        else:
            outcome_names = outcomes

        n_studies = len(data)
        n_outcomes = len(outcome_names)

        # Extract effect sizes
        y = data[outcome_names].values

        # Extract within-study covariances
        S = np.zeros((n_studies, n_outcomes, n_outcomes))

        for i in range(n_studies):
            for j, outcome in enumerate(outcome_names):
                # Look for variance column
                var_col = f'var_{outcome}'
                se_col = f'se_{outcome}'

                if var_col in data.columns:
                    S[i, j, j] = data.iloc[i][var_col]
                elif se_col in data.columns:
                    S[i, j, j] = data.iloc[i][se_col] ** 2
                else:
                    warnings.warn(f"No variance found for {outcome} in study {i}, using 1.0")
                    S[i, j, j] = 1.0

                # Look for covariances
                for k in range(j + 1, n_outcomes):
                    cov_col = f'cov_{outcome_names[j]}_{outcome_names[k]}'
                    if cov_col in data.columns:
                        S[i, j, k] = data.iloc[i][cov_col]
                        S[i, k, j] = data.iloc[i][cov_col]

        # Create design matrix for treatment comparisons
        n_treatments = len(treatment_names)
        treatment_to_idx = {t: i for i, t in enumerate(treatment_names)}

        # Design matrix: each column represents a basic parameter (treatment vs reference)
        # For consistency model, we use n_treatments - 1 parameters
        design_matrix = np.zeros((n_studies, n_treatments - 1))

        for i, row in data.iterrows():
            t1_idx = treatment_to_idx[row['t1']]
            t2_idx = treatment_to_idx[row['t2']]

            # Effect is t2 - t1
            # Express in terms of treatment vs reference (treatment 0)
            if t1_idx > 0:
                design_matrix[i, t1_idx - 1] = -1
            if t2_idx > 0:
                design_matrix[i, t2_idx - 1] = 1

        return y, S, design_matrix, treatment_names, outcome_names

    def _fit_network_reml(
        self,
        y: np.ndarray,
        S: np.ndarray,
        design_matrix: np.ndarray,
        treatment_names: List[str],
        outcome_names: List[str],
        reference_treatment: str
    ) -> MetaAnalysisResults:
        """
        Fit network meta-analysis using REML.
        """
        n_studies, n_outcomes = y.shape
        n_comparisons = design_matrix.shape[1]

        # Initialize between-study covariance
        Psi_init = np.eye(n_outcomes) * 0.5
        psi_params = self._psi_to_params(Psi_init)

        # REML objective
        def reml_objective(params):
            Psi = self._params_to_psi(params, n_outcomes)
            return self._compute_network_reml_loglik(y, S, Psi, design_matrix)

        # Optimize
        result = minimize(
            reml_objective,
            psi_params,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'disp': self.verbose}
        )

        # Extract results
        Psi_hat = self._params_to_psi(result.x, n_outcomes)
        theta_hat, theta_se = self._estimate_network_effects(y, S, Psi_hat, design_matrix)

        # Reshape to (n_comparisons, n_outcomes)
        theta_effects = theta_hat.reshape(n_comparisons, n_outcomes)
        theta_se_effects = theta_se.reshape(n_comparisons, n_outcomes)

        # Flatten for storage (all treatment effects for outcome 1, then outcome 2, etc.)
        theta_flat = theta_effects.T.flatten()
        theta_se_flat = theta_se_effects.T.flatten()

        return MetaAnalysisResults(
            theta=theta_flat,
            theta_se=theta_se_flat,
            Psi=Psi_hat,
            loglik=-result.fun,
            converged=result.success,
            method='Network-REML',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            additional_info={
                'theta_matrix': theta_effects,  # (n_comparisons, n_outcomes)
                'theta_se_matrix': theta_se_effects,
                'optimizer_result': result
            }
        )

    def _fit_network_ml(
        self,
        y: np.ndarray,
        S: np.ndarray,
        design_matrix: np.ndarray,
        treatment_names: List[str],
        outcome_names: List[str],
        reference_treatment: str
    ) -> MetaAnalysisResults:
        """
        Fit network meta-analysis using ML.
        """
        n_studies, n_outcomes = y.shape
        n_comparisons = design_matrix.shape[1]

        # Initialize
        Psi_init = np.eye(n_outcomes) * 0.5
        psi_params = self._psi_to_params(Psi_init)

        # ML objective
        def ml_objective(params):
            Psi = self._params_to_psi(params, n_outcomes)
            return self._compute_network_ml_loglik(y, S, Psi, design_matrix)

        # Optimize
        result = minimize(
            ml_objective,
            psi_params,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'disp': self.verbose}
        )

        # Extract results
        Psi_hat = self._params_to_psi(result.x, n_outcomes)
        theta_hat, theta_se = self._estimate_network_effects(y, S, Psi_hat, design_matrix)

        theta_effects = theta_hat.reshape(n_comparisons, n_outcomes)
        theta_se_effects = theta_se.reshape(n_comparisons, n_outcomes)

        theta_flat = theta_effects.T.flatten()
        theta_se_flat = theta_se_effects.T.flatten()

        return MetaAnalysisResults(
            theta=theta_flat,
            theta_se=theta_se_flat,
            Psi=Psi_hat,
            loglik=-result.fun,
            converged=result.success,
            method='Network-ML',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            additional_info={
                'theta_matrix': theta_effects,
                'theta_se_matrix': theta_se_effects,
                'optimizer_result': result
            }
        )

    def _fit_network_bayesian(
        self,
        y: np.ndarray,
        S: np.ndarray,
        design_matrix: np.ndarray,
        treatment_names: List[str],
        outcome_names: List[str],
        reference_treatment: str,
        **kwargs
    ) -> MetaAnalysisResults:
        """
        Fit network meta-analysis using Bayesian inference.
        """
        try:
            import pymc as pm
            import pytensor.tensor as pt
        except ImportError:
            raise ImportError("Bayesian estimation requires PyMC")

        n_studies, n_outcomes = y.shape
        n_comparisons = design_matrix.shape[1]

        with pm.Model() as model:
            # Priors for treatment effects
            # theta has shape (n_comparisons, n_outcomes)
            theta = pm.Normal('theta', mu=0, sigma=5, shape=(n_comparisons, n_outcomes))

            # Prior for between-study covariance
            sd_dist = pm.HalfNormal.dist(sigma=1.0)
            chol, corr, stds = pm.LKJCholeskyCov(
                'Psi_chol',
                n=n_outcomes,
                eta=2.0,
                sd_dist=sd_dist,
                compute_corr=True
            )
            Psi = pm.Deterministic('Psi', chol @ chol.T)

            # Likelihood
            for i in range(n_studies):
                # Expected effect for this study
                # mu_i = sum_j design_matrix[i,j] * theta[j, :]
                mu_i = pm.math.dot(design_matrix[i], theta)

                # Covariance
                Vi = S[i] + Psi

                pm.MvNormal(f'y_{i}', mu=mu_i, cov=Vi, observed=y[i])

            # Sample
            trace = pm.sample(
                draws=kwargs.get('n_draws', 2000),
                tune=kwargs.get('n_tune', 1000),
                chains=kwargs.get('n_chains', 4),
                return_inferencedata=True,
                progressbar=self.verbose
            )

        # Extract posteriors
        theta_post = trace.posterior['theta'].values  # (n_chains, n_draws, n_comparisons, n_outcomes)
        theta_hat = theta_post.mean(axis=(0, 1))  # (n_comparisons, n_outcomes)
        theta_se = theta_post.std(axis=(0, 1))

        Psi_hat = trace.posterior['Psi'].mean(dim=['chain', 'draw']).values

        theta_flat = theta_hat.T.flatten()
        theta_se_flat = theta_se.T.flatten()

        return MetaAnalysisResults(
            theta=theta_flat,
            theta_se=theta_se_flat,
            Psi=Psi_hat,
            loglik=0.0,  # Not directly available
            converged=True,
            method='Network-Bayesian',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            additional_info={
                'theta_matrix': theta_hat,
                'theta_se_matrix': theta_se,
                'trace': trace,
                'model': model
            }
        )

    def _compute_network_reml_loglik(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        design_matrix: np.ndarray
    ) -> float:
        """
        Compute REML log-likelihood for network meta-analysis.
        """
        n_studies, n_outcomes = y.shape

        # Construct augmented design matrix for all outcomes
        # X_full has shape (n_studies * n_outcomes, n_comparisons * n_outcomes)
        X_full = np.kron(design_matrix, np.eye(n_outcomes))

        # Stack data
        y_vec = y.flatten()

        # Block diagonal covariance
        V_blocks = []
        for i in range(n_studies):
            V_blocks.append(S[i] + Psi)

        from scipy.linalg import block_diag
        V = block_diag(*V_blocks)

        try:
            V_inv = np.linalg.inv(V)
            XtVinvX = X_full.T @ V_inv @ X_full
            XtVinvy = X_full.T @ V_inv @ y_vec

            beta_hat = np.linalg.solve(XtVinvX, XtVinvy)
            resid = y_vec - X_full @ beta_hat

            loglik = -0.5 * (
                np.linalg.slogdet(V)[1] +
                np.linalg.slogdet(XtVinvX)[1] +
                resid.T @ V_inv @ resid
            )

            return -loglik  # Return negative for minimization

        except np.linalg.LinAlgError:
            return np.inf

    def _compute_network_ml_loglik(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        design_matrix: np.ndarray
    ) -> float:
        """
        Compute ML log-likelihood for network meta-analysis.
        """
        n_studies, n_outcomes = y.shape

        X_full = np.kron(design_matrix, np.eye(n_outcomes))
        y_vec = y.flatten()

        V_blocks = [S[i] + Psi for i in range(n_studies)]
        from scipy.linalg import block_diag
        V = block_diag(*V_blocks)

        try:
            V_inv = np.linalg.inv(V)
            XtVinvX = X_full.T @ V_inv @ X_full
            XtVinvy = X_full.T @ V_inv @ y_vec

            beta_hat = np.linalg.solve(XtVinvX, XtVinvy)
            resid = y_vec - X_full @ beta_hat

            loglik = -0.5 * (
                np.linalg.slogdet(V)[1] +
                resid.T @ V_inv @ resid +
                n_studies * n_outcomes * np.log(2 * np.pi)
            )

            return -loglik

        except np.linalg.LinAlgError:
            return np.inf

    def _estimate_network_effects(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        design_matrix: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estimate treatment effects given Psi.
        """
        n_studies, n_outcomes = y.shape

        X_full = np.kron(design_matrix, np.eye(n_outcomes))
        y_vec = y.flatten()

        V_blocks = [S[i] + Psi for i in range(n_studies)]
        from scipy.linalg import block_diag
        V = block_diag(*V_blocks)

        try:
            V_inv = np.linalg.inv(V)
            XtVinvX = X_full.T @ V_inv @ X_full
            XtVinvy = X_full.T @ V_inv @ y_vec

            beta_hat = np.linalg.solve(XtVinvX, XtVinvy)
            beta_cov = np.linalg.inv(XtVinvX)
            beta_se = np.sqrt(np.diag(beta_cov))

        except np.linalg.LinAlgError:
            beta_hat = np.zeros(X_full.shape[1])
            beta_se = np.full(X_full.shape[1], np.inf)

        return beta_hat, beta_se

    def _psi_to_params(self, Psi: np.ndarray) -> np.ndarray:
        """Convert Psi to parameter vector."""
        n = Psi.shape[0]

        if self.variance_structure == 'unstructured':
            try:
                L = np.linalg.cholesky(Psi)
                params = L[np.tril_indices(n)]
            except np.linalg.LinAlgError:
                eigvals, eigvecs = np.linalg.eigh(Psi)
                eigvals = np.maximum(eigvals, 1e-6)
                Psi_fixed = eigvecs @ np.diag(eigvals) @ eigvecs.T
                L = np.linalg.cholesky(Psi_fixed)
                params = L[np.tril_indices(n)]

        elif self.variance_structure == 'diagonal':
            params = np.sqrt(np.maximum(np.diag(Psi), 1e-6))

        else:
            raise ValueError(f"Unknown variance structure: {self.variance_structure}")

        return params

    def _params_to_psi(self, params: np.ndarray, n_outcomes: int) -> np.ndarray:
        """Convert parameter vector to Psi."""
        if self.variance_structure == 'unstructured':
            L = np.zeros((n_outcomes, n_outcomes))
            L[np.tril_indices(n_outcomes)] = params
            Psi = L @ L.T

        elif self.variance_structure == 'diagonal':
            Psi = np.diag(params ** 2)

        else:
            raise ValueError(f"Unknown variance structure: {self.variance_structure}")

        return Psi

    def get_treatment_effects_table(self) -> pd.DataFrame:
        """
        Get a formatted table of treatment effects.

        Returns
        -------
        pd.DataFrame
            Table with columns: treatment, outcome, estimate, se, ci_lower, ci_upper
        """
        if self.results_ is None:
            raise ValueError("Model not fitted yet")

        treatment_names = self.results_.additional_info['treatment_names']
        outcome_names = self.results_.additional_info['outcome_names']
        theta_matrix = self.results_.additional_info['theta_matrix']
        theta_se_matrix = self.results_.additional_info['theta_se_matrix']

        n_comparisons, n_outcomes = theta_matrix.shape

        rows = []
        for j, outcome in enumerate(outcome_names):
            for i in range(n_comparisons):
                treatment = treatment_names[i + 1]  # +1 because reference is index 0
                rows.append({
                    'treatment': treatment,
                    'outcome': outcome,
                    'estimate': theta_matrix[i, j],
                    'se': theta_se_matrix[i, j],
                    'ci_lower': theta_matrix[i, j] - 1.96 * theta_se_matrix[i, j],
                    'ci_upper': theta_matrix[i, j] + 1.96 * theta_se_matrix[i, j],
                })

        return pd.DataFrame(rows)
