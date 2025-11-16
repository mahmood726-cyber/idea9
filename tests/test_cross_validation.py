"""
Tests for cross-validation functionality.
"""

import numpy as np
import pandas as pd
import pytest
from mvmeta.utils import simulate_multivariate_ma
from mvmeta.diagnostics import (
    leave_one_out_cv,
    k_fold_cv,
    cross_validate,
    compare_methods_cv
)


class TestLeaveOneOutCV:
    """Tests for leave-one-out cross-validation."""

    def test_loocv_basic(self):
        """Test basic LOOCV functionality."""
        y, S = simulate_multivariate_ma(
            n_studies=15,
            n_outcomes=2,
            true_effects=np.array([0.5, 0.3]),
            seed=42
        )

        cv_results = leave_one_out_cv(y, S, verbose=False)

        # Check structure
        assert 'predictions' in cv_results
        assert 'mspe' in cv_results
        assert 'coverage' in cv_results
        assert 'calibration' in cv_results
        assert 'cv_loglik' in cv_results

        # Check dimensions
        assert len(cv_results['mspe']) == 2  # n_outcomes
        assert len(cv_results['coverage']) == 2

        # Check predictions DataFrame
        df = cv_results['predictions']
        assert len(df) == 15 * 2  # n_studies * n_outcomes
        assert 'y_true' in df.columns
        assert 'y_pred' in df.columns
        assert 'pred_error' in df.columns
        assert 'covered' in df.columns

        # MSPE should be positive
        assert np.all(cv_results['mspe'] > 0)

        # Coverage should be between 0 and 1
        assert np.all((cv_results['coverage'] >= 0) & (cv_results['coverage'] <= 1))

    def test_loocv_perfect_data(self):
        """Test LOOCV on data with no heterogeneity."""
        n_studies = 20
        n_outcomes = 2
        true_effects = np.array([0.0, 0.0])

        # Create homogeneous data (no between-study variance)
        y, S = simulate_multivariate_ma(
            n_studies=n_studies,
            n_outcomes=n_outcomes,
            true_effects=true_effects,
            between_study_sd=0.01,  # Very small heterogeneity
            seed=123
        )

        cv_results = leave_one_out_cv(y, S, verbose=False)

        # With little heterogeneity, predictions should be close to truth
        df = cv_results['predictions']
        mean_errors = df.groupby('outcome')['pred_error'].mean().abs()

        # Mean prediction error should be small (close to 0)
        assert np.all(mean_errors < 0.2)

        # Coverage should be reasonably close to nominal
        assert np.all(cv_results['coverage'] > 0.8)

    def test_loocv_methods_comparison(self):
        """Test LOOCV with different estimation methods."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)

        # REML
        cv_reml = leave_one_out_cv(y, S, method='reml', verbose=False)

        # ML
        cv_ml = leave_one_out_cv(y, S, method='ml', verbose=False)

        # Both should produce valid results
        assert not np.any(np.isnan(cv_reml['mspe']))
        assert not np.any(np.isnan(cv_ml['mspe']))

        # Results should be similar but not identical
        assert np.allclose(cv_reml['mspe'], cv_ml['mspe'], rtol=0.5)


class TestKFoldCV:
    """Tests for k-fold cross-validation."""

    def test_kfold_basic(self):
        """Test basic k-fold CV functionality."""
        y, S = simulate_multivariate_ma(n_studies=30, n_outcomes=2, seed=42)

        cv_results = k_fold_cv(y, S, k=5, seed=42, verbose=False)

        # Check structure
        assert 'predictions' in cv_results
        assert 'mspe' in cv_results
        assert 'coverage' in cv_results
        assert 'k' in cv_results
        assert cv_results['k'] == 5

        # Check dimensions
        assert len(cv_results['mspe']) == 2  # n_outcomes

        # Predictions should cover all studies
        df = cv_results['predictions']
        n_predicted = len(df) / 2  # Divide by n_outcomes
        assert n_predicted == 30  # All studies should be predicted

    def test_kfold_different_k(self):
        """Test k-fold CV with different k values."""
        y, S = simulate_multivariate_ma(n_studies=40, n_outcomes=2, seed=42)

        for k in [5, 10]:
            cv_results = k_fold_cv(y, S, k=k, seed=42, verbose=False)

            assert cv_results['k'] == k
            assert not np.any(np.isnan(cv_results['mspe']))

    def test_kfold_seed_reproducibility(self):
        """Test that using the same seed gives same results."""
        y, S = simulate_multivariate_ma(n_studies=30, n_outcomes=2, seed=42)

        cv1 = k_fold_cv(y, S, k=5, seed=123, verbose=False)
        cv2 = k_fold_cv(y, S, k=5, seed=123, verbose=False)

        # Results should be identical
        assert np.allclose(cv1['mspe'], cv2['mspe'])
        assert np.allclose(cv1['coverage'], cv2['coverage'])

    def test_kfold_invalid_k(self):
        """Test that k > n_studies raises error."""
        y, S = simulate_multivariate_ma(n_studies=10, n_outcomes=2, seed=42)

        with pytest.raises(ValueError):
            k_fold_cv(y, S, k=20, verbose=False)


class TestCrossValidate:
    """Tests for unified cross-validation interface."""

    def test_cross_validate_loo(self):
        """Test cross_validate with LOO."""
        y, S = simulate_multivariate_ma(n_studies=15, n_outcomes=2, seed=42)

        cv_results = cross_validate(y, S, cv_type='loo', verbose=False)

        assert 'mspe' in cv_results
        assert 'coverage' in cv_results

    def test_cross_validate_kfold(self):
        """Test cross_validate with k-fold."""
        y, S = simulate_multivariate_ma(n_studies=30, n_outcomes=2, seed=42)

        cv_results = cross_validate(y, S, cv_type='kfold', k=5, seed=42, verbose=False)

        assert 'mspe' in cv_results
        assert 'k' in cv_results

    def test_cross_validate_aliases(self):
        """Test that CV type aliases work."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)

        # All these should work
        for cv_type in ['loo', 'loocv', 'leave-one-out']:
            cv = cross_validate(y, S, cv_type=cv_type, verbose=False)
            assert 'mspe' in cv

        for cv_type in ['kfold', 'k-fold']:
            cv = cross_validate(y, S, cv_type=cv_type, k=5, seed=42, verbose=False)
            assert 'k' in cv

    def test_cross_validate_invalid_type(self):
        """Test that invalid CV type raises error."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)

        with pytest.raises(ValueError):
            cross_validate(y, S, cv_type='invalid', verbose=False)


class TestCompareMethodsCV:
    """Tests for comparing methods via cross-validation."""

    def test_compare_methods_basic(self):
        """Test basic method comparison."""
        y, S = simulate_multivariate_ma(n_studies=25, n_outcomes=2, seed=42)

        comparison = compare_methods_cv(
            y, S,
            methods=['reml', 'ml'],
            cv_type='kfold',
            k=5,
            seed=42,
            verbose=False
        )

        # Check structure
        assert isinstance(comparison, pd.DataFrame)
        assert 'method' in comparison.columns
        assert 'outcome' in comparison.columns
        assert 'mspe' in comparison.columns
        assert 'coverage' in comparison.columns

        # Should have results for both methods and all outcomes
        assert len(comparison) == 2 * 2  # n_methods * n_outcomes

        # Check that both methods are present
        methods = comparison['method'].unique()
        assert 'REML' in methods
        assert 'ML' in methods

    def test_compare_methods_single(self):
        """Test comparison with single method."""
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)

        comparison = compare_methods_cv(
            y, S,
            methods=['reml'],
            cv_type='loo',
            verbose=False
        )

        assert len(comparison) == 2  # 1 method * 2 outcomes


class TestCVWithMissingData:
    """Tests for CV with missing data patterns."""

    def test_cv_with_missing_studies(self):
        """Test CV when some studies are missing outcomes."""
        # Create data with some missing values
        y, S = simulate_multivariate_ma(n_studies=20, n_outcomes=2, seed=42)

        # Set some values to NaN
        y[0, 1] = np.nan
        y[5, 0] = np.nan

        # Remove studies with any missing values for CV
        complete_mask = ~np.any(np.isnan(y), axis=1)
        y_complete = y[complete_mask]
        S_complete = S[complete_mask]

        # CV should work on complete cases
        cv_results = leave_one_out_cv(y_complete, S_complete, verbose=False)

        assert len(cv_results['predictions']) == np.sum(complete_mask) * 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
