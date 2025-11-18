# Multivariate Meta-Analysis: Methods for Synthesizing Correlated Outcomes

## Abstract

Meta-analysis traditionally analyzes outcomes separately, ignoring correlations between endpoints. Multivariate meta-analysis (MVMA) jointly models correlated outcomes, improving precision and enabling comprehensive evidence synthesis. This synthesis presents methods for MVMA including restricted maximum likelihood (REML), Bayesian estimation, and multiple imputation for missing data. We describe the two-stage hierarchical model, sample size requirements, and critical assumptions. While MVMA offers advantages through borrowing strength across correlated outcomes and principled missing data handling, success depends on adequate sample size and within-study correlation information.

## Introduction

Systematic reviews increasingly evaluate multiple correlated outcomes—efficacy and safety, quality-of-life domains, or endpoints across timepoints. Traditional meta-analysis analyzes each separately, discarding correlation information and potentially reaching inconsistent conclusions. For instance, antidepressant trials report efficacy and safety outcomes that are often correlated within studies. Separate analyses ignore this correlation, potentially overestimating heterogeneity and reducing statistical power.

MVMA explicitly models correlations, offering methodological advantages. First, MVMA "borrows strength": when outcomes are correlated across studies, information from precisely-measured outcomes improves estimates for imprecisely-measured ones through shrinkage toward the multivariate mean. Second, studies reporting only some outcomes still contribute information about all effects through the correlation structure. Third, MVMA preserves multivariate evidence, enabling coherent inference across domains simultaneously.

## Statistical Framework

### Two-Stage Hierarchical Model

MVMA uses a two-stage hierarchical framework. At stage 1, study $i$ estimates a $p$-dimensional effect vector:

$$\mathbf{y}_i | \boldsymbol{\mu}_i \sim N(\boldsymbol{\mu}_i, \mathbf{S}_i)$$

where $\mathbf{S}_i$ is the within-study covariance matrix, typically assumed known from reported standard errors and correlations. When unavailable, sensitivity analysis across plausible values (e.g., 0, 0.3, 0.6) is essential.

At stage 2, true study-specific effects vary around a pooled mean:

$$\boldsymbol{\mu}_i \sim N(\boldsymbol{\theta}, \boldsymbol{\Psi})$$

where $\boldsymbol{\theta}$ represents pooled effects and $\boldsymbol{\Psi}$ is the between-study covariance matrix capturing heterogeneity. The marginal distribution is:

$$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$$

The between-study correlation $\rho$ in $\boldsymbol{\Psi}$ quantifies how treatment effects vary together across studies.

### Estimation and Inference

**Restricted Maximum Likelihood (REML)** is recommended for estimating $\boldsymbol{\Psi}$, providing less biased variance estimates than maximum likelihood (ML), particularly for small meta-analyses ($k < 10$ studies), though both methods can be unstable when $k < 5$ (Thompson and Sharp, 1999).

Inference requires careful consideration of degrees of freedom. For small $k$, the Hartung-Knapp-Sidik-Jonkman adjustment provides better coverage than Wald-type intervals (IntHout et al., 2016). Degrees of freedom can be approximated using residual df ($k - p$) or Satterthwaite approximations.

**Bayesian estimation** using Markov Chain Monte Carlo provides full posterior distributions, enabling probability statements about effects and rankings. Weakly informative priors—LKJ priors for correlations and half-normal priors for standard deviations—ensure numerical stability while allowing data to dominate.

### Variance Structures and Sample Size

MVMA supports multiple structures for $\boldsymbol{\Psi}$. Unstructured covariance estimates all $p(p+1)/2$ elements but requires sufficient studies. As a rule of thumb, $k$ should exceed $2p$; when $k < 2p$, consider simpler structures like diagonal (independent outcomes) or compound symmetry (common correlation).

## Missing Data Methods

Missing outcomes pervade meta-analysis as many studies report only subsets of endpoints. MVMA enables principled handling through the correlation structure.

**Multiple imputation** generates complete datasets by drawing missing values from their posterior predictive distribution given observed data and estimated correlations. Analyzing $M$ imputed datasets (typically $M = 20-50$) and combining via Rubin's rules provides valid inference under missing-at-random (MAR) assumptions. However, imputation primarily provides valid standard errors under MAR; it cannot recover lost information.

**Pattern mixture models** analyze missing data patterns separately, allowing effects to differ between patterns—a missing-not-at-random (MNAR) mechanism. This provides sensitivity analysis beyond MAR, though results are typically presented as sensitivity analyses rather than primary findings.

## Network Meta-Analysis Extension

Network meta-analysis (NMA) compares multiple treatments through direct and indirect evidence. Multivariate NMA (MVNMA) analyzes comparative effectiveness across multiple endpoints simultaneously.

For study $i$ comparing treatments $j$ and $k$:

