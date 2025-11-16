# MVMeta Quick Start Guide

Welcome to **MVMeta**, a Python package for multivariate meta-analysis with correlated outcomes!

This guide will get you started in **5 minutes**.

## Installation

```bash
pip install mvmeta
```

Or install from source:

```bash
git clone https://github.com/yourusername/mvmeta.git
cd mvmeta
pip install -e .
```

## Dependencies

```bash
pip install numpy scipy pandas matplotlib seaborn statsmodels
```

---

## Basic Usage (30 seconds)

```python
import numpy as np
from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma

# 1. Generate example data (or use your own)
y, S = simulate_multivariate_ma(
    n_studies=20,
    n_outcomes=2,
    true_effects=np.array([0.5, 0.3]),
    seed=42
)

# 2. Fit the model
model = MultivariateMetaAnalysis()
results = model.fit(y, S, method='reml')

# 3. View results
print(f"Pooled effects: {results.theta}")
print(f"95% CI: {results.ci_lower} to {results.ci_upper}")
print(f"Heterogeneity (τ²): {np.diag(results.Psi)}")
```

**Output:**
```
Pooled effects: [0.489 0.305]
95% CI: [0.321 0.178] to [0.657 0.432]
Heterogeneity (τ²): [0.045 0.038]
```

That's it! You've run your first multivariate meta-analysis.

---

## Your Own Data (2 minutes)

### Step 1: Prepare your data

Your data should be:
- **y**: Effect sizes, shape `(n_studies, n_outcomes)`
- **S**: Within-study covariance matrices, shape `(n_studies, n_outcomes, n_outcomes)`

**Example with 3 studies and 2 outcomes:**

```python
import numpy as np

# Effect sizes for 3 studies, 2 outcomes each
y = np.array([
    [0.5, 0.3],  # Study 1: outcome1=0.5, outcome2=0.3
    [0.7, 0.4],  # Study 2
    [0.4, 0.2]   # Study 3
])

# Within-study covariance matrices
S = np.zeros((3, 2, 2))

# Study 1
S[0] = [[0.04, 0.01],   # var(outcome1)=0.04, cov=0.01
        [0.01, 0.03]]   # cov=0.01, var(outcome2)=0.03

# Study 2
S[1] = [[0.05, 0.02],
        [0.02, 0.04]]

# Study 3
S[2] = [[0.03, 0.00],
        [0.00, 0.02]]
```

**If you only have standard errors:**

```python
se = np.array([
    [0.20, 0.17],  # Study 1 SEs
    [0.22, 0.20],  # Study 2 SEs
    [0.17, 0.14]   # Study 3 SEs
])

# Convert to covariance matrices (assuming correlation = 0.5)
S = np.zeros((3, 2, 2))
rho = 0.5

for i in range(3):
    S[i, 0, 0] = se[i, 0]**2
    S[i, 1, 1] = se[i, 1]**2
    S[i, 0, 1] = S[i, 1, 0] = rho * se[i, 0] * se[i, 1]
```

### Step 2: Fit the model

```python
from mvmeta import MultivariateMetaAnalysis

model = MultivariateMetaAnalysis()
results = model.fit(y, S, method='reml')

# Access results
print("Pooled estimates:", results.theta)
print("Standard errors:", results.theta_se)
print("95% CI lower:", results.ci_lower)
print("95% CI upper:", results.ci_upper)
print("Between-study correlation:", results.between_study_correlation)
```

---

## Essential Features (5 minutes)

### 1. Model Fitting

```python
# REML (default, recommended)
results_reml = model.fit(y, S, method='reml')

# ML (faster, but biased for small samples)
results_ml = model.fit(y, S, method='ml')

# Bayesian (full posterior inference)
results_bayes = model.fit(y, S, method='bayesian', n_samples=2000)
```

### 2. Heterogeneity Assessment

```python
from mvmeta.diagnostics import assess_heterogeneity

het = assess_heterogeneity(results, y, S)
print(het[['outcome', 'Q', 'p_value', 'I2', 'tau2']])
```

