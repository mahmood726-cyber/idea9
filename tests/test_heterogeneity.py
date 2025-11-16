"""
Tests for heterogeneity assessment functionality.
"""

import numpy as np
import pytest
from mvmeta import MultivariateMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.diagnostics import (
    assess_heterogeneity,
    cochran_q_test,
    compute_prediction_interval
)


class TestCochranQ:
    """Tests for Cochran's Q test."""

    def test_cochran_q_homogeneous(self):
        """Test Q statistic with homogeneous data."""
        # Create homogeneous data (no heterogeneity)
        y = np.array([0.5, 0.52, 0.48, 0.51, 0.49])
        se = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
        S = se ** 2
        theta = 0.5

        Q, df, p_value = cochran_q_test(y, S, theta)

        # Q should be small for homogeneous data
        assert Q >= 0
        assert df == 4  # n - 1
        assert p_value > 0.05  # Should not reject homogeneity
        assert p_value <= 1.0

    def test_cochran_q_heterogeneous(self):
        """Test Q statistic with heterogeneous data."""
        # Create heterogeneous data
        y = np.array([0.2, 0.8, 0.3, 0.7, 0.4])
        se = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
        S = se ** 2
        theta = 0.5

        Q, df, p_value = cochran_q_test(y, S, theta)

        # Q should be large for heterogeneous data
        assert Q > 0
        assert df == 4
        # Likely to reject homogeneity (but not guaranteed)

    def test_cochran_q_returns(self):
        """Test return types and validity."""
        y = np.random.randn(10)
        S = np.ones(10) * 0.01

        Q, df, p_value = cochran_q_test(y, S, np.mean(y))

        assert isinstance(Q, float)
        assert isinstance(df, (int, np.integer))
        assert isinstance(p_value, float)
        assert Q >= 0
        assert df == 9
        assert 0 <= p_value <= 1


class TestHeterogeneityAssessment:
    """Tests for comprehensive heterogeneity assessment."""

    def test_assess_heterogeneity_basic(self):
        """Test basic heterogeneity assessment."""
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            between_study_sd=0.3,
            seed=42
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        # Check structure
        assert len(het_results) == 2  # Two outcomes
        assert 'outcome' in het_results.columns
        assert 'Q' in het_results.columns
        assert 'p_value' in het_results.columns
        assert 'I2' in het_results.columns
        assert 'tau2' in het_results.columns

        # Check values are valid
        assert all(het_results['Q'] >= 0)
        assert all((het_results['p_value'] >= 0) & (het_results['p_value'] <= 1))
        assert all(het_results['I2'] >= 0)
        assert all(het_results['tau2'] >= 0)

    def test_heterogeneity_with_low_tau(self):
        """Test with low heterogeneity."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            between_study_sd=0.1,  # Low heterogeneity
            seed=123
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        # I2 should be relatively low
        for _, row in het_results.iterrows():
            assert row['I2'] >= 0
            # tau2 should be close to true value (0.01)
            assert row['tau2'] >= 0

    def test_heterogeneity_with_high_tau(self):
        """Test with high heterogeneity."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            between_study_sd=0.8,  # High heterogeneity
            seed=456
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        # I2 should be relatively high
        for _, row in het_results.iterrows():
            # With high tau, we expect substantial I2
            assert row['I2'] >= 0
            assert row['tau2'] > 0


class TestPredictionIntervals:
    """Tests for prediction intervals."""

    def test_prediction_interval_basic(self):
        """Test basic prediction interval computation."""
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            seed=789
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        pi_lower, pi_upper = compute_prediction_interval(results, coverage=0.95)

        # Check shapes
        assert pi_lower.shape == (2,)
        assert pi_upper.shape == (2,)

        # Check validity
        assert all(pi_lower < results.theta)
        assert all(pi_upper > results.theta)
        assert all(pi_upper > pi_lower)

    def test_prediction_interval_width(self):
        """Test that PI is wider than CI."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            between_study_sd=0.4,
            seed=999
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        pi_lower, pi_upper = compute_prediction_interval(results)

        # PI should be wider than CI (in general)
        ci_width = results.ci_upper - results.ci_lower
        pi_width = pi_upper - pi_lower

        # At least one outcome should have wider PI
        # (This is almost always true unless tau2 is very small)
        assert any(pi_width >= ci_width)

    def test_prediction_interval_alpha(self):
        """Test different alpha levels."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=111)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        # 95% PI
        pi_lower_95, pi_upper_95 = compute_prediction_interval(results, coverage=0.95)

        # 99% PI
        pi_lower_99, pi_upper_99 = compute_prediction_interval(results, coverage=0.99)

        # 99% PI should be wider
        width_95 = pi_upper_95 - pi_lower_95
        width_99 = pi_upper_99 - pi_lower_99

        assert all(width_99 >= width_95)

    def test_prediction_interval_no_heterogeneity(self):
        """Test PI when tau2 = 0."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            between_study_sd=0.001,  # Essentially zero
            seed=222
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        pi_lower, pi_upper = compute_prediction_interval(results)

        # When tau2 ≈ 0, PI should be close to CI
        ci_width = results.ci_upper - results.ci_lower
        pi_width = pi_upper - pi_lower

        # Ratio should be close to 1
        ratio = pi_width / ci_width
        assert all(ratio < 1.5)  # Not much wider


class TestHeterogeneityEdgeCases:
    """Tests for edge cases in heterogeneity assessment."""

    def test_single_outcome(self):
        """Test heterogeneity with single outcome."""
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=1,
            seed=333
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        assert len(het_results) == 1
        assert het_results.iloc[0]['outcome'] == 0

    def test_many_outcomes(self):
        """Test heterogeneity with many outcomes."""
        y, S = simulate_multivariate_ma(
            n_studies=25,
            n_outcomes=5,
            seed=444
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        assert len(het_results) == 5
        assert list(het_results['outcome']) == [0, 1, 2, 3, 4]

    def test_small_sample(self):
        """Test with very small sample."""
        y, S = simulate_multivariate_ma(
            n_studies=5,
            n_outcomes=2,
            seed=555
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S)

        het_results = assess_heterogeneity(results, y, S)

        # Should still work with small samples
        assert len(het_results) == 2
        assert all(het_results['df'] == 4)  # n - 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
