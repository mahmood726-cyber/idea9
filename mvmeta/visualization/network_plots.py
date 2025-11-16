"""
Network visualization tools for multivariate network meta-analysis.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns

from mvmeta.models.base import MetaAnalysisResults


def plot_network(
    data: pd.DataFrame,
    treatments: Optional[List[str]] = None,
    node_size_by_studies: bool = True,
    edge_width_by_studies: bool = True,
    figsize: Tuple[float, float] = (10, 8),
    title: Optional[str] = None
) -> plt.Figure:
    """
    Plot network diagram showing treatment comparisons.

    Parameters
    ----------
    data : pd.DataFrame
        Network data with 't1' and 't2' columns
    treatments : List[str], optional
        List of treatment names
    node_size_by_studies : bool, default=True
        Scale node size by number of studies
    edge_width_by_studies : bool, default=True
        Scale edge width by number of comparisons
    figsize : Tuple[float, float], default=(10, 8)
        Figure size
    title : str, optional
        Figure title

    Returns
    -------
    plt.Figure
        Network diagram figure
    """
    # Get unique treatments
    if treatments is None:
        treatments = sorted(pd.concat([data['t1'], data['t2']]).unique())

    # Create network graph
    G = nx.Graph()
    G.add_nodes_from(treatments)

    # Add edges with weights (number of studies)
    edge_weights = {}
    for _, row in data.iterrows():
        t1, t2 = row['t1'], row['t2']
        edge = tuple(sorted([t1, t2]))
        edge_weights[edge] = edge_weights.get(edge, 0) + 1

    for edge, weight in edge_weights.items():
        G.add_edge(edge[0], edge[1], weight=weight)

    # Count studies per treatment
    treatment_counts = {}
    for t in treatments:
        count = ((data['t1'] == t) | (data['t2'] == t)).sum()
        treatment_counts[t] = count

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Node sizes
    if node_size_by_studies:
        node_sizes = [treatment_counts[t] * 200 + 500 for t in G.nodes()]
    else:
        node_sizes = 1000

    # Edge widths
    if edge_width_by_studies:
        edge_widths = [G[u][v]['weight'] * 2 for u, v in G.edges()]
    else:
        edge_widths = 2

    # Draw network
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color='lightblue',
        edgecolors='black',
        linewidths=2,
        ax=ax
    )

    nx.draw_networkx_edges(
        G, pos,
        width=edge_widths,
        alpha=0.6,
        ax=ax
    )

    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_weight='bold',
        ax=ax
    )

    # Add edge labels (number of studies)
    edge_labels = {(u, v): f"n={G[u][v]['weight']}" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        ax=ax
    )

    ax.axis('off')

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    else:
        ax.set_title('Treatment Network', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    return fig


def plot_treatment_effects(
    results: MetaAnalysisResults,
    outcome_names: Optional[List[str]] = None,
    figsize: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None
) -> plt.Figure:
    """
    Plot treatment effects for multivariate network meta-analysis.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from fitted MultivariateNetworkMetaAnalysis
    outcome_names : List[str], optional
        Names for outcomes
    figsize : Tuple[float, float], optional
        Figure size
    title : str, optional
        Figure title

    Returns
    -------
    plt.Figure
        Treatment effects plot
    """
    # Extract treatment effects matrix from results
    if 'theta_matrix' not in results.additional_info:
        raise ValueError("Results must be from MultivariateNetworkMetaAnalysis")

    theta_matrix = results.additional_info['theta_matrix']
    theta_se_matrix = results.additional_info['theta_se_matrix']
    treatment_names = results.additional_info['treatment_names']
    ref_treatment = results.additional_info['reference_treatment']

    n_comparisons, n_outcomes = theta_matrix.shape

    if outcome_names is None:
        if 'outcome_names' in results.additional_info:
            outcome_names = results.additional_info['outcome_names']
        else:
            outcome_names = [f"Outcome {i+1}" for i in range(n_outcomes)]

    if figsize is None:
        figsize = (12, max(6, n_comparisons * 1.5))

    # Create figure with subplots for each outcome
    fig, axes = plt.subplots(1, n_outcomes, figsize=figsize, sharey=True)
    if n_outcomes == 1:
        axes = [axes]

    for j, (ax, outcome_name) in enumerate(zip(axes, outcome_names)):
        # Extract estimates for this outcome
        estimates = theta_matrix[:, j]
        ses = theta_se_matrix[:, j]
        ci_lower = estimates - 1.96 * ses
        ci_upper = estimates + 1.96 * ses

        # Treatment names (excluding reference)
        comp_names = [treatment_names[i+1] for i in range(n_comparisons)]

        # Create forest plot
        y_positions = np.arange(n_comparisons)

        # Plot confidence intervals
        for i, (low, high, est) in enumerate(zip(ci_lower, ci_upper, estimates)):
            ax.plot([low, high], [i, i], 'k-', linewidth=2)

        # Plot point estimates
        colors = ['red' if est < 0 else 'blue' for est in estimates]
        ax.scatter(estimates, y_positions, s=100, c=colors, zorder=3, alpha=0.7)

        # Add null line
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        # Labels
        ax.set_yticks(y_positions)
        ax.set_yticklabels(comp_names)
        ax.set_xlabel('Effect vs. Reference')
        ax.set_title(outcome_name)

        if j == 0:
            ax.set_ylabel('Treatment')

        # Format
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3)

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    else:
        fig.suptitle(f'Treatment Effects (Reference: {ref_treatment})',
                    fontsize=14, fontweight='bold', y=0.98)

    plt.tight_layout()
    return fig


def plot_treatment_rankings(
    results: MetaAnalysisResults,
    outcome_idx: int = 0,
    outcome_name: Optional[str] = None,
    n_simulations: int = 10000,
    figsize: Tuple[float, float] = (10, 6),
    higher_is_better: bool = True
) -> plt.Figure:
    """
    Plot treatment ranking probabilities (SUCRA plot).

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from Bayesian network meta-analysis
    outcome_idx : int, default=0
        Index of outcome to rank
    outcome_name : str, optional
        Name of outcome
    n_simulations : int, default=10000
        Number of simulations for ranking
    figsize : Tuple[float, float], default=(10, 6)
        Figure size
    higher_is_better : bool, default=True
        Whether higher values are better

    Returns
    -------
    plt.Figure
        Treatment ranking plot
    """
    if 'trace' not in results.additional_info:
        raise ValueError("Rankings require Bayesian results with trace")

    treatment_names = results.additional_info['treatment_names']
    n_treatments = len(treatment_names)

    # Extract posterior samples
    trace = results.additional_info['trace']
    theta_samples = trace.posterior['theta'].values

    # Reshape: (n_chains, n_draws, n_comparisons, n_outcomes)
    n_chains, n_draws, n_comparisons, n_outcomes = theta_samples.shape

    # Flatten chains and draws
    theta_flat = theta_samples.reshape(-1, n_comparisons, n_outcomes)
    n_samples = theta_flat.shape[0]

    # Subsample if needed
    if n_samples > n_simulations:
        idx = np.random.choice(n_samples, n_simulations, replace=False)
        theta_flat = theta_flat[idx]

    # Add reference treatment (effect = 0)
    # theta_with_ref has shape (n_simulations, n_treatments, n_outcomes)
    theta_with_ref = np.zeros((theta_flat.shape[0], n_treatments, n_outcomes))
    theta_with_ref[:, 1:, :] = theta_flat

    # Rank treatments for the selected outcome
    if higher_is_better:
        ranks = np.argsort(-theta_with_ref[:, :, outcome_idx], axis=1)
    else:
        ranks = np.argsort(theta_with_ref[:, :, outcome_idx], axis=1)

    # Compute ranking probabilities
    rank_probs = np.zeros((n_treatments, n_treatments))
    for i in range(n_treatments):
        for rank in range(n_treatments):
            rank_probs[i, rank] = np.mean(ranks[:, rank] == i)

    # Compute SUCRA (Surface Under Cumulative Ranking)
    sucra = np.zeros(n_treatments)
    for i in range(n_treatments):
        cumsum = np.cumsum(rank_probs[i, :-1])
        sucra[i] = cumsum.sum() / (n_treatments - 1)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Ranking probabilities heatmap
    sns.heatmap(
        rank_probs * 100,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        xticklabels=[f"Rank {i+1}" for i in range(n_treatments)],
        yticklabels=treatment_names,
        ax=ax1,
        cbar_kws={'label': 'Probability (%)'}
    )
    ax1.set_title('Ranking Probabilities')
    ax1.set_xlabel('Rank')
    ax1.set_ylabel('Treatment')

    # SUCRA plot
    sorted_idx = np.argsort(sucra)[::-1]
    colors = plt.cm.RdYlGn(sucra[sorted_idx])

    bars = ax2.barh(
        range(n_treatments),
        sucra[sorted_idx] * 100,
        color=colors,
        alpha=0.7
    )
    ax2.set_yticks(range(n_treatments))
    ax2.set_yticklabels([treatment_names[i] for i in sorted_idx])
    ax2.set_xlabel('SUCRA (%)')
    ax2.set_title('Treatment Rankings (SUCRA)')
    ax2.set_xlim([0, 100])
    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='x', alpha=0.3)

    outcome_title = outcome_name if outcome_name else f"Outcome {outcome_idx + 1}"
    fig.suptitle(f'Treatment Rankings for {outcome_title}',
                fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig


def plot_league_table(
    results: MetaAnalysisResults,
    outcome_idx: int = 0,
    outcome_name: Optional[str] = None,
    figsize: Tuple[float, float] = (10, 10)
) -> plt.Figure:
    """
    Create league table for pairwise treatment comparisons.

    Parameters
    ----------
    results : MetaAnalysisResults
        Results from network meta-analysis
    outcome_idx : int, default=0
        Index of outcome to display
    outcome_name : str, optional
        Name of outcome
    figsize : Tuple[float, float], default=(10, 10)
        Figure size

    Returns
    -------
    plt.Figure
        League table figure
    """
    treatment_names = results.additional_info['treatment_names']
    theta_matrix = results.additional_info['theta_matrix']
    theta_se_matrix = results.additional_info['theta_se_matrix']

    n_treatments = len(treatment_names)

    # Compute all pairwise comparisons
    league_estimates = np.zeros((n_treatments, n_treatments))
    league_ci_lower = np.zeros((n_treatments, n_treatments))
    league_ci_upper = np.zeros((n_treatments, n_treatments))

    for i in range(n_treatments):
        for j in range(n_treatments):
            if i == j:
                continue

            # Effect of i vs j = (i vs ref) - (j vs ref)
            if i == 0:
                est = -theta_matrix[j-1, outcome_idx]
                se = theta_se_matrix[j-1, outcome_idx]
            elif j == 0:
                est = theta_matrix[i-1, outcome_idx]
                se = theta_se_matrix[i-1, outcome_idx]
            else:
                est = theta_matrix[i-1, outcome_idx] - theta_matrix[j-1, outcome_idx]
                # Approximate SE (ignoring correlation for simplicity)
                se = np.sqrt(theta_se_matrix[i-1, outcome_idx]**2 +
                           theta_se_matrix[j-1, outcome_idx]**2)

            league_estimates[i, j] = est
            league_ci_lower[i, j] = est - 1.96 * se
            league_ci_upper[i, j] = est + 1.96 * se

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create table
    table_data = []
    for i in range(n_treatments):
        row = []
        for j in range(n_treatments):
            if i == j:
                row.append(treatment_names[i])
            elif i < j:
                # Upper triangle: estimates
                est = league_estimates[i, j]
                ci_low = league_ci_lower[i, j]
                ci_high = league_ci_upper[i, j]
                row.append(f"{est:.2f}\n({ci_low:.2f}, {ci_high:.2f})")
            else:
                # Lower triangle: empty or complementary
                row.append("")
        table_data.append(row)

    # Plot table
    table = ax.table(
        cellText=table_data,
        cellLoc='center',
        loc='center',
        colLabels=treatment_names,
        rowLabels=treatment_names
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Color cells
    for i in range(n_treatments + 1):
        for j in range(n_treatments + 1):
            cell = table[(i, j)]

            if i == 0 or j == 0:
                # Header
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(weight='bold', color='white')
            elif i == j:
                # Diagonal
                cell.set_facecolor('#2196F3')
                cell.set_text_props(weight='bold', color='white')
            elif i < j:
                # Upper triangle with estimates
                cell.set_facecolor('#E3F2FD')

    ax.axis('off')

    outcome_title = outcome_name if outcome_name else f"Outcome {outcome_idx + 1}"
    ax.set_title(f'League Table for {outcome_title}\n(Row vs Column)',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    return fig
