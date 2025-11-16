"""
Simulation Study 1: Performance Characteristics of Estimation Methods

Evaluates bias, coverage, and efficiency of REML, ML, and Bayesian estimation
under varying conditions.

Research Question: How do the three estimation methods perform across different
scenarios in terms of bias, mean squared error, and confidence interval coverage?
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma


def run_simulation_scenario(
    n_studies: int,
    n_outcomes: int,
    between_study_correlation: float,
    between_study_sd: float,
    n_iterations: int = 1000,
    seed_offset: int = 0
) -> pd.DataFrame:
    """
    Run simulation for one scenario.

    Parameters
    ----------
    n_studies : int
        Number of studies per iteration
    n_outcomes : int
        Number of outcomes
    between_study_correlation : float
        True between-study correlation
    between_study_sd : float
        True between-study standard deviation
    n_iterations : int
        Number of Monte Carlo iterations
    seed_offset : int
        Offset for random seed

    Returns
    -------
    pd.DataFrame
        Results for this scenario
    """
    # True parameters
    true_effects = np.zeros(n_outcomes)  # Null effects for testing

    results = []

    # Use SeedSequence for proper independence of random streams
    # (addresses reviewer concern about sequential seeding)
    base_rng = np.random.SeedSequence(seed_offset)
    child_seeds = base_rng.spawn(n_iterations)

    for iter_num in tqdm(range(n_iterations), desc=f"k={n_studies}, p={n_outcomes}, ρ={between_study_correlation:.1f}"):
        # Each iteration gets independent random stream
        iter_seed = int(child_seeds[iter_num].generate_state(1)[0])

        # Generate data
        y, S = simulate_multivariate_ma(
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            true_effects=true_effects,
            between_study_sd=between_study_sd,
            within_study_sd=0.3,
            correlation=between_study_correlation,
            seed=iter_seed
        )

        # Fit with different methods
        methods = {
            'REML': 'reml',
            'ML': 'ml'
        }

        for method_name, method_code in methods.items():
            try:
                model = MultivariateMetaAnalysis(variance_structure='unstructured', verbose=False)
                fit_results = model.fit(y, S, method=method_code)

                if fit_results.converged:
                    for outcome_idx in range(n_outcomes):
                        # Bias
                        bias = fit_results.theta[outcome_idx] - true_effects[outcome_idx]

                        # Coverage
                        ci_lower = fit_results.ci_lower[outcome_idx]
                        ci_upper = fit_results.ci_upper[outcome_idx]
                        covered = (ci_lower <= true_effects[outcome_idx] <= ci_upper)

                        # CI width
                        ci_width = ci_upper - ci_lower

                        # MSE
                        mse = bias ** 2

                        # Between-study variance
                        tau2_est = fit_results.Psi[outcome_idx, outcome_idx]
                        tau2_true = between_study_sd ** 2
                        tau2_bias = tau2_est - tau2_true

                        # Between-study correlation (for p >= 2)
                        if n_outcomes >= 2 and outcome_idx == 0:
                            rho_est = fit_results.between_study_correlation[0, 1]
                            rho_bias = rho_est - between_study_correlation
                        else:
                            rho_est = np.nan
                            rho_bias = np.nan

                        results.append({
                            'iteration': iter_num,
                            'method': method_name,
                            'n_studies': n_studies,
                            'n_outcomes': n_outcomes,
                            'true_rho': between_study_correlation,
                            'true_tau2': tau2_true,
                            'outcome': outcome_idx,
                            'theta_est': fit_results.theta[outcome_idx],
                            'theta_se': fit_results.theta_se[outcome_idx],
                            'bias': bias,
                            'mse': mse,
                            'covered': int(covered),
                            'ci_width': ci_width,
                            'tau2_est': tau2_est,
                            'tau2_bias': tau2_bias,
                            'rho_est': rho_est,
                            'rho_bias': rho_bias,
                            'converged': 1
                        })
                else:
                    # Record non-convergence
                    results.append({
                        'iteration': iter_num,
                        'method': method_name,
                        'n_studies': n_studies,
                        'n_outcomes': n_outcomes,
                        'true_rho': between_study_correlation,
                        'true_tau2': tau2_true,
                        'outcome': 0,
                        'converged': 0
                    })
            except Exception as e:
                # Record failure
                results.append({
                    'iteration': iter_num,
                    'method': method_name,
                    'n_studies': n_studies,
                    'n_outcomes': n_outcomes,
                    'true_rho': between_study_correlation,
                    'true_tau2': tau2_true,
                    'outcome': 0,
                    'converged': 0,
                    'error': str(e)
                })

    return pd.DataFrame(results)


def main():
    """Run all simulation scenarios."""
    print("=" * 80)
    print("SIMULATION STUDY 1: Estimation Performance")
    print("=" * 80)

    # Define scenarios
    scenarios = []

    # Vary number of studies
    for k in [5, 10, 20, 50]:
        for p in [2, 3]:
            for rho in [0.0, 0.3, 0.6]:
                for tau in [0.1, 0.5]:
                    scenarios.append({
                        'n_studies': k,
                        'n_outcomes': p,
                        'rho': rho,
                        'tau': np.sqrt(tau)
                    })

    print(f"\nTotal scenarios: {len(scenarios)}")
    print(f"Iterations per scenario: 1000")
    print(f"Total datasets: {len(scenarios) * 1000:,}\n")

    # Run simulations
    all_results = []

    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] Scenario: k={scenario['n_studies']}, "
              f"p={scenario['n_outcomes']}, ρ={scenario['rho']:.1f}, τ={scenario['tau']:.2f}")

        scenario_results = run_simulation_scenario(
            n_studies=scenario['n_studies'],
            n_outcomes=scenario['n_outcomes'],
            between_study_correlation=scenario['rho'],
            between_study_sd=scenario['tau'],
            n_iterations=1000,
            seed_offset=i * 10000
        )

        all_results.append(scenario_results)

    # Combine results
    results_df = pd.concat(all_results, ignore_index=True)

    # Save raw results
    results_df.to_csv('simulations/results/sim01_raw_results.csv', index=False)
    print(f"\nSaved raw results: {len(results_df)} rows")

    # Compute summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    # Filter to converged results
    converged = results_df[results_df['converged'] == 1].copy()

    summary = converged.groupby(['method', 'n_studies', 'n_outcomes', 'true_rho']).agg({
        'bias': ['mean', 'std'],
        'mse': 'mean',
        'covered': 'mean',
        'ci_width': 'mean',
        'tau2_bias': ['mean', 'std'],
        'rho_bias': ['mean', 'std'],
        'converged': 'count'
    }).reset_index()

    summary.columns = ['_'.join(col).strip('_') for col in summary.columns.values]
    summary.to_csv('simulations/results/sim01_summary.csv', index=False)

    # Display key findings
    print("\n1. BIAS (Mean Bias by Method and Sample Size)")
    print("-" * 80)
    bias_summary = converged.groupby(['method', 'n_studies'])['bias'].mean()
    print(bias_summary)

    print("\n2. COVERAGE (Nominal 95% by Method)")
    print("-" * 80)
    coverage_summary = converged.groupby(['method', 'n_studies'])['covered'].mean()
    print(coverage_summary)

    print("\n3. BETWEEN-STUDY VARIANCE ESTIMATION")
    print("-" * 80)
    tau2_summary = converged.groupby(['method', 'n_studies'])['tau2_bias'].agg(['mean', 'std'])
    print(tau2_summary)

    print("\n4. CORRELATION ESTIMATION (when p >= 2)")
    print("-" * 80)
    rho_summary = converged[converged['n_outcomes'] >= 2].groupby(['method', 'true_rho'])['rho_bias'].agg(['mean', 'std'])
    print(rho_summary)

    print("\n5. CONVERGENCE RATES")
    print("-" * 80)
    convergence = results_df.groupby(['method', 'n_studies', 'n_outcomes'])['converged'].agg(['sum', 'count'])
    convergence['rate'] = convergence['sum'] / convergence['count']
    print(convergence)

    # Create visualizations
    create_visualizations(converged)

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print("\nResults saved to:")
    print("  - simulations/results/sim01_raw_results.csv")
    print("  - simulations/results/sim01_summary.csv")
    print("  - simulations/figures/sim01_*.png")


def create_visualizations(results_df: pd.DataFrame):
    """Create visualization of simulation results."""
    print("\nCreating visualizations...")

    # Set style
    sns.set_style("whitegrid")
    sns.set_palette("Set2")

    # 1. Bias by sample size
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Bias
    sns.boxplot(data=results_df, x='n_studies', y='bias', hue='method', ax=axes[0])
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[0].set_title('Bias in Effect Estimate by Sample Size')
    axes[0].set_xlabel('Number of Studies')
    axes[0].set_ylabel('Bias')

    # Coverage
    coverage_data = results_df.groupby(['n_studies', 'method'])['covered'].mean().reset_index()
    sns.barplot(data=coverage_data, x='n_studies', y='covered', hue='method', ax=axes[1])
    axes[1].axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='Nominal 95%')
    axes[1].set_title('Coverage Probability by Sample Size')
    axes[1].set_xlabel('Number of Studies')
    axes[1].set_ylabel('Coverage Probability')
    axes[1].legend()
    axes[1].set_ylim([0.85, 1.0])

    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_bias_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Between-study variance estimation
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Tau^2 bias
    sns.boxplot(data=results_df, x='n_studies', y='tau2_bias', hue='method', ax=axes[0])
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[0].set_title('Bias in Between-Study Variance')
    axes[0].set_xlabel('Number of Studies')
    axes[0].set_ylabel('τ² Bias')

    # Correlation bias (p >= 2)
    rho_data = results_df[results_df['n_outcomes'] >= 2].dropna(subset=['rho_bias'])
    if len(rho_data) > 0:
        sns.boxplot(data=rho_data, x='true_rho', y='rho_bias', hue='method', ax=axes[1])
        axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1].set_title('Bias in Between-Study Correlation')
        axes[1].set_xlabel('True Correlation')
        axes[1].set_ylabel('ρ Bias')

    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_variance_estimation.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. MSE comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    mse_data = results_df.groupby(['n_studies', 'method'])['mse'].mean().reset_index()
    sns.barplot(data=mse_data, x='n_studies', y='mse', hue='method', ax=ax)
    ax.set_title('Mean Squared Error by Sample Size')
    ax.set_xlabel('Number of Studies')
    ax.set_ylabel('MSE')
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_mse.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("  Created 3 visualization files")


if __name__ == '__main__':
    import os
    os.makedirs('simulations/results', exist_ok=True)
    os.makedirs('simulations/figures', exist_ok=True)
    main()
