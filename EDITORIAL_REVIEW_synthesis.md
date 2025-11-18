# Editorial Review: Multivariate Meta-Analysis Synthesis Paper

**Reviewer**: Synthesis Methods Editor
**Date**: 2025-11-18
**Recommendation**: MAJOR REVISION REQUIRED

## CRITICAL ISSUES - Statistical Accuracy and Data Precision

### 1. **UNSUBSTANTIATED NUMERICAL CLAIMS** ⚠️ CRITICAL

**Location**: Lines 57-58

**Issue**:
> "Simulation studies demonstrate 15-30% efficiency gains in small meta-analyses (k < 20) when outcomes are moderately correlated (ρ > 0.3). Greater gains emerge with missing data; MVMA maintains nominal coverage even with 30% missing outcomes under MAR..."

**Problem**: These specific quantitative claims (15-30%, 30% missing, k < 20, ρ > 0.3) are **NOT supported by any simulation studies presented in this paper or cited references**. This constitutes fabrication of data.

**Required Action**:
- Either conduct actual simulations to support these claims and present results
- OR cite specific published studies with exact page numbers where these results appear
- OR remove these specific numerical claims and use qualitative statements

**Suggested Revision**:
```
"Simulation studies suggest efficiency gains in small to moderate meta-analyses when
outcomes are moderately to strongly correlated (Jackson et al., 2011; Riley et al.,
2007). The magnitude of gain depends on the strength of correlation, number of studies,
and degree of missingness."
```

### 2. **STATISTICAL MODEL SPECIFICATION ISSUES** ⚠️ MAJOR

**Location**: Lines 19-23

**Issue**: The model specification is imprecise and potentially misleading.

**Current**:
$$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$$

**Problems**:
1. Doesn't specify that $\mathbf{S}_i$ is **assumed known** (a critical and often unrealistic assumption)
2. This is the marginal distribution; the two-stage hierarchical structure is not clear
3. No mention that this assumes multivariate normality

**Required Revision**:
```
The core MVMA model uses a two-stage hierarchical framework. At stage 1,
study i estimates a p-dimensional effect vector with:

$$\mathbf{y}_i | \boldsymbol{\mu}_i \sim N(\boldsymbol{\mu}_i, \mathbf{S}_i)$$

where $\mathbf{S}_i$ is the within-study covariance matrix, typically assumed known
from reported standard errors and correlations (or imputed if unavailable).

At stage 2, the true study-specific effects vary around a mean:

$$\boldsymbol{\mu}_i \sim N(\boldsymbol{\theta}, \boldsymbol{\Psi})$$

The marginal distribution is then:

$$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$$
```

### 3. **VAGUE QUANTITATIVE LANGUAGE** ⚠️ MODERATE

**Location**: Line 29

**Issue**:
> "For small meta-analyses (k < 10 studies), REML substantially outperforms ML."

**Problem**: "Substantially outperforms" is undefined. Outperforms in what metric? By how much?

**Required Revision**:
```
For small meta-analyses (k < 10 studies), REML produces less biased estimates of
between-study variance than ML, with bias reduction increasing as k decreases
(Thompson and Sharp, 1999). However, both methods can be unstable when k < 5.
```

### 4. **NETWORK MA MODEL NOTATION ERROR** ⚠️ MODERATE

**Location**: Line 49

**Issue**:
$$\mathbf{y}_{ijk} \sim N(\mathbf{d}_{jk}, \mathbf{S}_{ijk} + \boldsymbol{\Psi})$$

**Problem**: Subscript 'i' is undefined in this context. Is it indexing studies comparing treatments j and k? This needs clarification.

**Required Revision**:
```
For study i comparing treatments j and k, the model becomes:

$$\mathbf{y}_{i(jk)} \sim N(\boldsymbol{\mu}_{i0} + \mathbf{d}_{jk}, \mathbf{S}_{i(jk)} + \boldsymbol{\Psi})$$

where $\mathbf{d}_{jk}$ is the vector of relative treatment effects, $\boldsymbol{\mu}_{i0}$
is the study-specific baseline effect, and the subscript i(jk) indicates study i
contributes data for the j vs k comparison.
```

### 5. **MISSING CRITICAL METHODOLOGICAL DETAILS** ⚠️ MAJOR

