"""
Simulation Study 2: Missing Data Methods Performance

Evaluates performance of multiple imputation and pattern mixture models
under different missing data mechanisms.

Research Question: How do different missing data methods perform under
MCAR, MAR, and MNAR mechanisms with varying missing rates?
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from mvmeta import MultivariateMetaAnalysis
from mvmeta.imputation import MultipleImputation, PatternMixtureModel
from mvmeta.utils import simulate_multivariate_ma


def create_missing_data(
    y: np.ndarray,
    S: np.ndarray,
    mechanism: str,
    missing_rate: float,
    seed: int
) -> np.ndarray:
    """
    Create missing data with specified mechanism.

    Parameters
    ----------
    y : np.ndarray
        Complete data (n_studies, n_outcomes)
    S : np.ndarray
        Within-study covariances
    mechanism : str
        'MCAR', 'MAR', or 'MNAR'
    missing_rate : float
        Proportion of values to make missing
    seed : int
        Random seed

    Returns
    -------
    np.ndarray
        Data with missing values
    """
    np.random.seed(seed)
    n_studies, n_outcomes = y.shape
    y_miss = y.copy()

    n_to_remove = int(n_studies * n_outcomes * missing_rate)

    if mechanism == 'MCAR':
        # Missing Completely at Random
        all_indices = [(i, j) for i in range(n_studies) for j in range(n_outcomes)]
        missing_indices = np.random.choice(len(all_indices), n_to_remove, replace=False)
        for idx in missing_indices:
            i, j = all_indices[idx]
            y_miss[i, j] = np.nan

    elif mechanism == 'MAR':
        # Missing at Random (missing depends on observed values)
        # Make outcome 1 missing based on outcome 0 values
        if n_outcomes >= 2:
            # Higher values of outcome 0 → more likely outcome 1 is missing
            outcome0_values = y[:, 0]
            probs = 1 / (1 + np.exp(-(outcome0_values - np.median(outcome0_values))))
            probs = probs / probs.sum() * (n_to_remove / n_outcomes)

            n_to_remove_per_outcome = n_to_remove // n_outcomes
            for j in range(1, n_outcomes):
                missing_studies = np.random.choice(
                    n_studies,
                    size=min(n_to_remove_per_outcome, n_studies),
                    replace=False,
                    p=probs / probs.sum()
                )
                y_miss[missing_studies, j] = np.nan

    elif mechanism == 'MNAR':
        # Missing Not at Random (missing depends on missing value itself)
        # Higher values more likely to be missing
        for j in range(n_outcomes):
            outcome_values = y[:, j]
            # Probability of missingness increases with value
            probs = 1 / (1 + np.exp(-(outcome_values - np.median(outcome_values))))
            probs = probs / probs.sum()

            n_to_remove_outcome = n_to_remove // n_outcomes
            missing_studies = np.random.choice(
                n_studies,
                size=min(n_to_remove_outcome, n_studies),
                replace=False,
                p=probs
            )
            y_miss[missing_studies, j] = np.nan

    return y_miss


def run_missing_data_scenario(
    mechanism: str,
    missing_rate: float,
    n_iterations: int = 500,
    seed_offset: int = 0
) -> pd.DataFrame:
    """Run simulation for one missing data scenario."""
    results = []

    true_effects = np.array([0.5, 0.3])
    n_studies = 30
    n_outcomes = 2

    for iter_num in tqdm(range(n_iterations), desc=f"{mechanism}, rate={missing_rate:.0%}"):
        seed = seed_offset + iter_num

        # Generate complete data
        y_complete, S = simulate_multivariate_ma(
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            true_effects=true_effects,
            between_study_sd=0.4,
            correlation=0.5,
            seed=seed
        )

        # Create missing data
        y_miss = create_missing_data(y_complete, S, mechanism, missing_rate, seed)

        # Methods to compare
        methods = {
            'Complete Case': None,
            'MI-Normal': 'normal',
            'MI-PMM': 'pmm',
            'Pattern Mixture': 'pattern'
        }

        for method_name, method_config in methods.items():
            try:
                if method_name == 'Complete Case':
                    # Complete case analysis
                    complete_mask = ~np.any(np.isnan(y_miss), axis=1)
                    if np.sum(complete_mask) >= 3:
                        y_cc = y_miss[complete_mask]
                        S_cc = S[complete_mask]
                        model = MultivariateMetaAnalysis(verbose=False)
                        fit_results = model.fit(y_cc, S_cc, method='reml')
                    else:
                        continue

                elif method_name == 'Pattern Mixture':
                    # Pattern mixture model
                    pmm = PatternMixtureModel(min_pattern_size=2, verbose=False)
                    fit_results = pmm.fit(y_miss, S, method='reml')

                else:
                    # Multiple imputation
                    mi = MultipleImputation(
                        n_imputations=10,
                        method=method_config,
                        verbose=False
                    )
                    fit_results = mi.fit_transform(y_miss, S, method='reml')

                if fit_results.converged:
                    for outcome_idx in range(n_outcomes):
                        if not np.isnan(fit_results.theta[outcome_idx]):
                            bias = fit_results.theta[outcome_idx] - true_effects[outcome_idx]
                            mse = bias ** 2

                            ci_lower = fit_results.ci_lower[outcome_idx]
                            ci_upper = fit_results.ci_upper[outcome_idx]
                            covered = (ci_lower <= true_effects[outcome_idx] <= ci_upper)

                            results.append({
                                'iteration': iter_num,
                                'mechanism': mechanism,
                                'missing_rate': missing_rate,
                                'method': method_name,
                                'outcome': outcome_idx,
                                'bias': bias,
                                'mse': mse,
                                'se': fit_results.theta_se[outcome_idx],
                                'covered': int(covered),
                                'ci_width': ci_upper - ci_lower,
                                'converged': 1
                            })

            except Exception as e:
                results.append({
                    'iteration': iter_num,
                    'mechanism': mechanism,
                    'missing_rate': missing_rate,
                    'method': method_name,
                    'outcome': 0,
                    'converged': 0,
                    'error': str(e)
                })

    return pd.DataFrame(results)


def main():
    """Run all missing data scenarios."""
    print("=" * 80)
    print("SIMULATION STUDY 2: Missing Data Methods Performance")
    print("=" * 80)

    # Define scenarios
    scenarios = []
    for mechanism in ['MCAR', 'MAR', 'MNAR']:
        for missing_rate in [0.10, 0.30, 0.50]:
            scenarios.append({
                'mechanism': mechanism,
                'missing_rate': missing_rate
            })

    print(f"\nTotal scenarios: {len(scenarios)}")
    print(f"Iterations per scenario: 500")
    print(f"Total datasets: {len(scenarios) * 500:,}\n")

    # Run simulations
    all_results = []

    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] Scenario: {scenario['mechanism']}, "
              f"rate={scenario['missing_rate']:.0%}")

        scenario_results = run_missing_data_scenario(
            mechanism=scenario['mechanism'],
            missing_rate=scenario['missing_rate'],
            n_iterations=500,
            seed_offset=i * 10000
        )

        all_results.append(scenario_results)

    # Combine results
    results_df = pd.concat(all_results, ignore_index=True)

    # Save raw results
    results_df.to_csv('simulations/results/sim02_raw_results.csv', index=False)
    print(f"\nSaved raw results: {len(results_df)} rows")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    converged = results_df[results_df['converged'] == 1].copy()

    summary = converged.groupby(['mechanism', 'missing_rate', 'method']).agg({
        'bias': ['mean', 'std'],
        'mse': 'mean',
        'covered': 'mean',
        'se': 'mean',
        'converged': 'count'
    }).reset_index()

    summary.columns = ['_'.join(col).strip('_') for col in summary.columns.values]
    summary.to_csv('simulations/results/sim02_summary.csv', index=False)

    # Display key findings
    print("\n1. BIAS BY MECHANISM AND METHOD")
    print("-" * 80)
    bias_summary = converged.groupby(['mechanism', 'method'])['bias'].mean().unstack()
    print(bias_summary)

    print("\n2. COVERAGE BY MECHANISM AND MISSING RATE")
    print("-" * 80)
    coverage_summary = converged.groupby(['mechanism', 'missing_rate', 'method'])['covered'].mean().unstack()
    print(coverage_summary)

    print("\n3. MSE BY METHOD")
    print("-" * 80)
    mse_summary = converged.groupby(['method'])['mse'].mean().sort_values()
    print(mse_summary)

    print("\n4. STANDARD ERROR COMPARISON")
    print("-" * 80)
    se_summary = converged.groupby(['mechanism', 'missing_rate', 'method'])['se'].mean().unstack()
    print(se_summary)

    # Create visualizations
    create_visualizations(converged)

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


def create_visualizations(results_df: pd.DataFrame):
    """Create visualizations of missing data simulation results."""
    print("\nCreating visualizations...")

    sns.set_style("whitegrid")

    # 1. Bias by mechanism and method
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for i, mechanism in enumerate(['MCAR', 'MAR', 'MNAR']):
        data = results_df[results_df['mechanism'] == mechanism]
        sns.boxplot(data=data, x='missing_rate', y='bias', hue='method', ax=axes[i])
        axes[i].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[i].set_title(f'{mechanism}')
        axes[i].set_xlabel('Missing Rate')
        axes[i].set_ylabel('Bias')
        if i > 0:
            axes[i].get_legend().remove()

    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_bias_by_mechanism.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Coverage by mechanism
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for i, mechanism in enumerate(['MCAR', 'MAR', 'MNAR']):
        data = results_df[results_df['mechanism'] == mechanism]
        coverage_data = data.groupby(['missing_rate', 'method'])['covered'].mean().reset_index()
        sns.barplot(data=coverage_data, x='missing_rate', y='covered', hue='method', ax=axes[i])
        axes[i].axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='Nominal 95%')
        axes[i].set_title(f'{mechanism}')
        axes[i].set_xlabel('Missing Rate')
        axes[i].set_ylabel('Coverage')
        axes[i].set_ylim([0.8, 1.0])
        if i > 0:
            axes[i].get_legend().remove()

    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_coverage_by_mechanism.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. MSE comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    mse_data = results_df.groupby(['mechanism', 'missing_rate', 'method'])['mse'].mean().reset_index()
    sns.barplot(data=mse_data, x='mechanism', y='mse', hue='method', ax=ax)
    ax.set_title('Mean Squared Error by Mechanism and Method')
    ax.set_ylabel('MSE')
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_mse_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("  Created 3 visualization files")


if __name__ == '__main__':
    import os
    os.makedirs('simulations/results', exist_ok=True)
    os.makedirs('simulations/figures', exist_ok=True)
    main()