**Output:**
```
   outcome       Q  p_value     I2    tau2
0        0   24.32    0.043   42.1  0.045
1        1   18.67    0.128   28.3  0.038
```

### 3. Influence Diagnostics

```python
from mvmeta.diagnostics import comprehensive_diagnostics

diag = comprehensive_diagnostics(y, S, results)
print(diag[['study', 'cooks_d', 'is_influential', 'is_outlier']])
```

### 4. Cross-Validation

```python
from mvmeta.diagnostics import cross_validate, print_cv_summary

cv_results = cross_validate(y, S, cv_type='loo')
print_cv_summary(cv_results)
```

**Output:**
```
======================================================================
CROSS-VALIDATION SUMMARY
======================================================================
Method: REML
Number of studies: 20
Number of outcomes: 2
Cross-validation: Leave-one-out

Mean Squared Prediction Error (MSPE):
  Outcome 0: 0.2308
  Outcome 1: 0.2795

Prediction Interval Coverage:
  Outcome 0: 0.920 (gap: -0.030)
  Outcome 1: 0.960 (gap: +0.010)
```

### 5. Prediction Intervals

```python
from mvmeta.diagnostics import compute_prediction_interval

pi = compute_prediction_interval(results)
print(f"95% Prediction Interval: {pi}")
```

Prediction intervals tell you where a **new study's** effect is likely to fall.

---

## Common Scenarios

### Scenario 1: Simple Bivariate Meta-Analysis

Two correlated outcomes (e.g., blood pressure: systolic and diastolic).

```python
from mvmeta import MultivariateMetaAnalysis
import numpy as np

# Your data: 10 studies, 2 outcomes
y = np.array([...])  # shape: (10, 2)
S = np.array([...])  # shape: (10, 2, 2)

# Fit
model = MultivariateMetaAnalysis()
results = model.fit(y, S)

# Results
print(f"Systolic BP reduction: {results.theta[0]:.2f} mmHg")
print(f"Diastolic BP reduction: {results.theta[1]:.2f} mmHg")
print(f"Correlation: {results.between_study_correlation[0,1]:.2f}")
```

### Scenario 2: Multiple Outcomes (k > 2)

Three or more correlated outcomes.

```python
# 3 outcomes example
y = np.random.randn(15, 3)
S = np.array([np.eye(3) * 0.1 for _ in range(15)])

model = MultivariateMetaAnalysis()
results = model.fit(y, S)

# Full correlation matrix
print("Between-study correlations:")
print(results.between_study_correlation)
```

### Scenario 3: Missing Outcomes

Some studies don't report all outcomes.

```python
# Mark missing values as NaN
y = np.array([
    [0.5, 0.3],
    [0.7, np.nan],  # Study 2 missing outcome 2
    [np.nan, 0.2],  # Study 3 missing outcome 1
    [0.6, 0.4]
])

# Fit model (automatically handles missing data)
model = MultivariateMetaAnalysis()
results = model.fit(y, S)
```

**Note:** Currently uses complete-case analysis. For advanced missing data methods, see the documentation.

### Scenario 4: Comparing Methods

Which estimation method is best for your data?

```python
from mvmeta.diagnostics import compare_methods_cv

comparison = compare_methods_cv(
    y, S,
    methods=['reml', 'ml'],
    cv_type='loo'
)

print(comparison)
```

**Output:**
```
  method  outcome    mspe  coverage
0   REML        0  0.2308     0.920
1   REML        1  0.2795     0.960
2     ML        0  0.2415     0.900
3     ML        1  0.2891     0.940
```

REML typically wins for small samples!

---

## Visualization

### Forest Plot

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 6))

# Study effects
for i in range(len(y)):
    ci_lower = y[i, 0] - 1.96 * np.sqrt(S[i, 0, 0])
    ci_upper = y[i, 0] + 1.96 * np.sqrt(S[i, 0, 0])
    ax.plot([ci_lower, ci_upper], [i, i], 'b-', linewidth=2)
    ax.plot(y[i, 0], i, 'bs', markersize=8)

# Pooled effect
ax.plot([results.ci_lower[0], results.ci_upper[0]],
        [len(y), len(y)], 'r-', linewidth=3)
ax.plot(results.theta[0], len(y), 'rD', markersize=12)

ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Effect Size')
ax.set_ylabel('Study')
ax.set_title('Forest Plot')
plt.tight_layout()
plt.savefig('forest_plot.png', dpi=300)
```

### Calibration Plot

```python
from mvmeta.diagnostics import calibration_plot

cv_results = cross_validate(y, S, cv_type='loo')
calibration_plot(cv_results, outcome_idx=0, save_path='calibration.png')
```

---

## Real Data Example

See the full analysis of the [Berkey et al. (1998) dataset](examples/real_data_berkey.py):

```bash
python examples/real_data_berkey.py
```

This demonstrates a complete workflow:
- Data loading
- Model fitting (REML and ML)
- Heterogeneity assessment
- Influence diagnostics
- Cross-validation
- Publication-quality plots
- Clinical interpretation

---

## Tips and Best Practices

### ✅ DO:
1. **Use REML** as your primary method (better for small samples)
2. **Check heterogeneity** before interpreting results
3. **Run diagnostics** (influence, outliers, cross-validation)
4. **Report prediction intervals** (not just confidence intervals)
5. **Use cross-validation** to compare methods objectively

### ⚠️ DON'T:
1. **Don't use ML** for small samples (n < 20)
2. **Don't ignore heterogeneity** (I² > 50% needs investigation)
3. **Don't forget missing data** mechanisms (MAR vs MNAR)
4. **Don't over-interpret** with very few studies (n < 5)
5. **Don't rely on p-values alone** (focus on effect sizes and CIs)

### 📊 Sample Size Guidelines

| # Studies | Recommendation |
|-----------|----------------|
| < 5 | Use with caution, consider descriptive analysis |
| 5-15 | REML only, expect wider CIs, check influence |
| 15-30 | Both REML and ML acceptable, good coverage |
| > 30 | All methods work well, asymptotic theory applies |

### 🔍 Heterogeneity Interpretation

| I² | Interpretation | Action |
|----|----------------|--------|
| 0-25% | Low | Report pooled estimate |
| 25-50% | Moderate | Investigate sources, report PI |
| 50-75% | Substantial | Subgroup analysis, meta-regression |
| > 75% | Very high | Reconsider pooling, qualitative synthesis |

---

## Next Steps

### 📚 Learn More

1. **Examples:**
   - `examples/cross_validation_demo.py` - Comprehensive CV guide
   - `examples/real_data_berkey.py` - Real clinical trial analysis

2. **Simulation Studies:**
   - `simulations/SIMULATION_RESULTS.md` - Statistical validation
   - `simulations/01_estimation_performance_fast.py` - Run simulations

3. **API Documentation:**
   - See `docs/` for full API reference
   - All functions have detailed docstrings

### 🧪 Advanced Topics

Coming soon:
- Network meta-analysis
- Meta-regression with covariates
- Publication bias assessment
- Bayesian model averaging
- Multiple imputation for missing data

### 💡 Getting Help

- **Issues:** https://github.com/yourusername/mvmeta/issues
- **Documentation:** https://mvmeta.readthedocs.io
- **Examples:** See `examples/` directory

---

## Comparison with R's mvmeta

If you're coming from R's `mvmeta` package:

| R mvmeta | Python MVMeta | Notes |
|----------|---------------|-------|
| `mvmeta(y, S)` | `model.fit(y, S)` | Same interface |
| `method="reml"` | `method='reml'` | Default in both |
| `method="ml"` | `method='ml'` | Available |
| `predict()` | `compute_prediction_interval()` | Similar |
| `qtest.mvmeta()` | `assess_heterogeneity()` | Enhanced |

**Benchmark:** See `benchmarks/compare_with_R.md` for detailed comparisons.

---

## Citation

If you use MVMeta in your research, please cite:

```bibtex
@software{mvmeta2024,
  title={MVMeta: Multivariate Meta-Analysis in Python},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/mvmeta}
}
```

---

## License

MIT License - see LICENSE file.

---

**Version:** 0.1.0
**Last Updated:** 2025-11-16

Happy meta-analyzing! 🎉📊📈
