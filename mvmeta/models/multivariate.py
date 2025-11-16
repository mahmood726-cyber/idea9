"""
Multivariate meta-analysis models.

Implements multivariate random-effects meta-analysis with multiple correlated outcomes.
"""

from typing import Optional, Literal, Tuple
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import block_diag
import warnings

from mvmeta.models.base import BaseMetaAnalysis, MetaAnalysisResults


class MultivariateMetaAnalysis(BaseMetaAnalysis):
    """
    Multivariate random-effects meta-analysis.

    This model allows for multiple correlated outcomes to be analyzed jointly,
    borrowing strength across outcomes through the between-study correlation structure.

    The model is:
        y_i ~ N(theta + X_i*beta, S_i + Psi)

    where:
        y_i: observed effects for study i (p x 1)
        theta: pooled effects (p x 1)
        X_i: covariates for study i
        beta: regression coefficients
        S_i: within-study covariance (p x p)
        Psi: between-study covariance (p x p)

    Parameters
    ----------
    variance_structure : str, default='unstructured'
        Structure for between-study covariance:
        - 'unstructured': Full covariance matrix
        - 'diagonal': Independent outcomes
        - 'compound_symmetry': Common correlation
        - 'proportional': S_i proportional to Psi
    verbose : bool, default=False
        Print progress information

    References
    ----------
    Jackson, D., Riley, R., & White, I. R. (2011). Multivariate meta‐analysis:
    potential and promise. Statistics in medicine, 30(20), 2481-2498.

    Examples
    --------
    >>> import numpy as np
    >>> from mvmeta import MultivariateMetaAnalysis
    >>> # Simulate data
    >>> np.random.seed(42)
    >>> n_studies, n_outcomes = 10, 2
    >>> y = np.random.randn(n_studies, n_outcomes)
    >>> S = np.array([np.eye(n_outcomes) * 0.5 for _ in range(n_studies)])
    >>> # Fit model
    >>> model = MultivariateMetaAnalysis()
    >>> results = model.fit(y, S, method='reml')
    >>> print(results.summary())
    """

    def __init__(
        self,
        variance_structure: Literal[
            'unstructured', 'diagonal', 'compound_symmetry', 'proportional'
        ] = 'unstructured',
        verbose: bool = False
    ):
        super().__init__(verbose=verbose)
        self.variance_structure = variance_structure

    def fit(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None,
        method: Literal['reml', 'ml', 'bayesian'] = 'reml',
        init_Psi: Optional[np.ndarray] = None,
        **kwargs
    ) -> MetaAnalysisResults:
        """
        Fit the multivariate meta-analysis model.

        Parameters
        ----------
        y : np.ndarray
            Effect size estimates, shape (n_studies, n_outcomes)
        S : np.ndarray
            Within-study covariance matrices, shape (n_studies, n_outcomes, n_outcomes)
        X : np.ndarray, optional
            Study-level covariates, shape (n_studies, n_covariates)
        method : {'reml', 'ml', 'bayesian'}, default='reml'
            Estimation method
        init_Psi : np.ndarray, optional
            Initial value for between-study covariance
        **kwargs
            Additional arguments passed to estimation method

        Returns
        -------
        MetaAnalysisResults
            Results object with estimates and diagnostics
        """
        # Validate inputs
        y, S, X = self._validate_inputs(y, S, X)
        n_studies, n_outcomes = y.shape

        if self.verbose:
            print(f"Fitting multivariate meta-analysis with {n_studies} studies "
                  f"and {n_outcomes} outcomes using {method.upper()} estimation...")

        # Choose estimation method
        if method == 'reml':
            results = self._fit_reml(y, S, X, init_Psi)
        elif method == 'ml':
            results = self._fit_ml(y, S, X, init_Psi)
        elif method == 'bayesian':
            results = self._fit_bayesian(y, S, X, **kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")

        self.results_ = results
        return results

    def _fit_reml(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None,
        init_Psi: Optional[np.ndarray] = None
    ) -> MetaAnalysisResults:
        """
        Fit using Restricted Maximum Likelihood (REML).

        REML accounts for the uncertainty in estimating fixed effects.
        """
        n_studies, n_outcomes = y.shape

        # Initialize Psi
        if init_Psi is None:
            # Method of moments initialization
            init_Psi = self._initialize_psi(y, S)

        # Parameterize Psi
        psi_params = self._psi_to_params(init_Psi)

        # Define REML objective function
        def reml_objective(params):
            Psi = self._params_to_psi(params, n_outcomes)
            return self._compute_reml_loglik(y, S, Psi, X)

        # Optimize
        result = minimize(
            reml_objective,
            psi_params,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'disp': self.verbose}
        )

        # Extract results
        Psi_hat = self._params_to_psi(result.x, n_outcomes)
        theta_hat, theta_se = self._estimate_theta(y, S, Psi_hat, X)

        # Compute diagnostics
        Q_stat, I2 = self._compute_heterogeneity(y, S, theta_hat)
        residuals = y - theta_hat
        fitted_values = np.tile(theta_hat, (n_studies, 1))

        return MetaAnalysisResults(
            theta=theta_hat,
            theta_se=theta_se,
            Psi=Psi_hat,
            loglik=-result.fun,
            converged=result.success,
            method='REML',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            residuals=residuals,
            Q_stat=Q_stat,
            I2=I2,
            fitted_values=fitted_values,
            additional_info={'optimizer_result': result}
        )

    def _fit_ml(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None,
        init_Psi: Optional[np.ndarray] = None
    ) -> MetaAnalysisResults:
        """
        Fit using Maximum Likelihood (ML).
        """
        n_studies, n_outcomes = y.shape

        # Initialize
        if init_Psi is None:
            init_Psi = self._initialize_psi(y, S)

        psi_params = self._psi_to_params(init_Psi)

        # Define ML objective
        def ml_objective(params):
            Psi = self._params_to_psi(params, n_outcomes)
            return self._compute_ml_loglik(y, S, Psi, X)

        # Optimize
        result = minimize(
            ml_objective,
            psi_params,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'disp': self.verbose}
        )

        # Extract results
        Psi_hat = self._params_to_psi(result.x, n_outcomes)
        theta_hat, theta_se = self._estimate_theta(y, S, Psi_hat, X)

        # Diagnostics
        Q_stat, I2 = self._compute_heterogeneity(y, S, theta_hat)
        residuals = y - theta_hat

        return MetaAnalysisResults(
            theta=theta_hat,
            theta_se=theta_se,
            Psi=Psi_hat,
            loglik=-result.fun,
            converged=result.success,
            method='ML',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            residuals=residuals,
            Q_stat=Q_stat,
            I2=I2,
            additional_info={'optimizer_result': result}
        )

    def _fit_bayesian(
        self,
        y: np.ndarray,
        S: np.ndarray,
        X: Optional[np.ndarray] = None,
        **kwargs
    ) -> MetaAnalysisResults:
        """
        Fit using Bayesian inference with PyMC.
        """
        try:
            import pymc as pm
            import arviz as az
        except ImportError:
            raise ImportError(
                "Bayesian estimation requires PyMC. Install with: pip install pymc"
            )

        n_studies, n_outcomes = y.shape

        with pm.Model() as model:
            # Prior for pooled effects
            theta = pm.Normal('theta', mu=0, sigma=10, shape=n_outcomes)

            # Prior for between-study covariance
            # Use LKJ prior for correlation + separate scale parameters
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
                Vi = S[i] + Psi
                pm.MvNormal(f'y_{i}', mu=theta, cov=Vi, observed=y[i])

            # Sample
            n_draws = kwargs.get('n_draws', 2000)
            n_tune = kwargs.get('n_tune', 1000)
            n_chains = kwargs.get('n_chains', 4)

            trace = pm.sample(
                draws=n_draws,
                tune=n_tune,
                chains=n_chains,
                return_inferencedata=True,
                progressbar=self.verbose
            )

        # Extract posterior means
        theta_hat = trace.posterior['theta'].mean(dim=['chain', 'draw']).values
        theta_se = trace.posterior['theta'].std(dim=['chain', 'draw']).values
        Psi_hat = trace.posterior['Psi'].mean(dim=['chain', 'draw']).values

        # Compute log-likelihood (approximate)
        loglik = self._compute_ml_loglik(y, S, Psi_hat, X, return_neg=False)

        return MetaAnalysisResults(
            theta=theta_hat,
            theta_se=theta_se,
            Psi=Psi_hat,
            loglik=loglik,
            converged=True,
            method='Bayesian',
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            additional_info={'trace': trace, 'model': model}
        )

    def _compute_reml_loglik(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        X: Optional[np.ndarray],
        return_neg: bool = True
    ) -> float:
        """
        Compute REML log-likelihood.

        The REML likelihood marginalizes over fixed effects.
        """
        n_studies, n_outcomes = y.shape

        # Construct block-diagonal covariance matrix
        V_list = [S[i] + Psi for i in range(n_studies)]
        V_inv_list = [np.linalg.inv(V) for V in V_list]

        # Stack observations
        y_vec = y.flatten()

        # Design matrix for fixed effects
        if X is None:
            Z = np.kron(np.ones((n_studies, 1)), np.eye(n_outcomes))
        else:
            # Meta-regression design matrix
            raise NotImplementedError("Meta-regression not yet implemented")

        # Compute REML components
        V_inv = block_diag(*V_inv_list)
        ZtVinvZ = Z.T @ V_inv @ Z
        ZtVinvy = Z.T @ V_inv @ y_vec

        try:
            # Fixed effects estimate
            beta_hat = np.linalg.solve(ZtVinvZ, ZtVinvy)
            resid = y_vec - Z @ beta_hat

            # REML log-likelihood
            loglik = -0.5 * (
                np.sum([np.linalg.slogdet(V)[1] for V in V_list]) +
                np.linalg.slogdet(ZtVinvZ)[1] +
                resid.T @ V_inv @ resid
            )

            if return_neg:
                return -loglik
            return loglik

        except np.linalg.LinAlgError:
            return np.inf if return_neg else -np.inf

    def _compute_ml_loglik(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        X: Optional[np.ndarray],
        return_neg: bool = True
    ) -> float:
        """Compute ML log-likelihood."""
        n_studies, n_outcomes = y.shape

        loglik = 0.0
        for i in range(n_studies):
            Vi = S[i] + Psi
            try:
                # Compute log-likelihood for study i
                sign, logdet = np.linalg.slogdet(Vi)
                if sign <= 0:
                    return np.inf if return_neg else -np.inf

                Vi_inv = np.linalg.inv(Vi)
                theta_hat, _ = self._estimate_theta(y, S, Psi, X)
                resid = y[i] - theta_hat

                loglik += -0.5 * (logdet + resid @ Vi_inv @ resid)

            except np.linalg.LinAlgError:
                return np.inf if return_neg else -np.inf

        if return_neg:
            return -loglik
        return loglik

    def _estimate_theta(
        self,
        y: np.ndarray,
        S: np.ndarray,
        Psi: np.ndarray,
        X: Optional[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estimate pooled effects theta given Psi.

        Uses generalized least squares (weighted average).
        """
        n_studies, n_outcomes = y.shape

        # Compute weights
        V_inv_sum = np.zeros((n_outcomes, n_outcomes))
        V_inv_y_sum = np.zeros(n_outcomes)

        for i in range(n_studies):
            Vi = S[i] + Psi
            try:
                Vi_inv = np.linalg.inv(Vi)
                V_inv_sum += Vi_inv
                V_inv_y_sum += Vi_inv @ y[i]
            except np.linalg.LinAlgError:
                warnings.warn(f"Singular covariance for study {i}, skipping")
                continue

        # Pooled estimate
        try:
            theta_cov = np.linalg.inv(V_inv_sum)
            theta = theta_cov @ V_inv_y_sum
            theta_se = np.sqrt(np.diag(theta_cov))
        except np.linalg.LinAlgError:
            theta = np.zeros(n_outcomes)
            theta_se = np.full(n_outcomes, np.inf)

        return theta, theta_se

    def _initialize_psi(self, y: np.ndarray, S: np.ndarray) -> np.ndarray:
        """
        Initialize Psi using method of moments.
        """
        n_studies, n_outcomes = y.shape

        # Simple method: use sample covariance of y minus average within-study variance
        y_cov = np.cov(y.T)
        S_avg = np.mean(S, axis=0)

        Psi_init = y_cov - S_avg
        # Ensure positive semi-definite
        eigvals, eigvecs = np.linalg.eigh(Psi_init)
        eigvals = np.maximum(eigvals, 1e-6)
        Psi_init = eigvecs @ np.diag(eigvals) @ eigvecs.T

        return Psi_init

    def _psi_to_params(self, Psi: np.ndarray) -> np.ndarray:
        """
        Convert Psi matrix to parameter vector for optimization.

        Uses Cholesky decomposition to ensure positive semi-definiteness.
        """
        n = Psi.shape[0]

        if self.variance_structure == 'unstructured':
            # Use Cholesky decomposition
            try:
                L = np.linalg.cholesky(Psi)
                # Extract lower triangular elements
                params = L[np.tril_indices(n)]
            except np.linalg.LinAlgError:
                # If not positive definite, use eigenvalue decomposition
                eigvals, eigvecs = np.linalg.eigh(Psi)
                eigvals = np.maximum(eigvals, 1e-6)
                Psi_fixed = eigvecs @ np.diag(eigvals) @ eigvecs.T
                L = np.linalg.cholesky(Psi_fixed)
                params = L[np.tril_indices(n)]

        elif self.variance_structure == 'diagonal':
            # Only variances
            params = np.sqrt(np.maximum(np.diag(Psi), 1e-6))

        elif self.variance_structure == 'compound_symmetry':
            # Common variance and correlation
            var = np.mean(np.diag(Psi))
            if n > 1:
                corr = np.mean(Psi[np.triu_indices(n, k=1)]) / var
                corr = np.clip(corr, -0.99, 0.99)
            else:
                corr = 0
            params = np.array([np.sqrt(var), corr])

        else:
            raise ValueError(f"Unknown variance structure: {self.variance_structure}")

        return params

    def _params_to_psi(self, params: np.ndarray, n_outcomes: int) -> np.ndarray:
        """
        Convert parameter vector to Psi matrix.
        """
        if self.variance_structure == 'unstructured':
            # Reconstruct from Cholesky factor
            L = np.zeros((n_outcomes, n_outcomes))
            L[np.tril_indices(n_outcomes)] = params
            Psi = L @ L.T

        elif self.variance_structure == 'diagonal':
            Psi = np.diag(params ** 2)

        elif self.variance_structure == 'compound_symmetry':
            var = params[0] ** 2
            corr = params[1]
            Psi = var * (corr * np.ones((n_outcomes, n_outcomes)) +
                         (1 - corr) * np.eye(n_outcomes))

        else:
            raise ValueError(f"Unknown variance structure: {self.variance_structure}")

        return Psi

    def _compute_heterogeneity(
        self,
        y: np.ndarray,
        S: np.ndarray,
        theta: np.ndarray
    ) -> Tuple[float, np.ndarray]:
        """
        Compute Cochran's Q and I-squared statistics.
        """
        n_studies, n_outcomes = y.shape

        # Compute Q statistic (multivariate generalization)
        Q = 0.0
        for i in range(n_studies):
            resid = y[i] - theta
            try:
                Q += resid @ np.linalg.inv(S[i]) @ resid
            except np.linalg.LinAlgError:
                continue

        # I-squared for each outcome
        I2 = np.zeros(n_outcomes)
        for j in range(n_outcomes):
            # Univariate Q for outcome j
            Q_j = 0.0
            for i in range(n_studies):
                if S[i, j, j] > 0:
                    Q_j += ((y[i, j] - theta[j]) ** 2) / S[i, j, j]

            # I-squared
            df = n_studies - 1
            if Q_j > df:
                I2[j] = (Q_j - df) / Q_j
            else:
                I2[j] = 0.0

        return Q, I2
