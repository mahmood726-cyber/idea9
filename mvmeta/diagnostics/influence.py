"""
Influence and outlier diagnostics for multivariate meta-analysis.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from tqdm import tqdm

from mvmeta.models.multivariate import MultivariateMetaAnalysis
from mvmeta.models.base import MetaAnalysisResults


def leave_one_out_analysis(
    y: np.ndarray,
    S: np.ndarray,
    method: str = 'reml',
    verbose: bool = False
) -> pd.DataFrame:
    """
    Leave-one-out influence analysis.

    Fits the model n times, each time leaving out one study,
    to assess the influence of each study on the results.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    method : str, default='reml'
        Estimation method
    verbose : bool, default=False
        Print progress

    Returns
    -------
    pd.DataFrame
        Influence statistics for each study
    """
    n_studies, n_outcomes = y.shape

    # Fit full model
    model_full = MultivariateMetaAnalysis(verbose=False)
    results_full = model_full.fit(y, S, method=method)

    # Store results
    influence_stats = []

    iterator = tqdm(range(n_studies), desc="Leave-one-out analysis") if verbose else range(n_studies)

    for i in iterator:
        # Create dataset without study i
        y_loo = np.delete(y, i, axis=0)
        S_loo = np.delete(S, i, axis=0)

        # Fit model
        try:
            model_loo = MultivariateMetaAnalysis(verbose=False)
            results_loo = model_loo.fit(y_loo, S_loo, method=method)

            if results_loo.converged:
                for j in range(n_outcomes):
                    # Change in pooled estimate
                    delta_theta = results_full.theta[j] - results_loo.theta[j]

                    # Standardized change
                    std_delta = delta_theta / results_full.theta_se[j]

                    # Change in heterogeneity
                    delta_tau2 = results_full.Psi[j, j] - results_loo.Psi[j, j]

                    # Change in log-likelihood
                    delta_loglik = results_full.loglik - results_loo.loglik

                    influence_stats.append({
                        'study': i,
                        'outcome': j,
                        'theta_full': results_full.theta[j],
                        'theta_loo': results_loo.theta[j],
                        'delta_theta': delta_theta,
                        'std_delta_theta': std_delta,
                        'tau2_full': results_full.Psi[j, j],
                        'tau2_loo': results_loo.Psi[j, j],
                        'delta_tau2': delta_tau2,
                        'delta_loglik': delta_loglik,
                        'converged': 1
                    })
            else:
                influence_stats.append({
                    'study': i,
                    'outcome': 0,
                    'converged': 0
                })

        except Exception as e:
            influence_stats.append({
                'study': i,
                'outcome': 0,
                'converged': 0,
                'error': str(e)
            })

    return pd.DataFrame(influence_stats)


def cook_distance(
    y: np.ndarray,
    S: np.ndarray,
    results: MetaAnalysisResults
) -> np.ndarray:
    """
    Compute Cook's distance for each study (multivariate version).

    Cook's distance measures the influence of each study on the
    overall meta-analysis results.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    results : MetaAnalysisResults
        Fitted model results

    Returns
    -------
    np.ndarray
        Cook's distances (n_studies,)
    """
    n_studies, n_outcomes = y.shape

    cooks_d = np.zeros(n_studies)

    for i in range(n_studies):
        # Residual for study i
        resid_i = y[i] - results.theta

        # Total covariance for study i
        V_i = S[i] + results.Psi

        try:
            # Multivariate Cook's distance
            V_i_inv = np.linalg.inv(V_i)
            cooks_d[i] = (resid_i @ V_i_inv @ resid_i) / n_outcomes

        except np.linalg.LinAlgError:
            cooks_d[i] = np.nan

    return cooks_d


def identify_outliers(
    y: np.ndarray,
    S: np.ndarray,
    results: MetaAnalysisResults,
    threshold: float = 3.0
) -> Dict[int, dict]:
    """
    Identify outlying studies.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    results : MetaAnalysisResults
        Fitted model results
    threshold : float, default=3.0
        Threshold for standardized residuals

    Returns
    -------
    Dict[int, dict]
        Dictionary of outlier information indexed by study ID
    """
    n_studies, n_outcomes = y.shape

    outliers = {}

    for i in range(n_studies):
        # Residuals
        resid_i = y[i] - results.theta

        # Standardized residuals
        std_resid = np.zeros(n_outcomes)
        for j in range(n_outcomes):
            V_ij = S[i, j, j] + results.Psi[j, j]
            std_resid[j] = resid_i[j] / np.sqrt(V_ij)

        # Check if any standardized residual exceeds threshold
        max_std_resid = np.max(np.abs(std_resid))

        if max_std_resid > threshold:
            outliers[i] = {
                'max_std_residual': max_std_resid,
                'std_residuals': std_resid,
                'raw_residuals': resid_i,
                'outlier_outcomes': np.where(np.abs(std_resid) > threshold)[0].tolist()
            }

    return outliers


def studentized_residuals(
    y: np.ndarray,
    S: np.ndarray,
    results: MetaAnalysisResults
) -> np.ndarray:
    """
    Compute studentized (externally standardized) residuals.

    These are more robust than internally standardized residuals
    for outlier detection.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    results : MetaAnalysisResults
        Fitted model results

    Returns
    -------
    np.ndarray
        Studentized residuals (n_studies, n_outcomes)
    """
    n_studies, n_outcomes = y.shape

    stud_resid = np.zeros((n_studies, n_outcomes))

    for i in range(n_studies):
        # Leave-one-out residual
        y_loo = np.delete(y, i, axis=0)
        S_loo = np.delete(S, i, axis=0)

        try:
            model_loo = MultivariateMetaAnalysis(verbose=False)
            results_loo = model_loo.fit(y_loo, S_loo, method='reml')

            if results_loo.converged:
                resid_i = y[i] - results_loo.theta

                for j in range(n_outcomes):
                    V_ij = S[i, j, j] + results_loo.Psi[j, j]
                    stud_resid[i, j] = resid_i[j] / np.sqrt(V_ij)
            else:
                stud_resid[i, :] = np.nan

        except Exception:
            stud_resid[i, :] = np.nan

    return stud_resid


def hat_values(
    S: np.ndarray,
    Psi: np.ndarray
) -> np.ndarray:
    """
    Compute hat (leverage) values for each study.

    Parameters
    ----------
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    Psi : np.ndarray
        Between-study covariance (n_outcomes, n_outcomes)

    Returns
    -------
    np.ndarray
        Hat values (n_studies,)
    """
    n_studies = S.shape[0]
    n_outcomes = Psi.shape[0]

    hat_vals = np.zeros(n_studies)

    # Compute sum of inverse covariances
    V_inv_sum = np.zeros((n_outcomes, n_outcomes))
    for i in range(n_studies):
        V_i = S[i] + Psi
        try:
            V_inv_sum += np.linalg.inv(V_i)
        except np.linalg.LinAlgError:
            continue

    # Hat value for each study
    for i in range(n_studies):
        V_i = S[i] + Psi
        try:
            V_i_inv = np.linalg.inv(V_i)
            V_sum_inv = np.linalg.inv(V_inv_sum)

            # Trace of influence matrix
            H_i = V_i_inv @ V_sum_inv @ V_i_inv @ V_i
            hat_vals[i] = np.trace(H_i) / n_outcomes

        except np.linalg.LinAlgError:
            hat_vals[i] = np.nan

    return hat_vals


def dfbetas(
    y: np.ndarray,
    S: np.ndarray,
    results: MetaAnalysisResults
) -> np.ndarray:
    """
    Compute DFBETAS (standardized difference in betas).

    Measures the change in each parameter estimate when a study
    is removed, standardized by the standard error.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    results : MetaAnalysisResults
        Fitted model results

    Returns
    -------
    np.ndarray
        DFBETAS (n_studies, n_outcomes)
    """
    n_studies, n_outcomes = y.shape

    dfbetas_vals = np.zeros((n_studies, n_outcomes))

    for i in range(n_studies):
        y_loo = np.delete(y, i, axis=0)
        S_loo = np.delete(S, i, axis=0)

        try:
            model_loo = MultivariateMetaAnalysis(verbose=False)
            results_loo = model_loo.fit(y_loo, S_loo, method='reml')

            if results_loo.converged:
                for j in range(n_outcomes):
                    delta = results.theta[j] - results_loo.theta[j]
                    dfbetas_vals[i, j] = delta / results.theta_se[j]
            else:
                dfbetas_vals[i, :] = np.nan

        except Exception:
            dfbetas_vals[i, :] = np.nan

    return dfbetas_vals


def comprehensive_diagnostics(
    y: np.ndarray,
    S: np.ndarray,
    results: MetaAnalysisResults,
    study_labels: List[str] = None
) -> pd.DataFrame:
    """
    Compute comprehensive influence diagnostics for all studies.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    results : MetaAnalysisResults
        Fitted model results
    study_labels : List[str], optional
        Labels for studies

    Returns
    -------
    pd.DataFrame
        Comprehensive diagnostics for each study
    """
    n_studies, n_outcomes = y.shape

    if study_labels is None:
        study_labels = [f"Study_{i+1}" for i in range(n_studies)]

    # Compute various diagnostics
    cooks_d = cook_distance(y, S, results)
    hat_vals = hat_values(S, results.Psi)
    outliers = identify_outliers(y, S, results, threshold=3.0)

    diagnostics = []

    for i in range(n_studies):
        # Residuals
        resid = y[i] - results.theta

        # Standardized residuals
        std_resid = np.zeros(n_outcomes)
        for j in range(n_outcomes):
            V_ij = S[i, j, j] + results.Psi[j, j]
            std_resid[j] = resid[j] / np.sqrt(V_ij)

        diagnostics.append({
            'study': study_labels[i],
            'study_id': i,
            'cooks_d': cooks_d[i],
            'hat_value': hat_vals[i],
            'max_std_resid': np.max(np.abs(std_resid)),
            'is_outlier': i in outliers,
            'is_influential': cooks_d[i] > 4 / n_studies if not np.isnan(cooks_d[i]) else False,
            'high_leverage': hat_vals[i] > 2 * n_outcomes / n_studies if not np.isnan(hat_vals[i]) else False
        })

    return pd.DataFrame(diagnostics)
