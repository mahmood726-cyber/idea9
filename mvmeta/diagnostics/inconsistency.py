"""
Inconsistency detection for network meta-analysis.

⚠️ WARNING: This module contains INCOMPLETE implementations marked as future work.
These functions require full network meta-analysis infrastructure which is not yet complete.

Status of functions:
- node_splitting(): INCOMPLETE - indirect estimates return None
- design_inconsistency_test(): PARTIAL - works for simple designs
- loop_inconsistency(): WORKS - for basic loop detection
- global_inconsistency_test(): INCOMPLETE - requires full NMA model
- detect_all_inconsistencies(): PARTIAL - runs available tests only

These functions are NOT exported in the public API and should be considered
experimental/unstable. Full implementation is planned for future releases.

For current functionality, use only the heterogeneity and influence diagnostics
from mvmeta.diagnostics.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import norm, chi2
import warnings

from mvmeta.models.multivariate import MultivariateMetaAnalysis


def node_splitting(
    data: pd.DataFrame,
    treatment1: str,
    treatment2: str,
    outcomes: List[str],
    method: str = 'reml'
) -> Dict:
    """
    Node-splitting for inconsistency detection.

    ⚠️ WARNING: INCOMPLETE IMPLEMENTATION
    This function computes direct estimates but returns None for indirect estimates.
    Indirect estimation requires full network meta-analysis model which is not yet implemented.
    Marked as future work - DO NOT use in production.

    Compares direct and indirect evidence for a specific comparison.

    Parameters
    ----------
    data : pd.DataFrame
        Network data
    treatment1, treatment2 : str
        Treatments to split
    outcomes : List[str]
        Outcome column names
    method : str, default='reml'
        Estimation method

    Returns
    -------
    Dict
        Node-splitting results including:
        - direct_estimate: Array of direct estimates
        - indirect_estimate: None (NOT IMPLEMENTED)
        - message: Status message indicating incomplete implementation

    Notes
    -----
    This function is NOT complete and NOT exported in the public API.
    Use with caution and expect None values for indirect estimates.
    """
    n_outcomes = len(outcomes)

    # Separate direct and indirect evidence
    direct_mask = ((data['t1'] == treatment1) & (data['t2'] == treatment2)) | \
                  ((data['t1'] == treatment2) & (data['t2'] == treatment1))

    direct_data = data[direct_mask].copy()
    indirect_data = data[~direct_mask].copy()

    if len(direct_data) == 0:
        return {
            'comparison': f'{treatment1} vs {treatment2}',
            'has_direct_evidence': False,
            'message': 'No direct evidence available'
        }

    if len(indirect_data) < 3:
        return {
            'comparison': f'{treatment1} vs {treatment2}',
            'has_indirect_evidence': False,
            'message': 'Insufficient indirect evidence'
        }

    results = {
        'comparison': f'{treatment1} vs {treatment2}',
        'n_direct': len(direct_data),
        'n_indirect': len(indirect_data),
        'has_direct_evidence': True,
        'has_indirect_evidence': True
    }

    # Estimate from direct evidence
    y_direct = direct_data[outcomes].values
    S_direct = []
    for idx, row in direct_data.iterrows():
        S_i = np.eye(n_outcomes)
        for j, outcome in enumerate(outcomes):
            var_col = f'var_{outcome}'
            if var_col in direct_data.columns:
                S_i[j, j] = row[var_col]
            else:
                S_i[j, j] = 1.0  # Default variance
        S_direct.append(S_i)
    S_direct = np.array(S_direct)

    try:
        model_direct = MultivariateMetaAnalysis(verbose=False)
        fit_direct = model_direct.fit(y_direct, S_direct, method=method)

        if fit_direct.converged:
            results['direct_estimate'] = fit_direct.theta
            results['direct_se'] = fit_direct.theta_se
        else:
            results['direct_estimate'] = None
            results['message'] = 'Direct evidence model did not converge'
            return results

    except Exception as e:
        results['direct_estimate'] = None
        results['message'] = f'Error fitting direct evidence: {str(e)}'
        return results

    # Estimate from indirect evidence (requires full network model)
    # For simplicity, we'll compute this by fitting the network without direct evidence
    try:
        from mvmeta import MultivariateNetworkMetaAnalysis

        model_indirect = MultivariateNetworkMetaAnalysis(verbose=False)
        fit_indirect = model_indirect.fit(indirect_data, outcomes=outcomes, method=method)

        # Extract estimate for this comparison from network model
        # This is a simplified version - full implementation would extract
        # the specific comparison from the network model results
        results['indirect_estimate'] = None  # Placeholder
        results['indirect_se'] = None
        results['message'] = 'Indirect estimation requires full network model implementation'

    except Exception as e:
        results['indirect_estimate'] = None
        results['message'] = f'Error with indirect evidence: {str(e)}'

    # Test for inconsistency (if we have both estimates)
    if results.get('direct_estimate') is not None and results.get('indirect_estimate') is not None:
        diff = results['direct_estimate'] - results['indirect_estimate']
        se_diff = np.sqrt(results['direct_se']**2 + results['indirect_se']**2)
        z_stat = diff / se_diff
        p_value = 2 * (1 - norm.cdf(np.abs(z_stat)))

        results['inconsistency'] = {
            'difference': diff,
            'se': se_diff,
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    return results


def design_inconsistency_test(
    data: pd.DataFrame,
    outcomes: List[str],
    method: str = 'reml'
) -> pd.DataFrame:
    """
    Design-based inconsistency test.

    Tests for inconsistency by comparing studies with different designs
    (different sets of treatments compared).

    Parameters
    ----------
    data : pd.DataFrame
        Network data
    outcomes : List[str]
        Outcome column names
    method : str, default='reml'
        Estimation method

    Returns
    -------
    pd.DataFrame
        Inconsistency test results by design
    """
    # Group studies by design (set of treatments compared)
    data['design'] = data.apply(
        lambda row: tuple(sorted([row['t1'], row['t2']])),
        axis=1
    )

    designs = data['design'].unique()

    results = []

    for design in designs:
        design_data = data[data['design'] == design]

        if len(design_data) < 2:
            continue

        # Fit model for this design
        y = design_data[outcomes].values
        n_outcomes = len(outcomes)
        S = []

        for idx, row in design_data.iterrows():
            S_i = np.eye(n_outcomes)
            for j, outcome in enumerate(outcomes):
                var_col = f'var_{outcome}'
                if var_col in design_data.columns:
                    S_i[j, j] = row[var_col]
                else:
                    S_i[j, j] = 1.0
            S.append(S_i)
        S = np.array(S)

        try:
            model = MultivariateMetaAnalysis(verbose=False)
            fit = model.fit(y, S, method=method)

            if fit.converged:
                # Test for heterogeneity within design
                for j, outcome in enumerate(outcomes):
                    results.append({
                        'design': f'{design[0]} vs {design[1]}',
                        'outcome': outcome,
                        'n_studies': len(design_data),
                        'estimate': fit.theta[j],
                        'se': fit.theta_se[j],
                        'tau2': fit.Psi[j, j],
                        'I2': fit.I2[j] if fit.I2 is not None else None
                    })

        except Exception as e:
            warnings.warn(f"Error fitting design {design}: {str(e)}")

    return pd.DataFrame(results)


def loop_inconsistency(
    data: pd.DataFrame,
    loop_treatments: List[str],
    outcomes: List[str]
) -> Dict:
    """
    Detect inconsistency in a closed loop of treatments.

    For a loop A-B-C-A, checks if the sum of effects around
    the loop equals zero (consistency requirement).

    Parameters
    ----------
    data : pd.DataFrame
        Network data
    loop_treatments : List[str]
        Treatments forming a closed loop (e.g., ['A', 'B', 'C'])
    outcomes : List[str]
        Outcome column names

    Returns
    -------
    Dict
        Loop inconsistency test results
    """
    if len(loop_treatments) < 3:
        raise ValueError("Loop must have at least 3 treatments")

    n_outcomes = len(outcomes)
    n_treatments = len(loop_treatments)

    # Extract comparisons in the loop
    loop_effects = []
    loop_variances = []

    for i in range(n_treatments):
        t1 = loop_treatments[i]
        t2 = loop_treatments[(i + 1) % n_treatments]

        # Find comparison
        comparison = data[
            ((data['t1'] == t1) & (data['t2'] == t2)) |
            ((data['t1'] == t2) & (data['t2'] == t1))
        ]

        if len(comparison) == 0:
            return {
                'loop': ' → '.join(loop_treatments + [loop_treatments[0]]),
                'complete': False,
                'message': f'Missing comparison {t1} vs {t2}'
            }

        # Get pooled estimate for this comparison
        y = comparison[outcomes].values
        S = []
        for idx, row in comparison.iterrows():
            S_i = np.eye(n_outcomes)
            for j, outcome in enumerate(outcomes):
                var_col = f'var_{outcome}'
                if var_col in comparison.columns:
                    S_i[j, j] = row[var_col]
                else:
                    S_i[j, j] = 1.0
            S.append(S_i)
        S = np.array(S)

        try:
            model = MultivariateMetaAnalysis(verbose=False)
            fit = model.fit(y, S, method='reml')

            # Adjust sign if needed
            if comparison.iloc[0]['t1'] == t2:
                effect = -fit.theta
            else:
                effect = fit.theta

            loop_effects.append(effect)
            loop_variances.append(fit.theta_se ** 2)

        except Exception:
            return {
                'loop': ' → '.join(loop_treatments + [loop_treatments[0]]),
                'complete': False,
                'message': f'Error fitting comparison {t1} vs {t2}'
            }

    # Sum effects around loop (should be zero under consistency)
    loop_effects = np.array(loop_effects)
    loop_variances = np.array(loop_variances)

    sum_effects = np.sum(loop_effects, axis=0)
    var_sum = np.sum(loop_variances, axis=0)
    se_sum = np.sqrt(var_sum)

    # Test statistics
    z_stats = sum_effects / se_sum
    p_values = 2 * (1 - norm.cdf(np.abs(z_stats)))

    results = {
        'loop': ' → '.join(loop_treatments + [loop_treatments[0]]),
        'complete': True,
        'n_comparisons': n_treatments,
        'outcomes': {}
    }

    for j, outcome in enumerate(outcomes):
        results['outcomes'][outcome] = {
            'inconsistency_factor': sum_effects[j],
            'se': se_sum[j],
            'z_statistic': z_stats[j],
            'p_value': p_values[j],
            'significant': p_values[j] < 0.05
        }

    return results


def global_inconsistency_test(
    data: pd.DataFrame,
    outcomes: List[str],
    method: str = 'reml'
) -> Dict:
    """
    Global test for inconsistency in network.

    Compares consistency model with full inconsistency model
    using likelihood ratio test.

    Parameters
    ----------
    data : pd.DataFrame
        Network data
    outcomes : List[str]
        Outcome column names
    method : str, default='reml'
        Estimation method

    Returns
    -------
    Dict
        Global inconsistency test results
    """
    from mvmeta import MultivariateNetworkMetaAnalysis

    try:
        # Fit consistency model
        model_consistent = MultivariateNetworkMetaAnalysis(
            consistency_model=True,
            verbose=False
        )
        fit_consistent = model_consistent.fit(data, outcomes=outcomes, method=method)

        # Fit inconsistency model (not yet implemented)
        # This would fit separate effects for each comparison
        # For now, return placeholder

        results = {
            'consistency_loglik': fit_consistent.loglik,
            'inconsistency_loglik': None,
            'test': 'Not yet implemented',
            'message': 'Full inconsistency model requires additional implementation'
        }

        return results

    except Exception as e:
        return {
            'error': str(e),
            'message': 'Error in global inconsistency test'
        }


def detect_all_inconsistencies(
    data: pd.DataFrame,
    outcomes: List[str],
    method: str = 'reml'
) -> Dict[str, pd.DataFrame]:
    """
    Run comprehensive inconsistency detection.

    Parameters
    ----------
    data : pd.DataFrame
        Network data
    outcomes : List[str]
        Outcome column names
    method : str, default='reml'
        Estimation method

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of inconsistency test results
    """
    results = {}

    # Design inconsistency
    print("Running design inconsistency test...")
    results['design'] = design_inconsistency_test(data, outcomes, method)

    # Global test
    print("Running global inconsistency test...")
    results['global'] = global_inconsistency_test(data, outcomes, method)

    return results
