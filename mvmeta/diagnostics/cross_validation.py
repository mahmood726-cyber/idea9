"""
Cross-validation for multivariate meta-analysis.

Implements various cross-validation strategies to assess model performance
and prediction accuracy.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import norm, chi2
from tqdm import tqdm
import warnings

from mvmeta.models.multivariate import MultivariateMetaAnalysis
from mvmeta.models.base import MetaAnalysisResults


def leave_one_out_cv(
    y: np.ndarray,
    S: np.ndarray,
    method: str = 'reml',
    alpha: float = 0.05,
    verbose: bool = False
) -> Dict:
    """
    Leave-one-out cross-validation for multivariate meta-analysis.

    For each study, fits the model on all other studies and evaluates
    prediction performance on the left-out study.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    method : str, default='reml'
        Estimation method ('reml' or 'ml')
    alpha : float, default=0.05
        Significance level for prediction intervals
    verbose : bool, default=False
        Show progress bar

    Returns
    -------
    Dict
        Cross-validation results including:
        - predictions: DataFrame with predictions for each study
        - mspe: Mean squared prediction error by outcome
        - coverage: Prediction interval coverage by outcome
        - calibration: Calibration statistics
        - cv_loglik: Cross-validated log-likelihood

    Examples
    --------
    >>> from mvmeta.utils import simulate_multivariate_ma
    >>> y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)
    >>> cv_results = leave_one_out_cv(y, S, verbose=True)
    >>> print(f"MSPE: {cv_results['mspe']}")
    >>> print(f"Coverage: {cv_results['coverage']}")
    """
    n_studies, n_outcomes = y.shape

    predictions = []
    squared_errors = np.zeros((n_studies, n_outcomes))
    coverage_indicator = np.zeros((n_studies, n_outcomes))
    log_predictive_densities = []

    iterator = tqdm(range(n_studies), desc="LOOCV") if verbose else range(n_studies)

    for i in iterator:
        # Training set: all studies except i
        y_train = np.delete(y, i, axis=0)
        S_train = np.delete(S, i, axis=0)

        # Test study
        y_test = y[i]
        S_test = S[i]

        try:
            # Fit model on training data
            model = MultivariateMetaAnalysis(verbose=False)
            fit = model.fit(y_train, S_train, method=method)

            if not fit.converged:
                warnings.warn(f"Model did not converge for fold {i}")
                continue

            # Predictions for test study
            y_pred = fit.theta

            # Prediction variance: Var(y_i | theta, Psi) = S_i + Psi
            V_pred = S_test + fit.Psi

            # Prediction error
            pred_error = y_test - y_pred
            squared_errors[i] = pred_error ** 2

            # Prediction intervals (multivariate)
            z_crit = norm.ppf(1 - alpha / 2)
            se_pred = np.sqrt(np.diag(V_pred))
            pi_lower = y_pred - z_crit * se_pred
            pi_upper = y_pred + z_crit * se_pred

            # Coverage
            for j in range(n_outcomes):
                coverage_indicator[i, j] = int(pi_lower[j] <= y_test[j] <= pi_upper[j])

            # Log predictive density
            try:
                V_pred_inv = np.linalg.inv(V_pred)
                logdet = np.linalg.slogdet(V_pred)[1]
                lpd = -0.5 * (n_outcomes * np.log(2 * np.pi) + logdet +
                             pred_error @ V_pred_inv @ pred_error)
                log_predictive_densities.append(lpd)
            except np.linalg.LinAlgError:
                pass

            # Store detailed predictions
            for j in range(n_outcomes):
                predictions.append({
                    'study': i,
                    'outcome': j,
                    'y_true': y_test[j],
                    'y_pred': y_pred[j],
                    'pred_error': pred_error[j],
                    'se_pred': se_pred[j],
                    'pi_lower': pi_lower[j],
                    'pi_upper': pi_upper[j],
                    'covered': coverage_indicator[i, j],
                    'tau2_est': fit.Psi[j, j]
                })

        except Exception as e:
            if verbose:
                warnings.warn(f"Error in fold {i}: {str(e)}")
            continue

    # Aggregate results
    predictions_df = pd.DataFrame(predictions)

    # Mean squared prediction error by outcome
    mspe = np.mean(squared_errors, axis=0)

    # Coverage by outcome
    coverage = np.mean(coverage_indicator, axis=0)

    # Cross-validated log-likelihood
    cv_loglik = np.sum(log_predictive_densities) if log_predictive_densities else np.nan

    # Calibration: compare empirical vs nominal coverage
    calibration = {
        'nominal_coverage': 1 - alpha,
        'empirical_coverage': coverage,
        'coverage_gap': coverage - (1 - alpha),
        'coverage_se': np.sqrt(coverage * (1 - coverage) / n_studies)
    }

    results = {
        'predictions': predictions_df,
        'mspe': mspe,
        'coverage': coverage,
        'calibration': calibration,
        'cv_loglik': cv_loglik,
        'n_studies': n_studies,
        'n_outcomes': n_outcomes,
        'method': method
    }

    return results


def k_fold_cv(
    y: np.ndarray,
    S: np.ndarray,
    k: int = 5,
    method: str = 'reml',
    alpha: float = 0.05,
    seed: int = None,
    verbose: bool = False
) -> Dict:
    """
    K-fold cross-validation for multivariate meta-analysis.

    Divides studies into k folds, trains on k-1 folds, validates on 1 fold.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    k : int, default=5
        Number of folds
    method : str, default='reml'
        Estimation method
    alpha : float, default=0.05
        Significance level for prediction intervals
    seed : int, optional
        Random seed for fold assignment
    verbose : bool, default=False
        Show progress

    Returns
    -------
    Dict
        Cross-validation results similar to leave_one_out_cv

    Examples
    --------
    >>> from mvmeta.utils import simulate_multivariate_ma
    >>> y, S = simulate_multivariate_ma(n_studies=50, n_outcomes=3, seed=42)
    >>> cv_results = k_fold_cv(y, S, k=10, verbose=True)
    """
    n_studies, n_outcomes = y.shape

    if k > n_studies:
        raise ValueError(f"k={k} cannot be larger than n_studies={n_studies}")

    # Randomly assign studies to folds
    if seed is not None:
        np.random.seed(seed)

    fold_ids = np.random.permutation(n_studies) % k

    predictions = []
    squared_errors = []
    coverage_indicator = []
    log_predictive_densities = []

    iterator = tqdm(range(k), desc=f"{k}-fold CV") if verbose else range(k)

    for fold in iterator:
        # Test set: studies in this fold
        test_mask = fold_ids == fold
        train_mask = ~test_mask

        n_test = np.sum(test_mask)
        if n_test == 0:
            continue

        y_train = y[train_mask]
        S_train = S[train_mask]
        y_test = y[test_mask]
        S_test = S[test_mask]

        try:
            # Fit model on training data
            model = MultivariateMetaAnalysis(verbose=False)
            fit = model.fit(y_train, S_train, method=method)

            if not fit.converged:
                warnings.warn(f"Model did not converge for fold {fold}")
                continue

            # Predictions for test studies
            for i, test_idx in enumerate(np.where(test_mask)[0]):
                y_pred = fit.theta
                V_pred = S_test[i] + fit.Psi
                pred_error = y_test[i] - y_pred

                squared_errors.append(pred_error ** 2)

                # Prediction intervals
                z_crit = norm.ppf(1 - alpha / 2)
                se_pred = np.sqrt(np.diag(V_pred))
                pi_lower = y_pred - z_crit * se_pred
                pi_upper = y_pred + z_crit * se_pred

                covered = np.array([pi_lower[j] <= y_test[i, j] <= pi_upper[j]
                                   for j in range(n_outcomes)])
                coverage_indicator.append(covered)

                # Log predictive density
                try:
                    V_pred_inv = np.linalg.inv(V_pred)
                    logdet = np.linalg.slogdet(V_pred)[1]
                    lpd = -0.5 * (n_outcomes * np.log(2 * np.pi) + logdet +
                                 pred_error @ V_pred_inv @ pred_error)
                    log_predictive_densities.append(lpd)
                except np.linalg.LinAlgError:
                    pass

                # Store predictions
                for j in range(n_outcomes):
                    predictions.append({
                        'fold': fold,
                        'study': test_idx,
                        'outcome': j,
                        'y_true': y_test[i, j],
                        'y_pred': y_pred[j],
                        'pred_error': pred_error[j],
                        'se_pred': se_pred[j],
                        'pi_lower': pi_lower[j],
                        'pi_upper': pi_upper[j],
                        'covered': int(covered[j])
                    })

        except Exception as e:
            if verbose:
                warnings.warn(f"Error in fold {fold}: {str(e)}")
            continue

    # Aggregate results
    predictions_df = pd.DataFrame(predictions)

    if len(squared_errors) > 0:
        squared_errors = np.array(squared_errors)
        coverage_indicator = np.array(coverage_indicator)

        mspe = np.mean(squared_errors, axis=0)
        coverage = np.mean(coverage_indicator, axis=0)
        cv_loglik = np.sum(log_predictive_densities)

        calibration = {
            'nominal_coverage': 1 - alpha,
            'empirical_coverage': coverage,
            'coverage_gap': coverage - (1 - alpha),
            'coverage_se': np.sqrt(coverage * (1 - coverage) / len(squared_errors))
        }
    else:
        mspe = np.full(n_outcomes, np.nan)
        coverage = np.full(n_outcomes, np.nan)
        cv_loglik = np.nan
        calibration = None

    results = {
        'predictions': predictions_df,
        'mspe': mspe,
        'coverage': coverage,
        'calibration': calibration,
        'cv_loglik': cv_loglik,
        'n_studies': n_studies,
        'n_outcomes': n_outcomes,
        'k': k,
        'method': method
    }

    return results


def cross_validate(
    y: np.ndarray,
    S: np.ndarray,
    cv_type: str = 'loo',
    k: int = 5,
    method: str = 'reml',
    alpha: float = 0.05,
    seed: int = None,
    verbose: bool = False
) -> Dict:
    """
    Unified cross-validation interface.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances (n_studies, n_outcomes, n_outcomes)
    cv_type : str, default='loo'
        Type of cross-validation: 'loo' (leave-one-out) or 'kfold'
    k : int, default=5
        Number of folds (only for cv_type='kfold')
    method : str, default='reml'
        Estimation method
    alpha : float, default=0.05
        Significance level for prediction intervals
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Show progress

    Returns
    -------
    Dict
        Cross-validation results

    Examples
    --------
    >>> from mvmeta.utils import simulate_multivariate_ma
    >>> y, S = simulate_multivariate_ma(n_studies=30, n_outcomes=2, seed=42)
    >>>
    >>> # Leave-one-out CV
    >>> cv_loo = cross_validate(y, S, cv_type='loo', verbose=True)
    >>> print(f"LOOCV MSPE: {cv_loo['mspe']}")
    >>>
    >>> # 10-fold CV
    >>> cv_kfold = cross_validate(y, S, cv_type='kfold', k=10, seed=42, verbose=True)
    >>> print(f"10-fold MSPE: {cv_kfold['mspe']}")
    """
    if cv_type.lower() in ['loo', 'loocv', 'leave-one-out']:
        return leave_one_out_cv(y, S, method=method, alpha=alpha, verbose=verbose)
    elif cv_type.lower() in ['kfold', 'k-fold']:
        return k_fold_cv(y, S, k=k, method=method, alpha=alpha, seed=seed, verbose=verbose)
    else:
        raise ValueError(f"Unknown cv_type: {cv_type}. Use 'loo' or 'kfold'.")


def print_cv_summary(cv_results: Dict) -> None:
    """
    Print a summary of cross-validation results.

    Parameters
    ----------
    cv_results : Dict
        Results from cross_validate, leave_one_out_cv, or k_fold_cv

    Examples
    --------
    >>> cv_results = cross_validate(y, S, verbose=True)
    >>> print_cv_summary(cv_results)
    """
    print("=" * 70)
    print("CROSS-VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\nMethod: {cv_results['method'].upper()}")
    print(f"Number of studies: {cv_results['n_studies']}")
    print(f"Number of outcomes: {cv_results['n_outcomes']}")

    if 'k' in cv_results:
        print(f"Cross-validation: {cv_results['k']}-fold")
    else:
        print("Cross-validation: Leave-one-out")

    print("\n" + "-" * 70)
    print("PREDICTION PERFORMANCE")
    print("-" * 70)

    print("\nMean Squared Prediction Error (MSPE):")
    for j, mspe in enumerate(cv_results['mspe']):
        print(f"  Outcome {j}: {mspe:.6f}")

    if cv_results['calibration'] is not None:
        cal = cv_results['calibration']
        print("\nPrediction Interval Coverage:")
        print(f"  Nominal: {cal['nominal_coverage']:.3f}")
        for j, cov in enumerate(cal['empirical_coverage']):
            gap = cal['coverage_gap'][j]
            se = cal['coverage_se'][j]
            print(f"  Outcome {j}: {cov:.3f} (gap: {gap:+.3f} ± {se:.3f})")

    if not np.isnan(cv_results['cv_loglik']):
        print(f"\nCross-validated log-likelihood: {cv_results['cv_loglik']:.2f}")

    print("\n" + "=" * 70)


def calibration_plot(
    cv_results: Dict,
    outcome_idx: int = 0,
    n_bins: int = 10,
    save_path: str = None
):
    """
    Create calibration plot for cross-validated predictions.

    Compares predicted standard errors with actual prediction errors.

    Parameters
    ----------
    cv_results : Dict
        Results from cross-validation
    outcome_idx : int, default=0
        Which outcome to plot
    n_bins : int, default=10
        Number of bins for calibration
    save_path : str, optional
        Path to save figure

    Examples
    --------
    >>> cv_results = cross_validate(y, S, verbose=True)
    >>> calibration_plot(cv_results, outcome_idx=0, save_path='calibration.png')
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("matplotlib is required for plotting")

    df = cv_results['predictions']
    df_outcome = df[df['outcome'] == outcome_idx].copy()

    # Standardized errors
    df_outcome['std_error'] = df_outcome['pred_error'] / df_outcome['se_pred']

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Predicted vs actual errors
    axes[0].scatter(df_outcome['se_pred'], np.abs(df_outcome['pred_error']),
                   alpha=0.5, s=30)

    # Add reference line (perfect calibration)
    max_se = df_outcome['se_pred'].max()
    axes[0].plot([0, max_se], [0, max_se], 'r--', label='Perfect calibration')

    axes[0].set_xlabel('Predicted SE')
    axes[0].set_ylabel('Absolute Prediction Error')
    axes[0].set_title(f'Calibration: Outcome {outcome_idx}')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Panel 2: Distribution of standardized errors
    axes[1].hist(df_outcome['std_error'], bins=20, density=True,
                alpha=0.7, edgecolor='black', label='Observed')

    # Overlay standard normal
    x = np.linspace(-4, 4, 100)
    axes[1].plot(x, norm.pdf(x), 'r-', linewidth=2, label='N(0,1)')

    axes[1].set_xlabel('Standardized Prediction Error')
    axes[1].set_ylabel('Density')
    axes[1].set_title('Distribution of Standardized Errors')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved calibration plot to {save_path}")
    else:
        plt.show()

    plt.close()


