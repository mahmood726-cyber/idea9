# Methodology: Multivariate Meta-Analysis

## Overview

This package implements advanced methods for multivariate meta-analysis, where multiple correlated outcomes are analyzed jointly. This approach has several advantages over separate univariate meta-analyses:

1. **Borrowing strength**: Information from one outcome can inform estimates of another
2. **Handling missing data**: Outcomes missing in some studies can be better handled
3. **Preserving correlation structure**: The between-study correlation is explicitly modeled
4. **Improved efficiency**: Joint analysis can provide more precise estimates

## Statistical Models

### Multivariate Random-Effects Model

The basic model for study $i$ is:

$$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$$

where:
- $\mathbf{y}_i$ is the vector of observed effect sizes (length $p$)
- $\boldsymbol{\theta}$ is the vector of pooled effects
- $\mathbf{S}_i$ is the within-study covariance matrix (known)
- $\boldsymbol{\Psi}$ is the between-study covariance matrix (to be estimated)

### Estimation Methods

#### REML (Restricted Maximum Likelihood)

REML is the default estimation method. It accounts for the uncertainty in estimating fixed effects and generally provides better estimates of variance components than ML.

The REML log-likelihood is:

$$\ell_{REML} = -\frac{1}{2}\left[\sum_i \log|\mathbf{V}_i| + \log|\mathbf{X}'\mathbf{V}^{-1}\mathbf{X}| + \mathbf{r}'\mathbf{V}^{-1}\mathbf{r}\right]$$

where $\mathbf{V}_i = \mathbf{S}_i + \boldsymbol{\Psi}$ and $\mathbf{r}$ are the residuals.

#### ML (Maximum Likelihood)

ML estimation maximizes the full likelihood. It can be preferred when the number of studies is large or for model comparison using likelihood ratio tests.

#### Bayesian Estimation

Bayesian estimation using PyMC provides:
- Full posterior distributions for all parameters
- Natural handling of uncertainty
- Flexible prior specifications
- Treatment rankings and probability statements

We use LKJ priors for the correlation matrix and half-normal priors for the standard deviations.

### Variance Structures

The package supports several structures for $\boldsymbol{\Psi}$:

1. **Unstructured**: Full covariance matrix (default)
   - Most flexible
   - Requires estimation of $p(p+1)/2$ parameters

2. **Diagonal**: Independent outcomes
   - Assumes zero between-study correlation
   - Requires $p$ parameters

3. **Compound Symmetry**: Common correlation
   - Assumes equal variances and correlations
   - Requires 2 parameters

## Missing Data Methods

### Multiple Imputation

Multiple imputation creates $M$ complete datasets by imputing missing values from their posterior predictive distribution. Results are combined using Rubin's rules:

$$\bar{\theta} = \frac{1}{M}\sum_{m=1}^M \hat{\theta}^{(m)}$$

$$\text{Var}(\bar{\theta}) = W + \left(1 + \frac{1}{M}\right)B$$

where $W$ is the within-imputation variance and $B$ is the between-imputation variance.

We implement three imputation methods:

1. **Normal**: Assumes multivariate normality
2. **Predictive Mean Matching (PMM)**: More robust, preserves distribution
3. **Bootstrap**: Bootstrap-based imputation

### Pattern Mixture Models

Pattern mixture models analyze each missing data pattern separately and then combine results. This allows for:
- Different effects in different patterns (MNAR)
- Sensitivity analysis
- More realistic missing data assumptions

## Multivariate Network Meta-Analysis

For network meta-analysis with multiple outcomes, we extend the consistency model:

$$\mathbf{y}_{ijk} \sim N(\mathbf{d}_{jk}, \mathbf{S}_{ijk} + \boldsymbol{\Psi})$$

where $\mathbf{d}_{jk}$ is the vector of relative treatment effects comparing treatments $j$ and $k$ across all outcomes.

The consistency assumption implies:
$$\mathbf{d}_{jk} = \mathbf{d}_{jl} + \mathbf{d}_{lk}$$

This allows indirect comparisons and increases precision.

## Novel Contributions

This package extends existing methods with:

### 1. Efficient Bayesian Estimation
- HMC sampling for complex multivariate structures
- Reparameterization for improved sampling
- Diagnostic tools for convergence assessment

### 2. Flexible Missing Data Mechanisms
- Pattern mixture models for MNAR
- Sensitivity analysis tools
- Multiple imputation methods

### 3. Joint Network-Multivariate Modeling
- First implementation combining network MA and multivariate MA
- Handles complex treatment networks with multiple outcomes
- Treatment rankings across multiple endpoints

### 4. Scalable Algorithms
- Efficient matrix operations
- Sparse matrix support for large networks
- Parallel computation options

### 5. Comprehensive Diagnostics
- Multivariate heterogeneity measures
- Influence analysis
- Inconsistency detection
- Network connectivity assessment

## References

1. **Jackson, D., Riley, R., & White, I. R. (2011).** Multivariate meta‐analysis: potential and promise. *Statistics in Medicine*, 30(20), 2481-2498.

2. **White, I. R. (2011).** Multivariate random-effects meta-regression: updates to mvmeta. *The Stata Journal*, 11(2), 255-270.

3. **Efthimiou, O., Mavridis, D., Riley, R. D., Cipriani, A., & Salanti, G. (2019).** Joint synthesis of multiple correlated outcomes in networks of interventions. *Biostatistics*, 20(1), 84-98.

4. **Riley, R. D., Abrams, K. R., Sutton, A. J., Lambert, P. C., & Thompson, J. R. (2007).** Bivariate random-effects meta-analysis and the estimation of between-study correlation. *BMC Medical Research Methodology*, 7(1), 1-15.

5. **Mavridis, D., & Salanti, G. (2013).** A practical introduction to multivariate meta‐analysis. *Statistical Methods in Medical Research*, 22(2), 133-158.

6. **Kirkham, J. J., Riley, R. D., & Williamson, P. R. (2012).** A multivariate meta‐analysis approach for reducing the impact of outcome reporting bias in systematic reviews. *Statistics in Medicine*, 31(20), 2179-2195.

## Implementation Details

### Optimization

For REML/ML estimation, we use L-BFGS-B optimization with:
- Cholesky parameterization for positive-definiteness
- Numerical derivatives when needed
- Multiple starting values for robustness

### Numerical Stability

We ensure numerical stability through:
- Eigenvalue adjustments for near-singular matrices
- Regularization when needed
- Careful handling of edge cases

### Computational Efficiency

The package is optimized for:
- Vectorized operations using NumPy
- Efficient matrix decompositions
- Minimal redundant computations
- Optional JAX acceleration

## Software Design

The package follows modern Python best practices:
- Object-oriented design with clear interfaces
- Type hints for better IDE support
- Comprehensive documentation
- Extensive test coverage
- Modular architecture for extensibility

## Future Extensions

Planned extensions include:
1. Meta-regression for multivariate outcomes
2. Publication bias methods (multivariate Egger's test)
3. Individual participant data (IPD) meta-analysis
4. Multivariate meta-analysis of survival outcomes
5. Spatial correlation models
6. Time-series meta-analysis
