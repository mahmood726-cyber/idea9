"""
Example 2: Handling Missing Outcome Data

This example demonstrates multiple imputation and pattern mixture models
for handling missing outcome data.
"""

import numpy as np
import matplotlib.pyplot as plt
from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.imputation import MultipleImputation, PatternMixtureModel

# Set random seed
np.random.seed(123)

print("=" * 70)
print("Example 2: Handling Missing Outcome Data")
print("=" * 70)

# Simulate data with missing outcomes
print("\n1. Simulating data with 30% missing outcomes...")
n_studies = 25
n_outcomes = 2

y, S = simulate_multivariate_ma(
    n_studies=n_studies,
    n_outcomes=n_outcomes,
    true_effects=np.array([0.4, 0.6]),
    between_study_sd=0.35,
    correlation=0.5,
    missing_rate=0.30,
    seed=123
)

n_missing = np.sum(np.isnan(y))
print(f"  Total missing values: {n_missing} out of {n_studies * n_outcomes}")
print(f"  Missing rate: {n_missing / (n_studies * n_outcomes) * 100:.1f}%")

# Complete case analysis (for comparison)
print("\n2. Complete case analysis...")
complete_mask = ~np.any(np.isnan(y), axis=1)
y_complete = y[complete_mask]
S_complete = S[complete_mask]

print(f"  Using {np.sum(complete_mask)} complete studies out of {n_studies}")

model_cc = MultivariateMetaAnalysis(verbose=False)
results_cc = model_cc.fit(y_complete, S_complete, method='reml')

print(f"  Complete case estimates: {results_cc.theta}")
print(f"  Standard errors: {results_cc.theta_se}")

# Multiple imputation
print("\n3. Multiple imputation (20 imputations)...")
mi = MultipleImputation(n_imputations=20, method='normal', verbose=True)
results_mi = mi.fit_transform(y, S, method='reml')

print(f"  MI estimates: {results_mi.theta}")
print(f"  Standard errors: {results_mi.theta_se}")

# Predictive mean matching
print("\n4. Multiple imputation with predictive mean matching...")
mi_pmm = MultipleImputation(n_imputations=20, method='pmm', verbose=False)
results_pmm = mi_pmm.fit_transform(y, S, method='reml')

print(f"  PMM estimates: {results_pmm.theta}")
print(f"  Standard errors: {results_pmm.theta_se}")

# Pattern mixture model
print("\n5. Pattern mixture model...")
pmm = PatternMixtureModel(min_pattern_size=2, verbose=True)
results_pmm_model = pmm.fit(y, S, method='reml')

# Get pattern summary
pattern_summary = pmm.get_pattern_summary()
print("\n  Missing data patterns:")
print(pattern_summary)

print(f"\n  Pattern mixture estimates: {results_pmm_model.theta}")
print(f"  Standard errors: {results_pmm_model.theta_se}")

# Comparison table
print("\n6. Comparison of methods:")
print("=" * 70)
print(f"{'Method':<25} {'Outcome 1':<20} {'Outcome 2':<20}")
print("-" * 70)
print(f"{'Complete case':<25} {results_cc.theta[0]:.4f} ({results_cc.theta_se[0]:.4f})  "
      f"{results_cc.theta[1]:.4f} ({results_cc.theta_se[1]:.4f})")
print(f"{'MI (normal)':<25} {results_mi.theta[0]:.4f} ({results_mi.theta_se[0]:.4f})  "
      f"{results_mi.theta[1]:.4f} ({results_mi.theta_se[1]:.4f})")
print(f"{'MI (PMM)':<25} {results_pmm.theta[0]:.4f} ({results_pmm.theta_se[0]:.4f})  "
      f"{results_pmm.theta[1]:.4f} ({results_pmm.theta_se[1]:.4f})")
if not np.any(np.isnan(results_pmm_model.theta)):
    print(f"{'Pattern mixture':<25} {results_pmm_model.theta[0]:.4f} ({results_pmm_model.theta_se[0]:.4f})  "
          f"{results_pmm_model.theta[1]:.4f} ({results_pmm_model.theta_se[1]:.4f})")
print(f"{'True values':<25} 0.4000               0.6000")
print("=" * 70)

print("\nExample completed successfully!")