def compare_methods_cv(
    y: np.ndarray,
    S: np.ndarray,
    methods: List[str] = ['reml', 'ml'],
    cv_type: str = 'loo',
    k: int = 5,
    seed: int = None,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Compare different estimation methods using cross-validation.

    Parameters
    ----------
    y : np.ndarray
        Effect sizes
    S : np.ndarray
        Within-study covariances
    methods : List[str], default=['reml', 'ml']
        Estimation methods to compare
    cv_type : str, default='loo'
        Cross-validation type
    k : int, default=5
        Number of folds (for k-fold CV)
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Show progress

    Returns
    -------
    pd.DataFrame
        Comparison of methods with MSPE and coverage

    Examples
    --------
    >>> comparison = compare_methods_cv(y, S, methods=['reml', 'ml'], verbose=True)
    >>> print(comparison)
    """
    n_outcomes = y.shape[1]

    results = []

    for method in methods:
        if verbose:
            print(f"\nEvaluating {method.upper()}...")

        cv_results = cross_validate(
            y, S,
            cv_type=cv_type,
            k=k,
            method=method,
            seed=seed,
            verbose=verbose
        )

        for j in range(n_outcomes):
            results.append({
                'method': method.upper(),
                'outcome': j,
                'mspe': cv_results['mspe'][j],
                'coverage': cv_results['coverage'][j],
                'cv_loglik': cv_results['cv_loglik']
            })

    return pd.DataFrame(results)
