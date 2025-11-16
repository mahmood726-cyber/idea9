"""
Tests for multivariate meta-analysis models.
"""

import numpy as np
import pytest
from mvmeta import MultivariateMetaAnalysis, MultivariateNetworkMetaAnalysis
from mvmeta.utils import simulate_multivariate_ma, simulate_network_ma


class TestMultivariateMetaAnalysis:
    """Tests for MultivariateMetaAnalysis class."""

    def test_basic_fit(self):
        """Test basic model fitting."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=42)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')

        assert results.converged
        assert results.theta.shape == (2,)
        assert results.theta_se.shape == (2,)
        assert results.Psi.shape == (2, 2)
        assert results.n_studies == 15
        assert results.n_outcomes == 2

    def test_ml_estimation(self):
        """Test ML estimation."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=42)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='ml')

        assert results.converged
        assert results.method == 'ML'

    def test_variance_structures(self):
        """Test different variance structures."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=42)

        for vs in ['unstructured', 'diagonal', 'compound_symmetry']:
            model = MultivariateMetaAnalysis(variance_structure=vs)
            results = model.fit(y, S, method='reml')
            assert results.converged, f"Failed for {vs}"

    def test_single_outcome(self):
        """Test with single outcome (univariate case)."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=1, seed=42)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')

        assert results.converged
        assert results.n_outcomes == 1

    def test_results_properties(self):
        """Test results properties and methods."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=42)

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')

        # Test properties
        assert results.ci_lower.shape == (2,)
        assert results.ci_upper.shape == (2,)
        assert results.between_study_correlation.shape == (2, 2)

        # Test methods
        summary = results.summary()
        assert isinstance(summary, str)
        assert 'Multivariate Meta-Analysis Results' in summary

        df = results.to_dataframe()
        assert df.shape == (2, 5)

    def test_input_validation(self):
        """Test input validation."""
        model = MultivariateMetaAnalysis()

        # Mismatched shapes
        y = np.random.randn(10, 2)
        S = np.random.randn(5, 2, 2)

        with pytest.raises(ValueError):
            model.fit(y, S)

    def test_heterogeneity_statistics(self):
        """Test heterogeneity statistics."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            between_study_sd=0.5,
            seed=42
        )

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')

        assert results.I2 is not None
        assert results.I2.shape == (2,)
        assert np.all(results.I2 >= 0)
        assert np.all(results.I2 <= 1)
        assert results.Q_stat is not None


class TestMultivariateNetworkMetaAnalysis:
    """Tests for MultivariateNetworkMetaAnalysis class."""

    def test_basic_network_fit(self):
        """Test basic network meta-analysis."""
        np.random.seed(42)
        data = simulate_network_ma(
            n_treatments=3,
            n_outcomes=2,
            n_studies=10,
            seed=42
        )

        model = MultivariateNetworkMetaAnalysis()
        results = model.fit(data, method='reml')

        assert results.converged
        assert results.n_outcomes == 2
        assert 'theta_matrix' in results.additional_info
        assert 'treatment_names' in results.additional_info

    def test_treatment_effects_table(self):
        """Test treatment effects table generation."""
        np.random.seed(42)
        data = simulate_network_ma(
            n_treatments=3,
            n_outcomes=2,
            n_studies=10,
            seed=42
        )

        model = MultivariateNetworkMetaAnalysis()
        results = model.fit(data, method='reml')

        table = model.get_treatment_effects_table()
        assert table.shape[0] == 4  # 2 treatments * 2 outcomes
        assert 'treatment' in table.columns
        assert 'outcome' in table.columns
        assert 'estimate' in table.columns

    def test_consistency_model(self):
        """Test consistency vs inconsistency models."""
        np.random.seed(42)
        data = simulate_network_ma(
            n_treatments=4,
            n_outcomes=2,
            n_studies=15,
            seed=42
        )

        model_consistent = MultivariateNetworkMetaAnalysis(consistency_model=True)
        results = model_consistent.fit(data, method='reml')

        assert results.converged


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_all_missing_study(self):
        """Test handling of studies with all missing outcomes."""
        y = np.array([
            [1.0, 2.0],
            [np.nan, np.nan],
            [1.5, 2.5]
        ])
        S = np.array([np.eye(2) for _ in range(3)])

        model = MultivariateMetaAnalysis()
        # Should handle gracefully
        results = model.fit(y, S, method='reml')
        assert results is not None

    def test_perfect_correlation(self):
        """Test with perfectly correlated outcomes."""
        np.random.seed(42)
        n_studies = 10
        y1 = np.random.randn(n_studies)
        y = np.column_stack([y1, y1])  # Perfect correlation

        S = np.array([np.eye(2) * 0.1 for _ in range(n_studies)])

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')
        # Should handle numerical issues gracefully
        assert results is not None

    def test_no_heterogeneity(self):
        """Test with no between-study heterogeneity."""
        np.random.seed(42)
        n_studies = 10
        true_effect = np.array([0.5, 0.3])

        # All studies have same true effect
        y = np.tile(true_effect, (n_studies, 1))
        y += np.random.randn(n_studies, 2) * 0.01  # Small noise

        S = np.array([np.eye(2) * 0.01 for _ in range(n_studies)])

        model = MultivariateMetaAnalysis()
        results = model.fit(y, S, method='reml')

        # Should estimate near-zero heterogeneity
        assert results.converged
        assert np.all(np.diag(results.Psi) < 0.1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
