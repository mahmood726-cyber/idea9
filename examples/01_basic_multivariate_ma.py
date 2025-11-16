"""
Example 1: Basic Multivariate Meta-Analysis

This example demonstrates basic multivariate meta-analysis with correlated outcomes.
"""

import numpy as np
import matplotlib.pyplot as plt
from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.visualization import plot_multivariate_forest, plot_outcome_correlations

# Set random seed for reproducibility
np.random.seed(42)

print("=" * 70)
print("Example 1: Basic Multivariate Meta-Analysis")
print("=" * 70)

# Simulate data: 20 studies, 3 outcomes
print("\n1. Simulating data...")
n_studies = 20
n_outcomes = 3
true_effects = np.array([0.5, 0.3, 0.7])

y, S = simulate_multivariate_ma(
    n_studies=n_studies,
    n_outcomes=n_outcomes,
    true_effects=true_effects,
    between_study_sd=0.4,
    within_study_sd=0.25,
    correlation=0.6,
    seed=42
)

print(f"  Generated {n_studies} studies with {n_outcomes} outcomes")
print(f"  True effects: {true_effects}")

# Fit multivariate meta-analysis using REML
print("\n2. Fitting multivariate meta-analysis (REML)...")
model_reml = MultivariateMetaAnalysis(variance_structure='unstructured', verbose=True)
results_reml = model_reml.fit(y, S, method='reml')

print("\n" + "=" * 70)
print(results_reml.summary())

# Compare with ML estimation
print("\n3. Comparing with ML estimation...")
model_ml = MultivariateMetaAnalysis(verbose=False)
results_ml = model_ml.fit(y, S, method='ml')

print("\nComparison:")
print(f"{'Method':<10} {'Outcome 1':<15} {'Outcome 2':<15} {'Outcome 3':<15}")
print("-" * 70)
print(f"{'REML':<10} {results_reml.theta[0]:<15.4f} {results_reml.theta[1]:<15.4f} {results_reml.theta[2]:<15.4f}")
print(f"{'ML':<10} {results_ml.theta[0]:<15.4f} {results_ml.theta[1]:<15.4f} {results_ml.theta[2]:<15.4f}")
print(f"{'True':<10} {true_effects[0]:<15.4f} {true_effects[1]:<15.4f} {true_effects[2]:<15.4f}")

# Visualizations
print("\n4. Creating visualizations...")

# Forest plot
outcome_names = ['Pain Score', 'Function', 'Quality of Life']
fig1 = plot_multivariate_forest(
    results_reml,
    outcome_names=outcome_names,
    title='Multivariate Meta-Analysis Results'
)
plt.savefig('examples/figures/01_forest_plot.png', dpi=300, bbox_inches='tight')
print("  Saved forest plot")

# Correlation plot
fig2 = plot_outcome_correlations(
    results_reml,
    outcome_names=outcome_names,
    title='Between-Study Correlations'
)
plt.savefig('examples/figures/01_correlations.png', dpi=300, bbox_inches='tight')
print("  Saved correlation plot")

# Analysis with different variance structures
print("\n5. Comparing variance structures...")
variance_structures = ['unstructured', 'diagonal', 'compound_symmetry']

for vs in variance_structures:
    model = MultivariateMetaAnalysis(variance_structure=vs, verbose=False)
    results = model.fit(y, S, method='reml')
    print(f"\n  {vs}:")
    print(f"    Log-likelihood: {results.loglik:.4f}")
    print(f"    Theta: {results.theta}")

print("\n" + "=" * 70)
print("Example completed successfully!")
print("=" * 70)

# Close plots
plt.close('all')
