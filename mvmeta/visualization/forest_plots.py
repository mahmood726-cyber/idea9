"""
Forest plots and correlation visualizations for multivariate meta-analysis.
"""

from typing import Optional, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle

from mvmeta.models.base import MetaAnalysisResults


def plot_multivariate_forest(
    results: MetaAnalysisResults,
    outcome_names: Optional[List[str]] = None,
    figsize: Optional[Tuple[float, float]] = None,
    show_pooled: bool = True,
    title: Optional[str] = None
) -> plt.Figure:
    """
    Create forest plot for multivariate meta-analysis results.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from fitted model
    outcome_names : List[str], optional
        Names for each outcome. If None, uses "Outcome 1", "Outcome 2", etc.
    figsize : Tuple[float, float], optional
        Figure size. If None, calculated automatically.
    show_pooled : bool, default=True
        Whether to show pooled estimates
    title : str, optional
        Figure title

    Returns
    -------
    plt.Figure
        Forest plot figure
    """
    n_outcomes = results.n_outcomes

    if outcome_names is None:
        outcome_names = [f"Outcome {i+1}" for i in range(n_outcomes)]

    if figsize is None:
        figsize = (10, 6)

    # Create subplots (one per outcome)
    fig, axes = plt.subplots(1, n_outcomes, figsize=figsize, sharey=False)
    if n_outcomes == 1:
        axes = [axes]

    for j, (ax, outcome_name) in enumerate(zip(axes, outcome_names)):
        # Pooled estimate
        theta_j = results.theta[j]
        se_j = results.theta_se[j]
        ci_lower = theta_j - 1.96 * se_j
        ci_upper = theta_j + 1.96 * se_j

        # Plot pooled estimate
        if show_pooled:
            ax.plot([ci_lower, ci_upper], [0, 0], 'k-', linewidth=2)
            ax.plot(theta_j, 0, 'kD', markersize=10, label='Pooled')

        # Add null line
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        # Labels
        ax.set_xlabel('Effect Size')
        ax.set_title(outcome_name)
        if j == 0:
            ax.set_ylabel('Study')

        # Format
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3)

        if show_pooled:
            ax.legend()

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig


def plot_outcome_correlations(
    results: MetaAnalysisResults,
    outcome_names: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (8, 6),
    cmap: str = 'RdBu_r',
    title: Optional[str] = None
) -> plt.Figure:
    """
    Visualize between-study correlation matrix.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from fitted model
    outcome_names : List[str], optional
        Names for outcomes
    figsize : Tuple[float, float], default=(8, 6)
        Figure size
    cmap : str, default='RdBu_r'
        Colormap for correlation matrix
    title : str, optional
        Figure title

    Returns
    -------
    plt.Figure
        Correlation heatmap figure
    """
    n_outcomes = results.n_outcomes

    if outcome_names is None:
        outcome_names = [f"Outcome {i+1}" for i in range(n_outcomes)]

    # Get correlation matrix
    corr_matrix = results.between_study_correlation

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Heatmap of correlations
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.3f',
        cmap=cmap,
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        xticklabels=outcome_names,
        yticklabels=outcome_names,
        ax=ax1,
        cbar_kws={'label': 'Correlation'}
    )
    ax1.set_title('Between-Study Correlations')

    # Variance components (diagonal of Psi)
    variances = np.diag(results.Psi)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, n_outcomes))

    ax2.bar(range(n_outcomes), variances, color=colors, alpha=0.7)
    ax2.set_xticks(range(n_outcomes))
    ax2.set_xticklabels(outcome_names, rotation=45, ha='right')
    ax2.set_ylabel('Between-Study Variance')
    ax2.set_title('Heterogeneity by Outcome')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='y', alpha=0.3)

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    return fig


