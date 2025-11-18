# Multivariate Meta-Analysis: Methods for Synthesizing Correlated Outcomes

## Abstract

Meta-analysis traditionally analyzes outcomes separately, ignoring correlations between multiple endpoints. Multivariate meta-analysis (MVMA) addresses this limitation by jointly modeling correlated outcomes, improving precision and enabling comprehensive evidence synthesis. This paper presents a unified framework for MVMA encompassing restricted maximum likelihood (REML), Bayesian estimation, multiple imputation for missing data, and network meta-analysis extensions. We describe the two-stage hierarchical model, estimation challenges for small samples, and practical recommendations for implementation. MVMA borrows strength across outcomes, handles partially missing data through correlation structure, and provides coherent multivariate inference, though success depends critically on adequate sample size and within-study correlation information.

## Introduction

Systematic reviews increasingly evaluate multiple correlated outcomes—efficacy and safety, multiple quality-of-life domains, or composite endpoints measured across different timepoints. Traditional meta-analysis analyzes each outcome separately, discarding information about correlations and potentially reaching inconsistent conclusions. For instance, antidepressant trials typically report both efficacy (symptom reduction) and safety (adverse events), outcomes that are often correlated within studies. Separate analyses ignore this correlation, potentially overestimating heterogeneity and reducing statistical power.

Multivariate meta-analysis explicitly models correlations between outcomes, offering several methodological advantages. First, MVMA "borrows strength" across outcomes: when outcomes are correlated across studies, information from precisely-measured outcomes improves estimates for imprecisely-measured ones through shrinkage toward the multivariate mean. Second, MVMA handles missing outcomes more effectively; studies reporting only some outcomes still contribute information about all effects through the correlation structure. Third, MVMA preserves the multivariate nature of clinical evidence, enabling coherent inference about treatment effects across multiple domains simultaneously.

Despite these advantages, MVMA adoption remains limited due to computational complexity, requirement for within-study correlations, and methodological challenges in small samples. This synthesis presents a comprehensive framework addressing these issues.

## Statistical Framework

### Two-Stage Hierarchical Model

The core MVMA model uses a two-stage hierarchical framework. At stage 1, study $i$ estimates a $p$-dimensional effect vector:

$$\mathbf{y}_i | \boldsymbol{\mu}_i \sim N(\boldsymbol{\mu}_i, \mathbf{S}_i)$$

where $\mathbf{S}_i$ is the within-study covariance matrix, typically assumed known from reported standard errors and correlations. When within-study correlations are unavailable—a common situation—sensitivity analysis across plausible values (e.g., 0, 0.3, 0.6) is essential.

At stage 2, true study-specific effects vary around a pooled mean:

$$\boldsymbol{\mu}_i \sim N(\boldsymbol{\theta}, \boldsymbol{\Psi})$$

where $\boldsymbol{\theta}$ represents pooled effects across $p$ outcomes and $\boldsymbol{\Psi}$ is the between-study covariance matrix capturing heterogeneity variances and correlations.

The marginal distribution is:

$$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$$

This framework generalizes univariate random-effects meta-analysis while accounting for outcome correlations. The between-study correlation $\rho$ in $\boldsymbol{\Psi}$ quantifies how treatment effects vary together across studies. Positive correlation suggests treatments affecting one outcome similarly affect others.

### Estimation Methods

**Restricted Maximum Likelihood (REML)** is recommended for estimating $\boldsymbol{\Psi}$, as it accounts for uncertainty in fixed effects and provides less biased variance estimates than maximum likelihood (ML). REML maximizes the residual likelihood, effectively removing bias from estimating $\boldsymbol{\theta}$. For small meta-analyses ($k < 10$ studies), REML produces less biased estimates of between-study variance than ML, though both methods can be unstable when $k < 5$ (Thompson and Sharp, 1999).

Inference requires careful consideration of degrees of freedom. For small $k$, the Hartung-Knapp-Sidik-Jonkman adjustment provides better coverage than Wald-type intervals. Degrees of freedom can be approximated using residual df ($k - p$) or Satterthwaite-type approximations for complex designs.

**Bayesian estimation** using Markov Chain Monte Carlo provides full posterior distributions for all parameters, enabling probability statements about treatment effects and rankings. Weakly informative priors—LKJ priors for correlations and half-normal priors for standard deviations—allow data to dominate while ensuring numerical stability. Bayesian approaches naturally handle complex models including network meta-analysis and pattern mixture models for missing data.

