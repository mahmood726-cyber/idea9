"""
Example 3: Multivariate Network Meta-Analysis

This example demonstrates network meta-analysis with multiple outcomes.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mvmeta import MultivariateNetworkMetaAnalysis
from mvmeta.utils import simulate_network_ma
from mvmeta.visualization import plot_network, plot_treatment_effects

# Set random seed
np.random.seed(456)

print("=" * 70)
print("Example 3: Multivariate Network Meta-Analysis")
print("=" * 70)

# Simulate network data
print("\n1. Simulating network meta-analysis data...")
n_treatments = 4
n_outcomes = 2
n_studies = 20

# True treatment effects (relative to T0)
true_effects = np.array([
    [0.5, 0.3],   # T1 vs T0
    [0.7, 0.5],   # T2 vs T0
    [0.4, 0.6],   # T3 vs T0
])

data = simulate_network_ma(
    n_treatments=n_treatments,
    n_outcomes=n_outcomes,
    n_studies=n_studies,
    true_effects=true_effects,
    between_study_sd=0.3,
    correlation=0.5,
    seed=456
)

print(f"  Generated {n_studies} studies comparing {n_treatments} treatments")
print(f"  Each study measures {n_outcomes} outcomes")
print("\n  First 5 studies:")
print(data.head())

# Visualize network structure
print("\n2. Visualizing network structure...")
fig1 = plot_network(
    data,
    node_size_by_studies=True,
    edge_width_by_studies=True,
    title='Treatment Comparison Network'
)
plt.savefig('examples/figures/03_network_structure.png', dpi=300, bbox_inches='tight')
print("  Saved network plot")

# Fit multivariate network meta-analysis
print("\n3. Fitting multivariate network meta-analysis (REML)...")
model = MultivariateNetworkMetaAnalysis(consistency_model=True, verbose=True)

outcome_names = ['Efficacy', 'Safety']
results = model.fit(
    data,
    outcomes=['outcome_1', 'outcome_2'],
    method='reml'
)

print("\n" + "=" * 70)
print("Treatment Effects (vs Reference T0):")
print("=" * 70)

treatment_names = results.additional_info['treatment_names']
theta_matrix = results.additional_info['theta_matrix']
theta_se_matrix = results.additional_info['theta_se_matrix']

for i, treatment in enumerate(treatment_names[1:]):  # Skip reference
    print(f"\n{treatment}:")
    for j, outcome in enumerate(outcome_names):
        est = theta_matrix[i, j]
        se = theta_se_matrix[i, j]
        ci_low = est - 1.96 * se
        ci_high = est + 1.96 * se
        print(f"  {outcome}: {est:.4f} (95% CI: {ci_low:.4f}, {ci_high:.4f})")

# Between-study correlation
print("\n" + "=" * 70)
print("Between-Study Correlation Matrix:")
print("=" * 70)
corr_matrix = results.between_study_correlation
for i, row in enumerate(corr_matrix):
    print(f"{outcome_names[i]}: " + "  ".join([f"{x:6.3f}" for x in row]))

# Get treatment effects table
print("\n4. Treatment effects table...")
effects_table = model.get_treatment_effects_table()
print(effects_table)

# Visualize treatment effects
print("\n5. Creating treatment effects plots...")
fig2 = plot_treatment_effects(
    results,
    outcome_names=outcome_names,
    title='Treatment Effects for Multiple Outcomes'
)
plt.savefig('examples/figures/03_treatment_effects.png', dpi=300, bbox_inches='tight')
print("  Saved treatment effects plot")

# Compare with true values
print("\n6. Comparison with true values:")
print("=" * 70)
print(f"{'Treatment':<10} {'Outcome':<10} {'Estimated':<12} {'True':<12} {'Difference':<12}")
print("-" * 70)
for i, treatment in enumerate(treatment_names[1:]):
    for j, outcome in enumerate(outcome_names):
        est = theta_matrix[i, j]
        true = true_effects[i, j]
        diff = est - true
        print(f"{treatment:<10} {outcome:<10} {est:>11.4f} {true:>11.4f} {diff:>11.4f}")

print("\n" + "=" * 70)
print("Example completed successfully!")
print("=" * 70)

plt.close('all')
