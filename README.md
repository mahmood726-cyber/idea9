# MVMeta: Multivariate Meta-Analysis in Python

A comprehensive Python package for multivariate and multi-endpoint meta-analysis with advanced features for handling correlated outcomes, missing data, and network meta-analysis.

## Features

### Core Functionality
- **Multivariate Random-Effects Meta-Analysis**: Handle multiple correlated outcomes jointly
- **Missing Outcome Imputation**: Multiple imputation and pattern mixture models
- **Borrowing Strength**: Leverage correlations across outcomes for more efficient estimation
- **Multivariate Network Meta-Analysis**: Extension to network meta-analysis with multiple endpoints

### Estimation Methods
- **Frequentist**: REML and ML estimation with efficient algorithms
- **Bayesian**: Full Bayesian inference using PyMC for complex models
- **Flexible Variance Structures**: Unstructured, compound symmetry, AR(1), and custom structures

### Advanced Features
- Missing data handling (MAR, MNAR)
- Multivariate meta-regression
- Publication bias assessment for multiple outcomes
- Comprehensive diagnostics (heterogeneity, inconsistency, influence)
- Rich visualization (forest plots, network diagrams, correlation plots)

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```python
import numpy as np
from mvmeta import MultivariateMetaAnalysis

# Example: Two correlated outcomes from 10 studies
y = np.random.randn(10, 2)  # Effect sizes
S = np.random.uniform(0.5, 2, (10, 2, 2))  # Within-study covariances

# Fit multivariate meta-analysis
model = MultivariateMetaAnalysis()
results = model.fit(y, S, method='reml')

print(results.summary())
print(f"Between-study correlation: {results.between_study_correlation}")
```

## Methodology

This package implements methods from:

- **Jackson et al. (2011)**: Multivariate meta-analysis: Potential and promise. *Statistics in Medicine*
- **White et al. (2012)**: Consistency and inconsistency in network meta-analysis. *Statistics in Medicine*
- **Efthimiou et al. (2019)**: Combining multiple outcomes in network meta-analysis. *Biostatistics*
- **Riley et al. (2017)**: Multivariate meta-analysis using individual participant data. *Research Synthesis Methods*

## Novel Contributions

This package extends existing methods with:

1. **Efficient Bayesian estimation** for complex multivariate structures
2. **Flexible missing data mechanisms** beyond MAR
3. **Joint modeling of network and multivariate structures**
4. **Scalable algorithms** for high-dimensional outcomes
5. **Comprehensive diagnostic suite** for multivariate meta-analysis

## Examples

See the `examples/` directory for:
- Basic multivariate meta-analysis
- Handling missing outcomes
- Multivariate network meta-analysis
- Meta-regression with multiple outcomes
- Publication bias assessment

## Citation

If you use this package, please cite:

```
[Your paper citation here]
```

## License

MIT License

## Contact

[Your contact information]