### Variance Structures and Sample Size Requirements

MVMA supports multiple structures for $\boldsymbol{\Psi}$, balancing flexibility and parsimony. Unstructured covariance estimates all $p(p+1)/2$ unique elements, providing maximum flexibility but requiring sufficient studies. As a rule of thumb, $k$ should exceed $2p$; when $k < 2p$, consider simpler structures.

Diagonal structures assume independent outcomes, reducing to separate univariate meta-analyses. Intermediate structures—compound symmetry (common correlation), factor analytic—impose constraints improving estimation efficiency when appropriate.

## Missing Data Methods

Missing outcomes pervade meta-analysis; many studies report only subsets of relevant endpoints. Traditional approaches either exclude studies with missing outcomes (complete-case analysis) or impute simple values (zeros), both potentially biasing results. MVMA enables principled missing data handling through the correlation structure.

**Multiple imputation** generates complete datasets by drawing missing values from their posterior predictive distribution given observed data and estimated correlations. Analyzing $M$ imputed datasets (typically $M = 20-50$) and combining results via Rubin's rules provides valid inference under missing-at-random (MAR) assumptions. The correlation structure is crucial: strongly correlated outcomes enable more accurate imputation. However, imputation cannot recover information lost when data are missing; it primarily provides valid standard errors under MAR.

**Pattern mixture models** analyze missing data patterns separately, allowing effects to differ between studies with different patterns—a missing-not-at-random (MNAR) mechanism. This approach provides sensitivity analysis beyond MAR, exploring how conclusions change if missing outcomes differ systematically from observed ones. Patterns with few studies can be pooled or analyzed with informative priors in Bayesian frameworks. Results are often presented as sensitivity analyses under different MNAR assumptions rather than as primary analyses.

## Network Meta-Analysis Extension

Network meta-analysis (NMA) compares multiple treatments through direct and indirect evidence. Extending NMA to multiple outcomes creates a multivariate network meta-analysis (MVNMA) framework, analyzing comparative effectiveness across multiple endpoints simultaneously.

For study $i$ comparing treatments $j$ and $k$, the model becomes:

$$\mathbf{y}_{i(jk)} \sim N(\boldsymbol{\mu}_{i0} + \mathbf{d}_{jk}, \mathbf{S}_{i(jk)} + \boldsymbol{\Psi})$$

where $\mathbf{d}_{jk}$ is the vector of relative treatment effects comparing treatments $j$ and $k$ across all outcomes, $\boldsymbol{\mu}_{i0}$ is the study-specific baseline effect, and the subscript $i(jk)$ indicates study $i$ contributes data for the $j$ versus $k$ comparison.

The consistency assumption—$\mathbf{d}_{jk} = \mathbf{d}_{jl} + \mathbf{d}_{lk}$—enables indirect comparisons, combining evidence across the network. Testing this assumption through node-splitting or loop-inconsistency checks is essential.

MVNMA is particularly valuable for benefit-risk assessment. Consider antidepressant networks evaluating efficacy and tolerability: MVNMA provides joint treatment rankings balancing both outcomes, identifying treatments with favorable benefit-risk profiles rather than optimizing single outcomes.

## Advantages and Applications

MVMA offers practical advantages over separate univariate analyses when outcomes are moderately to strongly correlated. The magnitude of efficiency gains depends on correlation strength, number of studies, missing data patterns, and degree of heterogeneity (Jackson et al., 2011; Riley et al., 2007). Gains are most pronounced when correlation is moderate to strong and when missing data patterns differ across outcomes.

Clinical applications include: (1) diagnostic test accuracy meta-analysis jointly modeling sensitivity and specificity; (2) survival meta-analysis analyzing progression-free and overall survival; (3) multi-domain quality-of-life synthesis; (4) dose-response meta-analysis across multiple outcomes. Each application benefits from preserved correlation structure and comprehensive evidence synthesis.

## Computational Considerations

Practical MVMA implementation faces computational challenges. Estimating $\boldsymbol{\Psi}$ requires optimization over constrained parameter spaces ensuring positive-definiteness. Cholesky parameterization addresses this, transforming the problem to unconstrained optimization while guaranteeing valid covariance matrices. Modern optimization algorithms (L-BFGS-B) with analytical gradients typically achieve convergence within seconds to minutes for moderate-sized networks (up to 50 studies, 5 outcomes) on standard hardware.

Bayesian estimation using Hamiltonian Monte Carlo (HMC) efficiently samples high-dimensional posteriors. Reparameterization and non-centered parameterizations improve sampling efficiency for hierarchical structures.

