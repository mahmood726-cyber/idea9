"""
FAST Simulation Study 1: Performance Characteristics of Estimation Methods

Streamlined version with fewer scenarios and iterations for rapid completion.
Evaluates bias, coverage, and efficiency of REML and ML estimation.
"""

import numpy as np
import pandas as pd
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
    n_iterations: int = 200,
    seed_offset: int = 0
) -> pd.DataFrame:
    """Run simulation for one scenario."""
    true_effects = np.zeros(n_outcomes)
    results = []

    base_rng = np.random.SeedSequence(seed_offset)
    child_seeds = base_rng.spawn(n_iterations)

    for iter_num in tqdm(range(n_iterations), desc=f"k={n_studies}, p={n_outcomes}, ρ={between_study_correlation:.1f}"):
        iter_seed = int(child_seeds[iter_num].generate_state(1)[0])

        y, S = simulate_multivariate_ma(
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            true_effects=true_effects,
            between_study_sd=between_study_sd,
            within_study_sd=0.3,
            correlation=between_study_correlation,
            seed=iter_seed
        )

        methods = {'REML': 'reml', 'ML': 'ml'}

        for method_name, method_code in methods.items():
            try:
                model = MultivariateMetaAnalysis(variance_structure='unstructured', verbose=False)
                fit_results = model.fit(y, S, method=method_code)

                if fit_results.converged:
                    for outcome_idx in range(n_outcomes):
                        bias = fit_results.theta[outcome_idx] - true_effects[outcome_idx]
                        ci_lower = fit_results.ci_lower[outcome_idx]
                        ci_upper = fit_results.ci_upper[outcome_idx]
                        covered = int(ci_lower <= true_effects[outcome_idx] <= ci_upper)
                        ci_width = ci_upper - ci_lower
                        mse = bias ** 2
                        tau2_est = fit_results.Psi[outcome_idx, outcome_idx]
                        tau2_true = between_study_sd ** 2
                        tau2_bias = tau2_est - tau2_true

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
                            'covered': covered,
                            'ci_width': ci_width,
                            'tau2_est': tau2_est,
                            'tau2_bias': tau2_bias,
                            'rho_est': rho_est,
                            'rho_bias': rho_bias,
                            'converged': 1
                        })
            except:
                pass

    return pd.DataFrame(results)


