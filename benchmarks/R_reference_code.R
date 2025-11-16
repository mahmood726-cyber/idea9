# R Reference Code for Benchmark Comparison
# This code generates reference values for comparing Python MVMeta with R mvmeta
#
# Install R mvmeta package first:
# install.packages("mvmeta")

library(mvmeta)

cat("=" , rep("=", 78), "\n", sep="")
cat("R mvmeta Reference Results\n")
cat("=" , rep("=", 78), "\n\n", sep="")

# ============================================================================
# Test 1: Berkey et al. (1998) Dataset - REML
# ============================================================================

cat("TEST 1: Berkey et al. (1998) Dataset - REML\n")
cat(rep("-", 80), "\n", sep="")

# Load the built-in dataset
data(berkey98, package="mvmeta")

# Extract data
y <- as.matrix(berkey98[, c("PD", "AL")])
S <- as.list(berkey98[, c("SPD", "SAL", "rho")])

# Convert to covariance matrices
S_matrices <- lapply(1:nrow(berkey98), function(i) {
  se_pd <- berkey98$SPD[i]
  se_al <- berkey98$SAL[i]
  rho <- berkey98$rho[i]

  matrix(c(
    se_pd^2, rho * se_pd * se_al,
    rho * se_pd * se_al, se_al^2
  ), nrow=2)
})

# Fit REML model
fit_reml <- mvmeta(y, S_matrices, method="reml")

# Print results
cat("\nPooled Effects (θ):\n")
print(coef(fit_reml))

cat("\nStandard Errors:\n")
print(sqrt(diag(vcov(fit_reml))))

cat("\n95% Confidence Intervals:\n")
print(confint(fit_reml))

cat("\nBetween-Study Covariance (Ψ):\n")
print(fit_reml$Psi)

cat("\nLog-likelihood:\n")
print(logLik(fit_reml))

cat("\n\nReference Values for Python Comparison:\n")
cat(sprintf("theta_PD: %.4f\n", coef(fit_reml)[1]))
cat(sprintf("theta_AL: %.4f\n", coef(fit_reml)[2]))
cat(sprintf("se_PD: %.4f\n", sqrt(vcov(fit_reml)[1,1])))
cat(sprintf("se_AL: %.4f\n", sqrt(vcov(fit_reml)[2,2])))
ci <- confint(fit_reml)
cat(sprintf("ci_lower_PD: %.4f\n", ci[1,1]))
cat(sprintf("ci_upper_PD: %.4f\n", ci[1,2]))
cat(sprintf("ci_lower_AL: %.4f\n", ci[2,1]))
cat(sprintf("ci_upper_AL: %.4f\n", ci[2,2]))
cat(sprintf("tau2_PD: %.4f\n", fit_reml$Psi[1,1]))
cat(sprintf("tau2_AL: %.4f\n", fit_reml$Psi[2,2]))
cat(sprintf("loglik: %.4f\n", as.numeric(logLik(fit_reml))))


# ============================================================================
# Test 2: Same Dataset - ML Estimation
# ============================================================================

cat("\n\n", rep("=", 80), "\n", sep="")
cat("TEST 2: Berkey et al. (1998) Dataset - ML\n")
cat(rep("-", 80), "\n", sep="")

# Fit ML model
fit_ml <- mvmeta(y, S_matrices, method="ml")

cat("\nML Results:\n")
cat(sprintf("theta_PD: %.4f\n", coef(fit_ml)[1]))
cat(sprintf("theta_AL: %.4f\n", coef(fit_ml)[2]))
cat(sprintf("tau2_PD: %.4f\n", fit_ml$Psi[1,1]))
cat(sprintf("tau2_AL: %.4f\n", fit_ml$Psi[2,2]))


# ============================================================================
# Test 3: Simulated Data (matching Python seed)
# ============================================================================

cat("\n\n", rep("=", 80), "\n", sep="")
cat("TEST 3: Simulated Data for Validation\n")
cat(rep("-", 80), "\n", sep="")

# Note: This would require reproducing Python's random number generation
# For benchmarking, we use the Python-generated data and run R on it
cat("\nNote: For simulated data, we use Python-generated data\n")
cat("      and compare R's analysis of that data.\n")


# ============================================================================
# Test 4: Heterogeneity Statistics
# ============================================================================

cat("\n\n", rep("=", 80), "\n", sep="")
cat("TEST 4: Heterogeneity Statistics\n")
cat(rep("-", 80), "\n", sep="")

# Cochran's Q test
cat("\nCochran's Q test for each outcome:\n")

# Q test for PD (outcome 1)
q_test_pd <- qtest.mvmeta(fit_reml, outcome=1)
cat(sprintf("PD - Q: %.2f, df: %d, p-value: %.4f\n",
            q_test_pd$Q, q_test_pd$df, q_test_pd$pvalue))

# Q test for AL (outcome 2)
q_test_al <- qtest.mvmeta(fit_reml, outcome=2)
cat(sprintf("AL - Q: %.2f, df: %d, p-value: %.4f\n",
            q_test_al$Q, q_test_al$df, q_test_al$pvalue))


# ============================================================================
# Test 5: Prediction
# ============================================================================

cat("\n\n", rep("=", 80), "\n", sep="")
cat("TEST 5: Prediction Intervals\n")
cat(rep("-", 80), "\n", sep="")

# Predict for a new study
pred <- predict(fit_reml, interval="prediction", level=0.95)
cat("\n95% Prediction Intervals:\n")
print(pred)


# ============================================================================
# Summary
# ============================================================================

cat("\n\n", rep("=", 80), "\n", sep="")
cat("SUMMARY\n")
cat(rep("=", 80), "\n", sep="")

cat("\nR mvmeta Package Information:\n")
cat(sprintf("Version: %s\n", packageVersion("mvmeta")))
cat(sprintf("R Version: %s\n", R.version.string))

cat("\nReference:\n")
cat("Gasparrini A, Armstrong B, Kenward MG (2012).\n")
cat("'Multivariate meta-analysis for non-linear and other\n")
cat("multi-parameter associations.'\n")
cat("Statistics in Medicine, 31(29), 3821-3839.\n")

cat("\nThese results serve as reference values for validating\n")
cat("the Python MVMeta implementation.\n")

cat("\n", rep("=", 80), "\n", sep="")
