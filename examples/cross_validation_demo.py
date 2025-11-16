"""
Demonstration of Cross-Validation for Multivariate Meta-Analysis

This example shows how to:
1. Perform leave-one-out cross-validation (LOOCV)
2. Perform k-fold cross-validation
3. Compare estimation methods using CV
4. Interpret cross-validation results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.diagnostics import (
    cross_validate,
    print_cv_summary,
    calibration_plot,
    compare_methods_cv
)

# Set style
sns.set_style("whitegrid")
np.random.seed(42)


def example_1_basic_loocv():
    """Example 1: Basic Leave-One-Out Cross-Validation."""
    print("=" * 80)
    print("EXAMPLE 1: Leave-One-Out Cross-Validation")
    print("=" * 80)

    # Simulate data: 25 studies, 2 outcomes
    y, S = simulate_multivariate_ma(
        n_studies=25,
        n_outcomes=2,
        true_effects=np.array([0.5, 0.3]),
        between_study_sd=0.4,
        correlation=0.5,
        seed=42
    )

    print(f"\nData: {y.shape[0]} studies, {y.shape[1]} outcomes")
    print(f"True effects: [0.5, 0.3]")

    # Perform LOOCV
    print("\nPerforming leave-one-out cross-validation...")
    cv_results = cross_validate(y, S, cv_type='loo', verbose=True)

    # Print summary
    print_cv_summary(cv_results)

    # Analyze results
    print("\nInterpretation:")
    print("-" * 80)

    for j, mspe in enumerate(cv_results['mspe']):
        print(f"\nOutcome {j}:")
        print(f"  • MSPE = {mspe:.4f}")
        print(f"    → Average squared prediction error")
        print(f"    → RMSE = {np.sqrt(mspe):.4f}")

        coverage = cv_results['coverage'][j]
        print(f"  • Coverage = {coverage:.3f}")
        if coverage < 0.90:
            print(f"    → Warning: Lower than nominal 95%")
            print(f"    → Prediction intervals may be too narrow")
        elif coverage > 0.98:
            print(f"    → Coverage is higher than nominal 95%")
            print(f"    → Prediction intervals may be conservative")
        else:
            print(f"    → Good: Close to nominal 95%")

    return cv_results


def example_2_kfold_cv():
    """Example 2: K-Fold Cross-Validation."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: K-Fold Cross-Validation")
    print("=" * 80)

    # Simulate larger dataset
    y, S = simulate_multivariate_ma(
        n_studies=50,
        n_outcomes=3,
        true_effects=np.array([0.3, 0.5, 0.2]),
        between_study_sd=0.5,
        correlation=0.6,
        seed=123
    )

    print(f"\nData: {y.shape[0]} studies, {y.shape[1]} outcomes")

    # Compare different k values
    print("\nComparing different fold numbers:")
    print("-" * 80)

    results_by_k = []

    for k in [5, 10]:
        print(f"\n{k}-fold cross-validation...")
        cv_results = cross_validate(
            y, S,
            cv_type='kfold',
            k=k,
            seed=42,
            verbose=True
        )

        for j in range(y.shape[1]):
            results_by_k.append({
                'k': k,
                'outcome': j,
                'mspe': cv_results['mspe'][j],
                'coverage': cv_results['coverage'][j]
            })

    # Summary table
    results_df = pd.DataFrame(results_by_k)
    print("\n\nSummary of Results:")
    print(results_df.pivot(index='outcome', columns='k', values='mspe'))

    print("\n\nKey Points:")
    print("• 5-fold is faster but has more variance")
    print("• 10-fold is slower but more stable")
    print("• For meta-analysis (small n), LOOCV is often preferred")