## Key Assumptions

MVMA relies on several critical assumptions:

1. **Multivariate normality** of effect estimates within and between studies
2. **Within-study covariances** $\mathbf{S}_i$ known or reliably estimated/assumed
3. **Study exchangeability** (random sample from population of studies)
4. **Correct specification** of $\boldsymbol{\Psi}$ structure
5. **MAR assumption** for missing data (or explicit MNAR modeling in sensitivity analyses)

Violations of these assumptions, particularly unknown within-study correlations, require careful sensitivity analysis.

## Recommendations and Limitations

**MVMA is recommended when:**
- Outcomes are conceptually related and likely correlated
- Some studies report missing outcomes that differ by study
- Joint inference across outcomes is scientifically meaningful
- Sample size is adequate ($k \geq 2p$ for unstructured $\boldsymbol{\Psi}$)

**MVMA can be unreliable when:**
- Number of studies $k$ is small relative to outcomes $p$ (rule of thumb: $k < 2p$)
- Within-study correlations are unknown and misspecified
- Between-study correlation estimates are near boundaries ($|\rho| \approx 1$)
- Heterogeneity is extreme ($I^2 > 90\%$) with limited studies
- Outcomes are truly independent ($\rho \approx 0$), offering no efficiency gain

**Critical limitation:** Within-study correlations are rarely reported in primary studies. While these can be imputed or assumed, sensitivity analyses across plausible correlation values are essential. Results robust to this assumption are more credible; substantial sensitivity suggests caution in interpretation.

For small meta-analyses ($k < 5$), simpler variance structures (diagonal, common correlation) are preferable to unstructured covariance. Consider fixed-effect models or univariate analyses when sample size is insufficient for reliable estimation.

## Conclusion

Multivariate meta-analysis provides a rigorous framework for synthesizing correlated outcomes when sample size is adequate and assumptions are met. Through borrowing strength, principled missing data handling, and coherent multivariate inference, MVMA can deliver more efficient evidence synthesis than separate univariate analyses. Extensions to network meta-analysis enable joint benefit-risk assessment across treatment networks. However, success critically depends on adequate sample size relative to dimensionality, availability of within-study correlation information, and careful assessment of assumptions. As clinical trials increasingly evaluate multiple endpoints, MVMA offers essential methodology for evidence synthesis when applied appropriately with thorough sensitivity analyses.

## References

1. Jackson D, Riley R, White IR. Multivariate meta-analysis: potential and promise. *Stat Med*. 2011;30(20):2481-2498.

2. Riley RD, Abrams KR, Sutton AJ, Lambert PC, Thompson JR. Bivariate random-effects meta-analysis and the estimation of between-study correlation. *BMC Med Res Methodol*. 2007;7:3.

3. Thompson SG, Sharp SJ. Explaining heterogeneity in meta-analysis: a comparison of methods. *Stat Med*. 1999;18(20):2693-2708.

4. Efthimiou O, Mavridis D, Riley RD, Cipriani A, Salanti G. Joint synthesis of multiple correlated outcomes in networks of interventions. *Biostatistics*. 2019;20(1):84-98.

5. White IR, Barrett JK, Jackson D, Higgins JPT. Consistency and inconsistency in network meta-analysis: model estimation using multivariate meta-regression. *Res Synth Methods*. 2012;3(2):111-125.

6. Mavridis D, Salanti G. A practical introduction to multivariate meta-analysis. *Stat Methods Med Res*. 2013;22(2):133-158.

7. Kirkham JJ, Riley RD, Williamson PR. A multivariate meta-analysis approach for reducing the impact of outcome reporting bias in systematic reviews. *Stat Med*. 2012;31(20):2179-2195.

8. Riley RD, Jackson D, Salanti G, et al. Multivariate and network meta-analysis of multiple outcomes and multiple treatments: rationale, concepts, and examples. *BMJ*. 2017;358:j3932.

9. Copas JB, Jackson D, White IR, Riley RD. The role of secondary outcomes in multivariate meta-analysis. *J R Stat Soc Ser C*. 2018;67(5):1177-1205.

10. IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ. Plea for routinely presenting prediction intervals in meta-analysis. *BMJ Open*. 2016;6(7):e010247.

11. Van Houwelingen HC, Arends LR, Stijnen T. Advanced methods in meta-analysis: multivariate approach and meta-regression. *Stat Med*. 2002;21(4):589-624.
