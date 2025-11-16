"""
Tests for imputation methods.
"""

import numpy as np
import pytest
from mvmeta.imputation import MultipleImputation, PatternMixtureModel
from mvmeta.utils import simulate_multivariate_ma


class TestMultipleImputation:
    """Tests for MultipleImputation class."""

    def test_basic_imputation(self):
        """Test basic multiple imputation."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            missing_rate=0.2,
            seed=42
        )

        mi = MultipleImputation(n_imputations=5, method='normal')
        results = mi.fit_transform(y, S, method='reml')

        assert results.converged
        assert results.method == 'MI-REML'
        assert 'n_imputations' in results.additional_info
        assert results.additional_info['n_imputations'] == 5

    def test_no_missing_data(self):
        """Test when there's no missing data."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=10,
            n_outcomes=2,
            missing_rate=0.0,
            seed=42
        )

        mi = MultipleImputation(n_imputations=5)
        results = mi.fit_transform(y, S)

        # Should fit directly without imputation
        assert results.converged

    def test_imputation_methods(self):
        """Test different imputation methods."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            missing_rate=0.3,
            seed=42
        )

        for method in ['normal', 'pmm']:
            mi = MultipleImputation(n_imputations=3, method=method)
            results = mi.fit_transform(y, S)
            assert results.converged, f"Failed for method {method}"

    def test_imputed_datasets(self):
        """Test that imputed datasets are generated."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=10,
            n_outcomes=2,
            missing_rate=0.2,
            seed=42
        )

        mi = MultipleImputation(n_imputations=5)
        results = mi.fit_transform(y, S)

        assert mi.imputed_datasets_ is not None
        assert len(mi.imputed_datasets_) == 5

        # Check that imputed datasets have no missing values
        for y_imp, S_imp in mi.imputed_datasets_:
            assert not np.any(np.isnan(y_imp))

    def test_variance_components(self):
        """Test that variance components are computed correctly."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            missing_rate=0.2,
            seed=42
        )

        mi = MultipleImputation(n_imputations=10)
        results = mi.fit_transform(y, S)

        # Should have within and between variance
        assert 'within_var' in results.additional_info
        assert 'between_var' in results.additional_info

        W = results.additional_info['within_var']
        B = results.additional_info['between_var']

        assert W.shape == (2,)
        assert B.shape == (2,)
        assert np.all(W >= 0)
        assert np.all(B >= 0)


class TestPatternMixtureModel:
    """Tests for PatternMixtureModel class."""

    def test_pattern_identification(self):
        """Test missing data pattern identification."""
        # Create data with specific patterns
        y = np.array([
            [1.0, 2.0, 3.0],      # Complete
            [1.5, 2.5, 3.5],      # Complete
            [1.2, np.nan, 3.2],   # Missing outcome 2
            [1.3, np.nan, 3.3],   # Missing outcome 2
            [np.nan, 2.1, np.nan],# Missing outcomes 1, 3
        ])
        S = np.array([np.eye(3) for _ in range(5)])

        pmm = PatternMixtureModel()
        pmm._identify_patterns(y)

        # Should identify 3 patterns
        assert len(pmm.patterns_) == 3

    def test_basic_pattern_mixture(self):
        """Test basic pattern mixture model."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            missing_rate=0.25,
            seed=42
        )

        pmm = PatternMixtureModel(min_pattern_size=2)
        results = pmm.fit(y, S)

        assert results is not None
        assert pmm.patterns_ is not None
        assert pmm.pattern_results_ is not None

    def test_pattern_summary(self):
        """Test pattern summary table."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            missing_rate=0.2,
            seed=42
        )

        pmm = PatternMixtureModel()
        results = pmm.fit(y, S)

        summary = pmm.get_pattern_summary()
        assert summary is not None
        assert 'pattern' in summary.columns
        assert 'n_studies' in summary.columns

    def test_combine_methods(self):
        """Test different combining methods."""
        np.random.seed(42)
        y, S = simulate_multivariate_ma(
            n_studies=20,
            n_outcomes=2,
            missing_rate=0.2,
            seed=42
        )

        for method in ['weighted', 'min_variance']:
            pmm = PatternMixtureModel(combine_method=method)
            results = pmm.fit(y, S)
            assert results.method == f"PatternMixture-{method}"

    def test_minimum_pattern_size(self):
        """Test minimum pattern size enforcement."""
        y = np.array([
            [1.0, 2.0],
            [1.5, 2.5],
            [np.nan, 2.0],  # Singleton pattern
        ])
        S = np.array([np.eye(2) for _ in range(3)])

        pmm = PatternMixtureModel(min_pattern_size=2)
        results = pmm.fit(y, S)

        # Should skip singleton pattern
        assert results is not None


class TestImputationWithModels:
    """Integration tests with full models."""

    def test_imputation_recovers_truth(self):
        """Test that imputation recovers true values reasonably well."""
        np.random.seed(42)
        true_effects = np.array([0.5, 0.3])

        # Generate complete data first
        y_complete, S = simulate_multivariate_ma(
            n_studies=30,
            n_outcomes=2,
            true_effects=true_effects,
            missing_rate=0.0,
            seed=42
        )

        # Now add missing data
        y_missing = y_complete.copy()
        n_missing = int(0.25 * y_missing.size)
        missing_idx = np.random.choice(y_missing.size, n_missing, replace=False)
        for idx in missing_idx:
            i, j = divmod(idx, 2)
            y_missing[i, j] = np.nan

        # Impute and fit
        mi = MultipleImputation(n_imputations=20, method='normal')
        results = mi.fit_transform(y_missing, S)

        # Check that estimates are reasonably close to true values
        assert np.abs(results.theta[0] - true_effects[0]) < 0.3
        assert np.abs(results.theta[1] - true_effects[1]) < 0.3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