def main():
    """Run streamlined simulation scenarios."""
    print("=" * 80)
    print("FAST SIMULATION STUDY 1: Estimation Performance")
    print("=" * 80)

    # Key scenarios only for speed
    scenarios = [
        {'n_studies': 10, 'n_outcomes': 2, 'rho': 0.0, 'tau': 0.316},
        {'n_studies': 10, 'n_outcomes': 2, 'rho': 0.5, 'tau': 0.316},
        {'n_studies': 20, 'n_outcomes': 2, 'rho': 0.0, 'tau': 0.316},
        {'n_studies': 20, 'n_outcomes': 2, 'rho': 0.5, 'tau': 0.316},
        {'n_studies': 10, 'n_outcomes': 3, 'rho': 0.0, 'tau': 0.316},
        {'n_studies': 10, 'n_outcomes': 3, 'rho': 0.5, 'tau': 0.316},
        {'n_studies': 20, 'n_outcomes': 3, 'rho': 0.5, 'tau': 0.707},
        {'n_studies': 50, 'n_outcomes': 2, 'rho': 0.5, 'tau': 0.316},
    ]

    print(f"\nScenarios: {len(scenarios)}")
    print(f"Iterations per scenario: 200")
    print(f"Total datasets: {len(scenarios) * 200:,}\n")

    all_results = []

    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] Scenario: k={scenario['n_studies']}, "
              f"p={scenario['n_outcomes']}, ρ={scenario['rho']:.1f}, τ={scenario['tau']:.3f}")

        scenario_results = run_simulation_scenario(
            n_studies=scenario['n_studies'],
            n_outcomes=scenario['n_outcomes'],
            between_study_correlation=scenario['rho'],
            between_study_sd=scenario['tau'],
            n_iterations=200,
            seed_offset=i * 10000
        )

        all_results.append(scenario_results)

    results_df = pd.concat(all_results, ignore_index=True)
    results_df.to_csv('simulations/results/sim01_results.csv', index=False)
    print(f"\nSaved results: {len(results_df)} rows")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    converged = results_df[results_df['converged'] == 1].copy()

    print("\n1. BIAS (Mean by Method and Sample Size)")
    print("-" * 80)
    bias_summary = converged.groupby(['method', 'n_studies'])['bias'].mean()
    print(bias_summary)
    print(f"\nMean absolute bias: {np.abs(converged['bias']).mean():.6f}")

    print("\n2. COVERAGE (Nominal 95%)")
    print("-" * 80)
    coverage_summary = converged.groupby(['method', 'n_studies'])['covered'].mean()
    print(coverage_summary)
    print(f"\nOverall coverage: {converged['covered'].mean():.4f} (target: 0.95)")

    print("\n3. MEAN SQUARED ERROR")
    print("-" * 80)
    mse_summary = converged.groupby(['method', 'n_studies'])['mse'].mean()
    print(mse_summary)

    print("\n4. BETWEEN-STUDY VARIANCE ESTIMATION")
    print("-" * 80)
    tau2_summary = converged.groupby(['method', 'n_studies'])['tau2_bias'].agg(['mean', 'std'])
    print(tau2_summary)

    print("\n5. CORRELATION ESTIMATION (p >= 2)")
    print("-" * 80)
    rho_data = converged[converged['n_outcomes'] >= 2].groupby(['method', 'true_rho'])['rho_bias'].agg(['mean', 'std'])
    print(rho_data)

    # Create visualizations
    create_visualizations(converged)

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print("\nResults saved to:")
    print("  - simulations/results/sim01_results.csv")
    print("  - simulations/figures/sim01_*.png")


def create_visualizations(results_df: pd.DataFrame):
    """Create visualization of simulation results."""
    print("\nCreating visualizations...")

    sns.set_style("whitegrid")
    sns.set_palette("Set2")

    # 1. Bias and Coverage
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.boxplot(data=results_df, x='n_studies', y='bias', hue='method', ax=axes[0])
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[0].set_title('Bias in Effect Estimate by Sample Size', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Number of Studies')
    axes[0].set_ylabel('Bias')

    coverage_data = results_df.groupby(['n_studies', 'method'])['covered'].mean().reset_index()
    sns.barplot(data=coverage_data, x='n_studies', y='covered', hue='method', ax=axes[1])
    axes[1].axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='Nominal 95%')
    axes[1].set_title('Coverage Probability by Sample Size', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Number of Studies')
    axes[1].set_ylabel('Coverage Probability')
    axes[1].legend()
    axes[1].set_ylim([0.85, 1.0])

    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_bias_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Variance estimation
    fig, ax = plt.subplots(figsize=(10, 6))
    tau2_data = results_df.groupby(['n_studies', 'method'])['tau2_bias'].mean().reset_index()
    sns.barplot(data=tau2_data, x='n_studies', y='tau2_bias', hue='method', ax=ax)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.set_title('Bias in Between-Study Variance Estimation', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Studies')
    ax.set_ylabel('τ² Bias')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_variance_estimation.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. MSE comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    mse_data = results_df.groupby(['n_studies', 'method'])['mse'].mean().reset_index()
    sns.barplot(data=mse_data, x='n_studies', y='mse', hue='method', ax=ax)
    ax.set_title('Mean Squared Error by Sample Size', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Studies')
    ax.set_ylabel('MSE')
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim01_mse.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("  ✓ Created 3 visualization files")


if __name__ == '__main__':
    import os
    os.makedirs('simulations/results', exist_ok=True)
    os.makedirs('simulations/figures', exist_ok=True)
    main()