The following essential statistical issues are not addressed:

**a) Degrees of Freedom** (ABSENT)
- How are degrees of freedom calculated for confidence intervals?
- Hartung-Knapp adjustment for small k not mentioned
- This affects coverage rates claimed in line 57

**Required Addition**:
```
Inference for MVMA requires careful consideration of degrees of freedom. For small k,
the Hartung-Knapp-Sidik-Jonkman adjustment provides better coverage than Wald-type
intervals (IntHout et al., 2014). Degrees of freedom approximations include residual
df (k - p) or Satterthwaite-type approximations for complex designs.
```

**b) Estimation Challenges** (ABSENT)
- When k is small relative to p, $\boldsymbol{\Psi}$ is poorly estimated
- No guidance on minimum k/p ratio needed

**Required Addition**:
```
Reliable estimation of $\boldsymbol{\Psi}$ requires sufficient studies relative to
parameters. As a rule of thumb, k should exceed 2p, though structured covariance
models (compound symmetry, AR(1)) can be estimated with fewer studies. When k < 2p,
consider simpler variance structures or fixed-effect models.
```

**c) Within-Study Correlation Assumption** (Mentioned but understated)
- Line 70 mentions this limitation but doesn't emphasize how critical it is
- Most primary studies don't report within-study correlations

**Strengthen to**:
```
A major practical limitation is that within-study correlations are rarely reported
in primary studies. While these can be imputed or assumed, sensitivity analyses
across plausible correlation values (e.g., 0, 0.3, 0.6) are essential. Results
robust to this assumption are more credible; substantial sensitivity suggests caution.
```

### 6. **EFFICIENCY CLAIMS LACK PRECISION** ⚠️ MODERATE

**Location**: Line 57

**Issue**: "Efficiency gains" is vague. Efficiency relative to what? Standard error reduction? MSE? Power?

**Required Revision**:
```
Compared to separate univariate meta-analyses, MVMA can provide narrower confidence
intervals (increased precision) when outcomes are correlated and when missing data
patterns differ across outcomes. The gain depends on the between-study correlation,
with negligible benefit when ρ ≈ 0.
```

### 7. **REFERENCE ACCURACY ISSUES** ⚠️ MODERATE

Several references need verification:

**Reference 2** (Line 81-82):
- Citation seems correct, but this is actually about **bivariate** (2 outcomes), not general multivariate MA
- Should clarify: "...bivariate random-effects meta-analysis..."

**Missing Key References**:
1. **Thompson SG, Sharp SJ (1999)** - For REML vs ML comparison mentioned line 29
2. **IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ (2014)** - For Hartung-Knapp adjustment
3. **Van Houwelingen HC, Arends LR, Stijnen T (2002)** - Advanced methods for multivariate MA

**Add these to references**

### 8. **INTERNAL INCONSISTENCY** ⚠️ MINOR

**Location**: Lines 34-35 vs. Line 57

- Line 34: Mentions "autoregressive" structure for $\boldsymbol{\Psi}$
- Problem: AR structures are typically for **within-study** repeated measures, not between-study correlations
- Either explain why AR makes sense for between-study covariance or remove

**Suggested fix**: Replace "autoregressive" with "factor analytic" or "diagonal with common correlation"

---

## MODERATE ISSUES - Clarity and Precision

### 9. **BORROWING OF STRENGTH - IMPRECISE LANGUAGE**

**Location**: Lines 11, 56

**Issue**: "Borrowing strength" is used colloquially without technical explanation

**Suggested Addition** (after line 11):
```
This "borrowing of strength" occurs because the between-study correlation structure
provides information: if outcomes are positively correlated across studies, a study
with high Outcome 1 effect likely has high Outcome 2 effect. This shrinks estimates
toward the multivariate mean, similar to how random-effects models shrink toward the
overall mean.
```

### 10. **PATTERN MIXTURE MODELS - OVERSIMPLIFIED**

**Location**: Lines 43-44

**Issue**: PMM description is too simple; doesn't mention challenges

**Add**:
```
However, PMMs require sufficient studies within each pattern for stable estimation.
Patterns with few studies can be pooled or analyzed with informative priors in
Bayesian frameworks. Results are often presented as sensitivity analyses under
different MNAR assumptions.
```