$$\mathbf{y}_{i(jk)} \sim N(\boldsymbol{\mu}_{i0} + \mathbf{d}_{jk}, \mathbf{S}_{i(jk)} + \boldsymbol{\Psi})$$

where $\mathbf{d}_{jk}$ is the vector of relative treatment effects, $\boldsymbol{\mu}_{i0}$ is the study-specific baseline, and $i(jk)$ indicates study $i$ comparing treatments $j$ and $k$.

The consistency assumption—$\mathbf{d}_{jk} = \mathbf{d}_{jl} + \mathbf{d}_{lk}$—enables indirect comparisons. Testing via node-splitting or loop-inconsistency checks is essential.

MVNMA is valuable for benefit-risk assessment, providing joint treatment rankings balancing multiple outcomes rather than optimizing single endpoints.

## Advantages and Applications

MVMA offers advantages over univariate analyses when outcomes are moderately to strongly correlated. Efficiency gains depend on correlation strength, number of studies, missing data patterns, and heterogeneity (Jackson et al., 2011; Riley et al., 2007).

Applications include: (1) diagnostic test accuracy meta-analysis jointly modeling sensitivity and specificity; (2) survival meta-analysis analyzing progression-free and overall survival; (3) multi-domain quality-of-life synthesis; (4) dose-response meta-analysis across outcomes.

## Key Assumptions and Limitations

MVMA relies on critical assumptions:

1. **Multivariate normality** of effect estimates
2. **Within-study covariances** $\mathbf{S}_i$ known or reliably estimated
3. **Study exchangeability** (random sample from population)
4. **Correct specification** of $\boldsymbol{\Psi}$ structure
5. **MAR assumption** for missing data (or explicit MNAR modeling)

**MVMA can be unreliable when:**
- $k < 2p$ (insufficient studies relative to outcomes)
- Within-study correlations are unknown and misspecified
- Between-study correlation near boundaries ($|\rho| \approx 1$)
- Heterogeneity is extreme ($I^2 > 90\%$) with limited studies
- Outcomes are independent ($\rho \approx 0$), offering no efficiency gain

**Critical limitation:** Within-study correlations are rarely reported. While these can be imputed or assumed, sensitivity analyses across plausible values are essential. Results robust to this assumption are more credible.

For $k < 5$, simpler variance structures (diagonal, common correlation) are preferable. Consider fixed-effect models or univariate analyses when sample size is insufficient.

## Computational Considerations

Estimating $\boldsymbol{\Psi}$ requires optimization ensuring positive-definiteness. Cholesky parameterization transforms to unconstrained optimization while guaranteeing valid covariance matrices. Modern algorithms (L-BFGS-B) with analytical gradients typically converge within seconds to minutes for moderate networks (up to 50 studies, 5 outcomes).

Bayesian estimation using Hamiltonian Monte Carlo efficiently samples high-dimensional posteriors through reparameterization and non-centered parameterizations.

## Conclusion

Multivariate meta-analysis provides rigorous methods for synthesizing correlated outcomes when assumptions are met and sample size is adequate. Through borrowing strength and principled missing data handling, MVMA can deliver more efficient evidence synthesis than univariate analyses. However, success critically depends on adequate $k$ relative to $p$, within-study correlation information, and careful assumption assessment. As clinical trials increasingly evaluate multiple endpoints, MVMA offers essential methodology when applied appropriately with thorough sensitivity analyses.

## References

1. Jackson D, Riley R, White IR. Multivariate meta-analysis: potential and promise. *Stat Med*. 2011;30(20):2481-2498.

2. Riley RD, Abrams KR, Sutton AJ, Lambert PC, Thompson JR. Bivariate random-effects meta-analysis and the estimation of between-study correlation. *BMC Med Res Methodol*. 2007;7:3.

3. Thompson SG, Sharp SJ. Explaining heterogeneity in meta-analysis: a comparison of methods. *Stat Med*. 1999;18(20):2693-2708.

4. Efthimiou O, Mavridis D, Riley RD, Cipriani A, Salanti G. Joint synthesis of multiple correlated outcomes in networks of interventions. *Biostatistics*. 2019;20(1):84-98.

5. White IR, Barrett JK, Jackson D, Higgins JPT. Consistency and inconsistency in network meta-analysis: model estimation using multivariate meta-regression. *Res Synth Methods*. 2012;3(2):111-125.

6. Mavridis D, Salanti G. A practical introduction to multivariate meta-analysis. *Stat Methods Med Res*. 2013;22(2):133-158.

7. IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ. Plea for routinely presenting prediction intervals in meta-analysis. *BMJ Open*. 2016;6(7):e010247.

8. Van Houwelingen HC, Arends LR, Stijnen T. Advanced methods in meta-analysis: multivariate approach and meta-regression. *Stat Med*. 2002;21(4):589-624.
