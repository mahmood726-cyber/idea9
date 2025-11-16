"""
FAST Simulation Study 2: Missing Data Methods Performance

Streamlined version evaluating missing data methods under MCAR, MAR, MNAR.
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


def create_missing_data(y: np.ndarray, mechanism: str, missing_rate: float, seed: int) -> np.ndarray:
    """Create missing data with specified mechanism."""
    np.random.seed(seed)
    n_studies, n_outcomes = y.shape
    y_miss = y.copy()
    n_to_remove = int(n_studies * n_outcomes * missing_rate)

    if mechanism == 'MCAR':
        all_indices = [(i, j) for i in range(n_studies) for j in range(n_outcomes)]
        missing_indices = np.random.choice(len(all_indices), n_to_remove, replace=False)
        for idx in missing_indices:
            i, j = all_indices[idx]
            y_miss[i, j] = np.nan

    elif mechanism == 'MAR':
        if n_outcomes >= 2:
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
        for j in range(n_outcomes):
            outcome_values = y[:, j]
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


def run_missing_data_scenario(mechanism: str, missing_rate: float, n_iterations: int = 100, seed_offset: int = 0) -> pd.DataFrame:
    """Run simulation for one missing data scenario."""
    results = []
    true_effects = np.array([0.5, 0.3])
    n_studies = 30
    n_outcomes = 2

    base_rng = np.random.SeedSequence(seed_offset)
    child_seeds = base_rng.spawn(n_iterations)

    for iter_num in tqdm(range(n_iterations), desc=f"{mechanism}, rate={missing_rate:.0%}"):
        iter_seed = int(child_seeds[iter_num].generate_state(1)[0])

        y_complete, S = simulate_multivariate_ma(
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            true_effects=true_effects,
            between_study_sd=0.4,
            correlation=0.5,
            seed=iter_seed
        )

        y_miss = create_missing_data(y_complete, mechanism, missing_rate, iter_seed)

        # Complete case analysis
        complete_mask = ~np.any(np.isnan(y_miss), axis=1)
        if np.sum(complete_mask) >= 3:
            try:
                y_cc = y_miss[complete_mask]
                S_cc = S[complete_mask]
                model = MultivariateMetaAnalysis(verbose=False)
                fit_results = model.fit(y_cc, S_cc, method='reml')

                if fit_results.converged:
                    for outcome_idx in range(n_outcomes):
                        bias = fit_results.theta[outcome_idx] - true_effects[outcome_idx]
                        ci_lower = fit_results.ci_lower[outcome_idx]
                        ci_upper = fit_results.ci_upper[outcome_idx]
                        covered = int(ci_lower <= true_effects[outcome_idx] <= ci_upper)

                        results.append({
                            'iteration': iter_num,
                            'mechanism': mechanism,
                            'missing_rate': missing_rate,
                            'method': 'Complete Case',
                            'outcome': outcome_idx,
                            'bias': bias,
                            'mse': bias ** 2,
                            'covered': covered,
                            'n_effective': np.sum(complete_mask)
                        })
            except:
                pass

    return pd.DataFrame(results)


def main():
    """Run streamlined missing data simulations."""
    print("=" * 80)
    print("FAST SIMULATION STUDY 2: Missing Data Methods")
    print("=" * 80)

    scenarios = [
        {'mechanism': 'MCAR', 'rate': 0.10},
        {'mechanism': 'MCAR', 'rate': 0.30},
        {'mechanism': 'MAR', 'rate': 0.10},
        {'mechanism': 'MAR', 'rate': 0.30},
        {'mechanism': 'MNAR', 'rate': 0.10},
        {'mechanism': 'MNAR', 'rate': 0.30},
    ]

    print(f"\nScenarios: {len(scenarios)}")
    print(f"Iterations per scenario: 100")
    print(f"Total datasets: {len(scenarios) * 100}\n")

    all_results = []

    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] Scenario: {scenario['mechanism']}, rate={scenario['rate']:.0%}")

        scenario_results = run_missing_data_scenario(
            mechanism=scenario['mechanism'],
            missing_rate=scenario['rate'],
            n_iterations=100,
            seed_offset=i * 10000
        )

        all_results.append(scenario_results)

    results_df = pd.concat(all_results, ignore_index=True)
    results_df.to_csv('simulations/results/sim02_results.csv', index=False)
    print(f"\nSaved results: {len(results_df)} rows")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    print("\n1. BIAS by Mechanism and Missing Rate")
    print("-" * 80)
    bias_summary = results_df.groupby(['mechanism', 'missing_rate', 'method'])['bias'].mean()
    print(bias_summary)

    print("\n2. COVERAGE by Mechanism")
    print("-" * 80)
    coverage_summary = results_df.groupby(['mechanism', 'missing_rate', 'method'])['covered'].mean()
    print(coverage_summary)

    print("\n3. EFFECTIVE SAMPLE SIZE")
    print("-" * 80)
    n_eff_summary = results_df.groupby(['mechanism', 'missing_rate'])['n_effective'].mean()
    print(n_eff_summary)

    # Create visualizations
    create_visualizations(results_df)

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print("\nResults saved to:")
    print("  - simulations/results/sim02_results.csv")
    print("  - simulations/figures/sim02_*.png")


def create_visualizations(results_df: pd.DataFrame):
    """Create visualization of simulation results."""
    print("\nCreating visualizations...")

    sns.set_style("whitegrid")
    sns.set_palette("Set2")

    # 1. Bias by mechanism and rate
    fig, ax = plt.subplots(figsize=(12, 6))
    bias_data = results_df.groupby(['mechanism', 'missing_rate'])['bias'].mean().reset_index()
    sns.barplot(data=bias_data, x='mechanism', y='bias', hue='missing_rate', ax=ax)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.set_title('Bias by Missing Data Mechanism and Rate', fontsize=12, fontweight='bold')
    ax.set_xlabel('Missing Data Mechanism')
    ax.set_ylabel('Bias')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_bias.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Coverage
    fig, ax = plt.subplots(figsize=(12, 6))
    coverage_data = results_df.groupby(['mechanism', 'missing_rate'])['covered'].mean().reset_index()
    sns.barplot(data=coverage_data, x='mechanism', y='covered', hue='missing_rate', ax=ax)
    ax.axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='Nominal 95%')
    ax.set_title('Coverage Probability by Mechanism', fontsize=12, fontweight='bold')
    ax.set_xlabel('Missing Data Mechanism')
    ax.set_ylabel('Coverage Probability')
    ax.set_ylim([0.8, 1.0])
    ax.legend()
    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. MSE comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    mse_data = results_df.groupby(['mechanism', 'missing_rate'])['mse'].mean().reset_index()
    sns.barplot(data=mse_data, x='mechanism', y='mse', hue='missing_rate', ax=ax)
    ax.set_title('Mean Squared Error by Mechanism', fontsize=12, fontweight='bold')
    ax.set_xlabel('Missing Data Mechanism')
    ax.set_ylabel('MSE')
    plt.tight_layout()
    plt.savefig('simulations/figures/sim02_mse.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("  ✓ Created 3 visualization files")


if __name__ == '__main__':
    import os
    os.makedirs('simulations/results', exist_ok=True)
    os.makedirs('simulations/figures', exist_ok=True)
    main()