### 11. **COMPUTATIONAL CLAIMS NEED CONTEXT**

**Location**: Lines 63-65

**Issue**: "Networks up to 50 studies and 5 outcomes" and "convergence within minutes" - needs context

**Revision**:
```
Modern optimization algorithms (L-BFGS-B) with analytical gradients typically achieve
convergence within seconds to minutes for moderate-sized networks (up to 50 studies,
5 outcomes) on standard hardware. Larger networks or more complex variance structures
may require more sophisticated initialization or regularization.
```

---

## MINOR ISSUES - Editorial Polish

### 12. **Title Precision**
Consider: "Multivariate Meta-Analysis: **Methods for** Synthesizing Correlated Outcomes"
- More accurate than "Framework"

### 13. **Abstract Word Count**
Current abstract is ~90 words. For synthesis journals, 150-250 words is typical. Consider expanding to include:
- Specific methods covered (REML, Bayesian, MI)
- One concrete application example

### 14. **Equation Formatting**
- Line 51: Ensure consistency assumption is numbered if referenced later
- Consider numbering key equations (lines 21, 49) for referencing

### 15. **Terminology Consistency**
- "Meta-analysis" vs "meta-analyses" - be consistent with hyphenation
- "Between-study" vs "among-study" - pick one throughout

---

## STATISTICAL ACCURACY VERIFICATION CHECKLIST

| Item | Status | Action Required |
|------|--------|-----------------|
| Model equations correct | ⚠️ Needs revision | Add two-stage hierarchy |
| Numerical claims substantiated | ❌ FAIL | Provide evidence or remove |
| Estimation methods accurate | ✓ Pass | Minor clarifications needed |
| Missing data theory correct | ✓ Pass | Add PMM caveats |
| Network MA model correct | ⚠️ Needs revision | Fix notation |
| Inference procedures complete | ❌ FAIL | Add df, Hartung-Knapp |
| Limitations adequately stated | ⚠️ Partial | Strengthen within-study corr issue |
| References accurate | ⚠️ Partial | Add missing refs, verify details |
| Internal consistency | ⚠️ Minor issues | Fix AR(1) mention |

---

## OVERALL ASSESSMENT

**Strengths**:
1. Clear structure and logical flow
2. Good coverage of key MVMA topics
3. Appropriate scope for 1000-word synthesis
4. Relevant clinical examples

**Critical Weaknesses**:
1. **Unsubstantiated quantitative claims** (15-30% gains, 30% missing, etc.)
2. **Incomplete statistical specifications** (model hierarchy, df, k/p ratio)
3. **Missing essential methodological details** (Hartung-Knapp, within-study correlation challenges)

**Recommendation**: **MAJOR REVISION**

The paper addresses important methodology but contains unsubstantiated numerical claims that could mislead readers. Statistical model specifications need technical precision expected in a methods journal.

**Required revisions before publication**:
1. Remove all specific numerical claims not supported by presented or cited evidence
2. Revise model specifications to show two-stage hierarchy
3. Add sections on degrees of freedom and small-sample inference
4. Strengthen discussion of within-study correlation assumption
5. Add missing key references
6. Address notation issues in network MA section

**Estimated revision effort**: 2-3 days for a thorough revision

**Revised manuscript length**: ~1200-1300 words (additional technical details required)

---

## RECOMMENDED ADDITIONS FOR ACCURACY

### Critical Addition 1: Assumptions Box

Add after Statistical Framework section:

```
**Key Assumptions**:
1. Multivariate normality of effect estimates
2. Within-study covariances $\mathbf{S}_i$ known or reliably estimated
3. Studies are exchangeable (random sample from population of studies)
4. Correct specification of $\boldsymbol{\Psi}$ structure
5. For missing data: MAR assumption (or explicit MNAR modeling)
```

### Critical Addition 2: When MVMA Can Be Unreliable

Add to Limitations section:

```
MVMA can produce unreliable results when:
1. Number of studies (k) is small relative to outcomes (p) - rule of thumb: k ≥ 2p
2. Within-study correlations are unknown and misspecified
3. Between-study correlation is near boundary (|ρ| ≈ 1)
4. Heterogeneity is extreme (I² > 90%)
5. Publication bias affects outcomes differentially
```

---

**Contact reviewer for clarifications**: [Editorial office email]