def example_3_compare_methods():
    """Example 3: Comparing REML vs ML using Cross-Validation."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Comparing Estimation Methods")
    print("=" * 80)

    # Simulate data
    y, S = simulate_multivariate_ma(
        n_studies=30,
        n_outcomes=2,
        true_effects=np.array([0.4, 0.6]),
        between_study_sd=0.3,
        correlation=0.4,
        seed=456
    )

    print(f"\nData: {y.shape[0]} studies, {y.shape[1]} outcomes")
    print("\nComparing REML vs ML estimation...")

    # Compare methods
    comparison = compare_methods_cv(
        y, S,
        methods=['reml', 'ml'],
        cv_type='loo',
        verbose=True
    )

    print("\n\nComparison Results:")
    print("-" * 80)
    print(comparison.to_string(index=False))

    # Analyze differences
    print("\n\nAnalysis:")
    print("-" * 80)

    for outcome in range(y.shape[1]):
        outcome_data = comparison[comparison['outcome'] == outcome]

        reml_mspe = outcome_data[outcome_data['method'] == 'REML']['mspe'].values[0]
        ml_mspe = outcome_data[outcome_data['method'] == 'ML']['mspe'].values[0]

        print(f"\nOutcome {outcome}:")
        print(f"  • REML MSPE: {reml_mspe:.4f}")
        print(f"  • ML MSPE:   {ml_mspe:.4f}")

        if reml_mspe < ml_mspe:
            improvement = (ml_mspe - reml_mspe) / ml_mspe * 100
            print(f"  → REML is better by {improvement:.1f}%")
        else:
            improvement = (reml_mspe - ml_mspe) / reml_mspe * 100
            print(f"  → ML is better by {improvement:.1f}%")

    print("\n\nConclusion:")
    print("• REML typically performs better for small sample sizes")
    print("• ML and REML converge as sample size increases")
    print("• Use CV to objectively compare methods for your data")

    return comparison


def example_4_prediction_accuracy():
    """Example 4: Assessing Prediction Accuracy."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: Prediction Accuracy Assessment")
    print("=" * 80)

    # Simulate data with varying heterogeneity
    print("\nComparing low vs high heterogeneity scenarios...")

    scenarios = [
        {'tau': 0.1, 'label': 'Low heterogeneity'},
        {'tau': 0.8, 'label': 'High heterogeneity'}
    ]

    results = []

    for scenario in scenarios:
        print(f"\n{scenario['label']} (τ = {scenario['tau']}):")
        print("-" * 40)

        y, S = simulate_multivariate_ma(
            n_studies=25,
            n_outcomes=2,
            true_effects=np.array([0.5, 0.3]),
            between_study_sd=scenario['tau'],
            correlation=0.5,
            seed=789
        )

        cv_results = cross_validate(y, S, cv_type='loo', verbose=False)

        for j in range(2):
            results.append({
                'scenario': scenario['label'],
                'tau': scenario['tau'],
                'outcome': j,
                'mspe': cv_results['mspe'][j],
                'rmse': np.sqrt(cv_results['mspe'][j]),
                'coverage': cv_results['coverage'][j]
            })

            print(f"  Outcome {j}: RMSE = {np.sqrt(cv_results['mspe'][j]):.4f}, "
                  f"Coverage = {cv_results['coverage'][j]:.3f}")

    results_df = pd.DataFrame(results)

    print("\n\nKey Insights:")
    print("-" * 80)
    print("• Higher heterogeneity → larger prediction errors")
    print("• Prediction intervals should maintain coverage")
    print("• CV helps detect when model assumptions are violated")

    return results_df


def example_5_calibration():
    """Example 5: Calibration Plot."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 5: Calibration Plot")
    print("=" * 80)

    # Simulate data
    y, S = simulate_multivariate_ma(
        n_studies=30,
        n_outcomes=2,
        true_effects=np.array([0.5, 0.3]),
        between_study_sd=0.4,
        seed=999
    )

    print(f"\nData: {y.shape[0]} studies, {y.shape[1]} outcomes")

    # Perform CV
    print("\nPerforming cross-validation...")
    cv_results = cross_validate(y, S, cv_type='loo', verbose=False)

    # Create calibration plot
    print("\nCreating calibration plot...")

    import os
    os.makedirs('examples/figures', exist_ok=True)

    calibration_plot(
        cv_results,
        outcome_idx=0,
        save_path='examples/figures/cv_calibration.png'
    )

    print("\nCalibration plot interpretation:")
    print("-" * 80)
    print("• Left panel: Predicted SE vs actual errors")
    print("  - Points on diagonal = perfect calibration")
    print("  - Points above diagonal = underestimated uncertainty")
    print("  - Points below diagonal = overestimated uncertainty")
    print("• Right panel: Distribution of standardized errors")
    print("  - Should follow N(0,1) if model is well-calibrated")
    print("  - Heavy tails suggest model misspecification")


def main():
    """Run all examples."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  CROSS-VALIDATION FOR MULTIVARIATE META-ANALYSIS".center(78) + "█")
    print("█" + "  Comprehensive Demonstration".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    # Run examples
    example_1_basic_loocv()
    example_2_kfold_cv()
    example_3_compare_methods()
    example_4_prediction_accuracy()
    example_5_calibration()

    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nCross-validation is essential for:")
    print("  1. Assessing prediction accuracy")
    print("  2. Comparing estimation methods objectively")
    print("  3. Detecting model misspecification")
    print("  4. Validating prediction intervals")
    print("\nFor meta-analysis with small sample sizes:")
    print("  • Use leave-one-out CV (most stable)")
    print("  • Focus on prediction interval coverage")
    print("  • Compare REML vs ML using CV")
    print("  • Check calibration plots for model fit")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