def plot_heterogeneity_comparison(
    results: MetaAnalysisResults,
    outcome_names: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (10, 5)
) -> plt.Figure:
    """
    Compare heterogeneity measures across outcomes.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from fitted model
    outcome_names : List[str], optional
        Names for outcomes
    figsize : Tuple[float, float], default=(10, 5)
        Figure size

    Returns
    -------
    plt.Figure
        Heterogeneity comparison figure
    """
    n_outcomes = results.n_outcomes

    if outcome_names is None:
        outcome_names = [f"Outcome {i+1}" for i in range(n_outcomes)]

    if results.I2 is None:
        raise ValueError("I-squared statistics not available in results")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # I-squared
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, n_outcomes))
    bars1 = ax1.bar(range(n_outcomes), results.I2 * 100, color=colors, alpha=0.7)
    ax1.set_xticks(range(n_outcomes))
    ax1.set_xticklabels(outcome_names, rotation=45, ha='right')
    ax1.set_ylabel('I² (%)')
    ax1.set_title('Heterogeneity (I-squared)')
    ax1.axhline(y=25, color='gray', linestyle='--', alpha=0.5, label='Low')
    ax1.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Moderate')
    ax1.axhline(y=75, color='gray', linestyle='--', alpha=0.5, label='High')
    ax1.legend()
    ax1.set_ylim([0, 100])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='y', alpha=0.3)

    # Between-study SD
    tau = np.sqrt(np.diag(results.Psi))
    bars2 = ax2.bar(range(n_outcomes), tau, color=colors, alpha=0.7)
    ax2.set_xticks(range(n_outcomes))
    ax2.set_xticklabels(outcome_names, rotation=45, ha='right')
    ax2.set_ylabel('τ (between-study SD)')
    ax2.set_title('Between-Study Standard Deviation')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    return fig


def plot_bivariate_ellipse(
    results: MetaAnalysisResults,
    outcome1_idx: int = 0,
    outcome2_idx: int = 1,
    outcome_names: Optional[List[str]] = None,
    confidence_level: float = 0.95,
    figsize: Tuple[float, float] = (8, 6)
) -> plt.Figure:
    """
    Plot confidence ellipse for two outcomes.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from fitted model
    outcome1_idx : int, default=0
        Index of first outcome
    outcome2_idx : int, default=1
        Index of second outcome
    outcome_names : List[str], optional
        Names for outcomes
    confidence_level : float, default=0.95
        Confidence level for ellipse
    figsize : Tuple[float, float], default=(8, 6)
        Figure size

    Returns
    -------
    plt.Figure
        Bivariate confidence ellipse
    """
    from matplotlib.patches import Ellipse
    from scipy.stats import chi2

    if outcome_names is None:
        outcome_names = [f"Outcome {i+1}" for i in range(results.n_outcomes)]

    # Extract estimates for the two outcomes
    theta1 = results.theta[outcome1_idx]
    theta2 = results.theta[outcome2_idx]

    # Extract 2x2 covariance submatrix
    cov_12 = np.array([
        [results.theta_se[outcome1_idx]**2, 0],
        [0, results.theta_se[outcome2_idx]**2]
    ])

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot point estimate
    ax.plot(theta1, theta2, 'ro', markersize=10, label='Pooled Estimate')

    # Compute confidence ellipse
    chi2_val = chi2.ppf(confidence_level, df=2)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_12)

    angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))
    width = 2 * np.sqrt(chi2_val * eigenvalues[0])
    height = 2 * np.sqrt(chi2_val * eigenvalues[1])

    ellipse = Ellipse(
        (theta1, theta2),
        width=width,
        height=height,
        angle=angle,
        facecolor='red',
        alpha=0.2,
        edgecolor='red',
        linewidth=2,
        label=f'{confidence_level*100:.0f}% CI'
    )
    ax.add_patch(ellipse)

    # Add reference lines
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    # Labels
    ax.set_xlabel(outcome_names[outcome1_idx])
    ax.set_ylabel(outcome_names[outcome2_idx])
    ax.set_title(f'Bivariate Confidence Region\n(Correlation: {results.between_study_correlation[outcome1_idx, outcome2_idx]:.3f})')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig
