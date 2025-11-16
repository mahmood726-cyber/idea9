"""
Tests for influence diagnostics functionality.
"""

import numpy as np
import pytest
from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.diagnostics import (
    leave_one_out_analysis,
    cook_distance,
    identify_outliers,
    studentized_residuals,
    hat_values,
    dfbetas,
    comprehensive_diagnostics
)


class TestLeaveOneOutAnalysis:
    """Tests for leave-one-out influence analysis."""

    def test_loo_basic(self):
        """Test basic LOO analysis."""
        y, S = simulate_multivariate_ma(
            n_studies=10,
            n_outcomes=2,
            seed=42
        )

        loo_results = leave_one_out_analysis(y, S, verbose=False)

        # Check structure
        assert len(loo_results) == 10 * 2  # n_studies * n_outcomes
        assert 'study' in loo_results.columns
        assert 'outcome' in loo_results.columns
        assert 'delta_theta' in loo_results.columns
        assert 'std_delta_theta' in loo_results.columns

    def test_loo_convergence(self):
        """Test that LOO models converge."""
        y, S = simulate_multivariate_ma(n_studies=12, n_outcomes=2, seed=123)

        loo_results = leave_one_out_analysis(y, S, verbose=False)

        # Most models should converge
        if 'converged' in loo_results.columns:
            convergence_rate = loo_results['converged'].mean()
            assert convergence_rate > 0.8

    def test_loo_influence_detection(self):
        """Test that LOO detects influential points."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=456)

        # Add an outlier
        y[0, 0] = y[0, 0] + 3.0  # Large outlier

        loo_results = leave_one_out_analysis(y, S, verbose=False)

        # Study 0 should show large influence
        study_0 = loo_results[loo_results['study'] == 0]
        assert any(abs(study_0['std_delta_theta']) > 1.0)


class TestCooksDistance:
    """Tests for Cook's distance."""

    def test_cooks_d_basic(self):
        """Test basic Cook's distance computation."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=789)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        cooks_d = cook_distance(y, S, results)

        # Check shape and validity
        assert cooks_d.shape == (15,)
        assert all(cooks_d >= 0)
        assert not np.all(np.isnan(cooks_d))

    def test_cooks_d_outlier(self):
        """Test that Cook's distance detects outliers."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=111)

        # Add outlier
        y[5, :] = y[5, :] + 2.5

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        cooks_d = cook_distance(y, S, results)

        # Study 5 should have large Cook's distance
        assert cooks_d[5] > np.median(cooks_d)

    def test_cooks_d_threshold(self):
        """Test Cook's distance against threshold."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=222)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        cooks_d = cook_distance(y, S, results)

        # Threshold: 4/n
        threshold = 4 / len(y)

        # Most points should be below threshold
        below_threshold = np.sum(cooks_d < threshold)
        assert below_threshold > len(y) * 0.7


class TestOutlierIdentification:
    """Tests for outlier identification."""

    def test_identify_outliers_none(self):
        """Test when no outliers present."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            between_study_sd=0.2,  # Low heterogeneity
            seed=333
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        outliers = identify_outliers(y, S, results, threshold=3.0)

        # Should find few or no outliers with threshold=3
        assert len(outliers) <= 2  # At most 1-2 by chance

    def test_identify_outliers_present(self):
        """Test when outliers are present."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=444)

        # Add clear outliers
        y[3, 0] = y[3, 0] + 4.0
        y[10, 1] = y[10, 1] - 3.5

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        outliers = identify_outliers(y, S, results, threshold=2.5)

        # Should detect the outliers
        assert len(outliers) >= 1
        assert 3 in outliers or 10 in outliers

    def test_outlier_structure(self):
        """Test outlier information structure."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=555)
        y[5, 0] += 3.0  # Add outlier

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        outliers = identify_outliers(y, S, results, threshold=2.0)

        if len(outliers) > 0:
            study_id = list(outliers.keys())[0]
            outlier_info = outliers[study_id]

            assert 'max_std_residual' in outlier_info
            assert 'std_residuals' in outlier_info
            assert 'raw_residuals' in outlier_info
            assert 'outlier_outcomes' in outlier_info


class TestStudentizedResiduals:
    """Tests for studentized residuals."""

    def test_studentized_residuals_basic(self):
        """Test basic studentized residuals."""
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=666)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        stud_resid = studentized_residuals(y, S, results)

        # Check shape
        assert stud_resid.shape == (10, 2)

        # Should be approximately standard normal (mean ~0, sd ~1)
        valid_resid = stud_resid[~np.isnan(stud_resid)]
        if len(valid_resid) > 0:
            assert abs(np.mean(valid_resid)) < 1.0
            assert 0.5 < np.std(valid_resid) < 2.0

    def test_studentized_vs_regular_residuals(self):
        """Test that studentized residuals differ from regular."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=777)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        stud_resid = studentized_residuals(y, S, results)

        # Regular residuals
        reg_resid = y - results.theta

        # Studentized should be standardized
        valid_stud = stud_resid[~np.isnan(stud_resid)]
        if len(valid_stud) > 0:
            # Studentized should have smaller variance than raw
            assert np.var(valid_stud) < np.var(reg_resid)


class TestHatValues:
    """Tests for hat (leverage) values."""

    def test_hat_values_basic(self):
        """Test basic hat value computation."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=888)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        h = hat_values(S, results.Psi)

        # Check properties
        assert h.shape == (15,)
        assert all(h >= 0)
        # Hat values should sum approximately to p (number of outcomes)
        # But this isn't exact for multivariate case

    def test_hat_values_range(self):
        """Test that hat values are in reasonable range."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=999)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        h = hat_values(S, results.Psi)

        # Should be between 0 and 1 typically
        assert all(h >= 0)
        assert all(h <= 2)  # Can exceed 1 in multivariate case


class TestDFBETAS:
    """Tests for DFBETAS."""

    def test_dfbetas_basic(self):
        """Test basic DFBETAS computation."""
        y, S = simulate_multivariate_ma(n_studies=12, n_outcomes=2, seed=101)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        dfb = dfbetas(y, S, results)

        # Check shape
        assert dfb.shape == (12, 2)

    def test_dfbetas_threshold(self):
        """Test DFBETAS against threshold."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=202)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        dfb = dfbetas(y, S, results)

        # Threshold: 2/sqrt(n)
        threshold = 2 / np.sqrt(len(y))

        # Most should be below threshold
        valid_dfb = dfb[~np.isnan(dfb)]
        if len(valid_dfb) > 0:
            below_threshold = np.sum(np.abs(valid_dfb) < threshold)
            assert below_threshold > len(valid_dfb) * 0.6


class TestComprehensiveDiagnostics:
    """Tests for comprehensive diagnostics."""

    def test_comprehensive_diagnostics_basic(self):
        """Test basic comprehensive diagnostics."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=303)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        diag = comprehensive_diagnostics(y, S, results)

        # Check structure
        assert len(diag) == 15
        assert 'study' in diag.columns
        assert 'cooks_d' in diag.columns
        assert 'hat_value' in diag.columns
        assert 'max_std_resid' in diag.columns
        assert 'is_outlier' in diag.columns
        assert 'is_influential' in diag.columns

    def test_comprehensive_diagnostics_flags(self):
        """Test diagnostic flags."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=404)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        diag = comprehensive_diagnostics(y, S, results)

        # Should have boolean flags
        assert diag['is_outlier'].dtype == bool
        assert diag['is_influential'].dtype == bool
        assert diag['high_leverage'].dtype == bool

        # Most studies should not be flagged
        assert diag['is_outlier'].sum() < len(diag) * 0.3
        assert diag['is_influential'].sum() < len(diag) * 0.3

    def test_comprehensive_diagnostics_labels(self):
        """Test with custom study labels."""
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=505)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        labels = [f"Study_{i+1}" for i in range(10)]
        diag = comprehensive_diagnostics(y, S, results, study_labels=labels)

        # Check labels
        assert list(diag['study']) == labels

    def test_comprehensive_diagnostics_outlier_detection(self):
        """Test that comprehensive diagnostics detect outliers."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=606)

        # Add clear outlier
        y[8, :] += 3.0

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        diag = comprehensive_diagnostics(y, S, results)

        # Study 8 should be flagged
        study_8 = diag[diag['study_id'] == 8].iloc[0]
        assert study_8['is_outlier'] or study_8['is_influential']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
